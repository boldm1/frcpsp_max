
from numpy import *
from copy import deepcopy

#from temporal_analysis import temporal_analysis

class Project():

    def __init__(self, name, tasks, R_max, l_min):         
        self.name = name
        self.tasks = tasks # tasks = {task_id : task_object}
        self.cycles = self.get_cycles()
        self.R_max = R_max # resource availabilities
        self.l_min = l_min # min. block length
        self.T = sum(tasks[i].d_max for i in tasks) # project horizon

        # getting task predecessors 
        for j in self.tasks:
            self.tasks[j].predecessors = [[] for type in [0,1,2,3]]
            for i in self.tasks:
                for type in [0,1,2,3]:
                    for successor in self.tasks[i].successors[type]:
                        if successor[0] == j:
                            self.tasks[j].predecessors[type].append((i, successor[1]))

#        # calculating task priorities (longest path following)
#        top_ordering = self.get_top_ordering()
#        top_ordering.reverse()
#        for task in top_ordering[1:-1]: # remove dummy activities
#            ### ONLY CONSIDERING S->S PRECEDENCE RELATIONS ###
#            task.LPF = math.ceil(task.w/task.q_max[0]) + max([self.tasks[successor[0]].LPF for successor in task.successors[0]])

        self.init_dgraph = self.dgraph_init() # initial dgraph. Useful for unscheduling step
        self.dgraph = self.dgraph_init()
        self.temporal_analysis()

#    # Topological ordering of tasks, i.e. no task is ordered before its predecessors
#    def get_top_ordering(self):
#        ordered_tasks = []
#        visited = [False for i in range(len(self.tasks))]
#        for task in self.tasks.values():
#            if visited[task.id] == False:
#                self.top_order_task(task, visited, ordered_tasks)
#        return(ordered_tasks) # list of task objects
#    
#    def top_order_task(self, task, visited, ordered_tasks):
#        visited[task.id] = True
#        ### ONLY S->S SUCCESSORS CONSIDERED!!! ###
#        for successor in task.successors[0]:
#            successor_id = successor[0]
#            if visited[successor_id] == False:
#                successor = self.tasks[successor_id]
#                self.top_order_task(successor, visited, ordered_tasks)
#        ordered_tasks.insert(0, task)

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

    # updates dgraph for a given project
    def temporal_analysis(self):
        dgraph = deepcopy(self.dgraph)
        ### floyd-warshall algorithm ###
        for k in self.tasks:
            for i in self.tasks:
                jrange = range(i-(len(self.tasks)-1),i+1)
                for j in [j%len(self.tasks) for j in jrange]:
                    dgraph[i][j][0][0] = max(dgraph[i][j][0][0], max(dgraph[i][k][0][0]+dgraph[k][j][0][0], dgraph[i][k][0][1]+dgraph[k][j][1][0])) # min(d_si->sj, d_si->k + d_k->sj)
                    dgraph[i][j][0][1] = max(dgraph[i][j][0][1], max(dgraph[i][k][0][0]+dgraph[k][j][0][1], dgraph[i][k][0][1]+dgraph[k][j][1][1])) # min(d_si->fj, d_si->k + d_k->fj)
                    dgraph[i][j][1][0] = max(dgraph[i][j][1][0], max(dgraph[i][k][1][0]+dgraph[k][j][0][0], dgraph[i][k][1][1]+dgraph[k][j][1][0])) # min(d_fi->sj, d_fi->k + d_k->sj)
                    dgraph[i][j][1][1] = max(dgraph[i][j][1][1], max(dgraph[i][k][1][0]+dgraph[k][j][0][1], dgraph[i][k][1][1]+dgraph[k][j][1][1])) # min(d_fi->fj, d_fi->k + d_k->fj)
        ### checking feasibility ###
        for i in self.tasks:
            if dgraph[i][i][0][0] != 0 or dgraph[i][i][1][1] != 0:
                print('Project is infeasible.')
                return(1)
        self.dgraph = deepcopy(dgraph)
        ### update d_min, d_max, ES, LS, q_min, q_max ###
        for task in self.tasks.values():
            task.d_min = dgraph[task.id][task.id][0][1]
            task.d_max = -dgraph[task.id][task.id][1][0]
            task.ES = dgraph[0][task.id][0][0]
            task.LS = -dgraph[task.id][0][0][0]
            # only updating work-content resource limits
            if task.d_max == 0:
                task.q_min[0] = 0
                task.q_max[0] = 0
            else:
                task.q_min[0] = task.w/task.d_max
                task.q_max[0] = task.w/task.d_min
