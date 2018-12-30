from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import max_n_turbines
import numpy as np


class MaxTI(ExplicitComponent):

    def __init__(self, n_cases):
        super(MaxTI, self).__init__()
        self.n_cases = n_cases

    def setup(self):
        self.add_input('all_TI', shape=(self.n_cases, max_n_turbines))

        self.add_output('max_TI', shape=max_n_turbines)

        #self.declare_partials(of='max_TI', wrt='all_TI', method='fd')

    def compute(self, inputs, outputs):
        outputs['max_TI'] = np.amax(inputs['all_TI'], axis=0)


class AbstractSupportStructureDesign(ExplicitComponent):

    def setup(self):
        self.add_input('max_TI', shape=max_n_turbines)
        self.add_input('depth', shape=max_n_turbines)
        self.add_input('n_turbines', val=0)
        self.add_input('rotor_radius', units='m', desc='radius of the turbine')     
        self.add_input('rated_wind_speed', units = 'm/s', desc='rated wind speed', val=11.4)
        self.add_input('rotor_thrust', units = 'N', desc='max rotor thrust', val=1500000.0)
        self.add_input('rna_mass', units='kg', desc='mass of RNA', val=589211.0)
        self.add_input('solidity_rotor', val=0.0516)
        self.add_input('cd_rotor_idle_vane', val=0.4)
        self.add_input('cd_nacelle', val=1.2)
        self.add_input('yaw_diameter', units='m', val=5.5)
        self.add_input('front_area_nacelle', units='m**2', val=14.0)
        self.add_input('yaw_to_hub_height', units='m', val=5.01)
        self.add_input('mass_eccentricity', units='m', val=1.9)

        self.add_output('cost_support', shape=max_n_turbines)

    def compute(self, inputs, outputs):
        n_turbines = int(inputs['n_turbines'])
        TI = inputs['max_TI'][:n_turbines]
        depth = inputs['depth'][:n_turbines]
        costs = self.support_design_model(TI, depth, inputs['rotor_radius'], inputs['rated_wind_speed'], \
                                          inputs['rotor_thrust'], inputs['rna_mass'], \
                                          inputs['solidity_rotor'], inputs['cd_rotor_idle_vane'], inputs['cd_nacelle'], \
                                          inputs['yaw_diameter'], inputs['front_area_nacelle'], inputs['yaw_to_hub_height'], inputs['mass_eccentricity'])
        lendif = max_n_turbines - len(costs)
        if lendif > 0:
            costs = np.concatenate((costs, [0.0 for _ in range(lendif)]))
        costs = costs.reshape(max_n_turbines)
        outputs['cost_support'] = costs

    def support_design_model(self, TIs, depths, rotor_radius, rated_wind_speed, \
                             rotor_thrust, rna_mass):
        #  Redefine method in subclass of AbstractSupportStructureDesign with specific model that has same inputs and outputs.
        pass


if __name__ == '__main__':
    from openmdao.api import Problem, Group, IndepVarComp

    class TeamPlay(AbstractSupportStructureDesign):

        def compute(self, inputs, outputs):
            TI = inputs['TI']
            depth = inputs['depth']
            outputs['cost_support'] = TI * depth ** 3.0

    model = Group()
    ivc = IndepVarComp()

    ivc.add_output('TI', 0.12)
    ivc.add_output('depth', 14.0)

    model.add_subsystem('indep', ivc)
    model.add_subsystem('teamplay', TeamPlay())

    model.connect('indep.TI', 'teamplay.TI')
    model.connect('indep.depth', 'teamplay.depth')

    prob = Problem(model)
    prob.setup()
    prob.run_model()
    print(prob['teamplay.cost_support'])
