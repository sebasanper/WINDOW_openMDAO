import numpy as np

from time import time
from math import pi

from WINDOW_openMDAO.src.api import AbsGearbox
from drivese_utils import stageTypeCalc, stageMassCalc, gbxWeightEst, stageRatioCalc
      
        




#############################################################################
##############################  MODEL#1: DriveSE ############################
#############################################################################        
class DriveSE(AbsGearbox):
    def compute(self, inputs, outputs):
        # metadata
        safety_factor = self.metadata['safety_factor']
        gearbox_stages = self.metadata['gearbox_stages']
        self.gear_configuration=self.metadata['gear_configuration']
        
        # inputs
        self.gear_ratio = inputs['gear_ratio']
        self.Np = inputs['Np']
        self.rotor_speed = inputs['rotor_speed']
        self.rotor_diameter = inputs['rotor_diameter']
        self.rotor_torque = inputs['rotor_torque']*safety_factor
        self.cm_input = inputs['gearbox_cm_x']      
        
        self.ratio_type='optimal' # ['optimal', 'empirical']
        self.shaft_type='normal' # ['short', 'normal']

        self.stageRatio=np.zeros(gearbox_stages)
        self.stageTorque = np.zeros(gearbox_stages) #filled in when ebxWeightEst is called
        self.stageMass = np.zeros(gearbox_stages) #filled in when ebxWeightEst is called
        self.stageType=stageTypeCalc(self, self.gear_configuration)
        #print self.gear_ratio
        #print self.Np
        #print self.ratio_type
        #print self.gear_configuration
        self.stageRatio=stageRatioCalc(self, self.gear_ratio,self.Np,self.ratio_type,self.gear_configuration)
        #print self.stageRatio

        m=gbxWeightEst(self, self.gear_configuration,self.gear_ratio,self.Np,self.ratio_type,self.shaft_type,self.rotor_torque)
        self.mass = float(m)
        self.stage_masses=self.stageMass
        # calculate mass properties

        self.length = (0.012 * self.rotor_diameter)
        self.height = (0.015 * self.rotor_diameter)
        self.diameter = (0.75 * self.height)

        cm0   = self.cm_input
        cm1   = 0.0
        cm2   = 0.4*self.height #TODO validate or adjust factor. origin is modified to be above bedplate top
        self.cm = np.array([cm0, cm1, cm2])

        I0 = self.mass * (self.diameter ** 2 ) / 8 + (self.mass / 2) * (self.height ** 2) / 8
        I1 = self.mass * (0.5 * (self.diameter ** 2) + (2 / 3) * (self.length ** 2) + 0.25 * (self.height ** 2)) / 8
        I2 = I1
        self.I = np.array([I0, I1, I2])
        
        outputs['stage_masses'] = self.stage_masses #np.reshape(self.stage_masses, 3)
        outputs['mass'] = self.mass
        outputs['cm'] = self.cm
        outputs['I'] = np.reshape(self.I, 3)
        outputs['length'] = self.length
        outputs['height'] = self.height
        outputs['diameter'] = self.diameter
        outputs['efficiency'] = 0.98
        



        
        








#############################################################################
#########################  MODEL#2: 1-Stage Polinder ########################
#############################################################################        
class Polinder(AbsGearbox):
    def compute(self, inputs, outputs):
        # inputs
        gear_ratio = inputs['gear_ratio']
        Np = inputs['Np']
        rotor_torque = inputs['rotor_torque']*self.metadata['safety_factor']
        
        loss = 0.015 # loss percentage at rated power
        rw = (gear_ratio/2.0) - 1
        Tm = rotor_torque/gear_ratio
        Fw = (1.0/Np) + (1.0/(Np*rw)) + rw + (rw**2) + 0.4*((1+rw)*(gear_ratio-1)**2)/Np # weight factor
        Fs = 1.25 # gearbox service factor - surface damage and failure by metal fatigue
        mass = 3.2*Tm*Fs*Fw/1000.0        
        
        outputs['stage_masses'] = mass
        outputs['mass'] = mass
        outputs['efficiency'] = 1.0 - loss
        
        # the following outputs are not calculated
        outputs['cm'] = np.zeros(3)
        outputs['I'] = np.zeros(3)
        outputs['length'] = 0.0
        outputs['height'] = 0.0
        outputs['diameter'] = 0.0
    
    
        
        
        


#############################################################################
##############################  UNIT TESTING ################################
#############################################################################    
if __name__ == "__main__":
    from WINDOW_openMDAO.src.api import beautify_dict
    
    ###################################################
    ############### Model 1 Execution #################
    ################################################### 
    inputs={'gear_ratio' : 96.76, \
            'Np' : [3,3,1], \
            'rotor_speed' : 12.1, \
            'rotor_diameter' : 126., \
            'rotor_torque' : (5000*1000/0.95)/(12.1*pi/30), \
            'gearbox_cm_x' : 0.1}
    outputs={}
     
    model = DriveSE(safety_factor=1.5, gearbox_stages=3, gear_configuration='eep')
    model.compute(inputs, outputs)
    
    
#     ###################################################
#     ############### Model 2 Execution #################
#     ################################################### 
#     inputs={'gear_ratio' : 7.12, \
#             'Np' : 6, \
#             'rotor_torque' : (5000*1000)/(14.8*pi/30)}
#     outputs={}
#      
#     model = Polinder(safety_factor=1.5, gearbox_stages=1)
#     model.compute(inputs, outputs)
    
    
    
      
    ###################################################
    ############### Post Processing ###################
    ################################################### 
    beautify_dict(inputs) 
    print '-'*10
    beautify_dict(outputs)  
        