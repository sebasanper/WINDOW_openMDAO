from openmdao.api import Group, ExplicitComponent, LinearRunOnce, LinearBlockGS, NewtonSolver, NonlinearBlockGS, DirectSolver, LinearBlockJac
from numpy import sqrt, deg2rad, tan
import numpy as np
from jensen import determine_if_in_wake, wake_radius, wake_deficit1
from order_layout import order
from ThrustCoefficient.abstract_thrust import ThrustCoefficient
from WakeModel.WakeMerge.abstract_wake_merging import WakeMergeRSS
from input_params import u_far, n_turbines


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
        self.add_input('k', val=0.04)
        self.add_input('r', val=40.0)
        
        self.add_output('fraction', shape=n_turbines - 1)

    def compute(self, inputs, outputs):
        layout = inputs['layout']
        angle = inputs['angle']
        downwind_d = inputs['downwind_d']
        crosswind_d = inputs['crosswind_d']
        fractions = np.array([])
        k = inputs['k']
        r = inputs['r']
        i = 0
        for n in range(len(layout)):
            if n != self.number:
                fractions = np.append(fractions, determine_if_in_wake(layout[self.number][1], layout[self.number][2], layout[n][1], layout[n][2], angle, downwind_d[i], crosswind_d[i], r, k))
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
        self.add_subsystem('determine', DetermineIfInWakeJensen(self.number), promotes_inputs=['angle', 'layout', 'r', 'k'])
        self.add_subsystem('deficit', JensenWakeDeficit(), promotes_inputs=['ct', 'r', 'k'], promotes_outputs=['dU'])
        self.connect('distance.dist_down', 'determine.downwind_d')
        self.connect('distance.dist_cross', 'determine.crosswind_d')
        self.connect('distance.dist_down', 'deficit.dist_down')
        self.connect('distance.dist_cross', 'deficit.dist_cross')
        self.connect('determine.fraction', 'deficit.fraction')



class JensenWakeDeficit(WakeDeficit):
    def __init__(self):
        super(JensenWakeDeficit, self).__init__()
        self.wake_deficit = wake_deficit1


class SpeedDeficits(ExplicitComponent):

    def setup(self):
        self.add_input('dU', val=0.5)
        self.add_output('U', val=8.0)

    def compute(self, inputs, outputs):
        dU = inputs['dU']
        outputs['U'] = u_far * (1.0 - dU)


class LinearSolveWake(Group):

    def setup(self):
        self.add_subsystem('order_layout', OrderLayout(), promotes_inputs=['original', 'angle'])
        for n in range(n_turbines):
            self.add_subsystem('ct{}'.format(n), ThrustCoefficient(n))
            self.add_subsystem('deficits{}'.format(n), Wake(n), promotes_inputs=['angle', 'r', 'k'])
            self.add_subsystem('merge{}'.format(n), WakeMergeRSS())
            self.add_subsystem('speed{}'.format(n), SpeedDeficits())
            self.connect('ct{}.ct'.format(n), 'deficits{}.ct'.format(n))
            self.connect('order_layout.ordered', 'deficits{}.layout'.format(n))
            self.connect('deficits{}.dU'.format(n), 'merge{}.all_deficits'.format(n))
            self.connect('merge{}.sqrt'.format(n), 'speed{}.dU'.format(n), )
            for m in range(n_turbines):
                if m != n:
                    self.connect('speed{}.U'.format(n), 'ct{}.U{}'.format(m, n))
        self.linear_solver = LinearRunOnce()


class WakeModel(Group):

    def setup(self):
        self.add_subsystem('linear_solve', LinearSolveWake(), promotes_inputs=['r', 'k', 'original', 'angle'])
        self.add_subsystem('combine', CombineSpeed(), promotes_outputs=['U'])
        for n in range(n_turbines):
            self.connect('linear_solve.speed{}.U'.format(n), 'combine.U{}'.format(n))
        self.connect('linear_solve.order_layout.ordered', 'combine.ordered_layout')


class OrderLayout(ExplicitComponent):

    def setup(self):
        self.add_input('original', shape=(n_turbines, 3))
        self.add_input('angle', val=1.0)
        self.add_output('ordered', shape=(n_turbines, 3))

    def compute(self, inputs, outputs):
        original = inputs['original']
        angle = inputs['angle']

        outputs['ordered'] = order(original, angle)


class CombineSpeed(ExplicitComponent):

    def setup(self):

        for n in range(n_turbines):
            self.add_input('U{}'.format(n), val=8.5)
        self.add_input('ordered_layout', shape=(n_turbines, 3))


        self.add_output('U', shape=n_turbines)

    def compute(self, inputs, outputs):
        results = inputs['ordered_layout'].tolist()
        print results
        indices = [i[0] for i in results]
        print indices
        final = [[indices[n], inputs['U{}'.format(int(n))][0]] for n in range(len(indices))]
        print final
        array_speeds = [speed[1] for speed in sorted(final)]
        print array_speeds
        outputs['U'] = np.array(array_speeds)
