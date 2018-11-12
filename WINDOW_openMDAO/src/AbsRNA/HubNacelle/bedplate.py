from openmdao.api import ExplicitComponent

class AbsBedplate(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('safety_factor', desc='Safety factor due to model fidelity', default=1.)
        self.metadata.declare('uptower_transformer', desc='Is uptower transformer present? [True/False]', default=False)
        
        
    def setup(self):
        # inputs
        self.add_input('gbx_length', units = 'm', desc = 'gearbox length')
        self.add_input('gbx_location', units = 'm', desc = 'gearbox CM location')
        self.add_input('gbx_mass', units = 'kg', desc = 'gearbox mass')
        self.add_input('hss_location', units = 'm', desc='HSS CM location')
        self.add_input('hss_mass', units = 'kg', desc='HSS mass')
        self.add_input('generator_location', units = 'm', desc='generator CM location')
        self.add_input('generator_mass', units = 'kg', desc='generator mass')
        self.add_input('lss_location', units = 'm', desc='LSS CM location')
        self.add_input('lss_mass', units = 'kg', desc='LSS mass')
        self.add_input('lss_length', units = 'm', desc = 'LSS length')
        self.add_input('mb1_location', units = 'm', desc='Upwind main bearing CM location')
        self.add_input('FW_mb1', units = 'm', desc = 'Upwind main bearing facewidth')
        self.add_input('mb1_mass', units = 'kg', desc='Upwind main bearing mass')
        self.add_input('mb2_location', units = 'm', desc='Downwind main bearing CM location', val=0)
        self.add_input('mb2_mass', units = 'kg', desc='Downwind main bearing mass', val=0)
        self.add_input('tower_top_diameter', units = 'm', desc='diameter of the top tower section at the yaw gear')
        self.add_input('rotor_diameter', units = 'm', desc='rotor diameter')
        self.add_input('machine_rating', units='kW', desc='machine_rating machine rating of the turbine')
        self.add_input('rotor_mass', units='kg', desc='rotor mass')
        self.add_input('rotor_bending_moment', units='N*m', desc='The bending moment about the y axis', shape=3)
        self.add_input('rotor_force', units='N', desc='The force along the z axis applied at hub center', shape=3)
        self.add_input('overhang', units='m', desc='Overhang distance')
        self.add_input('transformer_mass', units = 'kg', desc='Transformer mass', val=0)
        self.add_input('transformer_location', units = 'm', desc = 'transformer CM location', val=0)
    
        # outputs
        self.add_output('mass', units='kg', desc='overall component mass')
        self.add_output('cm', units='m', desc='center of mass of the component in [x,y,z] for an arbitrary coordinate system', shape=3)
        self.add_output('I', units='kg*m**2', desc=' moments of Inertia for the component [Ixx, Iyy, Izz] around its center of mass', shape=3)    
        self.add_output('length', units='m', desc='length of bedplate')
        self.add_output('height', units='m', desc='max height of bedplate')
        self.add_output('width', units='m', desc='width of bedplate')
