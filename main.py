
from pathlib import Path

from load_instance import load_instance
from eva import evolutionary_algorithm
from dt3 import mip_solve


test_instances_dir = Path("test_instances")
project = load_instance(test_instances_dir/'sm_j30'/'PSP156_r1.sch')
evolutionary_algorithm(project, pop_size=50, n_generations=10)
#mip_solve(project)


