
from schedule import Schedule

# given project (that has already been applied to temporal_analysis function), returns a resource-feasible schedule.
def nongreedy_heuristic(project):
    ### Initialise empty schedule object ready to be populated ###
    schedule = Schedule(project)
    ### Order tasks by ES from temporal analysis
    task_order = [task for task in project.tasks.values()]
    task_order.sort(key=lambda x: x.ES)
#    print([task.id for task in activity_order])
    ### Start tasks according to above order with max duration/min resource allocation
    for task in task_order:
        task_start = int(task.ES)
        task_duration = int(project.temporal_network[task.id][task.id][0][1][1])
        task_finish = task_start + task_duration
        schedule.task_starts[task.id] = task_start
        schedule.task_ends[task.id] = task_finish
        for r in range(len(project.R_max)):
            if task.q_min[r] != 0:
                resource_applied = task.w/task_duration
                schedule.task_resource_usage_changes[r][task.id][task_start] = 1
                schedule.task_resource_usage_changes[r][task.id][task_finish] = 1
                ### Updating task_resource_usage ###
                for t in range(task_start, task_finish):
                    schedule.task_resource_usage[r][task.id][t] = resource_applied
                    schedule.resource_availability[r][t] -= resource_applied
    print(schedule.task_resource_usage[0][1])
    print(schedule.task_resource_usage[0][2])
    print(schedule.task_resource_usage[0][3])
    print(schedule.resource_availability[0])


