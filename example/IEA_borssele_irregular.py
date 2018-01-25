# This file must be run from the example folder. Otherwise, the absolute path to the WINDOW_openMDAO installation folder needs to be given below.

from os import path
import sys
sys.path.append(path.abspath('../../WINDOW_openMDAO/'))

from workflow_irregular import WorkingGroup
from openmdao.api import Problem, view_model
from time import time, clock

def print_nice(string, value):
    header = '=' * 10 + " " + string + " " + '=' * 10 + '\n'
    header += str(value) + "\n"
    header += "=" * (22 + len(string))
    print header
print_nice("Before defining problem", clock())
prob = Problem()
prob.model = WorkingGroup()
#     prob.model.approx_totals(of=['lcoe.LCOE'], wrt=['indep2.layout'], method='fd', step=1e-7, form='central', step_calc='rel')
print_nice("Before setup", clock())
prob.setup()
"Input/weibull_windrose_12unique.dat"

print clock(), "After setup"
# view_model(prob) # Uncomment to view N2 chart.
start = time()

prob.run_model()
# prob.check_totals(of=['lcoe.LCOE'], wrt=['indep2.layout'])

# of = ['lcoe.LCOE']
# wrt = ['indep2.layout']
# derivs = prob.compute_totals(of=of, wrt=wrt)

# print(derivs['lcoe.LCOE', 'indep2.layout'])
print_nice("After first run", time() - start)

print_nice("LCOE", prob['lcoe.LCOE'])
print_nice("AEP", prob['AEP.AEP'])
print_nice("investment costs", prob['Costs.investment_costs'])
print_nice("OandM.annual_cost_O&M", prob['OandM.annual_cost_O&M'])
print_nice("Costs.decommissioning_costs", prob['Costs.decommissioning_costs'])

print_nice("support.cost_support", sum(prob['support.cost_support']))
print_nice("electrical.cost_p_cable_type", prob['electrical.cost_p_cable_type'])

# print prob['AeroAEP.wakemodel.combine.ct']
# print prob['lcoe.LCOE']
# with open('all_outputs.dat', 'w') as out:
#     out.write("{}".format(prob.model.list_outputs(out_stream=None)))
# print prob['AeroAEP.AEP']
# print prob['Costs.investment_costs']
# print prob['Costs.decommissioning_costs']
# print prob['lcoe.LCOE']
# print prob['OandM.availability']
# print prob['OandM.annual_cost_O&M']

# print prob['find_max_TI.max_TI']
# print prob['support.cost_support']

# print prob['electrical.topology']
# print prob['electrical.cost_p_cable_type']
# print prob['electrical.length_p_cable_type']

# print prob['AEP.windrose.cases']
# print prob['AEP.farmpower.ind_powers']
# print prob['AEP.wakemodel.U']
# print prob['AEP.wakemodel.linear_solve.deficits0.dU']
# print prob['AEP.wakemodel.linear_solve.deficits1.dU']
# print prob['AEP.wakemodel.linear_solve.deficits2.dU']
# print prob['AEP.wakemodel.linear_solve.deficits3.dU']
# print prob['AEP.wakemodel.linear_solve.deficits4.dU']
# print prob['AEP.wakemodel.linear_solve.ct0.ct']
# print prob['AEP.wakemodel.linear_solve.ct1.ct']
# print prob['AEP.wakemodel.linear_solve.ct2.ct']
# print prob['AEP.wakemodel.linear_solve.ct3.ct']
# print prob['AEP.wakemodel.linear_solve.ct4.ct']
# print prob['AEP.wakemodel.linear_solve.deficits1.distance.dist_down']
# print prob['AEP.wakemodel.linear_solve.deficits1.distance.dist_cross']
# ordered = prob['AEP.wakemodel.linear_solve.order_layout.ordered']
# print ordered
# print prob['indep2.layout']
# # print [[prob['AEP.wakemodel.combine.U'][i] for i in [x[0] for x in ordered]] for item  in prob['AEP.wakemodel.combine.U']]

# print "second run"
# start = time()
# # print clock(), "Before 2nd run"
# prob.run_model()
# print clock(), "After 2nd run"
# print time() - start, "seconds", clock()
# print prob['lcoe.LCOE']

# with open("angle_power.dat", "w") as out:
#     for n in range(n_cases):
#         out.write("{} {} {} {} {}\n".format(prob['AEP.open_cases.wind_directions'][n], prob['AEP.open_cases.freestream_wind_speeds'][n], prob['AEP.windrose.probabilities'][n], prob['AEP.farmpower.farm_power'][n], prob['AEP.energies'][n]))
# print prob['AEP.AEP']
# print sum(prob['AEP.windrose.probabilities'])
