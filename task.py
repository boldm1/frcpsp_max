

class Task():
    
    def __init__(self, id, successors, w, q_min, q_max):
        self.id = id
        self.successors = successors # e.g. successor[i=2(FS)] = [(FS successor id, min. time-lag),...]
        self.w = w
        self.q_min = q_min
        self.q_max = q_max
