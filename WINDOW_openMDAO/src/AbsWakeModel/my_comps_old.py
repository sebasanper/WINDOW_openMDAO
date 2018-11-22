from builtins import range
from openmdao.api import ExplicitComponent

class DetermineIfInWakeJensen(ExplicitComponent):
    def __init__(self, number):
        super(DetermineIfInWakeJensen, self).__init__()
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
                    fractions = np.append(fractions, self.wake_fraction(layout[self.number][1], layout[self.number][2], layout[n][1], layout[n][2], angle, downwind_d[i], crosswind_d[i], r, k))
                    i += 1
        lendif = max_n_turbines - len(fractions) - 1
        outputs['fractions'] = np.concatenate((fractions, [0 for n in range(lendif)]))
        #print outputs['fraction'], "Output"


class WakeDeficit(ExplicitComponent):

    def setup(self):
        self.add_input('r', val=40.0)
        self.add_input('dist_down', shape=max_n_turbines - 1, val=560.0)
        self.add_input('dist_cross', shape=max_n_turbines - 1, val=0.0)
        self.add_input('ct', shape=max_n_turbines - 1, val=0.79)
        self.add_input('fraction', shape=max_n_turbines - 1)
        self.add_input('n_turbines', val=1)
        self.add_output('dU', shape=max_n_turbines - 1, val=0.3)

    def compute(self, inputs, outputs):
        #print "5 WakeDeficit"
        n_turbines = int(inputs['n_turbines'])
        r = inputs['r']
        d_down = inputs['dist_down']
        d_cross = inputs['dist_cross']
        c_t = inputs['ct']
        fraction = inputs['fraction']
        #print c_t, "Input1 ct"
        #print fraction, "Input2 fraction"
        deficits = np.array([])
        for ind in range(n_turbines - 1):
            if fraction[ind] > 0.0:
                deficits = np.append(deficits, [fraction[ind] * self.wake_deficit(d_down[ind], d_cross[ind], c_t[ind], k, r)])
            else:
                deficits = np.append(deficits, [0.0])
        lendif = max_n_turbines - len(deficits) - 1
        outputs['dU'] = np.concatenate((deficits, [0 for n in range(lendif)]))
        #print outputs['dU'], "Output"