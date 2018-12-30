class Properties:
    def __init__(self):
        self.rna = None

        self.support_structure = SupportStructure()


# RNA **************************************************


class RNA:
    
    def __init__(self, rotor_radius, rated_wind_speed, rotor_thrust, rna_mass, \
                 solidity_rotor, cd_rotor_idle_vane, cd_nacelle, \
                 yaw_diameter, front_area_nacelle, yaw_to_hub_height, mass_eccentricity):
        
        # DATA FROM USER INPUT **************************************************
        self.solidity_rotor = solidity_rotor  # [-] 'Generic' value, based on Peter Jamieson's book - Figure 2.5 - P.53
        self.cd_rotor_idle_vane = cd_rotor_idle_vane  # [-] 'Generic' value, very dependent on angle of attack and therefore the assumed rotor misalignment
        # cd_rotor_idle_failed_pitch = 1.2 # [-]
        self.cd_nacelle = cd_nacelle  # [-] OWTES V66: 1.3, but using a frontal area of 13 m^2
        self.front_area_nacelle = front_area_nacelle  # [m^2] Vestas V80 brochure: height for transport 4 m, width 3.4 m, rounded up 14 m^2 to include height including cooler top 5.4 m
        self.max_thrust = rotor_thrust  # [N] Maximum thrust determined from thrust coefficient curve multiplied with 1.5 amplification factor (determined by Otto for NREL 5 MW turbine)
        self.yaw_to_hub_height = yaw_to_hub_height  # [m] Vestas V80 brochure: height for transport 4 m - On picture, the axis appears to be in the middle of the nacelle.
        self.mass = rna_mass  # [kg] 79 tonne nacelle + 3x 6.5 tonne blades
        self.mass_eccentricity = mass_eccentricity  # [m] - in x-direction, so negative when upwind of tower centre - Just a guess - Vestas V80 brochure: Length of nacelle = 10.4 m
        self.yaw_diameter = yaw_diameter  # [m] From OWTES V66
        self.rotor_radius = rotor_radius  # [m]
        self.wind_speed_at_max_thrust = rated_wind_speed  # [m/s] Horns rev website: 13 m/s - Vestas V80 brochure: 16 m/s, but max thrust appears at 12 m/s
        # generator_voltage = generator_voltage  # [V] There are 480 and 690 voltage versions of the V80. The higher voltage is assumed, considering the need of high voltage in the connections to the public grid.
        # pm_interval = pm_interval  # [h] Horns Rev website: two services per year
        # pm_duration = pm_duration  # [h] (Spare parts report: 1x 3 days, 1x 2 days. 1 day = 12 hours minus ~3 hours preparation and sailing (2x 2 hours are mentioned for CM, but during PM an extra boat is available): average: 2.5 * 9 hours)
        # pm_consumables_costs = pm_consumables_costs  # [E] (Spare parts report: 1x 1500, 1x 1000 Euro; Average: 1250 Euro)
        # people_per_crew = people_per_crew  # [-] (Spare part optimisation report p.52: 6 Vattenfall technicians in 1 shift, with 3 Vestas service personnel, so probably 2 Vattenfall and 1 Vestas people per crew - For PM 2 technicians are needed)
        # purchase_price = purchase_price  # [Euro]
        # warranty_percentage = warranty_percentage  # [%]
    
        # PROCESSED DATA **************************************************
        # rated_power = 0.0  # [W]

#     def __init__(self):
#         pass
#         #        # DATA FROM USER INPUT **************************************************
#         #        self.failure_stat = ([[73000.0, 8.0, 85.0, 0.0, 'yes', 210000.0],
#         #                              [6100.0, 1.0, 5.0, 0.0, 'no', 1100.0],
#         #                              [13000.0, 0.0, 5.0, 0.0, 'no', 1600.0]])
#         # List of different failure types; Per type:
#         # [MTBF [h], Diagnose time [h], Repair time [h], Waiting time for spare parts [h], Lifting equipment [yes/no], costs of consumables/spare parts [E]]
#         # (Data based on Spare parts optimisation thesis - Appendix B)
#         # Source for power curve: Jensen, EWEC 2004 (Corresponds well with my own readings of Vestas V80 brochure)
#         # self.power_curve = power_curve
# 
#         #    # Source for thrust (coefficient) curve: Jensen, EWEC 2004 - Paper mentions that this V80 curve is specific for the turbines delivered for Horns Rev (Appears to be one of the curves in Fernando's report, figure 5-8, p. 74)
#         # self.thrust_curve = thrust_curve


# SUPPORT STRUCTURE **************************************************

class SupportStructure:
    # INTRINSIC PROPERTIES
    hub_height = 0.0  # [m]
    base_tp = 0.0  # [m]
    platform_height = 0.0  # [m]

    tower_mass = 0.0  # [kg]
    transition_piece_mass = 0.0  # [kg]
    grout_mass = 0.0  # [kg]
    pile_mass = 0.0  # [kg]

    scour_protection_volume = 0.0  # [m^3]

    def __init__(self):
        pass
