import numpy as np
from openmdao.api import ExplicitComponent

class Scaler(ExplicitComponent):
    def setup(self):                
        # inputs
        self.add_input('rotor_diameter', units='m', desc='rotor diameter')
        self.add_input('machine_rating', units='W', desc='machine rating')
        
        # outputs
        self.add_output('warranty_percentage', desc='insurance of the turbines % to its cost price', val=15)
        self.add_output('generator_voltage', units='V', desc='voltage at generator', val=4000.0)
        self.add_output('collection_voltage', units='V', desc='voltage at substation', val=66000.0)
        self.add_output('turbine_rated_current', units='A', desc='3 phase current per line', val=10000000.0 / (66000.0  * np.sqrt(3.0)))
        self.add_output('solidity_rotor', val=0.0516)
        self.add_output('cd_nacelle', val=1.2)
        self.add_output('cd_rotor_idle_vane', val=0.4)
        self.add_output('mass_eccentricity', units='m', val=1.9)
        self.add_output('yaw_to_hub_height', units='m', val=5.01)
        self.add_output('front_area_nacelle', units='m**2', val=14.0)
        self.add_output('hub_height', units='m', desc='hub height', val=119.0)
        self.add_output('hub_radius', units = 'm', desc = 'hub radius')
        self.add_output('overhang', units='m', desc='overhang distance')
        self.add_output('gearbox_cm_x', units = 'm', desc = 'distance from tower-top center to gearbox cm--negative for upwind')
        self.add_output('tower_top_diameter', units='m', desc='diameter of tower top')
        

    
    def compute(self, inputs, outputs):
        # inputs     
        rotor_diameter = inputs['rotor_diameter']  
        machine_rating = inputs['machine_rating']
        
        # hard coded
        outputs['generator_voltage'] = 4000.0
        outputs['collection_voltage'] = 66000.0
        outputs['warranty_percentage'] = 15.0
        outputs['turbine_rated_current'] = machine_rating / (outputs['collection_voltage']  * np.sqrt(3.0))
        outputs['solidity_rotor'] = 0.0516
        outputs['cd_nacelle'] = 1.2
        outputs['cd_rotor_idle_vane'] = 0.4
        
        # scaled from DTU 10MW Reference Turbine
        s = rotor_diameter/190.8
        outputs['mass_eccentricity'] = 1.9 * s
        outputs['yaw_to_hub_height'] = 5.01 * s
        outputs['front_area_nacelle'] = 14.0 * (s**2)
        outputs['hub_height'] = 119 * s
        
        # scaled from NREL 5MW Reference Turbine
        s = rotor_diameter/126.0
        outputs['hub_radius'] = 1.5 * s
        outputs['overhang'] = 5.0 * s
        outputs['gearbox_cm_x'] = 0.1 * s
        outputs['tower_top_diameter'] = 3.78 * s


     
        
        
        
        