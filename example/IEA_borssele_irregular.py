
from os import path
import sys
from openmdao.api import Problem, view_model
from time import time, clock

# from WINDOW_openMDAO.workflow_irregular import WorkingGroup  # For every function as an openmdao component.
from WINDOW_openMDAO.fast_workflow_irregular import WorkingGroup  # For a fast and unique AEP openmdao component.

def print_nice(string, value):
    header = '=' * 10 + " " + string + " " + '=' * 10 + '\n'
    header += str(value) + "\n"
    header += "=" * (22 + len(string))
    print header
prob = Problem()
# prob.model = WorkingGroup(direction_sampling_angle=10.0, windspeed_sampling_points=5, windrose_file='Input/weibull_windrose_12identical.dat', power_curve_file='Input/power_dtu10.dat', ct_curve_file='Input/ct_dtu10.dat')
prob.model = WorkingGroup(direction_sampling_angle=1.0, windspeed_sampling_points=10)
prob.setup()

print_nice("Time after setup", clock())
# view_model(prob) # Uncomment to view N2 chart.
start = time()

prob.run_model()
print_nice("Execution time first run", time() - start)

# print_nice("turbulences", prob['AeroAEP.max_TI'])
print_nice("AEP", prob['AeroAEP.AEP'])
print_nice("LCOE", prob['lcoe.LCOE'])
# print_nice("investment costs", prob['Costs.investment_costs'])
# print_nice("OandM.annual_cost_O&M", prob['OandM.annual_cost_O&M'])
# print_nice("Costs.decommissioning_costs", prob['Costs.decommissioning_costs'])

# print_nice("support.cost_support", sum(prob['support.cost_support']))
# print_nice("electrical.cost_p_cable_type", prob['electrical.cost_p_cable_type'])

# start = time()
# prob['indep2.interest_rate'] = 0.05 # Changing one parameter for a second run.
# prob.run_model()
# print_nice("Execution time second run", time() - start)
# print_nice("LCOE", prob['lcoe.LCOE'])
