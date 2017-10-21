from numpy import pi, arccos, sin, sqrt

__author__ = 'Sebastian Sanchez Perez Moreno' \
             's.sanchezperezmoreno@tudelft.nl'

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
            return (r ** 2 * arccos((d ** 2 + r ** 2 - R ** 2) / (2.0 * d * r)) + R ** 2 * arccos((d ** 2 + R ** 2 - r ** 2) / (2.0 * d * R)) - 0.5 * sqrt((- d + r + R) * (d + r - R) * (d - r + R) * (d + r + R))) / (pi * r ** 2)
        else:
            return 0.0


if __name__ == '__main__':
    file1 = open('areas_overlap.dat', 'w')
    for i in range(1, 300):
        AreaWan1 = AreaWan(1.0, 2.0, 0.01 * i)
        AreaReal1 = AreaReal(1.0, 2.0, 0.01 * i)
        file1.write('{0:f}\t{1:f}\t{1:f}\n'.format(0.01 * i, AreaWan1.area(), AreaReal1.area()))
    file1.close()
