from openmdao.api import ExplicitComponent

class AbsAboveYaw(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('has_crane', desc='Is the crane present? [0/1]', default=0)
        
        
    def setup(self):
        # inputs
        self.add_input('machine_rating', units='kW', desc='machine rating')
        self.add_input('lss_mass', units='kg', desc='component mass')
        self.add_input('main_bearing_mass', units='kg', desc='component mass')
        self.add_input('second_bearing_mass', units='kg', desc='component mass', val=0)
        self.add_input('gearbox_mass', units='kg', desc='component mass')
        self.add_input('hss_mass', units='kg', desc='component mass')
        self.add_input('generator_mass', units='kg', desc='component mass')
        self.add_input('bedplate_mass', units='kg', desc='component mass')
        self.add_input('bedplate_length', units='m', desc='component length')
        self.add_input('bedplate_width', units='m', desc='component width')
        self.add_input('transformer_mass', units = 'kg', desc='Transformer mass', val=0)
    
        # outputs
        self.add_output('electrical_mass', units='kg', desc='component mass')
        self.add_output('vs_electronics_mass', units='kg', desc='component mass')
        self.add_output('hvac_mass', units='kg', desc='component mass')
        self.add_output('controls_mass', units='kg', desc='component mass')
        self.add_output('platforms_mass', units='kg', desc='component mass')
        self.add_output('crane_mass', units='kg', desc='component mass', val=0)
        self.add_output('mainframe_mass', units='kg', desc='component mass')
        self.add_output('cover_mass', units='kg', desc='component mass')
        self.add_output('above_yaw_mass', units='kg', desc='total mass above yaw system')
        self.add_output('length', units='m', desc='component length')
        self.add_output('width', units='m', desc='component width')
        self.add_output('height', units='m', desc='component height')            