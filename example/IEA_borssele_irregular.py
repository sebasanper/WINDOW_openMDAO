# This file must be run from the example folder. Otherwise, the absolute path to the WINDOW_openMDAO installation folder needs to be given below.

from os import path
import sys
from openmdao.api import Problem, view_model
from time import time, clock

sys.path.append(path.abspath('../../WINDOW_openMDAO/'))

from workflow_irregular import WorkingGroup

def print_nice(string, value):
    header = '=' * 10 + " " + string + " " + '=' * 10 + '\n'
    header += str(value) + "\n"
    header += "=" * (22 + len(string))
    print header
prob = Problem()
prob.model = WorkingGroup()
prob.setup()

print_nice("Time after setup", clock())
# view_model(prob) # Uncomment to view N2 chart.
start = time()

prob.run_model()
print_nice("Execution time first run", time() - start)

print_nice("wind speeds", prob["AeroAEP.open_cases.freestream_wind_speeds"])
print_nice("turbulences", prob['find_max_TI.max_TI'])
print_nice("AEP", prob['AeroAEP.AEP'])
print_nice("powers", prob["AeroAEP.farmpower.ind_powers"])
# print_nice("investment costs", prob['Costs.investment_costs'])
# print_nice("OandM.annual_cost_O&M", prob['OandM.annual_cost_O&M'])
# print_nice("Costs.decommissioning_costs", prob['Costs.decommissioning_costs'])

# print_nice("support.cost_support", sum(prob['support.cost_support']))
# print_nice("electrical.cost_p_cable_type", prob['electrical.cost_p_cable_type'])

# print "second run"
# start = time()
# prob['indep2.interest_rate'] = 0.05 # Changing one parameter for a second run.
# prob.run_model()
# print clock(), "Execution time second run"
# print time() - start, "seconds", clock()
# print prob['lcoe.LCOE']
