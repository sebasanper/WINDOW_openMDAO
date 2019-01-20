import jensen
#import larsen
#import ainslie1d
#import ainslie2d
#from farm_energy.wake_model_mean_new.ainslie2d_cy import ainslie_full
# ainslie_full = Memoize(ainslie_full)
from ainslie_common import crosswind_distance, determine_front
from time import time
#from WINDOW_openMDAO.input_params import rotor_radius


def constantwake(coordinates_upstream, thrust_coefficient, coordinates_downstream, angle, wind_speed_upstream, ambient_turbulence_intensity):
    return [0.2 for _ in range(len(coordinates_downstream))]


def JensenEffects(coordinates_upstream, thrust_coefficient, coordinates_downstream, angle, wind_speed_upstream, ambient_turbulence_intensity, rotor_radius):
    angle3 = angle + 180.0
    # coordinates downstream will be an array with coordinates and original index.
    partial_deficits = []

    for i in range(len(coordinates_downstream)):
        determ = jensen.determine_if_in_wake(coordinates_upstream[1], coordinates_upstream[2], coordinates_downstream[i][1], coordinates_downstream[i][2], angle3, rotor_radius)
        # print determ[1], "determ1"
        # print determ[0], "determ0"

        if determ[0] != 0.0:
            # print jensen.wake_deficit(thrust_coefficient, determ[1])
            partial_deficits.append(determ[0] * jensen.wake_deficit(thrust_coefficient, determ[1]))
        else:
            partial_deficits.append(0.0)

    return partial_deficits


def LarsenEffects(coordinates_upstream, thrust_coefficient, coordinates_downstream, angle, wind_speed_upstream, ambient_turbulence_intensity):
    angle3 = angle + 180.0
    partial_deficits = []

    for i in range(len(coordinates_downstream)):
        proportion, flag, perpendicular_distance, parallel_distance = larsen.determine_if_in_wake_larsen(coordinates_upstream[1], coordinates_upstream[2], coordinates_downstream[i][1], coordinates_downstream[i][2], thrust_coefficient, angle3, ambient_turbulence_intensity)
        if parallel_distance > 0.0:
            if proportion != 0.0:
                partial_deficits.append(proportion * larsen.wake_deficit_larsen(wind_speed_upstream, thrust_coefficient, parallel_distance + larsen.x0(thrust_coefficient, ambient_turbulence_intensity), perpendicular_distance, ambient_turbulence_intensity))
            else:
                partial_deficits.append(0.0)
        else:
            partial_deficits.append(0.0)

    return partial_deficits


def Ainslie1DEffects(coordinates_upstream, thrust_coefficient, coordinates_downstream, angle, wind_speed_upstream, ambient_turbulence_intensity, diameter=190.8):
    angle3 = angle + 180.0
    partial_deficits = []
    normalised_upstream = [coordinates_upstream[i] / diameter for i in range(1, 3)]
    normalised_downstream = [[coordinates_downstream[j][i] / diameter for i in range(1, 3)] for j in range(len(coordinates_downstream))]

    for i in range(len(normalised_downstream)):

        parallel_distance = determine_front(angle3, normalised_upstream[0], normalised_upstream[1], normalised_downstream[i][0], normalised_downstream[i][1])
        perpendicular_distance = crosswind_distance(angle3, normalised_upstream[0], normalised_upstream[1], normalised_downstream[i][0], normalised_downstream[i][1])
        if perpendicular_distance <= 1.7 and parallel_distance > 0.0:  # 1.7 gives same results as a bigger distance, many times faster.
            partial_deficits.append(ainslie1d.ainslie(thrust_coefficient, wind_speed_upstream, parallel_distance, perpendicular_distance, ambient_turbulence_intensity))
        else:
            partial_deficits.append(0.0)

    return partial_deficits


# from time import time
def Ainslie2DEffects(coordinates_upstream, thrust_coefficient, coordinates_downstream, angle, wind_speed_upstream, ambient_turbulence_intensity, diameter=190.8):
    angle3 = angle + 180.0
    partial_deficits = []
    normalised_upstream = [coordinates_upstream[i] / diameter for i in range(1, 3)]
    normalised_downstream = [[coordinates_downstream[j][i] / diameter for i in range(1, 3)] for j in range(len(coordinates_downstream))]
    # start = time()
    for i in range(len(normalised_downstream)):
        parallel_distance = determine_front(angle3, normalised_upstream[0], normalised_upstream[1], normalised_downstream[i][0], normalised_downstream[i][1])
        perpendicular_distance = crosswind_distance(angle3, normalised_upstream[0], normalised_upstream[1], normalised_downstream[i][0], normalised_downstream[i][1])
        if perpendicular_distance < 2.0 and parallel_distance > 0.0:
            # if wind_speed_upstream > 23.0:
                # print thrust_coefficient, wind_speed_upstream, parallel_distance, perpendicular_distance, ambient_turbulence_intensity
            partial_deficits.append(ainslie2d.ainslie_full(thrust_coefficient, wind_speed_upstream, parallel_distance, perpendicular_distance, ambient_turbulence_intensity))
        else:
            partial_deficits.append(0.0)

    return partial_deficits


if __name__ == '__main__':
    upstream = [0, 0.0, 0.0]
    ct_upstream = 0.79
    downstream_turbines = [[1, 500.0, 0.0], [2, 1000.0, 0.0], [3, 1500.0, 0.0], [4, 2000.0, 0.0], [5, 2500.0, 0.0], [6, 1000.0, 0.0], [7, 1500.0, 0.0], [8, 2000.0, 0.0], [9, 2500.0, 0.0], [10, 1000.0, 0.0], [11, 1500.0, 0.0], [12, 2000.0, 0.0], [13, 2500.0, 0.0], [14, 1000.0, 0.0], [15, 1500.0, 0.0], [16, 2000.0, 0.0], [17, 2500.0, 0.0], [18, 1000.0, 0.0], [19, 1500.0, 0.0], [20, 2000.0, 0.0], [21, 2500.0, 0.0]]

    # print LarsenEffects(upstream, ct_upstream, downstream_turbines, 180.0, 8.5, 0.08)
    #
    # print LarsenEffects(upstream, ct_upstream, downstream_turbines, 180.0, 8.5, 0.08)
    #
    # print Ainslie1DEffects(upstream, ct_upstream, downstream_turbines, 180.0, 8.5, 0.08)
    #
    # print Ainslie2DEffects(upstream, ct_upstream, downstream_turbines, 180.0, 8.5, 0.08)
