from openmdao.api import ExplicitComponent

class AbsGenerator(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('drivetrain_design', desc='Drive train configuration', default='geared') # ['geared', 'single_stage', 'multi_drive', 'pm_direct_drive']
    
    
    def setup(self):
        # inputs
        self.add_input('rotor_diameter', units='m', desc='rotor diameter')
        self.add_input('machine_rating', units='kW', desc='machine rating of generator')
        self.add_input('gear_ratio', desc='overall gearbox ratio')
        self.add_input('hss_length', units = 'm', desc='length of high speed shaft and brake')
        self.add_input('hss_cm', units = 'm', desc='cm of high speed shaft and brake', shape=3)
        self.add_input('rotor_speed', units='rpm', desc='Speed of rotor at rated power')
    
        # outputs
        self.add_output('mass', units='kg', desc='overall component mass')
        self.add_output('cm', units='m', desc='center of mass of the component in [x,y,z] for an arbitrary coordinate system', shape=3)
        self.add_output('I', units='kg*m**2', desc=' moments of Inertia for the component [Ixx, Iyy, Izz] around its center of mass', shape=3)
        