from WINDOW_openMDAO.src.api import AbsTransformer
from drivese_utils import size_Transformer

        
        
#############################################################################
#############################  MODEL#1: DriveSE #############################
#############################################################################        
class DriveSE(AbsTransformer):
    def compute(self, inputs, outputs):
        # metadata
        self.uptower_transformer = self.metadata['uptower_transformer']
        
        # inputs
        self.machine_rating = inputs['machine_rating']
        self.tower_top_diameter = inputs['tower_top_diameter']
        self.rotor_mass = inputs['rotor_mass']
        self.overhang = inputs['overhang']
        self.generator_cm = inputs['generator_cm']
        self.rotor_diameter = inputs['rotor_diameter']
        self.RNA_mass = inputs['RNA_mass']
        self.RNA_cm = inputs['RNA_cm']
        
        size_Transformer(self)
        
        # outputs
        outputs['mass'] = self.mass
        outputs['cm'] = self.cm
        outputs['I'] = self.I      