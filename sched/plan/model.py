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
import functools
import random
import pickle
import time
from collections import namedtuple

from sched.util import *

__package__ = 'sched.plan'


class Plan(Problem):
  """
   An instance of Production Planning Problem
  """

  __name__ = f"{__package__}.Plan"
  logger = logging.getLogger(__name__)

  instance_container = \
    namedtuple(
      'plan_instance',
      [
        'bom',
        'horizon', 'items', 'raws', 'products',
        'lead_time', 'demand', 'inventory'
      ]
    )
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
               instance,
               **kwargs):
    if not (instance):
      raise ValueError('Cannot initialize the problem')

    self.instance_data = instance

  def mp_create_model(self):
    # the mathematical formulation
    #  based on lot-sizing and network flow
    pass

  def dump_instance(self, path, protocol='pickle'):
    current_time = time.time()
    if protocol == 'pickle':
      with open(f'{path}/%d-{Plan.__name__}.pickle' % current_time, 'wb') as f:
        # todo fix this. unable to pickle an inclass namedtuple
        # switch to protobuf
        pickle.dump(self.instance_data._asdict(), f)
    else:
      raise ValueError(f"protocol: {protocol} not implemented yet")

  def cp_create_model(self, *args, **kwargs):
    pass

  def cp_extract_sol(self, *args, **kwargs):
    pass

  def mp_extract_sol(self, *args, **kwargs):
    pass

  @staticmethod
  def rd_instance(m: int,
                  n: int,
                  tau: int,
                  mu: float = 2,
                  density: float = 0.8):
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
    # items
    _nodes = {i: [j for j in range(random.randint(1, n))] for i in range(m)}
    # edges of the bom tree
    _edges = {
      (f'{j}#{i}', f'{j1}#{i1}'): random.random() * mu
      for i, i1 in zip(range(m)[:-1], range(m)[1:])
      for j in _nodes[i]
      for j1 in _nodes[i1]
      if random.random() > 1 - density
    }
    _items = functools.reduce(lambda x, y: set.union(x, y), _edges, set())
    _raws = {i for i in _items if str.endswith(i, f"#{m - 1}")}
    _products = _items.difference(_raws)
    _time_scale = range(tau)
    _inventory = {
      (i, t): random.randint(1, 10) if i in _products
      else random.randint(100, 200)
      for i in _items for t in _time_scale}
    _demand = {(i, t): random.randint(1, 100)
               for i in _items for t in _time_scale}
    _lead_time = {(i, t): random.randint(1, 5) for i in _products for t in _time_scale}

    _instance = Plan.instance_container(
      bom=_edges,
      horizon=_time_scale,
      items=_items,
      raws=_raws,
      products=_products,
      lead_time=_lead_time,
      demand=_demand,
      inventory=_inventory
    )

    return _instance


# alias
plan_random_instance = Plan.rd_instance

if __name__ == '__main__':
  instance = plan_random_instance(4, 5, 7, 2, 0.8)
  data = bom_to_graph_mermaid(instance.bom)
  render_meimaid_html(
    template_path=f'{UTIL_ASSET_PATH}/mermaid.template',
    record_path='',
    record_ls=data,
    fp='/tmp/bom.html')
