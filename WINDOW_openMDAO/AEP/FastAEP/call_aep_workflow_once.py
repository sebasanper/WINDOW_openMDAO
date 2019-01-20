from aep_workflow import Workflow as aep_workflow
from site_conditions.wind_conditions.windrose_new import WeibullWindBins
from farm_energy.wake_model_mean_new.aero_power_ct_models.aero_models import power, thrust_coefficient


def call_aep(wake_model, turbulence_model, merge_model, power_curve_file, ct_curve_file, windrose_file, layout, nbins, artif_angle, \
             cutin, cutout, rated_wind, rotor_radius, rated_power):

    workflow1 = aep_workflow(WeibullWindBins, windrose_file, turbulence_model, thrust_coefficient, ct_curve_file, wake_model, merge_model, power, power_curve_file, \
                             cutin, cutout, rated_wind, rotor_radius, rated_power)

    workflow1.windrose.nbins = nbins
    workflow1.windrose.artificial_angle = artif_angle
    workflow1.print_output = False
    answer = workflow1.run(layout)
    # power2.reset()
    # thrust_coefficient2.reset()
    return answer
