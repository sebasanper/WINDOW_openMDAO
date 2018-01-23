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

real_angle = 30.0
artificial_angle = 30.0
n_windspeedbins = 0
n_cases = int((360.0 / artificial_angle) * (n_windspeedbins + 1.0))


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
        indep2.add_output('layout', val=np.array([[0.0, 0.0], [560.0, 0.0], [1120.0, 0.0],
                                                  [0.0, 560.0], [560.0, 560.0], [1120.0, 560.0],
                                                  [0.0, 1120.0], [560.0, 1120.0], [1120.0, 1120.0]]))

        wd, wsc, wsh, wdp = read_windrose('weibull_windrose_12unique.dat')

        indep2.add_output('weibull_shapes', val=wsh)
        indep2.add_output('weibull_scales', val=wsc)
        indep2.add_output('dir_probabilities', val=wdp)
        indep2.add_output('wind_directions', val=wd)  # Follows windrose convention N = 0, E = 90, S = 180, W = 270 deg.
        indep2.add_output('cut_in', val=8.5)
        indep2.add_output('cut_out', val=8.5)
        indep2.add_output('turbine_radius', val=turbine_radius)
        indep2.add_output('n_turbines', val=9)
        indep2.add_output('n_turbines_p_cable_type', val=[1, 2, 0])  # In ascending order, but 0 always at the end. 0 is used for requesting only two or three cable types.
        indep2.add_output('substation_coords', val=central_platform)
        indep2.add_output('n_substations', val=1)
        indep2.add_output('electrical_efficiency', val=0.99)
        indep2.add_output('transm_electrical_efficiency', val=0.95)
        indep2.add_output('operational_lifetime', val=20.0)
        indep2.add_output('interest_rate', val=interest_rate)

        indep2.add_output('TI_amb', val=[0.11 for _ in range(n_cases)])
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

        self.add_subsystem('constraint_distance', MinDistance())
        self.add_subsystem('constraint_boundary', WithinBoundaries())
        self.add_subsystem('lcoe', LCOE())
        self.connect("indep2.layout", "numberlayout.orig_layout")

        self.connect("indep2.layout", "constraint_distance.orig_layout")
        self.connect("indep2.turbine_radius", "constraint_distance.turbine_radius")
        self.connect("indep2.layout", "constraint_boundary.layout")
        self.connect("indep2.areas", "constraint_boundary.areas")

        self.connect('numberlayout.number_layout', 'depths.layout')

        self.connect('numberlayout.number_layout', 'AeroAEP.original')
        self.connect('indep2.n_turbines', ['AeroAEP.n_turbines', 'TI.n_turbines', 'electrical.n_turbines', 'support.n_turbines', 'Costs.n_turbines'])
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
    prob = Problem()
    prob.model = WorkingGroup(JensenWakeFraction, JensenWakeDeficit, MergeRSS, DanishRecommendation)
    prob.setup()
    prob.run_model()
    print(prob['lcoe.LCOE'], "LCOE")
    print(prob['constraint_boundary.n_constraint_violations'], "No. Boundary constraint violations")
    print(prob['constraint_distance.n_constraint_violations'], "No. Distance constraint violations")
