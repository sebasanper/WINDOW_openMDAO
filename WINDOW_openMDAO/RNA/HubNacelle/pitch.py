from WINDOW_openMDAO.src.api import AbsPitch


#############################################################################
#############################  MODEL#1: DriveSE #############################
#############################################################################        
class DriveSE(AbsPitch):
    def compute(self, inputs, outputs):
        # metadata
        safety_factor = self.metadata['safety_factor']
        
        # inputs    
        self.blade_mass = inputs['blade_mass']
        self.rotor_bending_moment = inputs['rotor_bending_moment']*safety_factor
        self.blade_number = inputs['blade_number']
        
        # Sunderland method for calculating pitch system masses
        pitchmatldensity = 7860.0                             # density of pitch system material (kg / m^3) - assuming BS1503-622 (same material as LSS)
        pitchmatlstress  = 371000000.0                              # allowable stress of hub material (N / m^2)

        hubpitchFact      = 1.0                                 # default factor is 1.0 (0.54 for modern designs)
        #self.mass =hubpitchFact * (0.22 * self.blade_mass * self.blade_number + 12.6 * self.blade_number * self.rotor_bending_moment * (pitchmatldensity / pitchmatlstress))
                                                            # mass of pitch system based on Sunderland model
        self.mass =hubpitchFact * (0.22 * self.blade_mass * self.blade_number + 12.6 * self.rotor_bending_moment * (pitchmatldensity / pitchmatlstress))
                                                            # mass of pitch system based on Sunderland model
                                                            
        outputs['mass'] = self.mass                                                   
           
 
 
 
        
#############################################################################
#############################  UNIT TESTING #################################
#############################################################################  
if __name__ == "__main__":
    from WINDOW_openMDAO.src.api import beautify_dict
    
    ###################################################
    ############### Model 1 Execution #################
    ################################################### 
    inputs = {'blade_mass' : 17740.0, \
              'rotor_bending_moment' : 6196163.664902505, \
              'blade_number' : 3}
    outputs={}
    
    model = DriveSE(safety_factor=1.5)    
    model.compute(inputs, outputs) 
    
    ###################################################
    ############### Post Processing ###################
    ################################################### 
    beautify_dict(inputs) 
    print '-'*10
    beautify_dict(outputs)     