from area import AreaReal
from WINDOW_openMDAO.src.api import DetermineIfInWake, WakeDeficit
from numpy import deg2rad, sqrt, cos, sin
import numpy as np
from WINDOW_openMDAO.input_params import max_n_turbines


class JensenWakeDeficit(WakeDeficit):
    def setup(self):
        super(JensenWakeDeficit, self).setup()

    def wake_deficit_model(self, inputs, *args, **kwargs):
        return wake_deficit1(k_jensen=0.04, *args, **kwargs)


class JensenWakeFraction(DetermineIfInWake):
    def setup(self):
        super(JensenWakeFraction, self).setup()

    def wake_fraction_model(self, inputs, *args, **kwargs):
        return determine_if_in_wake(k_jensen=0.04, *args, **kwargs)


def wake_deficit1(x_down, x_cross, Ct, k_jensen, r0):
    return (1.0 - sqrt(1.0 - Ct)) / (1.0 + (k_jensen * x_down) / r0) ** 2.0


def determine_if_in_wake(x_upstream, y_upstream, x_downstream, y_downstream, wind_direction, downwind_d, crosswind_d,
                         radius, k_jensen):
    wind_direction = - wind_direction + 90.0
    wind_direction = deg2rad(wind_direction + 180.0)
    radius = jensen_wake_radius(downwind_d, radius, k_jensen)
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
    return np.array(fraction)


def jensen_wake_radius(x_down, r0, k_jensen):
    return r0 + k_jensen * x_down


if __name__ == '__main__':
    def ct(v):
        if v < 4.0:
            ans = np.array([0.1])
        elif v <= 25.0:
            val = 7.3139922126945e-7 * v ** 6.0 - 6.68905596915255e-5 * v ** 5.0 + 2.3937885e-3 * v ** 4.0 - \
                  0.0420283143 * v ** 3.0 + 0.3716111285 * v ** 2.0 - 1.5686969749 * v + 3.2991094727
            ans = np.array([val])
        else:
            ans = np.array([0.1])
        return ans


    def u(du):
        return 5.5 * (1.0 - du)


    du0 = wake_deficit1(560.0, 0.0, ct(5.5), 0.04, 40.0)
    u0 = u(du0)
    print du0, u0, ct(5.5)
    du1a = wake_deficit1(560.0, 0.0, ct(u0), 0.04, 40.0)
    u1a = u(du1a)
    print du1a, ct(u0), u1a
    du1b = wake_deficit1(1120.0, 0.0, ct(5.5), 0.04, 40.0)
    print du1b, u(du1b)
    du1 = sqrt(du1b ** 2.0 + du1a ** 2.0)
    print du1, u(du1)
    # print 5.5*(1-wake_deficit1(1120.0, 0.0, 0.79411391, 0.04, 40.0))
    # print 5.5*(1-wake_deficit1(1120.0, 0.0, 0.79411391, 0.04, 40.0))
    # print determine_if_in_wake(0, 0, 500, 0, 150.0, 64.0)
