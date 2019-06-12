
from pathlib import Path

from load_instance import load_instance
#from schedule import Schedule
#from temporal_analysis import temporal_analysis
#from sgs import sgs
#from plot_schedule import plot_schedule
from eva import evolutionary_algorithm


test_instances_dir = Path("test_instances")
project = load_instance(test_instances_dir/'sm_j10'/'PSP3_r1.sch')
evolutionary_algorithm(project)

#print(project.R_max)
#temporal_analysis(project)
#for task in project.tasks.values():
#   print('(task.ES,task.LS): (%d,%d)' %(task.ES,task.LS))
#    print('(task.d_min,task.d_max): (%d,%d)' %(task.d_min,task.d_max))
#    print('(task.q_min,task.q_max): (%.2f,%.2f)' %(task.q_min[0],task.q_max[0]))
#nongreedy_heuristic(project)
#alr = []
#for task in project.tasks.values():
#    alr.append(task)
#for task in project.tasks.values():
#    print(task.successors)
#unscheduling_counter = 0
#schedule = Schedule(project)
#if sgs(project, schedule, alr, unscheduling_counter):
#    print('project is infeasible')
#schedule = sgs(project, alr)
#for task in alr:
#    print('%d' %task.id, schedule.task_resource_usage[0][task.id])
##plot_schedule(schedule)
#genetic_algorithm(project)

