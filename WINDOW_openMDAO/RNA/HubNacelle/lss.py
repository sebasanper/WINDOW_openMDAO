import numpy as np
from math import pi, sin, cos

from WINDOW_openMDAO.src.api import AbsLSS
from drivese_utils import get_L_rb, get_My, get_Mz, size_LSS_3pt, resize_for_bearings, \
            size_LSS_4pt_Loop_1, size_LSS_4pt_Loop_2, get_rotor_mass


#############################################################################
##############################  MODEL#1: DriveSE ############################
#############################################################################        
class DriveSE3pt(AbsLSS):
    def compute(self, inputs, outputs):
        # metadata
        safety_factor = self.metadata['safety_factor']
        self.mb1Type = self.metadata['mb1_type']
        self.mb2Type = self.metadata['mb2_type']
        
        # inputs
        self.rotor_bending_moment_x = inputs['rotor_bending_moment'][0]*safety_factor
        self.rotor_bending_moment_y = inputs['rotor_bending_moment'][1]*safety_factor
        self.rotor_bending_moment_z = inputs['rotor_bending_moment'][2]*safety_factor
        self.rotor_force_x = inputs['rotor_force'][0]*safety_factor
        self.rotor_force_y = inputs['rotor_force'][1]*safety_factor
        self.rotor_force_z = inputs['rotor_force'][2]*safety_factor
        self.rotor_mass = inputs['rotor_mass']
        self.rotor_diameter = inputs['rotor_diameter']
        self.machine_rating = inputs['machine_rating']
        self.gearbox_mass = inputs['gearbox_mass']
        self.carrier_mass = np.polyval([-1.45658263e-04,  2.66106443e+00, -1.66386555e+03], self.machine_rating) # http://www.ntnglobal.com/en/products/review/pdf/NTN_TR76_en_p113_120.pdf
        self.overhang = inputs['overhang']
        self.L_rb = 0.0
        self.shrink_disc_mass = 333.3 * self.machine_rating/1000.0 # http://www.ringfeder.com/international/applications/energies/renewable/wind-turbine---shrink-discs-rfn-4051/wind-turbine---shrink-discs-rfn-4051/
        self.gearbox_cm = inputs['gearbox_cm']
        self.gearbox_length = inputs['gearbox_length']
        self.flange_length = 0.0
        self.shaft_angle = inputs['shaft_angle']
        self.shaft_ratio = 0.1 #inputs['shaft_ratio']        
        self.check_fatigue = 0   
        
        
        
        if self.flange_length == 0:
            self.flange_length = 0.3*(self.rotor_diameter/100.0)**2.0 - 0.1 * (self.rotor_diameter / 100.0) + 0.4

        if self.L_rb == 0: #distance from hub center to main bearing
            L_rb = get_L_rb(self.rotor_diameter, False)[0]
        else:
            L_rb = self.L_rb

        #If user does not know important moments, crude approx
        if self.rotor_mass > 0 and self.rotor_bending_moment_y == 0: 
            self.rotor_bending_moment_y=get_My(self.rotor_mass,L_rb)

        if self.rotor_mass > 0 and self.rotor_bending_moment_z == 0:
            self.rotor_bending_moment_z=get_Mz(self.rotor_mass,L_rb)

        self.g = 9.81 #m/s
        self.density = 7850.0


        self.L_ms_new = 0.0
        self.L_ms_0=0.5 # main shaft length downwind of main bearing
        self.L_ms=self.L_ms_0
        tol=1e-4 
        check_limit = 1.0
        dL=0.05
        self.D_max = 1.0
        self.D_min = 0.2

        T=self.rotor_bending_moment_x/1000.0

        #Main bearing defelection check
        if self.mb1Type == 'TRB1' or 'TRB2':
            Bearing_Limit = 3.0/60.0/180.0*pi
        elif self.mb1Type == 'CRB':
            Bearing_Limit = 4.0/60.0/180.0*pi
        elif self.mb1Type == 'SRB' or 'RB':
            Bearing_Limit = 0.078
        elif self.mb1Type == 'RB':
            Bearing_Limit = 0.002
        elif self.mb1Type == 'CARB':
            Bearing_Limit = 0.5/180*pi
        else:
            Bearing_Limit = False
        
        self.n_safety_brg = 1.0
        self.n_safety=2.5
        self.Sy = 66000#*self.S_ut/700e6 #psi
        self.E=2.1e11  
        N_count=50    
          
        self.u_knm_inlb = 8850.745454036
        self.u_in_m = 0.0254000508001
        counter=0
        length_max = self.overhang - L_rb + (self.gearbox_cm[0] -self.gearbox_length/2.) #modified length limit 7/29

        while abs(check_limit) > tol and self.L_ms_new < length_max:
            counter =counter+1
            if self.L_ms_new > 0:
                self.L_ms=self.L_ms_new
            else:
                self.L_ms=self.L_ms_0

            #-----------------------
            size_LSS_3pt(self)
            #-----------------------

            check_limit = abs(abs(self.theta_y[-1])-Bearing_Limit/self.n_safety_brg)
            #print 'deflection slope'
            #print Bearing_Limit
            #print 'threshold'
            #print theta_y[-1]
            self.L_ms_new = self.L_ms + dL        

#         # fatigue check Taylor Parsons 6/2014
#         if self.check_fatigue == 1 or 2:
#           #start_time = time.time()
#           #material properties 34CrNiMo6 steel +QT, large diameter
#           self.E=2.1e11
#           self.density=7800.0
#           self.n_safety = 2.5
#           if self.S_ut <= 0:
#             self.S_ut=700.0e6 #Pa
#           Sm=0.9*self.S_ut #for bending situations, material strength at 10^3 cycles
#           C_size=0.6 #diameter larger than 10"
#           C_surf=4.51*(self.S_ut/1e6)**-.265 #machined surface 272*(self.S_ut/1e6)**-.995 #forged
#           C_temp=1 #normal operating temps
#           C_reliab=0.814 #99% reliability
#           C_envir=1. #enclosed environment
#           Se=C_size*C_surf*C_temp*C_reliab*C_envir*.5*self.S_ut #modified endurance limit for infinite life
# 
#           if self.fatigue_exponent!=0:
#             if self.fatigue_exponent > 0:
#                 self.SN_b = - self.fatigue_exponent
#             else:
#                 self.SN_b = self.fatigue_exponent
#           else:
#             Nfinal = 5e8 #point where fatigue limit occurs under hypothetical S-N curve TODO adjust to fit actual data
#             z=log10(1e3)-log10(Nfinal)  #assuming no endurance limit (high strength steel)
#             self.SN_b=1/z*log10(Sm/Se)
#           self.SN_a=Sm/(1000.**self.SN_b)
#           # print 'm:', -1/self.SN_b
#           # print 'a:', self.SN_a
# 
#           if self.check_fatigue == 1:
#               #checks to make sure all inputs are reasonable
#               if self.rotor_mass < 100:
#                   [self.rotor_mass] = get_rotor_mass(self.machine_rating,False)
# 
#               #Rotor Loads calculations using DS472
#               setup_Fatigue_Loads(self)
# 
#               #upwind diameter calculations
#               iterationstep=0.001
#               diameter_limit = 1.5
#               while True:
# 
#                   get_Damage_Brng1(self)
# 
#                   if self.Damage < 1 or self.D_max >= diameter_limit:
#                       break
#                   else:
#                       self.D_max+=iterationstep
# 
#               #begin bearing calculations
#               N_bearings = self.N/self.blade_number #rotation number
# 
#               Fz1stoch = (-self.My_stoch)/(self.L_ms)
#               Fy1stoch = self.Mz_stoch/self.L_ms
#               Fz1determ = (self.weightGbx*self.L_gb - self.LssWeight*.5*self.L_ms - self.rotorWeight*(self.L_ms+L_rb)) / (self.L_ms)
# 
#               Fr_range = ((abs(Fz1stoch)+abs(Fz1determ))**2 +Fy1stoch**2)**.5 #radial stochastic + deterministic mean
#               Fa_range = self.Fx_stoch*cos(self.shaft_angle) + (self.rotorWeight+self.LssWeight)*sin(self.shaft_angle) #axial stochastic + mean
# 
#               life_bearing = self.N_f/self.blade_number
# 
#               [self.D_max_a,FW_max,bearingmass] = fatigue_for_bearings(self.D_max, Fr_range, Fa_range, N_bearings, life_bearing, self.mb1Type,False)
# 
#           # elif self.check_fatigue == 2:
#           #   Fx = self.rotor_thrust_distribution
#           #   n_Fx = self.rotor_thrust_count
#           #   Fy = self.rotor_Fy_distribution
#           #   n_Fy = self.rotor_Fy_count
#           #   Fz = self.rotor_Fz_distribution
#           #   n_Fz = self.rotor_Fz_count
#           #   Mx = self.rotor_torque_distribution
#           #   n_Mx = self.rotor_torque_count
#           #   My = self.rotor_My_distribution
#           #   n_My = self.rotor_My_count
#           #   Mz = self.rotor_Mz_distribution
#           #   n_Mz = self.rotor_Mz_count
# 
#           #   # print n_Fx
#           #   # print Fx*.5
#           #   # print Mx*.5
#           #   # print -1/self.SN_b
# 
#           #   def Ninterp(L_ult,L_range,m):
#           #       return (L_ult/(.5*L_range))**m #TODO double-check that the input will be the load RANGE instead of load amplitudes. Also, may include means?
# 
#           #   #upwind bearing calcs
#           #   diameter_limit = 5.0
#           #   iterationstep=0.001
#           #   #upwind bearing calcs
#           #   while True:
#           #       self.Damage = 0
#           #       Fx_ult = self.SN_a*(pi/4.*(self.D_max**2-self.D_in**2))
#           #       Fyz_ult = self.SN_a*(pi*(self.D_max**4-self.D_in**4))/(self.D_max*32*self.L_rb)
#           #       Mx_ult = self.SN_a*(pi*(self.D_max**4-self.D_in**4))/(32*(3.**.5)*self.D_max)
#           #       Myz_ult = self.SN_a*(pi*(self.D_max**4-self.D_in**4))/(self.D_max*64.)
#           #       if Fx_ult and np.all(n_Fx):
#           #           self.Damage+=scp.integrate.simps(n_Fx/Ninterp(Fx_ult,Fx,-1/self.SN_b),x=n_Fx,even = 'avg')
#           #       if Fyz_ult:
#           #           if np.all(n_Fy):
#           #               self.Damage+=scp.integrate.simps(abs(n_Fy/Ninterp(Fyz_ult,Fy,-1/self.SN_b)),x=n_Fy,even = 'avg')
#           #           if np.all(n_Fz):
#           #               self.Damage+=scp.integrate.simps(abs(n_Fz/Ninterp(Fyz_ult,Fz,-1/self.SN_b)),x=n_Fz,even = 'avg')
#           #       if Mx_ult and np.all(n_Mx):
#           #           self.Damage+=scp.integrate.simps(abs(n_Mx/Ninterp(Mx_ult,Mx,-1/self.SN_b)),x=n_Mx,even = 'avg')
#           #       if Myz_ult:
#           #           if np.all(n_My):
#           #               self.Damage+=scp.integrate.simps(abs(n_My/Ninterp(Myz_ult,My,-1/self.SN_b)),x=n_My,even = 'avg')
#           #           if np.all(n_Mz):
#           #               self.Damage+=scp.integrate.simps(abs(n_Mz/Ninterp(Myz_ult,Mz,-1/self.SN_b)),x=n_Mz,even = 'avg')
# 
#           #       print 'Upwind Bearing Diameter:', self.D_max
#           #       print 'self.Damage:', self.Damage
# 
#           #       if self.Damage <= 1 or self.D_max >= diameter_limit:
#           #           # print 'Upwind Bearing Diameter:', self.D_max
#           #           # print 'self.Damage:', self.Damage
#           #           #print (time.time() - start_time), 'seconds of total simulation time'
#           #           break
#           #       else:
#           #           self.D_max+=iterationstep
# 
#           #   #bearing calcs
#           #   if self.availability != 0 and rotor_freq != 0 and self.T_life != 0 and self.cut_out != 0 and self.weibull_A != 0:
#           #       N_rotations = self.availability*rotor_freq/60.*(self.T_life*365*24*60*60)*exp(-(self.cut_in/self.weibull_A)**self.weibull_k)-exp(-(self.cut_out/self.weibull_A)**self.weibull_k)
#           #   elif np.max(n_Fx > 1e6):
#           #       N_rotations = np.max(n_Fx)/self.blade_number
#           #   elif np.max(n_My > 1e6):
#           #       N_rotations = np.max(n_My)/self.blade_number
# 
#           #   # Fz1 = (Fz*(self.L_ms+self.L_rb)+My)/self.L_ms
#           #   Fz1_Fz = Fz*(self.L_ms+self.L_rb)/self.L_ms #force in z direction due to Fz
#           #   Fz1_My = My/self.L_ms #force in z direction due to My
#           #   Fy1_Fy = -Fy*(self.L_ms+self.L_rb)/self.L_ms
#           #   Fy1_Mz = Mz/self.L_ms
#           #   [self.D_max_a,FW_max,bearingmass] = fatigue2_for_bearings(self.D_max,self.mb1Type,np.zeros(2),np.array([1,2]),Fy1_Fy,n_Fy/self.blade_number,Fz1_Fz,n_Fz/self.blade_number,Fz1_My,n_My/self.blade_number,Fy1_Mz,n_Mz/self.blade_number,N_rotations)
#          
        #resize bearing if no fatigue check
        if self.check_fatigue == 0:
            [self.D_max_a,FW_max,bearingmass] = resize_for_bearings(self.D_max,  self.mb1Type,False)

        [self.D_min_a,FW_min,trash] = resize_for_bearings(self.D_min,  self.mb2Type,False) #mb2 is a representation of the gearbox connection
            
        lss_mass_new=(pi/3)*(self.D_max_a**2+self.D_min_a**2+self.D_max_a*self.D_min_a)*(self.L_ms-(FW_max+FW_min)/2)*self.density/4+ \
                         (pi/4)*(self.D_max_a**2-self.D_in**2)*self.density*FW_max+\
                         (pi/4)*(self.D_min_a**2-self.D_in**2)*self.density*FW_min-\
                         (pi/4)*(self.D_in**2)*self.density*(self.L_ms+(FW_max+FW_min)/2)
        lss_mass_new *= 1.35 # add flange and shrink disk mass
        self.length=self.L_ms_new + (FW_max+FW_min)/2 + self.flange_length
        #print ("self.L_ms: {0}").format(self.L_ms)
        #print ("LSS length, m: {0}").format(self.length)
        self.D_outer=self.D_max
        #print ("Upwind MB OD, m: {0}").format(self.D_max_a)
        #print ("CB OD, m: {0}").format(self.D_min_a)
        #print ("self.D_min: {0}").format(self.D_min)
        self.D_in=self.D_in
        self.mass=lss_mass_new
        self.diameter1= self.D_max_a
        self.diameter2= self.D_min_a 
        #self.length=self.L_ms
        #print self.length
        self.D_outer=self.D_max_a
        self.diameter=self.D_max_a

        # calculate mass properties
        downwind_location = np.array([self.gearbox_cm[0]-self.gearbox_length/2. , self.gearbox_cm[1] , self.gearbox_cm[2] ])

        bearing_location1 = np.array([0.,0.,0.]) #upwind
        bearing_location1[0] = downwind_location[0] - self.L_ms*cos(self.shaft_angle)
        bearing_location1[1] = downwind_location[1]
        bearing_location1[2] = downwind_location[2] + self.L_ms*sin(self.shaft_angle)
        self.bearing_location1 = bearing_location1

        self.bearing_location2 = np.array([0.,0.,0.]) #downwind does not exist

        cm = np.array([0.0,0.0,0.0])
        self.cm = cm
        cm[0] = downwind_location[0] - 0.65*self.length*cos(self.shaft_angle) #From solid models, center of mass with flange (not including shrink disk) very nearly .65*total_length
        cm[1] = downwind_location[1]
        cm[2] = downwind_location[2] + 0.65*self.length*sin(self.shaft_angle)

        #including shrink disk mass
        self.cm[0] = (cm[0]*self.mass + downwind_location[0]*self.shrink_disc_mass) / (self.mass+self.shrink_disc_mass) 
        self.cm[1] = cm[1]
        self.cm[2] = (cm[2]*self.mass + downwind_location[2]*self.shrink_disc_mass) / (self.mass+self.shrink_disc_mass)
        # print 'shaft before shrink disk:', self.mass
        self.mass+=self.shrink_disc_mass

        I = np.array([0.0, 0.0, 0.0])
        I[0]  = self.mass * (self.D_in ** 2.0 + self.D_outer ** 2.0) / 8.0
        I[1]  = self.mass * (self.D_in ** 2.0 + self.D_outer ** 2.0 + (4.0 / 3.0) * (self.length ** 2.0)) / 16.0
        I[2]  = I[1]
        self.I = I

        # print 'self.L_rb %8.f' %(self.L_rb) #*(self.machine_rating/5.0e3)   #distance from hub center to main bearing scaled off NREL 5MW
        # print 'L_bg %8.f' %(L_bg) #*(self.machine_rating/5.0e3)         #distance from hub center to gearbox yokes
        # print 'L_as %8.f' %(L_as) #distance from main bearing to shaft center
      
        self.FW_mb=FW_max
        self.bearing_mass1 = bearingmass
        self.bearing_mass2 = 0.        
        
        
        
        # outputs
        outputs['length'] = self.length
        outputs['diameter1'] = self.diameter1
        outputs['diameter2'] = self.diameter2
        outputs['mass'] = self.mass
        outputs['cm'] = self.cm
        outputs['I'] = self.I
        outputs['FW_mb1'] = self.FW_mb
        outputs['bearing_mass1'] = self.bearing_mass1
        outputs['bearing_mass2'] = self.bearing_mass2
        outputs['bearing_location1'] = self.bearing_location1
        outputs['bearing_location2'] = self.bearing_location2 
        
        






#############################################################################
##############################  MODEL#2: DriveSE ############################
#############################################################################        
class DriveSE4pt(AbsLSS):
    def compute(self, inputs, outputs):
        # metadata
        safety_factor = self.metadata['safety_factor']
        self.mb1Type = self.metadata['mb1_type']
        self.mb2Type = self.metadata['mb2_type']
        
        # inputs
        self.rotor_bending_moment_x = inputs['rotor_bending_moment'][0]*safety_factor
        self.rotor_bending_moment_y = inputs['rotor_bending_moment'][1]*safety_factor
        self.rotor_bending_moment_z = inputs['rotor_bending_moment'][2]*safety_factor
        self.rotor_force_x = inputs['rotor_force'][0]*safety_factor
        self.rotor_force_y = inputs['rotor_force'][1]*safety_factor
        self.rotor_force_z = inputs['rotor_force'][2]*safety_factor
        self.rotor_mass = inputs['rotor_mass']
        self.rotor_diameter = inputs['rotor_diameter']
        self.machine_rating = inputs['machine_rating']
        self.gearbox_mass = inputs['gearbox_mass']
        self.carrier_mass = np.polyval([-1.45658263e-04,  2.66106443e+00, -1.66386555e+03], self.machine_rating)
        self.overhang = inputs['overhang']
        self.L_rb = 0.0
        self.shrink_disc_mass = 333.3 * self.machine_rating / 1000.0
        self.gearbox_cm = inputs['gearbox_cm']
        self.gearbox_length = inputs['gearbox_length']
        self.flange_length = 0.0
        self.shaft_angle = inputs['shaft_angle']
        self.shaft_ratio = 0.1 #inputs['shaft_ratio']        
        self.check_fatigue = 0  
        
        
        
        #input parameters
        self.g=9.81

        if self.L_rb == 0: #distance from hub center to main bearing
            L_rb = 0.007835*self.rotor_diameter+0.9642
        else:
            L_rb = self.L_rb

        #If user does not know important moments, crude approx
        if self.rotor_mass > 0 and self.rotor_bending_moment_y == 0: 
            self.rotor_bending_moment_y=get_My(self.rotor_mass,L_rb)

        if self.rotor_mass > 0 and self.rotor_bending_moment_z == 0:
            self.rotor_bending_moment_z=get_Mz(self.rotor_mass,L_rb)

        if self.rotor_mass ==0:
            [self.rotor_mass] = get_rotor_mass(self.machine_rating,False)

        if self.flange_length == 0:
            self.flange_length = 0.3*(self.rotor_diameter/100.0)**2.0 - 0.1 * (self.rotor_diameter / 100.0) + 0.4
                
        # initialization for iterations    
        self.L_ms_new = 0.0
        self.L_ms_0=0.5 # main shaft length downwind of main bearing
        self.L_ms=self.L_ms_0
        self.len_pts=101
        self.D_max=1
        self.D_min=0.2

        tol=1e-4 
        check_limit = 1.0
        dL=0.05
        counter = 0
        N_count=50
        N_count_2=2

        #Distances
        self.L_bg = 6.11-L_rb    #distance from first main bearing to gearbox yokes  # to add as an input
        self.L_as = self.L_ms/2.0     #distance from main bearing to shaft center
        self.L_gb = 0.0          #distance to gbx center from trunnions in x-dir # to add as an input
        self.H_gb = 1.0          #distance to gbx center from trunnions in z-dir # to add as an input     
        self.L_gp = 0.825        #distance from gbx coupling to gbx trunnions
        self.L_cu = self.L_ms + 0.5   #distance from upwind main bearing to upwind carrier bearing 0.5 meter is an estimation # to add as an input
        self.L_cd = self.L_cu + 0.5   #distance from upwind main bearing to downwind carrier bearing 0.5 meter is an estimation # to add as an input
        
        #material properties
        self.E=2.1e11
        self.density=7800.0
        self.n_safety = 2.5 # According to AGMA, takes into account the peak load safety factor
        self.Sy = 66000#*self.S_ut/700e6 #66000 #psi

        #unit conversion
        self.u_knm_inlb = 8850.745454036
        self.u_in_m = 0.0254000508001

        #Main bearing defelection check
        if self.mb1Type == 'TRB1' or 'TRB2':
            Bearing_Limit = 3.0/60.0/180.0*pi
        elif self.mb1Type == 'CRB':
            Bearing_Limit = 4.0/60.0/180.0*pi
        elif self.mb1Type == 'SRB' or 'RB':
            Bearing_Limit = 0.078
        elif self.mb1Type == 'RB':
            Bearing_Limit = 0.002
        elif self.mb1Type == 'CARB':
            Bearing_Limit = 0.5/180*pi
        else:
            Bearing_Limit = False

        #Second bearing defelection check
        if self.mb2Type == 'TRB1' or 'TRB2':
            Bearing_Limit2 = 3.0/60.0/180.0*pi
        elif self.mb2Type == 'CRB':
            Bearing_Limit2 = 4.0/60.0/180.0*pi
        elif self.mb2Type == 'SRB' or 'RB':
            Bearing_Limit2 = 0.078
        elif self.mb2Type == 'RB':
            Bearing_Limit2 = 0.002
        elif self.mb2Type == 'CARB':
            Bearing_Limit2 = 0.5/180*pi
        else:
            Bearing_Limit2 = False

        self.n_safety_brg = 1.0

        length_max = self.overhang - L_rb + (self.gearbox_cm[0] -self.gearbox_length/2.) #modified length limit 7/29/14

        while abs(check_limit) > tol and self.L_ms_new < length_max:
            counter = counter+1
            if self.L_ms_new > 0:
                self.L_ms=self.L_ms_new
            else:
                self.L_ms=self.L_ms_0

            size_LSS_4pt_Loop_1(self)

            check_limit = abs(abs(self.theta_y[-1])-Bearing_Limit/self.n_safety_brg)

            if check_limit < 0:
                self.L_ms_new = self.L_ms + dL

            else:
                self.L_ms_new = self.L_ms + dL

        #Initialization
        self.L_mb=self.L_ms_new
        counter_ms=0
        check_limit_ms=1.0
        self.L_mb_new=0.0
        self.L_mb_0=self.L_mb                     #main shaft length
        self.L_ms = self.L_ms_new
        dL_ms = 0.05
        dL = 0.0025

        while abs(check_limit_ms)>tol and self.L_mb_new < length_max:
            counter_ms= counter_ms + 1
            if self.L_mb_new > 0:
                self.L_mb=self.L_mb_new
            else:
                self.L_mb=self.L_mb_0

            counter = 0.0
            check_limit=1.0
            self.L_ms_gb_new=0.0
            self.L_ms_0=0.5 #mainshaft length
            self.L_ms = self.L_ms_0


            while abs(check_limit) > tol and counter <N_count_2:
                counter =counter+1
                if self.L_ms_gb_new>0.0:
                    self.L_ms_gb = self.L_ms_gb_new
                else:
                    self.L_ms_gb = self.L_ms_0

                size_LSS_4pt_Loop_2(self)

                check_limit = abs(abs(self.theta_y[-1])-Bearing_Limit/self.n_safety_brg)

                if check_limit < 0:
                    self.L_ms__gb_new = self.L_ms_gb + dL
                else:
                    self.L_ms__gb_new = self.L_ms_gb + dL

                check_limit_ms = abs(abs(self.theta_y[-1]) - Bearing_Limit2/self.n_safety_brg)

                if check_limit_ms < 0:
                    self.L_mb_new = self.L_mb + dL_ms
                else:
                    self.L_mb_new = self.L_mb + dL_ms

#         # fatigue check Taylor Parsons 6/14
#         if self.check_fatigue == 1 or self.check_fatigue == 2:
#           #start_time = time.time()
# 
#           #checks to make sure all inputs are reasonable
#           if self.rotor_mass < 100:
#               [self.rotor_mass] = get_rotor_mass(self.machine_rating,False)
# 
#           #material properties 34CrNiMo6 steel +QT, large diameter
#           self.n_safety = 2.5
#           if self.S_ut <= 0:
#             self.S_ut=700.0e6 #Pa
# 
#           #calculate material props for fatigue
#           Sm=0.9*self.S_ut #for bending situations, material strength at 10^3 cycles
# 
#           if self.fatigue_exponent!=0:
#             if self.fatigue_exponent > 0:
#                 self.SN_b = - self.fatigue_exponent
#             else:
#                 self.SN_b = self.fatigue_exponent
#           else:
#               C_size=0.6 #diameter larger than 10"
#               C_surf=4.51*(self.S_ut/1e6)**-.265 #machined surface 272*(self.S_ut/1e6)**-.995 #forged
#               C_temp=1 #normal operating temps
#               C_reliab=0.814 #99% reliability
#               C_envir=1. #enclosed environment
#               Se=C_size*C_surf*C_temp*C_reliab*C_envir*.5*self.S_ut #modified endurance limit for infinite life (should be Sf)\
#               Nfinal = 5e8 #point where fatigue limit occurs under hypothetical S-N curve TODO adjust to fit actual data
#               z=log10(1e3)-log10(Nfinal)  #assuming no endurance limit (high strength steel)
#               self.SN_b=1/z*log10(Sm/Se)
#           self.SN_a=Sm/(1000.**self.SN_b)
#           # print 'fatigue_exponent:',self.SN_b
#           # print 'm:', -1/self.SN_b
#           # print 'a:', self.SN_a
#           if self.check_fatigue == 1:
# 
#               setup_Fatigue_Loads(self)
# 
#               #upwind bearing calculations
#               iterationstep=0.001
#               diameter_limit = 5.0
#               while True:
#                   get_Damage_Brng1(self)
#                   if self.Damage < 1 or self.D_max >= diameter_limit:
#                       break
#                   else:
#                       self.D_max+=iterationstep
# 
#               #downwind bearing calculations
#               diameter_limit = 5.0
#               iterationstep=0.001
#               while True:
#                   get_Damage_Brng2(self)
#                   if self.Damage < 1 or self.D_med >= diameter_limit:
#                       break
#                   else:
#                       self.D_med+=iterationstep
# 
#               #begin bearing calculations
#               N_bearings = self.N/self.blade_number #counts per rotation (not defined by characteristic frequency 3n_rotor)
# 
#               Fr1_range = ((abs(self.Fz1stoch)+abs(self.Fz1determ))**2 +self.Fy1stoch**2)**.5 #radial stochastic + deterministic mean
#               Fa1_range = np.zeros(len(self.Fy1stoch))
# 
#               #...calculate downwind forces
#               lss_weight=self.density*9.81*(((pi/12)*(self.D_max**2+self.D_med**2+self.D_max*self.D_med)*(self.L_mb))-(pi/4*self.L_mb*self.D_in**2))
#               Fy2stoch = -self.Mz_stoch/(self.L_mb) #= -Fy1 - Fy_stoch
#               Fz2stoch = -(lss_weight*2./3.*self.L_mb-self.My_stoch)/(self.L_mb) + (lss_weight+self.shrinkDiscWeight+self.gbxWeight)*cos(self.shaft_angle) - self.rotorWeight #-Fz1 +Weights*cos(gamma)-Fz_stoch+Fz_mean (Fz_mean is in negative direction)
#               Fr2_range = (Fy2stoch**2+(Fz2stoch+abs(-self.rotorWeight*L_rb + 0.5*lss_weight+self.gbxWeight*self.L_gb/self.L_mb))**2)**0.5
#               Fa2_range = self.Fx_stoch*cos(self.shaft_angle) + (self.rotorWeight+lss_weight)*sin(self.shaft_angle) #axial stochastic + mean
# 
#               life_bearing = self.N_f/self.blade_number
# 
#               [self.D_max_a,FW_max,bearing1mass] = fatigue_for_bearings(self.D_max, Fr1_range, Fa1_range, N_bearings, life_bearing, self.mb1Type,False)
#               [self.D_med_a,FW_med,bearing2mass] = fatigue_for_bearings(self.D_med, Fr2_range, Fa2_range, N_bearings, life_bearing, self.mb2Type,False)
# 
#           # elif self.check_fatigue == 2: # untested and not used currently
#           #   Fx = self.rotor_thrust_distribution
#           #   n_Fx = self.rotor_thrust_count
#           #   Fy = self.rotor_Fy_distribution
#           #   n_Fy = self.rotor_Fy_count
#           #   Fz = self.rotor_Fz_distribution
#           #   n_Fz = self.rotor_Fz_count
#           #   Mx = self.rotor_torque_distribution
#           #   n_Mx = self.rotor_torque_count
#           #   My = self.rotor_My_distribution
#           #   n_My = self.rotor_My_count
#           #   Mz = self.rotor_Mz_distribution
#           #   n_Mz = self.rotor_Mz_count
# 
#           #   print n_Fx
#           #   print Fx*.5
#           #   print Mx*.5
#           #   print -1/self.SN_b
# 
#           #   def Ninterp(L_ult,L_range,m):
#           #       return (L_ult/(.5*L_range))**m #TODO double-check that the input will be the load RANGE instead of load amplitudes. May also include means
# 
#           #   #upwind bearing calcs
#           #   diameter_limit = 5.0
#           #   iterationstep=0.001
#           #   #upwind bearing calcs
#           #   while True:
#           #       self.Damage = 0
#           #       Fx_ult = self.SN_a*(pi/4.*(self.D_max**2-self.D_in**2))
#           #       Fyz_ult = self.SN_a*(pi*(self.D_max**4-self.D_in**4))/(self.D_max*64.)/self.L_rb
#           #       Mx_ult = self.SN_a*(pi*(self.D_max**4-self.D_in**4))/(32*(3)**.5*self.D_max)
#           #       Myz_ult = self.SN_a*(pi*(self.D_max**4-self.D_in**4))/(self.D_max*64.)
#           #       if Fx_ult !=0 and np.all(n_Fx) != 0:
#           #           self.Damage+=scp.integrate.simps(n_Fx/Ninterp(Fx_ult,Fx,-1/self.SN_b),x=n_Fx,even = 'avg')
#           #       if Fyz_ult !=0:
#           #           if np.all(n_Fy) != 0:
#           #               self.Damage+=scp.integrate.simps(abs(n_Fy/Ninterp(Fyz_ult,Fy,-1/self.SN_b)),x=n_Fy,even = 'avg')
#           #           if np.all(n_Fz) != 0:
#           #               self.Damage+=scp.integrate.simps(abs(n_Fz/Ninterp(Fyz_ult,Fz,-1/self.SN_b)),x=n_Fz,even = 'avg')
#           #       if Mx_ult !=0 and np.all(n_Mx) != 0:
#           #           self.Damage+=scp.integrate.simps(abs(n_Mx/Ninterp(Mx_ult,Mx,-1/self.SN_b)),x=n_Mx,even = 'avg')
#           #       if Myz_ult!=0:
#           #           if np.all(n_My) != 0:
#           #               self.Damage+=scp.integrate.simps(abs(n_My/Ninterp(Myz_ult,My,-1/self.SN_b)),x=n_My,even = 'avg')
#           #           if np.all(n_Mz) != 0:
#           #               self.Damage+=scp.integrate.simps(abs(n_Mz/Ninterp(Myz_ult,Mz,-1/self.SN_b)),x=n_Mz,even = 'avg')
# 
#           #       print 'Upwind Bearing Diameter:', self.D_max
#           #       print 'self.Damage:', self.Damage
# 
#           #       if self.Damage <= 1 or self.D_max >= diameter_limit:
#           #           # print 'Upwind Bearing Diameter:', self.D_max
#           #           # print 'self.Damage:', self.Damage
#           #           #print (time.time() - start_time), 'seconds of total simulation time'
#           #           break
#           #       else:
#           #           self.D_max+=iterationstep
#           #   #downwind bearing calcs
#           #   while True:
#           #       self.Damage = 0
#           #       Fx_ult = self.SN_a*(pi/4.*(self.D_med**2-self.D_in**2))
#           #       Mx_ult = self.SN_a*(pi*(self.D_med**4-self.D_in**4))/(32*(3)**.5*self.D_med)
#           #       if Fx_ult !=0:
#           #           self.Damage+=scp.integrate.simps(n_Fx/Ninterp(Fx_ult,Fx,-1/self.SN_b),x=n_Fx,even = 'avg')
#           #       if Mx_ult !=0:
#           #           self.Damage+=scp.integrate.simps(n_Mx/Ninterp(Mx_ult,Mx,-1/self.SN_b),x=n_Mx,even = 'avg')
#           #       print 'Downwind Bearing Diameter:', self.D_med
#           #       print 'self.Damage:', self.Damage
# 
#           #       if self.Damage <= 1 or self.D_med>= diameter_limit:
#           #           # print 'Upwind Bearing Diameter:', self.D_max
#           #           # print 'self.Damage:', self.Damage
#           #           #print (time.time() - start_time), 'seconds of total simulation time'
#           #           break
#           #       else:
#           #           self.D_med+=iterationstep
# 
#           #   #bearing calcs
#           #   if self.availability != 0 and rotor_freq != 0 and self.T_life != 0 and self.cut_out != 0 and self.weibull_A != 0:
#           #       N_rotations = self.availability*rotor_freq/60.*(self.T_life*365*24*60*60)*exp(-(self.cut_in/self.weibull_A)**self.weibull_k)-exp(-(self.cut_out/self.weibull_A)**self.weibull_k)
#           #   elif np.max(n_Fx > 1e6):
#           #       N_rotations = np.max(n_Fx)/self.blade_number
#           #   elif np.max(n_My > 1e6):
#           #       N_rotations = np.max(n_My)/self.blade_number
#           #   # print 'Upwind bearing calcs'
#           #   Fz1_Fz = Fz*(self.L_mb+self.L_rb)/self.L_mb
#           #   Fz1_My = My/self.L_mb
#           #   Fy1_Fy = -Fy*(self.L_mb+self.L_rb)/self.L_mb
#           #   Fy1_Mz = Mz/self.L_mb
#           #   [self.D_max_a,FW_max,bearing1mass] = fatigue2_for_bearings(self.D_max,self.mb1Type,np.zeros(2),np.array([1,2]),Fy1_Fy,n_Fy/self.blade_number,Fz1_Fz,n_Fz/self.blade_number,Fz1_My,n_My/self.blade_number,Fy1_Mz,n_Mz/self.blade_number,N_rotations)
#           #   # print 'Downwind bearing calcs'
#           #   Fz2_Fz = Fz*self.L_rb/self.L_mb
#           #   Fz2_My = My/self.L_mb
#           #   Fy2_Fy = Fy*self.L_rb/self.L_mb
#           #   Fy2_Mz = Mz/self.L_mb
#           #   [self.D_med_a,FW_med,bearing2mass] = fatigue2_for_bearings(self.D_med,self.mb2Type,Fx,n_Fx/self.blade_number,Fy2_Fy,n_Fy/self.blade_number,Fz2_Fz,n_Fz/self.blade_number,Fz2_My,n_My/self.blade_number,Fy2_Mz,n_Mz/self.blade_number,N_rotations)

        if self.check_fatigue == 0: #if fatigue_check is not true, resize based on diameter            
            [self.D_max_a,FW_max,bearing1mass] = resize_for_bearings(self.D_max,  self.mb1Type,False)
            [self.D_med_a,FW_med,bearing2mass] = resize_for_bearings(self.D_med,  self.mb2Type,False)

        # end fatigue code additions 6/2014
            
        lss_mass_new=(pi/3)*(self.D_max_a**2+self.D_med_a**2+self.D_max_a*self.D_med_a)*(self.L_mb-(FW_max+FW_med)/2)*self.density/4+ \
                         (pi/4)*(self.D_max_a**2-self.D_in**2)*self.density*FW_max+\
                         (pi/4)*(self.D_med_a**2-self.D_in**2)*self.density*FW_med-\
                         (pi/4)*(self.D_in**2)*self.density*(self.L_mb+(FW_max+FW_med)/2)

        ## begin bearing routine with updated shaft mass
        self.length=self.L_mb_new + (FW_max+FW_med)/2 + self.flange_length # add facewidths and flange
        # print ("self.L_mb: {0}").format(self.L_mb)
        # print ("LSS length, m: {0}").format(self.length)
        self.D_outer=self.D_max
        # print ("Upwind MB OD, m: {0}").format(self.D_max_a)
        # print ("Dnwind MB OD, m: {0}").format(self.D_med_a)
        # print ("self.D_min: {0}").format(self.D_min)
        self.D_in=self.D_in
        self.mass=lss_mass_new*1.33 # add flange mass
        self.diameter1= self.D_max_a
        self.diameter2= self.D_med_a 

        # calculate mass properties
        downwind_location = np.array([self.gearbox_cm[0]-self.gearbox_length/2. , self.gearbox_cm[1] , self.gearbox_cm[2] ])

        bearing_location1 = np.array([0.,0.,0.]) #upwind
        bearing_location1[0] = downwind_location[0] - (self.L_mb_new + FW_med/2)*cos(self.shaft_angle)
        bearing_location1[1] = downwind_location[1]
        bearing_location1[2] = downwind_location[2] + (self.L_mb_new + FW_med/2)*sin(self.shaft_angle)
        self.bearing_location1 = bearing_location1

        bearing_location2 = np.array([0.,0.,0.]) #downwind
        bearing_location2[0] = downwind_location[0] - FW_med*.5*cos(self.shaft_angle)
        bearing_location2[1] = downwind_location[1]
        bearing_location2[2] = downwind_location[2] + FW_med*.5*sin(self.shaft_angle)
        self.bearing_location2 = bearing_location2

        cm = np.array([0.0,0.0,0.0])
        self.cm = cm
        cm[0] = downwind_location[0] - 0.65*self.length*cos(self.shaft_angle) #From solid models, center of mass with flange (not including shrink disk) very nearly .65*total_length
        cm[1] = downwind_location[1]
        cm[2] = downwind_location[2] + 0.65*self.length*sin(self.shaft_angle)

        #including shrink disk mass
        self.cm[0] = (cm[0]*self.mass + downwind_location[0]*self.shrink_disc_mass) / (self.mass+self.shrink_disc_mass) 
        self.cm[1] = cm[1]
        self.cm[2] = (cm[2]*self.mass + downwind_location[2]*self.shrink_disc_mass) / (self.mass+self.shrink_disc_mass)
        self.mass+=self.shrink_disc_mass

        I = np.array([0.0, 0.0, 0.0])
        I[0]  = self.mass * (self.D_in ** 2.0 + self.D_outer ** 2.0) / 8.0
        I[1]  = self.mass * (self.D_in ** 2.0 + self.D_outer ** 2.0 + (4.0 / 3.0) * (self.length ** 2.0)) / 16.0
        I[2]  = I[1]
        self.I = I

        self.FW_mb1 = FW_max
        self.FW_mb2 = FW_med

        self.bearing_mass1 = bearing1mass
        self.bearing_mass2 = bearing2mass 
        
        
        # outputs
        outputs['length'] = self.length
        outputs['diameter1'] = self.diameter1
        outputs['diameter2'] = self.diameter2
        outputs['mass'] = self.mass
        outputs['cm'] = self.cm
        outputs['I'] = self.I
        outputs['FW_mb1'] = self.FW_mb1
        outputs['FW_mb2'] = self.FW_mb2
        outputs['bearing_mass1'] = self.bearing_mass1
        outputs['bearing_mass2'] = self.bearing_mass2
        outputs['bearing_location1'] = self.bearing_location1
        outputs['bearing_location2'] = self.bearing_location2 


#############################################################################
##############################  UNIT TESTING ################################
#############################################################################  
if __name__ == "__main__":
    from WINDOW_openMDAO.src.api import beautify_dict
    
    ###################################################
    ############### Model Execution ###################
    ################################################### 
    inputs={'rotor_bending_moment' : [330770.0, -16665000.0 , 2896300.0], \
            'rotor_force' : [599610.0, 186780.0 , -842710.0 ], \
            'rotor_mass' : 0.0, \
            'rotor_diameter' : 126.0, \
            'machine_rating' : 5000.0, \
            'gearbox_mass' : 0.0, \
            'overhang' : 5.0, \
            'gearbox_cm' :  [0., 0., 0.], \
            'gearbox_length' : 0, \
            'shaft_angle': 5.0}
    outputs={}
    
    #model = DriveSE3pt(safety_factor=1.5, mb1_type='CARB', mb2_type='SRB')
    model = DriveSE4pt(safety_factor=1.5, mb1_type='CARB', mb2_type='SRB')
      
    model.compute(inputs, outputs)  
    
    
    ###################################################
    ############### Post Processing ###################
    ################################################### 
    beautify_dict(inputs) 
    print '-'*10
    beautify_dict(outputs)  

        