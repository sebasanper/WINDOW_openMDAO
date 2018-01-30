from os import path
import sys
from openmdao.api import ExplicitComponent

sys.path.append(path.abspath('../../WINDOW-dev/'))
from call_workflow_once import call_aep


class AEPFast(ExplicitComponent):
	def setup(self):
		self.add_input("layout", shape=3)
		self.add_output("AEP", val=0.0)

	def compute(self, inputs, outputs):
		return fun_aep_fast(layout)

def fun_aep_fast(layout):
    a=1
    c=2
    d=0
    e=0
    f=4
    j=0
    return call_aep(layout, 15, 30.0, a, c, d, e, f, j)