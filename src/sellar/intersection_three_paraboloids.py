import numpy as np
from openmdao.api import Problem, Group, IndepVarComp, ExecComp, ExplicitComponent, view_model, NewtonSolver, DirectSolver, NonlinearBlockGS


class Plane1(ExplicitComponent):

    def setup(self):

        # Global Design Variable
        self.add_input('z', val=4.0)

        # Local Design Variable
        self.add_input('x', val=1.1)

        # Coupling output
        self.add_output('y', val=0.0)

        # Finite difference all partials.
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):

        z = inputs['z']
        x = inputs['x']

        outputs['y'] = 3.0 * x ** 2.0 + 2.0 * z ** 2.0 - 9.0


class Plane2(ExplicitComponent):

    def setup(self):
        # Global Design Variable
        self.add_input('z', val=1.5)

        # Coupling parameter
        self.add_input('y', val=1.0)

        # Coupling output
        self.add_output('x', val=1.0)

        # Finite difference all partials.
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):

        z = inputs['z'][0]
        y = inputs['y']

        outputs['x'] = - 6.0 * y ** 2.0 + 1.5 * z ** 2.0 + 5.0


class Plane3(ExplicitComponent):

    def setup(self):
        # Global Design Variable
        self.add_output('z', val=10.3)

        # Coupling parameter
        self.add_input('y', val=15.0)

        # Coupling output
        self.add_input('x', val=-18.0)

        # Finite difference all partials.
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):

        x = inputs['x']
        y = inputs['y']

        outputs['z'] = x ** 2.0 + y ** 2.0


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


prob = Problem()

prob.model = PlanesIntersection()
a = prob.model.nonlinear_solver = NewtonSolver()
a = prob.model.linear_solver = DirectSolver()

a.options['maxiter'] = 10

prob.setup()
# view_model(prob)

prob.run_model()
print(prob['p1.y'], prob['p1.x'], prob['p1.z'])
