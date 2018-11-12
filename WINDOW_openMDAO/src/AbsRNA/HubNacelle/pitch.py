from openmdao.api import ExplicitComponent

class AbsPitch(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('safety_factor', desc='Safety factor due to model fidelity', default=1)
        
    def setup(self):
        # inputs
        self.add_input('blade_mass', units='kg', desc='mass of one blade')
        self.add_input('rotor_bending_moment', units='N*m', desc='flapwise bending moment at blade root')
        self.add_input('blade_number', desc='number of turbine blades')
    
        # outputs
        self.add_output('mass', units='kg', desc='overall component mass')    