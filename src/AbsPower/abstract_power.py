from openmdao.api import ExplicitComponent
from input_params import max_n_turbines
import numpy as np


class AbstractPower2(ExplicitComponent):
    def __init__(self, n_cases):
        super(AbstractPower, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        self.add_input('U', shape=(self.n_cases, max_n_turbines))
        self.add_input('n_turbines', val=1)

        self.add_output('p', shape=(self.n_cases, max_n_turbines))

        # Finite difference all partials.
        # #self.declare_partals('*', '*', method='fd')

    def compute(self, inputs, outputs):
        ans = np.array([])
        for case in range(self.n_cases):
            n_turbines = int(inputs['n_turbines'])
            u = inputs['U'][case][:n_turbines]
            p = np.array([])
            for u0 in u:
                power = self.power_model(u0)
                p = np.append(p, [power])
            lendif = max_n_turbines - len(p)
            if lendif > 0:
                p = np.concatenate((p, [0 for _ in range(lendif)]))
            ans = np.append(ans, p)
        ans = ans.reshape(self.n_cases, max_n_turbines)
        outputs['p'] = ans


class FarmAeroPower(ExplicitComponent):
    def __init__(self, n_cases):
        super(FarmAeroPower, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        self.add_input('ind_powers', shape=(self.n_cases, max_n_turbines))
        self.add_input('n_turbines', val=1)

        self.add_output('farm_power', shape=self.n_cases)
        # Finite difference all partials.
        #self.declare_partals(of='farm_power', wrt=['ind_powers', 'n_turbines'], method='fd')

    def compute(self, inputs, outputs):
        n_turbines = int(inputs['n_turbines'])
        ans = np.array([])
        for case in range(self.n_cases):
            farm_output = sum(inputs['ind_powers'][case][:n_turbines])  # Alternative without using n_turbines.
            ans = np.append(ans, farm_output)
        ans = ans.reshape(self.n_cases)
        outputs['farm_power'] = ans


if __name__ == '__main__':
    from openmdao.api import Problem, Group, IndepVarComp, ExecComp

    class PowerFidelity1(AbstractPower):

        def compute(self, inputs, outputs):

            outputs['p'] = inputs['u'] ** 3.0

    model = Group()
    ivc = IndepVarComp()
    ivc.add_output('u', 7.0)
    model.add_subsystem('indep', ivc)
    model.add_subsystem('pow', PowerFidelity1())
    model.add_subsystem('equal', ExecComp('y=x+1'))

    model.connect('indep.u', 'pow.u')
    model.connect('pow.p', 'equal.x')

    prob = Problem(model)
    prob.setup()
    prob.run_model()
    print(prob['equal.y'])
