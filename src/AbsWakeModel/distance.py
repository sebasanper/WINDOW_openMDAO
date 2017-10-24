from openmdao.api import ExplicitComponent
from input_params import max_n_turbines
import numpy as np
from numpy import sqrt, deg2rad, tan

class DistanceComponent(ExplicitComponent):
    def __init__(self, number):
        super(DistanceComponent, self).__init__()
        self.number = number

    def setup(self):
        self.add_input('angle', val=90.0)
        self.add_input('layout', shape=(max_n_turbines, 3))
        self.add_input('n_turbines', val=1)
        self.add_output('dist_down', shape=max_n_turbines - 1, val=500.0)
        self.add_output('dist_cross', shape=max_n_turbines - 1, val=300.0)

        # Finite difference all partials.
        # self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):
        #print "3 Distance"
        n_turbines = int(inputs['n_turbines'])
        layout = inputs['layout']
        # print layout, "Input"
        angle = inputs['angle']
        d_down = np.array([])
        d_cross = np.array([])
        for n in range(n_turbines):
            if n != self.number and self.number < n_turbines:
                d_down1, d_cross1 = distance(layout[self.number], layout[n], angle)
                d_cross = np.append(d_cross, [d_cross1])
                d_down = np.append(d_down, [d_down1])
        lendif = max_n_turbines - len(d_cross) - 1
        outputs['dist_down'] = np.concatenate((d_down, [0 for n in range(lendif)]))
        #print outputs['dist_down'], "Output1"
        outputs['dist_cross'] = np.concatenate((d_cross, [0 for n in range(lendif)]))
        #print outputs['dist_cross'], "Output2"


def distance(t1, t2, angle):
    wind_direction = deg2rad(- angle + 90.0)
    distance_to_centre = abs(- tan(wind_direction) * t2[1] + t2[2] + tan(wind_direction) * t1[1] - t1[2]) / sqrt(
        1.0 + tan(wind_direction) ** 2.0)
    # Coordinates of the intersection between closest path from turbine in wake to centreline.
    x_int = (t2[1] + tan(wind_direction) * t2[2] + tan(wind_direction) * (tan(wind_direction) * t1[1] - t1[2])) / \
            (tan(wind_direction) ** 2.0 + 1.0)
    y_int = (- tan(wind_direction) * (- t2[1] - tan(wind_direction) * t2[2]) - tan(
        wind_direction) * t1[1] + t1[2]) / (tan(wind_direction) ** 2.0 + 1.0)
    # Distance from intersection point to turbine
    distance_to_turbine = sqrt((x_int - t1[1]) ** 2.0 + (y_int - t1[2]) ** 2.0)
    return np.array(distance_to_turbine), np.array(distance_to_centre)
