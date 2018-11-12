from openmdao.api import ExplicitComponent

class AbsNacelle(ExplicitComponent):
    def setup(self):
        # inputs
        self.add_input('above_yaw_mass', units='kg', desc='mass above yaw system')
        self.add_input('yawMass', units='kg', desc='mass of yaw system')
        self.add_input('lss_mass', units='kg', desc='component mass')
        self.add_input('main_bearing_mass', units='kg', desc='component mass')
        self.add_input('second_bearing_mass', units='kg', desc='component mass', val=0)
        self.add_input('gearbox_mass', units='kg', desc='component mass')
        self.add_input('hss_mass', units='kg', desc='component mass')
        self.add_input('generator_mass', units='kg', desc='component mass')
        self.add_input('bedplate_mass', units='kg', desc='component mass')
        self.add_input('mainframe_mass', units='kg', desc='component mass')
        self.add_input('lss_cm', units='m', desc='component CM', shape=3)
        self.add_input('main_bearing_cm', units='m', desc='component CM', shape=3)
        self.add_input('second_bearing_cm', units='m', desc='component CM', shape=3)
        self.add_input('gearbox_cm', units='m', desc='component CM', shape=3)
        self.add_input('hss_cm', units='m', desc='component CM', shape=3)
        self.add_input('generator_cm', units='m', desc='component CM', shape=3)
        self.add_input('bedplate_cm', units='m', desc='component CM', shape=3)
        self.add_input('lss_I', units='kg*m**2', desc='component I', shape=3)
        self.add_input('main_bearing_I', units='kg*m**2', desc='component I', shape=3)
        self.add_input('second_bearing_I', units='kg*m**2', desc='component I', shape=3)
        self.add_input('gearbox_I', units='kg*m**2', desc='component I', shape=3)
        self.add_input('hss_I', units='kg*m**2', desc='component I', shape=3)
        self.add_input('generator_I', units='kg*m**2', desc='component I', shape=3)
        self.add_input('bedplate_I', units='kg*m**2', desc='component I', shape=3)
        self.add_input('transformer_mass', units='kg', desc='component mass', val=0)
        self.add_input('transformer_cm', units='m', desc='component CM', shape=3)
        self.add_input('transformer_I', units='kg*m**2', desc='component I', shape=3)
    
        # outputs
        self.add_output('nacelle_mass', units='kg', desc='overall component mass')
        self.add_output('nacelle_cm', units='m', desc='center of mass of the component in [x,y,z] for an arbitrary coordinate system', shape=3)
        self.add_output('nacelle_I', units='kg*m**2', desc=' moments of Inertia for the component [Ixx, Iyy, Izz] around its center of mass', shape=6)