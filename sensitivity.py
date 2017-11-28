__author__ = 'sebasanper'

from numpy.random import random
from numpy import sqrt, array
import numpy as np
from copy import deepcopy
from joblib import Parallel, delayed
from openmdao.api import Problem
from workflow import WorkingGroup
import time
from random import choice, randint

prob = Problem()
# print clock(), "Before defining model"
prob.model = WorkingGroup()
# print clock(), "Before setup"
prob.setup()

# print clock(), "After setup"
def fit(layout):
    prob['indep2.layout'] = layout
    prob.run_model()
    lcoe = prob['lcoe.LCOE'][0]
    # if layout[4][0] == 500.0 or layout[4][0] == 620 or layout[4][1] == 500.0 or layout[4][1] == 620.0:
    # if prob['constraint_distance.magnitude_violations'] > 0:
    #     lcoe += 20.0
    # if prob['constraint_boundary.n_constraint_violations'] > 0:
    #     lcoe += 20.0
    return lcoe

def sensitivity_all():
    with open("sensitivity_all_rand.dat", "w") as out:
        layout = np.array([[float(randint(0, 1120)), float(randint(0, 1120))] for _ in range(9)])
        for i in range(10):
            print(i)
            a = [randint(0, 1000), randint(0, 1000)]
            layout2 = layout + np.array([a for _ in range(9)])
            lcoe = fit(layout2)
            out.write("{} {}\n".format(i, lcoe))

n = 20

def sensitivity_one():
    # layout = np.array([[float(randint(0, 1120)), float(randint(0, 1120))] for _ in range(9)])
    r = 3
    with open("small{}y+.dat".format(r), "w") as out:
        for i in range(1,n):
            layout = np.array([[0.0, 0.0], [560.0, 0.0], [1120.0, 0.0],
                      [0.0, 560.0], [560.0, 560.0], [1120.0, 560.0],
                      [0.0, 1120.0], [560.0, 1120.0], [1120.0, 1120.0]])
            print(i)
            layout[r][1] += 1.0 / float(i)
            lcoe = fit(layout)
            out.write("{} {}\n".format(i, lcoe))
    with open("small{}x+.dat".format(r), "w") as out:
        for i in range(1,n):
            layout = np.array([[0.0, 0.0], [560.0, 0.0], [1120.0, 0.0],
                      [0.0, 560.0], [560.0, 560.0], [1120.0, 560.0],
                      [0.0, 1120.0], [560.0, 1120.0], [1120.0, 1120.0]])
            print(i)
            layout[r][0] += 1.0 / float(i)
            lcoe = fit(layout)
            out.write("{} {}\n".format(i, lcoe))
    with open("small{}y-.dat".format(r), "w") as out:
        for i in range(1,n):
            layout = np.array([[0.0, 0.0], [560.0, 0.0], [1120.0, 0.0],
                      [0.0, 560.0], [560.0, 560.0], [1120.0, 560.0],
                      [0.0, 1120.0], [560.0, 1120.0], [1120.0, 1120.0]])
            print(i)
            layout[r][1] -= 1.0 / float(i)
            lcoe = fit(layout)
            out.write("{} {}\n".format(i, lcoe))
    with open("small{}x-.dat".format(r), "w") as out:
        for i in range(1,n):
            layout = np.array([[0.0, 0.0], [560.0, 0.0], [1120.0, 0.0],
                      [0.0, 560.0], [560.0, 560.0], [1120.0, 560.0],
                      [0.0, 1120.0], [560.0, 1120.0], [1120.0, 1120.0]])
            print(i)
            layout[r][0] -= 1.0 / float(i)
            lcoe = fit(layout)
            out.write("{} {}\n".format(i, lcoe))

if __name__ == '__main__':
    sensitivity_one()
