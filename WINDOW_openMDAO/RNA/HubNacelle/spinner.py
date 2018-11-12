from WINDOW_openMDAO.src.api import AbsSpinner

#############################################################################
#############################  MODEL#1: DriveSE #############################
#############################################################################        
class DriveSE(AbsSpinner):
    def compute(self, inputs, outputs):
        # inputs    
        self.rotor_diameter = inputs['rotor_diameter']
        
        self.mass =18.5 * self.rotor_diameter + (-520.5)   # spinner mass comes from cost and scaling model
                                                            
        outputs['mass'] = self.mass                                                  