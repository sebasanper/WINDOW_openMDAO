from openmdao.api import Group, ExplicitComponent, LinearRunOnce, LinearBlockGS, NewtonSolver, NonlinearBlockGS, \
    LinearBlockJac, IndepVarComp
import numpy as np
from order_layout import OrderLayout
from src.AbsThrustCoefficient.abstract_thrust import ThrustCoefficient
from input_params import max_n_turbines
from distance import DistanceComponent
from windspeed_deficits import SpeedDeficits, CombineSpeed


class WakeModel(Group):
    def __init__(self, fraction_model, deficit_model, merge_model):
        super(WakeModel, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.merge_model = merge_model

    def setup(self):
        self.add_subsystem('linear_solve', LinearSolveWake(self.fraction_model, self.deficit_model, self.merge_model),
                           promotes_inputs=['r', 'original', 'angle', 'n_turbines', 'freestream'])
        self.add_subsystem('combine', CombineSpeed(), promotes_inputs=['n_turbines'], promotes_outputs=['U'])
        for n in range(max_n_turbines):
            self.connect('linear_solve.speed{}.U'.format(n), 'combine.U{}'.format(n))
        self.connect('linear_solve.order_layout.ordered', 'combine.ordered_layout')


class LinearSolveWake(Group):
    def __init__(self, fraction_model, deficit_model, merge_model):
        super(LinearSolveWake, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.merge_model = merge_model

    def setup(self):
        self.add_subsystem('order_layout', OrderLayout(), promotes_inputs=['original', 'angle', 'n_turbines'])

        for n in range(max_n_turbines):
            self.add_subsystem('ct{}'.format(n), ThrustCoefficient(n), promotes_inputs=['n_turbines'])
            self.add_subsystem('deficits{}'.format(n), Wake(self.fraction_model, self.deficit_model, n),
                               promotes_inputs=['angle', 'r', 'n_turbines'])
            self.add_subsystem('merge{}'.format(n), self.merge_model(), promotes_inputs=['n_turbines'])
            self.add_subsystem('speed{}'.format(n), SpeedDeficits(), promotes_inputs=['freestream'])

            self.connect('order_layout.ordered', 'deficits{}.ordered'.format(n))
            self.connect('ct{}.ct'.format(n), 'deficits{}.ct'.format(n))
            self.connect('deficits{}.dU'.format(n), 'merge{}.all_deficits'.format(n))
            self.connect('merge{}.sqrt'.format(n), 'speed{}.dU'.format(n))
            for m in range(max_n_turbines):
                if m > n:
                    self.connect('speed{}.U'.format(n), 'ct{}.U{}'.format(m, n))
        # self.linear_solver = LinearRunOnce()
        # self.nonlinear_solver = NonlinearBlockGS()
        # self.nonlinear_solver.options['maxiter'] = 30


class Wake(Group):
    def __init__(self, fraction_model, deficit_model, number):
        super(Wake, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.number = number

    def setup(self):
        self.add_subsystem('distance', DistanceComponent(self.number),
                           promotes_inputs=['angle', 'ordered', 'n_turbines'])
        self.add_subsystem('total_wake', TotalWake(self.fraction_model, self.deficit_model, self.number),
                           promotes_inputs=['ct', 'angle', 'ordered', 'r', 'n_turbines'], promotes_outputs=['dU'])
        self.connect('distance.dist_down', 'total_wake.downwind_d')
        self.connect('distance.dist_cross', 'total_wake.crosswind_d')


class TotalWake(Group):

    def __init__(self, fraction_model, deficit_model, number):
        super(TotalWake, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.number = number

    def setup(self):
        k = self.add_subsystem('k_indep', IndepVarComp())
        k.add_output('k_jensen', val=0.04)
        self.add_subsystem('fraction', self.fraction_model(self.number),
                           promotes_inputs=['ordered', 'angle', 'n_turbines', 'downwind_d', 'crosswind_d', 'r'])
        self.add_subsystem('deficit', self.deficit_model(),
                           promotes_inputs=['r', 'downwind_d', 'crosswind_d', 'ct', 'n_turbines'],
                           promotes_outputs=['dU'])

        self.connect('fraction.fractions', 'deficit.fractions')
        self.connect('k_indep.k_jensen', 'fraction.k')
        self.connect('k_indep.k_jensen', 'deficit.k')
