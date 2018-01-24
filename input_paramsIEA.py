from numpy import sqrt
import numpy as np


turbine_voltage = 66000.0
turbine_rated_power = 10000000.0
cutin_wind_speed = 4.0
cutout_wind_speed = 25.0

hub_height = 119.0
solidity_rotor = 0.0516  # [-] 'Generic' value, based on Peter Jamieson's book - Figure 2.5 - P.53
cd_rotor_idle_vane = 0.4  # [-] 'Generic' value, very dependent on angle of attack and therefore the assumed rotor misalignment
# cd_rotor_idle_failed_pitch = 1.2 # [-]
cd_nacelle = 1.2  # [-] OWTES V66: 1.3, but using a frontal area of 13 m^2
front_area_nacelle = 14.0  # [m^2] Vestas V80 brochure: height for transport 4 m, width 3.4 m, rounded up 14 m^2 to include height including cooler top 5.4 m
max_thrust = 1500000.0  # [N] Maximum thrust determined from thrust coefficient curve multiplied with 1.5 amplification factor (determined by Otto for NREL 5 MW turbine)
yaw_to_hub_height = 5.01  # [m]
mass = 589211.0  # [kg] 296,780 kg nacelle + 3x 17.74 ton blades
mass_eccentricity = 1.9  # [m] - in x-direction, so negative when upwind of tower centre
yaw_diameter = 5.5  # [m]
rotor_radius = 95.4  # [m]
wind_speed_at_max_thrust = 11.4  # [m/s]
generator_voltage = 4000.0  # [V] There are 480 and 690 voltage versions of the V80. The higher voltage is assumed, considering the need of high voltage in the connections to the public grid.
purchase_price = 10000000.0  # [Euro]
warranty_percentage = 15  # [%]

# central_platform = [[498000.0, 5731000.0], [490000.0, 5725000.0], [492000.0, 5732000.0]]
central_platform = [0, 498000.0, 5731000.0]
number_turbines_per_cable = [2, 4, 7]
n_quadrilaterals = 2
areas = np.array([[[484178.55, 5732482.8], [500129.9, 5737534.4], [497318.1, 5731880.24], [491858.00, 5725044.75]], [[491858.00, 5725044.75], [497318.1, 5731880.24], [503163.37, 5729155.3], [501266.5, 5715990.05]]])  # Areas need to be defined in clockwise order starting on the "bottom left" corner.

# Physical Environment
ref_height_wind_speed = 90.0
alpha = 0.10  # Approximate mean value of fits to data in ECN report and paper of Tambke (EWEC 2004)
hat = 2.05  # Horns Rev website: Tides are approximately 1.2 m; Paper ICCE: appr. 1.5 m - A little more than half of this is taken for 'extrapolation'
lat = - 1.6  # Horns Rev website: Tides are approximately 1.2 m; Paper ICCE: appr. 1.5 m - A little more than half of this is taken for 'extrapolation'
storm_surge_pos = 2.5  # Paper ICCE
storm_surge_neg = - 0.5  # Guess
Hs_50_year = 5.0  # Horns Rev website: Highest value in graph of Hm0 is 4.3. Somewhat higher value taken for 'extrapolation' (note: graph is for 1 hour values) - Support structure design tool description derives Hs_1_year = 0.64 * Hs_50_year
Hs_1_year = 3.3  # Horns Rev website: waves of more than 6 m height reached every year. Divided by 1.86 to estimate significant wave height
current_depth_averaged_50_year = 0.8  # [m/s] Horns Rev website: Currents may reach 0.8 m/s during storms (doesn't mention return period and whether this is depth averaged)
angle_wave_current_50_year = 20.0  # [degrees] (Arbitrary default)
water_density = 1025.0  # [kg/m^3] Generic value
d50_soil = 0.0002  # [m]  Values given as 'range' in baggrund8 IEA report and confirmed by figure 2.2. in fish IEA report
d90_soil = 0.0005  # [m]  Values given as 'range' in baggrund8 IEA report and confirmed by figure 2.2. in fish IEA report
friction_angle = 35.0  # [degrees] Depth averaged friction angle from 'friction angle-report'
submerged_unit_weight = 10000.0  # [N/m^3] From 'friction angle-report', lighter layer ignored, because it is at great depth.

V_rated_voltage = [22000, 33000, 45000, 66000, 132000, 220000]  # Rated voltage in V # User's option
rv = 3  # User can pick each time one rated voltage. 0 represents the first place in a Python list

power_factor = 1.0  # cos angle

# cost constants
Ap_init = [0.284, 0.411, 0.516, 0.688, 1.971, 3.181]  # must be multiplied by 10**6
Bp_init = [0.583, 0.596, 0.612, 0.625, 0.209, 0.11]  # must be multiplied by 10**6
Cp_init = [6.15, 4.1, 3.0, 2.05, 1.66, 1.16]  # must be multiplied by 10**6

# Cable procurement costs

# cross_section = [95.0, 120.0, 150.0, 185.0, 240.0, 300.0, 400.0, 500.0, 630.0, 800.0, 1000.0]  # mm**2
# current_rating = [300, 340, 375, 420, 480, 530, 590, 655, 715, 775, 825]  # Ampere
# Cost = [206.0, 221.0, 236.0, 256.0, 287.0, 316.0, 356.0, 406.0, 459.0, 521.0, 579.0]  # Euros/meter

# -------------------------------------------------- Cable Topology - INPUT -----------------------------------------------------------------------
Crossing_penalty = 0
Area = []
# Transmission=[[central_platform_locations[0],[463000,5918000]],[central_platform_locations[1],[463000,5918000]]]
Transmission = []

# --------------------------------------------------- LPC/Costs - INPUT -----------------------------------------------------------------------------------------
i = 0.075  # interest rate [-]
v = 0.015  # inflation rate [-]
operational_lifetime = 25  # [years] - FIXED VALUE NOTE: The fixed price in PPA is valid for a number of full load hours that is reached in appr. 10 years. After that, market prices apply.
value_year = 2016
actual_year = 2016  # Year for which costs are expressed
management_percentage = 3.0  # [%]
distance_to_grid = 60000.0  # [m] Grid connection report: Submarine cable length 21 km - Onshore cable length 34 km - Total 50 km
distance_to_harbour = 40000.0  # [m] Spare part optimisation report says the 20 km sail to Horns Rev
onshore_transport_distance = 100000.0  # [m]
frequency = 50  # [Hz]
transmission_voltage = 220000.0  # [V]
grid_coupling_point_voltage = 169000.0  # [V]
rho_copper = 8940  # [kg/m^3]
rho_xlpe = 940  # [kg/m^3]
epsilon_0 = 8.85e-12  # [F/m]
epsilon_r = 2.3  # [-] (XLPE)





max_n_turbines = max_n_branches = max_n_turbines_p_branch = 74
# turbine_radius = 40.0
max_n_substations = 1
# n_quadrilaterals = 1
# separation_value_y = 1200.0
# areas = np.array([[[0, 0], [1120, 0.0], [1120.0, 1120.0], [0.0, 1120.0]]])
# # Turbine parameters
# turbine_rated_power = 2000000.0
# turbine_voltage = 33000.0
turbine_rated_current = turbine_rated_power / (turbine_voltage  * sqrt(3.0))  # A = Power / sqrt(3) / Voltage. 3 phase current per line.

cable_types = [[95, 300, 206], [120, 340, 221], [150, 375, 236], [185, 420, 256], [240, 480, 287], [300, 530, 316], [400, 590, 356], [500, 655, 406], [630, 715, 459], [800, 775, 521], [1000, 825, 579]] # Current, cross section, cost

# hub_height = 90.0

# rotor_radius = 40.0  # [m]

# solidity_rotor = 0.052  # [-] 'Generic' value, based on Peter Jamieson's book - Figure 2.5 - P.53
# cd_rotor_idle_vane = 0.4  # [-] 'Generic' value, very dependent on angle of attack and therefore the assumed rotor misalignment
# # cd_rotor_idle_failed_pitch = 1.2 # [-]
# cd_nacelle = 1.2  # [-] OWTES V66: 1.3, but using a frontal area of 13 m^2
# front_area_nacelle = 14.0  # [m^2] Vestas V80 brochure: height for transport 4 m, width 3.4 m, rounded up 14 m^2 to include height including cooler top 5.4 m
# max_thrust = 475000.0  # [N] Maximum thrust determined from thrust coefficient curve multiplied with 1.5 amplification factor (determined by Otto for NREL 5 MW turbine)
# yaw_to_hub_height = 2.0  # [m] Vestas V80 brochure: height for transport 4 m - On picture, the axis appears to be in the middle of the nacelle.
# mass = 98500.0  # [kg] 79 tonne nacelle + 3x 6.5 tonne blades
# mass_eccentricity = - 2.0  # [m] - in x-direction, so negative when upwind of tower centre - Just a guess - Vestas V80 brochure: Length of nacelle = 10.4 m
# yaw_diameter = 2.26  # [m] From OWTES V66
# wind_speed_at_max_thrust = 12.0  # [m/s] Horns rev website: 13 m/s - Vestas V80 brochure: 16 m/s, but max thrust appears at 12 m/s
# generator_voltage = 690.0  # [V] There are 480 and 690 voltage versions of the V80. The higher voltage is assumed, considering the need of high voltage in the connections to the public grid.
# purchase_price = 1500000.0  # [Euro]
# warranty_percentage = 15.0  # [%]


# #  Plant parameters
# # central_platform = [[0, 1000.0, 1000.0], [1,1,1], [2,2,2]]
# central_platform = [[0, 1000.0, 1000.0]]
# # central_platform = [[0, 429500, 6147600], [1,1,1], [2,2,2]]
# ref_height_wind_speed = 62.0
# alpha = 0.10  # Approximate mean value of fits to data in ECN report and paper of Tambke (EWEC 2004)
# hat = 0.8  # Horns Rev website: Tides are approximately 1.2 m; Paper ICCE: appr. 1.5 m - A little more than half of this is taken for 'extrapolation'
# lat = - 0.8  # Horns Rev website: Tides are approximately 1.2 m; Paper ICCE: appr. 1.5 m - A little more than half of this is taken for 'extrapolation'
# storm_surge_pos = 2.5  # Paper ICCE
# storm_surge_neg = - 0.5  # Guess
# Hs_50_year = 5.0  # Horns Rev website: Highest value in graph of Hm0 is 4.3. Somewhat higher value taken for 'extrapolation' (note: graph is for 1 hour values) - Support structure design tool description derives Hs_1_year = 0.64 * Hs_50_year
# Hs_1_year = 3.3  # Horns Rev website: waves of more than 6 m height reached every year. Divided by 1.86 to estimate significant wave height
# current_depth_averaged_50_year = 0.8  # [m/s] Horns Rev website: Currents may reach 0.8 m/s during storms (doesn't mention return period and whether this is depth averaged)
# angle_wave_current_50_year = 20.0  # [degrees] (Arbitrary default)
# water_density = 1025.0  # [kg/m^3] Generic value
# d50_soil = 0.0002  # [m]  Values given as 'range' in baggrund8 IEA report and confirmed by figure 2.2. in fish IEA report
# d90_soil = 0.0005  # [m]  Values given as 'range' in baggrund8 IEA report and confirmed by figure 2.2. in fish IEA report
# friction_angle = 35.0  # [degrees] Depth averaged friction angle from 'friction angle-report'
# submerged_unit_weight = 10000.0  # [N/m^3] From 'friction angle-report', lighter layer ignored, because it is at great depth.

# V_rated_voltage = [22000, 33000, 45000, 66000, 132000, 220000]  # Rated voltage in V # User's option

# power_factor = 1.0  # cos angle
# inflationrate = 1.18  # average inflation rate
# exchangerate = 0.11  # exchange rate of SEK to Euros

# # cost constants
# Ap_init = [0.284, 0.411, 0.516, 0.688, 1.971, 3.181]  # must be multiplied by 10**6
# Bp_init = [0.583, 0.596, 0.612, 0.625, 0.209, 0.11]  # must be multiplied by 10**6
# Cp_init = [6.15, 4.1, 3.0, 2.05, 1.66, 1.16]  # must be multiplied by 10**6

# rv = 1  # User can pick each time one rated voltage. 0 represents the first place in a Python list

# # -------------------------------------------------- Cable Topology - INPUT -----------------------------------------------------------------------
# Crossing_penalty = 0
# Area = []
# # Transmission=[[central_platform_locations[0],[463000,5918000]],[central_platform_locations[1],[463000,5918000]]]
# Transmission = []

# # --------------------------------------------------- LPC/Costs - INPUT -----------------------------------------------------------------------------------------
# i = 0.1  # interest rate [-]
# v = 0.025  # inflation rate [-]
# operational_lifetime = 20  # [years] - FIXED VALUE NOTE: The fixed price in PPA is valid for a number of full load hours that is reached in appr. 10 years. After that, market prices apply.
# value_year = 2016
# actual_year = 2016  # Year for which costs are expressed
# management_percentage = 3.0  # [%]
# distance_to_grid = 55000.0  # [m] Grid connection report: Submarine cable length 21 km - Onshore cable length 34 km - Total 50 km
# distance_to_harbour = 20000.0  # [m] Spare part optimisation report says the 20 km sail to Horns Rev
# onshore_transport_distance = 100000.0  # [m]
# frequency = 50  # [Hz]
# transmission_voltage = 220000.0  # [V]
# grid_coupling_point_voltage = 169000.0  # [V]
# rho_copper = 8940  # [kg/m^3]
# rho_xlpe = 940  # [kg/m^3]
# epsilon_0 = 8.85e-12  # [F/m]
# epsilon_r = 2.3  # [-] (XLPE)

def separation_equation_y(x):  # values y greater than f(x) use mapping 1, else mapping 0
    if len(areas) > 1:
        m = (areas[1][0][1] - areas[1][1][1]) / (areas[1][0][0] - areas[1][1][0])
        yy = areas[1][0][1]
        xx = areas[1][0][0]
        b = yy - m * xx
        return m * x + b
    else:
        return - 10000000.0