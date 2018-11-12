from openmdao.api import ExplicitComponent

class AbsRNAAssembly(ExplicitComponent):
    def setup(self):
        # inputs
        self.add_input('yawMass', units='kg', desc='mass of yaw system')
        self.add_input('lss_mass', units='kg', desc='component mass')
        self.add_input('main_bearing_mass', units='kg', desc='component mass')
        self.add_input('second_bearing_mass', units='kg', desc='component mass', val=0)
        self.add_input('gearbox_mass', units='kg', desc='component mass')
        self.add_input('hss_mass', units='kg', desc='component mass')
        self.add_input('generator_mass', units='kg', desc='component mass')
        self.add_input('lss_cm', units='m', desc='component CM', shape=3)
        self.add_input('main_bearing_cm', units='m', desc='component CM', shape=3)
        self.add_input('second_bearing_cm', units='m', desc='component CM', shape=3)
        self.add_input('gearbox_cm', units='m', desc='component CM', shape=3)
        self.add_input('hss_cm', units='m', desc='component CM', shape=3)
        self.add_input('generator_cm', units='m', desc='component CM', shape=3)
        self.add_input('overhang', units='m', desc='nacelle overhang')
        self.add_input('rotor_mass', units='kg', desc='component mass')
        self.add_input('machine_rating', units = 'kW', desc = 'machine rating')
    
        # outputs
        self.add_output('RNA_mass', units='kg', desc='mass of total RNA')
        self.add_output('RNA_cm', units='m', desc='RNA CM along x-axis', shape=3)           