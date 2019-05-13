from __future__ import division
from past.utils import old_div
import numpy as numpy
# import radians, tan, cos, sqrt


def distances_to_front(layout, theta):
    theta = np.radians(theta)
    return old_div(np.abs(x + np.tan(theta) * y - old_div(100000000.0, np.cos(theta))), np.sqrt(1.0 + np.tan(theta) ** 2.0))


def order(layout_array, wind_direction):
    distances = np.empty(len(layout_array))
    # for turbine in layout_array:
    distances = distances_to_front(layout_array, wind_direction)
    # print distances
    distances.sort()
    # print distances
    ordered_indices = [item[1] for item in distances]
    ordered_layout = [layout_array[i] for i in ordered_indices]
    return ordered_layout

if __name__ == '__main__':
    layout = [[0, 5, 0], [1, 3, 0], [2, 7, 1], [3, 2.5, 0]]
    angle = 0.0
    # print order(layout, angle)
