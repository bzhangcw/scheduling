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
def compute():
    m, n, p, d = 5, 10, 1, 0.8
    jobs, machines = JSP.rd_instance(m, n, copy=p, density=d)
    jsp = JSP(jobs, machines)
    jsp.create_cp_model(max_sec=500, num_workers=10)
    jsp.cp_to_gantt_mermaid()
    pass