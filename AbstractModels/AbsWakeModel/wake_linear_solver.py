from openmdao.api import Group, ExplicitComponent, LinearRunOnce, LinearBlockGS, NewtonSolver, NonlinearBlockGS, DirectSolver, LinearBlockJac, IndepVarComp
from numpy import sqrt, deg2rad, tan
import numpy as np
from AbstractModels.AbsWakeModel.order_layout import OrderLayout
from AbstractModels.AbsThrustCoefficient.abstract_thrust import ThrustCoefficient, FirstThrustCoefficient
from AbstractModels.AbsWakeModel.WakeMerge.abstract_wake_merging import WakeMergeRSS
from input_params import max_n_turbines


def distance(t1, t2, angle):
    wind_direction = deg2rad(- angle + 90.0)
    distance_to_centre = abs(- tan(wind_direction) * t2[1] + t2[2] + tan(wind_direction) * t1[1] - t1[2]) / sqrt(
        1.0 + tan(wind_direction) ** 2.0)
    # Coordinates of the intersection between closest path from turbine in wake to centreline.
    x_int = (t2[1] + tan(wind_direction) * t2[2] + tan(wind_direction) * (tan(wind_direction) * t1[1] - t1[2])) / \
            (tan(wind_direction) ** 2.0 + 1.0)
    y_int = (- tan(wind_direction) * (- t2[1] - tan(wind_direction) * t2[2]) - tan(
        wind_direction) * t1[1] + t1[2]) / (tan(wind_direction) ** 2.0 + 1.0)
    # Distance from intersection point to turbine
    distance_to_turbine = sqrt((x_int - t1[1]) ** 2.0 + (y_int - t1[2]) ** 2.0)
    return np.array(distance_to_turbine), np.array(distance_to_centre)


class DistanceComponent(ExplicitComponent):
    def __init__(self, number):
        super(DistanceComponent, self).__init__()
        self.number = number

    def setup(self):
        self.add_input('angle', val=90.0)
        self.add_input('layout', shape=(max_n_turbines, 3))
        self.add_input('n_turbines', val=1)
        self.add_output('dist_down', shape=max_n_turbines - 1, val=500.0)
        self.add_output('dist_cross', shape=max_n_turbines - 1, val=300.0)

        # Finite difference all partials.
        # self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):
        #print "3 Distance"
        n_turbines = int(inputs['n_turbines'])
        layout = inputs['layout']
        # print layout, "Input"
        angle = inputs['angle']
        d_down = np.array([])
        d_cross = np.array([])
        for n in range(n_turbines):
            if n != self.number and self.number < n_turbines:
                d_down1, d_cross1 = distance(layout[self.number], layout[n], angle)
                d_cross = np.append(d_cross, [d_cross1])
                d_down = np.append(d_down, [d_down1])
        lendif = max_n_turbines - len(d_cross) - 1
        outputs['dist_down'] = np.concatenate((d_down, [0 for n in range(lendif)]))
        #print outputs['dist_down'], "Output1"
        outputs['dist_cross'] = np.concatenate((d_cross, [0 for n in range(lendif)]))
        #print outputs['dist_cross'], "Output2"


class TotalWake(Group):

    def __init__(self, fraction_model, deficit_model, number):
        super(TotalWake, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.number = number

    def setup(self):
        self.add_subsystem('fraction', self.fraction_model(self.number), promotes_inputs=['layout', 'angle', 'n_turbines', 'downwind_d', 'crosswind_d', 'r'])
        self.add_subsystem('deficit', self.deficit_model(), promotes_inputs=['r', 'downwind_d', 'crosswind_d', 'ct', 'n_turbines'], promotes_outputs=['dU'])

        self.connect('fraction.fractions', 'deficit.fractions')


class Wake(Group):
    def __init__(self, number):
        super(Wake, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.number = number

    def setup(self):
        self.add_subsystem('distance', DistanceComponent(self.number), promotes_inputs=['angle', 'layout', 'n_turbines'])
        self.add_subsystem('total_wake', TotalWake(self.fraction_model, self.deficit_model, self.number), promotes_inputs=['ct', 'angle', 'layout', 'r', 'n_turbines'], promotes_outputs=['dU'])
        self.connect('distance.dist_down', 'total_wake.downwind_d')
        self.connect('distance.dist_cross', 'total_wake.crosswind_d')


class SpeedDeficits(ExplicitComponent):

    def setup(self):
        self.add_input('dU', val=0.5)
        self.add_input('freestream', val=0.5)
        self.add_output('U', val=2.5)

    def compute(self, inputs, outputs):

        #print "8 Speed"
        dU = inputs['dU']
        freestream = inputs['freestream']
        #print dU, 'Input dU'
        outputs['U'] = np.array(freestream * (1.0 - dU))
        #print outputs['U'], "Output U"


class LinearSolveWake(Group):
    def __init__(self, number):
        super(LinearSolveWake, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model

    def setup(self):
        freestream = self.add_subsystem('freestream', IndepVarComp())
        freestream.add_output('freestream', val=8.5)
        self.add_subsystem('order_layout', OrderLayout(), promotes_inputs=['original', 'angle', 'n_turbines'])

        for n in range(max_n_turbines):
            self.add_subsystem('ct{}'.format(n), ThrustCoefficient(n), promotes_inputs=['n_turbines'])
            self.add_subsystem('deficits{}'.format(n), Wake(self.fraction_model, self.deficit_model, n), promotes_inputs=['angle', 'r', 'n_turbines'])
            self.add_subsystem('merge{}'.format(n), WakeMergeRSS(), promotes_inputs=['n_turbines'])
            self.add_subsystem('speed{}'.format(n), SpeedDeficits(), promotes_inputs=['freestream'])

            self.connect('order_layout.ordered', 'deficits{}.layout'.format(n))
            self.connect('ct{}.ct'.format(n), 'deficits{}.ct'.format(n))
            self.connect('deficits{}.dU'.format(n), 'merge{}.all_deficits'.format(n))
            self.connect('merge{}.sqrt'.format(n), 'speed{}.dU'.format(n))
            for m in range(max_n_turbines):
                if m > n:
                    # self.connect('freestream.freestream', 'ct{}.U{}'.format(m, n))
                    self.connect('speed{}.U'.format(n), 'ct{}.U{}'.format(m, n))
        # self.linear_solver = LinearRunOnce()
        # self.nonlinear_solver = NonlinearBlockGS()
        # self.nonlinear_solver.options['maxiter'] = 30


class WakeModel(Group):
    def __init__(self, number):
        super(WakeModel, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model

    def setup(self):
        self.add_subsystem('linear_solve', LinearSolveWake(self.fraction_model, self.deficit_model), promotes_inputs=['r', 'original', 'angle', 'n_turbines', 'freestream'])
        self.add_subsystem('combine', CombineSpeed(), promotes_inputs=['n_turbines'], promotes_outputs=['U'])
        for n in range(max_n_turbines):
            self.connect('linear_solve.speed{}.U'.format(n), 'combine.U{}'.format(n))
        self.connect('linear_solve.order_layout.ordered', 'combine.ordered_layout')


class CombineSpeed(ExplicitComponent):

    def setup(self):

        for n in range(max_n_turbines):
            self.add_input('U{}'.format(n), val=8.5)
        self.add_input('ordered_layout', shape=(max_n_turbines, 3))
        self.add_input('n_turbines', val=1)

        self.add_output('U', shape=max_n_turbines)

    def compute(self, inputs, outputs):
        n_turbines = int(inputs['n_turbines'])
        ordered_layout = inputs['ordered_layout'][:n_turbines].tolist()
        # print ordered_layout
        indices = [i[0] for i in ordered_layout]
        # print indices
        # print inputs['U0'], inputs['U1'], inputs['U2']
        final = [[indices[n], inputs['U{}'.format(int(n))][0]] for n in range(len(indices))]
        # print final
        array_speeds = [speed[1] for speed in sorted(final)]
        # print array_speeds
        lendif = max_n_turbines - len(array_speeds)
        if lendif > 0:
            array_speeds = np.concatenate((array_speeds, [0 for n in range(lendif)]))
        outputs['U'] = np.array(array_speeds)
        #print outputs['U'], "Combined Wind Speeds U"
if __name__ == '__main__':
    pass