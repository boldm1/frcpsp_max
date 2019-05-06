

class Project():

    def __init__(self, name, tasks, R_max, l):         
        self.name = name
        self.tasks = tasks # tasks = {task_id : task_object}
        self.R_max = R_max # resource availabilities
        self.l = l # min. block length
        self.temporal_network = None # updated in temporal_analysis function to be minimal project network wrt temporal constraints
        self.T = 20

