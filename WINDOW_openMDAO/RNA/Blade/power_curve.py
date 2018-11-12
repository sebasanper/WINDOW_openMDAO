import numpy as np

from WINDOW_openMDAO.src.api import AbsPowerCurve  


class PowerCurve(AbsPowerCurve):
    '''
        a simple power curve model
    '''
                
    def compute(self, inputs, outputs):
        # metadata
        num_bins = self.metadata['num_bins']
        rho_air = self.metadata['rho_air']
        
        # inputs
        design_tsr = inputs['design_tsr'] 
        cut_in_speed = inputs['cut_in_speed'] 
        cut_out_speed = inputs['cut_out_speed']  
        swept_area = inputs['swept_area']
        machine_rating = inputs['machine_rating'] 
        eta_dt = inputs['drive_train_efficiency']
        rotor_cp = inputs['rotor_cp']   
        rotor_ct = inputs['rotor_ct']  
        
        rated_wind_speed = (machine_rating * 1000.0 / (rotor_cp * 0.5 * rho_air * swept_area * eta_dt))**(1.0/3.0)
        rated_tip_speed  = design_tsr * rated_wind_speed
        wind_bin = np.linspace(0, 30.0, num_bins) 
        aero_power_bin, elec_power_bin, thrust_bin, cp_bin, ct_bin = [], [], [], [], []
       
        # aerodynamic calculations
        for v in wind_bin:
            if v < cut_in_speed or v > cut_out_speed:
                power, thrust, cp, ct = 0., 0., 0., 0.
            elif v < rated_wind_speed:
                power  = rotor_cp * 0.5 * rho_air * swept_area * (v**3) / 1000.0  
                thrust = rotor_ct * 0.5 * rho_air * swept_area * (v**2)   
                cp = rotor_cp
                ct = rotor_ct           
            else:
                power = machine_rating/eta_dt    
                cp = (machine_rating * 1000.0)/(0.5 * rho_air * swept_area * (v**3) * eta_dt)
                
                # => cp = 4a(1-a)^2 
                # => 4a^3 - 8a^2 + 4a - cp = 0
                a = min(np.roots([4, -8, 4, -1*cp]))
                ct = 4*a*(1-a)
                thrust = ct * 0.5 * rho_air * swept_area * (rated_wind_speed**2)
            
            aero_power_bin.append(power)        # aerodynamic power
            elec_power_bin.append(power*eta_dt) # electrical power    
            thrust_bin.append(thrust)
            cp_bin.append(cp)
            ct_bin.append(ct)        


        
        outputs['rated_wind_speed'] = rated_wind_speed     
        outputs['rated_tip_speed'] = rated_tip_speed   
        outputs['wind_bin'] = wind_bin
        outputs['elec_power_bin'] = np.array(elec_power_bin).reshape(num_bins)
        outputs['aero_power_bin'] = aero_power_bin
        outputs['thrust_bin'] = thrust_bin    
        outputs['cp_bin'] = cp_bin
        outputs['ct_bin'] = ct_bin   
        
        
        
        
        
        
#############################################################################
##############################  UNIT TESTING ################################
#############################################################################     
if __name__ == "__main__":
    from WINDOW_openMDAO.src.api import beautify_dict
    import matplotlib.pyplot as plt
    
    ###################################################
    ############### Model Execution ###################
    ################################################### 
    inputs={'design_tsr' : 7.0, \
            'cut_in_speed' : 3.0, \
            'cut_out_speed' : 25.0, \
            'swept_area' : 12445.26, \
            'machine_rating' : 5000., \
            'drive_train_efficiency' : 0.95, \
            'rotor_cp' : 0.467403, \
            'rotor_ct' : 0.7410045}
    outputs={}
    
    model = PowerCurve(num_bins=30, rho_air=1.225)
      
    model.compute(inputs, outputs)  
    
    
    ###################################################
    ############### Post Processing ###################
    ################################################### 
    beautify_dict(inputs) 
    print '-'*10
    beautify_dict(outputs)  
    
    plots = {'Electrical Power (kW)'  : 'elec_power_bin', \
             'Aerodynamic Power (kW)' : 'aero_power_bin', \
             'Thrust (N)' : 'thrust_bin', \
             'C_p (-)' : 'cp_bin', \
             'C_t (-)' : 'ct_bin'}
    for key, value in plots.items():
        plt.plot(outputs['wind_bin'], outputs[value])
        plt.xlabel('Wind Speed (m/s)')
        plt.ylabel(key)
        plt.show() 
     
    


         
