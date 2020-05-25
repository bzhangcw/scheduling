from sched import *

if __name__ == '__main__':
   m, n, p, d = 50, 20, 2, 0.5
   jobs, machines = JSP.rd_instance(m, n, copy=p, density=d)
   jsp = JSP(jobs, machines)
   jsp.cp_create_model(max_sec=500, num_workers=2, max_sol=100)
   # jsp.create_cp_model(max_sec=500, num_workers=2, para=True)
   jsp.cp_to_gantt_mermaid()
