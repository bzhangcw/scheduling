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


# @staticmethod
def rd_instance(n: int, m: int, mu: float = 2, density: float = 0.8):
    """generate a random planning instance by modeling the BOM by a directed graph
        generally, the graph should be a DAG
        for each layer in 1..m, has a random number of items (uniform 1-n) 
        the l

        the connection rate between items (probability) 

    Arguments:
        n {int} -- num of items in each layer
        m {int} -- num of layers

    Keyword Arguments:
        mu {float} -- upper bound of edge weight, the multiplier for the bom pairs (default: {2})
        density {float} -- probability of having a edge in the bipartite subgraph (default: {0.8})
    """

    pass
