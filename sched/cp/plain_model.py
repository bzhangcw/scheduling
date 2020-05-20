import random

from ortools.sat.python import cp_model


def jsp_generate_random_instance(m: int, n: int, copy=1, density: float = 0.8, style='non-f'):
    """
    :param style:
        non-f, regular jsp
        f, flexible jsp, for which each machine has copies
    :param m: num of jobs
    :param n: num of machines
    :return: a JSP instance
    """
    # m = [Job(idx=i) for i in range(m)]
    # n = [Machine(idx=i) for i in range(n)]
    jobs_data = [[(j, random.randint(1, 5))
                  for j in range(n)
                  if random.random() >= 1 - density]
                 for i in range(m)]
    if style == 'non-f':
        return jobs_data, None
    machine_cp = {i: random.randint(1, copy) for i in range(n)}
    return jobs_data, machine_cp


def jsp(m, n):
    import collections

    from ortools.sat.python import cp_model

    model = cp_model.CpModel()

    # jobs_data = [  # task = (machine_id, processing_time).
    #     [(0, 3), (1, 2), (2, 2)],  # Job0
    #     [(0, 2), (2, 1), (1, 4)],  # Job1
    #     [(1, 4), (2, 3)]  # Job2
    # ]
    jobs_data, _ = jsp_generate_random_instance(m, n)

    machines_count = 1 + max(task[0] for job in jobs_data for task in job)
    all_machines = range(machines_count)

    # Computes horizon dynamically as the sum of all durations.
    horizon = sum(task[1] for job in jobs_data for task in job)

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple('task_type', 'start end interval')
    # Named tuple to manipulate solution information.
    assigned_task_type = collections.namedtuple('assigned_task_type',
                                                'start job index duration')

    # Creates job intervals and add to the corresponding machine lists.
    all_tasks = {}
    machine_to_intervals = collections.defaultdict(list)

    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine = task[0]
            duration = task[1]
            suffix = '_%i_%i' % (job_id, task_id)
            start_var = model.NewIntVar(0, horizon, 'start' + suffix)
            end_var = model.NewIntVar(0, horizon, 'end' + suffix)
            interval_var = model.NewIntervalVar(start_var, duration, end_var,
                                                'interval' + suffix)
            all_tasks[job_id, task_id] = task_type(
                start=start_var, end=end_var, interval=interval_var)
            machine_to_intervals[machine].append(interval_var)

    # Create and add disjunctive constraints.
    for machine in all_machines:
        model.AddNoOverlap(machine_to_intervals[machine])

    # Precedences inside a job.
    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job) - 1):
            model.Add(all_tasks[job_id, task_id +
                                1].start >= all_tasks[job_id, task_id].end)

    # Makespan objective.
    obj_var = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(obj_var, [
        all_tasks[job_id, len(job) - 1].end
        for job_id, job in enumerate(jobs_data) if len(job) > 0
    ])
    model.Minimize(obj_var)

    # Solve model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        # Create one list of assigned tasks per machine.
        assigned_jobs = collections.defaultdict(list)
        for job_id, job in enumerate(jobs_data):
            for task_id, task in enumerate(job):
                machine = task[0]
                assigned_jobs[machine].append(
                    assigned_task_type(
                        start=solver.Value(all_tasks[job_id, task_id].start),
                        job=job_id,
                        index=task_id,
                        duration=task[1]))

        # Create per machine output lines.
        output = ''
        for machine in all_machines:
            # Sort by starting time.
            assigned_jobs[machine].sort()
            sol_line_tasks = 'Machine ' + str(machine) + ': '
            sol_line = '           '

            for assigned_task in assigned_jobs[machine]:
                name = 'job_%i_%i' % (assigned_task.job, assigned_task.index)
                # Add spaces to output to align columns.
                sol_line_tasks += '%-10s' % name

                start = assigned_task.start
                duration = assigned_task.duration
                sol_tmp = '[%i,%i]' % (start, start + duration)
                # Add spaces to output to align columns.
                sol_line += '%-10s' % sol_tmp

            sol_line += '\n'
            sol_line_tasks += '\n'
            output += sol_line_tasks
            output += sol_line

        # Finally print the solution found.
        print('Optimal Schedule Length: %i' % solver.ObjectiveValue())
        print(output)


class VarArraySolutionPrinterWithLimit(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, makespan, limit):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.makespan = makespan
        self.__solution_count = 0
        self.__solution_limit = limit

    def on_solution_callback(self):
        self.__solution_count += 1
        print(f'{self.WallTime()} - {self.makespan} :={self.Value(self.makespan)}\n')

        if self.__solution_count >= self.__solution_limit:
            print('Stop search after %i solutions' % self.__solution_limit)
            self.StopSearch()

    def solution_count(self):
        return self.__solution_count


def fjsp_preemptive(m, n, p, pre=False):
    import collections

    model = cp_model.CpModel()

    # jobs_data = [  # task = (machine_id, processing_time).
    #     [(0, 3), (1, 2), (2, 2)],  # Job0
    #     [(0, 2), (2, 1), (1, 4)],  # Job1
    #     [(1, 4), (2, 3)]  # Job2
    # ]
    jobs_data, mcopy = jsp_generate_random_instance(m, n, copy=p, style='f', density=0.5)

    machines_count = 1 + max(task[0] for job in jobs_data for task in job)
    all_machines = range(machines_count)

    # Computes horizon dynamically as the sum of all durations.
    horizon = sum(task[1] for job in jobs_data for task in job)

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple('task_type', 'start end interval duration')

    # Named tuple to manipulate solution information.
    assigned_task_type = collections.namedtuple('assigned_task_type',
                                                'start job index duration')

    # Creates job intervals and add to the corresponding machine lists.
    all_tasks = {}
    machine_to_intervals = collections.defaultdict(list)
    tasks_durs = collections.defaultdict(list)
    job_s = collections.defaultdict()
    job_e = collections.defaultdict()
    job_opt = collections.defaultdict(list)
    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine, duration = task
            tasks_durs[job_id, task_id].append(duration)
            suffix = f'{job_id}_{task_id}'
            start_var = model.NewIntVar(0, horizon, 'start' + suffix)
            end_var = model.NewIntVar(0, horizon, 'end' + suffix)
            job_s[job_id, task_id] = start_var
            job_e[job_id, task_id] = end_var
            for idx in range(mcopy[machine]):
                suffix = f'{job_id}_{task_id}_{idx}'
                start_var = model.NewIntVar(0, horizon, 'start' + suffix)
                end_var = model.NewIntVar(0, horizon, 'end' + suffix)
                duration_var = model.NewIntVar(0, duration, 'dur' + suffix)
                option_var = model.NewBoolVar('opt' + suffix)
                job_opt[job_id, task_id].append(option_var)
                interval_var = \
                    model.NewIntervalVar(
                        start_var, duration_var, end_var,
                        name='interval' + suffix)

                if not pre:
                    model.Add(duration_var == duration).OnlyEnforceIf(option_var)

                all_tasks[job_id, task_id, idx] = \
                    task_type(start=start_var, end=end_var,
                              duration=duration_var, interval=interval_var)
                machine_to_intervals[machine, idx].append(interval_var)
                tasks_durs[job_id, task_id].append(duration_var)
    # Create and add disjunctive constraints.
    for machine in all_machines:
        for idx in range(mcopy[machine]):
            model.AddNoOverlap(machine_to_intervals[machine, idx])

    # Preemptive or non-preemptive schedules
    if pre:
        for (job_id, task_id), v_list in tasks_durs.items():
            model.Add(sum(v_list[1:]) == v_list[0])
    else:
        for job_id, job in enumerate(jobs_data):
            for task_id, task in enumerate(job):
                model.Add(sum(job_opt[job_id, task_id]) == 1)
    # Precedences inside a job.
    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine, duration = task
            scope = [idx for idx in range(mcopy[machine])]
            model.AddMaxEquality(job_e[job_id, task_id],
                                 [all_tasks[job_id, task_id, idx].end for idx in scope])
            model.AddMinEquality(job_s[job_id, task_id],
                                 [all_tasks[job_id, task_id, idx].start for idx in scope])
        for task_id in range(len(job) - 1):
            task = job[task_id]
            model.Add(job_s[job_id, task_id + 1] >= job_e[job_id, task_id])

    # Makespan objective.
    obj_var = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(obj_var, [
        job_e[job_id, len(job) - 1]
        for job_id, job in enumerate(jobs_data) if len(job) > 0
    ])
    model.Minimize(obj_var)

    # Solve model.
    solver = cp_model.CpSolver()

    solution_printer = VarArraySolutionPrinterWithLimit(obj_var, 50)
    status = solver.SolveWithSolutionCallback(model, solution_printer)
    print('Status = %s' % solver.StatusName(status))
    print('Number of solutions found: %i' % solution_printer.solution_count())

    if status == cp_model.OPTIMAL:
        # Create one list of assigned tasks per machine.
        assigned_jobs = collections.defaultdict(list)
        for job_id, job in enumerate(jobs_data):
            for task_id, task in enumerate(job):
                machine = task[0]
                for idx in range(mcopy[machine]):
                    var_ = all_tasks[job_id, task_id, idx]
                    start = solver.Value(all_tasks[job_id, task_id, idx].start)
                    dur = solver.Value(all_tasks[job_id, task_id, idx].duration)
                    if dur > 0:
                        assigned_jobs[machine, idx].append(
                            assigned_task_type(
                                start=start,
                                job=job_id,
                                index=task_id,
                                duration=dur))

        # Create per machine output lines.
        output = ''
        for machine in all_machines:
            for idx in range(mcopy[machine]):
                # Sort by starting time.
                assigned_jobs[machine, idx].sort()
                sol_line_tasks = f'Machine:{machine}@{idx}'
                sol_line = '           '

                for assigned_task in assigned_jobs[machine, idx]:
                    name = 'job_%i_%i' % (assigned_task.job, assigned_task.index)
                    # Add spaces to output to align columns.
                    sol_line_tasks += '%-10s' % name

                    start = assigned_task.start
                    duration = assigned_task.duration
                    sol_tmp = '[%i,%i]' % (start, start + duration)
                    # Add spaces to output to align columns.
                    sol_line += '%-10s' % sol_tmp

                sol_line += '\n'
                sol_line_tasks += '\n'
                output += sol_line_tasks
                output += sol_line

        # Finally print the solution found.
        print('Optimal Schedule Length: %i' % solver.ObjectiveValue())
        print(output)
        print(1)


def fjsp(m, n, p):
    pass


fjsp_preemptive(50, 10, 5, pre=False)
# jsp(50, 10)
