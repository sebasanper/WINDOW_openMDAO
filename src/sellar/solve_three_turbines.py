import numpy as np
from openmdao.api import Problem, Group, IndepVarComp, ExecComp, ExplicitComponent, view_model, NewtonSolver, DirectSolver, NonlinearBlockGS
from numpy import sqrt

u_far = 8.5


def ct(U0):
    if U0 < 4.0:
        return 0.1
    elif U0 <= 25.0:
        return 7.3139922126945e-7 * U0 ** 6.0 - 6.68905596915255e-5 * U0 ** 5.0 + 2.3937885e-3 * U0 ** 4.0 + - 0.0420283143 * U0 ** 3.0 + 0.3716111285 * U0 ** 2.0 - 1.5686969749 * U0 + 3.2991094727
    else:
        return 0.1


def wake_deficit(x, Ct, k=0.04, r0=40.0):
    return (1.0 - sqrt(1.0 - Ct)) / (1.0 + (k * x) / r0) ** 2.0


def speed(deficit):
    return u_far * (1.0 - deficit)


class Plane1(ExplicitComponent):

    def setup(self):

        # Global Design Variable
        self.add_input('z', val=6.3)

        # Local Design Variable
        self.add_input('x', val=11.1)

        # Coupling output
        self.add_output('y', val=7.0)

        # Finite difference all partials.
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):

        z = inputs['z']
        x = inputs['x']

        outputs['y'] = u_far


class Plane2(ExplicitComponent):

    def setup(self):
        # Global Design Variable
        self.add_input('z', val=6.3)

        # Coupling parameter
        self.add_input('y', val=7.0)

        # Coupling output
        self.add_output('x', val=6.0)

        # Finite difference all partials.
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):

        z = inputs['z']
        y = inputs['y']

        outputs['x'] = speed(sqrt(wake_deficit(560.0, ct(y)) ** 2.0))


class Plane3(ExplicitComponent):

    def setup(self):
        # Global Design Variable
        self.add_output('z', val=6.3)

        # Coupling parameter
        self.add_input('y', val=5.0)

        # Coupling output
        self.add_input('x', val=8.0)

        # Finite difference all partials.
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):

        x = inputs['x']
        y = inputs['y']

        outputs['z'] = speed(sqrt(wake_deficit(560.0, ct(x)) ** 2.0 + wake_deficit(1120.0, ct(y)) ** 2.0))


class PlanesIntersection(Group):

    def setup(self):
        self.add_subsystem('p3', Plane3())
        self.add_subsystem('p1', Plane1())
        self.add_subsystem('p2', Plane2())

        self.connect('p1.y', 'p2.y')
        self.connect('p1.y', 'p3.y')
        self.connect('p2.x', 'p3.x')
        self.connect('p2.x', 'p1.x')
        self.connect('p3.z', 'p1.z')
        self.connect('p3.z', 'p2.z')
if __name__ == '__main__':

    prob = Problem()

    prob.model = PlanesIntersection()
    a = prob.model.nonlinear_solver = NewtonSolver()
    a = prob.model.linear_solver = DirectSolver()

    a.options['maxiter'] = 10

    prob.setup()
    # view_model(prob)

    prob.run_model()
    print(prob['p1.y'], prob['p1.x'], prob['p1.z'])
