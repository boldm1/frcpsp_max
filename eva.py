import math
import random

def genetic_algorithm(project):
    init_pop = get_init_pop(project)

def get_init_pop(project):
    V = [task for task in project.tasks.values()] # list of tasks
    N = V[1:-1] # list of non-dummy tasks
    V_ids = [task.id for task in V]
    E # eligible tasks
    S # scheduled tasks
    for i in range(100): # population size of 100
        schedule = Schedule(project)
        # calculating task priorities (longest path following)
        for task in N:
            task.LPF = math.ceil(task.w/task.q_max) + max([successor.LPF for successor in task.successors_raw)
        
        ### getting eligible activities ###
        for i in V_ids:
            for j in V_ids:
                if project.tasks[j].successors


        for j in N_ids:
            task = random.choice(N, 1, p=[task.LPF for task in N])
        
        # randomly sample tasks based on priority rule


def get_fitness

def crossover

