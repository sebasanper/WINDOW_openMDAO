from openmdao.api import Group, Problem, IndepVarComp, view_model
import aerodynamic_design, structural_design, rotor_aerodynamics, power_curve, rotor_mechanics


#############################################################################
############################ BLADE WORKFLOW #################################
#############################################################################
class Blade(Group):
    def initialize(self):
        # fixed parameters
        self.metadata.declare('num_pegged', desc='Number of pegged nodes required to define the chord/twist profile')
        self.metadata.declare('num_airfoils', desc='Number of airfoils along the blade')
        self.metadata.declare('num_nodes', desc='Number of blade sections')
        self.metadata.declare('num_bins', desc='Number of wind speed samples')
        self.metadata.declare('reference_turbine', desc='CSV file with the definition of the Reference Turbine')
        self.metadata.declare('rho_air',  desc='Density of air [kg/m**3]', default=1.225)
        self.metadata.declare('E_blade', desc='Youngs modulus of glass fiber [Pa]', default=36.233e9)
        self.metadata.declare('g', desc='acceleration due to gravity [m/s**2]', default=9.8)
        
        
    def setup(self):
        # metadata
        num_pegged = self.metadata['num_pegged']
        num_airfoils = self.metadata['num_airfoils']
        num_nodes = self.metadata['num_nodes']
        num_bins = self.metadata['num_bins']
        reference_turbine = self.metadata['reference_turbine']
        rho_air = self.metadata['rho_air']
        E_blade = self.metadata['E_blade']
        g = self.metadata['g']
        
        
#         # design variables
#         i = self.add_subsystem('dof', IndepVarComp(), promotes=['*'])
#         i.add_output('design_tsr', desc='design tip speed ratio')
#         i.add_output('blade_number', desc='number of blades')
#         i.add_output('rotor_diameter', units='m', desc='rotor diameter')
#         i.add_output('hub_radius', units = 'm', desc = 'hub radius')
#         i.add_output('chord_coefficients', units = 'm', desc = 'coefficients of polynomial chord profile', shape=num_pegged)
#         i.add_output('twist_coefficients', units = 'deg', desc = 'coefficients of polynomial twist profile', shape=num_pegged)
#         i.add_output('span_airfoil_r', units='m', desc='list of blade node radial location at which the airfoils are specified', shape=num_airfoils)
#         i.add_output('span_airfoil_id', desc='list of blade node Airfoil ID', shape=num_airfoils)
#         i.add_output('pitch', units = 'deg', desc = 'blade pitch angle')
#         i.add_output('thickness_factor', desc='scaling factor for laminate thickness')
#         i.add_output('shaft_angle', units='deg', desc='angle of the LSS inclindation with respect to the horizontal')
#         i.add_output('cut_in_speed', units = 'm/s', desc = 'cut-in wind speed')
#         i.add_output('cut_out_speed', units = 'm/s', desc = 'cut-out wind speed')
#         i.add_output('machine_rating', units='kW', desc='machine rating')
#         i.add_output('drive_train_efficiency', desc='efficiency of aerodynamic to electrical conversion')
        
        # sub systems
        self.add_subsystem('aero_design', aerodynamic_design.Scaling(num_pegged=num_pegged, num_nodes=num_nodes, \
                                                                     num_airfoils=num_airfoils, reference_turbine = reference_turbine), \
                           promotes_inputs=['rotor_diameter', 'hub_radius', \
                                            'chord_coefficients', 'twist_coefficients', \
                                            'span_airfoil_r', 'span_airfoil_id'], \
                           promotes_outputs=['span_r', 'span_chord', 'span_twist'])
        
        self.add_subsystem('struc_design', structural_design.VariableRadius(num_nodes=num_nodes, reference_turbine = reference_turbine), \
                           promotes_inputs=['rotor_diameter', 'thickness_factor', 'blade_number'], \
                           promotes_outputs=['blade_mass', 'blades_mass'])
                           
        
        self.add_subsystem('aero_partial', rotor_aerodynamics.BEM(num_nodes=num_nodes, rho_air=rho_air), \
                           promotes_inputs=['design_tsr', 'blade_number', 'rotor_diameter', 'hub_radius', 'pitch'], \
                           promotes_outputs=['rotor_cp', 'rotor_ct'])
                           
        
        self.add_subsystem('pc', power_curve.PowerCurve(num_bins=num_bins, rho_air=rho_air), \
                           promotes_inputs=['design_tsr', 'cut_in_speed', 'cut_out_speed', 'machine_rating', 'drive_train_efficiency'], \
                           promotes_outputs=['rated_wind_speed', 'wind_bin', 'elec_power_bin', 'ct_bin'])
                           
        
        self.add_subsystem('aero_rated', rotor_aerodynamics.BEM(num_nodes=num_nodes, rho_air=rho_air), \
                           promotes_inputs=['design_tsr', 'blade_number', 'rotor_diameter', 'hub_radius', 'pitch'], \
                           promotes_outputs=['rotor_speed', 'rotor_torque', 'rotor_thrust'])
        
        self.add_subsystem('mech', rotor_mechanics.Analytical(num_nodes=num_nodes, E_blade=E_blade, g=g), \
                           promotes_inputs=['shaft_angle'], \
                           promotes_outputs=['root_moment_flap', 'span_stress_max', 'tip_deflection'])  
        
        # connections
        self.connect('span_r', ['struc_design.span_r', 'aero_partial.span_r', \
                                'aero_rated.span_r', 'mech.span_r'])
        self.connect('aero_design.span_dr', ['struc_design.span_dr', 'aero_partial.span_dr', \
                                             'aero_rated.span_dr', 'mech.span_dr'])
        self.connect('aero_design.span_airfoil', ['aero_partial.span_airfoil', 'aero_rated.span_airfoil'])
        self.connect('span_chord', ['struc_design.span_chord', 'aero_partial.span_chord', \
                                    'aero_rated.span_chord', 'mech.span_chord'])
        self.connect('span_twist', ['aero_partial.span_twist', 'aero_rated.span_twist'])
        
        self.connect('struc_design.span_thickness', ['mech.span_thickness'])
        self.connect('struc_design.span_mass', ['mech.span_mass'])
        self.connect('struc_design.span_flap_stiff', ['mech.span_flap_stiff'])
        self.connect('struc_design.span_edge_stiff', ['mech.span_edge_stiff'])
        
        self.connect('aero_partial.swept_area', ['pc.swept_area'])
        self.connect('rotor_cp', ['pc.rotor_cp'])
        self.connect('rotor_ct', ['pc.rotor_ct'])
        
        self.connect('rated_wind_speed', ['aero_rated.wind_speed'])
        
        self.connect('aero_rated.span_fx', ['mech.span_fx'])
        self.connect('aero_rated.span_fy', ['mech.span_fy'])  










#############################################################################
##############################  UNIT TESTING ################################
# Activate (Uncomment) the design variables in the Group
############################################################################# 
if __name__ == "__main__":
    from time import time
    from WINDOW_openMDAO.src.api import beautify_dict
    
    start = time()
    
    # workflow setup
    prob = Problem(Blade(num_pegged=3, num_airfoils=8, num_nodes=20, num_bins=30, \
                         reference_turbine='Airfoils/reference_turbine.csv', \
                         rho_air=1.225, E_blade=36.233e9, g=9.8))
    prob.setup()
    #view_model(prob)
    
    # define inputs
    prob['design_tsr'] = 7.0
    prob['blade_number'] = 3
    prob['rotor_diameter'] = 126.0
    prob['hub_radius'] = 1.5
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
      
    prob.run_model()
    print 'Executed in ' + str(round(time() - start, 2)) + ' seconds\n'
     
    # print outputs 
    var_list = ['rotor_torque', 'rotor_thrust', 'rated_wind_speed' ,'wind_bin', 'elec_power_bin', \
                'ct_bin', 'root_moment_flap', 'span_stress_max', 'tip_deflection', 'blade_mass', \
                'rotor_cp', 'rotor_ct']
    saved_output = {}
    for v in var_list:
        saved_output[v] = prob[v]
        
        
    beautify_dict(saved_output)    
     
  
    
        

        

