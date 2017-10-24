from openmdao.api import ExplicitComponent
from input_params import max_n_turbines
import numpy as np


class DetermineIfInWake(ExplicitComponent):
    def __init__(self, number):
        super(DetermineIfInWake, self).__init__()
        self.number = number

    def setup(self):
        self.add_input('layout', shape=(max_n_turbines, 3))
        self.add_input('angle', val=90.0)
        self.add_input('n_turbines', val=1)
        self.add_input('downwind_d', shape=max_n_turbines - 1)
        self.add_input('crosswind_d', shape=max_n_turbines - 1)
        self.add_input('r', val=40.0)

        self.add_output('fractions', shape=max_n_turbines - 1, val=0)

    def compute(self, inputs, outputs):
        # print "4 Determine"
        # print inputs['layout'], "Input"
        n_turbines = int(inputs['n_turbines'])
        layout = inputs['layout']
        angle = inputs['angle']
        downwind_d = inputs['downwind_d']
        crosswind_d = inputs['crosswind_d']
        fractions = np.array([])
        r = inputs['r']
        i = 0
        if self.number < n_turbines:
            for n in range(n_turbines):
                if n != self.number:
                    fractions = np.append(fractions, self.wake_fraction(inputs, x_upstream=layout[self.number][1],
                                                                        y_upstream=layout[self.number][2],
                                                                        x_downstream=layout[n][1],
                                                                        y_downstream=layout[n][2],
                                                                        wind_direction=angle,
                                                                        downwind_d=downwind_d[i],
                                                                        crosswind_d=crosswind_d[i],
                                                                        radius=r))
                    i += 1
        lendif = max_n_turbines - len(fractions) - 1
        outputs['fractions'] = np.concatenate((fractions, [0 for _ in range(lendif)]))
        # print outputs['fraction'], "Output"


class WakeDeficit(ExplicitComponent):

    def setup(self):
        self.add_input('r', val=40.0)
        self.add_input('downwind_d', shape=max_n_turbines - 1, val=560.0)
        self.add_input('crosswind_d', shape=max_n_turbines - 1, val=0.0)
        self.add_input('ct', shape=max_n_turbines - 1, val=0.79)
        self.add_input('fractions', shape=max_n_turbines - 1)
        self.add_input('n_turbines', val=1)
        self.add_output('dU', shape=max_n_turbines - 1, val=0.3)

    def compute(self, inputs, outputs):
        # print "5 WakeDeficit"
        n_turbines = int(inputs['n_turbines'])
        r = inputs['r']
        d_down = inputs['downwind_d']
        d_cross = inputs['crosswind_d']
        c_t = inputs['ct']
        fraction = inputs['fractions']
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
        outputs['dU'] = np.concatenate((deficits, [0 for _ in range(lendif)]))
        # print outputs['dU'], "Output"
