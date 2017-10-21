from openmdao.api import ExplicitComponent
import numpy as np
from input_params import max_n_turbines, u_far


class AbstractThrust(ExplicitComponent):

    def setup(self):
        self.add_input('u', val=8.0)

        self.add_output('Ct', val=0.79)

    def compute(self, inputs, outputs):
        pass


class ThrustCoefficient(ExplicitComponent):

    def __init__(self, number):
        super(ThrustCoefficient, self).__init__()
        self.number = number

    def setup(self):
        self.add_input('n_turbines', val=5)
        for n in range(max_n_turbines):
            if n != self.number:
                self.add_input('U{}'.format(n), val=u_far)

        self.add_output('ct', shape=max_n_turbines - 1, val=0.79)

        # Finite difference all partials.
        # self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):
        n_turbines = int(inputs['n_turbines'])
        c_t = np.array([])
        for n in range(max_n_turbines-2):
            if n != self.number:
                c_t = np.append(c_t, [ct(inputs['U{}'.format(n)])])
        lendif = max_n_turbines - n_turbines
        outputs['ct'] = np.concatenate((c_t, [float('nan') for n in range(lendif)]))


def ct(v):
    if v == v:
        if v < 4.0:
            ans = np.array([0.1])
        elif v <= 25.0:
            val = 7.3139922126945e-7 * v ** 6.0 - 6.68905596915255e-5 * v ** 5.0 + 2.3937885e-3 * v ** 4.0 - 0.0420283143 * v ** 3.0 + 0.3716111285 * v ** 2.0 - 1.5686969749 * v + 3.2991094727
            ans = np.array([val])
        else:
            ans = np.array([0.1])
    else:
        ans = float('nan')
    return ans

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