from openmdao.api import ExplicitComponent, Group
from input_params import max_n_turbines
from numpy import sqrt

class AbstractWakeMerging(ExplicitComponent):
        
    def __init__(self, max_n_turbines):
        super(AbstractWakeMerging, self).__init__()
        self.max_n_turbines = max_n_turbines

    def setup(self):
        self.add_input('all_du', shape=self.max_n_turbines)

        self.add_output('u', val=6.0)

    def compute(self, inputs, outputs):
        pass


class SumSquares(ExplicitComponent):
    def setup(self):
        self.add_input('all_deficits', shape=max_n_turbines - 1)
        self.add_input('n_turbines', val=5)
        self.add_output('sos')

    def compute(self, inputs, outputs):
        print "6 SumSquares"
        n_turbines = int(inputs['n_turbines'])
        defs = inputs['all_deficits'][:n_turbines]
        print defs, "Input deficits"
        summation = 0.0
        for item in defs:
            summation += item ** 2.0
        outputs['sos'] = summation
        print outputs['sos'], "Output Sum of Squares"


class Sqrt(ExplicitComponent):

    def setup(self):
        self.add_input('summation')
        self.add_output('sqrt')

    def compute(self, inputs, outputs):
        print "7 Sqrt"
        print inputs['summation'], "Input Sum"
        outputs['sqrt'] = sqrt(inputs['summation'])
        print outputs['sqrt'], "Output Sqrt"


class WakeMergeRSS(Group):
    def setup(self):
        self.add_subsystem('sum', SumSquares(), promotes_inputs=['all_deficits', 'n_turbines'])
        self.add_subsystem('sqrt', Sqrt(), promotes_outputs=['sqrt'])
        self.connect('sum.sos', 'sqrt.summation')

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
