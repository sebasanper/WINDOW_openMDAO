from openmdao.api import ExplicitComponent

class AbsAerodynamicDesign(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('num_pegged', desc='Number of pegged nodes required to define the chord/twist profile')
        self.metadata.declare('num_airfoils', desc='Number of airfoils along the blade')
        self.metadata.declare('num_nodes', desc='Number of blade sections')
        self.metadata.declare('reference_turbine', desc='URL of CSV file with the definition of the Reference Turbine')
        
        
    def setup(self):        
        # metadata
        num_pegged = self.metadata['num_pegged']
        num_airfoils = self.metadata['num_airfoils']
        num_nodes = self.metadata['num_nodes']
        
        # inputs
        self.add_input('rotor_diameter', units='m', desc='rotor diameter')
        self.add_input('hub_radius', units = 'm', desc = 'hub radius')
        self.add_input('chord_coefficients', units = 'm', desc = 'coefficients of polynomial chord profile', shape=num_pegged)
        self.add_input('twist_coefficients', units = 'deg', desc = 'coefficients of polynomial twist profile', shape=num_pegged)
        self.add_input('span_airfoil_r', units='m', desc='list of blade node radial location at which the airfoils are specified', shape=num_airfoils)
        self.add_input('span_airfoil_id', desc='list of blade node Airfoil ID', shape=num_airfoils)
        
        # outputs
        self.add_output('span_r', units='m', desc='spanwise radial location of blade junctions', shape=num_nodes)
        self.add_output('span_dr', units='m', desc='spanwise blade node thickness', shape=num_nodes)
        self.add_output('span_airfoil', desc='list of blade node airfoil ID', shape=num_nodes)
        self.add_output('span_chord', units='m', desc='list of blade node chord length', shape=num_nodes)
        self.add_output('span_twist', units='deg', desc='list of blade node twist angle', shape=num_nodes)

    


 