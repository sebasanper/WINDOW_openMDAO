from openmdao.api import ExplicitComponent

class AbsYaw(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('safety_factor', desc='Safety factor due to model fidelity', default=1)
        
    def setup(self):
        # inputs
        self.add_input('rotor_diameter', units='m', desc='rotor diameter')
        self.add_input('rotor_thrust', units='N', desc='maximum rotor thrust')
        self.add_input('tower_top_diameter', units='m', desc='tower top diameter')
        #self.add_input('above_yaw_mass', units='kg', desc='above yaw mass', val=0)
        #self.add_input('bedplate_height', units = 'm', desc = 'bedplate height', val=0)
    
        # outputs
        self.add_output('mass', units='kg', desc='overall component mass')
        self.add_output('cm', units='m', desc='center of mass of the component in [x,y,z] for an arbitrary coordinate system', shape=3)
        self.add_output('I', units='kg*m**2', desc=' moments of Inertia for the component [Ixx, Iyy, Izz] around its center of mass', shape=3)    

            