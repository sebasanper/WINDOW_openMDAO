from random import randint
from numpy import mean, var
from time import time
from openmdao.api import Problem
from workflow import WorkingGroup
import numpy as np

prob = Problem()
# print clock(), "Before defining model"
prob.model = WorkingGroup()
# print clock(), "Before setup"
prob.setup()

start = time()


def f(x):
    prob['indep2.layout'] = x
    prob.run_model()
    lcoe = prob['lcoe.LCOE'][0]
    return lcoe

def counted(fn):
    def wrapper(*args, **kwargs):
        wrapper.called += 1
        return fn(*args, **kwargs)
    wrapper.called = 0
    wrapper.__name__ = fn.__name__
    return wrapper


def sobol(number):
    start = time()

    # memo = {}
    # @counted
    # def f(x, y, z):
    #     if not (x, y, z) in memo:
    #         memo[(x, y, z)] = fl(x, y, z)
    #     return memo[(x, y, z)]

    # @counted

    m = number
    x = [[] for _ in range(9)]
    for i in range(9):
        x[i] = [[float(randint(1, 1120)), float(randint(1, 1120))] for _ in range(m)]

    Y = [f([x[0][i], x[1][i], x[2][i], x[3][i], x[4][i], x[5][i], x[6][i], x[7][i], x[8][i]]) for i in range(m)]
    # TODO: Monte-Carlo all wrong. Needs to change the input randomly.
    v = var(Y)
    # v1 = var([mean([f(x1[i], x2[o], x3[o]) for o in range(m)]) for i in range(m)])
    v1 = var([mean([f([x[0][o], x[1][i], x[2][i], x[3][i], x[4][i], x[5][i], x[6][i], x[7][i], x[8][i]]) for i in range(m)]) for o in range(m)])
    v2 = var([mean([f([x[0][i], x[1][o], x[2][i], x[3][i], x[4][i], x[5][i], x[6][i], x[7][i], x[8][i]]) for i in range(m)]) for o in range(m)])
    v3 = var([mean([f([x[0][i], x[1][i], x[2][o], x[3][i], x[4][i], x[5][i], x[6][i], x[7][i], x[8][i]]) for i in range(m)]) for o in range(m)])
    v4 = var([mean([f([x[0][i], x[1][i], x[2][i], x[3][o], x[4][i], x[5][i], x[6][i], x[7][i], x[8][i]]) for i in range(m)]) for o in range(m)])
    v5 = var([mean([f([x[0][i], x[1][i], x[2][i], x[3][i], x[4][o], x[5][i], x[6][i], x[7][i], x[8][i]]) for i in range(m)]) for o in range(m)])
    v6 = var([mean([f([x[0][i], x[1][i], x[2][i], x[3][i], x[4][i], x[5][o], x[6][i], x[7][i], x[8][i]]) for i in range(m)]) for o in range(m)])
    v7 = var([mean([f([x[0][i], x[1][i], x[2][i], x[3][i], x[4][i], x[5][i], x[6][o], x[7][i], x[8][i]]) for i in range(m)]) for o in range(m)])
    v8 = var([mean([f([x[0][i], x[1][i], x[2][i], x[3][i], x[4][i], x[5][i], x[6][i], x[7][o], x[8][i]]) for i in range(m)]) for o in range(m)])
    v9 = var([mean([f([x[0][i], x[1][i], x[2][i], x[3][i], x[4][i], x[5][i], x[6][i], x[7][i], x[8][o]]) for i in range(m)]) for o in range(m)])


    # v12 = var([mean([f(x1[i], x2[i], x3[o]) for o in range(m)]) for i in range(m)]) - v1 - v2
    # v13 = var([mean([f(x1[i], x2[o], x3[i]) for o in range(m)]) for i in range(m)]) - v1 - v3
    # v23 = var([mean([f(x1[o], x2[i], x3[i]) for o in range(m)]) for i in range(m)]) - v2 - v3

    t1 = 1.0 - var([mean([f([x[0][o], x[1][i], x[2][i], x[3][i], x[4][i], x[5][i], x[6][i], x[7][i], x[8][i]]) for o in range(m)]) for i in range(m)]) / v
    t2 = 1.0 - var([mean([f([x[0][i], x[1][o], x[2][i], x[3][i], x[4][i], x[5][i], x[6][i], x[7][i], x[8][i]]) for o in range(m)]) for i in range(m)]) / v
    t3 = 1.0 - var([mean([f([x[0][i], x[1][i], x[2][o], x[3][i], x[4][i], x[5][i], x[6][i], x[7][i], x[8][i]]) for o in range(m)]) for i in range(m)]) / v
    t4 = 1.0 - var([mean([f([x[0][i], x[1][i], x[2][i], x[3][o], x[4][i], x[5][i], x[6][i], x[7][i], x[8][i]]) for o in range(m)]) for i in range(m)]) / v
    t5 = 1.0 - var([mean([f([x[0][i], x[1][i], x[2][i], x[3][i], x[4][o], x[5][i], x[6][i], x[7][i], x[8][i]]) for o in range(m)]) for i in range(m)]) / v
    t6 = 1.0 - var([mean([f([x[0][i], x[1][i], x[2][i], x[3][i], x[4][i], x[5][o], x[6][i], x[7][i], x[8][i]]) for o in range(m)]) for i in range(m)]) / v
    t7 = 1.0 - var([mean([f([x[0][i], x[1][i], x[2][i], x[3][i], x[4][i], x[5][i], x[6][o], x[7][i], x[8][i]]) for o in range(m)]) for i in range(m)]) / v
    t8 = 1.0 - var([mean([f([x[0][i], x[1][i], x[2][i], x[3][i], x[4][i], x[5][i], x[6][i], x[7][o], x[8][i]]) for o in range(m)]) for i in range(m)]) / v
    t9 = 1.0 - var([mean([f([x[0][i], x[1][i], x[2][i], x[3][i], x[4][i], x[5][i], x[6][i], x[7][i], x[8][o]]) for o in range(m)]) for i in range(m)]) / v

    print( t1, t2, t3, t1 + t2 + t3)
    #
    s1 = v1 / v
    # print s1
    s2 = v2 / v
    # print s2
    s3 = v3 / v
    # print s3
    # s12 = v12 / v
    # # print s12
    # s13 = v13 / v
    # # print s13
    # s23 = v23 / v
    # print s23
    # print '------sum----------'
    # print s1 + s2 + s3 + s12 + s13 + s23
    # print
    # print '-----------time in seconds--------------'
    # print time() - start
    return s1, s2, s3, s1 + s2 + s3 + s12 + s13 + s23, time() - start#, fl.called, f.called

if __name__ == '__main__':
    print (sobol(2))
    # out = open('sobol.dat', 'a', 5)
    # # out.write('#MCnumber\ts1    \ts2      \ts3      \ts12      \ts13      \ts23      \tsum      \ttime\n')
    # for mc in range(1625, 4000):
    #     a = sobol(mc)
    #     out.write('{8:d}    \t{0:f}\t{1:f}\t{2:f}\t{3:f}\t{4:f}\t{5:f}\t{6:f}\t{7:f}\n'.format(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], mc))
    #     print(str((float(mc) - 1625.0) * 100.0 / (4000.0 - 1625.0)) + ' %\n')
    # out.close()
