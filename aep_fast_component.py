from os import path
import sys
from openmdao.api import ExplicitComponent
from input_params import max_n_turbines

sys.path.append(path.abspath('C:\Users\Sebastian\PycharmProjects\WINDOW_dev'))
sys.path.append(path.abspath('C:\Users\Sebastian\PycharmProjects\WINDOW_openMDAO\example'))
from call_workflow_once import call_aep


class AEPFast(ExplicitComponent):
    def setup(self):
        self.add_input("layout", shape=(max_n_turbines, 2))
        self.add_output("AEP", val=0.0)
        self.add_output("max_TI", shape=max_n_turbines)

    def compute(self, inputs, outputs):
        outputs['AEP'], outputs['max_TI'] = fun_aep_fast(inputs['layout'])


def fun_aep_fast(layout):
    a=1
    c=2
    d=0
    e=0
    f=4
    j=0
    return call_aep(layout, 15, 10.0, a, c, d, e, f, j)
