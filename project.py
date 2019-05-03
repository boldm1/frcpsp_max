

class Project():

    def __init__(self, name, tasks, R):         
        self.name = name
        self.tasks = tasks # tasks = {task_id : task_object}
        self.R = R # resource availabilities
