import datetime
import pickle
import random
from collections import defaultdict, namedtuple
from typing import *

from sched.jobshop.helper import *

__package__ = 'sched.jobshop'


class JSP:
   """
   An instance of Job Shop Scheduling Problem
   """
   __name__ = f"{__package__}.JSP"
   logger = logging.getLogger(__name__)

   cp_var_container = \
      namedtuple('cp_vars',
                 ['task_start',
                  'task_end',
                  'task_start_on_m',
                  'task_end_on_m',
                  'task_dur_on_m',
                  'task_opt_on_m',
                  'task_int_on_m',
                  'makespan'])
   cp_sol_container = \
      namedtuple('cp_sol',
                 ['task_start',
                  'task_end',
                  'task_start_on_m',
                  'task_end_on_m',
                  'task_dur_on_m',
                  'task_opt_on_m',
                  'makespan'])

   def __init__(
         self,
         jobs: Dict[Any, JSPJob] = None,
         machines: Dict[Any, List[JSPMachine]] = None,
         **kwargs):
      if not (jobs and machines):
         raise ValueError('Cannot initialize the problem')

      self.jobs = jobs
      self.groups = machines

      try:
         self.mp_model: ModelWrapper = ModelWrapper(solver_name='copt')
      except Exception as e:
         logger.warning("Cannot create an optimization wrapper")
         self.mp_model = None

      # bool is flexible jsp
      self.is_fjsp = 0
      self.is_parallel = kwargs.get('para', False)
      for g, m_list in machines.items():
         if len(m_list) > 1:
            self.is_fjsp = 1
            break

      # attrs for constraint programming
      self._ub_variable = \
         sum(t.duration for job in self.jobs.values() for t in job.tasks)

      self.cp_vars = None
      self.cp_model = None
      self.cp_solver = None
      self.cp_solution_printer = None
      self.cp_status = None
      self.cp_solution = None

   def create_cp_model(self, **kwargs):

      max_sec = kwargs.get('max_sec', 20)
      max_sol = kwargs.get('max_sol', 20)
      num_workers = kwargs.get('num_workers', 2)
      # the cp instance
      model = cp_model.CpModel()

      # create variables
      task_start = {}
      task_end = {}
      task_start_on_m = {}
      task_end_on_m = {}
      task_dur_on_m = {}
      task_opt_on_m = {}
      task_int_on_m = {}
      makespan = model.NewIntVar(0, self._ub_variable, name='C_max')

      # reduced maps
      machine_intervals = defaultdict(list)
      task_durations = defaultdict(list)
      task_options = defaultdict(list)
      for _, job in self.jobs.items():
         job_id = job.idx
         for t in job.tasks:  # iterate over the route
            dur, g = t.duration, t.group
            group_name_suffix = f"{job_id}@{g}"
            start_var = model.NewIntVar(0, self._ub_variable, f'start-{group_name_suffix}')
            end_var = model.NewIntVar(0, self._ub_variable, f'end-{group_name_suffix}')
            task_start[job_id, g] = start_var
            task_end[job_id, g] = end_var
            for machine in self.groups[g]:
               m_id = machine.idx
               suffix = f'{job_id}_{g}_{m_id}'
               m_start_var = model.NewIntVar(0, self._ub_variable, f'start-{suffix}')
               m_end_var = model.NewIntVar(0, self._ub_variable, f'end-{suffix}')
               m_duration_var = model.NewIntVar(0, self._ub_variable, f'dur-{suffix}')
               m_option_var = model.NewBoolVar(f'opt-{suffix}')
               m_interval_var = model.NewIntervalVar(m_start_var, m_duration_var, m_end_var,
                                                     name=f'interval-{suffix}')
               task_start_on_m[job_id, g, m_id] = m_start_var
               task_end_on_m[job_id, g, m_id] = m_end_var
               task_dur_on_m[job_id, g, m_id] = m_duration_var
               task_opt_on_m[job_id, g, m_id] = m_option_var
               task_int_on_m[job_id, g, m_id] = m_interval_var
               machine_intervals[g, m_id].append(m_interval_var)
               task_durations[job_id, g].append(m_duration_var)
               task_options[job_id, g].append(m_option_var)

      # parallel scheduling?
      if not self.is_parallel:
         for _, job in self.jobs.items():
            for t in job.tasks:
               model.Add(sum(task_options[job.idx, t.group]) == 1)
               for machine in self.groups[t.group]:
                  model.Add(task_dur_on_m[job.idx, t.group, machine.idx] == t.duration) \
                     .OnlyEnforceIf(task_opt_on_m[job.idx, t.group, machine.idx])
      else:
         for _, job in self.jobs.items():
            for t in job.tasks:
               model.Add(sum(task_durations[job.idx, t.group]) == t.duration)

      # non-overlapping
      for k, v in machine_intervals.items():
         model.AddNoOverlap(v)

      # precedences
      for _, job in self.jobs.items():
         for t in job.tasks:
            m_list = self.groups[t.group]
            model.AddMinEquality(task_start[job.idx, t.group],
                                 (task_start_on_m[job.idx, t.group, _m.idx] for _m in m_list))
            model.AddMaxEquality(task_end[job.idx, t.group],
                                 (task_end_on_m[job.idx, t.group, _m.idx] for _m in m_list))

         _size = len(job.tasks)
         for _prev, _next in zip(job.tasks[:_size - 1], job.tasks[1:]):
            model.Add(task_start[job.idx, _next.group] >= task_end[job.idx, _prev.group])

      # makespan
      model.AddMaxEquality(makespan, [task_end[job.idx, job.tasks[-1].group] for _, job in self.jobs.items()])

      model.Minimize(makespan)

      self.cp_vars = self.cp_var_container(
         task_start=task_start,
         task_end=task_end,
         task_start_on_m=task_start_on_m,
         task_end_on_m=task_end_on_m,
         task_dur_on_m=task_dur_on_m,
         task_opt_on_m=task_opt_on_m,
         task_int_on_m=task_int_on_m,
         makespan=makespan
      )
      self.cp_model = model
      self.cp_solver = solver = cp_model.CpSolver()
      solver.parameters.max_time_in_seconds = max_sec
      solver.parameters.log_search_progress = True
      solver.parameters.num_search_workers = num_workers
      self.cp_solution_printer = solution_printer = SatCallBack(makespan, max_sol, max_sec)
      self.cp_status = status = solver.SolveWithSolutionCallback(model, solution_printer)
      self.logger.info('Status = %s' % solver.StatusName(status))
      self.logger.info('Number of solutions found: %i' % solution_printer.solution_count())
      if solution_printer.solution_count() > 0:
         self.cp_solution = self.cp_sol_container(**self.cp_extract_sol())
      self.logger.info(self.cp_solver.ResponseStats())

   def cp_extract_sol(self):
      solution = {}
      vars_dict = self.cp_vars._asdict()
      for _attr in self.cp_sol_container._fields:
         vars = vars_dict[_attr]
         if isinstance(vars, dict):
            solution[_attr] = {k: self.cp_solver.Value(v) for k, v in vars.items()}
         else:
            solution[_attr] = self.cp_solver.Value(vars)
      return solution

   def cp_to_gantt_mermaid(self, fp='result', start_date=None):
      """
      Serialize to Mermaid.js Gantt graph

      example:
      ```{=mermaid gantt graph}
         gantt
          dateFormat hh:mm:ss
          axisFormat %H:%M
          section  1
          11 :done, a11, 08:30:50 , 4m
          12 :active, a12, after a11 , 3m
          13 :active, a13, after a12, 4m
          section machine 2
          21 :active, a21, 08:30:50 , 4m
          13 :active, a13, after a12 , 6m
          23 :active, a23, after a13 , 1m
          section machine 3
          31 :active, a31, 08:30:50 , 6m
          32 :active, a32, after a31 , 1m
          33 :active, a33, after a32, 4m
      ```
      :return:
      """
      sol = self.cp_solution
      # 3-d data:
      # job_id, group_id, machine_id
      start = pd.Series(sol.task_start_on_m)
      dur = pd.Series(sol.task_dur_on_m)
      opt = pd.Series(sol.task_opt_on_m)
      _start_date = datetime.datetime.now() if start_date is None else start_date

      def generate_sections():
         # ==== sections ====
         for g, machines in self.groups.items():
            for m in machines:
               yield f"section {m}"
               try:
                  _start = start[:, m.group, m.idx]
                  _dur = dur[:, m.group, m.idx]
                  _opt = opt[:, m.group, m.idx]
                  for job_id, _start in _start.items():
                     val = _opt[job_id]
                     if val == 0:
                        continue
                     start_time = _start_date + datetime.timedelta(minutes=int(_start))
                     yield f"{job_id} :active, {job_id}@{g}, {start_time.strftime('%Y-%m-%d %H:%M:%S')}, {_dur[job_id]}m"
               except:
                  self.logger.warning(f"no task started @{m}")

      data = generate_sections()
      _dir = f'{fp}/%d' % time.time()
      os.mkdir(_dir)
      with open(f'{_dir}/gantt.record', 'w') as f:
         for line in MERMAID_GANTT_HEADER:
            f.write(line)
            f.write('\n')
         f.write(f"title schedule of (f)jsp\n")
         for line in data:
            f.write(line)
            f.write('\n')

      # liquid

   # ===================
   # utility functions
   # ===================
   @staticmethod
   def rd_instance(m: int, n: int,
                   copy: int = 1,
                   density: float = 0.8):
      """

      :param m: num of jobs
      :param n: num of machines (actually groups)
              - if copy > 1, we generate n groups,
                      each group with randomly 1-copy identical machines
      :param copy: see `n`
      :param density:
              average machine-job adjacent rate
      :return: a (F)JSP instance
      """
      jobs = {i: JSPJob(idx=i, release=0, due=100) for i in range(m)}
      groups = [i for i in range(n)]
      for i in range(m):
         # shuffling routes
         random.shuffle(groups)
         tasks = [
            JSPTask(idx=i,
                    seq=idx,
                    group=g,
                    duration=random.randint(1, 5))
            for idx, g in enumerate(groups) if
            random.random() >= 1 - density]

         if tasks.__len__() == 0:
            jobs.pop(i)
            continue
         jobs[i].tasks = tasks
      machines = {g: [JSPMachine(idx=idx, group=g)
                      for idx in range(random.randint(1, copy))]
                  for g in groups}
      return jobs, machines

   def dump_instance(self, path, protocol='pickle'):
      """
      dump jobs and machines to data files
      """
      current_time = time.time()
      if protocol == 'pickle':
         with open(f'{path}/%d-jobs.pickle' % current_time, 'wb') as f:
            pickle.dump(self.jobs, f)
         with open(f'{path}/%d-machines.pickle' % current_time, 'wb') as f:
            pickle.dump(self.groups, f)
      else:
         raise ValueError(f"protocol: {protocol} not implemented yet")


def sol_to_series(jsp: JSP):
   sol = jsp.cp_solution
   start = pd.Series(sol['task_start_on_m'])
   end = pd.Series(sol['task_end_on_m'])
   dur = pd.Series(sol['task_dur_on_m'])
   opt = pd.Series(sol['task_opt_on_m'])
   return start, end, dur, opt


# aliases
jsp_generate_random_instance = JSP.rd_instance

if __name__ == '__main__':
   # trial run
   m, n, p, d = 5, 10, 1, 0.8
   jobs, machines = JSP.rd_instance(m, n, copy=p, density=d)
   jsp = JSP(jobs, machines)
   jsp.create_cp_model(max_sec=500, num_workers=10)
   jsp.cp_to_gantt_mermaid()
