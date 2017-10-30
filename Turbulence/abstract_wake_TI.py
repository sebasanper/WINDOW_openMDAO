from openmdao.api import ExplicitComponent
from input_params import max_n_turbines
import numpy as np
from numpy import sqrt


class AbstractWakeAddedTurbulence(ExplicitComponent):
    def __init__(self, n_cases):
        super(AbstractWakeAddedTurbulence, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        self.add_input('ordered', shape=(self.n_cases, max_n_turbines, 3))
        self.add_input('TI_amb', shape=self.n_cases)
        self.add_input('ct', shape=(self.n_cases, max_n_turbines, max_n_turbines))
        self.add_input('dU_matrix', shape=(self.n_cases, max_n_turbines, max_n_turbines))
        self.add_input('freestream', shape=self.n_cases)
        self.add_input('n_turbines', val=0)

        self.add_output('TI_eff', shape=(self.n_cases, max_n_turbines))

    def compute(self, inputs, outputs):
        TI_eff = np.array([])
        n_turbines = int(inputs['n_turbines'])
        # print ct
        for case in range(self.n_cases):
            ordered = inputs['ordered'][case][:n_turbines]
            TI_amb_case = inputs['TI_amb'][case]
            freestream_case = inputs['freestream'][case]
            TI_case = np.array([])
            for n in range(n_turbines):
                rowct = inputs['ct'][case][n]
                row = inputs['dU_matrix'][case][n]
                max_index = np.argmax(row)
                ct_case_closest = rowct[max_index]
                distance_closest = self.distance(ordered[n][1], ordered[n][2], ordered[max_index][1], ordered[max_index][2])
                # print n, row, max_index, rowct, ct_case_closest, n, max_index, distance_closest, ordered[n][1], ordered[n][2], ordered[max_index][1], ordered[max_index][2]
                ans = self.TI_model(TI_amb_case, ct_case_closest, freestream_case, distance_closest)
                TI_case = np.append(TI_case, ans)
            lendif = max_n_turbines - len(TI_case)
            if lendif > 0:
                TI_case = np.concatenate((TI_case, [0 for _ in range(lendif)]))
            TI_eff = np.append(TI_eff, TI_case)
        TI_eff = TI_eff.reshape(self.n_cases, max_n_turbines)
        outputs['TI_eff'] = TI_eff

    def distance(self, x1, y1, x2, y2):
        return sqrt((x1 - x2) ** 2.0 + (y1 - y2) ** 2.0)

    def TI_model(self, ambient_turbulence, ct, wind_speed, spacing):
        print ambient_turbulence, ct, wind_speed, spacing
        if ct == 0:
            return ambient_turbulence
        return 0.18


class DeficitMatrix(ExplicitComponent):
    def __init__(self, n_cases):
        super(DeficitMatrix, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        for n in range(max_n_turbines):
            self.add_input('deficits{}'.format(n), shape=(self.n_cases, max_n_turbines - 1))
        self.add_output('dU_matrix', shape=(self.n_cases, max_n_turbines, max_n_turbines))

    def compute(self, inputs, outputs):
        matrix = np.array([])
        for n in range(max_n_turbines):
            row = inputs['deficits{}'.format(n)]
            row = np.insert(row, n, 0)
            matrix = np.append(matrix, row)
        matrix = matrix.reshape(self.n_cases, max_n_turbines, max_n_turbines)
        outputs['dU_matrix'] = matrix


class CtMatrix(ExplicitComponent):
    def __init__(self, n_cases):
        super(CtMatrix, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        for n in range(max_n_turbines):
            self.add_input('ct{}'.format(n), shape=(self.n_cases, max_n_turbines - 1))
        self.add_output('ct_matrix', shape=(self.n_cases, max_n_turbines, max_n_turbines))

    def compute(self, inputs, outputs):
        matrix = np.array([])
        for n in range(max_n_turbines):
            row = inputs['ct{}'.format(n)]
            row = np.insert(row, n, 0)
            matrix = np.append(matrix, row)
        matrix = matrix.reshape(self.n_cases, max_n_turbines, max_n_turbines)
        outputs['ct_matrix'] = matrix


if __name__ == '__main__':
    from openmdao.api import Problem, Group, IndepVarComp

    class AddedTurbModel1(AbstractWakeAddedTurbulence):

        def compute(self, inputs, outputs):
            TI_amb = inputs['TI_amb']
            ct = inputs['ct']
            u_inf = inputs['u_inf']
            d = inputs['d']

            outputs['TI_eff'] = TI_amb * ct + u_inf / d

    model = Group()
    ivc = IndepVarComp()

    ivc.add_output('TI_amb', 0.12)
    ivc.add_output('ct', 0.6)
    ivc.add_output('u_inf', 8.0)
    ivc.add_output('d', 460.0)

    model.add_subsystem('indep', ivc)
    model.add_subsystem('added1', AddedTurbModel1())

    model.connect('indep.TI_amb', 'added1.TI_amb')
    model.connect('indep.ct', 'added1.ct')
    model.connect('indep.u_inf', 'added1.u_inf')
    model.connect('indep.d', 'added1.d')

    prob = Problem(model)
    prob.setup()
    prob.run_model()
    print(prob['added1.TI_eff'])
