from lib.designers_support.dimension_team_support import DimensionTeamSupport
from lib.system.properties import RNA
from lib.environment.physical_environment import Site
from currency import Cost1


def teamplay(TI, depth, rotor_radius, rated_wind_speed, rotor_thrust, rna_mass, \
             solidity_rotor, cd_rotor_idle_vane, cd_nacelle, \
             yaw_diameter, front_area_nacelle, yaw_to_hub_height, mass_eccentricity):
    
    dimension_team_support = DimensionTeamSupport()
    dimension_team_support.fsf = TI + 1.4 # 1.4 safety factor to account for wave-induced fatigue and the rest is wind-induced.
    # dimension_team_support.fsf = 1.5
    rna = RNA(rotor_radius, rated_wind_speed, rotor_thrust, rna_mass, \
              solidity_rotor, cd_rotor_idle_vane, cd_nacelle, \
                 yaw_diameter, front_area_nacelle, yaw_to_hub_height, mass_eccentricity)
    site_data = Site()
    site_data.water_depth = depth

    # print site_data.water_depth
    dimension_team_support.run(rna, site_data)

    boat_landing_cost = Cost1(60000.0, 'USD', 2003)  # [$/turbine]
    # Investment costs - Procurement & Installation - Support structure

    return dimension_team_support.total_support_structure_cost + boat_landing_cost