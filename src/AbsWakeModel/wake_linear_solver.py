from openmdao.api import Group, ExplicitComponent, LinearRunOnce, LinearBlockGS, NewtonSolver, NonlinearBlockGS, DirectSolver, LinearBlockJac, IndepVarComp
import numpy as np
from order_layout import OrderLayout
from src.AbsThrustCoefficient.abstract_thrust import ThrustCoefficient, FirstThrustCoefficient
from src.AbsWakeModel.AbsWakeMerge.abstract_wake_merging import WakeMergeRSS
from input_params import max_n_turbines
from distance import DistanceComponent
from windspeed_deficits import SpeedDeficits, CombineSpeed


class WakeModel(Group):
    def __init__(self, fraction_model, deficit_model):
        super(WakeModel, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model

    def setup(self):
        self.add_subsystem('linear_solve', LinearSolveWake(self.fraction_model, self.deficit_model), promotes_inputs=['r', 'original', 'angle', 'n_turbines', 'freestream'])
        self.add_subsystem('combine', CombineSpeed(), promotes_inputs=['n_turbines'], promotes_outputs=['U'])
        for n in range(max_n_turbines):
            self.connect('linear_solve.speed{}.U'.format(n), 'combine.U{}'.format(n))
        self.connect('linear_solve.order_layout.ordered', 'combine.ordered_layout')


class LinearSolveWake(Group):
    def __init__(self, fraction_model, deficit_model):
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
                    self.connect('speed{}.U'.format(n), 'ct{}.U{}'.format(m, n))
        # self.linear_solver = LinearRunOnce()
        # self.nonlinear_solver = NonlinearBlockGS()


class Wake(Group):
    def __init__(self, fraction_model, deficit_model, number):
        super(Wake, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.number = number

    def setup(self):
        self.add_subsystem('distance', DistanceComponent(self.number), promotes_inputs=['angle', 'layout', 'n_turbines'])
        self.add_subsystem('total_wake', TotalWake(self.fraction_model, self.deficit_model, self.number), promotes_inputs=['ct', 'angle', 'layout', 'r', 'n_turbines'], promotes_outputs=['dU'])
        self.connect('distance.dist_down', 'total_wake.downwind_d')
        self.connect('distance.dist_cross', 'total_wake.crosswind_d')


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
