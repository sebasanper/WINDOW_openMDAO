"""Summary
"""
from builtins import range
from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import max_n_turbines, rotor_radius, hub_height

import numpy as np

from py_wake.wake_models.noj import NOJ
from py_wake.aep_calculator import AEPCalculator
from py_wake.site._site import UniformWeibullSite
from py_wake.wind_turbines import OneTypeWindTurbines
import time 

class pyWakeDTU(ExplicitComponent):

    """Summary
    
    Attributes:
        options (TYPE): Description
        wt (TYPE): Description
    """
    
    def __init__(self, options):
        """Summary
        
        Args:
            options (TYPE): Description
        """
        super(pyWakeDTU, self).__init__()
        self.options = options
        # self.artif_angles = artif_angles
        # self.nbins = nbins
        # self.windrose_file = windrose_file
        # self.power_curve_file = power_curve_file
        # self.ct_curve_file = ct_curve_file
        # self.wake_model = wake_model
        # self.turbulence_model = turbulence_model
        # self.merge_model = merge_model

    # wt9_x = np.array(wt_x)[[0, 1, 2, 8, 9, 10, 16, 17, 18]]
    # wt9_y = np.array(wt_y)[[0, 1, 2, 8, 9, 10, 16, 17, 18]]

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
        AEP, max_TI, efficiency = function_aep_pywake(self.options, layout, inputs)
        if diff:
            np.append(max_TI, np.full(diff, np.nan))
        # print(AEP, max_TI, efficiency)
        outputs['AEP'], outputs['max_TI'], outputs['efficiency'] = AEP, max_TI, efficiency


def function_aep_pywake(options, layout, inputs):
    """Summary
    
    Args:
        options (TYPE): Description
        layout (TYPE): Description
        inputs (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    class V80(OneTypeWindTurbines):

        """Summary
        
        Attributes:
            ct_curve (TYPE): Description
            power_curve (TYPE): Description
        """
        
        def __init__(self):
            """Summary
            """
            OneTypeWindTurbines.__init__(self, 'V80', diameter= rotor_radius * 2., hub_height= hub_height, ct_func=self._ct, power_func=self._power, power_unit='GW')
            self.power_curve = np.loadtxt(options.input.turbine.power_curve_file)
            self.ct_curve = np.loadtxt(options.input.turbine.ct_curve_file)

        def _ct(self, u):
            """Summary
            
            Args:
                u (TYPE): Description
            
            Returns:
                TYPE: Description
            """
            return np.interp(u, self.ct_curve[:, 0], self.ct_curve[:, 1])

        def _power(self, u):
            """Summary
            
            Args:
                u (TYPE): Description
            
            Returns:
                TYPE: Description
            """
            return np.interp(u, self.power_curve[:, 0], self.power_curve[:, 1])


    class IEA37(UniformWeibullSite):

        """Summary
        
        Attributes:
            initial_position (TYPE): Description
        """
        
        def __init__(self, layout):
            """Summary
            """
            windrose = np.loadtxt(options.input.site.windrose_file)
            a = windrose[:,0]
            k = windrose[:,1]
            f = windrose[:,2]
            UniformWeibullSite.__init__(self, f, a, k, .1)

            self.initial_position = layout

    wt = V80()

    aep_calculator = AEPCalculator(IEA37(layout), wt, NOJ(wt))
    start = time.time()
    aep = aep_calculator.calculate_AEP(layout[:,0], layout[:,1], wd=np.arange(0, 360, 1), ws=np.arange(1,28)).sum()
    aep_nowake = aep_calculator.calculate_AEP_no_wake_loss(layout[:,0], layout[:,1]).sum()

    print(time.time() - start, "time_pywake")
    efficiency = aep / aep_nowake
    return aep, np.full(len(layout), 0.15), efficiency
