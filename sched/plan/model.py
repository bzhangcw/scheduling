# ....................
# @license: %MIT License%:~ http://www.opensource.org/licenses/MIT
# @project: plan
# @file: /model.py
# @created: Monday, 25th May 2020
# @author: brentian (chuwzhang@gmail.com)
# @modified: brentian (chuwzhang@gmail.com>)
#    Monday, 25th May 2020 10:24:18 am
# ....................
# @description:
#
# HIGH-TO-MID LEVEL PLANNING
#
# The planning model to generate a weekly production plan;
#    combines the MRP the AP (Advanced Planning) systems
#    it takes into account:
#    BOM (bill of materials), lead time, ...


import random
from collections import namedtuple
from typing import *

from sched.util import *


class Plan:
  """
   An instance of Production Planning Problem
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

  def __init__(self,
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

  @staticmethod
  def rd_instance(m: int, n: int, mu: float = 2, density: float = 0.8):
    """generate a random planning instance by modeling the BOM by a directed graph
          generally, the graph should be a DAG
          for each layer in 1..m, has a random number of items (uniform 1-n)
          the l

      Arguments:
        m {int} -- num of layers
        n {int} -- num of items in each layer


      Keyword Arguments:
          mu {float} -- upper bound of edge weight, the multiplier for the bom pairs (default: {2})
          density {float} -- probability of having a edge in the bipartite subgraph (default: {0.8})
      """
    nodes = {i: [j for j in range(random.randint(1, n))] for i in range(m)}
    edges = {
      (f'{j}#{i}', f'{j1}#{i1}'): random.random() * mu
      for i, i1 in zip(range(m)[:-1], range(m)[1:])
      for j in nodes[i]
      for j1 in nodes[i1]
      if random.random() > 1 - density
    }
    return edges


# alias
plan_random_instance = Plan.rd_instance

if __name__ == '__main__':
  edges = plan_random_instance(4, 5, 2, 0.8)
  data = bom_to_graph_mermaid(edges)
  render_meimaid_html(
    template_path=f'{UTIL_ASSET_PATH}/mermaid.template',
    record_path='',
    record_ls=data,
    fp='/tmp/bom.html')
