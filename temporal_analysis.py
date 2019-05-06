from numpy import *

# returns feasible start time interval for each activity
def temporal_analysis(project):
    ### initialise distance graph ###
    dgraph = [[array([[float('-inf'),float('-inf')],[float('-inf'),float('-inf')]]) for j in project.tasks] for i in project.tasks] # dgraph[i][j] = [[d_si->sj, d_si->fj],[d_fi->sj, d_fi->fj]]
    for i in project.tasks:
        dgraph[i][i] = array([[0,project.tasks[i].d_min],[-project.tasks[i].d_max,0]])
    for i in project.tasks:
        for j in range(4): # precedence relation type
            for k in project.tasks[i].successors[j]:
                if j == 0: #S->S relation
                    dgraph[i][k[0]][0][0] = k[1]
                if j == 1: #S->F relation
                    dgraph[i][k[0]][0][1] = k[1]
                if j == 2: #F->S relation
                    dgraph[i][k[0]][1][0] = k[1]
                if j == 3: #F->F relation
                    dgraph[i][k[0]][1][1] = k[1]

    ### floyd-warshall algorithm ###
    for k in project.tasks:
        for i in project.tasks:
            jrange = range(i-(len(project.tasks)-1),i+1)
            for j in [j%len(project.tasks) for j in jrange]:
                dgraph[i][j][0][0] = max(dgraph[i][j][0][0], max(dgraph[i][k][0][0]+dgraph[k][j][0][0], dgraph[i][k][0][1]+dgraph[k][j][1][0])) # min(d_si->sj, d_si->k + d_k->sj)
                dgraph[i][j][0][1] = max(dgraph[i][j][0][1], max(dgraph[i][k][0][0]+dgraph[k][j][0][1], dgraph[i][k][0][1]+dgraph[k][j][1][1])) # min(d_si->fj, d_si->k + d_k->fj)
                dgraph[i][j][1][0] = max(dgraph[i][j][1][0], max(dgraph[i][k][1][0]+dgraph[k][j][0][0], dgraph[i][k][1][1]+dgraph[k][j][1][0])) # min(d_fi->sj, d_fi->k + d_k->sj)
                dgraph[i][j][1][1] = max(dgraph[i][j][1][1], max(dgraph[i][k][1][0]+dgraph[k][j][0][1], dgraph[i][k][1][1]+dgraph[k][j][1][1])) # min(d_fi->fj, d_fi->k + d_k->fj)
    ### checking feasibility ###
    for i in project.tasks:
        if dgraph[i][i][0][0] != 0 or dgraph[i][i][1][1] != 0:
            print('Project is infeasible.')
            return(1)
    ### minimal network ###
    min_network = [[[] for j in project.tasks] for i in project.tasks]
    for i in project.tasks:
        for j in project.tasks:
           min_network[i][j] = array([[[dgraph[i][j][0][0],-dgraph[j][i][0][0]], [dgraph[i][j][0][1],-dgraph[j][i][1][0]]], [[dgraph[i][j][1][0],-dgraph[j][i][0][1]], [dgraph[i][j][1][1], -dgraph[j][i][1][1]]]])
    project.temporal_network = min_network
#    for i in project.tasks:
#        for j in project.tasks:
#            print('%d,%d:\n ' %(i,j), min_network[i][j])
    ### earliest starts wrt temporal constraints ###
    for task in project.tasks.values():
        task.ES = dgraph[0][task.id][0][0]
    





