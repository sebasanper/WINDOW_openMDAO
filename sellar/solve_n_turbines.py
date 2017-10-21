from openmdao.api import Problem, Group, ExplicitComponent, view_model, IndepVarComp, LinearRunOnce, LinearBlockGS, NewtonSolver, NonlinearBlockGS, DirectSolver, LinearBlockJac
from numpy import sqrt, deg2rad, tan
import numpy as np
from jensen import determine_if_in_wake, wake_radius, wake_deficit1

u_far = 8.5


def ct(v):
    if v < 4.0:
        return np.array([0.1])
    elif v <= 25.0:
        return 7.3139922126945e-7 * v ** 6.0 - 6.68905596915255e-5 * v ** 5.0 + 2.3937885e-3 * v ** 4.0 - 0.0420283143 * v ** 3.0 + 0.3716111285 * v ** 2.0 - 1.5686969749 * v + 3.2991094727
    else:
        return np.array([0.1])


def speed(deficit):
    return u_far * (1.0 - deficit)


def distance(t1, t2, angle):
    wind_direction = deg2rad(angle)
    distance_to_centre = abs(- tan(wind_direction) * t2[1] + t2[2] + tan(wind_direction) * t1[1] - t1[2]) / sqrt(
        1.0 + tan(wind_direction) ** 2.0)
    # Coordinates of the intersection between closest path from turbine in wake to centreline.
    x_int = (t2[1] + tan(wind_direction) * t2[2] + tan(wind_direction) * (tan(wind_direction) * t1[1] - t1[2])) / \
            (tan(wind_direction) ** 2.0 + 1.0)
    y_int = (- tan(wind_direction) * (- t2[1] - tan(wind_direction) * t2[2]) - tan(
        wind_direction) * t1[1] + t1[2]) / (tan(wind_direction) ** 2.0 + 1.0)
    # Distance from intersection point to turbine
    distance_to_turbine = sqrt((x_int - t1[1]) ** 2.0 + (y_int - t1[2]) ** 2.0)
    return distance_to_turbine, distance_to_centre


n_turbines = 8


class ThrustCoefficient(ExplicitComponent):

    def __init__(self, number):
        super(ThrustCoefficient, self).__init__()
        self.number = number

    def setup(self):

        for n in range(n_turbines):
            if n != self.number:
                self.add_input('U{}'.format(n), val=u_far)

        self.add_output('ct', shape=n_turbines - 1, val=0.79)

        # Finite difference all partials.
        # self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):
        c_t = np.array([])
        for n in range(n_turbines):
            if n != self.number:
                c_t = np.append(c_t, [ct(inputs['U{}'.format(n)])])
        outputs['ct'] = c_t


class DistanceComponent(ExplicitComponent):
    def __init__(self, number):
        super(DistanceComponent, self).__init__()
        self.number = number

    def setup(self):
        self.add_input('angle', val=90.0)
        self.add_input('layout', shape=(n_turbines, 3))
        self.add_output('dist_down', shape=n_turbines - 1, val=500.0)
        self.add_output('dist_cross', shape=n_turbines - 1, val=300.0)

        # Finite difference all partials.
        # self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):
        layout = inputs['layout']
        angle = inputs['angle']
        d_down = np.array([])
        d_cross = np.array([])

        for n in range(len(layout)):
            if n != self.number:
                d_down1, d_cross1 = distance(layout[self.number], layout[n], angle)
                d_cross = np.append(d_cross, [d_cross1])
                d_down = np.append(d_down, [d_down1])
                # print n, self.number, layout[self.number], layout[n], angle, d_down1, d_cross1
        outputs['dist_down'] = d_down
        outputs['dist_cross'] = d_cross


class DetermineIfInWakeJensen(ExplicitComponent):
    def __init__(self, number):
        super(DetermineIfInWakeJensen, self).__init__()
        self.number = number

    def setup(self):
        self.add_input('layout', shape=(n_turbines, 3))
        self.add_input('angle', val=90.0)
        self.add_input('downwind_d', shape=n_turbines - 1)
        self.add_input('crosswind_d', shape=n_turbines - 1)

        self.add_output('fraction', shape=n_turbines - 1)

    def compute(self, inputs, outputs):
        layout = inputs['layout']
        angle = inputs['angle']
        downwind_d = inputs['downwind_d']
        crosswind_d = inputs['crosswind_d']
        fractions = np.array([])
        i = 0
        for n in range(len(layout)):
            if n != self.number:
                fractions = np.append(fractions, determine_if_in_wake(layout[self.number][1], layout[self.number][2], layout[n][1], layout[n][2], angle, downwind_d[i], crosswind_d[i]))
                # print self.number, n, layout[self.number], layout[n], angle, i, downwind_d, crosswind_d, fractions
                i += 1
        outputs['fraction'] = fractions


class WakeDeficit(ExplicitComponent):
    
    def __init__(self):
        super(WakeDeficit, self).__init__()
        self.wake_deficit = None
    
    def setup(self):
        self.add_input('k', val=0.04)
        self.add_input('r', val=40.0)
        self.add_input('dist_down', shape=n_turbines - 1, val=560.0)
        self.add_input('dist_cross', shape=n_turbines - 1, val=0.0)
        self.add_input('ct', shape=n_turbines - 1, val=0.79)
        self.add_input('fraction', shape=n_turbines - 1)
        self.add_output('dU', shape=n_turbines - 1, val=0.3)

    def compute(self, inputs, outputs):
        k = inputs['k']
        r = inputs['r']
        d_down = inputs['dist_down']
        d_cross = inputs['dist_cross']
        c_t = inputs['ct']
        fraction = inputs['fraction']
        deficits = np.array([])
        for ind in range(len(d_down)):
            if fraction[ind] > 0.0:
                # print "called"
                deficits = np.append(deficits, [fraction[ind] * self.wake_deficit(d_down[ind], d_cross[ind], c_t[ind], k, r)])
            else:
                deficits = np.append(deficits, [0.0])
        outputs['dU'] = deficits


class Wake(Group):
    def __init__(self, number):
        super(Wake, self).__init__()
        self.number = number

    def setup(self):
        self.add_subsystem('distance', DistanceComponent(self.number), promotes_inputs=['angle', 'layout'])
        self.add_subsystem('determine', DetermineIfInWakeJensen(self.number), promotes_inputs=['angle', 'layout'])
        self.add_subsystem('deficit', JensenWakeDeficit(), promotes_inputs=['ct'], promotes_outputs=['dU'])
        self.connect('distance.dist_down', 'determine.downwind_d')
        self.connect('distance.dist_cross', 'determine.crosswind_d')
        self.connect('distance.dist_down', 'deficit.dist_down')
        self.connect('distance.dist_cross', 'deficit.dist_cross')
        self.connect('determine.fraction', 'deficit.fraction')



class JensenWakeDeficit(WakeDeficit):
    def __init__(self):
        super(JensenWakeDeficit, self).__init__()
        self.wake_deficit = wake_deficit1


class SumSquares(ExplicitComponent):
    def setup(self):
        self.add_input('all_deficits', shape=n_turbines - 1)
        self.add_output('sos')

    def compute(self, inputs, outputs):
        defs = inputs['all_deficits']
        summation = 0.0
        for item in defs:
            summation += item ** 2.0
        outputs['sos'] = summation


class Sqrt(ExplicitComponent):

    def setup(self):
        self.add_input('summation')
        self.add_output('sqrt')

    def compute(self, inputs, outputs):
        outputs['sqrt'] = sqrt(inputs['summation'])


class SpeedDeficits(ExplicitComponent):

    def setup(self):
        self.add_input('dU', val=0.5)
        self.add_output('U', val=8.0)

    def compute(self, inputs, outputs):
        dU = inputs['dU']
        outputs['U'] = u_far * (1.0 - dU)


class WakeMergeRSS(Group):
    def setup(self):
        self.add_subsystem('sum', SumSquares(), promotes_inputs=['all_deficits'])
        self.add_subsystem('sqrt', Sqrt(), promotes_outputs=['sqrt'])
        self.connect('sum.sos', 'sqrt.summation')


class WakeModel(Group):

    def setup(self):

        for n in range(n_turbines):
            self.add_subsystem('ct{}'.format(n), ThrustCoefficient(n))
            self.add_subsystem('deficits{}'.format(n), Wake(n), promotes_inputs=['layout', 'angle'])
            self.add_subsystem('merge{}'.format(n), WakeMergeRSS())
            self.add_subsystem('speed{}'.format(n), SpeedDeficits())
            self.connect('ct{}.ct'.format(n), 'deficits{}.ct'.format(n))
            self.connect('deficits{}.dU'.format(n), 'merge{}.all_deficits'.format(n))
            self.connect('merge{}.sqrt'.format(n), 'speed{}.dU'.format(n), )
            for m in range(n_turbines):
                if m != n:
                    self.connect('speed{}.U'.format(n), 'ct{}.U{}'.format(m, n))
        self.linear_solver = LinearRunOnce()
        # self.nonlinear_solver = NonlinearBlockGS()
        # self.nonlinear_solver.options['maxiter'] = 300

from order_layout import order
class OrderLayout(ExplicitComponent):
    def setup(self):
        self.add_input('original', shape=(n_turbines, 3))
        self.add_input('angle', val=1.0)
        self.add_output('ordered', shape=(n_turbines, 3))

    def compute(self, inputs, outputs):
        original = inputs['original']
        angle = inputs['angle']

        outputs['ordered'] = order(original, angle)


class WorkingGroup(Group):
    def setup(self):
        indep2 = self.add_subsystem('indep2', IndepVarComp())
        indep2.add_output('layout', val=read_layout('horns_rev9.dat'))
        # indep2.add_output('layout', val=np.array([[0, 0.0, 0.0], [1, 560.0, 560.0], [2, 1120.0, 1120.0], [3, 1120.0, 0.0], [4, 0.0, 1120.0]]))
        indep2.add_output('angle', val=0.0)
        self.add_subsystem('order', OrderLayout())
        self.add_subsystem('wakemodel', WakeModel())
        self.connect('indep2.layout', 'order.original')
        self.connect('indep2.angle', 'order.angle')
        self.connect('order.ordered', 'wakemodel.layout')
        self.connect('indep2.angle', 'wakemodel.angle')

def read_layout(layout_file):

    layout_file = open(layout_file, 'r')
    layout = []
    i = 0
    for line in layout_file:
        columns = line.split()
        layout.append([i, float(columns[0]), float(columns[1])])
        i += 1

    return np.array(layout)

if __name__ == '__main__':
    from time import time
    prob = Problem()
    prob.model = WorkingGroup()
    prob.setup()
    # view_model(prob)
    prob['indep2.angle'] = 276.0
    start = time()
    prob.run_model()
    print time() - start, "seconds"
    prob.model.list_outputs()

    # # prob2 = Problem()
    # # prob2.model = WorkingGroup()
    # # prob2.setup()
    # # # view_model(prob)
    # # prob2['indep2.angle'] = 90.0
    # # prob2.run_model()

    # print prob['order.ordered']
    # print
    # # indices = [i[0] for i in prob['order.ordered']]
    # results = prob['order.ordered'].tolist()
    # indices = [i[0] for i in results]
    # # results.sort()
    # print results
    # print
    # print indices
    # final = [[indices[n], prob['wakemodel.speed{}.U'.format(int(n))][0]] for n in range(len(indices))]
    # print final
    # final = sorted(final)
    # print final
    # for n in range(79):
    #     # print(prob['wakemodel.speed{}.U'.format(int(n))], prob['order.ordered'][int(n)])
    #     print(final[n][1])

    #     print(prob2['wakemodel.speed{}.U'.format(n)])
    # with open("angle_speedhorns0.dat", 'w') as out:
    #     start= time()
    #     for ang in range(360):
    #         prob['indep2.angle'] = ang
    #         prob.run_model()
    #         indices = [i[0] for i in prob['order.ordered']]
    #         final = [[indices[n], prob['wakemodel.speed{}.U'.format(int(n))][0]] for n in range(len(indices))]
    #         final =sorted(final)
    #         out.write('{}'.format(ang))
    #         out.write(' {}'.format(final[35][1]))
    #         out.write('\n')
    #     print time() - start, "seconds"
