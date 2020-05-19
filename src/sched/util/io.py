#
# Module defining the instances
#   of a Scheduling Problem,
#   the Job, Machine, Task et cetera.
#
# @author: chuwen <chuwen@shanshu.ai>
import numpy as np
import pandas as pd


class Instance(object):
    """
    skeleton object for air cargo model
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
    The Job object, maybe upper level `mfg`
    """
    __slots__ = [
        'idx', 'quantity', 'item',
        'release', 'due',
        'start', 'end',
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        # check sufficiency
        return f"T@{self.idx}"

    def __lt__(self, other):
        return self.idx < other.idx


class ColUtil:
    CLS_MAPPING = {"F": 5, "E": 4, "D2": 3, "D1": 2, "C": 1}

    @classmethod
    def cls_to_num(cls, col):
        return cls.CLS_MAPPING.get(col, 1)

    @classmethod
    def taxiway_to_region(cls, col):
        try:
            # todo; use regex instead
            return col[1]
        except Exception as e:
            return col


# alias
cul = ColUtil


@np.vectorize
def serialize(col):
    return str(col)
