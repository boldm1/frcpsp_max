import math
from numpy import *
from copy import deepcopy

from temporal_analysis import temporal_analysis

# considering just a single resource (the work-content resource 0)!!

#attempts to construct a schedule given an activity list representation
def sgs(project, alr):
    conglomerates = get_conglomerates(project, alr)
    print(conglomerates)
#    for task in alr:

def get_conglomerates(project, alr):
    project_cycles = [cycle[:-1] for cycle in deepcopy(project.cycles)]
    n = len(alr)
    n_cycles = len(project.cycles)
    i = 0
    inside_CON = 0 # indicates if inside conglomerate
    c_in_CON = [] # indices of uncompleted cycles in current conglomerate
    n_CON = 0 # number of conglomerates
    conglomerates = [] # list of conglomerates
    while i < n:
        if inside_CON == 0:
            # continue up until first activity in a cycle
            while (i < n) and ([alr[i].id for cycle in project_cycles if alr[i].id in cycle] == []):
                i += 1
            if i == n:
                return conglomerates
            # for activities that are in a cycle...
            # get index of cycle to which alr[i] belongs
            j = next(index for index,cycle in enumerate(project_cycles) if alr[i].id in cycle)
            c_in_CON.append(j)
            inside_CON = 1
            n_CON += 1
            conglomerates.append([alr[i].id])
        elif inside_CON == 1:
            # continue through activities that are not in a cycle
            while [alr[i].id for cycle in project_cycles if alr[i].id in cycle] == []:
                conglomerates[n_CON-1].append(alr[i].id)
                i += 1  
            # for activities that are in a cycle...
            # get index of cycle to which alr[i] belongs
            j_set = [index for index,cycle in enumerate(project_cycles) if alr[i].id in cycle]
#            j = next(index for index,cycle in enumerate(project_cycles) if alr[i].id in cycle)
#            print('j', j)
            # remove activity from cycle
            for j in j_set:
                project_cycles[j].remove(alr[i].id)
                # if new cycle has been encountered
                if j not in c_in_CON:
                    c_in_CON.append(j)
                    conglomerates[n_CON-1].append(alr[i].id)
                # if we have come to the end of a cycle
                if project_cycles[j] == []:
                    c_in_CON.remove(j)
                # if we have come to the end of a conglomerate
                if c_in_CON == []:
                    inside_CON = 0
            i += 1
    return conglomerates


                





#attempts to construct a schedule given an activity list representation
def old_sgs(project, schedule, alr, unscheduling_counter):
    for task in alr:
        delta = greedily_schedule_task(task, project, schedule)
        # if greedily_schedule_task fails (misses max. time-lag)
        if delta is not None:     
            print('greedy scheduling has failed')
            print('attempting unscheduling step')
            unscheduling_counter += 1
            if unscheduling(task, project, schedule, delta, unscheduling_counter):
                print('unscheduling has failed. project is infeasible')
                return 1
            else:
                # removing already scheduled tasks from alr
                for task in alr:
                    if task in schedule.tasks_scheduled:
                        alr.remove(task)
                # attempt to schedule remaining activities
                return sgs(project, schedule, alr, unscheduling_counter)
        # if greedily_schedule_task succeeds
        else:
            print("Task %d resource usage: " %task.id, schedule.task_resource_usage[0][task.id])
            ### update dgraph given actual task start ###
            project.dgraph[0][task.id][0][0] = schedule.task_starts[task.id]
            project.dgraph[task.id][0][0][0] = -schedule.task_starts[task.id]
            temporal_analysis(project)

def greedily_schedule_task(task, project, schedule, counter=0):
    task_start = task.ES+counter
    ### Initialise temporary current schedule ###
    task_resource_usage = deepcopy(schedule.task_resource_usage)
    resource_availability = deepcopy(schedule.resource_availability)
    t = task_start
    zeta = task.w # work-content remaining (still to be processed)
    l = project.l_min # time since last change in resource allocation
    while zeta > 0:
        resource_available = resource_availability[0][t]
        # if time-feasible windows has been missed
        if task_start > task.LS:
            print("time-feasible window of activity %d has been missed by %d time units" %(task.id, task_start - task.LS))
            # return failure
            return task_start - task.LS
        # if not enough resource at time t
        if resource_available < task.q_min[0]:
            print("can't schedule task %d at time %d" %(task.id, t))
            # try starting activity next period
            return greedily_schedule_task(task, project, schedule, counter+1)
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
                        q = min(resource_available, task.q_max[0], zeta/project.l_min)
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
    schedule.tasks_scheduled.append(task)
    schedule.task_starts[task.id] = task_start
    schedule.task_ends[task.id] = t
    schedule.task_resource_usage[0][task.id] = task_resource_usage[0][task.id]
    schedule.resource_availability[0] = resource_availability[0]

def unscheduling(task_star, project, schedule, delta, counter, u_max=10):
    # find activities that determine LS_task
    U = []
    for task in schedule.tasks_scheduled:
        # if LS_j = S_i + SS^max_ij
        if task.id != 0 and task_star.LS == schedule.task_starts[task.id] - project.dgraph[task_star.id][task.id][0][0]:
            U.append(task)
    # if there is no feasible solution
    if U == []:
        print('U is empty')
        return 1
    elif counter > u_max:
        print('maximum number of unscheduling steps has been exceeded!')
        return 1
    else:
        U_min_start = min([schedule.task_starts[task.id] for task in U])
        # right-shift and unschedule activites in U
        for task in U:
            task.ES = schedule.task_starts[task.id] + delta
            for t in range(schedule.task_starts[task.id],schedule.task_ends[task.id]+1):
                schedule.resource_availability[0][t] += schedule.task_resource_usage[0][task.id][t]
            schedule.task_resource_usage[0][task.id] = [0 for t in range(project.T)]
            del schedule.task_starts[task.id]
            del schedule.task_ends[task.id]
            schedule.tasks_scheduled.remove(task)
        # unschedule all activities i with S_i > min(S_h for h in U)
        for task in schedule.tasks_scheduled:
            if schedule.task_starts[task.id] > U_min_start:
                for t in range(schedule.task_starts[task.id],schedule.task_ends[task.id]+1):
                    schedule.resource_availability[0][t] += schedule.task_reource_usage[0][task.id][t]
                schedule.task_resource_usage[0][task.id] = [0 for t in range(project.T)]
                del schedule.task_starts[task.id]
                del schedule.task_ends[task.id]
                schedule.tasks_scheduled.remove(task.id)
        # update ES and LS having unscheduled tasks
        for i in project.tasks:
            for j in project.tasks:
                if (j != i) and (project.tasks[i] not in schedule.tasks_scheduled):
                    project.dgraph[i][j] = project.init_dgraph[i][j]
        for task in U:
            project.dgraph[0][task.id][0][0] = task.ES
        temporal_analysis(project)
        # if there is no feasible solution
        if task.ES > task.LS:
            return 1


