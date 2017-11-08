from openmdao.api import Group, ExplicitComponent, LinearRunOnce, LinearBlockGS, NewtonSolver, NonlinearBlockGS, \
    LinearBlockJac, IndepVarComp
import numpy as np
from order_layout import OrderLayout
from input_params import max_n_turbines
from distance import DistanceComponent
from windspeed_deficits import SpeedDeficits, CombineSpeed


class WakeModel(Group):
    def __init__(self, n_cases, fraction_model, deficit_model, merge_model, thrust_model):
        super(WakeModel, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.merge_model = merge_model
        self.n_cases = n_cases
        self.thrust_model = thrust_model

    def setup(self):
        self.add_subsystem('linear_solve', LinearSolveWake(self.n_cases, self.fraction_model, self.deficit_model, self.merge_model, self.thrust_model),
                           promotes_inputs=['turbine_radius', 'original', 'angle', 'n_turbines', 'freestream'])
        self.add_subsystem('combine', CombineSpeed(self.n_cases), promotes_inputs=['n_turbines'], promotes_outputs=['U'])
        for n in range(max_n_turbines):
            self.connect('linear_solve.speed{}.U'.format(n), 'combine.U{}'.format(n))
        self.connect('linear_solve.order_layout.ordered', 'combine.ordered_layout')


class LinearSolveWake(Group):
    def __init__(self, n_cases, fraction_model, deficit_model, merge_model, thrust_model):
        super(LinearSolveWake, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.merge_model = merge_model
        self.n_cases = n_cases
        self.thrust_model = thrust_model

    def setup(self):
        self.add_subsystem('order_layout', OrderLayout(self.n_cases), promotes_inputs=['original', 'angle', 'n_turbines'])

        for n in range(max_n_turbines):
            self.add_subsystem('ct{}'.format(n), self.thrust_model(n, self.n_cases), promotes_inputs=['n_turbines'])
            self.add_subsystem('deficits{}'.format(n), Wake(self.n_cases, self.fraction_model, self.deficit_model, n),
                               promotes_inputs=['angle', 'turbine_radius', 'n_turbines'])
            self.add_subsystem('merge{}'.format(n), self.merge_model(self.n_cases), promotes_inputs=['n_turbines'])
            self.add_subsystem('speed{}'.format(n), SpeedDeficits(self.n_cases), promotes_inputs=['freestream'])

            self.connect('order_layout.ordered', 'deficits{}.ordered'.format(n))
            self.connect('ct{}.ct'.format(n), 'deficits{}.ct'.format(n))
            self.connect('deficits{}.dU'.format(n), 'merge{}.all_deficits'.format(n))
            self.connect('merge{}.dU'.format(n), 'speed{}.dU'.format(n))
            for m in range(max_n_turbines):
                if m > n:
                    self.connect('speed{}.U'.format(n), 'ct{}.U{}'.format(m, n))
            
            if n > 0:
                self.connect('ct{}.ct'.format(n - 1), 'ct{}.prev_ct'.format(n))
        # self.linear_solver = LinearRunOnce()
        # self.nonlinear_solver = NonlinearBlockGS()
        # self.nonlinear_solver.options['maxiter'] = 30


class Wake(Group):
    def __init__(self, n_cases, fraction_model, deficit_model, number):
        super(Wake, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.number = number
        self.n_cases = n_cases

    def setup(self):
        self.add_subsystem('distance', DistanceComponent(self.number, self.n_cases),
                           promotes_inputs=['angle', 'ordered', 'n_turbines'])
        self.add_subsystem('total_wake', TotalWake(self.n_cases, self.fraction_model, self.deficit_model, self.number),
                           promotes_inputs=['ct', 'angle', 'ordered', 'turbine_radius', 'n_turbines'], promotes_outputs=['dU'])
        self.connect('distance.dist_down', 'total_wake.downwind_d')
        self.connect('distance.dist_cross', 'total_wake.crosswind_d')


class TotalWake(Group):

    def __init__(self, n_cases, fraction_model, deficit_model, number):
        super(TotalWake, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.number = number
        self.n_cases = n_cases

    def setup(self):
        k = self.add_subsystem('k_indep', IndepVarComp())
        k.add_output('k_jensen', val=0.04)
        self.add_subsystem('fraction', self.fraction_model(self.number, self.n_cases),
                           promotes_inputs=['ordered', 'angle', 'n_turbines', 'downwind_d', 'crosswind_d', 'turbine_radius'])
        self.add_subsystem('deficit', self.deficit_model(self.n_cases),
                           promotes_inputs=['turbine_radius', 'downwind_d', 'crosswind_d', 'ct', 'n_turbines'],
                           promotes_outputs=['dU'])

        self.connect('fraction.fractions', 'deficit.fractions')
        self.connect('k_indep.k_jensen', 'fraction.k')
        self.connect('k_indep.k_jensen', 'deficit.k')
