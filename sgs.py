import math

from schedule import Schedule
from temporal_analysis import temporal_analysis

# considering just a single resource (the work-content resource 0)!!

#attempts to construct a schedule given an activity list representation
def sgs(project, alr):
    schedule = Schedule(project)
    for task in alr:
        greedily_schedule_task(task, project, schedule)
    print("Task 1 resource usage: ", schedule.task_resource_usage[0][1])
    print("Task 2 resource usage: ", schedule.task_resource_usage[0][2])
    print("Task 3 resource usage: ", schedule.task_resource_usage[0][3])
    print(schedule.resource_availability[0])

def greedily_schedule_task(task, project, schedule, counter=0):
    task_start = task.ES+counter
    ### Initialise temporary current schedule ###
    task_resource_usage = schedule.task_resource_usage
    task_resource_usage_changes = schedule.task_resource_usage_changes
    resource_availability = schedule.resource_availability
    
    t = task_start
    zeta = task.w # work-content remaining (still to be processed)
    l = project.l_min # time since last change in resource allocation
    while zeta > 0:
        resource_available = resource_availability[0][t]
        # not enough resource at time t
        if resource_available < task.q_min[0]:
            print("can't schedule task %d at time %d" %(task.id, t))
            greedily_schedule_task(task, project, schedule, counter+1)
            return
        else:
            # if task has not yet started
            if t == task_start:
                q = min(resource_available, task.q_max[0])
                l = 1
            else:
                # if min. block length has been satisfied
                if l >= project.l_min:
                    # if at least enough resource to continue current block
                    if resource_available >= task_resource_usage[0][task.id][t-1]:
                        q = min(resource_available, task.q_max[0], zeta/task_resource_usage[0][task.id][t-1])
                        # if changing resource allocation is better
                        if (math.ceil(zeta/q) >= project.l_min) and (math.ceil(zeta/q) < math.ceil(zeta/task_resource_usage[0][task.id][t-1])): 
                            # the above value of q is kept
                            l = 1
                        # if changing resource allocation isn't better
                        else:
                            # continue previous block
                            q = task_resource_usage[0][task.id][t-1]
                            l += 1
                    # if there is not enough resource to continue current block
                    else:
                        # new block started with lower resource allocation than previous block
                        q = resource_available
                        l = 1
                # min. block length not yet satisfied -> continue block
                else:
                    # continue last block
                    q = task_resource_usage[0][task.id][t-1]
                    l += 1
        task_resource_usage[0][task.id][t] = q
        resource_availability[0][t] -= q
        zeta -= q
        t += 1




#    while zeta > 0.1:
#        # if min. block length has been satisfied
#        if l >= project.l_min:
#            resource_available = resource_availability[0][t]
#            if resource_available < task.q_min[0]:
#                greedily_schedule_task(task, project, schedule, counter+1)
#                return
#            else:
#                if resource_available >= task_resource_usage[0][task.id][t-1]:
#                    q = min(resource_available, task.q_max[0], zeta/project.l_min)
#                    if (math.ceil(zeta/q) >= project.l_min) and (math.ceil(zeta/q) < math.ceil(zeta/task_resource_usage[0][task.id][t-1])):
#                        task_resource_usage[0][task.id][t] = q
#                    else:
#                        task_resource_usage[0][task.id][t] = task_resource_usage[0][task.id][t]
#                else:
#                    task_resource_usage[0][task.id][t] = resource_available
#                resource_availability[0][t] -= task_resource_usage[0][task.id][t]
#                zeta -= task_resource_usage[0][task.id][t]
#                if task_resource_usage[0][task.id][t] == task_resource_usage[0][task.id][t-1]:
#                    l += 1
#                else:
#                    l = 1
#        # if min. block length has not yet been satisfied
#        else:
#            task_resource_usage[0][task.id][t] = task_resource_usage[0][task.id][t-1]
#            resource_availability[0][t] -= task_resource_usage[0][task.id][t]
#            zeta -= task_resource_usage[0][task.id][t]
#            l += 1
#        # if there are not enough resources to schedule activity at time t
#        if resource_availability[0][t] < 0:
#            greedily_schedule_task(task, project, schedule, counter+1)
#            return
#        else:
#            t += 1
#

