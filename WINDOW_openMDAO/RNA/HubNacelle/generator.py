from WINDOW_openMDAO.src.api import AbsGenerator
from drivese_utils import size_Generator


#############################################################################
#############################  MODEL#1: DriveSE #############################
#############################################################################        
class DriveSE(AbsGenerator):
    def compute(self, inputs, outputs):
        # metadata
        self.drivetrain_design = self.metadata['drivetrain_design']
        
        # inputs
        self.rotor_diameter = inputs['rotor_diameter']
        self.machine_rating = inputs['machine_rating']
        self.gear_ratio = inputs['gear_ratio']
        self.highSpeedSide_length = inputs['hss_length']
        self.highSpeedSide_cm = inputs['hss_cm']
        self.rotor_speed = inputs['rotor_speed']
        
        size_Generator(self)
        
        # outputs
        outputs['mass'] = self.mass
        outputs['cm'] = self.cm
        outputs['I'] = self.I