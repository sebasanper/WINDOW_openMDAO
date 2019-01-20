from openmdao.api import ExplicitComponent

class AbsPowerCurve(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('num_bins', desc='Number of wind speed samples')
        self.metadata.declare('rho_air',  desc='Density of air [kg/m**3]', default=1.225)
        self.metadata.declare('power_file', desc='URL of power curve file')
        self.metadata.declare('ct_file', desc='URL of thrust coefficient curve file')
        
    def setup(self):
        # metadata
        num_bins = self.metadata['num_bins']
        
        # inputs
        self.add_input('design_tsr', desc='design tip speed ratio')
        self.add_input('cut_in_speed', units = 'm/s', desc = 'cut-in wind speed')
        self.add_input('cut_out_speed', units = 'm/s', desc = 'cut-out wind speed')
        self.add_input('swept_area', units='m**2', desc='rotor swept area')
        self.add_input('machine_rating', units='kW', desc='machine rating')
        self.add_input('drive_train_efficiency', desc='efficiency of aerodynamic to electrical conversion', val=1.0)
        self.add_input('rotor_cp', desc='rotor power coefficient')
        self.add_input('rotor_ct', desc='rotor thrust coefficient')
        
        # outputs
        self.add_output('rated_wind_speed', units = 'm/s', desc = 'rated wind speed')
        self.add_output('rated_tip_speed', units = 'm/s', desc = 'rated tip speed')
        self.add_output('wind_bin', units = 'm/s', desc='list of wind speeds', shape=num_bins)
        self.add_output('elec_power_bin', units='kW', desc='list of electrical power output', shape=num_bins)
        self.add_output('aero_power_bin', units='kW', desc='list of aerodynamic power output', shape=num_bins)
        self.add_output('thrust_bin', units = 'N', desc='list of rotor thrust', shape=num_bins)
        self.add_output('cp_bin', desc='list of power coefficients', shape=num_bins)
        self.add_output('ct_bin', desc='list of thrust coefficients', shape=num_bins)