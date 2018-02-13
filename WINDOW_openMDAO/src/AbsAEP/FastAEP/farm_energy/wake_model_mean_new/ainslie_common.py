from numpy import radians, cos, sin
from memoize import Memoize
karman = 0.41  # von Karman constant


def b(deficit, ct):  # Wake width measure
    if deficit <= 0.0:
        deficit = 0.0000000000001
        # print "deficit negativo"
    if 1.0 - 0.5 * deficit < 0.0:
        # print deficit, "deficit negativo"
        pass
    return (3.56 * ct / (8.0 * deficit * (1.0 - 0.5 * deficit))) ** 0.5
# b = Memoize(b)


def F(x):  # Factor for near and far wake
    if x >= 5.5:
        return 1.0
    if x < 5.5:
        if x >= 4.5:
            return 0.65 + ((x - 4.5) / 23.32) ** (1.0 / 3.0)
        else:
            return 0.65 - ((- x + 4.5) / 23.32) ** (1.0 / 3.0)
# F = Memoize(F)


def E(x1, Ud, Dm, u0, i0, ct):  # Eddy viscosity term
    if 1.0 - 0.5 * Dm < 0.0:
        # print x1, Ud, Dm, u0, i0, ct
        pass
    eddy = F(x1) * ((0.015 * b(Dm, ct) * (u0 - Ud)) + (karman ** 2.0) * i0)
    return eddy
# E = Memoize(E)


def determine_front(wind_angle, x_t1, y_t1, x_t2, y_t2):
    wind_angle = radians(wind_angle)
    projection = (x_t2 - x_t1) * cos(wind_angle) + (y_t2 - y_t1) * sin(wind_angle)
    if projection > 0.0:
        return projection
    else:
        return 0.0
# determine_front = Memoize(determine_front)


def crosswind_distance(w_d, t1_x, t1_y, t2_x, t2_y):
    w_d = radians(w_d)
    sol = abs(t1_x * (- sin(w_d)) + t1_y * cos(w_d) - t2_x * (- sin(w_d)) - t2_y * cos(w_d))
    return sol
# crosswind_distance = Memoize(crosswind_distance)
