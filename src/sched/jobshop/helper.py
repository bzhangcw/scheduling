from sched.util import *
from typing import *

from ortools.sat.python import cp_model
import time
import logging

__package__ = 'sched.jobshop'
logger = logging.getLogger(__package__)


# JSP instances
class JSPJob(Job):
    __slots__ = [
        'idx',
        'release', 'due',
        'start', 'end',
        'tasks'
        # constraint programming
        'cp_start_var', 'cp_end_var',
    ]


class JSPMachine(Machine):
    """
    A machine in the JSP model may also have a group number,
        a task of a job may be pointed to the group, i.e.,
        any machine amongst the group can be used to do the task,
        see the definition of Flexible Job Shop Scheduling Problem.

    Note the group may also be referred to as "station, job unit, etc.
    """
    __slots__ = [
        'idx',
        'group'
    ]


class JSPTask(Task):
    __slots__ = [
        'idx',
        'machine',
        'start', 'end', 'duration',
        # constraint programming
        'cp_dur_var', 'cp_start_var', 'cp_end_var', 'cp_int_var',
        # mathematic programming
    ]


# or-tools helper classes
class SatCallBack(cp_model.CpSolverSolutionCallback):
    """(Constraint Programming)
        Satisfactory solver callback
    """
    logger = logging.getLogger(f"{__package__}.{__name__}")

    def __init__(self, v, solution_limit=20, time_limit=100):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.v = v
        self.__solution_count = 0
        self.__solution_limit = solution_limit
        self.__start_time = time.time()
        self.__time_limit = time_limit

    def on_solution_callback(self):
        self.__solution_count += 1
        current_time = time.time()

        logger.info(f'%.2f - {self.v} :={self.Value(self.v)}\n' % self.WallTime())
        if self.__solution_count >= self.__solution_limit:
            logger.info('Stop search after %i solutions' % self.__solution_limit)
            self.StopSearch()
        if current_time - self.__start_time >= self.__time_limit:
            logger.info('Stop search after %i seconds' % self.__time_limit)
            self.StopSearch()

    def solution_count(self):
        return self.__solution_count
