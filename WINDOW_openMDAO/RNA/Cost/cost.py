import pandas as pd
from WINDOW_openMDAO.src.api import AbsRNACost

#############################################################################
################  MODEL#1: NREL Cost & Scaling Model ########################
#############################################################################  
class CSM(AbsRNACost):
    '''
        This cost model pertains only to the NREL 5MW Offshore Wind Turbine
    '''
    
    def compute(self, inputs, outputs):
        
        machine_rating = inputs['machine_rating']
        rotor_diameter = inputs['rotor_diameter']
        blade_number = inputs['blade_number']
        rotor_radius = rotor_diameter/2.0
        gearbox_stages = 3
         
        BCE = 1.0 # blade material cost escalator
        GDPE = 1.0 # labor cost escalator 

        # NREL cost model  
        outputs['cost_blade'] = ((0.4019*rotor_radius**3 - 955.24)*BCE + (2.7445*rotor_radius**2.5025)*GDPE)/(1-0.28)
        
        outputs['cost_hub'] = inputs['hub_mass'] * 4.25
        outputs['cost_pitch'] = 2.28 * (0.2106 * rotor_diameter**2.6578)
        outputs['cost_spinner'] = inputs['spinner_mass'] * 5.57
        
        outputs['cost_lss'] = 0.01 * rotor_diameter**2.887
        outputs['cost_main_bearing'] = 2 * inputs['main_bearing_mass'] * 17.6 # 2 times because housing mass = bearing mass
        outputs['cost_second_bearing'] = 2 * inputs['second_bearing_mass'] * 17.6
        
        # gearbox
        if gearbox_stages == 0:
            # direct-drive
            cost_gearbox = 0.0
            cost_generator = machine_rating * 219.33
            cost_mainframe = 627.28 * rotor_diameter**0.85
        elif gearbox_stages == 1:
            # single-stage
            cost_gearbox = 74.1 * machine_rating ** 1.0
            cost_generator = machine_rating * 54.73
            cost_mainframe = 303.96 * rotor_diameter**1.067
        else:
            # three-stage
            cost_gearbox = 16.45 * machine_rating ** 1.249  
            cost_generator = machine_rating * 65.0
            cost_mainframe = 9.489 * rotor_diameter**1.953
                     
        outputs['cost_gearbox'] = cost_gearbox        
        outputs['cost_hss'] = 1.9894 * (machine_rating - 0.1141)
        outputs['cost_generator'] = cost_generator
        outputs['cost_mainframe'] = cost_mainframe + inputs['platform_mass']*8.7
        outputs['cost_yaw'] = 2.0 * (0.0339 * rotor_diameter**2.964)
        outputs['cost_vs_electronics'] = machine_rating * 79.0
        outputs['cost_hvac'] = machine_rating * 12.0
        outputs['cost_cover'] = 11.537 * machine_rating + 3849.7
        outputs['cost_electrical'] = machine_rating * 40.0
        outputs['cost_controls'] = 55000.0
        outputs['cost_transformer'] = inputs['transformer_mass'] * 18.8 #(3.49e-06*machine_rating**2 - 0.0221*machine_rating + 109.7)*machine_rating
        
        # aggregator
        [outputs['cost_blades'], \
         outputs['cost_hub_system'], \
         outputs['cost_nacelle'], \
         outputs['cost_rna']] = aggregator_rna(outputs, blade_number)




#############################################################################
######################  MODEL#2: Calibrated NREL CSM ########################
#############################################################################             
class CSMCalibrated(AbsRNACost):
    '''
        This cost model pertains to the scaled version of a reference turbine
    '''
    
    def ref_cost_mass(self, component):
        #RT = pd.read_csv(cost_folder + 'reference_turbine_cost_mass.csv')
        RT = pd.read_csv(self.metadata['reference_turbine_cost'])
        return RT.loc[RT['Component'] == component, 'Cost'].values / RT.loc[RT['Component'] == component, 'Mass'].values
        
        
    def compute(self, inputs, outputs):
        blade_number = inputs['blade_number']
        machine_rating = inputs['machine_rating']
        mainframe_mass = inputs['bedplate_mass'] + inputs['platform_mass'] + inputs['crane_mass']
        
        outputs['cost_blade'] = inputs['blade_mass'] * self.ref_cost_mass('Blade')
        
        outputs['cost_hub'] = inputs['hub_mass'] * self.ref_cost_mass('Hub')
        outputs['cost_pitch'] = inputs['pitch_mass'] * self.ref_cost_mass('Pitch')
        outputs['cost_spinner'] = inputs['spinner_mass'] * self.ref_cost_mass('Spinner')
        
        outputs['cost_lss'] = inputs['lss_mass'] * self.ref_cost_mass('LSS')
        outputs['cost_main_bearing'] = inputs['main_bearing_mass'] * self.ref_cost_mass('Main Bearing')
        outputs['cost_second_bearing'] = inputs['second_bearing_mass'] * self.ref_cost_mass('Second Bearing')
        outputs['cost_gearbox'] = inputs['gearbox_mass'] * self.ref_cost_mass('Gearbox')
        outputs['cost_hss'] = inputs['hss_mass'] * self.ref_cost_mass('HSS')
        outputs['cost_generator'] = inputs['generator_mass'] * self.ref_cost_mass('Generator')
        outputs['cost_mainframe'] = mainframe_mass * self.ref_cost_mass('Mainframe')
        outputs['cost_yaw'] = inputs['yaw_mass'] * self.ref_cost_mass('Yaw')
        outputs['cost_vs_electronics'] = machine_rating * 26.33
        outputs['cost_hvac'] = machine_rating * 12.0
        outputs['cost_cover'] = inputs['cover_mass'] * self.ref_cost_mass('Cover')
        outputs['cost_electrical'] = machine_rating * 40.0
        outputs['cost_controls'] = 55000.0
        outputs['cost_transformer'] = inputs['transformer_mass'] * self.ref_cost_mass('Transformer')
        
        # aggregator
        [outputs['cost_blades'], \
         outputs['cost_hub_system'], \
         outputs['cost_nacelle'], \
         outputs['cost_rna']] = aggregator_rna(outputs, blade_number)

        
        
        
        
#############################################################################
############################# Common Routines ###############################
#############################################################################
def aggregator_rna(outputs, blade_number):
    # RNA
    cost_blades = aggregator_blades(outputs, blade_number)
    cost_hub = aggregator_hub(outputs)
    cost_nacelle = aggregator_nacelle(outputs)
    cost_rna = cost_blades + cost_hub + cost_nacelle
    
    return [cost_blades, cost_hub, cost_nacelle, cost_rna] 

def aggregator_blades(outputs, blade_number):
    cost_blades = outputs['cost_blade'] * blade_number
    return cost_blades
    
def aggregator_hub(outputs):    
    cost_hub =  outputs['cost_hub'] + outputs['cost_pitch'] + outputs['cost_spinner']
    return cost_hub        
    
def aggregator_nacelle(outputs):
    cost_nacelle = outputs['cost_lss'] + \
                             outputs['cost_main_bearing'] + \
                             outputs['cost_second_bearing'] + \
                             outputs['cost_gearbox'] + \
                             outputs['cost_hss'] + \
                             outputs['cost_generator'] + \
                             outputs['cost_mainframe'] + \
                             outputs['cost_yaw'] + \
                             outputs['cost_vs_electronics'] + \
                             outputs['cost_hvac'] + \
                             outputs['cost_cover'] + \
                             outputs['cost_electrical'] + \
                             outputs['cost_controls'] + \
                             outputs['cost_transformer']
                             
    return cost_nacelle                 
    
  
        
        