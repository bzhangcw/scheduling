#
import functools
import random
import pickle
import time
from collections import namedtuple

from sched.util import *

__package__ = 'sched.para'


class Parallel(Problem):
  """
   An instance of Parallel Machine Scheduling Problem
  """

  def cp_create_model(self, *args, **kwargs):
    pass

  def cp_extract_sol(self, *args, **kwargs):
    pass

  def mp_create_model(self, *args, **kwargs):
    pass

  def mp_extract_sol(self, *args, **kwargs):
    pass

  def dump_instance(self, path, protocol):
    pass

  @staticmethod
  def rd_instance(*args):
    pass
