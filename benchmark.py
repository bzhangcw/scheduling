# ....................
# @license: %MIT License%:~ http://www.opensource.org/licenses/MIT
# @project: jobshop
# @file: /benchmark.py
# @created: Monday, 25th May 2020
# @author: brentian (chuwzhang@gmail.com)
# @modified: brentian (chuwzhang@gmail.com>)
#    Monday, 25th May 2020 10:43:18 am
# ....................
# @description:
# benchmark of JSP, on size
from sched import *


def main(problem, sizes, *args, **kwargs):
    m, n, p, d = 50, 20, 2, 0.5
    jobs, machines = JSP.rd_instance(m, n, copy=p, density=d)
    jsp = JSP(jobs, machines)
    jsp.cp_create_model(max_sec=500, num_workers=2, max_sol=100)
    # jsp.create_cp_model(max_sec=500, num_workers=2, para=True)
    jsp.cp_to_gantt_mermaid()