# This file must be run from the 'example' folder that has the 'Input' folder.
import numpy as np

# Imports OpenMDAO API
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
    print header


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

options.input.turbine.power_file = "Input/power_rna.dat"
options.input.turbine.ct_file = "Input/ct_rna.dat"
options.input.turbine.num_pegged = 3
options.input.turbine.num_airfoils = 8
options.input.turbine.num_nodes = 20
options.input.turbine.num_bins = 31
options.input.turbine.safety_factor = 1.5
options.input.turbine.gearbox_stages = 3
options.input.turbine.gear_configuration = 'eep'
options.input.turbine.mb1_type = 'CARB'
options.input.turbine.mb2_type = 'SRB'
options.input.turbine.drivetrain_design = 'geared'
options.input.turbine.uptower_transformer = True
options.input.turbine.has_crane = True
options.input.turbine.reference_turbine = 'Input/reference_turbine.csv'
options.input.turbine.reference_turbine_cost = 'Input/reference_turbine_cost_mass.csv'
        
# Instantiate OpenMDAO problemlem class
problem = Problem()
problem.model = WorkingGroup(options)

problem.setup()

# Default input values of DTU 10 MW Reference Turbine
problem['indep2.design_tsr'] = 7.6
problem['indep2.blade_number'] = 3
problem['indep2.chord_coefficients'] = np.array([3.542, 3.01, 2.313]) * 190.8/126.0
problem['indep2.twist_coefficients'] = [13.308, 9.0, 3.125]
problem['indep2.span_airfoil_r'] =  np.array([01.36, 06.83, 10.25, 14.35, 22.55, 26.65, 34.85, 43.05]) * 190.8/126.0
problem['indep2.span_airfoil_id'] = [0,     1,     2,     3,     4,     5,     6,     7]
problem['indep2.pitch'] = 0.0
problem['indep2.thickness_factor'] = 1.0
problem['indep2.shaft_angle'] = -5.0
problem['indep2.cut_in_speed'] = 3.0
problem['indep2.cut_out_speed'] = 25.0
problem['indep2.machine_rating'] = 10000.0
problem['indep2.drive_train_efficiency'] = 0.95
problem['indep2.gear_ratio'] = 96.76
problem['indep2.Np'] = [3,3,1]


### Uncomment below to plot N2 diagram in a browser.
# view_model(problem)
problem.run_model()

lcoe = problem['lcoe.LCOE'][0]
aep = problem['AeroAEP.AEP'][0]

print_nice("LCOE", lcoe)
print_nice("AEP", aep)

# print outputs 
from WINDOW_openMDAO.src.api import beautify_dict
var_list = ['rotor_mass', 'nacelle_mass', 'cost_rna', 'tip_deflection', 'span_stress_max', \
            'rotor_cp', 'rotor_ct', 'rotor_torque', 'rotor_thrust', \
            'rated_wind_speed', 'wind_bin', 'elec_power_bin', 'ct_bin', \
            'scale.hub_height', 'scale.turbine_rated_current', 'scale.solidity_rotor', \
            'rna_mass']
saved_output = {}
for v in var_list:
    saved_output[v] = problem['rna.' + v]   
beautify_dict(saved_output)

