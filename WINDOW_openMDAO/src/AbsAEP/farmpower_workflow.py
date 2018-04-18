from openmdao.api import Group, ExplicitComponent
from WINDOW_openMDAO.src.AbsWakeModel.wake_linear_solver import WakeModel
from WINDOW_openMDAO.src.AbsAEP.abstract_power import FarmAeroPower
from WINDOW_openMDAO.src.SiteConditionsPrep.windrose_process import WindrosePreprocessor
from WINDOW_openMDAO.src.AbsAEP.open_cases import OpenCases
from time import clock


class AEPWorkflow(Group):
    def __init__(self, real_angle, artificial_angle, n_windspeedbins, fraction_model, deficit_model, merge_model, turbine_model, power_table, ct_table):
        super(AEPWorkflow, self).__init__()
        self.real_angle = real_angle
        self.artificial_angle = artificial_angle
        self.n_windspeedbins = n_windspeedbins
        self.n_angles = 360.0 / self.artificial_angle
        self.n_windspeeds = n_windspeedbins + 1
        self.n_cases = int(self.n_angles * self.n_windspeeds)
        self.fraction_model = fraction_model
        self.deficit_model = deficit_model
        self.merge_model = merge_model
        self.turbine_model = turbine_model
        self.power_table = power_table
        self.ct_table = ct_table

    def setup(self):
        self.add_subsystem('windrose', WindrosePreprocessor(self.real_angle, self.artificial_angle,
                                                            self.n_windspeedbins), promotes_inputs=['cut_in', 'cut_out',
                                                                                                    'weibull_shapes',
                                                                                                    'weibull_scales',
                                                                                                    'dir_probabilities',
                                                                                                    'wind_directions'])
        self.add_subsystem('open_cases', OpenCases(self.n_cases))
        self.add_subsystem('wakemodel', WakeModel(self.n_cases, self.fraction_model, self.deficit_model, self.merge_model, self.turbine_model, power_table, ct_table),
                           promotes_inputs=['turbine_radius', 'original', 'n_turbines'])
        self.add_subsystem('farmpower', FarmAeroPower(self.n_cases), promotes_inputs=['n_turbines'])
        self.add_subsystem('energy', PowersToAEP(self.artificial_angle, self.n_windspeedbins),
                           promotes_outputs=['energies', 'AEP'])

        self.connect('windrose.cases', 'open_cases.cases')
        self.connect('windrose.probabilities', 'energy.probabilities')
        self.connect('open_cases.freestream_wind_speeds', 'wakemodel.freestream')
        self.connect('open_cases.wind_directions', 'wakemodel.angle')
        self.connect('wakemodel.p', 'farmpower.ind_powers')
        self.connect('farmpower.farm_power', 'energy.powers')


class PowersToAEP(ExplicitComponent):
    def __init__(self, artificial_angle, n_windspeedbins):
        super(PowersToAEP, self).__init__()
        self.n_angles = 360.0 / artificial_angle
        self.n_windspeeds = n_windspeedbins + 1
        self.windrose_cases = int(self.n_angles * self.n_windspeeds)

    def setup(self):
        self.add_input('powers', shape=self.windrose_cases)
        self.add_input('probabilities', shape=self.windrose_cases)

        self.add_output('energies', shape=self.windrose_cases)
        self.add_output('AEP', val=0.0)

        #self.declare_partials(of=['AEP', 'energies'], wrt=['powers', 'probabilities'], method='fd')

    def compute(self, inputs, outputs):
        powers = inputs['powers']
        probs = inputs['probabilities']
        energies = powers * probs * 8760.0
        # with open('energies_out.dat', 'w') as out:
        #     for n in range(self.windrose_cases):
        #         out.write('{} {} {}\n'.format(powers[n], probs[n], energies[n]))
        outputs['energies'] = energies
        # print energies
        outputs['AEP'] = sum(energies)
        # print clock(), "Last line compute AEP energies"
