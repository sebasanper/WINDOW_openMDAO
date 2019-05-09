from __future__ import absolute_import
from .aep_workflow import Workflow as aep_workflow
from .site_conditions.wind_conditions.windrose_new import WeibullWindBins
from .farm_energy.wake_model_mean_new.aero_power_ct_models.aero_models import power, thrust_coefficient


def call_aep(options, layout):

    workflow1 = aep_workflow(WeibullWindBins, options)

    workflow1.windrose.nbins = options.samples.wind_speeds
    workflow1.windrose.artificial_angle = options.samples.wind_sectors_angle
    workflow1.print_output = False
    answer = workflow1.run(layout)
    # power2.reset()
    # thrust_coefficient2.reset()
    return answer
