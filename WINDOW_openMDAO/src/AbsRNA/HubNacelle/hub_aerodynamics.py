from openmdao.api import ExplicitComponent

class AbsHubAerodynamics(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('safety_factor', desc='Safety factor due to model fidelity', default=1.)
        self.metadata.declare('g', desc='acceleration due to gravity', default=9.8)
        
        
    def setup(self):
        # inputs
        self.add_input('hub_mass', units = 'kg', desc = 'mass of the hub')
        self.add_input('pitch_mass', units = 'kg', desc = 'mass of pitching system')
        self.add_input('spinner_mass', units = 'kg', desc = 'mass of the spinner')        
        self.add_input('blade_number', desc='number of turbine blades')
        self.add_input('blade_mass', units = 'kg', desc='mass of the one blade')
        self.add_input('shaft_angle', units='deg', desc='angle of the main shaft inclindation wrt the horizontal')
        self.add_input('rotor_torque', units='N*m', desc='rotor torque')
        self.add_input('rotor_thrust',  units='N', desc='rotor thrust')
    
        # outputs
        self.add_output('hub_assembly_mass', units = 'kg', desc = 'mass of the hub assembly')
        self.add_output('rotor_mass', units = 'kg', desc = 'mass of the rotor = hub + blades')
        self.add_output('rotor_force', units='N', desc='rotor load vector in hub coordinate system', val=[0., 0., 0.])
        self.add_output('rotor_moment',  units='N*m', desc='rotor moment vector in hub coordinate system', val=[0., 0., 0.])


        