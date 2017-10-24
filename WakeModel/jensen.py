from area import AreaReal
# from wake_linear_solver import distance, WakeDeficit, DetermineIfInWake
from numpy import deg2rad, tan, sqrt, cos, sin
import numpy as np
from openmdao.api import ExplicitComponent
from input_params import max_n_turbines

# class JensenModel():
#     def fraction(inputs, *args, **kwargs):
#         return determine_if_in_wake(k=0.04, *args, **kwargs)

#     def deficit(inputs, *args, **kwargs):
#         return wake_deficit1(k=0.04, *args, **kwargs)


class DetermineIfInWake(ExplicitComponent):
    def __init__(self, number):
        super(DetermineIfInWake, self).__init__()
        self.number = number

    def setup(self):
        self.add_input('layout', shape=(max_n_turbines, 3))
        self.add_input('angle', val=90.0)
        self.add_input('n_turbines', val=1)
        self.add_input('downwind_d', shape=max_n_turbines - 1)
        self.add_input('crosswind_d', shape=max_n_turbines - 1)
        self.add_input('r', val=40.0)

        self.add_output('fractions', shape=max_n_turbines - 1, val=0)

    def compute(self, inputs, outputs):
        # print "4 Determine"
        # print inputs['layout'], "Input"
        n_turbines = int(inputs['n_turbines'])
        layout = inputs['layout']
        angle = inputs['angle']
        downwind_d = inputs['downwind_d']
        crosswind_d = inputs['crosswind_d']
        fractions = np.array([])
        r = inputs['r']
        i = 0
        if self.number < n_turbines:
            for n in range(n_turbines):
                if n != self.number:
                    fractions = np.append(fractions, self.wake_fraction(inputs, x_upstream=layout[self.number][1], y_upstream=layout[self.number][2], x_downstream=layout[n][1], y_downstream=layout[n][2], wind_direction=angle, downwind_d=downwind_d[i], crosswind_d=crosswind_d[i], radius=r))
                    i += 1
        lendif = max_n_turbines - len(fractions) - 1
        outputs['fractions'] = np.concatenate((fractions, [0 for n in range(lendif)]))
        #print outputs['fraction'], "Output"


class WakeDeficit(ExplicitComponent):

    def setup(self):
        self.add_input('r', val=40.0)
        self.add_input('downwind_d', shape=max_n_turbines - 1, val=560.0)
        self.add_input('crosswind_d', shape=max_n_turbines - 1, val=0.0)
        self.add_input('ct', shape=max_n_turbines - 1, val=0.79)
        self.add_input('fractions', shape=max_n_turbines - 1)
        self.add_input('n_turbines', val=1)
        self.add_output('dU', shape=max_n_turbines - 1, val=0.3)

    def compute(self, inputs, outputs):
        # print "5 WakeDeficit"
        n_turbines = int(inputs['n_turbines'])
        r = inputs['r']
        d_down = inputs['downwind_d']
        d_cross = inputs['crosswind_d']
        c_t = inputs['ct']
        fraction = inputs['fractions']
        # print c_t, "Input1 ct"
        # print fraction, "Input2 fraction"
        deficits = np.array([])
        for ind in range(n_turbines - 1):
            if fraction[ind] > 0.0:
                deficits = np.append(deficits, [fraction[ind] * self.wake_deficit(inputs, x_down=d_down[ind], x_cross=d_cross[ind], Ct=c_t[ind], r0=r)])
            else:
                deficits = np.append(deficits, [0.0])
        lendif = max_n_turbines - len(deficits) - 1
        outputs['dU'] = np.concatenate((deficits, [0 for n in range(lendif)]))
        # print outputs['dU'], "Output"


def wake_deficit1(x_down, x_cross, Ct, k, r0):
    return (1.0 - sqrt(1.0 - Ct)) / (1.0 + (k * x_down) / r0) ** 2.0

# def jensen_fraction(*args, **kwargs):
#     return determine_if_in_wake(k_jensen=inputs['k'], *args, **kwargs)


def determine_if_in_wake(x_upstream, y_upstream, x_downstream, y_downstream, wind_direction, downwind_d, crosswind_d, radius, k_jensen):
    wind_direction = - wind_direction + 90.0
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


def jensen_wake_radius(x_down, r0, k):
    return r0 + k * x_down


class JensenWakeDeficit(WakeDeficit):

    def setup(self):
        super(JensenWakeDeficit, self).setup()
        self.add_input('k', val=0.04)

    def wake_deficit(self, inputs, *args, **kwargs):
        k_jensen = inputs['k']
        return wake_deficit1(k=k_jensen, *args, **kwargs)
        # self.wake_deficit == wake_deficit1(d_down[ind], d_cross[ind], c_t[ind], k, r)


class JensenWakeFraction(DetermineIfInWake):

    def setup(self):
        super(JensenWakeFraction, self).setup()
        self.add_input('k', val=0.04)

    def wake_fraction(self, inputs, *args, **kwargs):
        k_jensen = inputs['k']
        return determine_if_in_wake(k_jensen=k_jensen, *args, **kwargs)


if __name__ == '__main__':
    def ct(v):
        if v < 4.0:
            ans = np.array([0.1])
        elif v <= 25.0:
            val = 7.3139922126945e-7 * v ** 6.0 - 6.68905596915255e-5 * v ** 5.0 + 2.3937885e-3 * v ** 4.0 - 0.0420283143 * v ** 3.0 + 0.3716111285 * v ** 2.0 - 1.5686969749 * v + 3.2991094727
            ans = np.array([val])
        else:
            ans = np.array([0.1])
        return ans

    def u(du):
        return 5.5*(1.0-du)


    du0=wake_deficit1(560.0, 0.0, ct(5.5), 0.04, 40.0)
    u0 = u(du0)
    print du0, u0, ct(5.5)
    du1a= wake_deficit1(560.0, 0.0, ct(u0), 0.04, 40.0)
    u1a = u(du1a)
    print du1a, ct(u0), u1a
    du1b = wake_deficit1(1120.0, 0.0, ct(5.5), 0.04, 40.0)
    print du1b, u(du1b)
    du1= sqrt(du1b**2.0+du1a**2.0)
    print du1, u(du1)
    # print 5.5*(1-wake_deficit1(1120.0, 0.0, 0.79411391, 0.04, 40.0))
    # print 5.5*(1-wake_deficit1(1120.0, 0.0, 0.79411391, 0.04, 40.0))
    # print determine_if_in_wake(0, 0, 500, 0, 150.0, 64.0)
