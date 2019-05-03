

class Task():
    
    def __init__(self, id, successors, d, q):
        self.id = id
        self.successors = successors # ((F-->S) successor_id, min. time-lag)
        self.d = d
        self.q = q
