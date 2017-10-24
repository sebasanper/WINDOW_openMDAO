from openmdao.api import ExplicitComponent
import numpy as np
from input_params import max_n_turbines


class SpeedDeficits(ExplicitComponent):

    def setup(self):
        self.add_input('dU', val=0.5)
        self.add_input('freestream', val=0.5)
        self.add_output('U', val=2.5)

    def compute(self, inputs, outputs):

        # print "8 Speed"
        dU = inputs['dU']
        freestream = inputs['freestream']
        # print dU, 'Input dU'
        outputs['U'] = np.array(freestream * (1.0 - dU))
        # print outputs['U'], "Output U"


class CombineSpeed(ExplicitComponent):

    def setup(self):

        for n in range(max_n_turbines):
            self.add_input('U{}'.format(n), val=8.5)
        self.add_input('ordered_layout', shape=(max_n_turbines, 3))
        self.add_input('n_turbines', val=1)

        self.add_output('U', shape=max_n_turbines)

    def compute(self, inputs, outputs):
        n_turbines = int(inputs['n_turbines'])
        ordered_layout = inputs['ordered_layout'][:n_turbines].tolist()
        # print ordered_layout
        indices = [i[0] for i in ordered_layout]
        # print indices
        # print inputs['U0'], inputs['U1'], inputs['U2']
        final = [[indices[n], inputs['U{}'.format(int(n))][0]] for n in range(len(indices))]
        # print final
        array_speeds = [speed[1] for speed in sorted(final)]
        # print array_speeds
        lendif = max_n_turbines - len(array_speeds)
        if lendif > 0:
            array_speeds = np.concatenate((array_speeds, [0 for n in range(lendif)]))
        outputs['U'] = np.array(array_speeds)
        # print outputs['U'], "Combined Wind Speeds U"
