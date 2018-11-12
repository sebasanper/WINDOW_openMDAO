from openmdao.api import Group, Problem, IndepVarComp, view_model
import hub, pitch, spinner, hub_aerodynamics



#############################################################################
################################  WORKFLOWS #################################
#############################################################################
class Hub(Group):
    def initialize(self):
        self.metadata.declare('safety_factor', desc='Safety factor due to model fidelity', default=1.)
        self.metadata.declare('g', desc='acceleration due to gravity', default=9.8)
        
    def setup(self):
        # metadata
        safety_factor = self.metadata['safety_factor']
        g = self.metadata['g']
        
#         # design variables
#         i = self.add_subsystem('dof', IndepVarComp(), promotes=['*'])
#         i.add_output('rotor_diameter', units='m', desc='rotor diameter')
#         i.add_output('blade_number', desc='number of turbine blades')
#         i.add_output('blade_root_diameter', units='m', desc='blade root diameter')
#         i.add_output('machine_rating', units = 'MW', desc = 'machine rating of turbine')
#         i.add_output('blade_mass', units='kg', desc='mass of one blade')
#         i.add_output('rotor_bending_moment', units='N*m', desc='flapwise bending moment at blade root')
#         i.add_output('shaft_angle', units='deg', desc='angle of the main shaft inclindation wrt the horizontal')
#         i.add_output('rotor_torque', units='N*m', desc='rotor torque')
#         i.add_output('rotor_thrust',  units='N', desc='rotor thrust')
        
        
        # sub-systems     
        self.add_subsystem('hub', hub.DriveSE(), \
                           promotes_inputs=['blade_root_diameter', 'machine_rating', 'blade_number'], \
                           promotes_outputs=[('diameter', 'hub_diameter'), ('thickness', 'hub_thickness'), ('mass', 'hub_mass')])
        
        self.add_subsystem('pitch', pitch.DriveSE(safety_factor=safety_factor), \
                           promotes_inputs=['blade_mass', 'rotor_bending_moment', 'blade_number'], \
                           promotes_outputs=[('mass', 'pitch_mass')])
        
        self.add_subsystem('spinner', spinner.DriveSE(), \
                           promotes_inputs=['rotor_diameter'],  \
                           promotes_outputs=[('mass', 'spinner_mass')])  
        
        self.add_subsystem('aero', hub_aerodynamics.Tanuj(safety_factor=safety_factor, g=g), \
                            promotes_inputs=['blade_number', 'blade_mass', 'shaft_angle', 'rotor_torque', 'rotor_thrust'], \
                            promotes_outputs=['hub_assembly_mass', 'rotor_mass', 'rotor_force', 'rotor_moment'])
                        
        
        # connections
        self.connect('hub_mass', 'aero.hub_mass')
        self.connect('pitch_mass', 'aero.pitch_mass')
        self.connect('spinner_mass', 'aero.spinner_mass')






#############################################################################
##############################  UNIT TESTING ################################
# Activate (Uncomment) the design variables in the Group
############################################################################# 
if __name__ == "__main__":
    from time import time
    from math import pi
    from WINDOW_openMDAO.src.api import beautify_dict
    
    start = time()
    
    # workflow setup
    prob = Problem(Hub(safety_factor=1.5, g=9.8))
    prob.setup()
    #view_model(prob)
    
    # define inputs
    prob['dof.rotor_diameter'] = 126.0
    prob['dof.blade_number'] = 3
    prob['dof.blade_root_diameter'] = 3.542
    prob['dof.machine_rating'] = 5000.0
    prob['dof.blade_mass'] = 51352.9261/3.
    prob['dof.rotor_bending_moment'] = (3.06 * pi / 8) * 1.225 * (11.05 ** 2) * (0.0517 * (126.0 ** 3)) / 3.0
    prob['dof.shaft_angle'] = 5.0
    prob['dof.rotor_torque'] = (5000*1000/0.95)/(12.1*pi/30)
    prob['dof.rotor_thrust'] = 599610.0
      
    prob.run_model()
    print 'Executed in ' + str(round(time() - start, 2)) + ' seconds\n'
     
    # print outputs 
    var_list = ['hub_diameter', 'hub_thickness', 'hub_mass', 'pitch_mass', 'spinner_mass', 'hub_assembly_mass', \
                  'rotor_mass', 'rotor_force', 'rotor_moment']
    saved_output = {}
    for v in var_list:
        saved_output[v] = prob[v]
        
        
    beautify_dict(saved_output)  
        
        
        
        
        
