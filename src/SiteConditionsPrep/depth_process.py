from openmdao.api import ExplicitComponent
from input_params import max_n_turbines


class AbstractWaterDepth(ExplicitComponent):

    def setup(self):
        self.add_input('layout', shape=(max_n_turbines, 3))
        self.add_input('n_turbines', val=0)

        self.add_output('water_depths', shape=max_n_turbines)

    def compute(self, inputs, outputs):
        n_turbines = int(inputs['n_turbines'])
        layout = inputs['layout']

        outputs['water_depths'] = self.depth_model(layout[:n_turbines])

    def depth_model(self, layout):
        pass
