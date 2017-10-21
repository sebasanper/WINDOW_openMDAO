from abstract_power import AbstractPower
from openmdao.api import Problem, Group, IndepVarComp, ExecComp


class PowerFidelity1(AbstractPower):

    def compute(self, inputs, outputs):

        outputs['p'] = inputs['u'] ** 3.0

if __name__ == '__main__':
    n_cases = 4

    model = Group()
    ivc = IndepVarComp()

    for n in range(1, n_cases + 1):
        ivc.add_output('u{}'.format(n), n + 3)

    ivc.add_output('n_cases', n_cases)

    model.add_subsystem('indep', ivc)

    for n in range(1, n_cases + 1):
        model.add_subsystem('pow{}'.format(n), PowerFidelity1())

    model.add_subsystem('average', ExecComp('y=(x1+x2+x3+x4)/{}'.format(n_cases)))

    for n in range(1, n_cases + 1):
        model.connect('indep.u{}'.format(n), 'pow{}.u'.format(n))

    for n in range(1, n_cases + 1):
        model.connect('pow{}.p'.format(n), 'average.x{}'.format(n))

    prob = Problem(model)
    prob.setup()
    prob.run_model()
    print(prob['average.y'])
