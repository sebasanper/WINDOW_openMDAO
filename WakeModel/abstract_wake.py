from openmdao.api import ExplicitComponent


class AbstractWakeDeficit(ExplicitComponent):

    def setup(self):
        self.add_input('up_u', val=8.0)
        self.add_input('up_ct', val=0.79)
        self.add_input('down_d', val=640.0)
        self.add_input('cross_d', val=400.0)
        self.add_input('TI', val=0.08)
        self.add_input('r', val=80.0)

        self.add_output('down_du', val=6.0)

    def compute(self, inputs, outputs):
        pass


if __name__ == '__main__':
    from openmdao.api import Problem, Group, IndepVarComp

    class JensenWake(AbstractWakeDeficit):

        def compute(self, inputs, outputs):
            u = inputs['up_u']
            ct = inputs['up_ct']
            down_d = inputs['down_d']
            cross_d = inputs['cross_d']
            TI = inputs['TI']
            r = inputs['r']

            outputs['down_du'] = u * ct * TI + cross_d + down_d + r

    model = Group()
    ivc = IndepVarComp()

    ivc.add_output('up_u', 6.5)
    ivc.add_output('up_ct', 0.6)
    ivc.add_output('cross_d', 475.0)
    ivc.add_output('down_d', 200.0)
    ivc.add_output('TI', 0.08)
    ivc.add_output('r', 100.0)

    model.add_subsystem('indep', ivc)
    model.add_subsystem('jensen', JensenWake())

    model.connect('indep.up_u', 'jensen.up_u')
    model.connect('indep.up_ct', 'jensen.up_ct')
    model.connect('indep.cross_d', 'jensen.cross_d')
    model.connect('indep.down_d', 'jensen.down_d')
    model.connect('indep.TI', 'jensen.TI')
    model.connect('indep.r', 'jensen.r')

    prob = Problem(model)
    prob.setup()
    prob.run_model()
    print(prob['jensen.down_du'])
