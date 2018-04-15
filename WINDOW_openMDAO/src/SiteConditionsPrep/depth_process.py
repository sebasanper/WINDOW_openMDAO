from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import max_n_turbines
import numpy as np


class AbstractWaterDepth(ExplicitComponent):
    def __init__(self, n_turbines, bathymetry_path):
        super(AbstractWaterDepth, self).__init__()
        self.n_turbines = n_turbines
        self.bathymetry_path = bathymetry_path

    def setup(self):
        self.add_input('layout', shape=(self.n_turbines, 3))

        self.add_output('water_depths', shape=max_n_turbines)
        #self.declare_partals(of='water_depths', wrt='layout', method='fd')

    def compute(self, inputs, outputs):
        layout = inputs['layout']

        ans = np.array(self.depth_model(layout[:self.n_turbines]))
        dif = max_n_turbines - len(ans)
        if dif > 0:
            ans = np.append(ans, [0 for _ in range(dif)])
        ans = ans.reshape(max_n_turbines)
        outputs['water_depths'] = ans

    def depth_model(self, layout):
        pass
