from WINDOW_openMDAO.src.api import AbsBedplate
from drivese_utils import setup_Bedplate, characterize_Bedplate_Rear, \
                        setup_Bedplate_Front, characterize_Bedplate_Front, size_Bedplate


#############################################################################
#############################  MODEL#1: DriveSE #############################
#############################################################################        
class DriveSE(AbsBedplate):
    def compute(self, inputs, outputs):
        # metadata
        safety_factor = self.metadata['safety_factor']
        self.uptower_transformer = self.metadata['uptower_transformer']
        
        # inputs
        self.gbx_length = inputs['gbx_length']
        self.gbx_location = inputs['gbx_location']
        self.gbx_mass = inputs['gbx_mass']
        self.hss_location = inputs['hss_location']
        self.hss_mass = inputs['hss_mass']
        self.generator_location = inputs['generator_location']
        self.generator_mass = inputs['generator_mass']
        self.lss_location = inputs['lss_location']
        self.lss_mass = inputs['lss_mass']
        self.lss_length = inputs['lss_length']
        self.mb1_location = inputs['mb1_location']
        self.FW_mb1 = inputs['FW_mb1']
        self.mb1_mass = inputs['mb1_mass']
        self.mb2_location = inputs['mb2_location']
        self.mb2_mass = inputs['mb2_mass']
        self.tower_top_diameter = inputs['tower_top_diameter']
        self.rotor_diameter = inputs['rotor_diameter']
        self.machine_rating = inputs['machine_rating']
        self.rotor_mass = inputs['rotor_mass']
        self.rotor_bending_moment_y = inputs['rotor_bending_moment'][1]*safety_factor
        self.rotor_force_z = inputs['rotor_force'][2]*safety_factor
        self.flange_length = 0.0
        self.L_rb = 0.0
        self.overhang = inputs['overhang']
        self.transformer_mass = inputs['transformer_mass']
        self.transformer_location = inputs['transformer_location']
        
#         print self.gbx_length, self.gbx_location, self.hss_location, \
#         self.generator_location, self.lss_location, self.mb1_location, \
#         self.mb2_location, self.overhang, self.transformer_location
        
        
        setup_Bedplate(self)
        counter = 0
        while self.rootStress*self.stress_mult - self.stressMax >  self.stressTol or self.totalTipDefl - self.deflMax >  self.deflTol:

            counter += 1
            
            characterize_Bedplate_Rear(self)
            
            self.tf += 0.002 
            self.tw += 0.002
            self.b0 += 0.006
            self.h0 += 0.006
            rearCounter = counter

        self.rearHeight = self.h0

        #Front cast section:
        setup_Bedplate_Front(self)

        counter = 0

        while self.rootStress*self.stress_mult - self.stressMax >  self.stressTol or self.totalTipDefl - self.deflMax >  self.deflTol:
            counter += 1
            characterize_Bedplate_Front(self)
            self.tf += 0.002 
            self.tw += 0.002
            self.b0 += 0.006
            self.h0 += 0.006
            
            frontCounter=counter

        size_Bedplate(self)
        
        
        
        # outputs
        outputs['mass'] = self.mass
        outputs['cm'] = self.cm
        outputs['I'] = self.I
        outputs['length'] = self.length
        outputs['height'] = self.height
        outputs['width'] = self.width
        
        
        
        
        
#############################################################################
##############################  UNIT TESTING ################################
#############################################################################         
if __name__ == "__main__":
    from WINDOW_openMDAO.src.api import beautify_dict
    
    ###################################################
    ############### Model 1 Execution #################
    ################################################### 
    inputs={}
    inputs['gbx_length'] = 1.512
    inputs['gbx_location'] = 0.1
    inputs['gbx_mass'] = 58594.4943
    inputs['hss_location'] = 1.606
    inputs['hss_mass'] = 2414.6772
    inputs['generator_location'] = 4.057
    inputs['generator_mass'] = 16699.8513
    inputs['lss_location'] = -1.1633
    inputs['lss_mass'] = 16873.6459
    inputs['lss_length'] = 3.053
    inputs['mb1_location'] = -1.3356
    inputs['FW_mb1'] = 0.3147
    inputs['mb1_mass'] = 6489.0463
    inputs['mb2_location'] = -0.6831
    inputs['mb2_mass'] = 1847.7989
    inputs['tower_top_diameter'] = 3.78
    inputs['rotor_diameter'] = 126.0
    inputs['machine_rating'] = 5000.0
    inputs['rotor_mass'] = 53220.0
    inputs['rotor_bending_moment'] = [0, -16665000.0, 0]
    inputs['rotor_force'] = [0, 0, -842710.0] 
    inputs['overhang'] = 5.0
    inputs['transformer_mass'] = 0
    inputs['transformer_location'] = 0
    
    
    outputs={}
     
    model = DriveSE(safety_factor=1.5, uptower_transformer=False)
    
    model.compute(inputs, outputs)   
    
      
    ###################################################
    ############### Post Processing ###################
    ################################################### 
    beautify_dict(inputs) 
    print '-'*10
    beautify_dict(outputs)        