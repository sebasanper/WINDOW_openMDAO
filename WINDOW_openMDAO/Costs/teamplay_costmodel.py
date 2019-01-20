from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import max_n_turbines
from costs.other_costs import other_costs


class TeamPlayCostModel(ExplicitComponent):

    def setup(self):
        self.add_input('n_substations', val=0)
        self.add_input('n_turbines', val=0)
        self.add_input('length_p_cable_type', shape=3)
        self.add_input('cost_p_cable_type', shape=3)
        self.add_input('support_structure_costs', shape=max_n_turbines)
        self.add_input('depth_central_platform', val=0.0)
        self.add_input('machine_rating', units='W', desc='machine rating', val=10e6)
        self.add_input('rotor_radius', units='m', desc='rotor radius', val=95.4)
        self.add_input('hub_height', units='m', desc='hub height', val=119.0)
        self.add_input('purchase_price', desc='turbine cost in EUR', val=10000000.0)
        self.add_input('warranty_percentage', desc='insurance of the turbines % to its cost price', val=15)
        self.add_input('rna_mass', units='kg', desc='mass of RNA', val=589211.0)
        self.add_input('generator_voltage', units='V', desc='voltage at generator', val=4000.0)
        self.add_input('collection_voltage', units='V', desc='voltage at substation', val=66000.0)
        
        self.add_output('investment_costs', val=0.0)
        self.add_output('decommissioning_costs', val=0.0)

        #self.declare_partals(of=['investment_costs', 'decommissioning_costs'], wrt=['n_substations', 'n_turbines', 'length_p_cable_type', 'cost_p_cable_type', 'support_structure_costs', 'depth_central_platform'], method='fd')

    def compute(self, inputs, outputs):
        n_substations = inputs['n_substations']
        n_turbines = inputs['n_turbines']
        length_p_cable_type = inputs['length_p_cable_type']
        cost_p_cable_type = inputs['cost_p_cable_type']
        support_structure_costs = inputs['support_structure_costs']
        depth_central_platform = inputs['depth_central_platform']
        other_investment, outputs['decommissioning_costs'] = other_costs(depth_central_platform, n_turbines, sum(length_p_cable_type), n_substations, \
                                                                         inputs['machine_rating'], inputs['rotor_radius'], inputs['purchase_price'], inputs['warranty_percentage'], \
                                                                         inputs['rna_mass'], inputs['hub_height'], inputs['generator_voltage'], inputs['collection_voltage'])
        # other_investment = 0.0
        infield_cable_investment = sum(cost_p_cable_type)
        # infield_cable_investment = 7973617.59755
        support_structure_investment = sum(support_structure_costs)
        # support_structure_investment = 91955760.7762
        outputs['investment_costs'] = support_structure_investment + infield_cable_investment + other_investment  # TODO Apply management percentage also to electrical and support structure costs.
        # print support_structure_investment ,infield_cable_investment ,other_investment, outputs['decommissioning_costs']
