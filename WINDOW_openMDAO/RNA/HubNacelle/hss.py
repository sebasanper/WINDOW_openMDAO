from WINDOW_openMDAO.src.api import AbsHSS
from drivese_utils import size_HighSpeedSide


#############################################################################
#############################  MODEL#1: DriveSE #############################
#############################################################################        
class DriveSE(AbsHSS):
    def compute(self, inputs, outputs):
        # metadata
        safety_factor = self.metadata['safety_factor']
        
        # inputs
        self.rotor_diameter = inputs['rotor_diameter']
        self.rotor_torque = inputs['rotor_torque']*safety_factor
        self.gear_ratio = inputs['gear_ratio']
        self.lss_diameter = inputs['lss_diameter']
        self.gearbox_length = inputs['gearbox_length']
        self.gearbox_height = inputs['gearbox_height']
        self.gearbox_cm = inputs['gearbox_cm']
        self.length_in = 0.0
        
        size_HighSpeedSide(self)
        
        # outputs
        outputs['mass'] = self.mass
        outputs['cm'] = self.cm
        outputs['I'] = self.I
        outputs['length'] = self.length
        