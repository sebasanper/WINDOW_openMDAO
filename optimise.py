import numpy as np

from openmdao.api import Problem, pyOptSparseDriver
from workflow import WorkingGroup

prob = Problem()
model = prob.model = WorkingGroup(JensenWakeFraction, JensenWakeDeficit, MergeRSS, DanishRecommendation)

prob.driver = pyOptSparseDriver()
prob.driver.options['optimizer'] = "ALPSO"

model.add_design_var('indep2.layout', lower=np.array([[0, 0.0, 0.0], [1, 0.0, 0.0], [2, 0.0, 0.0]]), upper=np.array([[0, 1120.0, 0.0], [1, 1120.0, 0.0], [2, 1120.0, 0.0]]))
model.add_objective('lcoe.LCOE')
# model.add_constraint('con1', upper=0.0)

prob.set_solver_print(level=5)

prob.setup(check=False)
prob.run_driver()

print(prob['indep2.layout'])
