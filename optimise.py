import numpy as np

from openmdao.api import Problem, ScipyOptimizer
# fron openmdao.api imprt pyOptSparseDrivers
from workflow import WorkingGroup

prob = Problem()
model = prob.model = WorkingGroup()
# prob.driver = pyOptSparseDriver()
prob.driver = ScipyOptimizer()
prob.driver.options['optimizer'] = "SLSQP"#COBYLA, 
prob.driver.options['maxiter'] = 600

model.add_design_var('indep2.layout', lower=np.array([[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]), upper=np.array([[1120.0, 1120.0], [1120.0, 1120.0], [1120.0, 1120.0]]))
model.add_objective('lcoe.LCOE')
model.add_constraint('constraint_distance.n_constraint_violations', upper=0.0)
model.add_constraint('constraint_boundary.n_constraint_violations', upper=0.0)

prob.set_solver_print(level=5)

prob.setup(check=False)
prob.run_driver()

print(prob['indep2.layout'])
print(prob['lcoe.LCOE'])

print(prob['constraint_distance.n_constraint_violations'])
print(prob['constraint_boundary.n_constraint_violations'])
print(prob['constraint_boundary.magnitude_violations'])
