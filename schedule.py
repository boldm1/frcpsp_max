
from copy import deepcopy

class Schedule():

    def __init__(self, project):
        self.tasks = project.tasks
        self.dgraph = project.dgraph
        self.tasks_scheduled = []
        self.task_starts = {}
        self.task_ends = {}
        self.task_resource_usage = [[[0 for t in range(project.T)] for i in project.tasks] for r in range(len(project.R_max))]
        self.resource_availability = [[project.R_max[r] for t in range(project.T)] for r in range(len(project.R_max))]
        self.makespan = None
            
    # updates dgraph for given schedule
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
                print('This schedule is infeasible.')
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
