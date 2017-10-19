from openmdao.api import Problem, Group, ExplicitComponent, view_model
from numpy import sqrt

u_far = 8.5


def ct(v):
    if v < 4.0:
        return 0.1
    elif v <= 25.0:
        return 7.3139922126945e-7 * v ** 6.0 - 6.68905596915255e-5 * v ** 5.0 + 2.3937885e-3 * v ** 4.0 - 0.0420283143 * v ** 3.0 + 0.3716111285 * v ** 2.0 - 1.5686969749 * v + 3.2991094727
    else:
        return 0.1


def wake_deficit(x, Ct, k=0.04, r0=40.0):
    if x > 0.0:
        print x, Ct
        return (1.0 - sqrt(1.0 - Ct)) / (1.0 + (k * x) / r0) ** 2.0
    else:
        return 0.0


def speed(deficit):
    return u_far * (1.0 - deficit)


def distance(a, b):
    if a == 0:
        return 0.0
    elif a == 1:
        if b == 0:
            return 560.0
        elif b == 2:
            return 0.0
    elif a == 2:
        if b == 0:
            return 1120.0
        elif b == 1:
            return 560.0


n_turbines = 3


class UnknownWindSpeed(ExplicitComponent):

    def __init__(self, number):
        super(UnknownWindSpeed, self).__init__()
        self.number = number

    def setup(self):

        for n in range(n_turbines):
            if n != self.number:
                self.add_input('U{}'.format(n), val=u_far)

        self.add_output('dU', val=u_far)

        # Finite difference all partials.
        # self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):
        suma = 0.0
        for n in range(n_turbines):
            if n != self.number:
                d = distance(self.number, n)
                if d > 0.0:
                    suma += wake_deficit(d, ct(inputs['U{}'.format(n)])) ** 2.0

        outputs['dU'] = suma


class SqrtRSS(ExplicitComponent):

    def setup(self):
        self.add_input('summation')
        self.add_output('sqrt')

    def compute(self, inputs, outputs):
        outputs['sqrt'] = sqrt(inputs['summation'])


class SpeedDeficits(ExplicitComponent):

    def setup(self):
        self.add_input('dU', val=0.5)
        self.add_output('U', val=8.0)

    def compute(self, inputs, outputs):
        dU = inputs['dU']

        outputs['U'] = u_far * (1.0 - dU)


class TurbineArray(Group):

    def setup(self):
        for n in range(n_turbines):
            self.add_subsystem('comp{}'.format(n), UnknownWindSpeed(n))
            self.add_subsystem('speed{}'.format(n), SpeedDeficits())
            self.add_subsystem('sqrt{}'.format(n), SqrtRSS())
            self.connect('comp{}.dU'.format(n), 'sqrt{}.summation'.format(n))
            self.connect('sqrt{}.sqrt'.format(n), 'speed{}.dU'.format(n), )
            for m in range(n_turbines):
                if m != n:
                    self.connect('speed{}.U'.format(n), 'comp{}.U{}'.format(m, n))


if __name__ == '__main__':
    from openmdao.api import NonlinearBlockGS
    prob = Problem()

    prob.model = TurbineArray()
    NS = prob.model.nonlinear_solver = NonlinearBlockGS()

    prob.setup()
    # view_model(prob)

    prob.run_model()
    for n in range(n_turbines):
        print(prob['speed{}.U'.format(n)])
