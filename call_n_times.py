from numpy.random import random
from numpy import sqrt, array
from copy import deepcopy
# from joblib import Parallel, delayed
from openmdao.api import Problem
from workflow import WorkingGroup
import time

prob = Problem()
# print clock(), "Before defining model"
prob.model = WorkingGroup()
# print clock(), "Before setup"
prob.setup()
all_start = time.time()
for _ in range(50):
	start = time.time()
	prob.run_model()
	print time.time() - start
print
print time.time() - all_start
