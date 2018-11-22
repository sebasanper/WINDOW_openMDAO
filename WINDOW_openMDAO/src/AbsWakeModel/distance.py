from __future__ import division
from builtins import range
from past.utils import old_div
from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import max_n_turbines
import numpy as np
from numpy import sqrt, deg2rad, tan


class DistanceComponent(ExplicitComponent):
    def __init__(self, number, n_cases):
        super(DistanceComponent, self).__init__()
        self.number = number
        self.n_cases = n_cases

    def setup(self):
        self.add_input('angle', shape=self.n_cases)
        self.add_input('ordered', shape=(self.n_cases, max_n_turbines, 3))
        self.add_input('n_turbines', val=1)
        self.add_output('dist_down', shape=(self.n_cases, max_n_turbines))
        self.add_output('dist_cross', shape=(self.n_cases, max_n_turbines))

        # Finite difference all partials.
        #self.declare_partals(of=['dist_down', 'dist_cross'], wrt=['angle', 'ordered', 'n_turbines'], method='fd')

    def compute(self, inputs, outputs):
        d_down2 = []
        d_cross2 = []
        for case in range(self.n_cases):
            # print "3 Distance"
            n_turbines = int(inputs['n_turbines'])
            ordered = inputs['ordered']
            # print layout, "Input"
            angle = inputs['angle'][case]
            d_down = np.array([])
            d_cross = np.array([])
            for n in range(n_turbines):
                if n != self.number and self.number < n_turbines:
                    d_down1, d_cross1 = distance(ordered[case][self.number], ordered[case][n], angle)
                    d_cross = np.append(d_cross, [d_cross1])
                    d_down = np.append(d_down, [d_down1])
            lendif = max_n_turbines - len(d_cross)
            d_down = np.concatenate((d_down, [0 for _ in range(lendif)]))
            d_cross = np.concatenate((d_cross, [0 for _ in range(lendif)]))
            d_down2 = np.append(d_down2, d_down)
            d_cross2 = np.append(d_cross2, d_cross)
        d_down2 = d_down2.reshape(self.n_cases, max_n_turbines)
        d_cross2 = d_cross2.reshape(self.n_cases, max_n_turbines)
        outputs['dist_down'] = d_down2
        outputs['dist_cross'] = d_cross2
        # print outputs['dist_down'], "Output1"
        # print outputs['dist_cross'], "Output2"


def distance(t1, t2, angle):
    wind_direction = deg2rad(- angle + 90.0)
    distance_to_centre = old_div(abs(- tan(wind_direction) * t2[1] + t2[2] + tan(wind_direction) * t1[1] - t1[2]), \
                         sqrt(1.0 + tan(wind_direction) ** 2.0))
    # Coordinates of the intersection between closest path from turbine in wake to centreline.
    x_int = old_div((t2[1] + tan(wind_direction) * t2[2] + tan(wind_direction) * (tan(wind_direction) * t1[1] - t1[2])), \
            (tan(wind_direction) ** 2.0 + 1.0))
    y_int = old_div((- tan(wind_direction) * (- t2[1] - tan(wind_direction) * t2[2]) - tan(
        wind_direction) * t1[1] + t1[2]), (tan(wind_direction) ** 2.0 + 1.0))
    # Distance from intersection point to turbine
    distance_to_turbine = sqrt((x_int - t1[1]) ** 2.0 + (y_int - t1[2]) ** 2.0)
    return np.array(distance_to_turbine), np.array(distance_to_centre)
