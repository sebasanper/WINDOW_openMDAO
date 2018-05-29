from openmdao.api import ExplicitComponent



class AbstractOandM(ExplicitComponent):

    def setup(self):
        self.add_input('AEP', val=0.0)
        self.add_input('array_efficiency', val=0.0)

        self.add_output('annual_cost_O&M', val=0.0)
        self.add_output('availability', val=0.0)


    def compute(self, inputs, outputs):
        AEP = inputs['AEP']
        eff = inputs['array_efficiency']
        outputs['annual_cost_O&M'], outputs['availability'] = self.OandM_model(AEP, eff)
