from openmdao.api import ExplicitComponent


class AbstractWakeAddedTurbulence(ExplicitComponent):

    def setup(self):
        self.add_input('TI_amb', val=0.08)
        self.add_input('ct', val=0.79)
        self.add_input('u_inf', val=8.5)
        self.add_input('d', val=640.0)

        self.add_output('TI_eff', val=0.25)

    def compute(self, inputs, outputs):
        pass


if __name__ == '__main__':
    from openmdao.api import Problem, Group, IndepVarComp

    class AddedTurbModel1(AbstractWakeAddedTurbulence):

        def compute(self, inputs, outputs):
            TI_amb = inputs['TI_amb']
            ct = inputs['ct']
            u_inf = inputs['u_inf']
            d = inputs['d']

            outputs['TI_eff'] = TI_amb * ct + u_inf / d

    model = Group()
    ivc = IndepVarComp()

    ivc.add_output('TI_amb', 0.12)
    ivc.add_output('ct', 0.6)
    ivc.add_output('u_inf', 8.0)
    ivc.add_output('d', 460.0)

    model.add_subsystem('indep', ivc)
    model.add_subsystem('added1', AddedTurbModel1())

    model.connect('indep.TI_amb', 'added1.TI_amb')
    model.connect('indep.ct', 'added1.ct')
    model.connect('indep.u_inf', 'added1.u_inf')
    model.connect('indep.d', 'added1.d')

    prob = Problem(model)
    prob.setup()
    prob.run_model()
    print(prob['added1.TI_eff'])
