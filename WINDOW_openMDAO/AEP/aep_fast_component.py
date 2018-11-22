from builtins import range
from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import max_n_turbines

from WINDOW_openMDAO.AEP.FastAEP.call_aep_workflow_once import call_aep


class AEPFast(ExplicitComponent):
    def __init__(self, wake_model, turbulence_model, merge_model, artif_angles, nbins, windrose_file, power_curve_file,
                 ct_curve_file):
        super(AEPFast, self).__init__()
        self.artif_angles = artif_angles
        self.nbins = nbins
        self.windrose_file = windrose_file
        self.power_curve_file = power_curve_file
        self.ct_curve_file = ct_curve_file
        self.wake_model = wake_model
        self.turbulence_model = turbulence_model
        self.merge_model = merge_model

    def setup(self):
        self.add_input("layout", shape=(max_n_turbines, 2))
        self.add_input("n_turbines", val=0)
        self.add_output("AEP", val=0.0)
        self.add_output("max_TI", shape=max_n_turbines)
        self.add_output("efficiency", val=0.0)

    def compute(self, inputs, outputs):
        n_turbines = int(inputs["n_turbines"])
        layout = inputs["layout"][:n_turbines]
        # layout = []
        # for t in layout2:
        #     if t[0] >= 0.0 and t[1] >= 0.0:
        #         layout.append(t)
        diff = max_n_turbines - len(layout)
        AEP, max_TI, efficiency = fun_aep_fast(self.wake_model, self.turbulence_model, self.merge_model,
                                               self.power_curve_file, self.ct_curve_file, self.windrose_file, layout,
                                               self.nbins, self.artif_angles)
        max_TI += [0.0 for _ in range(diff)]
        outputs['AEP'], outputs['max_TI'], outputs['efficiency'] = AEP, max_TI, efficiency
        # outputs['AEP'] = 2710828306070.0


def fun_aep_fast(wake_model, turbulence_model, merge_model, power_curve_file, ct_curve_file, windrose_file, layout,
                 nbins, artif_angle):

    return call_aep(wake_model, turbulence_model, merge_model, power_curve_file, ct_curve_file, windrose_file, layout,
                    nbins, artif_angle)
