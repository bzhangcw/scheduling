import random
import collections

from sched.jobshop.helper import *
import sched.jobshop.deprecated.model as jsp_dep


class JSP:
    """
    An instance of Job Shop Scheduling Problem
    """

    def __init__(self, jobs=None, machines=None, **kwargs):
        if not (jobs and machines):
            pass

    logger = logging.getLogger(f"{__package__}")

    @staticmethod
    def rd_instance(m: int, n: int,
                    copy: int = 1,
                    density: float = 0.8):
        """
        :param density:
        :param copy:
        :param style:
            - non-f, regular jsp
            - f, fjsp, flexible jsp, for which each machine has copies
        :param m: num of jobs
        :param n: num of machines (actually groups)
        :return: a JSP instance
        """
        # m = [Job(idx=i) for i in range(m)]
        # n = [Machine(idx=i) for i in range(n)]

        jobs = {i: JSPJob(idx=i, release=0, due=100) for i in range(m)}
        groups = [i for i in range(n)]
        for i in range(m):
            # shuffling routes
            random.shuffle(groups)
            tasks = [JSPTask(idx=idx, machine=g, duration=random.randint(1, 5))
                     for idx, g in enumerate(groups) if
                     random.random() >= 1 - density]
            jobs[i].tasks = tasks
        machines = {g: [JSPMachine(idx=idx, group=g)
                        for idx in range(random.randint(1, copy))]
                    for g in groups}
        return jobs, machines

    # aliases
    jsp_generate_random_instance = rd_instance


if __name__ == '__main__':
    m, n, p = 5, 3, 3
    jobs, machines = JSP.rd_instance(m, n, p, density=
    0.8)
