from openmdao.api import ExplicitComponent


class LCOE(ExplicitComponent):

    def setup(self):

        self.add_input('investment_costs', val=0.0)
        self.add_input('oandm_costs', val=0.0)
        self.add_input('decommissioning_costs', val=0.0)
        self.add_input('AEP', val=0.0)
        self.add_input('transm_electrical_efficiency', val=0.0)
        self.add_input('operational_lifetime', val=0.0)
        self.add_input('interest_rate', val=0.0)

        self.add_output('LCOE', val=0.0)

    def compute(self, inputs, outputs):
        investment_costs = inputs['investment_costs']
        oandm_costs = inputs['oandm_costs']
        decommissioning_costs = inputs['decommissioning_costs']
        AEP = inputs['AEP']
        transm_electrical_efficiency = inputs['transm_electrical_efficiency']
        operational_lifetime = inputs['operational_lifetime']
        interest_rate = inputs['interest_rate']

        annuity = 1.0 / interest_rate * (1.0 - 1.0 / (1.0 + interest_rate) ** operational_lifetime)
        lcoe_previous = (investment_costs * 100.0) / (annuity * (AEP / 1000.0)) + oandm_costs * 100.0 / (AEP / 1000.0) + decommissioning_costs * 100.0 * (1.0 + 0.075) ** (- operational_lifetime) / (annuity * (AEP / 1000.0))

        lcoe = lcoe_previous / transm_electrical_efficiency

        outputs['LCOE'] = lcoe
