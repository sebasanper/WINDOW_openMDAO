from WINDOW_openMDAO.src.api import AbsRNAAssembly
from drivese_utils import add_RNA


#############################################################################
#############################  MODEL#1: DriveSE #############################
#############################################################################        
class DriveSE(AbsRNAAssembly):
    def compute(self, inputs, outputs):
        # inputs
        self.yawMass = inputs['yawMass']
        self.lss_mass = inputs['lss_mass']
        self.main_bearing_mass = inputs['main_bearing_mass']
        self.second_bearing_mass = inputs['second_bearing_mass']
        self.gearbox_mass = inputs['gearbox_mass']
        self.hss_mass = inputs['hss_mass']
        self.generator_mass = inputs['generator_mass']
        self.lss_cm = inputs['lss_cm']
        self.main_bearing_cm = inputs['main_bearing_cm']
        self.second_bearing_cm = inputs['second_bearing_cm']
        self.gearbox_cm = inputs['gearbox_cm']
        self.hss_cm = inputs['hss_cm']
        self.generator_cm = inputs['generator_cm']
        self.overhang = inputs['overhang']
        self.rotor_mass = inputs['rotor_mass']
        self.machine_rating = inputs['machine_rating']
        
        add_RNA(self)
        
        # outputs
        outputs['RNA_mass'] = self.RNA_mass
        outputs['RNA_cm'] = self.RNA_cm
        
        
                