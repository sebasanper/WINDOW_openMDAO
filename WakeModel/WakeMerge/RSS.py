from openmdao.api import ExplicitComponent, Group
from input_params import max_n_turbines
from numpy import sqrt
import numpy as np
from src.api import BaseWakeMerge


class SumSquares(ExplicitComponent):
    def __init__(self, n_cases):
        super(SumSquares, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        self.add_input('all_deficits', shape=(self.n_cases, max_n_turbines - 1))
        self.add_input('n_turbines', val=5)
        self.add_output('sos', shape=self.n_cases)

    def compute(self, inputs, outputs):
        # print "6 SumSquares"
        sos = np.array([])
        for case in range(self.n_cases):
            n_turbines = int(inputs['n_turbines'])
            defs = inputs['all_deficits'][case][:n_turbines]
            # print defs, "Input deficits"
            summation = 0.0
            for item in defs:
                summation += item ** 2.0
            sos = np.append(sos, summation)
        outputs['sos'] = sos
        # print outputs['sos'], "Output Sum of Squares"


class Sqrt(ExplicitComponent):
    def __init__(self, n_cases):
        super(ExplicitComponent, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        self.add_input('summation', shape=self.n_cases)
        self.add_output('sqrt', shape=self.n_cases)

    def compute(self, inputs, outputs):
        # print "7 Sqrt"
        # print inputs['summation'], "Input Sum"
        outputs['sqrt'] = sqrt(inputs['summation'])
        # print outputs['sqrt'], "Output Sqrt"


class WakeMergeRSS(Group):
    def __init__(self, n_cases):
        super(WakeMergeRSS, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        self.add_subsystem('sum', SumSquares(self.n_cases), promotes_inputs=['all_deficits', 'n_turbines'])
        self.add_subsystem('sqrt', Sqrt(self.n_cases), promotes_outputs=['sqrt'])
        self.connect('sum.sos', 'sqrt.summation')


if __name__ == '__main__':
    from openmdao.api import Problem, Group, IndepVarComp
    from numpy import sqrt

    model = Group()
    ivc = IndepVarComp()

    ivc.add_output('deficits', [0.16, 0.14, 0.15, 0.18])

    model.add_subsystem('indep', ivc)
    model.add_subsystem('rms', WakeMergeRSS(4))

    model.connect('indep.deficits', 'rms.all_du')

    prob = Problem(model)
    prob.setup()
    prob.run_model()
    print(prob['rms.u'])
