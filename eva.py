
import sys
import math
import random
import itertools
import more_itertools as mit
from copy import deepcopy
from operator import itemgetter
from plot_schedule import plot_schedule

#from schedule import Schedule
from sgs import sgs

def evolutionary_algorithm(project, pop_size, n_generations):
    init_pop = get_init_pop(project, pop_size)
    for alr in init_pop:
        print(alr)
    if init_pop == 1:
        return(1)
    solutions = []
    for alr in init_pop:
        schedule = sgs(project, alr)
        if schedule != 1:
            solutions.append((alr, schedule.makespan))
        elif schedule == 1:
            solutions.append((alr, 10000))
    if all(solution[1] == 10000 for solution in solutions):
        sys.exit('Error: No feasible solution has been found.')
    print('generation 0: ', sorted([solution[1] for solution in solutions]))
    for generation in range(1, n_generations+1):
        solutions = get_new_generation(project, solutions, pop_size)
        print('generation %d: ' %generation, sorted([solution[1] for solution in solutions]))
    sorted_solutions = sorted(solutions, key=lambda solution:solution[1])
    best_alr = sorted_solutions[0][0]
    print('best_alr', best_alr)
    schedule = sgs(project, best_alr)
    plot_schedule(schedule)

def get_new_generation(project, solutions, pop_size):
    sorted_old_solutions = sorted(solutions, key=itemgetter(1))
    new_solutions = []
    for i in range(int(pop_size/2)):
        best_sol = sorted_old_solutions[i]
        new_solutions.append(best_sol) 
    for i in range(int(pop_size/2)):
        solution1, solution2, solution3 = random.sample(new_solutions, 3)
        new_alr = crossover(project, solution1[0], solution2[0], solution3[0])
        schedule = sgs(project, new_alr)
        if schedule != 1:
            makespan = max(schedule.task_ends.values())
            new_solutions.append((new_alr, makespan))
        elif schedule == 1:
            makespan = 10000
            new_solutions.append((new_alr, makespan))
    return(new_solutions)

# given three 'parent' alrs, returns 'child' alr
def crossover(project, alr, alr1, alr2):
#    print(alr1)
#    print(alr2)
    sublists = get_conglomerate_sublists(project, alr1, alr2)
    suitable_range = get_suitable_range(project, sublists)
    new_alr = create_new_alr(project, alr, suitable_range)
    return(new_alr)

# given third parent alr and suitable range, returns new_alr, i.e. a list of task objects
def create_new_alr(project, alr, suitable_range):
#    print(alr)
    n = len(alr) - 2 # no. of non-dummy activities
    new_alr = [0] + [None for i in range(n)] + [n+1]
    ### Getting required info. ###
    # position of sublists (min. position of a task in the sublist) in alr
    p_sublists = {}
    for i in range(len(suitable_range)):
        p_sublists[i] = min(alr.index(task_id) for task_id in suitable_range[i])
    # list of ids of tasks that are not in any sublist in the suitable range
    nonsublist_tasks = [task_id for task_id in project.tasks if task_id not in list(itertools.chain.from_iterable(suitable_range))]
    # list of ids of predecessors of activities in sublists, ordered according to alr
    pred_sublists = {i:[] for i in range(len(suitable_range))}     
    for i in range(len(suitable_range)):
        for task_id in suitable_range[i]:
            pred_sublists[i].extend([predecessor for predecessor in project.tasks[task_id].SS_predecessors if predecessor not in pred_sublists[i] if predecessor not in [task_id for task_id in suitable_range[i]]])
        # order tasks in pred_sublist[i] according to their order in alr
        pred_sublists[i].sort(key = lambda x:alr.index(x))
    ### Construct sublist ###
    h = 1
#    print('third ALR parent', alr)
#    print('sublist predecessors', pred_sublists)
#    print('suitable_range', suitable_range)
#    print('p_sublists', p_sublists)
    for i in range(len(suitable_range)):
        # insert non-sublist activities
        for j in range(h, p_sublists[i]):
            if alr[j] in nonsublist_tasks and alr[j] not in new_alr:
#                print(h)
#                print(new_alr)
                new_alr[h] = alr[j]
                h += 1
        # insert predecessor activities
        for j in range(len(pred_sublists[i])):
            if pred_sublists[i][j] not in new_alr:
#                print(h)
#                print(new_alr)
                new_alr[h] = pred_sublists[i][j]
                h += 1
        # insert sublist
        for j in range(len(suitable_range[i])):
#            print(h)
#            print(new_alr)
            new_alr[h] = suitable_range[i][j]
            h += 1
    for j in range(len(alr)):
        if alr[j] not in new_alr:
#            print(h)
#            print(new_alr)
            new_alr[h] = alr[j]
            h += 1
#    print('finished alr: ', new_alr)
    return new_alr


def get_suitable_range(project, sublists):
    sublists_available = [i for i in range(len(sublists))]
    sublists_graph = get_sublists_graph(project, sublists)
    suitable_range = []
    while sublists_available != []:
        index = random.choice(sublists_available) # randomly choose sublist (index)
        suitable_range.append(sublists[index])
        sublists_available = [i for i in sublists_available if i in sublists_graph[index]]
    return(suitable_range)

        
def get_sublists_graph(project, sublists):
    sublists_graph = {i:[] for i in range(len(sublists))}
    for i in range(len(sublists)):
        for j in range(len(sublists)):
            if edge_check(project, sublists[i], sublists[j]) == True:
                sublists_graph[i].append(j)
    return(sublists_graph)

# returns true if there is an edge between the two given sublists in the sublist graph
def edge_check(project, sublist1, sublist2):
    prec_12 = False
    prec_21 = False
    if set(sublist1).isdisjoint(sublist2):
        for i in sublist1:
            successors_i = [successor for successor in project.tasks[i].SS_successors]
            for j in sublist2:
                successors_j = [successor for successor in project.tasks[j].SS_successors]
                if (j in successors_i):
                    prec_12 = True
                if (i in successors_j):
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

# partitions alr into sublists based on conglomerates
def get_conglomerate_partition(project, alr):
    project_cycles = [cycle[:-1] for cycle in deepcopy(project.cycles)]
#    print('ALR', alr)
#    print('project cycles', project_cycles)
    n = len(alr) - 2 # no. of non-dummy activities
    n_cycles = len(project_cycles)
    i = 1
    inside_CON = 0 # indicates if inside conglomerate
    c_in_CON = [] # indices of uncompleted cycles in current conglomerate
    sublists = [] # list of sublists
    n_sublists = 0 # number of sublists
    new_sublist = 1 # indicates that a new sublist is to begin
    while i < n:
#        print('index: ', i, 'task %d: ' %i, alr[i])
        if inside_CON == 0:
#            print('we are not currently inside a conglomerate')
            # continue up until first activity in a cycle
            if not any(alr[i] in cycle for cycle in project_cycles):
#                print('task %d is not in a cycle' %alr[i])
                if new_sublist == 1:
                    sublists.append([alr[i]])
                    n_sublists += 1
                    new_sublist = 0
                else:
                    sublists[n_sublists-1].append(alr[i])
                i += 1
                continue
            if i == n:
                break
            # for activities that are in a cycle...
            # get index of cycles to which alr[i] belongs
            j_set = [index for index,cycle in enumerate(project_cycles) if alr[i] in cycle]
#            print('task %d belongs to the cycles with the following indices: ' %alr[i], j_set)
            for j in j_set: 
                c_in_CON.append(j)
                project_cycles[j].remove(alr[i])
            inside_CON = 1
            sublists.append([alr[i]])
            n_sublists += 1
            i += 1
#            print('sublists: ', sublists)
        elif inside_CON == 1:
#            print('we are currently inside a conglomerate')
            # continue through activities that are not in a cycle
            if not any(alr[i] in cycle for cycle in project_cycles):
#                print('task %d is not in a cycle' %alr[i])
                sublists[n_sublists-1].append(alr[i])
                i += 1  
            if i == n:
                break
            # for activities that are in a cycle...
            sublists[n_sublists-1].append(alr[i])
            # get index of cycles to which alr[i] belongs
            j_set = [index for index,cycle in enumerate(project_cycles) if alr[i] in cycle]
#            print('task %d belongs to the cycles with the following indices: ' %alr[i], j_set)
            # remove activity from cycles
            for j in j_set:
                project_cycles[j].remove(alr[i])
                # if new cycle has been encountered
                if j not in c_in_CON:
                    c_in_CON.append(j)
                # if we have come to the end of a cycle
                if project_cycles[j] == []:
                    c_in_CON.remove(j)
                # if we have come to the end of a conglomerate
                if c_in_CON == []:
                    inside_CON = 0
                    new_sublist = 1
            i += 1
#            print('sublists: ', sublists)
#    print(sublists)
    return sublists

# returns a population of alrs of size pop_size
def get_init_pop(project, pop_size):
    population = []
    # creating a population of different activity list representations
    attempt = 0
    while attempt < 5000 and len(population) < pop_size: 
        attempt += 1
        alr = generate_alr(project)
        if alr not in population:
            population.append(alr)
    if attempt >= 5000:
        print('Could not get a population of size %d. Try a smaller population size instead.' %pop_size)
        return(1)
    return(population)

######################################################################
### random topological ordering wrt SS relations with +ve min. lag ###
######################################################################

# returns randomly generated alr, i.e. list of task_ids
def generate_alr(project):
    n_tasks = len(project.tasks)-2 # no. of non-dummy tasks
    ordered_tasks = []
    visited = [True] + [False for i in range(n_tasks)] + [True]  
    while False in visited:
        task_id = random.randint(0, len(project.tasks)-1)
        if visited[task_id] == False:
            top_order_task(project, task_id, visited, ordered_tasks)
    return([0] + ordered_tasks + [n_tasks+1])

def top_order_task(project, task_id, visited, ordered_tasks):
    visited[task_id] = True
    ### ONLY S->S PRECEDENCE RELATIONSHIPS ARE CONSIDERED ###
    successor_ids = [successor for successor in project.tasks[task_id].SS_successors]
    while False in [v for i,v in enumerate(visited) if i in successor_ids]:
        successor_id = random.choice(successor_ids)
        if visited[successor_id] == False:
            top_order_task(project, successor_id, visited, ordered_tasks)
    ordered_tasks.insert(0, task_id)



