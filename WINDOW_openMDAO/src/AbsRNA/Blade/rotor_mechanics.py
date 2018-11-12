from openmdao.api import ExplicitComponent

class AbsRotorMechanics(ExplicitComponent):
    def initialize(self):
        self.metadata.declare('num_nodes', desc='Number of blade sections')
        self.metadata.declare('E_blade', desc='Youngs modulus of glass fiber [Pa]', default=36.233e9)
        self.metadata.declare('g', desc='acceleration due to gravity [m/s**2]', default=9.8)
        
    def setup(self):        
        # metadata
        num_nodes = self.metadata['num_nodes']
        
        # inputs
        self.add_input('shaft_angle', units='deg', desc='angle of the LSS inclindation with respect to the horizontal')
        self.add_input('span_r', units='m', desc='list of blade node radial location', shape=num_nodes)
        self.add_input('span_dr', units='m', desc='spanwise blade node thickness', shape=num_nodes)
        self.add_input('span_chord', units='m', desc='spanwise chord distribution', shape=num_nodes)
        self.add_input('span_thickness', units='m', desc='spanwise blade thickness', shape=num_nodes)
        self.add_input('span_mass', units='kg/m', desc='spanwise blade node mass per unit length', shape=num_nodes)
        self.add_input('span_flap_stiff', units = 'N*m**2', desc = 'spanwise flapwise stiffness', shape=num_nodes)
        self.add_input('span_edge_stiff', units = 'N*m**2', desc = 'spanwise edgewise stiffness', shape=num_nodes)
        self.add_input('span_fx', units = 'N/m', desc = 'spanwise force normal to rotation', shape=num_nodes)
        self.add_input('span_fy', units = 'N/m', desc = 'spanwise force tangential to rotation', shape=num_nodes)        
     
        # outputs
        self.add_output('root_moment_flap', units = 'N*m', desc='flapping moment at blade root')
        self.add_output('span_moment_flap', units = 'N*m', desc='spanwise flapping moment', shape=num_nodes)
        self.add_output('span_moment_edge', units = 'N*m', desc='spanwise edge-wise moment', shape=num_nodes)
        self.add_output('span_moment_gravity', units = 'N*m', desc='spanwise edge-wise moment', shape=num_nodes)
        self.add_output('span_stress_flap', units = 'Pa', desc='spanwise flapping stress', shape=num_nodes)
        self.add_output('span_stress_edge', units = 'Pa', desc='spanwise edgewise stress', shape=num_nodes)
        self.add_output('span_stress_gravity', units = 'Pa', desc='spanwise gravity loading', shape=num_nodes)
        self.add_output('span_stress_max', units = 'Pa', desc='maximum loading')
        self.add_output('tip_deflection', units = 'm', desc='tip deflection from neutral point')