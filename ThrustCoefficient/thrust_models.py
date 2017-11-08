import numpy as np
from input_params import max_n_turbines
from src.api import AbstractThrustCoefficient


class ThrustPolynomial(AbstractThrustCoefficient):

    def ct_model(self, u):
        # print u
        if u < 4.0:
            ans = 0.1
        elif u <= 25.0:
            val = 7.3139922126945e-7 * u ** 6.0 - 6.68905596915255e-5 * u ** 5.0 + 2.3937885e-3 * u ** 4.0 - 0.0420283143 * u ** 3.0 + 0.3716111285 * u ** 2.0 - 1.5686969749 * u + 3.2991094727
            ans = val
        else:
            ans = 0.1
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
