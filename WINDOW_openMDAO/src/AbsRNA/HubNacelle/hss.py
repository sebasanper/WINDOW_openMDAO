from openmdao.api import ExplicitComponent

class AbsHSS(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('safety_factor', desc='Safety factor due to model fidelity', default=1.)
        
    def setup(self):
        # inputs
        self.add_input('rotor_diameter', units='m', desc='rotor diameter')
        self.add_input('rotor_torque', units='N*m', desc='rotor torque at rated power')
        self.add_input('gear_ratio', desc='overall gearbox ratio')
        self.add_input('lss_diameter', units='m', desc='low speed shaft outer diameter')
        self.add_input('gearbox_length', units = 'm', desc='gearbox length')
        self.add_input('gearbox_height', units = 'm', desc = 'gearbox height')
        self.add_input('gearbox_cm', units = 'm', desc = 'gearbox cm [x,y,z]', shape=3)
    
        # outputs
        self.add_output('mass', units='kg', desc='overall component mass')
        self.add_output('cm', units='m', desc='center of mass of the component in [x,y,z] for an arbitrary coordinate system', shape=3)
        self.add_output('I', units='kg*m**2', desc=' moments of Inertia for the component [Ixx, Iyy, Izz] around its center of mass', shape=3)
        self.add_output('length', units='m', desc='length of high speed shaft')
        