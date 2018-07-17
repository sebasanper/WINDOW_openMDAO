from math import sqrt
# from memoize import Memoize
# from WINDOW_openMDAO.input_params import rotor_radius
rotor_radius = 63.0
#  Change in Fatigue and Extreme Loading when Moving Wind Farms Offshore // Sten Frandsen and Kenneth Thomsen.
#  Only nearest wake-shedding turbine matters in a wind farm.

def constantturbulence(ambient_turbulence, Ct, wind_speed, spacing):
    return 0.15


def frandsen2(ambient_turbulence, Ct, wind_speed, spacing):
    return sqrt(1.2 * Ct / spacing ** 2.0 + ambient_turbulence ** 2.0)


# frandsen2 = Memoize(frandsen2)


def danish_recommendation(ambient_turbulence, ct, wind_speed, spacing):

    def beta_v(u):
        if u < 12.0:
            return 1.0
        elif u < 20.0:
            return 1.747 - 0.0625 * u
        else:
            return 0.5

    # Beta_l, x is turbine spacing

    def beta_l(d, cluster=True):
        if cluster:
            if d < 2.9838:
                return 1.0
            elif d < 5.9856:
                return 1.333 - 0.1116 * d
            else:
                return 0.665

        else:
            if d < 5.0:
                return 1.0
            elif d < 10.0:
                return 1.333 - 0.067 * d
            else:
                return 0.665

    Iw = 0.15 * beta_v(wind_speed) * beta_l(spacing)
    Ia = ambient_turbulence
    Id = sqrt(Ia ** 2.0 + Iw ** 2.0)
    return Id


# danish_recommendation = Memoize(danish_recommendation)


def larsen_turbulence(ambient_turbulence, Ct, speed, spacing):
    # Wind Resource Assessment and Micro-siting: Science and Engineering
    # By Matthew Huaiquan Zhangaiquan Zhang
    # for spacings larger than 2D
    s = spacing
    Iw = 0.29 * s ** (- 1.0 / 3.0) * (1.0 - (1.0 - Ct) ** 0.5) ** 0.5
    Ia = ambient_turbulence
    Id = sqrt(Ia ** 2.0 + Iw ** 2.0)
    return Id


# larsen_turbulence = Memoize(larsen_turbulence)


def frandsen(ambient_turbulence, Ct, speed, spacing, large=False):
    #  For spacings smaller than 10D
    Ia = ambient_turbulence
    s = spacing
    # 0.8 sometimes 0.3 double check
    # u = 10.0  # wind speed
    Iw = 1.0 / (1.5 + 0.8 * s / Ct ** 0.5)
    It = sqrt(Iw ** 2.0 + Ia ** 2.0)

    if large:
        #  More than 5 turbines between turbine under consideration and edge of park, OR turbines spaces less than 3D
        # in the direction perpendicular to wind. For regular layouts.

        sd = spacing
        sc = spacing
        Iw = 0.36 / (1.0 + 0.2 * (sd * sc / Ct) ** 0.5)
        Ia = 0.5 * (Ia + (Iw ** 2.0 + Ia ** 2.0) ** 0.5)
        It = (Iw ** 2.0 + Ia ** 2.0) ** 0.5

    return It


# frandsen = Memoize(frandsen)


def Quarton(ambient_turbulence, Ct, speed, x, tsr=7.6):
    # TODO
    D = rotor_radius * 2.0
    # x /= D
    Ia = ambient_turbulence
    K1 = 4.8
    a1 = 0.7
    a2 = 0.68
    a3 = - 0.57
    m = 1.0 / (1.0 - Ct) ** 0.5
    r0 = D / 2.0 * ((m + 1.0) / 2.0) ** 0.5

    if Ia >= 0.020:
        da = 0.025 * Ia + 0.050
    else:
        da = 0.050 * Ia

    B = 3  # Number of blades
    L = tsr  # Tip speed ratio
    dl = 0.012 * B * L
    dm = (1.0 - m) * (1.49 + m) ** 0.5 / (9.76 * (1.0 + m))

    xh = r0 * (da + dl + dm) ** (- 0.5)
    xn = xh * (0.212 + 0.145 * m) ** 0.5 * (1.0 - (0.134 + 0.124 * m) ** 0.5) / (1.0 - (0.212 + 0.145 * m) ** 0.5) / (0.134 + 0.124 * m) ** 0.5
    # print x/xn
    Iw = K1 * (Ct ** a1) * (Ia ** a2) * (x/xn*D) ** a3
    # print Iw, x, xn
    return sqrt(Iw ** 2.0 * 100.0 + Ia ** 2.0)


# Quarton = Memoize(Quarton)

#  ONLY to be used with the Ainslie Eddy Viscosity model. Use Eddy Viscosity term from the Ainslie model (E)
# def Lange(eddy_viscosity, free_flow_wind_speed, hub_height, wake_radius, karman=0.41):
#
#     u0 = free_flow_wind_speed
#     eps = eddy_viscosity
#     H = hub_height
#     I = eps * 2.4 / karman / u0 / H
#     return Ia + I *


# def ForWind():
#     A = 1.42
#     B = 0.54
#     I_shear = A * I_mean
#     I_add = I_shear + I_diff


if __name__ == "__main__":
    # 7d downstream
    ct = 0.6
    with open('turb_downstream_d3.dat', 'w') as out:
        for x in range(100):
            d = float(x) * 0.1 + 0.1
            out.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'.format(d, danish_recommendation(0.11, ct, 8.28, d), larsen_turbulence(0.11, ct, 8.28, d), Quarton(0.11, ct, 8.28, d*rotor_radius*2.0), frandsen(0.11, ct, 8.28, d), frandsen2(0.11, ct, 8.28, d)))

    # print danish_recommendation(0.08, 8.5, 7.0)
    # print Larsen_turbulence(0.08, 7.0, 0.79)
    # # print frandsen(0.08, 0.79, )
    # print Quarton(8.0, 0.79, 80.0, 9.0, 560.0)
    # print Lange(0.064, 8.5, 100.0)
