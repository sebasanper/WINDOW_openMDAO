from openmdao.api import ExplicitComponent
from input_params import n_turbines
import numpy as np


class AbstractPower(ExplicitComponent):

    def setup(self):
        self.add_input('U', shape=n_turbines)

        self.add_output('p', shape=n_turbines)

                # Finite difference all partials.
        self.declare_partials('*', '*', method='fd')


    def compute(self, inputs, outputs):
        pass


class PowerPolynomial(AbstractPower):
    def compute(self, inputs, outputs):
        u = inputs['U']
        p = np.array([])
        for u0 in u:
            if u0 < 4.0:
                pow = 0.0
            elif u0 <= 10.0:
                pow = (3.234808e-4 * u0 ** 7.0 - 0.0331940121 * u0 ** 6.0 + 1.3883148012 * u0 ** 5.0 - 30.3162345004 * u0 ** 4.0 + 367.6835557011 * u0 ** 3.0 - 2441.6860655008 * u0 ** 2.0 + 8345.6777042343 * u0 - 11352.9366182805) * 1000.0
            elif u0 <= 25.0:
                pow = 2000000.0
            else:
                pow = 0.0
            p = np.append(p, pow)
        outputs['p'] = p


class FarmAeroPower(ExplicitComponent):
    def setup(self):
        self.add_input('ind_powers', shape=n_turbines)
        self.add_input('n_turbines', val=5)

        self.add_output('farm_power', val=0.0)
                # Finite difference all partials.
        self.declare_partials('*', '*', method='cs')


    def compute(self, inputs, outputs):
        outputs['farm_power'] = sum(inputs['ind_powers'] * 2)


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
