from area import *
from numpy import deg2rad, tan, sqrt, cos, sin


def wake_deficit1(x_down, x_cross, Ct, k=0.04, r0=40.0):
    return (1.0 - sqrt(1.0 - Ct)) / (1.0 + (k * x_down) / r0) ** 2.0


def determine_if_in_wake(x_upstream, y_upstream, x_downstream, y_downstream, wind_direction, downwind_d, crosswind_d, radius=40.0, k=0.04):
    wind_direction = deg2rad(wind_direction + 180.0)
    crosswind_d = abs(- tan(wind_direction) * x_downstream + y_downstream + tan(wind_direction) * x_upstream - y_upstream) / sqrt(
        1.0 + tan(wind_direction) ** 2.0)
    # Coordinates of the intersection between closest path from turbine in wake to centreline.
    x_int = (x_downstream + tan(wind_direction) * y_downstream + tan(wind_direction) * (tan(wind_direction) * x_upstream - y_upstream)) / \
            (tan(wind_direction) ** 2.0 + 1.0)
    y_int = (- tan(wind_direction) * (- x_downstream - tan(wind_direction) * y_downstream) - tan(
        wind_direction) * x_upstream + y_upstream) / (tan(wind_direction) ** 2.0 + 1.0)
    # Distance from intersection point to turbine
    downwind_d = sqrt((x_int - x_upstream) ** 2.0 + (y_int - y_upstream) ** 2.0)
    radius = wake_radius(downwind_d, radius, k)
    fraction = 0.0
    if (x_downstream - x_upstream) * cos(wind_direction) + (y_downstream - y_upstream) * sin(wind_direction) <= 0.0:
        if abs(radius) >= abs(crosswind_d):
            if abs(radius) >= abs(crosswind_d) + radius:
                fraction = 1.0
            elif abs(radius) < abs(crosswind_d) + radius:
                fraction = AreaReal(radius, radius, crosswind_d).area()
        elif abs(radius) < abs(crosswind_d):
            if abs(radius) <= abs(crosswind_d) - radius:
                pass
            elif abs(radius) > abs(crosswind_d) - radius:
                fraction = AreaReal(radius, radius, crosswind_d).area()
    return fraction


def wake_radius(x_down, r0, k):
    return r0 + k * x_down


if __name__ == '__main__':
    pass
    # print determine_if_in_wake(0, 0, 500, 0, 150.0, 64.0)
