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
from ElectricalCollection.topology_hybrid_optimiser import TopologyHybridHeuristic
from SupportStructure.teamplay import TeamPlay
from src.api import MaxTI

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
                                                #   [9, 1160.0, 1160.0]]))
        # indep2.add_output('layout', val=np.array([[0, 485101.04983316606, 5732217.3257142855], [1, 485503.6486449828, 5731759.337142857],
        #        [2, 485866.01741583704, 5731311.565714286], [3, 486268.61622765375, 5730792.548571428],
        #        [4, 486671.24216694245, 5732675.28], [5, 487089.95469712175, 5732217.3257142855],
        #        [6, 487444.23948132276, 5731708.457142857], [7, 487846.86542061146, 5731250.502857143],
        #        [8, 487846.86542061146, 5733591.222857143], [9, 488249.4642324282, 5733061.988571429],
        #        [10, 488660.1199034262, 5732624.4], [11, 489014.43181509915, 5732166.411428572],
        #        [12, 489425.0874860972, 5731657.577142857], [13, 489827.7134253859, 5731199.622857143],
        #        [14, 489425.0874860972, 5733998.297142857], [15, 489827.7134253859, 5733530.16],
        #        [16, 490238.3690963839, 5733021.291428572], [17, 490592.65388058487, 5732563.337142857],
        #        [18, 491003.3366790549, 5732095.2], [19, 491405.9354908716, 5731596.514285714],
        #        [20, 491808.5614301603, 5733479.245714285], [21, 492170.9030735426, 5732960.228571429],
        #        [22, 492581.5587445406, 5732502.274285714], [23, 492984.1846838293, 5732034.137142858],
        #        [24, 494152.1579903969, 5735245.577142857], [25, 494553.2647912541, 5734783.68],
        #        [26, 494963.2965303963, 5734321.782857143], [27, 495319.8328947725, 5733803.554285714],
        #        [28, 495720.93969562976, 5735684.938285714], [29, 496130.971434772, 5735166.72],
        #        [30, 496541.0031739142, 5734716.102857143], [31, 496897.5395382904, 5734265.451428572],
        #        [32, 497307.57127743267, 5736090.504], [33, 497708.6780782899, 5735628.610285714],
        #        [34, 489415.4029785964, 5729387.485714286], [35, 489820.4161354203, 5728866.377142857],
        #        [36, 490184.08702493017, 5728396.285714285], [37, 490589.07305428205, 5727947.108571429],
        #        [38, 490994.086211106, 5727435.222857143], [39, 491407.34611941513, 5726975.588571428],
        #        [40, 491762.7431299677, 5726526.411428572], [41, 490994.086211106, 5729775.188571429],
        #        [42, 491407.34611941513, 5729315.554285714], [43, 491771.0170089249, 5728803.702857143],
        #        [44, 492167.72915931966, 5728354.491428572], [45, 492581.0161951008, 5727894.857142857],
        #        [46, 492977.7283454955, 5727435.222857143], [47, 492977.7283454955, 5729712.514285714],
        #        [48, 493349.6731139625, 5729263.337142857], [49, 493746.4123918292, 5728803.702857143],
        #        [50, 494556.41157800506, 5730172.148571429], [51, 492974.7985785205, 5725094.708571428],
        #        [52, 493341.1279602854, 5724641.794285715], [53, 493755.25594769826, 5724128.468571428],
        #        [54, 494153.43298158044, 5723665.474285714], [55, 494511.78688658006, 5723212.56],
        #        [56, 493747.2804709329, 5726463.565714286], [57, 494153.43298158044, 5726000.571428572],
        #        [58, 494511.78688658006, 5725487.28], [59, 494917.93939722754, 5725044.411428572],
        #        [60, 495332.06738464045, 5724571.337142857]]))

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
        indep2.add_output('n_turbines_p_cable_type', val=[2, 0, 0])
        indep2.add_output('substation_coords', val=[[500.0, 500.0], [496845.0, 5731342.0]])
        indep2.add_output('n_substations', val=1)

        indep2.add_output('TI_amb', val=[0.11 for _ in range(n_cases)])

        self.add_subsystem('AEP', AEPWorkflow(real_angle, artificial_angle, n_windspeedbins, self.power_model,
                                                    self.fraction_model, self.deficit_model, self.merge_model, self.thrust_model))
        self.add_subsystem('TI', TIWorkflow(n_cases, self.turbulence_model))

        self.add_subsystem('electrical', TopologyHybridHeuristic())

        self.add_subsystem('find_max_TI', MaxTI(n_cases))
        self.add_subsystem('support', TeamPlay())

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
        self.connect('indep2.n_turbines', 'electrical.n_turbines')

        self.connect('indep2.n_turbines', 'support.n_turbines')
        self.connect('TI.TI_eff', 'find_max_TI.all_TI')
        self.connect('depths.water_depths', 'support.depth')
        self.connect('find_max_TI.max_TI', 'support.max_TI')


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