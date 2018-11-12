from openmdao.api import ExplicitComponent

class AbsSpinner(ExplicitComponent):
    def setup(self):
        # inputs
        self.add_input('rotor_diameter', units='m', desc='rotor diameter')
    
        # outputs
        self.add_output('mass', units='kg', desc='overall component mass')                                           
           
        
        