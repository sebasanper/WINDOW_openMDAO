from WINDOW_openMDAO.src.api import AbsNacelle
from drivese_utils import add_Nacelle

#############################################################################
#############################  MODEL#1: DriveSE #############################
#############################################################################        
class DriveSE(AbsNacelle):
    def compute(self, inputs, outputs):
        # inputs
        self.above_yaw_mass = inputs['above_yaw_mass']
        self.yawMass = inputs['yawMass']
        self.lss_mass = inputs['lss_mass']
        self.main_bearing_mass = inputs['main_bearing_mass']
        self.second_bearing_mass = inputs['second_bearing_mass']
        self.gearbox_mass = inputs['gearbox_mass']
        self.hss_mass = inputs['hss_mass']
        self.generator_mass = inputs['generator_mass']
        self.bedplate_mass = inputs['bedplate_mass']
        self.mainframe_mass = inputs['mainframe_mass']
        self.lss_cm = inputs['lss_cm']
        self.main_bearing_cm = inputs['main_bearing_cm']
        self.second_bearing_cm = inputs['second_bearing_cm']
        self.gearbox_cm = inputs['gearbox_cm']
        self.hss_cm = inputs['hss_cm']
        self.generator_cm = inputs['generator_cm']
        self.bedplate_cm = inputs['bedplate_cm']
        self.lss_I = inputs['lss_I']
        self.main_bearing_I = inputs['main_bearing_I']
        self.second_bearing_I = inputs['second_bearing_I']
        self.gearbox_I = inputs['gearbox_I']
        self.hss_I = inputs['hss_I']
        self.generator_I = inputs['generator_I']
        self.bedplate_I = inputs['bedplate_I']
        self.transformer_mass = inputs['transformer_mass']
        self.transformer_cm = inputs['transformer_cm']
        self.transformer_I = inputs['transformer_I']
        
        add_Nacelle(self)
        
        # outputs
        outputs['nacelle_mass'] = self.nacelle_mass
        outputs['nacelle_cm'] = self.nacelle_cm
        outputs['nacelle_I'] = self.nacelle_I
                