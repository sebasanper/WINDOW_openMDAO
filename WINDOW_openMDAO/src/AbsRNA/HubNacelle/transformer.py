from openmdao.api import ExplicitComponent

class AbsTransformer(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('uptower_transformer', desc='uptower or downtower transformer [True/False]', default=False)
        
        
    def setup(self):
        # inputs
        self.add_input('machine_rating', units='kW', desc='machine rating of the turbine')
        self.add_input('tower_top_diameter', units = 'm', desc = 'tower top diameter for comparision of nacelle CM')
        self.add_input('rotor_mass', units='kg', desc='rotor mass')
        self.add_input('overhang', units='m', desc='rotor overhang distance')
        self.add_input('generator_cm', units='m', desc='center of mass of the generator in [x,y,z]', shape=3)
        self.add_input('rotor_diameter', units='m', desc='rotor diameter of turbine')
        self.add_input('RNA_mass', units='kg', desc='mass of total RNA')
        self.add_input('RNA_cm', units='m', desc='RNA CM along x-axis')
    
        # outputs
        self.add_output('mass', units='kg', desc='overall component mass', val=0)
        self.add_output('cm', units='m', desc='center of mass of the component in [x,y,z] for an arbitrary coordinate system', val=[0., 0., 0.])
        self.add_output('I', units='kg*m**2', desc=' moments of Inertia for the component [Ixx, Iyy, Izz] around its center of mass', val=[0., 0., 0.])    
        
        
                