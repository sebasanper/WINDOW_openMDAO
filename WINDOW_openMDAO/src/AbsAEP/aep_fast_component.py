from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import max_n_turbines

from WINDOW_openMDAO.src.AbsAEP.FastAEP.call_aep_workflow_once import call_aep


class AEPFast(ExplicitComponent):

    def __init__(self, artif_angles, nbins, windrose_file, power_curve_file, ct_curve_file):
        super(AEPFast, self).__init__()
        self.artif_angles = artif_angles
        self.nbins = nbins
        self.windrose_file = windrose_file
        self.power_curve_file = power_curve_file
        self.ct_curve_file = ct_curve_file

    def setup(self):
        self.add_input("layout", shape=(max_n_turbines, 2))
        self.add_output("AEP", val=0.0)
        self.add_output("max_TI", shape=max_n_turbines)

    def compute(self, inputs, outputs):
        layout2 = inputs["layout"]
        layout = []
        for t in layout2:
            if t[0] > 0.0 and t[1] > 0.0:
                layout.append(t)
        outputs['AEP'], outputs['max_TI'] = fun_aep_fast(self.power_curve_file, self.ct_curve_file, self.windrose_file, inputs['layout'], self.nbins, self.artif_angles)


def fun_aep_fast(power_curve_file, ct_curve_file, windrose_file, layout, nbins, artif_angle):
    a=1
    c=2
    e=0
    return call_aep(power_curve_file, ct_curve_file, windrose_file, layout, nbins, artif_angle, a, c, e)
