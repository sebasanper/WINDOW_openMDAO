from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import max_n_turbines
from numpy import sqrt
import numpy as np


class AbstractWakeMerge(ExplicitComponent):
    def __init__(self, n_cases):
        super(AbstractWakeMerge, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        self.add_input('all_deficits', shape=(self.n_cases, max_n_turbines))
        self.add_input('n_turbines', val=0)
        self.add_output('dU', shape=self.n_cases)

        #self.declare_partals(of='dU', wrt=['all_deficits', 'n_turbines'], method='fd')

    def compute(self, inputs, outputs):
        # print "6 SumSquares"
        ans = np.array([])
        n_turbines = int(inputs['n_turbines'])
        for case in range(self.n_cases):
            defs = inputs['all_deficits'][case][:n_turbines]
            ans = np.append(ans, self.merge_model(defs))
        outputs['dU'] = ans

    def merge_model(self, deficits):
        pass  # To be defined in another subclass of AbstractWakeMerge for specific merging models.


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
