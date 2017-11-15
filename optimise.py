import numpy as np

from openmdao.api import Problem, pyOptSparseDriver, ScipyOptimizer
from workflow import WorkingGroup

prob = Problem()
model = prob.model = WorkingGroup()

# prob.driver = pyOptSparseDriver()
prob.driver = ScipyOptimizer()
prob.driver.options['optimizer'] = "SLSQP"

model.add_design_var('indep2.layout', lower=np.array([[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]), upper=np.array([[1120.0, 1120.0], [1120.0, 1120.0], [1120.0, 1120.0]]))
model.add_objective('lcoe.LCOE')
# model.add_constraint('indep2.cut_in', upper=10.0)

prob.set_solver_print(level=5)

prob.setup(check=False)
prob.run_driver()

print(prob['indep2.layout'])
