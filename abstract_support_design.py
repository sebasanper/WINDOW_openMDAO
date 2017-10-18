from openmdao.api import ExplicitComponent


class AbstractSupportStructureDesign(ExplicitComponent):

    def setup(self):
        self.add_input('TI', val=0.08)
        self.add_input('depth', val=20.0)
        self.add_output('cost_support', val=5600000.0)

    def compute(self, inputs, outputs):
        pass


if __name__ == '__main__':
    from openmdao.api import Problem, Group, IndepVarComp

    class TeamPlay(AbstractSupportStructureDesign):

        def compute(self, inputs, outputs):
            TI = inputs['TI']
            depth = inputs['depth']
            outputs['cost_support'] = TI * depth ** 3.0

    model = Group()
    ivc = IndepVarComp()

    ivc.add_output('TI', 0.12)
    ivc.add_output('depth', 14.0)

    model.add_subsystem('indep', ivc)
    model.add_subsystem('teamplay', TeamPlay())

    model.connect('indep.TI', 'teamplay.TI')
    model.connect('indep.depth', 'teamplay.depth')

    prob = Problem(model)
    prob.setup()
    prob.run_model()
    print(prob['teamplay.cost_support'])
