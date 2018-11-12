from openmdao.api import ExplicitComponent

class AbsRNACost(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('reference_turbine_cost', desc='URL of CSV file with the cost of the Reference Turbine components')
    
    def setup(self):
        # inputs
        self.add_input('machine_rating', units = 'kW', desc = 'machine rating of turbine')
        self.add_input('rotor_diameter', units = 'm', desc = 'rotor_diameter')
        self.add_input('blade_mass', units = 'kg', desc='mass of each blade')
        self.add_input('blade_number', desc='number of blades')        
        self.add_input('hub_mass', units='kg',desc='mass of Hub')
        self.add_input('pitch_mass', units='kg',desc='mass of Pitch System')
        self.add_input('spinner_mass', units='kg',desc='mass of spinner')
        self.add_input('lss_mass', units='kg', desc='component mass')
        self.add_input('main_bearing_mass', units='kg', desc='component mass')
        self.add_input('second_bearing_mass', units='kg', desc='component mass', val=0)
        self.add_input('gearbox_mass', units='kg', desc='component mass')
        self.add_input('hss_mass', units='kg', desc='component mass')
        self.add_input('generator_mass', units='kg', desc='component mass')
        self.add_input('bedplate_mass', units='kg', desc='component mass')
        self.add_input('platform_mass', units='kg', desc='component mass')
        self.add_input('crane_mass', units='kg', desc='component mass', val=0)
        self.add_input('yaw_mass', units='kg', desc='component mass')
        self.add_input('vs_electronics_mass', units='kg', desc='component mass')
        self.add_input('hvac_mass', units='kg', desc='component mass')
        self.add_input('cover_mass', units='kg', desc='component mass')
        self.add_input('transformer_mass', units='kg', desc='component mass', val=0)
        
        
        # outputs
        self.add_output('cost_blade', units='USD', desc='Cost of 1 blade', val=0.0)        
        self.add_output('cost_hub', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_pitch', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_spinner', units='USD', desc='component cost', val=0.0)        
        self.add_output('cost_lss', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_main_bearing', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_second_bearing', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_gearbox', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_hss', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_generator', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_mainframe', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_yaw', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_vs_electronics', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_hvac', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_cover', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_electrical', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_controls', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_transformer', units='USD', desc='component cost', val=0.0)
        self.add_output('cost_blades', units='USD', desc='Cost of all the blades', val=0.0)
        self.add_output('cost_hub_system', units='USD', desc='Hub System cost', val=0.0)
        self.add_output('cost_nacelle', units='USD', desc='Nacelle System cost', val=0.0)
        self.add_output('cost_rna', units='USD', desc='cost of RNA assembly', val=0.0)     