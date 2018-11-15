from builtins import range
from openmdao.api import ExplicitComponent
import numpy as np
from WINDOW_openMDAO.input_params import max_n_turbines


class SpeedDeficits(ExplicitComponent):
    def __init__(self, n_cases):
        super(SpeedDeficits, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        self.add_input('dU', shape=self.n_cases)
        self.add_input('freestream', shape=self.n_cases)
        self.add_output('U', shape=self.n_cases)

        #self.declare_partals(of='U', wrt=['dU', 'freestream'], method='fd')

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


class CombineOutputs(ExplicitComponent):
    def __init__(self, n_cases):
        super(CombineOutputs, self).__init__()
        self.n_cases = n_cases

    def setup(self):

        for n in range(max_n_turbines + 1):
            self.add_input('power{}'.format(n), shape=(self.n_cases, max_n_turbines))
            self.add_input('ct{}'.format(n), shape=(self.n_cases, max_n_turbines))

            #self.declare_partals(of=['p', 'ct'], wrt=['power{}'.format(n), 'ct{}'.format(n)], method='fd')
            
        self.add_input('ordered_layout', shape=(self.n_cases, max_n_turbines, 3))
        self.add_input('n_turbines', val=1)

        self.add_output('p', shape=(self.n_cases, max_n_turbines))
        self.add_output('ct', shape=(self.n_cases, max_n_turbines))

        #self.declare_partals(of=['p', 'ct'], wrt=['ordered_layout', 'n_turbines'], method='fd')

    def compute(self, inputs, outputs):
        ans = np.array([])
        ans_ct = np.array([])
        n_turbines = int(inputs['n_turbines'])
        for case in range(self.n_cases):
            # print inputs['power0'], inputs['power1'], inputs['power2'], inputs['power3']
            power_in = inputs['power{}'.format(n_turbines)][case]
            ct_in = inputs['ct{}'.format(n_turbines)][case]
            ordered_layout = inputs['ordered_layout'][case][:n_turbines].tolist()
            # print ordered_layout
            indices = [i[0] for i in ordered_layout]
            # print indices
            # print inputs['U0'], inputs['U1'], inputs['U2']
            final = [[indices[n], power_in[n]] for n in range(len(indices))]
            final_ct = [[indices[n], ct_in[n]] for n in range(len(indices))]
            # print final
            array_power = [power[1] for power in sorted(final)]
            array_ct = [c_t[1] for c_t in sorted(final_ct)]
            # print array_speeds
            lendif = max_n_turbines - len(array_power)
            if lendif > 0:
                array_power = np.concatenate((array_power, [0 for _ in range(lendif)]))
                array_ct = np.concatenate((array_ct, [0 for _ in range(lendif)]))
            ans = np.append(ans, array_power)
            ans_ct = np.append(ans_ct, array_ct)
        ans = ans.reshape(self.n_cases, max_n_turbines)
        ans_ct = ans_ct.reshape(self.n_cases, max_n_turbines)
        # for n in range(self.n_cases):
        #     inputs['U{}'.format(n)] = []
        outputs['p'] = np.array(ans)
        outputs['ct'] = np.array(ans_ct)
        # print outputs['U'], "Combined Wind Speeds U"
