from libc.math cimport exp
from farm_energy.wake_model_mean_new.thomas_algorithm_cy import thomas
from turbine_description import rotor_radius
from farm_energy.wake_model_mean_new.ainslie_common_cy import b, E
rotor_diameter = 2.0 * rotor_radius


def ainslie_full(double ct, double u0, double distance_parallel, double distance_perpendicular, double i0):
    # centreline = open('centreline.dat', 'w')
    # velocity = open('velocity.dat', 'w')
    cdef int ni, nj, g, j, i
    cdef double k, h, Dmi
    di = 2.0
    dj = distance_parallel
    # ni = int(di * 80)
    # nj = int(dj * 80)
    ni = 100
    nj = 100
    k = dj / float(nj)
    h = di / float(ni)

    nj += 1
    ni += 1
    Dmi = ct - 0.05 - (16.0 * ct - 0.5) * i0 / 10.0
    if Dmi < 0.0:
        Dmi = 0.00000000001

    u = [0.0 for _ in range(ni)]
    v = [0.0 for _ in range(ni)]

    for g in range(ni):
        u[g] = u0 * (1.0 - Dmi * exp(- 3.56 * float(g * h) ** 2.0 / b(Dmi, ct) ** 2.0))
    # print u
    old_u = u
    u_initial = u
    old_v = v
    old2_u = u
    # start = time()
    for j in range(1, nj):
        # start = time()
        A = []
        B = []
        C = []
        R = []

        i = 0

        A.append(- k * E(j * k, old_u[i], (u0 - old_u[i]) / u0, u0, i0, ct))
        B.append(2.0 * (h ** 2.0 * old_u[i] + k * E(j * k, old_u[i], (u0 - old_u[i]) / u0, u0, i0, ct)))
        C.append(- k * E(j * k, old_u[i], (u0 - old_u[i]) / u0, u0, i0, ct))
        R.append(k * E(j * k, old_u[i], (u0 - old_u[i]) / u0, u0, i0, ct) * (2.0 * old_u[i + 1] - 2.0 * old_u[i]) + 2.0 * h ** 2.0 * old_u[i] ** 2.0)

        v[0] = 0.0
        # print time() - start, "loop out"
        for i in range(1, ni):
            # print j, i, j * k, i * h, old_u[i], (u0 - old_u[i]) / u0
            #  Uncomment if v is not neglected. Radial velocity.
            if j == 1:
                v[i] = (i * h) / ((i * h) + h) * (old_v[i - 1] - h / k * (old_u[i] - u_initial[i]))
            elif j > 1:
                v[i] = (i * h) / ((i * h) + h) * (old_v[i - 1] - h / k * (old_u[i] - old2_u[i]))

            A.append(k * (h * E(j * k, old_u[i], (u0 - old_u[i]) / u0, u0, i0, ct) - (i * h) * h * v[i] - 2.0 * (i * h) * E(j * k, old_u[i], (u0 - old_u[i]) / u0, u0, i0, ct)))
            B.append(4.0 * (i * h) * (h ** 2.0 * old_u[i] + k * E(j * k, old_u[i], (u0 - old_u[i]) / u0, u0, i0, ct)))
            C.append(k * ((i * h) * h * v[i] - 2.0 * (i * h) * E(j * k, old_u[i], (u0 - old_u[i]) / u0, u0, i0, ct) - h * E(j * k, old_u[i], (u0 - old_u[i]) / u0, u0, i0, ct)))
            if i < ni - 1:
                R.append(h * k * E(j * k, old_u[i], (u0 - old_u[i]) / u0, u0, i0, ct) * (old_u[i + 1] - old_u[i - 1]) + 2.0 * k * E(j * k, old_u[i], (u0 - old_u[i]) / u0, u0, i0, ct) * (i * h) * (old_u[i + 1] - 2.0 * old_u[i] + old_u[i - 1]) - (i * h) * h * k * old_v[i] * (old_u[i + 1] - old_u[i - 1]) + 4.0 * (i * h) * h ** 2.0 * old_u[i] ** 2.0)
            elif i == ni - 1:
                R.append(h * k * E(j * k, old_u[i], (u0 - old_u[i]) / u0, u0, i0, ct) * (u0 - old_u[i - 1]) + 2.0 * k * E(j * k, old_u[i], (u0 - old_u[i]) / u0, u0, i0, ct) * (i * h) * (u0 - 2.0 * old_u[i] + old_u[i - 1]) - (i * h) * h * k * old_v[i] * (u0 - old_u[i - 1]) + 4.0 * (i * h) * h ** 2.0 * old_u[i] ** 2.0)
        # print time() - start

        C[0] += A[0]
        del A[0]
        R[-1] -= C[-1] * u0
        del C[-1]
        # start3 = time()
        old2_u = old_u
        old_u = thomas(A, B, C, R)
        # print old_u
        old_v = v
        # print time() - start3
    # print time() - star,
    # print 's'

    # Code to calculate the average wake deficit in all the area of the rotor ###############

    # Define function to integrate.

    # p. 77 Adapting and calibration of existing wake models to meet the conditions inside offshore wind farms. For integrand squared momentum deficit.
    # def G(r, theta):
    #     z = sqrt(Y ** 2.0 + r ** 2.0 + 2.0 * Y * r * cos(theta))
    #     gauss = U0 * (1.0 - d1[n - 1] * exp(- 3.56 * (z / b(d1[n - 1])) ** 2.0))
    #     return r * (U0 - gauss) ** 2.0
    #
    # A = pi * 0.5 ** 2.0  ## Unitary diameter in this program.
    # U = U0 - sqrt((1.0 / A) * simpson_integrate2D(G, 0.0, 0.5, 5, 0.0, 2.0 * pi, 10))
    # return 1.0 - old_u[int(round(distance_perpendicular * rotor_diameter, 0))] / u0
    return 1.0 - old_u[int(distance_perpendicular * ni / di)] / u0


# ainslie_full = Memoize(ainslie_full)
    # centreline.close()
    # velocity.close()

if __name__ == '__main__':
#     from ainslie1d import ainslie
#     from jensen import wake_deficit as jensen
#     from larsen import wake_deficit as larsen
#
#     for x in range(1, 560):
#         print ainslie_full(0.79, 8.5, x / 80.0, 0.0, 0.08), ainslie(0.79, 8.5, x / 80.0, 0.0, 0.08), jensen(0.79, x, 0.04, 40.0), larsen(8.5, 0.79, x, 0.0, 0.08)
#         # print jensen(0.79, x, 0.04, 40.0), larsen(8.5, 0.79, x, 0.0, 0.08)
    # print
    #
    # for x in range(20, 70):
    #     print ainslie(0.79, 8.5, x, 0.0, 0.08)
    # print jensen(0.79, 560.0, 0.04, 40.0)
    # print larsen(8.5, 0.79, 560.0, 0.0, 0.08)
    # print ainslie_full(0.28025, -30.7274355682, 2.30063219336, 23.625, 0.11, 0.0537295322098)
    print ainslie_full(0.537295322098, 10.0, 14.0125, 0.3, 0.11)
