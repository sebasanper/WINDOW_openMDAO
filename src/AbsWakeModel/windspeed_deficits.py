from openmdao.api import ExplicitComponent
import numpy as np
from input_params import max_n_turbines


class SpeedDeficits(ExplicitComponent):
    def __init__(self, n_cases):
        super(SpeedDeficits, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        self.add_input('dU', shape=self.n_cases)
        self.add_input('freestream', shape=self.n_cases)
        self.add_output('U', shape=self.n_cases)

    def compute(self, inputs, outputs):
        # print "8 Speed"
        ans = np.array([])
        for case in range(self.n_cases):
            dU = inputs['dU'][case]
            freestream = inputs['freestream'][case]
        # print dU, 'Input dU'
            res = [freestream * (1.0 - dU)]
            ans = np.append(ans, res)
        ans = ans.reshape(self.n_cases)
        # print ans
        # inputs['dU'] = []
        outputs['U'] = ans
        # print outputs['U'], "Output U"


class CombineSpeed(ExplicitComponent):
    def __init__(self, n_cases):
        super(CombineSpeed, self).__init__()
        self.n_cases = n_cases

    def setup(self):

        for n in range(max_n_turbines):
            self.add_input('power{}'.format(n), shape=self.n_cases)
        self.add_input('ordered_layout', shape=(self.n_cases, max_n_turbines, 3))
        self.add_input('n_turbines', val=1)

        self.add_output('p', shape=(self.n_cases, max_n_turbines))

    def compute(self, inputs, outputs):
        ans = np.array([])
        n_turbines = int(inputs['n_turbines'])
        for case in range(self.n_cases):
            ordered_layout = inputs['ordered_layout'][case][:n_turbines].tolist()
            # print ordered_layout
            indices = [i[0] for i in ordered_layout]
            # print indices
            # print inputs['U0'], inputs['U1'], inputs['U2']
            final = [[indices[n], inputs['power{}'.format(int(n))][case]] for n in range(len(indices))]
            # print final
            array_speeds = [speed[1] for speed in sorted(final)]
            # print array_speeds
            lendif = max_n_turbines - len(array_speeds)
            if lendif > 0:
                array_speeds = np.concatenate((array_speeds, [0 for _ in range(lendif)]))
            ans = np.append(ans, array_speeds)
        ans = ans.reshape(self.n_cases, max_n_turbines)
        # for n in range(self.n_cases):
        #     inputs['U{}'.format(n)] = []
        outputs['p'] = np.array(ans)
        # print outputs['U'], "Combined Wind Speeds U"
