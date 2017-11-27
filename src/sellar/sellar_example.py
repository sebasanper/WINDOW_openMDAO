import numpy as np
from openmdao.api import Problem, Group, IndepVarComp, ExecComp, NonlinearBlockGS, ExplicitComponent


class SellarDis1(ExplicitComponent):

    def setup(self):

        # Global Design Variable
        self.add_input('z', val=np.zeros(2))

        # Local Design Variable
        self.add_input('x', val=0.)

        # Coupling parameter
        self.add_input('y2', val=-4.0)

        # Coupling output
        self.add_output('y1', val=4.0)

        # Finite difference all partials.
        #self.declare_partals('*', '*', method='fd')

    def compute(self, inputs, outputs):

        z1 = inputs['z'][0]
        z2 = inputs['z'][1]
        x1 = inputs['x']
        y2 = inputs['y2']

        outputs['y1'] = z1**2 + z2 + x1 - 0.2*y2


class SellarDis2(ExplicitComponent):

    def setup(self):
        # Global Design Variable
        self.add_input('z', val=np.zeros(2))

        # Coupling parameter
        self.add_input('y1', val=4.0)

        # Coupling output
        self.add_output('y2', val=-4.0)

        # Finite difference all partials.
        #self.declare_partals('*', '*', method='fd')

    def compute(self, inputs, outputs):

        z1 = inputs['z'][0]
        z2 = inputs['z'][1]
        y1 = inputs['y1']

        # Note: this may cause some issues. However, y1 is constrained to be
        # above 3.16, so lets just let it converge, and the optimizer will
        # throw it out
        if y1.real < 0.0:
            y1 *= -1

        outputs['y2'] = y1**.5 + z1 + z2


class SellarMDA(Group):

    def setup(self):
        indeps = self.add_subsystem('indeps', IndepVarComp(), promotes=['*'])
        indeps.add_output('x', 1.0)
        indeps.add_output('z', np.array([5.0, 2.0]))

        cycle = self.add_subsystem('cycle', Group(), promotes=['*'])
        cycle.add_subsystem('d1', SellarDis1(), promotes_inputs=['x', 'z', 'y2'], promotes_outputs=['y1'])
        cycle.add_subsystem('d2', SellarDis2(), promotes_inputs=['z', 'y1'], promotes_outputs=['y2'])

        # Nonlinear Block Gauss Seidel is a gradient free solver
        cycle.nonlinear_solver = NonlinearBlockGS()


prob = Problem()

prob.model = SellarMDA()

prob.setup()
prob['x'] = 2.
prob['z'] = [-1., -1.]

prob.run_model()
print(prob['y1'][0], prob['y2'][0])
