import re
from task import Task
from project import Project
from temporal_analysis import temporal_analysis

def load_instance(path_to_file):
    f = open(path_to_file, 'r')
    raw_lines = f.read().splitlines()
    stripped_lines = []
    for line in raw_lines:
        line = line.replace('\t', ',').replace('[', '').replace(']', '')
        stripped_lines.append(re.split(',', line))
    first_line = stripped_lines[0]
    n_activities = int(first_line[0]) + 2 # number of activities (incl. dummy activities)
    n_resources = int(first_line[1])
    ### loading tasks ###
    tasks = {}
    for activity in range(n_activities):
        ### first block ###
        line1 = stripped_lines[activity+1]
        line2 = stripped_lines[n_activities+activity+1]
        task_id = int(line1[0])
        n_successors = int(line1[2])
        successors = []
        if n_successors > 0:
            for i in range(n_successors):
                successors.append((int(line1[3+i]), int(line1[3+n_successors+i]))) # ((F-->S) successor_id, min. time-lag)
        ### second block ###
        d = int(line2[2]) # activity duration
        q = [] # quantity of resource required of each resource
        for r in range(n_resources):
            q.append(int(line2[3+r])) 
        task = Task(task_id, successors, d, q)
        tasks[task_id] = task 
    last_line = stripped_lines[2*n_activities+1]
    R = [] # resource_availabilities
    for r in range(n_resources):
        R.append(int(last_line[r]))
    project = Project(path_to_file, tasks, R)
    return(project)

project = load_instance('psp2.sch')
temporal_analysis(project)



