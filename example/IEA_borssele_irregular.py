from __future__ import print_function
# This file must be run from the 'example' folder that has the 'Input' folder.

# Imports OpenMDAO API
from builtins import str
from openmdao.api import Problem, view_model

# Imports WINDOW workflow
from WINDOW_openMDAO.multifidelity_fast_workflow import WorkingGroup

# Imports models included in WINDOW 
# from WINDOW_openMDAO.Turbine.Curves import Curves # Not used in the AEP fast calculator.
from WINDOW_openMDAO.ElectricalCollection.topology_hybrid_optimiser import TopologyHybridHeuristic
from WINDOW_openMDAO.ElectricalCollection.constant_electrical import ConstantElectrical
from WINDOW_openMDAO.ElectricalCollection.POS_optimiser import POSHeuristic
from WINDOW_openMDAO.SupportStructure.teamplay import TeamPlay
from WINDOW_openMDAO.SupportStructure.constant_support import ConstantSupport
from WINDOW_openMDAO.OandM.OandM_models import OM_model1
from WINDOW_openMDAO.AEP.aep_fast_component import AEPFast
from WINDOW_openMDAO.Costs.teamplay_costmodel import TeamPlayCostModel
from WINDOW_openMDAO.AEP.FastAEP.farm_energy.wake_model_mean_new.wake_turbulence_models import frandsen2, danish_recommendation, frandsen, larsen_turbulence, Quarton, constantturbulence
from WINDOW_openMDAO.AEP.FastAEP.farm_energy.wake_model_mean_new.downstream_effects import JensenEffects as Jensen, LarsenEffects as Larsen, Ainslie1DEffects as Ainslie1D, Ainslie2DEffects as Ainslie2D, constantwake
from WINDOW_openMDAO.AEP.FastAEP.farm_energy.wake_model_mean_new.wake_overlap import root_sum_square, maximum, multiplied, summed

# Imports the Options class to instantiate a workflow.
from WINDOW_openMDAO.src.api import WorkflowOptions


def print_nice(string, value):
    header = '=' * 10 + " " + string + " " + '=' * 10 + '\n'
    header += str(value) + "\n"
    header += "=" * (22 + len(string))
    print(header)


options = WorkflowOptions()

# Define models to be implemented.
options.models.aep = AEPFast
options.models.wake = Jensen  
options.models.merge = root_sum_square
options.models.turbine = None # Unnecessary for now as long as the power and Ct curves are defined below.
options.models.turbulence = frandsen
options.models.electrical = TopologyHybridHeuristic
options.models.support = TeamPlay
options.models.opex = OM_model1
options.models.apex = TeamPlayCostModel

# Define number of windrose sampling points
options.samples.wind_speeds = 1
options.samples.wind_sectors_angle = 30.0

# Define paths to site and turbine defining input files.
options.input.site.windrose_file = "Input/weibull_windrose_12unique.dat"
options.input.site.bathymetry_file = "Input/bathymetry_table.dat"
options.input.turbine.power_file = "Input/power_dtu10.dat"
options.input.turbine.ct_file = "Input/ct_dtu10.dat"

# Instantiate OpenMDAO problemlem class
problem = Problem()
problem.model = WorkingGroup(options)

problem.setup()


### Uncomment below to plot N2 diagram in a browser.
# view_model(problem)
problem.run_model()

lcoe = problem['lcoe.LCOE'][0]
aep = problem['AeroAEP.AEP'][0]

print_nice("LCOE", lcoe)
print_nice("AEP", aep)
