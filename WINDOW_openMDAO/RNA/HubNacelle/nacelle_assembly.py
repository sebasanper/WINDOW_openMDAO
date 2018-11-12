from openmdao.api import Group, Problem, IndepVarComp, view_model
import gearbox, lss, bearing, hss, generator, bedplate, yaw, transformer, above_yaw, rna, nacelle


#############################################################################
################################  WORKFLOWS #################################
#############################################################################
class Nacelle(Group):
    
    def initialize(self):
        self.metadata.declare('safety_factor', desc='Safety factor of the model fidelity', default=1)
        self.metadata.declare('gearbox_stages', desc='Number of stages in the gearbox', default=3)        
        self.metadata.declare('gear_configuration', desc='Parallel or Planetary configuration of each stage', default='eep')
        self.metadata.declare('mb1_type', desc='Upwind main bearing type') # ['CARB','TRB1','TRB2','SRB','CRB','RB']
        self.metadata.declare('mb2_type', desc='Downwind main bearing type', allow_none=True)
        self.metadata.declare('drivetrain_design', desc='Drive train configuration', default='geared') # ['geared', 'single_stage', 'multi_drive', 'pm_direct_drive']
        self.metadata.declare('uptower_transformer', desc='Is uptower transformer present? [True/False]', default=False)
        self.metadata.declare('has_crane', desc='Is the crane present? [0/1]', default=0)

        
    def setup(self):
        # metadata
        safety_factor = self.metadata['safety_factor']
        gearbox_stages = self.metadata['gearbox_stages']
        gear_configuration = self.metadata['gear_configuration']
        mb1_type = self.metadata['mb1_type']
        mb2_type = self.metadata['mb2_type']
        drivetrain_design = self.metadata['drivetrain_design']
        uptower_transformer = self.metadata['uptower_transformer']
        has_crane = self.metadata['has_crane']
        
#         # design variables
#         i = self.add_subsystem('dof', IndepVarComp(), promotes=['*'])
#         i.add_output('rotor_diameter', units='m', desc='rotor diameter')
#         i.add_output('rotor_mass', units='kg', desc='rotor mass')
#         i.add_output('rotor_torque', units='N*m', desc='rotor torque at rated power')
#         i.add_output('rotor_thrust', units='N', desc='maximum rotor thrust')
#         i.add_output('rotor_speed', units='rpm', desc='rotor speed at rated')
#         i.add_output('machine_rating', units='kW', desc='machine rating of generator')
#         i.add_output('gear_ratio', desc='overall gearbox ratio')
#         i.add_output('tower_top_diameter', units='m', desc='diameter of tower top')
#         i.add_output('rotor_bending_moment', units='N*m', desc='The bending moment', shape=3)
#         i.add_output('rotor_force', units='N', desc='The force along the x axis applied at hub center', shape=3)
#         i.add_output('shaft_angle', units='deg', desc='Angle of the LSS inclindation with respect to the horizontal')
#         i.add_output('overhang', units='m', desc='Overhang distance')
#         i.add_output('gearbox_cm_x', units = 'm', desc = 'distance from tower-top center to gearbox cm--negative for upwind')
#         i.add_output('Np', desc='number of planets in each stage', shape=3)
        
        
        # sub-systems  
        self.add_subsystem('gearbox', gearbox.DriveSE(safety_factor=safety_factor,\
                                                      gearbox_stages=gearbox_stages, \
                                                      gear_configuration=gear_configuration), \
                            promotes_inputs=['gear_ratio', 'Np', 'rotor_speed', 'rotor_diameter', \
                                             'rotor_torque', 'gearbox_cm_x'], \
                            promotes_outputs=[('mass', 'gearbox_mass')])
        

        self.add_subsystem('lss', lss.DriveSE4pt(safety_factor=safety_factor,\
                                                  mb1_type=mb1_type, \
                                                  mb2_type=mb2_type), \
                           promotes_inputs=['rotor_bending_moment', 'rotor_force', 'rotor_mass', 'rotor_diameter', \
                                            'machine_rating', 'overhang', 'shaft_angle'], \
                           promotes_outputs=[('mass', 'lss_mass')])

        
        self.add_subsystem('main_bearing', bearing.MainBearing(safety_factor=safety_factor), \
                           promotes_inputs=['rotor_diameter', 'rotor_torque'], \
                           promotes_outputs=[('mass', 'main_bearing_mass')])
        
        self.add_subsystem('second_bearing', bearing.SecondBearing(safety_factor=safety_factor), \
                           promotes_inputs=['rotor_diameter', 'rotor_torque'], \
                           promotes_outputs=[('mass', 'second_bearing_mass')])
        
        self.add_subsystem('hss', hss.DriveSE(safety_factor=safety_factor), \
                           promotes_inputs=['rotor_diameter', 'rotor_torque', 'gear_ratio'], \
                           promotes_outputs=[('mass', 'hss_mass')])        
        
        self.add_subsystem('generator', generator.DriveSE(drivetrain_design=drivetrain_design), \
                           promotes_inputs=['rotor_diameter', 'machine_rating', 'gear_ratio', 'rotor_speed'], \
                           promotes_outputs=[('mass', 'generator_mass')])
        
        self.add_subsystem('yaw', yaw.DriveSE(safety_factor=safety_factor), \
                           promotes_inputs=['rotor_diameter', 'rotor_thrust', 'tower_top_diameter'], \
                           promotes_outputs=[('mass', 'yaw_mass')])
        
        self.add_subsystem('rna', rna.DriveSE(), \
                           promotes_inputs=['overhang', 'rotor_mass', 'machine_rating'], \
                           promotes_outputs=[])
        
        self.add_subsystem('transformer', transformer.DriveSE(uptower_transformer=uptower_transformer), \
                           promotes_inputs=['machine_rating', 'rotor_diameter', 'tower_top_diameter', 'rotor_mass', 'overhang'], \
                           promotes_outputs=[('mass', 'transformer_mass')])
        
        self.add_subsystem('bedplate', bedplate.DriveSE(safety_factor=safety_factor, \
                                                        uptower_transformer=uptower_transformer), \
                           promotes_inputs=['rotor_diameter', 'tower_top_diameter', 'machine_rating', \
                                            'rotor_mass', 'rotor_bending_moment', 'rotor_force', 'overhang'], \
                           promotes_outputs=[('mass', 'bedplate_mass')])
        
        self.add_subsystem('above_yaw', above_yaw.DriveSE(has_crane=has_crane), \
                           promotes_inputs=['machine_rating'], \
                           promotes_outputs=['hvac_mass', 'crane_mass', 'platforms_mass', \
                                             'vs_electronics_mass', 'cover_mass', 'mainframe_mass'])
        
        self.add_subsystem('nacelle', nacelle.DriveSE(), \
                           promotes_inputs=[], \
                           promotes_outputs=['nacelle_mass'])



        # connections
        self.connect('gearbox.length', ['lss.gearbox_length', 'hss.gearbox_length', 'bedplate.gbx_length'])
        self.connect('gearbox.height', ['hss.gearbox_height'])
        self.connect('gearbox_mass', ['lss.gearbox_mass', 'bedplate.gbx_mass', 'above_yaw.gearbox_mass', \
                                      'nacelle.gearbox_mass', 'rna.gearbox_mass'])
        
        
        self.connect('lss.diameter1', ['main_bearing.lss_diameter', 'hss.lss_diameter'])
        self.connect('lss.diameter2', 'second_bearing.lss_diameter')        
        self.connect('lss.bearing_location1', 'main_bearing.location')
        self.connect('lss.bearing_location2', 'second_bearing.location') 
        self.connect('lss.length', 'bedplate.lss_length')
        self.connect('lss.bearing_mass1',['main_bearing.bearing_mass'])
        self.connect('lss.bearing_mass2',['second_bearing.bearing_mass'])
        self.connect('lss.FW_mb1', 'bedplate.FW_mb1')
        self.connect('lss_mass', ['bedplate.lss_mass','above_yaw.lss_mass', 'nacelle.lss_mass', 'rna.lss_mass'])
        
        
        self.connect('main_bearing_mass', ['bedplate.mb1_mass','above_yaw.main_bearing_mass', \
                                           'nacelle.main_bearing_mass', 'rna.main_bearing_mass'])
        self.connect('second_bearing_mass', ['bedplate.mb2_mass','above_yaw.second_bearing_mass', \
                                             'nacelle.second_bearing_mass', 'rna.second_bearing_mass'])
        
        self.connect('hss.length','generator.hss_length')
        self.connect('hss_mass', ['bedplate.hss_mass','above_yaw.hss_mass', 'nacelle.hss_mass', 'rna.hss_mass'])
        
        self.connect('generator_mass', ['bedplate.generator_mass','above_yaw.generator_mass', \
                                        'nacelle.generator_mass', 'rna.generator_mass'])        
        self.connect('yaw_mass', ['nacelle.yawMass', 'rna.yawMass'])
        self.connect('rna.RNA_mass', ['transformer.RNA_mass'])
        self.connect('transformer_mass', ['above_yaw.transformer_mass','bedplate.transformer_mass','nacelle.transformer_mass'])
        
        
        #self.connect('bedplate.height', 'yaw.bedplate_height')
        self.connect('bedplate.length', 'above_yaw.bedplate_length')
        self.connect('bedplate.width', 'above_yaw.bedplate_width')
        self.connect('bedplate_mass', ['above_yaw.bedplate_mass', 'nacelle.bedplate_mass'])
        
        self.connect('mainframe_mass', ['nacelle.mainframe_mass'])        
        self.connect('above_yaw.above_yaw_mass', ['nacelle.above_yaw_mass']) # 'yaw.above_yaw_mass'
        
        
        
        
        self.connect('lss.cm', ['nacelle.lss_cm', 'rna.lss_cm'])
        self.connect('lss.cm', 'bedplate.lss_location', src_indices=0)
        self.connect('main_bearing.cm', ['nacelle.main_bearing_cm', 'rna.main_bearing_cm'])
        self.connect('main_bearing.cm', 'bedplate.mb1_location', src_indices=0)
        self.connect('second_bearing.cm', ['nacelle.second_bearing_cm', 'rna.second_bearing_cm'])
        self.connect('second_bearing.cm', 'bedplate.mb2_location', src_indices=0)
        self.connect('gearbox.cm', ['lss.gearbox_cm', 'hss.gearbox_cm', 'nacelle.gearbox_cm', 'rna.gearbox_cm'])
        self.connect('gearbox.cm', 'bedplate.gbx_location', src_indices=0)
        self.connect('hss.cm', ['generator.hss_cm', 'nacelle.hss_cm', 'rna.hss_cm'])
        self.connect('hss.cm','bedplate.hss_location', src_indices=0)
        self.connect('generator.cm', ['transformer.generator_cm', 'nacelle.generator_cm', 'rna.generator_cm'])
        self.connect('generator.cm', 'bedplate.generator_location', src_indices=0)
        self.connect('bedplate.cm', 'nacelle.bedplate_cm')
        self.connect('rna.RNA_cm','transformer.RNA_cm', src_indices=0)
        self.connect('transformer.cm','nacelle.transformer_cm')
        self.connect('transformer.cm', 'bedplate.transformer_location', src_indices=0)
        
        self.connect('lss.I', ['nacelle.lss_I'])
        self.connect('main_bearing.I', 'nacelle.main_bearing_I')
        self.connect('second_bearing.I', 'nacelle.second_bearing_I')
        self.connect('gearbox.I', ['nacelle.gearbox_I'])
        self.connect('hss.I', ['nacelle.hss_I'])
        self.connect('generator.I', ['nacelle.generator_I'])
        self.connect('bedplate.I', ['nacelle.bedplate_I'])
        self.connect('transformer.I', 'nacelle.transformer_I')
 
 
 
 
        
#############################################################################
##############################  UNIT TESTING ################################
# Activate (Uncomment) the design variables in the Group
############################################################################# 
if __name__ == "__main__":
    from time import time
    from math import pi
    from WINDOW_openMDAO.src.api import beautify_dict
    
    start = time()
        
    # workflow setup
    prob = Problem(Nacelle(safety_factor=1.5, \
                           gearbox_stages=3, \
                           gear_configuration = 'eep', \
                           mb1_type='CARB', \
                           mb2_type='SRB', \
                           drivetrain_design='geared', \
                           uptower_transformer=True, \
                           has_crane=True))
    prob.setup()
    #view_model(prob)
    
    # define inputs
    prob['rotor_diameter'] = 126.0
    prob['rotor_mass'] = 99072.6974
    prob['rotor_torque'] = (5000*1000/0.95)/(12.1*pi/30)
    prob['rotor_thrust'] = 599610.0 
    prob['rotor_speed'] = 12.1
    prob['machine_rating'] = 5000.0
    prob['gear_ratio'] = 96.76
    prob['tower_top_diameter'] = 3.78
    prob['rotor_bending_moment'] = [330770.0, -16665000.0 , 2896300.0]
    prob['rotor_force'] = [599610.0, 186780.0 , -842710.0 ]
    prob['shaft_angle'] = 5.0
    prob['overhang'] = 5.0
    prob['gearbox_cm_x'] = 0.1
    prob['Np'] = [3,3,1]
      
    prob.run_model()
    print 'Executed in ' + str(round(time() - start, 2)) + ' seconds\n'
     
    # print outputs 
    var_list = ['gearbox.mass', 'lss.mass', 'lss.length' ,'lss.diameter1', 'lss.diameter2', \
            'main_bearing.mass', 'second_bearing.mass', \
            'hss.mass', 'generator.mass', 'bedplate.mass', 'yaw.mass', 'transformer.mass', 'nacelle.nacelle_mass']
    saved_output = {}
    for v in var_list:
        saved_output[v] = prob[v]
        
        
    beautify_dict(saved_output)  
    
    
            