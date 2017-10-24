from openmdao.api import ExplicitComponent
from numpy import deg2rad, tan, cos, sqrt
import numpy as np
from input_params import max_n_turbines


def distance_to_front(x, y, theta):
    theta = deg2rad(- theta + 90.0)
    return abs(x + tan(theta) * y - 10000000000.0 / cos(theta)) / sqrt(1.0 + tan(theta) ** 2.0)


def order(layout_array, wind_direction):
    distances = []
    for turbine in layout_array:
        distances.append([distance_to_front(turbine[1], turbine[2], wind_direction), turbine[0]])
    distances.sort()
    ordered_indices = [item[1] for item in distances]
    ordered_layout = np.array([layout_array[int(i)] for i in ordered_indices])
    return ordered_layout


class OrderLayout(ExplicitComponent):

    def setup(self):
        self.add_input('original', shape=(max_n_turbines, 3))
        self.add_input('angle', val=1.0)
        self.add_input('n_turbines', val=1)
        self.add_output('ordered', shape=(max_n_turbines, 3))

    def compute(self, inputs, outputs):
        # print "1 Order"
        n_turbines = int(inputs['n_turbines'])
        original = inputs['original'][:n_turbines]
        # print original, "Input Original layout"
        angle = inputs['angle']
        ordered = order(original, angle)
        lendif = max_n_turbines - len(original)
        if lendif > 0:
            ordered = np.concatenate((ordered, [[0 for _ in range(3)] for n in range(lendif)]))
        outputs['ordered'] = ordered
        # print ordered, "Output"


# if __name__ == '__main__':
#     layout = [[0, 5, 0], [1, 3, 0], [2, 7, 1], [3, 2.5, 0]]
#     angle = 0.0
#     print order(layout, angle)
