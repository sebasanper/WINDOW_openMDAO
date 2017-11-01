from openmdao.api import ExplicitComponent
from input_params import max_n_turbines
import numpy as np


class AbstractWaterDepth(ExplicitComponent):

    def setup(self):
        self.add_input('layout', shape=(max_n_turbines, 3))
        self.add_input('n_turbines', val=0)

        self.add_output('water_depths', shape=max_n_turbines)

    def compute(self, inputs, outputs):
        n_turbines = int(inputs['n_turbines'])
        layout = inputs['layout']

        ans = np.array(self.depth_model(layout[:n_turbines]))
        dif = max_n_turbines - len(ans)
        if dif > 0:
            ans = np.append(ans, [0 for _ in range(dif)])
        ans = ans.reshape(max_n_turbines)
        outputs['water_depths'] = ans

    def depth_model(self, layout):
        pass
