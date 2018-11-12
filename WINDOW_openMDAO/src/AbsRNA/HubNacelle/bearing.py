from openmdao.api import ExplicitComponent

class AbsBearing(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('safety_factor', desc='Safety factor due to model fidelity', default=1)
        
    def setup(self):
        # inputs
        self.add_input('bearing_mass', units = 'kg', desc = 'bearing mass from LSS model', val=0)
        self.add_input('lss_diameter', units='m', desc='lss outer diameter at main bearing')
        self.add_input('rotor_torque', units='N*m', desc='lss design torque')
        self.add_input('rotor_diameter', units='m', desc='rotor diameter')
        self.add_input('location', units = 'm', desc = 'x,y,z location from shaft model', shape=3)
    
        # outputs
        self.add_output('mass', units='kg', desc='bearing mass', val=0)
        self.add_output('cm', units='m', desc='center of mass of bearing in [x,y,z] for an arbitrary coordinate system', shape=3)
        self.add_output('I', units='kg*m**2', desc=' moments of Inertia for bearing [Ixx, Iyy, Izz] around its center of mass', shape=3)
        