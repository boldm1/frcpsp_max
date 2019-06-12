import math
import random
import more_itertools as mit
from copy import deepcopy

#from schedule import Schedule
from sgs import sgs

def evolutionary_algorithm(project):
    init_pop = get_init_pop(project)

#    init_pop.sort(key=lambda alr: [task.id for task in alr])
#    current_best_makespan = 10000
#    for alr in init_pop:
#        print([task.id for task in alr])
#        schedule = sgs(project, alr)
#        print('returned schedule', schedule)
#        if schedule != 1:
#            makespan = max(schedule.task_ends.values())
#            print(makespan)
#            if makespan < current_best_makespan:
#                current_best_makespan = makespan
#                current_best_schedule = schedule
##        else:
##            print('This alr cannot be scheduled')
#    solution = current_best_schedule
#    print(solution.task_starts)
#    print(solution.task_ends)

#    for alr in init_pop:
#        alr1, alr2 = random.sample(init_pop, 2)
    
    alr1 = [project.tasks[i] for i in [0,1,3,2,4,5,6,7,8]]
    alr2 = [project.tasks[i] for i in [0,2,3,4,5,6,1,7,8]]
    alr = [0,1,2,3,4,5,6,7,8]
    crossover(project, alr, alr1, alr2)

def crossover(project, alr, alr1, alr2):
    sublists = get_conglomerate_sublists(project, alr1, alr2)
    suitable_range = get_suitable_range(project, sublists)
    new_alr = create_new_alr(project, alr, suitable_range)

def create_new_alr(project, alr, suitable_range):
    stuff...

def get_suitable_range(project, sublists):
    indices_available = [i for i in range(len(sublists))]
    sublists_graph = get_sublists_graph(project, sublists)
    suitable_range = []
    while indices_available != []:
        index = random.choice(indices_available) # randomly choose sublist (index)
        sublist_a = sublists[index]
        suitable_range.append(sublist_a)
        indices_available = [i for i in indices_available if i in sublists_graph[index]]
    print([[task.id for task in sublist] for sublist in suitable_range])
    return(suitable_range)

        
def get_sublists_graph(project, sublists):
    sublists_graph = {i:[] for i in range(len(sublists))}
    for i in range(len(sublists)):
        for j in range(len(sublists)):
            if edge_check(project, sublists[i], sublists[j]) == True:
                sublists_graph[i].append(j)
#    print(sublists_graph)
    return(sublists_graph)

# returns true if there is an edge between the two given sublists in the sublist graph
def edge_check(project, sublist1, sublist2):
    prec_12 = False
    prec_21 = False
    if set(sublist1).isdisjoint(sublist2):
        for task_i in sublist1:
            successors_i = [successors[0] for successors in task_i.successors[0]]
            for task_j in sublist2:
                successors_j = [successors[0] for successors in task_j.successors[0]]
                if (task_j.id in successors_i):
                    prec_12 = True
                if (task_i.id in successors_j):
                    prec_21 = True
        if (prec_12 == True) and (prec_21 == False):
            return True
        elif (prec_12 == False) and (prec_21 == False):
            return True
    return False

# randomly splits the conglomerate partitions of two activity list representations and returns a list of sublists 
def get_conglomerate_sublists(project, alr1, alr2):
    sublists = []
    alr1_partition = get_conglomerate_partition(project, alr1)
    for list in alr1_partition:
        sublists.append(list)
    alr2_partition = get_conglomerate_partition(project, alr2)
    for list in alr2_partition:
        sublists.append(list)
    return sublists

# partitions activity list representation based on conglomerates
def get_conglomerate_partition(project, alr):
    project_cycles = [cycle[:-1] for cycle in deepcopy(project.cycles)]
    n = len(alr)
    n_cycles = len(project.cycles)
    i = 0
    inside_CON = 0 # indicates if inside conglomerate
    c_in_CON = [] # indices of uncompleted cycles in current conglomerate
    sublists = [] # list of sublists
    n_sublists = 0 # number of sublists
    new_sublist = 1 # indicates that a new sublist is to begin
    while i < n:
        if inside_CON == 0:
            # continue up until first activity in a cycle
            while (i < n) and ([alr[i].id for cycle in project_cycles if alr[i].id in cycle] == []):
                if new_sublist == 1:
                    sublists.append([alr[i]])
                    n_sublists += 1
                    new_sublist = 0
                else:
                    sublists[n_sublists-1].append(alr[i])
                i += 1
            if i == n:
                break
            # for activities that are in a cycle...
            # get index of cycle to which alr[i] belongs
            j = next(index for index,cycle in enumerate(project_cycles) if alr[i].id in cycle)
            c_in_CON.append(j)
            inside_CON = 1
            project_cycles[j].remove(alr[i].id)
            sublists.append([alr[i]])
            n_sublists += 1
            i += 1
        elif inside_CON == 1:
            # continue through activities that are not in a cycle
            while [alr[i].id for cycle in project_cycles if alr[i].id in cycle] == []:
                sublists[n_sublists-1].append(alr[i])
                i += 1  
            # for activities that are in a cycle...
            # get index of cycles to which alr[i] belongs
            j_set = [index for index,cycle in enumerate(project_cycles) if alr[i].id in cycle]
            # remove activity from cycles
            for j in j_set:
                sublists[n_sublists-1].append(alr[i])
                project_cycles[j].remove(alr[i].id)
                # if new cycle has been encountered
                if j not in c_in_CON:
                    c_in_CON.append(j)
                    sublists[n_sublists-1].append(alr[i])
                # if we have come to the end of a cycle
                if project_cycles[j] == []:
                    c_in_CON.remove(j)
                # if we have come to the end of a conglomerate
                if c_in_CON == []:
                    inside_CON = 0
                    new_sublist = 1
            i += 1
    return sublists



def get_init_pop(project):
    population = []
    # creating a population of 10 different activity list representations
    # BEWARE: no error catch for a larger-than-possible population
    attempt = 0
    while attempt < 100 and len(population) < 20: 
        attempt += 1
        alr = generate_alr(project)
        if alr not in population:
            population.append(alr)
    if attempt >= 100:
        print('Could not get a population of size 20. Population is of size %d instead.' %len(population))
    return(population)

###################################################################
### random topological ordering wrt relations with +ve min. lag ###
###################################################################

def generate_alr(project):
    ordered_tasks = []
    visited = [False for i in range(len(project.tasks))]
    while False in visited:
        task = random.choice(project.tasks)
        if visited[task.id] == False:
            top_order_task(project, task, visited, ordered_tasks)
    return(ordered_tasks)

def top_order_task(project, task, visited, ordered_tasks):
    visited[task.id] = True
    ### ONLY S->S PRECEDENCE RELATIONSHIPS ARE CONSIDERED ###
    successor_ids = [successor[0] for successor in task.successors[0] if successor[1] >= 0]
    while False in [v for i,v in enumerate(visited) if i in successor_ids]:
        successor_id = random.choice(successor_ids)
        if visited[successor_id] == False:
            successor = project.tasks[successor_id]
            top_order_task(project, successor, visited, ordered_tasks)
    ordered_tasks.insert(0, task)

###################################################################



#        while schedule.tasks_scheduled != N:
#            E = [task for task in N if task.predecessors in schedule.tasks_scheduled]
#            print(E)    

#    V_ids = [task.id for task in V]
#    E # eligible tasks
#    S # scheduled tasks
#    for i in range(100): # population size of 100
#        schedule = Schedule(project)
#        # calculating task priorities (longest path following)
#        for task in N:
#            task.LPF = math.ceil(task.w/task.q_max) + max([successor.LPF for successor in task.successors_raw)
#        
#        ### getting eligible activities ###
#        for i in V_ids:
#            for j in V_ids:
#                if project.tasks[j].successors
#
#
#        for j in N_ids:
#            task = random.choice(N, 1, p=[task.LPF for task in N])
#        
#        # randomly sample tasks based on priority rule




#def get_fitness

#def crossover

