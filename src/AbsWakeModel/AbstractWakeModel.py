from openmdao.api import ExplicitComponent
from input_params import max_n_turbines
import numpy as np


class DetermineIfInWake(ExplicitComponent):
    def __init__(self, artificial_angle, number, n_cases):
        super(DetermineIfInWake, self).__init__()
        self.number = number
        self.n_cases = n_cases
        self.artificial_angle = artificial_angle

    def setup(self):
        self.add_input('ordered', shape=(int(360.0 / self.artificial_angle), max_n_turbines, 3))
        self.add_input('angle', shape=self.n_cases)
        self.add_input('n_turbines', val=1)
        self.add_input('downwind_d', shape=(self.n_cases, max_n_turbines - 1))
        self.add_input('crosswind_d', shape=(self.n_cases, max_n_turbines - 1))
        self.add_input('r', val=40.0)

        self.add_output('fractions', shape=(self.n_cases, max_n_turbines - 1), val=0)

    def compute(self, inputs, outputs):
        # print "4 Determine"
        # print inputs['ordered'], "Input"
        fractions = np.array([])
        n_turbines = int(inputs['n_turbines'])
        for case in range(self.n_cases):
            angle = inputs['angle'][case]
            if case % (self.n_cases / int(360.0 / self.artificial_angle)) == 0:
                # print case, angle, int(360.0 / self.artificial_angle)
                ordered = inputs['ordered'][int(case / (360.0 / self.artificial_angle))]
            downwind_d = inputs['downwind_d'][case]
            crosswind_d = inputs['crosswind_d'][case]
            fractions1 = np.array([])
            r = inputs['r']
            i = 0
            if self.number < n_turbines:
                for n in range(n_turbines):
                    if n != self.number:
                        fractions1 = np.append(fractions1, self.wake_fraction(inputs, x_upstream=ordered[self.number][1],
                                                                            y_upstream=ordered[self.number][2],
                                                                            x_downstream=ordered[n][1],
                                                                            y_downstream=ordered[n][2],
                                                                            wind_direction=angle,
                                                                            downwind_d=downwind_d[i],
                                                                            crosswind_d=crosswind_d[i],
                                                                            radius=r))
                        i += 1
            lendif = max_n_turbines - len(fractions1) - 1
            fractions1 = np.concatenate((fractions1, [0 for _ in range(lendif)]))
            fractions = np.append(fractions, fractions1)
        fractions = fractions.reshape(self.n_cases, max_n_turbines - 1)
        outputs['fractions'] = fractions
        # print outputs['fraction'], "Output"


class WakeDeficit(ExplicitComponent):
    def __init__(self, n_cases):
        super(WakeDeficit, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        self.add_input('r', val=40.0)
        self.add_input('downwind_d', shape=(self.n_cases, max_n_turbines - 1))
        self.add_input('crosswind_d', shape=(self.n_cases, max_n_turbines - 1))
        self.add_input('ct', shape=(self.n_cases, max_n_turbines - 1))
        self.add_input('fractions', shape=(self.n_cases, max_n_turbines - 1))
        self.add_input('n_turbines', val=1)
        self.add_output('dU', shape=(self.n_cases, max_n_turbines - 1))

    def compute(self, inputs, outputs):
        # print "5 WakeDeficit"
        du = np.array([])
        for case in range(self.n_cases):
            n_turbines = int(inputs['n_turbines'])
            r = inputs['r']
            d_down = inputs['downwind_d'][case]
            d_cross = inputs['crosswind_d'][case]
            c_t = inputs['ct'][case]
            fraction = inputs['fractions'][case]
            # print c_t, "Input1 ct"
            # print fraction, "Input2 fraction"
            deficits = np.array([])
            for ind in range(n_turbines - 1):
                if fraction[ind] > 0.0:
                    deficits = np.append(deficits, [fraction[ind] * self.wake_deficit(inputs, x_down=d_down[ind],
                                                                                      x_cross=d_cross[ind], Ct=c_t[ind],
                                                                                      r0=r)])
                else:
                    deficits = np.append(deficits, [0.0])
            lendif = max_n_turbines - len(deficits) - 1
            deficits = np.concatenate((deficits, [0 for _ in range(lendif)]))
            du = np.append(du, deficits)
        du = du.reshape(self.n_cases, max_n_turbines - 1)
        outputs['dU'] = du
        # print outputs['dU'], "Output"
