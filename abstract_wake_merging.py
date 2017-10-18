from openmdao.api import ExplicitComponent


class AbstractWakeMerging(ExplicitComponent):
        
    def __init__(self, n_turbines):
        super(AbstractWakeMerging, self).__init__()
        self.n_turbines = n_turbines

    def setup(self):
        self.add_input('all_du', shape=self.n_turbines)

        self.add_output('u', val=6.0)

    def compute(self, inputs, outputs):
        pass

if __name__ == '__main__':
    from openmdao.api import Problem, Group, IndepVarComp
    from numpy import sqrt

    class RSSMerge(AbstractWakeMerging):

        def compute(self, inputs, outputs):
            all_du = inputs['all_du']
            add = 0.0
            for du in all_du:
                add += du ** 2.0
            root = sqrt(add)

            outputs['u'] = root

    model = Group()
    ivc = IndepVarComp()

    ivc.add_output('deficits', [0.16, 0.14, 0.15, 0.18])

    model.add_subsystem('indep', ivc)
    model.add_subsystem('rms', RSSMerge(4))

    model.connect('indep.deficits', 'rms.all_du')

    prob = Problem(model)
    prob.setup()
    prob.run_model()
    print(prob['rms.u'])
