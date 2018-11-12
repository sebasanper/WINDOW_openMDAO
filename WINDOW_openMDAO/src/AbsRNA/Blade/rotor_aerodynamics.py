from openmdao.api import ExplicitComponent


class AbsRotorAerodynamics(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('num_nodes',  desc='Number of blade sections')
        self.metadata.declare('rho_air',    desc='Density of air [kg/m**3]', default=1.225)

        
        
    def setup(self):
        # metadata
        num_nodes = self.metadata['num_nodes']
        
        # inputs
        self.add_input('design_tsr', desc='design tip speed ratio')
        self.add_input('wind_speed', units = 'm/s', desc = 'wind speed at hub height', val=8.0)
        self.add_input('blade_number', desc='number of blades')
        self.add_input('rotor_diameter', units='m', desc='rotor diameter')
        self.add_input('hub_radius', units = 'm', desc = 'hub radius')
        self.add_input('span_r', units='m', desc='list of blade node radial location', shape=num_nodes)
        self.add_input('span_dr', units='m', desc='list of blade annulus thickness', shape=num_nodes)
        self.add_input('span_airfoil', desc='list of blade node Airfoil ID', shape=num_nodes)
        self.add_input('span_chord', units='m', desc='list of blade node chord length', shape=num_nodes)
        self.add_input('span_twist', units='deg',desc='list of blade node twist angle', shape=num_nodes)
        self.add_input('pitch', units = 'deg', desc = 'blade pitch angle')
     
        # outputs        
        self.add_output('rotor_speed', units='rpm', desc='rotor speed')
        self.add_output('swept_area', units='m**2', desc='rotor swept area')
        self.add_output('rotor_cp', desc='rotor power coefficient')
        self.add_output('rotor_cq', desc='rotor torque coefficient')
        self.add_output('rotor_ct',  desc='rotor thrust coefficient')
        self.add_output('rotor_power', units='W', desc='rotor power')
        self.add_output('rotor_torque', units='N*m', desc='rotor torque')
        self.add_output('rotor_thrust',  units='N', desc='rotor thrust')
        self.add_output('span_fx', units='N/m', desc='list of spanwise normal force to the plane of rotation', shape=num_nodes)
        self.add_output('span_fy', units='N/m', desc='list of spanwise tangential force to the plane of rotation', shape=num_nodes)
  