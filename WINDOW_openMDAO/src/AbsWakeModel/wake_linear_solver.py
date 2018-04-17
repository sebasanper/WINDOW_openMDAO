from openmdao.api import Group, ExplicitComponent, LinearRunOnce, LinearBlockGS, NewtonSolver, NonlinearBlockGS, \
    LinearBlockJac, IndepVarComp
import numpy as np
from order_layout import OrderLayout
from WINDOW_openMDAO.input_params import max_n_turbines
from distance import DistanceComponent
from windspeed_deficits import SpeedDeficits, CombineOutputs


class WakeModel(Group):
    def __init__(self, n_cases, fraction_model, deficit_model, merge_model, turbine_model, power_table, ct_table):
        super(WakeModel, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.merge_model = merge_model
        self.turbine_model = turbine_model
        self.n_cases = n_cases
        self.power_table = power_table
        self.ct_table = ct_table

    def setup(self):
        self.add_subsystem('linear_solve', LinearSolveWake(self.n_cases, self.fraction_model, self.deficit_model, self.merge_model, self.turbine_model, self.power_table, self.ct_table),
                           promotes_inputs=['turbine_radius', 'original', 'angle', 'n_turbines', 'freestream'])
        self.add_subsystem('combine', CombineOutputs(self.n_cases), promotes_inputs=['n_turbines'], promotes_outputs=['p'])
        for n in range(max_n_turbines + 1):
            self.connect('linear_solve.turbine{}.power'.format(n), 'combine.power{}'.format(n))
            self.connect('linear_solve.turbine{}.ct'.format(n), 'combine.ct{}'.format(n))
        self.connect('linear_solve.order_layout.ordered', 'combine.ordered_layout')


class LinearSolveWake(Group):
    def __init__(self, n_cases, fraction_model, deficit_model, merge_model, turbine_model, power_table, ct_table):
        super(LinearSolveWake, self).__init__()
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.merge_model = merge_model
        self.turbine_model = turbine_model
        self.n_cases = n_cases
        self.power_table = power_table
        self.ct_table = ct_table

    def setup(self):
        self.add_subsystem('order_layout', OrderLayout(self.n_cases), promotes_inputs=['original', 'angle', 'n_turbines'])

        for n in range(max_n_turbines):
            self.add_subsystem('turbine{}'.format(n), self.turbine_model(n, self.n_cases, self.power_table, self.ct_table), promotes_inputs=['n_turbines'])
            self.add_subsystem('deficits{}'.format(n), Wake(self.n_cases, self.fraction_model, self.deficit_model, n),
                               promotes_inputs=['angle', 'turbine_radius', 'n_turbines'])
            self.add_subsystem('merge{}'.format(n), self.merge_model(self.n_cases), promotes_inputs=['n_turbines'])
            self.add_subsystem('speed{}'.format(n), SpeedDeficits(self.n_cases), promotes_inputs=['freestream'])

        for n in range(max_n_turbines):
            self.connect('order_layout.ordered', 'deficits{}.ordered'.format(n))
            self.connect('turbine{}.ct'.format(n), 'deficits{}.ct'.format(n))
            self.connect('deficits{}.dU'.format(n), 'merge{}.all_deficits'.format(n))
            self.connect('merge{}.dU'.format(n), 'speed{}.dU'.format(n))
            for m in range(n + 1, max_n_turbines):
                self.connect('speed{}.U'.format(n), 'turbine{}.U{}'.format(m, n))
            if n > 0:
                self.connect('turbine{}.ct'.format(n - 1), 'turbine{}.prev_turbine_ct'.format(n))
                self.connect('turbine{}.power'.format(n - 1), 'turbine{}.prev_turbine_p'.format(n))

        self.add_subsystem('turbine{}'.format(max_n_turbines), self.turbine_model(max_n_turbines, self.n_cases), promotes_inputs=['n_turbines'])
        self.connect('speed{}.U'.format(max_n_turbines-1), 'turbine{}.U{}'.format(max_n_turbines, max_n_turbines-1))
        self.connect('turbine{}.power'.format(max_n_turbines - 1), 'turbine{}.prev_turbine_p'.format(max_n_turbines))
        self.connect('turbine{}.ct'.format(max_n_turbines - 1), 'turbine{}.prev_turbine_ct'.format(max_n_turbines))

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
        self.fraction_model = fraction_model(number, n_cases)
        self.deficit_model = deficit_model(n_cases)

    def setup(self):
        self.add_subsystem('fraction', self.fraction_model,
                           promotes_inputs=['ordered', 'angle', 'n_turbines', 'downwind_d', 'crosswind_d', 'turbine_radius'])
        self.add_subsystem('deficit', self.deficit_model,
                           promotes_inputs=['turbine_radius', 'downwind_d', 'crosswind_d', 'ct', 'n_turbines'],
                           promotes_outputs=['dU'])

        self.connect('fraction.fractions', 'deficit.fractions')
