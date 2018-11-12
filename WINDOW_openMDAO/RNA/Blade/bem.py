from math import pi, atan, degrees, radians, acos, sqrt, cos, sin, exp, isnan
import numpy as np
import pandas as pd

from airfoils import ReadAirfoil


####################################################
##### Perform the BEM analysis over an annulus #####
####################################################
def bem_annulus(wind_speed, rho_air, \
                n_blades, rotor_radius, hub_radius, tsr, pitch, \
                r, dr, chord, twist, airfoil_id, \
                is_prandtl, is_glauert):
    '''
        the BEM code to calculate the aerodynamic load at a given blade section
    '''
    
    # Modelling parameters
    itr_max = 100
    itr_tol = 5e-5
    itr_relax = 0.75
    
    # Inputs
    mu = r/rotor_radius
    mu_root = hub_radius/rotor_radius
    area = pi * ((r+dr/2.0)**2 - (r-dr/2.0)**2)
    tsr_r = tsr * mu
    sigma_r = n_blades * chord / (2*pi*r)
    omega = tsr * wind_speed / rotor_radius
    airfoil = ReadAirfoil(airfoil_id) # read the airfoil coordinates
    
    # initial estimates of induction factors
    aA = 0.3
    aT = 0.0
    
    CT1 = 1.816
    CT2 = 2*sqrt(CT1)-CT1

    
    # start iterating until the max iteration is reached (check break command)
    for i in range(itr_max):
        phi = degrees(atan((1-aA)/(tsr_r * (1+aT)))) # degree
        alpha = phi - twist - pitch # degree
        phi = radians(phi) # radian
        
        cl = np.interp(alpha, airfoil.ix[:, 'Alpha'], airfoil.ix[:, 'Cl'])
        cd = np.interp(alpha, airfoil.ix[:, 'Alpha'], airfoil.ix[:, 'Cd'])
        
        # hack
        if np.isnan(cl) or cl < 1.0e-6 :
            cl = 1.0e-6       
        if np.isnan(cd): 
            cd = 0  
            
            
        w = wind_speed * sqrt( (1-aA)**2 + (tsr_r*(1+aT))**2 ) # m/s
        lift = 0.5 * chord * rho_air * (w**2) * cl  # N/m
        drag = 0.5 * chord * rho_air * (w**2) * cd  # N/m
        
        fx = (lift*cos(phi)) + (drag*sin(phi)) # N/m
        fy = (lift*sin(phi)) - (drag*cos(phi)) # N/m
        cx = fx/(0.5 * rho_air * (wind_speed**2) * rotor_radius) 
        cy = fy/(0.5 * rho_air * (wind_speed**2) * rotor_radius)
        
        thrust = fx * n_blades * dr # N
        ct = thrust/(0.5 * rho_air * (wind_speed**2) * area)
        
        torque = fy * n_blades * r * dr # Nm
        cq = torque/(0.5 * rho_air * (wind_speed**2) * area * rotor_radius)
        
        power = torque * omega # W
        cp = power/(0.5 * rho_air * (wind_speed**3) * area) 

        
        # Prandtl correction for tip and root losses        
        if(is_prandtl):
            f_tip   = (2.0/pi) * acos(exp(-(n_blades/2.0)*((1-mu)/mu)*sqrt(1+(tsr_r/(1-aA))**2)))
            f_root  = (2.0/pi) * acos(exp(-(n_blades/2.0)*((mu-mu_root)/mu)*sqrt(1+(tsr_r/(1-aA))**2)))
        else:
            f_tip   = 1
            f_root  = 1
            
        f = f_tip*f_root
        f = 0.0001 if f<0.0001 else f
           
        # Glauert correction for heavily loaded rotor
        if(is_glauert):
            aA_new =  0.5 - 0.5*sqrt(1 - ct) if (ct < CT2) else 1 + 0.25*(ct - CT1)/(sqrt(CT1) - 1)
        else:
            aA_new = 0.5 - 0.5*sqrt(1 - ct) if(ct <= 0.96) else 0.33
            

        # get new values of induction factor
        aA_new = aA_new/f
        aA = itr_relax*aA + (1-itr_relax)*aA_new
        
        aT = (fy * n_blades)/(2 * rho_air * 2*pi*r  * (wind_speed**2) * (1-aA) * tsr_r)
        aT = aT/f
        
        # discard NAN values
        if(isnan(aA)):
            cp = 0
            break
        
        # check convergence
        if(abs((aA_new - aA)) <= itr_tol):
            break      
    
        # for loop ends
    
        
    result = {  'r' : r, \
                'airfoil_id' : airfoil_id, \
                'tsr_r' : tsr_r, \
                'sigma_r' : sigma_r, \
                'dr': dr, \
                'mu' : mu, \
                'area' : area, \
                'chord': chord, \
                'twist': twist, \
                'phi' : phi, \
                'alpha' : alpha, \
                'aA' : aA, \
                'aT' : aT, \
                'f' : f, \
                'cl' : cl, \
                'cd' : cd, \
                'lift' : lift, \
                'drag' : drag, \
                'thrust' : thrust, \
                'torque' : torque, \
                'power': power, \
                'fx' : fx, \
                'fy' : fy, \
                'cx' : cx, \
                'cy' : cy, \
                'ct' : ct, \
                'cq' : cq, \
                'cp' : cp}


    return result    





###################################################
##### Integrated result over the entire rotor #####
###################################################
def bem_rotor(wind_speed, rho_air, \
              n_blades, rotor_radius, hub_radius, tsr, pitch, \
              span_r, span_dr, span_chord, span_twist, span_airfoil, \
              is_prandtl, is_glauert):
    '''
        executes the BEM code over the entire rotor
    '''
    
    result = []
    
    # loop through each blade section
    for i in range(len(span_r)):
        r = span_r[i]
        dr = span_dr[i]
        chord = span_chord[i]
        twist = span_twist[i]
        airfoil_id = int(span_airfoil[i])
        result.append(bem_annulus(wind_speed, rho_air, \
                                  n_blades, rotor_radius, hub_radius, tsr, pitch, \
                                  r, dr, chord, twist, airfoil_id, \
                                  is_prandtl, is_glauert))

    
    spanwise =  pd.DataFrame(result)   
            
            
    # aggregate the rotor values
    swept_area = pi * (rotor_radius**2 - hub_radius**2)
    omega = tsr*wind_speed/rotor_radius
    
    power = np.sum(np.array(spanwise['power']))
    torque = power/omega
    thrust = np.sum(np.array(spanwise['thrust']))
    
    cp = power/(0.5 * rho_air * (wind_speed ** 3) * swept_area)
    cq = cp/tsr
    ct = thrust/(0.5 * rho_air * (wind_speed ** 2) * swept_area) 
    
    # outputs
    rotor = {}
    rotor['tsr'] = tsr
    rotor['swept_area'] = swept_area
    rotor['power'] = power
    rotor['torque'] = torque
    rotor['thrust'] = thrust
    rotor['cp'] = cp
    rotor['cq'] = cq
    rotor['ct'] = ct             
        
    return [spanwise, rotor]





    
    
    
         
#############################################################################
##############################  UNIT TESTING ################################
#############################################################################     
if __name__ == "__main__":
    
    # set fixed_parameters.num_nodes = 20
    span_r = [3.0375, 6.1125, 9.1875, 12.2625, 15.3375, 18.4125, 21.4875, 24.5625, 27.6375, 30.7125, 33.7875, 36.8625, 39.9375, 43.0125, 46.0875, 49.1625, 52.2375, 55.3125, 58.3875, 61.4625]
    span_dr = [3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075, 3.075]
    span_airfoil = [0.0, 0.0, 1.0, 2.0, 3.0, 3.0, 3.0, 4.0, 5.0, 5.0, 5.0, 6.0, 6.0, 6.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0]
    span_chord = [3.5615, 3.9127, 4.2766, 4.5753, 4.6484, 4.5489, 4.3819, 4.2206, 4.0382, 3.8449, 3.6549, 3.4713, 3.2868, 3.1022, 2.9178, 2.7332, 2.5487, 2.3691, 2.1346, 1.4683]
    span_twist = [13.235, 13.235, 13.235, 13.1066, 11.6516, 10.5523, 9.6506, 8.7896, 7.876, 6.937, 6.0226, 5.1396, 4.2562, 3.428, 2.735, 2.1466, 1.5521, 0.9525, 0.3813, 0.0477]

    
    [spanwise, rotor] = bem_rotor(12.2, 1.225, \
                                  3, 63.0, 1.5, 7.0, 0, \
                                  span_r, span_dr, span_chord, span_twist, span_airfoil, \
                                  is_prandtl=1, is_glauert=1)
    
    
    print spanwise
    print rotor
    