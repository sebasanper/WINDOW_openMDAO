from __future__ import absolute_import
from builtins import zip
from builtins import range
from .order_layout import order


def energy_one_angle(original_layout, freestream_wind_speeds, probabilities_speed, wind_angle, ambient_turbulences, WakeModel, PowerModel, table_power, ThrustModel, ct_table, MergingModel):
    wind_angle = - wind_angle + 90.0  # To conform to windrose convention. Wake model is written to read 0 as positive X and then angles are measured counterclockwise.
    ordered_layout = order(original_layout, wind_angle)
    energy = 0.0
    weighted_individuals = [0.0 for _ in range(len(original_layout))]
    # print original_layout
    # print ordered_layout
    def first(x):
        return x[0]
    # print len(freestream_wind_speeds)
    for speed in range(len(freestream_wind_speeds)):
        ct = []
        wind_speeds_array = [freestream_wind_speeds[speed]]
        deficit_matrix = [[] for _ in range(len(ordered_layout))]
        total_deficit = [0.0]
        # print len(ordered_layout)
        for i in range(len(ordered_layout)):
            if i == 0:
                pass
            else:
                total_deficit.append(MergingModel([deficit_matrix[j][i] for j in range(i)]))
                wind_speeds_array.append(freestream_wind_speeds[speed] * (1.0 - total_deficit[i]))
            # print speed, i, wind_angle
            ct.append(ThrustModel(wind_speeds_array[i], ct_table))
            deficit_matrix[i] = [0.0 for _ in range(i + 1)]
            deficit_matrix[i] += WakeModel(ordered_layout[i], ct[i], ordered_layout[i + 1:], wind_angle, freestream_wind_speeds[speed], ambient_turbulences[speed])
        wind_speeds_array_original = [x for (y, x) in sorted(zip([item[0] for item in ordered_layout], wind_speeds_array), key=first)]
        # print len(wind_speeds_array_original)
        individual_powers = [PowerModel(wind, table_power) for wind in wind_speeds_array_original]
        # print individual_powers
        for turb in range(len(individual_powers)):
            weighted_individuals[turb] += individual_powers[turb] * probabilities_speed[speed] / 100.0
        farm_power = sum(individual_powers)
        energy += farm_power * probabilities_speed[speed] / 100.0 * 8760.0
    return energy, weighted_individuals, deficit_matrix
