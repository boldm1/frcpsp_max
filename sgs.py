import math
from numpy import *
from copy import deepcopy

#from temporal_analysis import temporal_analysis
from schedule import Schedule

# attempt to construct a schedule given an activity list representation
def sgs(project, alr):
    schedule = Schedule(project)
    for task_id in alr:
        task = project.tasks[task_id]
        schedule = greedily_schedule_task(task, project, schedule)
        # if greedy scheduling of task fails (i.e. misses max. time-lag)
        if schedule == 1:
#            print('greedy scheduling has failed')
            return 1
        else:
            ### update dgraph given actual task start ###
            schedule.dgraph[0][task_id][0][0] = schedule.task_starts[task_id]
            schedule.dgraph[task_id][0][0][0] = -schedule.task_starts[task_id]
            schedule.temporal_analysis()
#    print('a feasible schedule has been found')
    return schedule

def greedily_schedule_task(task, project, schedule, counter=0):
    task_start = task.ES + counter
    ### Initialise temporary current schedule ###
    task_resource_usage = deepcopy(schedule.task_resource_usage)
    resource_availability = deepcopy(schedule.resource_availability)
    t = task_start
    zeta = task.w # work-content still to be processed
    l = project.l_min # time since last change in resource allocation
    n_resources = len(project.R_max)
    while zeta > 0:
        # if time-feasible windows has been missed
        if task_start > task.LS:
#            print("time-feasible window of activity %d has been missed by %d time units" %(task.id, task_start - task.LS))
            # return failure
            return 1
        resource_available = [resource_availability[r][t] for r in range(n_resources)]
        q = [None for r in range(n_resources)] # resource allocation to task at time t
        for r in range(n_resources):
            # if not enough resource at time t
            if resource_available[r] < task.q_min[r]: 
#                print("can't schedule task %d at time %d" %(task.id, t))
                # try starting activity next period
                return greedily_schedule_task(task, project, schedule, counter+1)
        ### principle resource allocation ###
        # if task has not yet started
        if t == task_start:
            q[0] = min(resource_available[0], task.q_max[0])
            l = 1
        else:
            # if min. block length has been satisfied
            if l >= project.l_min:
                # if at least enough resource to continue current block
                if resource_available[0] >= task_resource_usage[0][task.id][t-1]:
                    q[0] = min(resource_available[0], task.q_max[0], zeta/project.l_min)
                    # if changing resource allocation is better
                    if (math.ceil(zeta/q[0]) >= project.l_min) and (math.ceil(zeta/q[0]) < math.ceil(zeta/task_resource_usage[0][task.id][t-1])): 
                        # the above value of q is kept
                        l = 1
                    # if changing resource allocation isn't better
                    else:
                        # continue previous block
                        q[0] = task_resource_usage[0][task.id][t-1]
                        l += 1
                # if there is not enough resource to continue current block
                else:
                    # new block started with lower resource allocation than previous block
                    q[0] = resource_available[0]
                    l = 1
            # min. block length not yet satisfied -> continue block
            else:
                # continue last block
                q[0] = task_resource_usage[0][task.id][t-1]
                l += 1
        ### dependent resource allocation ###
        q = dependent_resource_allocation(task, q, resource_available)
        ### independent resource allocation ###
        for r in task.r_ind:
            q[r] = task.q_min[r] 
        ### updating information ###
        for r in range(n_resources):
            task_resource_usage[r][task.id][t] = q[r]
            resource_availability[r][t] -= q[r]
        zeta -= q[0]
        t += 1
#    print('Task %d has been scheduled at time %d' %(task.id, task_start))
    schedule.tasks_scheduled.append(task)
    schedule.task_starts[task.id] = task_start
    schedule.task_ends[task.id] = t
    for r in range(n_resources):
        schedule.task_resource_usage[r][task.id] = task_resource_usage[r][task.id]
        schedule.resource_availability[r] = resource_availability[r]
        schedule.makespan = max(schedule.task_ends.values())
    return schedule

# checks that current principle resource allocation is feasible for dependent resources. If not, calculates new feasible principle resource allocation
def dependent_resource_allocation(task, q, resource_available):
    for r in task.r_dep:
        q[r] = task.alpha[r]*q[0] + task.beta[r]
        if q[r] > resource_available[r]:
            q[r] = resource_available[r]
            # re-calculate principle resource allocation
            q[0] = (q[r] - task.beta[r])/task.alpha[r]
            # re-calculate dependent resource allocations
            q = dependent_resource_allocation(task, q, resource_available)
    return q


