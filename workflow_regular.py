from WakeModel.jensen import JensenWakeFraction, JensenWakeDeficit
from openmdao.api import IndepVarComp, Problem, Group, view_model, SqliteRecorder, ExplicitComponent
import numpy as np
from time import time, clock
from input_params import turbine_radius, max_n_turbines, max_n_substations, i as interest_rate, central_platform, areas
from WakeModel.WakeMerge.RSS import MergeRSS
from src.api import AEPWorkflow, TIWorkflow, MaxTI, AEP
from WakeModel.Turbulence.turbulence_wake_models import Frandsen2, DanishRecommendation, Larsen, Frandsen, Quarton
from src.Utils.read_files import read_layout, read_windrose
from WaterDepth.water_depth_models import RoughInterpolation
from ElectricalCollection.topology_hybrid_optimiser import TopologyHybridHeuristic
from SupportStructure.teamplay import TeamPlay
from OandM.OandM_models import OM_model1
from Costs.teamplay_costmodel import TeamPlayCostModel
from Finance.LCOE import LCOE
from constraints import MinDistance, WithinBoundaries
from regular_parameterised import RegularLayout
#development branch
real_angle = 30.0
artificial_angle = 30.0
n_windspeedbins = 0
n_cases = int((360.0 / artificial_angle) * (n_windspeedbins + 1.0))
print (n_cases, "Number of cases")


class NumberLayout(ExplicitComponent):
    def setup(self):
        self.add_input("orig_layout", shape=(max_n_turbines, 2))
        self.add_output("number_layout", shape=(max_n_turbines, 3))

    def compute(self, inputs, outputs):
        orig_layout = inputs["orig_layout"]
        outputs["number_layout"] = [[n, orig_layout[n][0], orig_layout[n][1]] for n in range(len(orig_layout))]


class WorkingGroup(Group):
    def __init__(self, fraction_model=JensenWakeFraction, deficit_model=JensenWakeDeficit, merge_model=MergeRSS, turbulence_model=DanishRecommendation):
        super(WorkingGroup, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.merge_model = merge_model
        self.turbulence_model = turbulence_model

    def setup(self):
        indep2 = self.add_subsystem('indep2', IndepVarComp())
        indep2.add_output("areas", val=areas)
        indep2.add_output("downwind_spacing", val=50.0)
        indep2.add_output("crosswind_spacing", val=50.0)
        indep2.add_output("odd_row_shift_spacing", val=0.0)
        indep2.add_output("layout_angle", val=0.0)

        wd, wsc, wsh, wdp = read_windrose('weibull_windrose_12unique.dat')

        # wsh = [1.0, 1.0, 1.0, 1.0]
        # wsc = [8.0, 8.0, 8.0, 8.0]
        # wdp = [25.0, 25.0, 25.0, 25.0]
        # wd = [0.0, 90.0, 180.0, 270.0]
        # wsh = [1.0]
        # wsc = [8.0]
        # wdp = [100.0]
        # wd = [90.0]

        indep2.add_output('weibull_shapes', val=wsh)
        indep2.add_output('weibull_scales', val=wsc)
        indep2.add_output('dir_probabilities', val=wdp)
        indep2.add_output('wind_directions', val=wd)  # Follows windrose convention N = 0, E = 90, S = 180, W = 270 deg.
        indep2.add_output('cut_in', val=8.5)
        indep2.add_output('cut_out', val=8.5)
        indep2.add_output('turbine_radius', val=turbine_radius)
        indep2.add_output('n_turbines', val=9)
        # indep2.add_output('n_turbines_p_cable_type', val=[5, 7, 0])
        indep2.add_output('n_turbines_p_cable_type', val=[1, 2, 0])
        indep2.add_output('substation_coords', val=central_platform)
        indep2.add_output('n_substations', val=1)
        indep2.add_output('electrical_efficiency', val=0.99)
        indep2.add_output('transm_electrical_efficiency', val=0.95)
        indep2.add_output('operational_lifetime', val=20.0)
        indep2.add_output('interest_rate', val=interest_rate)

        indep2.add_output('TI_amb', val=[0.11 for _ in range(n_cases)])
        self.add_subsystem("regular_layout", RegularLayout())
        self.add_subsystem('numberlayout', NumberLayout())
        self.add_subsystem('depths', RoughInterpolation(max_n_turbines))
        self.add_subsystem('platform_depth', RoughInterpolation(max_n_substations))

        self.add_subsystem('AeroAEP', AEPWorkflow(real_angle, artificial_angle, n_windspeedbins, self.fraction_model, self.deficit_model, self.merge_model))
        self.add_subsystem('TI', TIWorkflow(n_cases, self.turbulence_model))

        self.add_subsystem('electrical', TopologyHybridHeuristic())

        self.add_subsystem('find_max_TI', MaxTI(n_cases))
        self.add_subsystem('support', TeamPlay())
        self.add_subsystem('OandM', OM_model1())
        self.add_subsystem('AEP', AEP())
        self.add_subsystem('Costs', TeamPlayCostModel())
        self.add_subsystem('lcoe', LCOE())
        self.connect("indep2.areas", "regular_layout.area")
        self.connect("indep2.downwind_spacing", "regular_layout.downwind_spacing")
        self.connect("indep2.crosswind_spacing", "regular_layout.crosswind_spacing")
        self.connect("indep2.odd_row_shift_spacing", "regular_layout.odd_row_shift_spacing")
        self.connect("indep2.layout_angle", "regular_layout.layout_angle")
        self.connect("regular_layout.regular_layout", "numberlayout.orig_layout")

        self.connect('numberlayout.number_layout', 'depths.layout')

        self.connect('numberlayout.number_layout', 'AeroAEP.original')
        self.connect("regular_layout.n_turbines_regular", ['AeroAEP.n_turbines', 'TI.n_turbines', 'electrical.n_turbines', 'support.n_turbines', 'Costs.n_turbines'])

        self.connect('indep2.cut_in', 'AeroAEP.cut_in')
        self.connect('indep2.cut_out', 'AeroAEP.cut_out')
        self.connect('indep2.weibull_shapes', 'AeroAEP.weibull_shapes')
        self.connect('indep2.weibull_scales', 'AeroAEP.weibull_scales')
        self.connect('indep2.dir_probabilities', 'AeroAEP.dir_probabilities')
        self.connect('indep2.wind_directions', 'AeroAEP.wind_directions')
        self.connect('indep2.turbine_radius', ['AeroAEP.turbine_radius', 'TI.radius'])

        for n in range(max_n_turbines):
            self.connect('AeroAEP.wakemodel.linear_solve.deficits{}.dU'.format(n), 'TI.dU_matrix.deficits{}'.format(n))
            self.connect('AeroAEP.wakemodel.linear_solve.turbine{}.ct'.format(n), 'TI.ct_matrix.ct{}'.format(n))

        self.connect('AeroAEP.wakemodel.linear_solve.order_layout.ordered', 'TI.ordered')
        self.connect('indep2.TI_amb', 'TI.TI_amb')
        self.connect('AeroAEP.open_cases.freestream_wind_speeds', 'TI.freestream')

        self.connect('numberlayout.number_layout', 'electrical.layout')
        self.connect('indep2.n_turbines_p_cable_type', 'electrical.n_turbines_p_cable_type')
        self.connect('indep2.substation_coords', 'electrical.substation_coords')
        self.connect('indep2.n_substations', 'electrical.n_substations')

        self.connect('TI.TI_eff', 'find_max_TI.all_TI')
        self.connect('depths.water_depths', 'support.depth')
        self.connect('find_max_TI.max_TI', 'support.max_TI')

        self.connect('AeroAEP.AEP', 'OandM.AEP')
        self.connect('OandM.availability', 'AEP.availability')
        self.connect('AeroAEP.AEP', 'AEP.aeroAEP')
        self.connect('indep2.electrical_efficiency', 'AEP.electrical_efficiency')

        self.connect('platform_depth.water_depths', 'Costs.depth_central_platform', src_indices=[0])

        self.connect('indep2.n_substations', 'Costs.n_substations')
        self.connect('electrical.length_p_cable_type', 'Costs.length_p_cable_type')
        self.connect('electrical.cost_p_cable_type', 'Costs.cost_p_cable_type')
        self.connect('support.cost_support', 'Costs.support_structure_costs')

        self.connect('indep2.substation_coords', 'platform_depth.layout')

        self.connect('Costs.investment_costs', 'lcoe.investment_costs')
        self.connect('OandM.annual_cost_O&M', 'lcoe.oandm_costs')
        self.connect('Costs.decommissioning_costs', 'lcoe.decommissioning_costs')
        self.connect('AEP.AEP', 'lcoe.AEP')
        self.connect('indep2.transm_electrical_efficiency', 'lcoe.transm_electrical_efficiency')
        self.connect('indep2.operational_lifetime', 'lcoe.operational_lifetime')
        self.connect('indep2.interest_rate', 'lcoe.interest_rate')



if __name__ == '__main__':
    def print_nice(string, value):
        header = '=' * 10 + " " + string + " " + '=' * 10 + '\n'
        header += str(value) + "\n"
        header += "=" * (22 + len(string))
        print header
    print_nice("Before defining problem", clock())
    prob = Problem()
    prob.model = WorkingGroup(JensenWakeFraction, JensenWakeDeficit, MergeRSS, DanishRecommendation)
#     prob.model.approx_totals(of=['lcoe.LCOE'], wrt=['indep2.layout'], method='fd', step=1e-7, form='central', step_calc='rel')
    print_nice("Before setup", clock())
    prob.setup()

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

    print_nice("Power", prob['lcoe.LCOE'])
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