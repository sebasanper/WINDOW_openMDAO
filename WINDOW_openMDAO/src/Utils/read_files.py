import numpy as np


def read_layout(layout_file):
    layout_file = open(layout_file, 'r')
    layout = []
    i = 0
    for line in layout_file:
        columns = line.split()
        layout.append([i, float(columns[0]), float(columns[1])])
        i += 1

    return np.array(layout)


def read_windrose(filename):
    direction = []
    weibull_scale = []
    weibull_shape = []
    dir_probability = []
    with open(filename, 'r') as windrose:
        for line in windrose:
            columns = line.split()
            direction.append(float(columns[0]))
            weibull_scale.append(float(columns[1]))
            weibull_shape.append(float(columns[2]))
            dir_probability.append(float(columns[3]))
    return direction, weibull_scale, weibull_shape, dir_probability

