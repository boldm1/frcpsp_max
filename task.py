import math

class Task():
    
    def __init__(self, id, successors, w, q_min, q_max):
        self.id = id
        self.successors = successors # e.g. successor[i=2(FS)] = [(FS successor id, min. time-lag),...]
        self.w = w
        self.q_min = q_min
        self.q_max = q_max
        try:
            self.d_max = math.ceil(self.w/self.q_min[0])
            self.d_min = math.ceil(self.w/self.q_max[0])
        except ZeroDivisionError:
            self.d_max = 0
            self.d_min = 0

