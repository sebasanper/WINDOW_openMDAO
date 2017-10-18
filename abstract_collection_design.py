from openmdao.api import ExplicitComponent


class AbstractCollectionDesign(ExplicitComponent):

    def __init__(self, n_substations, n_turbines):
        super(AbstractCollectionDesign, self).__init__()
        self.n_substations = n_substations
        self.n_turbines = n_turbines

    def setup(self):
        self.add_input('layout', shape=(self.n_turbines, 3))
        self.add_input('n_turbines_p_cable', val=7)
        self.add_input('substation_coordinates', shape=(self.n_substations, 2))

        self.add_output('topology', val=56000000.0)
        self.add_output('cost_collection', val=84000000.0)

    def compute(self, inputs, outputs):
        pass


if __name__ == '__main__':
    from openmdao.api import Problem, Group, IndepVarComp

    class TopologyOptimiser(AbstractCollectionDesign):

        def compute(self, inputs, outputs):
            aep = inputs['AEP']
            outputs['annual_cost_O&M'] = aep / 1000.0 * 16.0
            outputs['availability'] = 0.94 + aep / 100000000000.0

    model = Group()
    ivc = IndepVarComp()

    ivc.add_output('AEP', 698000457.0)
    ivc.add_output('distance_shore', 23000)
    ivc.add_output('layout', [[0, 6, 5], [1, 4, 7]])

    model.add_subsystem('indep', ivc)
    model.add_subsystem('OandMbasic', OandMBasicModel(2))

    model.connect('indep.AEP', 'OandMbasic.AEP')
    model.connect('indep.distance_shore', 'OandMbasic.distance_shore')
    model.connect('indep.layout', 'OandMbasic.layout')

    prob = Problem(model)
    prob.setup()
    prob.run_model()
    print(prob['OandMbasic.annual_cost_O&M'])
    print(prob['OandMbasic.availability'])
