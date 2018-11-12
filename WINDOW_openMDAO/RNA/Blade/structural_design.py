import numpy as np
import pandas as pd

from WINDOW_openMDAO.src.api import AbsStructuralDesign


def scale_turbine(ReferenceTurbine, thickness_factor, mu, scale_with, scalar):
    '''
        a common function that scales the structural profile of the blade with respect to the ReferenceTurbine
    '''
    
    # get the values of reference turbine
    ref_radius = ReferenceTurbine.r.iat[-1]
    ref_chord = np.interp(mu, ReferenceTurbine['mu'], ReferenceTurbine['chord'])
    ref_thickness = np.interp(mu, ReferenceTurbine['mu'], ReferenceTurbine['thickness'])
    ref_mass = np.interp(mu, ReferenceTurbine['mu'], ReferenceTurbine['mass'])
    ref_flap_inertia = np.interp(mu, ReferenceTurbine['mu'], ReferenceTurbine['flap_inertia'])
    ref_edge_inertia = np.interp(mu, ReferenceTurbine['mu'], ReferenceTurbine['edge_inertia'])
    ref_flap_stiff = np.interp(mu, ReferenceTurbine['mu'], ReferenceTurbine['flap_stiffness'])
    ref_edge_stiff = np.interp(mu, ReferenceTurbine['mu'], ReferenceTurbine['edge_stiffness'])
    
    if scale_with == 'Radius':
        s = scalar/ref_radius
    elif scale_with == 'Chord':
        s = scalar/ref_chord
    else:
        s = 1
    
    thickness = ref_thickness * (s**1)
    mass = ref_mass * (s**2) * thickness_factor
    flap_inertia = ref_flap_inertia * (s**4) * thickness_factor
    edge_inertia = ref_edge_inertia * (s**4) * thickness_factor
    flap_stiff = ref_flap_stiff * (s**4) * thickness_factor
    edge_stiff = ref_edge_stiff * (s**4) * thickness_factor
    
    return [thickness, mass, flap_inertia, edge_inertia, flap_stiff, edge_stiff]
    






#############################################################################
###########  MODEL 1: Scaling where radius is fixed #########################
#############################################################################
class VariableChord(AbsStructuralDesign):  
    '''
        scales the structural profile of the blade with respect to the ReferenceTurbine
        ASSUMING CONSTANT radius, airfoil distribution and number of blades
        but VARYING chord distribution
    '''  
    
    def compute(self, inputs, outputs):
        # metadata
        num_nodes = self.metadata['num_nodes']
        ReferenceTurbine = pd.read_csv(self.metadata['reference_turbine'])
        
        # inputs
        rotor_diameter = inputs['rotor_diameter']
        thickness_factor = inputs['thickness_factor']
        span_r = inputs['span_r']
        span_dr = inputs['span_dr']
        span_chord = inputs['span_chord']
        blade_number = inputs['blade_number']
        
        
        rotor_radius = rotor_diameter/2.0
        span_mu = [x/rotor_radius for x in span_r]
        span_thickness = np.array([])
        span_mass = np.array([])
        span_flap_inertia = np.array([])
        span_edge_inertia = np.array([])
        span_flap_stiff = np.array([])
        span_edge_stiff = np.array([])  
        
        for i in range(num_nodes):
            [thickness, mass, flap_inertia, edge_inertia, flap_stiff, edge_stiff] = \
                scale_turbine(ReferenceTurbine, thickness_factor, span_mu[i], 'Chord', span_chord[i])
             
            span_thickness = np.append(span_thickness, thickness)
            span_mass = np.append(span_mass, mass)
            span_flap_inertia = np.append(span_flap_inertia, flap_inertia)
            span_edge_inertia = np.append(span_edge_inertia, edge_inertia)
            span_flap_stiff = np.append(span_flap_stiff, flap_stiff)
            span_edge_stiff = np.append(span_edge_stiff, edge_stiff)
        
        blade_mass = np.dot(span_mass, span_dr)
        blades_mass = blade_mass * blade_number
        
        # outputs
        outputs['span_thickness'] = span_thickness
        outputs['span_mass'] = span_mass
        outputs['span_flap_inertia'] = span_flap_inertia
        outputs['span_edge_inertia'] = span_edge_inertia 
        outputs['span_flap_stiff'] = span_flap_stiff
        outputs['span_edge_stiff'] = span_edge_stiff
        outputs['blade_mass'] = blade_mass
        outputs['blades_mass'] = blades_mass

        


#############################################################################
###########  MODEL 2: Scaling where radius is varied ########################
#############################################################################        
class VariableRadius(AbsStructuralDesign):
    '''
        scales the structural profile of the blade with respect to the ReferenceTurbine
        ASSUMING CONSTANT blade design, airfoil distribution and number of blades
        but VARYING radius
    '''    
    def compute(self, inputs, outputs):
        # metadata
        num_nodes = self.metadata['num_nodes']
        ReferenceTurbine = pd.read_csv(self.metadata['reference_turbine'])
        
        # inputs
        rotor_diameter = inputs['rotor_diameter']
        thickness_factor = inputs['thickness_factor']
        span_r = inputs['span_r']
        span_dr = inputs['span_dr']
        span_chord = inputs['span_chord']
        blade_number = inputs['blade_number']
        
        
        rotor_radius = rotor_diameter/2.0
        span_mu = [x/rotor_radius for x in span_r]
        span_thickness = np.array([])
        span_mass = np.array([])
        span_flap_inertia = np.array([])
        span_edge_inertia = np.array([])
        span_flap_stiff = np.array([])
        span_edge_stiff = np.array([]) 
        
        for i in range(num_nodes):
            [thickness, mass, flap_inertia, edge_inertia, flap_stiff, edge_stiff] = \
                scale_turbine(ReferenceTurbine, thickness_factor, span_mu[i], 'Radius', rotor_radius)
             
            span_thickness = np.append(span_thickness, thickness)
            span_mass = np.append(span_mass, mass)
            span_flap_inertia = np.append(span_flap_inertia, flap_inertia)
            span_edge_inertia = np.append(span_edge_inertia, edge_inertia)
            span_flap_stiff = np.append(span_flap_stiff, flap_stiff)
            span_edge_stiff = np.append(span_edge_stiff, edge_stiff)
        
        blade_mass = np.dot(span_mass, span_dr)
        blades_mass = blade_mass * blade_number
        
        # outputs
        outputs['span_thickness'] = span_thickness
        outputs['span_mass'] = span_mass
        outputs['span_flap_inertia'] = span_flap_inertia
        outputs['span_edge_inertia'] = span_edge_inertia 
        outputs['span_flap_stiff'] = span_flap_stiff
        outputs['span_edge_stiff'] = span_edge_stiff 
        outputs['blade_mass'] = blade_mass
        outputs['blades_mass'] = blades_mass  
    


#############################################################################
##############################  UNIT TESTING ################################
#############################################################################    
if __name__ == "__main__":
    from WINDOW_openMDAO.src.api import beautify_dict
    
    ###################################################
    ############### Model Execution ###################
    ################################################### 
    span_r = [3.0375, 6.1125, 9.1875, 12.2625, 15.3375, 18.4125, 21.4875, 24.5625, 27.6375, 30.7125, 33.7875, 36.8625, 39.9375, 43.0125, 46.0875, 49.1625, 52.2375, 55.3125, 58.3875, 61.4625]
    span_dr = [3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075]
    span_chord = [3.5615, 3.9127, 4.2766, 4.5753, 4.6484, 4.5489, 4.3819, 4.2206, 4.0382, 3.8449, 3.6549, 3.4713, 3.2868, 3.1022, 2.9178, 2.7332, 2.5487, 2.3691, 2.1346, 1.4683]
    span_twist = [13.235, 13.235, 13.235, 13.1066, 11.6516, 10.5523, 9.6506, 8.7896, 7.876, 6.937, 6.0226, 5.1396, 4.2562, 3.428, 2.735, 2.1466, 1.5521, 0.9525, 0.3813, 0.0477]

    inputs={'rotor_diameter' : 126.0, \
            'thickness_factor' : 1.0, \
            'span_r' : span_r, \
            'span_dr' : span_dr, \
            'span_chord' : span_chord, \
            'blade_number' : 3}
    outputs={}
    
    model = VariableChord(num_nodes=20, reference_turbine = 'Airfoils/reference_turbine.csv')
#     model = VariableRadius(num_nodes=20, reference_turbine = 'Airfoils/reference_turbine.csv')
      
    model.compute(inputs, outputs)  
    
    
    ###################################################
    ############### Post Processing ###################
    ################################################### 
    beautify_dict(inputs) 
    print '-'*10
    beautify_dict(outputs)  
