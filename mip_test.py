
from gurobipy import *

import os.path
import re

from load_instance import load_instance
from dt3 import mip_solve


test_instances_dir = os.path.join('test_instances', 'sm_j10')
f1 = open('smj10_mip_results.txt', 'w+')
f1.write('instance \t feas \t opt \t LB \t sol \t gap \t time \n')
for full_filename in sorted(os.listdir(test_instances_dir), key = lambda filename: int(''.join(re.findall(r'\d+', filename)))):
    print(full_filename)
    project = load_instance(os.path.join(test_instances_dir, full_filename))
    model = mip_solve(project)
    status = model.Status
    if status == GRB.Status.INFEASIBLE:
        f1.write('{} \t no \t - \t - \t - \t - \t - \n'.format(project.name))
    elif status == GRB.Status.OPTIMAL:
        f1.write('{} \t yes \t yes \t {} \t {} \t {} \t {:.3f}\n'.format(project.name, model.ObjBound, model.ObjVal, model.MIPGap, model.Runtime))
    elif status == GRB.Status.TIME_LIMIT:    
        if model.SolCount == 0:
            f1.write('{} \t - \t no \t {} \t - \t - \t 180 \n'.format(project.name, model.ObjBound)) 
        elif model.SolCount != 0:
            f1.write('{} \t yes \t no \t {} \t {} \t 180 \n'.format(project.name, model.ObjBound, model.ObjVal, model.MIPGap))
f1.close()


