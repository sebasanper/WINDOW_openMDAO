from math import pi, acos, sin, sqrt

__author__ = 'Sebastian Sanchez Perez Moreno' \
             's.sanchezperezmoreno@tudelft.nl'


class AreaWan:
    def __init__(self, r1, r2, d):
        self.r1 = r1
        self.r2 = r2
        self.d = d

    def area(self):
        r1 = self.r1
        r2 = self.r2
        d = self.d
        if d <= abs(r2 - r1):
            return 1.0
        elif abs(r2 - r1) < d < abs(r1 + r2):
            a1 = 2.0 * acos((r1 ** 2 + d**2 - r2 ** 2) / (2.0 * r1 * d))
            a2 = 2.0 * acos((r2 ** 2 + d**2 - r1 ** 2) / (2.0 * r2 * d))
            return (0.5 * r1 ** 2. * (a1 - sin(a1)) + 0.5 * r2 ** 2 * (a2 - sin(a2))) / (pi * r1 ** 2)
        else:
            return 0.0


class AreaReal:
    def __init__(self, r, R, d):
        self.r = r
        self.R = R
        self.d = d

    def area(self):
        r = self.r
        R = self.R
        d = self.d
        if d <= abs(r - R):
            return 1.0
        elif abs(r - R) < d < abs(r + R):
            return (r ** 2 * acos((d ** 2 + r ** 2 - R ** 2) / (2.0 * d * r)) + R ** 2 * acos((d ** 2 + R ** 2 - r ** 2) / (2.0 * d * R)) - 0.5 * sqrt((- d + r + R) * (d + r - R) * (d - r + R) * (d + r + R))) / (pi * r ** 2)
        else:
            return 0.0


if __name__ == '__main__':
    file1 = open('areas_overlap.dat', 'w')
    for i in range(1, 300):
        AreaWan1 = AreaWan(1.0, 2.0, 0.01 * i)
        AreaReal1 = AreaReal(1.0, 2.0, 0.01 * i)
        file1.write('{0:f}\t{1:f}\t{1:f}\n'.format(0.01 * i, AreaWan1.area(), AreaReal1.area()))
    file1.close()
