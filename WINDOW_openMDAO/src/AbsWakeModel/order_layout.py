from openmdao.api import ExplicitComponent
from numpy import deg2rad, tan, cos, sqrt
import numpy as np
from WINDOW_openMDAO.input_params import max_n_turbines


def distance_to_front(x, y, theta):
    theta = deg2rad(- theta + 90.0)
    return abs(x + tan(theta) * y - 10000000000000000000.0 / cos(theta)) / sqrt(1.0 + tan(theta) ** 2.0)


def order(layout_array, wind_direction):
    distances = []
    for turbine in layout_array:
        distances.append([distance_to_front(turbine[1], turbine[2], wind_direction), turbine[0]])
    distances.sort()
    ordered_indices = [item[1] for item in distances]
    ordered_layout = np.array([layout_array[int(i)] for i in ordered_indices])
    return ordered_layout


class OrderLayout(ExplicitComponent):
    def __init__(self, n_cases):
        super(OrderLayout, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        self.add_input('original', shape=(max_n_turbines, 3))
        self.add_input('angle', shape=self.n_cases)
        self.add_input('n_turbines', val=1)
        self.add_output('ordered', shape=(self.n_cases, max_n_turbines, 3))

    def compute(self, inputs, outputs):
        # print "1 Order"
        ordered = np.array([])
        for case in range(self.n_cases):
            angle = inputs['angle'][case]
            n_turbines = int(inputs['n_turbines'])
            original = inputs['original'][:n_turbines]
            # print original, "Input Original layout"
            res = order(original, angle)
            lendif = max_n_turbines - len(original)
            if lendif > 0:
                res = np.concatenate((res, [[0 for _ in range(3)] for _ in range(lendif)]))
            ordered = np.append(ordered, res)
        ordered = ordered.reshape(self.n_cases, max_n_turbines, 3)
        outputs['ordered'] = ordered
        # print ordered, "Output"


# if __name__ == '__main__':
#     layout = [[0, 5, 0], [1, 3, 0], [2, 7, 1], [3, 2.5, 0]]
#     angle = 0.0
#     print order(layout, angle)
