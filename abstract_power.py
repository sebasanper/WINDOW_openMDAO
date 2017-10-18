from openmdao.api import ExplicitComponent


class AbstractPower(ExplicitComponent):

    def setup(self):
        self.add_input('u', val=8.0)

        self.add_output('p', val=2100000.0)

    def compute(self, inputs, outputs):
        pass

if __name__ == '__main__':
    from openmdao.api import Problem, Group, IndepVarComp

    class PowerFidelity1(AbstractPower):

        def compute(self, inputs, outputs):

            outputs['p'] = inputs['u'] ** 3.0

    model = Group()
    ivc = IndepVarComp()
    ivc.add_output('u', 7.0)
    model.add_subsystem('indep', ivc)
    model.add_subsystem('pow', PowerFidelity1())

    model.connect('indep.u', 'pow.u')

    prob = Problem(model)
    prob.setup()
    prob.run_model()
    print(prob['pow.p'])
