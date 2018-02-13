from numpy import exp
from ainslie_common import b, E
from WINDOW_openMDAO.input_params import rotor_radius
from memoize import Memoize
D = rotor_radius * 2.0


def ainslie(Ct, u0, distance_parallel, distance_perpendicular, I0):
    # centreline = open('centreline.dat', 'w')
    # velocity = open('velocity.dat', 'w')
    h = 0.007
    L = distance_parallel
    n = int(L / h) + 1
    Uc1 = [0.0 for _ in range(n)]
    d1 = [0.0 for _ in range(n)]
    U0 = u0
    # dr = 0.1
    Y = distance_perpendicular
    i0 = I0
    ct = Ct
    # m = int(Y / dr)

    Dmi = ct - 0.05 - (16.0 * ct - 0.5) * i0 / 10.0
    if Dmi < 0:
        Dmi = 0.0000000001

    Uc1[0] = U0 * (1.0 - Dmi)  # Boundary condition at x = 2.0
    d1[0] = Dmi

    for i in range(1, n):  # For all positions in the wake centreline direction. Recursive. Whole grid
        Uc1[i] = Uc1[i - 1] + (h * 16.0 * E(i * h, Uc1[i - 1], d1[i - 1], U0, I0, Ct) * (Uc1[i - 1] ** 3.0 - U0 * Uc1[i - 1] ** 2.0 - Uc1[i - 1] * U0 ** 2.0 + U0 ** 3.0) / (Uc1[i - 1] * Ct * U0 ** 2.0))
        d1[i] = 1.0 - Uc1[i] / U0

    # Code to calculate wake deficit at a specific point instead of the whole grid. Namely, the rotor's centrepoint.
    answer = d1[-1] * exp(- 3.56 * (Y / b(d1[-1], ct)) ** 2.0)  # * (1.0 + 7.12 * (0.07 * distance_perpendicular b(d1[-1], ct))) ** (- 0.5)

    return answer


# ainslie = Memoize(ainslie)
    # Code to calculate average wake deficit in all area of the rotor ###############

    # Define function to integrate.

    # p. 77 Adapting and calibration of existing wake models to meet the conditions inside offshore wind farms. For integrand squared momentum deficit.
    # def G(r, theta):
    #     z = sqrt(Y ** 2.0 + r ** 2.0 + 2.0 * Y * r * cos(theta))
    #     gauss = U0 * (1.0 - d1[n - 1] * exp(- 3.56 * (z / b(d1[n - 1])) ** 2.0))
    #     return r * (U0 - gauss) ** 2.0
    #
    # A = pi * 0.5 ** 2.0  ## Unitary diameter in this program.
    # U = U0 - sqrt((1.0 / A) * simpson_integrate2D(G, 0.0, 0.5, 5, 0.0, 2.0 * pi, 10))

    # return 1.0 - U / U0

if __name__ == '__main__':
    pass
    # from ainslie2d import ainslie_full
    # from jensen import wake_deficit
    # from larsen import wake_deficit as larsen
    # for i in range(1, 560):
    #     print ainslie(0.79, 8.5, i/80.0, 0.0, 0.08), ainslie_full(0.79, 8.5, i/80.0, 0.0, 0.08), larsen(8.5, 0.79, i, 0.0, 0.08), wake_deficit(0.79, i, 0.04, 40.0)

