from openmdao.api import ExecComp, Group, Problem, IndepVarComp, view_model

from Blade.blade import Blade
from HubNacelle.hub_assembly import Hub
from HubNacelle.nacelle_assembly import Nacelle
from Cost.cost import CSMCalibrated
from scaler import Scaler


#############################################################################
################################  WORKFLOW  #################################
#############################################################################
class RNA(Group):
    def initialize(self):
        # fixed parameters
        self.metadata.declare('num_pegged', desc='Number of pegged nodes required to define the chord/twist profile')
        self.metadata.declare('num_airfoils', desc='Number of airfoils along the blade')
        self.metadata.declare('num_nodes', desc='Number of blade sections')
        self.metadata.declare('num_bins', desc='Number of wind speed samples')
        self.metadata.declare('safety_factor', desc='Safety factor due to model fidelity', default=1.)
        self.metadata.declare('gearbox_stages', desc='Number of stages in the gearbox', default=3)        
        self.metadata.declare('gear_configuration', desc='Parallel or Planetary configuration of each stage', default='eep')
        self.metadata.declare('mb1_type', desc='Upwind main bearing type') # ['CARB','TRB1','TRB2','SRB','CRB','RB']
        self.metadata.declare('mb2_type', desc='Downwind main bearing type', allow_none=True)
        self.metadata.declare('drivetrain_design', desc='Drive train configuration', default='geared') # ['geared', 'single_stage', 'multi_drive', 'pm_direct_drive']
        self.metadata.declare('uptower_transformer', desc='Is uptower transformer present? [True/False]', default=True)
        self.metadata.declare('has_crane', desc='Is the crane present? [0/1]', default=True)
        self.metadata.declare('reference_turbine', desc='URL of CSV file with the definition of the Reference Turbine')
        self.metadata.declare('reference_turbine_cost', desc='URL of CSV file with the cost of the Reference Turbine components')
        self.metadata.declare('power_file', desc='URL of power curve file')
        self.metadata.declare('ct_file', desc='URL of thrust coefficient curve file')
    
    
    
    
    def setup(self):
        # metadata
        num_pegged = self.metadata['num_pegged']
        num_airfoils = self.metadata['num_airfoils']
        num_nodes = self.metadata['num_nodes']
        num_bins = self.metadata['num_bins']
        safety_factor = self.metadata['safety_factor']
        gearbox_stages = self.metadata['gearbox_stages']
        gear_configuration = self.metadata['gear_configuration']
        mb1_type = self.metadata['mb1_type']
        mb2_type = self.metadata['mb2_type']
        drivetrain_design = self.metadata['drivetrain_design']
        uptower_transformer = self.metadata['uptower_transformer']
        has_crane = self.metadata['has_crane']
        reference_turbine = self.metadata['reference_turbine']
        reference_turbine_cost = self.metadata['reference_turbine_cost'] 
        power_file = self.metadata['power_file']
        ct_file = self.metadata['ct_file']
        
        
#         # design variables
#         i = self.add_subsystem('dof', IndepVarComp(), promotes=['*'])
#         i.add_output('design_tsr', desc='design tip speed ratio')
#         i.add_output('blade_number', desc='number of blades')
#         i.add_output('rotor_diameter', units='m', desc='rotor diameter')
#         i.add_output('chord_coefficients', units = 'm', desc = 'coefficients of polynomial chord profile', shape=num_pegged)
#         i.add_output('twist_coefficients', units = 'deg', desc = 'coefficients of polynomial twist profile', shape=num_pegged)       
#         i.add_output('span_airfoil_r', units='m', desc='list of blade node radial location at which the airfoils are specified', shape=num_airfoils)
#         i.add_output('span_airfoil_id', desc='list of blade node Airfoil ID', shape=num_airfoils)
#         i.add_output('pitch', units='deg', desc = 'pitch angle')
#         i.add_output('thickness_factor', desc='scaling factor for laminate thickness')
#         i.add_output('shaft_angle', units='deg', desc='angle of the LSS inclindation with respect to the horizontal')
#         i.add_output('cut_in_speed', units = 'm/s', desc = 'cut-in wind speed')
#         i.add_output('cut_out_speed', units = 'm/s', desc = 'cut-out wind speed')
#         i.add_output('machine_rating', units='kW', desc='machine rating')
#         i.add_output('drive_train_efficiency', desc='efficiency of aerodynamic to electrical conversion')
#         i.add_output('gear_ratio', desc='overall gearbox ratio')
#         i.add_output('Np', desc='number of planets in each stage', shape=3)
        
        
        # sub-systems
        self.add_subsystem('scale', Scaler(), \
                           promotes_inputs=['machine_rating', 'rotor_diameter'], \
                           promotes_outputs=['generator_voltage', 'collection_voltage', 'turbine_rated_current', \
                                             'warranty_percentage', 'solidity_rotor', \
                                             'cd_nacelle', 'cd_rotor_idle_vane', \
                                             'mass_eccentricity', 'yaw_to_hub_height', \
                                             'front_area_nacelle', 'hub_height', \
                                             'tower_top_diameter'])
        
        self.add_subsystem('blade', Blade(num_pegged=num_pegged, \
                                          num_airfoils=num_airfoils, \
                                          num_nodes=num_nodes, \
                                          num_bins=num_bins, \
                                          reference_turbine=reference_turbine, \
                                          power_file=power_file, ct_file=ct_file, \
                                          rho_air=1.225, E_blade=36.233e9, g=9.8), \
                           promotes_inputs=['design_tsr', 'blade_number', 'rotor_diameter', \
                                            'chord_coefficients', 'twist_coefficients', 'span_airfoil_r', 'span_airfoil_id', \
                                            'pitch','thickness_factor', 'shaft_angle',\
                                            'cut_in_speed', 'cut_out_speed', 'machine_rating', 'drive_train_efficiency'], \
                           promotes_outputs=['rotor_cp', 'rotor_ct', 'rotor_torque', 'rotor_thrust', \
                                             'rated_wind_speed', 'wind_bin', 'elec_power_bin', 'ct_bin', \
                                             'span_stress_max', 'tip_deflection', 'blade_mass', 'rotor_speed'])
        
        self.add_subsystem('hub', Hub(safety_factor=safety_factor, g=9.8), \
                           promotes_inputs=['machine_rating', 'blade_number', 'rotor_diameter', 'shaft_angle'], \
                           promotes_outputs=[('hub_assembly_mass', 'hub_mass'), 'rotor_mass', 'rotor_force', 'rotor_moment'])        
        
        
        self.add_subsystem('nacelle', Nacelle(safety_factor=safety_factor, \
                                               gearbox_stages=gearbox_stages, \
                                               gear_configuration=gear_configuration, \
                                               mb1_type=mb1_type, \
                                               mb2_type=mb2_type, \
                                               drivetrain_design=drivetrain_design, \
                                               uptower_transformer=uptower_transformer, \
                                               has_crane=has_crane), \
                           promotes_inputs=['rotor_diameter', 'machine_rating', 'shaft_angle', 'gear_ratio', 'Np'], \
                           promotes_outputs=['nacelle_mass'])
        
        self.add_subsystem('mass', ExecComp('rna_mass = rotor_mass + nacelle_mass', \
                                           rna_mass = {'units': 'kg'}, \
                                           rotor_mass = {'units': 'kg'}, \
                                           nacelle_mass = {'units': 'kg'}), \
                            promotes_outputs=['rna_mass'])
        
        self.add_subsystem('cost', CSMCalibrated(reference_turbine_cost=reference_turbine_cost), \
                           promotes_inputs=['machine_rating', 'rotor_diameter', 'blade_number'], \
                           promotes_outputs=['cost_rna'])
        
        
        
        
        
        
        # connections       
        self.connect('scale.hub_radius', 'blade.hub_radius')
        self.connect('scale.overhang', 'nacelle.overhang')
        self.connect('tower_top_diameter', 'nacelle.tower_top_diameter')
        self.connect('scale.gearbox_cm_x', 'nacelle.gearbox_cm_x')
         
        self.connect('blade.span_chord', ['hub.blade_root_diameter'], src_indices=[0])
        self.connect('blade_mass', ['hub.blade_mass', 'cost.blade_mass'])
        self.connect('blade.root_moment_flap', ['hub.rotor_bending_moment'])
        self.connect('rotor_torque', ['hub.rotor_torque', 'nacelle.rotor_torque']) 
        self.connect('rotor_thrust', ['hub.rotor_thrust', 'nacelle.rotor_thrust']) 
        
        self.connect('rotor_speed', ['nacelle.rotor_speed']) 
        self.connect('rotor_force', ['nacelle.rotor_force']) 
        self.connect('rotor_moment', ['nacelle.rotor_bending_moment']) 
        self.connect('rotor_mass', ['nacelle.rotor_mass']) 
        
        self.connect('rotor_mass', ['mass.rotor_mass']) 
        self.connect('nacelle_mass', ['mass.nacelle_mass']) 
        
        self.connect('hub.hub_mass', 'cost.hub_mass')
        self.connect('hub.pitch_mass', 'cost.pitch_mass')
        self.connect('hub.spinner_mass', 'cost.spinner_mass')
        self.connect('nacelle.lss_mass', 'cost.lss_mass')
        self.connect('nacelle.main_bearing_mass', 'cost.main_bearing_mass')
        self.connect('nacelle.second_bearing_mass', 'cost.second_bearing_mass')
        self.connect('nacelle.gearbox_mass', 'cost.gearbox_mass')
        self.connect('nacelle.hss_mass', 'cost.hss_mass')
        self.connect('nacelle.generator_mass', 'cost.generator_mass')
        self.connect('nacelle.bedplate_mass', 'cost.bedplate_mass')
        self.connect('nacelle.platforms_mass', 'cost.platform_mass')
        self.connect('nacelle.crane_mass', 'cost.crane_mass')
        self.connect('nacelle.yaw_mass', 'cost.yaw_mass')
        self.connect('nacelle.vs_electronics_mass', 'cost.vs_electronics_mass')
        self.connect('nacelle.hvac_mass', 'cost.hvac_mass')
        self.connect('nacelle.cover_mass', 'cost.cover_mass')
        self.connect('nacelle.transformer_mass', 'cost.transformer_mass')
        

        


#############################################################################
##############################  UNIT TESTING ################################
# Activate (Uncomment) the design variables in the Group
############################################################################# 
if __name__ == "__main__":
    from time import time
    from WINDOW_openMDAO.src.api import beautify_dict
    
    start = time()
        
    # workflow setup
    prob = Problem(RNA(num_pegged=3, num_airfoils=8, num_nodes=20, num_bins=31, \
                       safety_factor=1.5, \
                       gearbox_stages=3, \
                       gear_configuration = 'eep', \
                       mb1_type='CARB', \
                       mb2_type='SRB', \
                       drivetrain_design='geared', \
                       uptower_transformer=True, \
                       has_crane=True, \
                       reference_turbine='Blade/Airfoils/reference_turbine.csv', \
                       reference_turbine_cost='Cost/reference_turbine_cost_mass.csv', \
                       power_file = 'power.dat', \
                       ct_file = 'ct.dat'))
    prob.setup()
    #view_model(prob)
    
    # define inputs
    prob['design_tsr'] = 7.0
    prob['blade_number'] = 3
    prob['rotor_diameter'] = 126.0
    #prob['hub_radius'] = 1.5
    prob['chord_coefficients'] = [3.542, 3.01, 2.313]
    prob['twist_coefficients'] = [13.308, 9.0, 3.125]
    prob['span_airfoil_r'] =  [01.36, 06.83, 10.25, 14.35, 22.55, 26.65, 34.85, 43.05]
    prob['span_airfoil_id'] = [0,     1,     2,     3,     4,     5,     6,     7]
    prob['pitch'] = 0.0
    prob['thickness_factor'] = 1.0
    prob['shaft_angle'] = -5.0
    prob['cut_in_speed'] = 3.0
    prob['cut_out_speed'] = 25.0
    prob['machine_rating'] = 5000.0
    prob['drive_train_efficiency'] = 1.0
    #prob['overhang'] = 5.0
    prob['gear_ratio'] = 96.76
    prob['Np'] = [3,3,1]
    #prob['gearbox_cm_x'] = 0.1
    #prob['tower_top_diameter'] = 3.78
      
    prob.run_model()
    print 'Executed in ' + str(round(time() - start, 2)) + ' seconds\n'
     
    # print outputs 
    var_list = ['rotor_mass', 'nacelle_mass', 'cost_rna', 'tip_deflection', 'span_stress_max', \
                'rotor_cp', 'rotor_ct', 'rotor_torque', 'rotor_thrust', \
                'rated_wind_speed', 'wind_bin', 'elec_power_bin', 'ct_bin', \
                'scale.hub_height', 'scale.turbine_rated_current', 'scale.solidity_rotor', \
                'rna_mass']
    saved_output = {}
    for v in var_list:
        saved_output[v] = prob[v]
        
        
    beautify_dict(saved_output)
    
           