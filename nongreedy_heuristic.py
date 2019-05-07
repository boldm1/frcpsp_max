
from numpy import *

from schedule import Schedule

from temporal_analysis import temporal_analysis

# given project (that has already been applied to temporal_analysis function), returns a resource-feasible schedule.
def nongreedy_heuristic(project):
    ### Order tasks by ES from temporal analysis
    task_order = [task for task in project.tasks.values()]
    task_order.sort(key=lambda x: x.ES)
#    print([task.id for task in activity_order])
    ### Initialise empty schedule object ready to be populated ###
    schedule = Schedule(project)
    ### Start tasks according to above order with max duration/min resource allocation
    for task in task_order:
        if schedule_task(task, project, schedule):
            return(1)
    print("Task 1 resource usage: ", schedule.task_resource_usage[0][1])
    print("Task 2 resource usage: ", schedule.task_resource_usage[0][2])
    print("Task 3 resource usage: ", schedule.task_resource_usage[0][3])
    print(schedule.resource_availability[0])


def schedule_task(task, project, schedule, attempt = 0):
    attempt += 1
    task_start = int(task.ES+attempt-1)
    task_duration = int(task.d_max) # longest resource and time feasible duration
    task_finish = task_start + task_duration
    ### Initialise temporary current schedule ###
    task_resource_usage = schedule.task_resource_usage
    task_resource_usage_changes = schedule.task_resource_usage_changes
    resource_availability = schedule.resource_availability
    for r in range(len(task.q_min)): # number of resources
        if task.q_min[r] != 0:
            resource_applied = int(task.w/task_duration)
            for t in range(task_start, task_finish):
                if schedule.resource_availability[r][t] < resource_applied:
                    schedule_task(task, project, schedule, attempt)
                    return
                else:
                    resource_availability[r][t] -= resource_applied
                    task_resource_usage[r][task.id][t] = resource_applied
            print(resource_availability[0])
            schedule.task_resource_usage_changes[r][task.id][task_start] = 1
            schedule.task_resource_usage_changes[r][task.id][task_finish] = 1
            schedule.task_resource_usage = task_resource_usage
    ### updating dgraph given actual task start ###
    project.dgraph[0][task.id][0][0] = task_start
    project.dgraph[task.id][0][0][0] = -task_start
    if temporal_analysis(project):
        return(1)




