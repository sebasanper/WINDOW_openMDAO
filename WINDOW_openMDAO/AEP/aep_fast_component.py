"""Summary
"""
from builtins import range
from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import max_n_turbines

from WINDOW_openMDAO.AEP.FastAEP.call_aep_workflow_once import call_aep


class AEPFast(ExplicitComponent):

    """Summary
    
    Attributes:
        artif_angles (TYPE): Description
        ct_curve_file (TYPE): Description
        merge_model (TYPE): Description
        nbins (TYPE): Description
        power_curve_file (TYPE): Description
        turbulence_model (TYPE): Description
        wake_model (TYPE): Description
        windrose_file (TYPE): Description
    """
    
    def __init__(self, options):
        """Summary
        
        Args:
            wake_model (TYPE): Description
            turbulence_model (TYPE): Description
            merge_model (TYPE): Description
            artif_angles (TYPE): Description
            nbins (TYPE): Description
            windrose_file (TYPE): Description
            power_curve_file (TYPE): Description
            ct_curve_file (TYPE): Description
        """
        super(AEPFast, self).__init__()
        self.options = options
        # self.artif_angles = artif_angles
        # self.nbins = nbins
        # self.windrose_file = windrose_file
        # self.power_curve_file = power_curve_file
        # self.ct_curve_file = ct_curve_file
        # self.wake_model = wake_model
        # self.turbulence_model = turbulence_model
        # self.merge_model = merge_model

    def setup(self):
        """Summary
        """
        self.add_input("layout", shape=(max_n_turbines, 2))
        self.add_input("n_turbines", val=0)

        self.add_output("AEP", val=0.0)
        self.add_output("max_TI", shape=max_n_turbines)
        self.add_output("efficiency", val=0.0)

    def compute(self, inputs, outputs):
        """Summary
        
        Args:
            inputs (TYPE): Description
            outputs (TYPE): Description
        """
        n_turbines = int(inputs["n_turbines"])
        layout = inputs["layout"][:n_turbines]
        # layout = []
        # for t in layout2:
        #     if t[0] >= 0.0 and t[1] >= 0.0:
        #         layout.append(t)
        diff = max_n_turbines - n_turbines
        AEP, max_TI, efficiency = function_aep_fast(self.options, layout)
        if diff:
            np.append(max_TI, np.empty(diff).fill(np.nan))
        outputs['AEP'], outputs['max_TI'], outputs['efficiency'] = AEP, max_TI, efficiency


def function_aep_fast(options, layout):
    """Summary
    
    Args:
        wake_model (TYPE): Description
        turbulence_model (TYPE): Description
        merge_model (TYPE): Description
        power_curve_file (TYPE): Description
        ct_curve_file (TYPE): Description
        windrose_file (TYPE): Description
        layout (TYPE): Description
        nbins (TYPE): Description
        artif_angle (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    return call_aep(options, layout)
