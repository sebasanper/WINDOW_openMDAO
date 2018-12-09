from area import *
from numpy import deg2rad, tan, sqrt, cos, sin

#from WINDOW_openMDAO.input_params import rotor_radius
from memoize import Memoize
jensen_k = 0.04


def determine_if_in_wake(x_upstream, y_upstream, x_downstream, y_downstream, wind_direction, radius, k=jensen_k):  # According to Jensen Model only
    # Eq. of centreline is Y = tan (d) (X - Xt) + Yt
    # Distance from point to line
    wind_direction = deg2rad(wind_direction + 180.0)
    distance_to_centre = abs(- tan(wind_direction) * x_downstream + y_downstream + tan(wind_direction) * x_upstream - y_upstream) / sqrt(1.0 + tan(wind_direction) ** 2.0)
    # print distance_to_centre
    # Coordinates of the intersection between closest path from turbine in wake to centreline.
    X_int = (x_downstream + tan(wind_direction) * y_downstream + tan(wind_direction) * (tan(wind_direction) * x_upstream - y_upstream)) / (tan(wind_direction) ** 2.0 + 1.0)
    Y_int = (- tan(wind_direction) * (- x_downstream - tan(wind_direction) * y_downstream) - tan(wind_direction) * x_upstream + y_upstream) / (tan(wind_direction) ** 2.0 + 1.0)
    # Distance from intersection point to turbine
    distance_to_turbine = sqrt((X_int - x_upstream) ** 2.0 + (Y_int - y_upstream) ** 2.0)
    # # Radius of wake at that distance
    radius = wake_radius(distance_to_turbine, radius, k)
    if (x_downstream - x_upstream) * cos(wind_direction) + (y_downstream - y_upstream) * sin(wind_direction) <= 0.0:
        if abs(radius) >= abs(distance_to_centre):
            if abs(radius) >= abs(distance_to_centre) + radius:
                fraction = 1.0
                return fraction, distance_to_turbine
            elif abs(radius) < abs(distance_to_centre) + radius:
                fraction = AreaReal(radius, radius, distance_to_centre).area()
                return fraction, distance_to_turbine
        elif abs(radius) < abs(distance_to_centre):
            if abs(radius) <= abs(distance_to_centre) - radius:
                fraction = 0.0
                return fraction, distance_to_turbine
            elif abs(radius) > abs(distance_to_centre) - radius:
                fraction = AreaReal(radius, radius, distance_to_centre).area()
                return fraction, distance_to_turbine
    else:
        return 0.0, distance_to_turbine


# determine_if_in_wake = Memoize(determine_if_in_wake)


def wake_deficit(Ct, x, k=jensen_k, r0=95.4):
    return (1.0 - sqrt(1.0 - Ct)) / (1.0 + (k * x) / r0) ** 2.0


# wake_deficit = Memoize(wake_deficit)


def wake_radius(x, r0, k=jensen_k):
    return r0 + k * x

# wake_radius = Memoize(wake_radius)
