
from numpy import *

from temporal_analysis import temporal_analysis

class Project():

    def __init__(self, name, tasks, R_max, l_min):         
        self.name = name
        self.tasks = tasks # tasks = {task_id : task_object}
        self.cycles = self.get_cycles()
        self.R_max = R_max # resource availabilities
        self.l_min = l_min # min. block length
        self.T = sum(tasks[i].d_max for i in tasks) # project horizon

        self.init_dgraph = self.dgraph_init() # initial dgraph. Useful for unscheduling step
        self.dgraph = self.dgraph_init()
        temporal_analysis(self)

    def get_cycles(self):
        all_cycles = [[task_id]+path for task_id in self.tasks for path in self.dfs(task_id, task_id)]
        cycles = []
        for cycle in all_cycles:
            first_task = cycle[0] # first task in cycle
            final_arc = [arc for arc in self.tasks[cycle[-2]].successors[0] if arc[0] == first_task][0]
            if final_arc[1] < 0:
                cycles.append(cycle)
        return(cycles)

   # depth-first search
    def dfs(self, start, end): # start(end) is task_id at start(end) of cycle
        stack = [(start, [])]
        while stack != []:
            i, path = stack.pop()
            if i == end and path != []:
                yield path
                continue
            for successor in self.tasks[i].successors[0]: # all successors are S->S successors
                if successor[0] in path:
                    continue
                stack.append((successor[0], path+[successor[0]]))

    def dgraph_init(self):
        dgraph = [[array([[-self.T,-self.T], [-self.T,-self.T]]) for j in self.tasks] for i in self.tasks] # dgraph[i][j] = [[d_si->sj, d_si->fj],[d_fi->sj, d_fi->fj]]
        for i in self.tasks:
            dgraph[i][i] = array([[0,self.tasks[i].d_min],[-self.tasks[i].d_max,0]])
        for i in self.tasks:
            for j in range(4): # precedence relation type
                for k in self.tasks[i].successors[j]:
                    if j == 0: #S->S relation
                        dgraph[i][k[0]][0][0] = k[1]
                    if j == 1: #S->F relation
                        dgraph[i][k[0]][0][1] = k[1]
                    if j == 2: #F->S relation
                        dgraph[i][k[0]][1][0] = k[1]
                    if j == 3: #F->F relation
                        dgraph[i][k[0]][1][1] = k[1]
        return(dgraph)    
