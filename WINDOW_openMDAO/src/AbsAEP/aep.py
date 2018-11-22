from openmdao.api import ExplicitComponent


class AEP(ExplicitComponent):

    def setup(self):
        self.add_input('aeroAEP', val=0.0)
        self.add_input('availability', val=0.0)
        self.add_input('electrical_efficiency', val=0.0)

        self.add_output('AEP', val=0.0)

        #self.declare_partials(of='AEP', wrt=['aeroAEP', 'availability', 'electrical_efficiency'], method='fd')

    def compute(self, inputs, outputs):
        # aeroaep = 2723354011950
        aeroaep = inputs['aeroAEP']
        outputs['AEP'] = aeroaep * inputs['availability'] * inputs['electrical_efficiency']
