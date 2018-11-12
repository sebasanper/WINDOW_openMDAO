from openmdao.api import ExplicitComponent

class AbsStructuralDesign(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('num_nodes', desc='Number of blade sections')
        self.metadata.declare('reference_turbine', desc='URL of CSV file with the definition of the Reference Turbine')
        
    def setup(self):        
        # metadata
        num_nodes = self.metadata['num_nodes']
        
        # inputs
        self.add_input('rotor_diameter', units='m', desc='rotor diameter')
        self.add_input('thickness_factor', desc='scaling factor for laminate thickness')
        self.add_input('span_r', units='m', desc='spanwise dimensionless radial location', shape=num_nodes)
        self.add_input('span_dr', units='m', desc='spanwise blade node thickness', shape=num_nodes)
        self.add_input('span_chord', units='m', desc='spanwise chord length', shape=num_nodes)   
        self.add_input('blade_number', desc='number of blades')     
        
        # outputs
        self.add_output('span_thickness', units='m', desc='spanwise blade thickness', shape=num_nodes)
        self.add_output('span_mass', units='kg/m', desc='spanwise blade node mass per unit length', shape=num_nodes)
        self.add_output('span_flap_inertia', units = 'm**4', desc = 'spanwise second moment of flapwise area', shape=num_nodes)
        self.add_output('span_edge_inertia', units = 'm**4', desc = 'spanwise second moment of edgewise area', shape=num_nodes)
        self.add_output('span_flap_stiff', units = 'N*m**2', desc = 'spanwise flapwise stiffness', shape=num_nodes)
        self.add_output('span_edge_stiff', units = 'N*m**2', desc = 'spanwise edgewise stiffness', shape=num_nodes)
        self.add_output('blade_mass', units = 'kg', desc='mass of one blade')
        self.add_output('blades_mass', units = 'kg', desc='mass of all blades')
       