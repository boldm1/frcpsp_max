from numpy import *

# returns feasible start time interval for each activity
def temporal_analysis(project):
    ### initialise distance graph ###
    dgraph = [[array([[float('-inf'),float('-inf')],[float('-inf'),float('-inf')]]) for j in project.tasks] for i in project.tasks] # dgraph[i][j] = [[d_si->sj, d_si->fj],[d_fi->sj, d_fi->fj]]
    for i in project.tasks:
        dgraph[i][i] = array([[0,project.tasks[i].d],[-project.tasks[i].d,0]])
    for i in project.tasks:
        for j in project.tasks[i].successors:
            d_i = project.tasks[i].d
            d_j = project.tasks[j[0]].d
            dgraph[i][j[0]] = array([[j[1],j[1]+d_j], [j[1]-d_i,j[1]-d_i+d_j]]) 
    ### floyd-warshall algorithm ###
    for k in project.tasks:
        for i in project.tasks:
            for j in project.tasks:
                d_i = project.tasks[i].d
                d_j = project.tasks[j].d
                new_minlag = max(dgraph[i][j][0][0], dgraph[i][k][0][0]+dgraph[k][j][0][0]) # min(d_si->sj, d_si->sk + d_sk->sj)
                dgraph[i][j] = array([[new_minlag,new_minlag+d_j], [new_minlag-d_i,new_minlag-d_i+d_j]])
    for i in project.tasks:
        print([dgraph[i][j][0][0] for j in project.tasks])
    ### checking feasibility ###
    for i in project.tasks:
        if dgraph[i][i][0][0] != 0 or dgraph[i][i][1][1] != 0:
            print('Project is infeasible.')
            return(1)
    ### minimal network ###
    min_network = [[[] for j in project.tasks] for i in project.tasks]
    for i in project.tasks:
        for j in project.tasks:
           min_network[i][j] = array([[[dgraph[j][i][0][0],-dgraph[i][j][0][0]], [dgraph[j][i][0][1],-dgraph[i][j][0][1]]], [[dgraph[j][i][1][0],-dgraph[i][j][1][0]], [dgraph[j][i][1][1], -dgraph[i][j][1][1]]]])
#    for i in project.tasks:
#        for j in project.tasks:
#            print('%d,%d:\n ' %(i,j), min_network[i][j])



