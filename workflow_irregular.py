from WakeModel.jensen import JensenWakeFraction, JensenWakeDeficit
from Turbine.Curves import Curves
from openmdao.api import IndepVarComp, Problem, Group, view_model, SqliteRecorder, ExplicitComponent
import numpy as np
from time import time, clock
from input_params2 import rotor_radius as turbine_radius, max_n_turbines, max_n_substations, i as interest_rate, central_platform, areas, n_quadrilaterals, separation_equation_y, cutin_wind_speed, cutout_wind_speed, operational_lifetime, number_turbines_per_cable
from WakeModel.WakeMerge.RSS import MergeRSS
from src.api import AEPWorkflow, TIWorkflow, MaxTI, AEP, NumberLayout, MinDistance, WithinBoundaries, RegularLayout, AreaMapping, read_layout, read_windrose
from WakeModel.Turbulence.turbulence_wake_models import Frandsen2, DanishRecommendation, Larsen, Frandsen, Quarton
from WaterDepth.water_depth_models import RoughInterpolation, RoughClosestNode
from ElectricalCollection.topology_hybrid_optimiser import TopologyHybridHeuristic
from SupportStructure.teamplay import TeamPlay
from OandM.OandM_models import OM_model1
from Costs.teamplay_costmodel import TeamPlayCostModel
from Finance.LCOE import LCOE
from random import uniform

real_angle = 30.0
artificial_angle = 30.0
n_windspeedbins = 10
n_cases = int((360.0 / artificial_angle) * (n_windspeedbins + 1.0))
print (n_cases, "Number of cases")

squares = []
for n in range(n_quadrilaterals):
   square = [[1.0 / n_quadrilaterals * n, 0.0], [n * 1.0 / n_quadrilaterals, 1.0], [(n + 1) * 1.0 / n_quadrilaterals, 1.0], [(n + 1) * 1.0 / n_quadrilaterals, 0.0]]
   squares.append(square)
borssele_mapping1 = AreaMapping(areas[0], squares[0])
borssele_mapping2 = AreaMapping(areas[1], squares[1])
def create_random():
   xt, yt = 2.0, 2.0
   while (xt < 0.0 or xt > 1.0) or (yt < 0.0 or yt > 1.0):
      xb, yb = uniform(min(min([item[0] for item in areas[0]]), min([item[0] for item in areas[1]])), max(max([item[0] for item in areas[0]]), max([item[0] for item in areas[1]]))), uniform(min(min([item[1] for item in areas[0]]), min([item[1] for item in areas[1]])), max(max([item[1] for item in areas[0]]), max([item[1] for item in areas[1]])))
      if yb > separation_equation_y(xb):
        xt, yt = borssele_mapping1.transform_to_rectangle(xb, yb)
      else:
        xt, yt = borssele_mapping2.transform_to_rectangle(xb, yb)
   return [xb, yb]


class WorkingGroup(Group):
    def __init__(self, fraction_model=JensenWakeFraction, deficit_model=JensenWakeDeficit, merge_model=MergeRSS, turbulence_model=DanishRecommendation, turbine_model=Curves):
        super(WorkingGroup, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.merge_model = merge_model
        self.turbine_model = turbine_model
        self.turbulence_model = turbulence_model

    def setup(self):
        indep2 = self.add_subsystem('indep2', IndepVarComp())
        indep2.add_output("areas", val=areas)
        indep2.add_output('layout', val=np.array([create_random() for _ in range(max_n_turbines)]))
        windrose_file = 'Input/weibull_windrose_12unique.dat'
        wd, wsc, wsh, wdp = read_windrose(windrose_file)

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
        indep2.add_output('cut_in', val=cutin_wind_speed)
        indep2.add_output('cut_out', val=cutout_wind_speed)
        indep2.add_output('turbine_radius', val=turbine_radius)
        indep2.add_output('n_turbines', val=74)
        indep2.add_output('n_turbines_p_cable_type', val=number_turbines_per_cable)  # In ascending order, but 0 always at the end. 0 is used for requesting only two or three cable types.
        indep2.add_output('substation_coords', val=central_platform)
        indep2.add_output('n_substations', val=1)
        indep2.add_output('electrical_efficiency', val=0.99)
        indep2.add_output('transm_electrical_efficiency', val=0.95)
        indep2.add_output('operational_lifetime', val=operational_lifetime)
        indep2.add_output('interest_rate', val=interest_rate)

        indep2.add_output('TI_amb', val=[0.11 for _ in range(n_cases)])
        self.add_subsystem('numberlayout', NumberLayout())
        self.add_subsystem('depths', RoughClosestNode(max_n_turbines))
        self.add_subsystem('platform_depth', RoughClosestNode(max_n_substations))

        self.add_subsystem('AeroAEP', AEPWorkflow(real_angle, artificial_angle, n_windspeedbins, self.fraction_model, self.deficit_model, self.merge_model, self.turbine_model))
        self.add_subsystem('TI', TIWorkflow(n_cases, self.turbulence_model))

        self.add_subsystem('electrical', TopologyHybridHeuristic())

        self.add_subsystem('find_max_TI', MaxTI(n_cases))
        self.add_subsystem('support', TeamPlay())
        self.add_subsystem('OandM', OM_model1())
        self.add_subsystem('AEP', AEP())
        self.add_subsystem('Costs', TeamPlayCostModel())
        self.add_subsystem('lcoe', LCOE())
        self.add_subsystem('constraint_distance', MinDistance())
        self.add_subsystem('constraint_boundary', WithinBoundaries())

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