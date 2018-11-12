from openmdao.api import ExplicitComponent

class AbsLSS(ExplicitComponent):
    
    def initialize(self):
        self.metadata.declare('safety_factor', desc='Safety factor due to model fidelity', default=1)
        self.metadata.declare('mb1_type', desc='Upwind main bearing type') # ['CARB','TRB1','TRB2','SRB','CRB','RB']
        self.metadata.declare('mb2_type', desc='Downwind main bearing type', allow_none=True)
        
    def setup(self):
        # inputs
        self.add_input('rotor_bending_moment', units='N*m', desc='The bending moment about the x axis', shape=3)
        self.add_input('rotor_force', units='N', desc='The force along the x axis applied at hub center', shape=3)
        self.add_input('rotor_mass', units='kg', desc='rotor mass')
        self.add_input('rotor_diameter', units='m', desc='rotor diameter')
        self.add_input('machine_rating', units='kW', desc='machine rating of the turbine')
        self.add_input('gearbox_mass', units='kg', desc='Gearbox mass')
        self.add_input('overhang', units='m', desc='Overhang distance')
        self.add_input('gearbox_cm', units = 'm', desc = 'center of mass of gearbox', shape=3)
        self.add_input('gearbox_length', units='m', desc='gearbox length')
        self.add_input('shaft_angle', units='rad', desc='Angle of the LSS inclindation with respect to the horizontal')
        
        # outputs
        self.add_output('length', units='m', desc='lss length')
        self.add_output('diameter1', units='m', desc='lss outer diameter at main bearing')
        self.add_output('diameter2', units='m', desc='lss outer diameter at second bearing')
        self.add_output('mass', units='kg', desc='overall component mass')
        self.add_output('cm', units='m', desc='center of mass of the component in [x,y,z] for an arbitrary coordinate system', shape=3)
        self.add_output('I', units='kg*m**2', desc=' moments of Inertia for the component [Ixx, Iyy, Izz] around its center of mass', shape=3)
        self.add_output('FW_mb1', units='m', desc='facewidth of main bearing') 
        self.add_output('FW_mb2', units='m', desc='facewidth of second main bearing')   
        self.add_output('bearing_mass1', units = 'kg', desc='main bearing mass')
        self.add_output('bearing_mass2', units = 'kg', desc='main bearing mass', val=0) #zero for 3-pt model
        self.add_output('bearing_location1', units = 'm', desc = 'main bearing 1 center of mass', shape=3)
        self.add_output('bearing_location2', units = 'm', desc = 'main bearing 2 center of mass', val=[0., 0., 0.])
        