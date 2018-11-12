from WINDOW_openMDAO.src.api import AbsYaw
from drivese_utils import size_YawSystem


#############################################################################
#############################  MODEL#1: DriveSE #############################
#############################################################################        
class DriveSE(AbsYaw):
    def compute(self, inputs, outputs):
        # metadata
        safety_factor = self.metadata['safety_factor']
        
        # inputs
        self.rotor_diameter = inputs['rotor_diameter']
        self.rotor_thrust = inputs['rotor_thrust']*safety_factor
        self.tower_top_diameter = inputs['tower_top_diameter']
        self.above_yaw_mass = 0 #inputs['above_yaw_mass']
        self.bedplate_height = 0 #inputs['bedplate_height']
        self.yaw_motors_number = 0 # will be derived emperically in the next step
        
        size_YawSystem(self)
        
        outputs['mass'] = self.mass
        outputs['cm'] = self.cm
        outputs['I'] = self.I
    
    
    
            