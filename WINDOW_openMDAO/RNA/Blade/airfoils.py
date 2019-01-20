import pandas as pd
import re
import os 

#abs_path = os.path.dirname(os.path.realpath(__file__)).replace('\\', '//') + '//'
abs_path = 'Input//'
airfoil_folder = abs_path + 'Airfoils//'
airfoils_db = ['Cylinder1_10Hz.dat', 'Cylinder2_10Hz.dat', 'DU40_A17_10Hz.dat', 'DU35_A17_10Hz.dat', \
                'DU30_A17_10Hz.dat', 'DU25_A17_10Hz.dat', 'DU21_A17_10Hz.dat', 'NACA64_A17_10Hz.dat']




def AirfoilName(airfoil_id):
    '''
        returns the name of the airfoil from its ID
    '''
    
    airfoil_name = airfoil_folder + airfoils_db[airfoil_id]
    
    return airfoil_name





def ReadAirfoil(airfoil_id):
    '''
        returns the airfoil polar coordinates from its ID
    '''
    
    airfoil_name = AirfoilName(airfoil_id)
    
    with open(airfoil_name) as f:
        # skip rows until you reach the main table
        for line_number, line in enumerate(f):            
            search_data = re.search('(\d*)\s+(NumAlf)', line)
            if search_data:
                num_data = int(search_data.group(1))
                break  
          
    airfoil = pd.read_table(airfoil_name, sep='\s+', index_col=False,  header=None, \
                          names=['Alpha', 'Cl', 'Cd', 'Cm'], usecols=[0, 1, 2, 3], \
                          skiprows=line_number+3, nrows=num_data, engine='python')
    
    #print airfoil
    airfoil = airfoil.astype(float) # convert all data to float
    
    return airfoil







def AirfoilProperties(airfoil_id):
    '''
        returns the airfoil's optimal lift coefficient and angle of attack
    '''
    
    airfoil_name = AirfoilName(airfoil_id)
    airfoil = ReadAirfoil(airfoil_id)
    airfoil['Cl_Cd'] = airfoil['Cl']/airfoil['Cd']
    
    cl_opt = airfoil.loc[airfoil['Cl_Cd'].idxmax(), 'Cl']
    alpha_opt = airfoil.loc[airfoil['Cl_Cd'].idxmax(), 'Alpha']
    
    result = {'id' : airfoil_id, \
              'name' : airfoil_name, \
              'cl_opt' : cl_opt, \
              'alpha_opt' : alpha_opt}
    
    return result




            
         




        
if __name__ == "__main__":
    import numpy as np
    airfoil= ReadAirfoil(3)
    #print np.interp(50, airfoil.ix[:, 'Alpha'], airfoil.ix[:, 'Cl'])
    #print np.interp(50, airfoil.ix[:, 'Alpha'], airfoil.ix[:, 'Cd'])
    #print ReferenceTurbine
    print ReadAirfoil(3)
    
            