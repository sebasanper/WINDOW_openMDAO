from openmdao.api import ExplicitComponent 

class AbsHub(ExplicitComponent):
    def setup(self):
        # inputs
        self.add_input('blade_root_diameter', units='m', desc='blade root diameter')
        self.add_input('machine_rating', units = 'kW', desc = 'machine rating of turbine')
        self.add_input('blade_number', desc='number of turbine blades')
    
        # outputs
        self.add_output('diameter', units='m', desc='hub diameter')
        self.add_output('thickness', units='m',desc='hub thickness')
        self.add_output('mass', units='kg', desc='overall component mass')
        