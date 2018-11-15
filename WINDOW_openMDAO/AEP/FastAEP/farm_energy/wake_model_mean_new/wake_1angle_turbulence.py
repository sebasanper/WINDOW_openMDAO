from __future__ import absolute_import
from __future__ import division
from builtins import zip
from builtins import range
from past.utils import old_div
from .order_layout import order
import numpy as np
from WINDOW_openMDAO.input_params import rotor_radius
from .memoize import Memoize


def turbulence_one_angle(deficit_matrix, original_layout, freestream_wind_speed, wind_angle, ambient_turbulence, WakeModel, ThrustModel, ct_table, TurbulenceModel):
    wind_angle = - wind_angle + 90.0 # To conform to windrose convention. Wake model is written to read 0 as positive X and then angles are measured counterclockwise.
    ordered_layout = order(original_layout, wind_angle)
    ct = []
    wind_speeds_array = freestream_wind_speed
    # deficit_matrix = [[] for _ in range(len(ordered_layout))]
    front = []
    # for i in range(len(ordered_layout)):
        # ct.append(ThrustModel(wind_speeds_array, thrust_file))
        # deficit_matrix[i] = [0.0 for _ in range(i + 1)]
        # deficit_matrix[i] += WakeModel(ordered_layout[i], ct[i], ordered_layout[i + 1:], wind_angle, freestream_wind_speed, ambient_turbulence)
    transposed = [list(x) for x in zip(*deficit_matrix)]
    for i in range(len(transposed)):
        lista = transposed[i]
        if len(set(lista)) <= 1:
            front.append(float("inf"))
            continue
        maximo = max(lista)
        indice = lista.index(maximo)
        indice_maximo = ordered_layout[indice][0]
        front.append(indice_maximo)
    # print front
    a = list(zip([item[0] for item in ordered_layout], front))
    # print a

    def first(x):
        return x[0]

    turbine_affects = sorted(a, key=first)

    wake_added_turbulence = []
    for item in turbine_affects:
        if float("inf") in item:
            wake_added_turbulence.append(ambient_turbulence)
        else:
            wake_added_turbulence.append(TurbulenceModel(ambient_turbulence, ThrustModel(freestream_wind_speed, ct_table), freestream_wind_speed, old_div(np.linalg.norm(np.array([original_layout[item[0]][1], original_layout[item[0]][2]]) - np.array([original_layout[item[1]][1], original_layout[item[1]][2]])), (2.0 * rotor_radius))))

    return wake_added_turbulence
# turbulence_one_angle = Memoize(turbulence_one_angle)


def max_turbulence_one_angle(deficits, original_layout, windspeeds, wind_angle, turbulences, WakeModel, ThrustModel, ct_table, TurbulenceModel):
    maximo = [0.0 for _ in range(len(original_layout))]
    for i in range(len(windspeeds)):
        maxturb = turbulence_one_angle(deficits, original_layout, windspeeds[i], wind_angle, turbulences[i], WakeModel, ThrustModel, ct_table, TurbulenceModel)
        for j in range(len(original_layout)):
            if maxturb[j] > maximo[j]:
                maximo[j] = maxturb[j]
    return maximo
# max_turbulence_one_angle = Memoize(max_turbulence_one_angle)
