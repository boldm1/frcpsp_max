import math

class Task():
    
    def __init__(self, id, successors, w, q_min, q_max):
        self.id = id
        ### successors and predecessors ###
        self.raw_successors = successors # e.g. successor[i=2(FS)] = [(FS successor id, min. time-lag),...]
        self.SS_successors = None # list of ids of SS min-lag successors (initialised upon project creation)
        self.raw_predecessors = None # (initialised upon project creation)
        self.SS_predecessors = None # list of ids of SS min-lag predecessors (initialised upon project creation)
        ### resource bounds ###
        self.q_min = q_min
        self.q_max = q_max
        ### resource requirements ###
        n_resources = len(q_min)
        self.w = w # priniple resource work-content
        self.r_dep = [r for r in range(1,n_resources) if q_min[r] < q_max[r]] # indices of dependent resources
        self.r_ind = [r for r in range(1,n_resources) if q_min[r] == q_max[r]] # indices of independent resources
        ### q_rjt = alpha_krj*q_krj + beta_krj ###
        self.alpha = [0 for r in range(n_resources)]
        self.beta = [0 for r in range(n_resources)]
        for r in self.r_dep:
            try:
                self.alpha[r] = (q_max[r]-q_min[r])/(q_max[0]-q_min[0])
            except ZeroDivisionError: # occurs if q_max[0] == q_min[0]
                self.alpha[r] = 0
            self.beta[r] = q_min[r]-q_min[0]*self.alpha[r]
        ### duration bounds ###
        try:
            self.d_max = math.ceil(w/self.q_min[0])
            self.d_min = math.ceil(w/self.q_max[0])
        except ZeroDivisionError:
            self.d_max = 0
            self.d_min = 0
        ### earliest and latest starts ###
        self.ES = float('-inf') # Earliest start wrt temporal constraints (updated in temporal_analysis)
        self.LS = float('inf')
        self.EF = float('-inf')
        self.LF = float('inf')
