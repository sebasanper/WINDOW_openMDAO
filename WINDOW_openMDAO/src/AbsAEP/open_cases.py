from openmdao.api import ExplicitComponent


class OpenCases(ExplicitComponent):
    def __init__(self, n_cases):
        super(OpenCases, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        self.add_input('cases', shape=(self.n_cases, 2))

        self.add_output('freestream_wind_speeds', shape=self.n_cases)
        self.add_output('wind_directions', shape=self.n_cases)

    def compute(self, inputs, outputs):
        outputs['wind_directions'] = inputs['cases'][:, 0]
        outputs['freestream_wind_speeds'] = inputs['cases'][:, 1]
