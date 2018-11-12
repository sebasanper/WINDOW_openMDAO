from openmdao.api import ExplicitComponent

class AbsGearbox(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('safety_factor', desc='Safety factor of the model fidelity', default=1)
        self.metadata.declare('gearbox_stages', desc='Number of stages in the gearbox', default=3)        
        self.metadata.declare('gear_configuration', desc='Parallel or Planetary configuration of each stage', default='eep')
        
    def setup(self):
        # metadata
        gearbox_stages = self.metadata['gearbox_stages']
        
        #inputs
        self.add_input('gear_ratio', desc='overall gearbox speedup ratio')
        self.add_input('Np', desc='number of planets in each stage', shape=gearbox_stages)
        self.add_input('rotor_speed', units='rpm', desc='rotor rpm at rated power')
        self.add_input('rotor_diameter', units='m', desc='rotor diameter')
        self.add_input('rotor_torque', units='N*m', desc='rotor torque at rated power')
        self.add_input('gearbox_cm_x', units='m', desc ='gearbox position along x-axis')
    
        # outputs
        self.add_output('stage_masses', units='kg', desc='individual gearbox stage masses', shape=gearbox_stages)
        self.add_output('mass', units='kg', desc='overall component mass')
        self.add_output('cm', units='m', desc='center of mass of the component in [x,y,z] for an arbitrary coordinate system', shape=3)
        self.add_output('I', units='kg*m**2', desc=' moments of Inertia for the component [Ixx, Iyy, Izz] around its center of mass', shape=3)    
        self.add_output('length', units='m', desc='gearbox length')
        self.add_output('height', units='m', desc='gearbox height')
        self.add_output('diameter', units='m', desc='gearbox diameter')
        self.add_output('efficiency', desc='gearbox transmission efficiency')