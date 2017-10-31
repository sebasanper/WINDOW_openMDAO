from WakeModel.jensen import JensenWakeFraction, JensenWakeDeficit
from openmdao.api import IndepVarComp, Problem, Group, view_model, SqliteRecorder
import numpy as np
from time import time, clock
from Power.power_models import PowerPolynomial
from input_params import turbine_radius, max_n_turbines
from WakeModel.WakeMerge.RSS import MergeRSS
from src.api import AEPWorkflow, TIWorkflow
from Turbulence.turbulence_wake_models import Frandsen2, DanishRecommendation, Larsen, Frandsen, Quarton
from ThrustCoefficient.thrust_models import ThrustPolynomial
from src.Utils.read_files import read_layout, read_windrose
from WaterDepth.water_depth_models import RoughInterpolation
from ElectricalCollection.topology_optimiser import TopologyHybridHeuristic

real_angle = 90.0
artificial_angle = 45.0
n_windspeedbins = 1
n_cases = int((360.0 / artificial_angle) * (n_windspeedbins + 1.0))
print n_cases, "Number of cases"


class WorkingGroup(Group):
    def __init__(self, power_model, fraction_model, deficit_model, merge_model, thrust_model, turbulence_model):
        super(WorkingGroup, self).__init__()
        self.power_model = power_model
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.merge_model = merge_model
        self.thrust_model = thrust_model
        self.turbulence_model = turbulence_model

    def setup(self):
        indep2 = self.add_subsystem('indep2', IndepVarComp())
        self.add_subsystem('depths', RoughInterpolation())
        # indep2.add_output('layout', val=read_layout('horns_rev9.dat'))
        indep2.add_output('layout', val=np.array([[0, 0.0, 0.0], [1, 560.0, 0.0], [2, 1120.0, 0.0],
                                                  [3, 0.0, 560.0], [4, 560.0, 560.0], [5, 1120.0, 560.0],
                                                  [6, 0.0, 1120.0], [7, 560.0, 1120.0], [8, 1120.0, 1120.0]]))#,
                                                  # [9, 0.0, 1120.0]]))

        wd, wsc, wsh, wdp = read_windrose('weibull_windrose_12identical.dat')

        # wsh = [1.0, 1.0]
        # wsc = [8.0, 8.0]
        # wdp = [50.0, 50.0]
        # wd = [0.0, 180.0]
        # wsh = [1.0]
        # wsc = [8.0]
        # wdp = [100.0]
        # wd = [45.0]

        indep2.add_output('weibull_shapes', val=wsh)
        indep2.add_output('weibull_scales', val=wsc)
        indep2.add_output('dir_probabilities', val=wdp)
        indep2.add_output('wind_directions', val=wd)  # Follows windrose convention N = 0, E = 90, S = 180, W = 270 deg.
        indep2.add_output('cut_in', val=3.0)
        indep2.add_output('cut_out', val=25.0)
        indep2.add_output('turbine_radius', val=turbine_radius)
        indep2.add_output('n_turbines', val=9)
        indep2.add_output('n_turbines_p_cable_type', val=[3, 0, 0])
        indep2.add_output('substation_coords', val=[[560.0, 560.0], [0, 0]])
        indep2.add_output('n_substations', val=1)

        indep2.add_output('TI_amb', val=[0.11 for _ in range(n_cases)])

        self.add_subsystem('AEP', AEPWorkflow(real_angle, artificial_angle, n_windspeedbins, self.power_model,
                                                    self.fraction_model, self.deficit_model, self.merge_model, self.thrust_model))
        self.add_subsystem('TI', TIWorkflow(n_cases, self.turbulence_model))

        self.add_subsystem('electrical', TopologyHybridHeuristic())

        self.connect('indep2.layout', 'depths.layout')
        self.connect('indep2.n_turbines', 'depths.n_turbines')

        self.connect('indep2.layout', 'AEP.original')
        self.connect('indep2.n_turbines', 'AEP.n_turbines')
        self.connect('indep2.cut_in', 'AEP.cut_in')
        self.connect('indep2.cut_out', 'AEP.cut_out')
        self.connect('indep2.weibull_shapes', 'AEP.weibull_shapes')
        self.connect('indep2.weibull_scales', 'AEP.weibull_scales')
        self.connect('indep2.dir_probabilities', 'AEP.dir_probabilities')
        self.connect('indep2.wind_directions', 'AEP.wind_directions')
        self.connect('indep2.turbine_radius', ['AEP.turbine_radius', 'TI.radius'])

        for n in range(max_n_turbines):
            self.connect('AEP.wakemodel.linear_solve.deficits{}.dU'.format(n), 'TI.dU_matrix.deficits{}'.format(n))
            self.connect('AEP.wakemodel.linear_solve.ct{}.ct'.format(n), 'TI.ct_matrix.ct{}'.format(n))

        self.connect('AEP.wakemodel.linear_solve.order_layout.ordered', 'TI.ordered')
        self.connect('indep2.TI_amb', 'TI.TI_amb')
        self.connect('AEP.open_cases.freestream_wind_speeds', 'TI.freestream')
        self.connect('indep2.n_turbines', 'TI.n_turbines')

        self.connect('indep2.layout', 'electrical.layout')
        self.connect('indep2.n_turbines_p_cable_type', 'electrical.n_turbines_p_cable_type')
        self.connect('indep2.substation_coords', 'electrical.substation_coords')
        self.connect('indep2.n_substations', 'electrical.n_substations')


print clock(), "Before defining problem"
prob = Problem()
print clock(), "Before defining model"
prob.model = WorkingGroup(PowerPolynomial, JensenWakeFraction, JensenWakeDeficit, MergeRSS, ThrustPolynomial, DanishRecommendation)
print clock(), "Before setup"
prob.setup()
# prob.model = WorkingGroup(PowerPolynomial, JensenWakeFraction, JensenWakeDeficit, WakeMergeRSS, ThrustPolynomial, Frandsen)

print clock(), "After setup"
# view_model(prob)
start = time()
print clock(), "Before 1st run"
prob.run_model()
print clock(), "After 1st run"
print time() - start, "seconds", clock()

print prob['electrical.topology']
print prob['electrical.cost']
print prob['electrical.cable_lengths']

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
# print [[prob['AEP.wakemodel.combine.U'][i] for i in [x[0] for x in ordered]] for item  in prob['AEP.wakemodel.combine.U']]

# print "second run"
# start = time()
# print clock(), "Before 2nd run"
# prob.run_model()
# print clock(), "After 2nd run"
# print time() - start, "seconds", clock()
# print prob['AEP.AEP']
#
#
# print "third run"
# start = time()
# print clock(), "Before 3rd run"
# prob.run_model()
# print clock(), "After 3rd run"
# print time() - start, "seconds", clock()
# print prob['AEP.AEP']


# with open("angle_power.dat", "w") as out:
#     for n in range(n_cases):
#         out.write("{} {} {} {} {}\n".format(prob['AEP.open_cases.wind_directions'][n], prob['AEP.open_cases.freestream_wind_speeds'][n], prob['AEP.windrose.probabilities'][n], prob['AEP.farmpower.farm_power'][n], prob['AEP.energies'][n]))
# print prob['AEP.AEP']
# print sum(prob['AEP.windrose.probabilities'])