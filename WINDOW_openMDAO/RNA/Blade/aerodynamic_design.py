import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from WINDOW_openMDAO.src.api import AbsAerodynamicDesign
from airfoils import AirfoilProperties



#############################################################################
###########  MODEL 1: USE CASE 1 with PEGGED POINTS #########################
#############################################################################
class PeggedNodes(AbsAerodynamicDesign):   
    '''
       defines the chord and twist distribution using pegged points
    '''  
    
    def compute(self, inputs, outputs):
        # metadata
        num_pegged = self.metadata['num_pegged']
        num_airfoils = self.metadata['num_airfoils']
        num_nodes = self.metadata['num_nodes']
        
        # inputs
        rotor_diameter = inputs['rotor_diameter']
        hub_radius = inputs['hub_radius']
        chord_coefficients = inputs['chord_coefficients'] # c[0], c[1], ..., c[N-2], c_tip  -----> N = num_pegged
        twist_coefficients = inputs['twist_coefficients'] # t_root, t[1], t[2], ..., t[N-1] -----> N = num_pegged
        span_airfoil_r = inputs['span_airfoil_r']
        span_airfoil_id = inputs['span_airfoil_id']
        
        rotor_radius = rotor_diameter/2.0
        mu_root = hub_radius/rotor_radius
        
        # get distinct airfoil data
        airfoils_ = []
        for i in set(span_airfoil_id):
            airfoils_.append(AirfoilProperties(int(i)))
            
        airfoils = pd.DataFrame(airfoils_)  
        airfoils = airfoils.set_index('id')
        
        # divide the blade into annulus
        mu_ = np.linspace(mu_root, 1.0, num_nodes + 1)
        span_mu = np.array([(x+y)/2.0 for x,y in zip(mu_[:-1], mu_[1:])]) # the position of the annulus is taken as its midpoint
        span_r = np.multiply(span_mu, rotor_radius)
        span_dr = np.array([(x-y)*rotor_radius for x,y in zip(mu_[1:], mu_[:-1])]).reshape(num_nodes)      
        
        span_airfoil = np.array([])
        span_airfoil_i = 0
        trans_point = 0
        
        for i in range(num_nodes):
            mu = span_mu[i]
            r = span_r[i]
            
            # check if we need to move to the next airfoil
            next_airfoil_i = span_airfoil_i + 1 if (span_airfoil_i < num_airfoils - 1) else num_airfoils - 1
            next_airfoil_r = span_airfoil_r[next_airfoil_i]
            span_airfoil_i = span_airfoil_i + 1 if (r >= next_airfoil_r and  span_airfoil_i < num_airfoils - 1) else span_airfoil_i
            airfoil_id = int(span_airfoil_id[span_airfoil_i])
            
            span_airfoil = np.append(span_airfoil, airfoil_id)
            
            # get the optimal values of that airfoil
            cl_opt = airfoils.loc[airfoil_id, 'cl_opt']
            
            # check transition point
            if cl_opt != 0.0 and trans_point == 0:
                trans_mu = mu
                trans_point = 1  
        
        # Burton's profile
        peg_mu = [mu_root, 0.7, 0.9]
        span_chord =  self.chord_profile(chord_coefficients, peg_mu, span_mu)  

        peg_mu = [trans_mu, 0.4, 0.7]
        span_twist =  self.twist_profile(twist_coefficients, peg_mu, span_mu)
        
        # outputs
        outputs['span_r'] = span_r
        outputs['span_dr'] = span_dr
        outputs['span_airfoil'] = span_airfoil
        outputs['span_chord'] = span_chord
        outputs['span_twist'] = span_twist
        #outputs['pitch'] = 0      
        
        
    def chord_profile(self, peg_chord, peg_mu, span_mu):
        '''
            returns the chord length at each node using the inputs at the pegged points
        '''
        
        num_nodes = self.metadata['num_nodes']
                
        # redesign for manufacturing ease
        mu0 = 0.20
        p0 = int(mu0*num_nodes) - 1 # index of mu0
        
        m = (peg_chord[1] - peg_chord[2])/(peg_mu[1] - peg_mu[2]) # slope
        y = peg_chord[2] - m*peg_mu[2] # y-intercept
        c0 = m*mu0 + y # chord length at 25% point
        m0 = (c0 - peg_chord[0])/(mu0 - peg_mu[0]) # slope of chord at the transition
        y0 = peg_chord[0] - m0*peg_mu[0] # y-intercept
        
        # blade root transition slope from the reference turbine
        span_chord = []
        for i in range(p0):
            #span_chord[i] = m_tran*span_mu[i] + root_chord
            span_chord.append(m0*span_mu[i] + y0)
            
        span_chord.append(c0)    
        
        for i in range(p0+1, num_nodes):
            #span_chord[i] = m*span_mu[i] + c
            span_chord.append(m*span_mu[i] + y)    
            
        # smooth out the curve
        span_chord[p0] = (span_chord[p0-1]+span_chord[p0]+span_chord[p0+1])/3
        #mu_temp = np.linspace(span_mu.min(), span_mu.max(), 300)
        #span_chord = spline(span_mu, span_chord, mu_temp)
        
        return span_chord
    
    
    def twist_profile(self, peg_twist, peg_mu, span_mu):
        '''
            returns the twist angle at each node using the inputs at the pegged points
        '''
        
        # peg_twist = [trans_twist, t1, t2]
        # peg_mu = [trans_mu, mu1, mu2]
       
        span_twist = []
        
        # zone 1 - root to p1
        for mu in [x for x in span_mu if x <= peg_mu[0]]:
            span_twist.append(peg_twist[0])
        
        # zone 2 - p1 to p2
        m1 = (peg_twist[1] - peg_twist[0])/(peg_mu[1] - peg_mu[0]) # slope
        y1 = peg_twist[0] - m1*peg_mu[0] # y-intercept   
        for mu in [x for x in span_mu if x > peg_mu[0] and x <= peg_mu[1]]:
            span_twist.append(m1*mu + y1)     
        
        # zone 3 - p2 to p3
        m2 = (peg_twist[1] - peg_twist[2])/(peg_mu[1] - peg_mu[2]) # slope
        y2 = peg_twist[2] - m2*peg_mu[2] # y-intercept
        for mu in [x for x in span_mu if x > peg_mu[1] and x <= peg_mu[2]]:
            span_twist.append(m2*mu + y2)  
        
        # zone 4 - p3 to tip
        m3 = (0.0 - peg_twist[2])/(span_mu[-1] - peg_mu[2]) # slope
        y3 = peg_twist[2] - m3*peg_mu[2] # y-intercept
        for mu in [x for x in span_mu if x > peg_mu[2]]:
            span_twist.append(m3*mu + y3)  
        
        return span_twist        
        
        
        
        

#############################################################################
###########  MODEL 2: Scaled from Reference Turbine #########################
#############################################################################
class Scaling(AbsAerodynamicDesign):   
    '''
        computes the chord and twist distribution by scaling it from a Reference turbine
    '''    
    
    def compute(self, inputs, outputs):
        # metadata
        num_pegged = self.metadata['num_pegged']
        num_airfoils = self.metadata['num_airfoils']
        num_nodes = self.metadata['num_nodes']
        
        # inputs
        rotor_diameter = inputs['rotor_diameter']
        hub_radius = inputs['hub_radius']
        span_airfoil_r = inputs['span_airfoil_r']
        span_airfoil_id = inputs['span_airfoil_id']
        
        rotor_radius = rotor_diameter/2.0
        mu_root = hub_radius/rotor_radius
        
        # divide the blade into annulus
        mu_ = np.linspace(mu_root, 1.0, num_nodes + 1)
        span_mu = np.array([(x+y)/2.0 for x,y in zip(mu_[:-1], mu_[1:])]) # the position of the annulus is taken as its midpoint
        span_r = np.multiply(span_mu, rotor_radius)
        span_dr = np.array([(x-y)*rotor_radius for x,y in zip(mu_[1:], mu_[:-1])]).reshape(num_nodes)        
        
        span_airfoil = np.array([])
        span_chord = np.array([])
        span_twist = np.array([])
        
        span_airfoil_i = 0
        
        for i in range(num_nodes):
            mu = span_mu[i]
            r = span_r[i]
            
            # check if we need to move to the next airfoil
            next_airfoil_i = span_airfoil_i + 1 if (span_airfoil_i < num_airfoils - 1) else num_airfoils - 1
            next_airfoil_r = span_airfoil_r[next_airfoil_i]
            span_airfoil_i = span_airfoil_i + 1 if (r >= next_airfoil_r and  span_airfoil_i < num_airfoils - 1) else span_airfoil_i
            airfoil_id = int(span_airfoil_id[span_airfoil_i])
            
            # use scaling law
            [chord, twist] = self.scale_chord_with_radius(mu, rotor_radius)
            
            span_airfoil = np.append(span_airfoil, airfoil_id)
            span_chord = np.append(span_chord, chord)
            span_twist = np.append(span_twist, twist) 
        
        # outputs
        outputs['span_r'] = span_r
        outputs['span_dr'] = span_dr
        outputs['span_airfoil'] = span_airfoil
        outputs['span_chord'] = span_chord
        outputs['span_twist'] = span_twist
        
        
    def scale_chord_with_radius(self, mu, radius):
        '''
            This function scales the chord length of the blade with respect to NREL 5MW Offshore wind turbine
            ASSUMING CONSTANT number of blades (3), airfoil distribution
            but VARYING rotor radius
        '''
        
        ReferenceTurbine = pd.read_csv(self.metadata['reference_turbine'])
        
        ref_radius = ReferenceTurbine.r.iat[-1]
        ref_chord = np.interp(mu, ReferenceTurbine['mu'], ReferenceTurbine['chord'])
        ref_twist = np.interp(mu, ReferenceTurbine['mu'], ReferenceTurbine['twist'])
        
        s = radius/ref_radius # scaling factor
        
        chord = ref_chord * (s**1)
        twist = ref_twist * (s**0)
        
        return [chord, twist]









#############################################################################
##############################  UNIT TESTING ################################
#############################################################################    
if __name__ == "__main__":
    from WINDOW_openMDAO.src.api import beautify_dict
    
    ###################################################
    ############### Model Execution ###################
    ################################################### 
    inputs={'design_tsr' : 8.0, \
            'blade_number' : 3, \
            'rotor_diameter' : 126.0, \
            'hub_radius' : 1.5, \
            'root_chord' : 3.542, \
            'chord_coefficients' : [3.542, 3.01, 2.313], \
            'twist_coefficients' : [13.308, 9.0, 3.125], \
            'span_airfoil_r' :  [01.36, 06.83, 10.25, 14.35, 22.55, 26.65, 34.85, 43.05], \
            'span_airfoil_id' : [0,     1,     2,     3,     4,     5,     6,     7]}
    outputs={}
    
    model = Scaling(num_pegged=3, num_nodes=20, num_airfoils=8, reference_turbine = 'Airfoils/reference_turbine.csv')
#     model = PeggedNodes(num_pegged=3, num_nodes=20, num_airfoils=8)
      
    model.compute(inputs, outputs)  
    
    
    ###################################################
    ############### Post Processing ###################
    ################################################### 
    beautify_dict(inputs) 
    print '-'*10
    beautify_dict(outputs)  
    
    span_chord = [3.5615, 3.9127, 4.2766, 4.5753, 4.6484, 4.5489, 4.3819, 4.2206, 4.0382, 3.8449, 3.6549, 3.4713, 3.2868, 3.1022, 2.9178, 2.7332, 2.5487, 2.3691, 2.1346, 1.4683]
    span_twist = [13.235, 13.235, 13.235, 13.1066, 11.6516, 10.5523, 9.6506, 8.7896, 7.876, 6.937, 6.0226, 5.1396, 4.2562, 3.428, 2.735, 2.1466, 1.5521, 0.9525, 0.3813, 0.0477]

    font = {'family' : 'Tahoma', 'size' : 15}
    plt.rc('font', **font)
    fig = plt.figure()
    
    x = np.array(outputs['span_r'])/63.0
    
    x1 = fig.add_subplot(121)
    x1.set_title('Chord distribution')
    x1.set_xlabel('Normalized radial distance [-]')
    x1.set_ylabel('Chord [m]')
    x1.plot(x, outputs['span_chord'], marker='^', label='Burton')
    x1.plot(x, span_chord, marker='s', label='Reference')
    x1.axvline(x=0.045, linestyle=':', color='r')
    x1.axvline(x=0.20, linestyle=':', color='c')
    x1.axvline(x=0.70, linestyle=':', color='r')
    x1.axvline(x=0.90, linestyle=':', color='r')
    
    
    x2 = fig.add_subplot(122)
    x2.set_title('Twist distribution')
    x2.set_xlabel('Normalized radial distance [m]')
    x2.set_ylabel('Twist [deg]')
    x2.plot(x, outputs['span_twist'], marker='^', label='Burton')
    x2.plot(x, span_twist, marker='s', label='Reference')
    x2.axvline(x=0.20, linestyle=':', color='r')
    x2.axvline(x=0.40, linestyle=':', color='r')
    x2.axvline(x=0.70, linestyle=':', color='r')
    
    x1.legend(loc='upper right')
    x2.legend(loc='upper right')
    plt.show()
    


 