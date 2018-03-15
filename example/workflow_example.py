from openmdao.api import Problem, view_model
from WINDOW_openMDAO.multifidelity_fast_workflow import WorkingGroup
from time import time
from WINDOW_openMDAO.Turbine.Curves import Curves
from WINDOW_openMDAO.WaterDepth.water_depth_models import RoughClosestNode
from WINDOW_openMDAO.ElectricalCollection.topology_hybrid_optimiser import TopologyHybridHeuristic
from WINDOW_openMDAO.SupportStructure.teamplay import TeamPlay
from WINDOW_openMDAO.OandM.OandM_models import OM_model1

from WINDOW_openMDAO.src.AbsAEP.FastAEP.farm_energy.wake_model_mean_new.wake_turbulence_models import frandsen2, danish_recommendation, frandsen, larsen_turbulence, Quarton, constantturbulence
from WINDOW_openMDAO.src.AbsAEP.FastAEP.farm_energy.wake_model_mean_new.downstream_effects import JensenEffects as Jensen, LarsenEffects as Larsen, Ainslie1DEffects as Ainslie1D, Ainslie2DEffects as Ainslie2D, constantwake
from WINDOW_openMDAO.src.AbsAEP.FastAEP.farm_energy.wake_model_mean_new.wake_overlap import root_sum_square, maximum, multiplied, summed

# # a - 1
# wakemodels = [constantwake, Jensen, Larsen, Ainslie1D, Ainslie2D]
# # c - 3
# turbmodels = [constantturbulence, frandsen2, danish_recommendation, frandsen, larsen_turbulence, Quarton]
# # e - 5
# mergingmodels = [root_sum_square, maximum, multiplied, summed]


from WINDOW_openMDAO.workflow import Options

options = Options()
options.models.wake = Ainslie2D
options.models.merge = root_sum_square
options.models.turbine = Curves
options.models.turbulence = frandsen

options.samples.wind_speeds = 7
options.samples.wind_sectors_angle = 6.0

options.input.site.windrose = "Input/weibull_windrose_12unique.dat"
options.input.turbine.power_file = "Input/power_dtu10.dat"
options.input.turbine.ct_file = "Input/ct_dtu10.dat"

problem = Problem()
problem.model = WorkingGroup(options)
problem.setup()
# view_model(problem)
start = time()
problem.run_model()
print time() - start
print problem['AeroAEP.AEP']
