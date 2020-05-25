#
# Module defining the instances
#   of a Scheduling Problem,
#   the Job, Machine, Task et cetera.
#
# @author: chuwen <chuwen@shanshu.ai>
import os

import numpy as np

UTIL_MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
UTIL_ASSET_PATH = os.path.join(UTIL_MODULE_PATH, 'assets')


class Instance(object):
   """
   skeleton object
   """

   def __init__(self, **kwargs):
      for k, v in kwargs.items():
         setattr(self, k, v)

   def __hash__(self):
      return self.__str__().__hash__()

   def __repr__(self):
      return self.__str__()


class Machine(Instance):
   __slots__ = [
      'idx'
   ]

   def __init__(self, **kwargs):
      super().__init__(**kwargs)

   def __str__(self):
      # check sufficiency
      return f"M@{self.idx}"

   def __lt__(self, other):
      return self.idx < other.idx


class Job(Instance):
   """
   The Job object
   """
   __slots__ = [
      'idx',
      'release', 'due',
      'start', 'end',
      'tasks'
   ]

   def __init__(self, **kwargs):
      super().__init__(**kwargs)

   def __str__(self):
      # check sufficiency
      return f"J@{self.idx}"

   def __lt__(self, other):
      return self.idx < other.idx


# aka Operation
class Task(Instance):
   __slots__ = [
      'idx',
      'start', 'end',
   ]

   def __init__(self, **kwargs):
      super().__init__(**kwargs)

   def __str__(self):
      # check sufficiency
      return f"T@{self.idx}"

   def __lt__(self, other):
      return self.idx < other.idx


@np.vectorize
def serialize(col):
   return str(col)
