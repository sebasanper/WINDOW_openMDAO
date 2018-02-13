from aep_workflow import Workflow as aep_workflow

from site_conditions.wind_conditions.windrose_new import WeibullWindBins
from farm_energy.wake_model_mean_new.wake_turbulence_models import frandsen2, danish_recommendation, frandsen, \
    larsen_turbulence, Quarton
from farm_energy.wake_model_mean_new.downstream_effects import JensenEffects as Jensen, LarsenEffects as Larsen, Ainslie1DEffects as Ainslie1D, Ainslie2DEffects as Ainslie2D, constantwake
from farm_energy.wake_model_mean_new.wake_overlap import root_sum_square, maximum, multiplied, summed
from farm_energy.wake_model_mean_new.aero_power_ct_models.aero_models import power, thrust_coefficient

# a - 1
wakemodels = [constantwake, Jensen, Larsen, Ainslie1D, Ainslie2D]
# c - 3
turbmodels = ["ConstantTurbulence", frandsen2, danish_recommendation, frandsen, larsen_turbulence, Quarton]
# e - 5
mergingmodels = [root_sum_square, maximum, multiplied, summed]

def call_aep(power_curve_file, ct_curve_file, windrose_file, layout, nbins, artif_angle, a, c, e):
    real_angle = 30.0
    new_layout = []
    workflow1 = aep_workflow(WeibullWindBins, windrose_file, turbmodels[c], thrust_coefficient, ct_curve_file, wakemodels[a], mergingmodels[e], power, power_curve_file)

    workflow1.windrose.nbins = nbins
    workflow1.windrose.artificial_angle = artif_angle
    workflow1.windrose.real_angle = real_angle
    workflow1.print_output = False
    answer = workflow1.run(layout)
    # power2.reset()
    # thrust_coefficient2.reset()
    return answer
