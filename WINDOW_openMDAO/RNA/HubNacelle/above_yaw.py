from WINDOW_openMDAO.src.api import AbsAboveYaw

from drivese_utils import add_AboveYawMass
       
#############################################################################
#############################  MODEL#1: DriveSE #############################
#############################################################################        
class DriveSE(AbsAboveYaw):
    def compute(self, inputs, outputs):
        # metadata
        self.crane = self.metadata['has_crane']
        
        # inputs
        self.machine_rating = inputs['machine_rating']
        self.lss_mass = inputs['lss_mass']
        self.main_bearing_mass = inputs['main_bearing_mass']
        self.second_bearing_mass = inputs['second_bearing_mass']
        self.gearbox_mass = inputs['gearbox_mass']
        self.hss_mass = inputs['hss_mass']
        self.generator_mass = inputs['generator_mass']
        self.bedplate_mass = inputs['bedplate_mass']
        self.bedplate_length = inputs['bedplate_length']
        self.bedplate_width = inputs['bedplate_width']
        self.transformer_mass = inputs['transformer_mass']

        add_AboveYawMass(self)
        
        outputs['electrical_mass'] = self.electrical_mass
        outputs['vs_electronics_mass'] = self.vs_electronics_mass
        outputs['hvac_mass'] = self.hvac_mass
        outputs['controls_mass'] = self.controls_mass
        outputs['platforms_mass'] = self.platforms_mass
        outputs['crane_mass'] = self.crane_mass
        outputs['mainframe_mass'] = self.mainframe_mass
        outputs['cover_mass'] = self.cover_mass
        outputs['above_yaw_mass'] = self.above_yaw_mass
        outputs['length'] = self.length
        outputs['width'] = self.width
        outputs['height'] = self.height
    
    
    
            