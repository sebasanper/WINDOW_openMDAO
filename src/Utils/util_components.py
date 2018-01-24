from openmdao.api import ExplicitComponent
from input_params import max_n_turbines


class NumberLayout(ExplicitComponent):
    def setup(self):
        self.add_input("orig_layout", shape=(max_n_turbines, 2))
        self.add_output("number_layout", shape=(max_n_turbines, 3))

    def compute(self, inputs, outputs):
        orig_layout = inputs["orig_layout"]
        outputs["number_layout"] = [[n, orig_layout[n][0], orig_layout[n][1]] for n in range(len(orig_layout))]
