from numpy import pi, sqrt, deg2rad, tan, cos, sin
from area import AreaReal
from WINDOW_openMDAO.input_params import rotor_radius as r0, hub_height as H
from memoize import Memoize

D = 2.0 * r0
rotor_area = pi * r0 ** 2.0
# print rotor_area


def rnb(ia):
    return max(1.08 * D, 1.08 * D + 21.7 * D * (ia - 0.05))
# rnb = Memoize(rnb)


def r95(ia):
    # print 0.5 * (rnb(ia) + min(H, rnb(ia)))
    return 0.5 * (rnb(ia) + min(H, rnb(ia)))
# r95 = Memoize(r95)


def wake_radius(ct, x, ia):
    return ((35.0 / 2.0 / pi) ** (1.0 / 5.0)) * ((3.0 * c1(ct, ia) ** 2.0) ** (1.0 / 5.0)) * ((ct * rotor_area * x) ** (1.0 / 3.0))
# wake_radius = Memoize(wake_radius)


def deff(Ct):
    # print D * sqrt((1.0 + sqrt(1.0 - Ct)) / (2.0 * sqrt(1.0 - Ct)))
    return D * sqrt((1.0 + sqrt(1.0 - Ct)) / (2.0 * sqrt(1.0 - Ct)))
# deff = Memoize(deff)


def x0(Ct, ia):
    # print "x0"
    # print (2.0 * r95(ia) / deff(Ct)) ** 3.0 - 1.0
    return 9.5 * D / ((2.0 * r95(ia) / deff(Ct)) ** 3.0 - 1.0)
# x0 = Memoize(x0)


def c1(Ct, ia):
    # print (x0(Ct, ia)) ** (- 5.0 / 6.0)
    return (deff(Ct) / 2.0) ** (5.0 / 2.0) * (105.0 / 2.0 / pi) ** (- 1.0 / 2.0) * (Ct * rotor_area * x0(Ct, ia)) ** (- 5.0 / 6.0)  # Prandtl mixing length
# c1 = Memoize(c1)


def determine_if_in_wake_larsen(xt, yt, xw, yw, ct, alpha, ia):  # According to Larsen Model only
    # Eq. of centreline is Y = tan (d) (X - Xt) + Yt
    # Distance from point to line
    alpha = deg2rad(alpha + 180)
    distance_to_centre = abs(- tan(alpha) * xw + yw + tan(alpha) * xt - yt) / sqrt(1.0 + tan(alpha) ** 2.0)
    # print distance_to_centre
    # Coordinates of the intersection between closest path from turbine in wake to centreline.
    X_int = (xw + tan(alpha) * yw + tan(alpha) * (tan(alpha) * xt - yt)) / (tan(alpha) ** 2.0 + 1.0)
    Y_int = (- tan(alpha) * (- xw - tan(alpha) * yw) - tan(alpha) * xt + yt) / (tan(alpha) ** 2.0 + 1.0)
    # Distance from intersection point to turbine
    distance_to_turbine = sqrt((X_int - xt) ** 2.0 + (Y_int - yt) ** 2.0)
    # Radius of wake at that distance
    radius = wake_radius(ct, distance_to_turbine + x0(ct, ia), ia)
    # print radius
    if (xw - xt) * cos(alpha) + (yw - yt) * sin(alpha) <= 0.0:
        if abs(radius) >= abs(distance_to_centre):
            if abs(radius) >= abs(distance_to_centre) + r0:
                fraction = 1.0
                value = True
                return fraction, value, distance_to_centre, distance_to_turbine
            elif abs(radius) < abs(distance_to_centre) + r0:
                fraction = AreaReal(r0, radius, distance_to_centre).area()
                value = True
                return fraction, value, distance_to_centre, distance_to_turbine
        elif abs(radius) < abs(distance_to_centre):
            if abs(radius) <= abs(distance_to_centre) - r0:
                fraction = 0.0
                value = False
                return fraction, value, distance_to_centre, distance_to_turbine
            elif abs(radius) > abs(distance_to_centre) - r0:
                fraction = AreaReal(r0, radius, distance_to_centre).area()
                value = True
                return fraction, value, distance_to_centre, distance_to_turbine
    else:
        return 0.0, False, distance_to_centre, distance_to_turbine


# determine_if_in_wake_larsen = Memoize(determine_if_in_wake_larsen)


def wake_speed(U0, ct, x, y, ia):
    return U0 * (1.0 - ((ct * rotor_area * x ** (- 2.0)) ** (1.0 / 3.0)) / 9.0 * (y ** (3.0 / 2.0) * (3.0 * c1(ct, ia) ** 2.0 * ct * rotor_area * x) ** (- 1.0 / 2.0) - (35.0 / 2.0 / pi) ** (3.0 / 10.0) * (3.0 * c1(ct, ia) ** 2.0) ** (- 1.0 / 5.0)) ** 2.0)


# wake_speed = Memoize(wake_speed)


def wake_deficit_larsen(U0, ct, x, y, ia):
    if U0 == 0.0:
        return 1.0
    return 1.0 - wake_speed(U0, ct, x + x0(ct, ia), y, ia) / U0


# wake_deficit_larsen = Memoize(wake_deficit_larsen)
