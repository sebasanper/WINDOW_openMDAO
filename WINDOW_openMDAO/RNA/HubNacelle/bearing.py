import numpy as np
from WINDOW_openMDAO.src.api import AbsBearing

#############################################################################
######################  MODEL#1: Upwind MainBearing #########################
#############################################################################        
class MainBearing(AbsBearing):
    def compute(self, inputs, outputs):
        # metadata
        safety_factor = self.metadata['safety_factor']
        
        # inputs
        self.bearing_mass = inputs['bearing_mass']
        self.lss_diameter = inputs['lss_diameter']
        self.lss_design_torque = inputs['rotor_torque']*safety_factor
        self.rotor_diameter = inputs['rotor_diameter']
        self.location = inputs['location']  
        
        self.mass = self.bearing_mass
        self.mass += self.mass*(8000.0/2700.0) #add housing weight
        
        # calculate mass properties
        inDiam  = self.lss_diameter
        depth = (inDiam * 1.5)

        if self.location[0] != 0.0:
            self.cm = self.location

        else:
            cmMB = np.array([0.0,0.0,0.0])
            cmMB = ([- (0.035 * self.rotor_diameter), 0.0, 0.025 * self.rotor_diameter])
            self.cm = cmMB
       
        b1I0 = (self.mass * inDiam ** 2 ) / 4.0 
        self.I = ([b1I0, b1I0 / 2.0, b1I0 / 2.0])
        
        # outputs 
        outputs['mass'] = self.mass
        outputs['cm'] = self.cm
        outputs['I'] = np.reshape(self.I, 3)
        
        
        
#############################################################################
######################  MODEL#2: Downwind MainBearing #######################
#############################################################################        
class SecondBearing(AbsBearing):
    def compute(self, inputs, outputs):
        # metadata
        safety_factor = self.metadata['safety_factor']
        
        # inputs
        self.bearing_mass = inputs['bearing_mass']
        self.lss_diameter = inputs['lss_diameter']
        self.lss_design_torque = inputs['rotor_torque']*safety_factor
        self.rotor_diameter = inputs['rotor_diameter']
        self.location = inputs['location']  
        
        self.mass = self.bearing_mass
        self.mass += self.mass*(8000.0/2700.0) #add housing weight
        
        # calculate mass properties
        inDiam  = self.lss_diameter
        depth = (inDiam * 1.5)

        if self.mass > 0 and self.location[0] != 0.0:
            self.cm = self.location
        else:
            self.cm = np.array([0,0,0])
            self.mass = 0.


        b2I0  = (self.mass * inDiam ** 2 ) / 4.0 
        self.I = ([b2I0, b2I0 / 2.0, b2I0 / 2.0])
        
        # outputs 
        outputs['mass'] = self.mass
        outputs['cm'] = self.cm
        outputs['I'] = np.reshape(self.I, 3)

        
        



#############################################################################
##############################  UNIT TESTING ################################
#############################################################################         
if __name__ == "__main__":
    from WINDOW_openMDAO.src.api import beautify_dict
    from math import pi
    
    ###################################################
    ############### Model 1 Execution #################
    ################################################### 
    inputs={'bearing_mass' : 1489.0804, \
            'lss_diameter' : 0.9819, \
            'rotor_torque' : ((5000*1000/0.95)/(12.1*pi/30)), \
            'rotor_diameter' : 126., \
            'location' : [-1.3637,  0.    , -1.6364]}
    outputs={}
     
    #model = MainBearing(safety_factor=1.5)
    model = SecondBearing(safety_factor=1.5)
    
    model.compute(inputs, outputs)   
    
      
    ###################################################
    ############### Post Processing ###################
    ################################################### 
    beautify_dict(inputs) 
    print '-'*10
    beautify_dict(outputs)