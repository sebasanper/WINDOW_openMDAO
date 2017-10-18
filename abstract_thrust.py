from openmdao.api import ExplicitComponent


class AbstractThrust(ExplicitComponent):

    def setup(self):
        self.add_input('u', val=8.0)

        self.add_output('Ct', val=0.79)

    def compute(self, inputs, outputs):
        pass

if __name__ == '__main__':
    from openmdao.api import Problem, Group, IndepVarComp

    class ThrustFidelity1(AbstractThrust):

        def compute(self, inputs, outputs):

            outputs['Ct'] = inputs['u'] + 3.0

    model = Group()
    ivc = IndepVarComp()
    ivc.add_output('u', 7.0)
    model.add_subsystem('indep', ivc)
    model.add_subsystem('thrust', ThrustFidelity1())

    model.connect('indep.u', 'thrust.u')

    prob = Problem(model)
    prob.setup()
    prob.run_model()
    print(prob['thrust.Ct'])
