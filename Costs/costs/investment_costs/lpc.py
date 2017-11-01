
# import math
from master_lib.supportstrucutres.lib.system.properties import RNA
from master_lib.supportstrucutres.lib.environment.physical_environment import Site
from master_lib.Cable_Topology.Hybrid import g_cable_length
from master_lib.Cable_Topology.Hybrid import g_total_cost
from master_lib.supportstrucutres.lib.designers_support.dimension_team_support import DimensionTeamSupport

from master_lib.custom.misc import Cost1, WT_List, mass, generator_voltage, transmission_voltage, \
    grid_coupling_point_voltage, epsilon_0, epsilon_r, V_rated_voltage
import master_lib.custom.misc
from master_lib.custom.misc import NT, r0, P_rated, operational_lifetime, value_year, actual_year, \
    management_percentage, onshore_transport_distance, i, v, rv
from master_lib.custom.misc import warranty_percentage, purchase_price, rho_xlpe, rho_copper, distance_to_grid, \
    frequency
from master_lib.Cables.central_platform import depth_central_platform

# rna = RNA()
# print rna.solidity_rotor
# site_data = Site()
# print site_data.scale_factor
# dimension_team_support = DimensionTeamSupport()
# dimension_team_support.run(rna, site_data)
Meters = 'm'
Euro = 'Euro'
MEuro = 'MEuro'
total_investment_costs = 0
total_decommissioning_costs = 0
total_operation_maintenance_costs = 0
annuity_factor = 0
r = 0
gpos0 = 0
gminDepth = 0


def run():
    # WT_List = master_lib.custom.misc.WT_List
    print "INSIDE: " + str(g_total_cost)
    global total_investment_costs
    global total_decommissioning_costs
    global total_operation_maintenance_costs
    global annuity_factor
    global r
    # global gpos0  # the position of the most expensive turbine
    global gminDepth
    # g_total_cost= 13159692.818       # WHEN I WANT CONSTANT INFIELD CABLE COST
    r = ((1.0 + i) / (1.0 + v)) - 1.0  # interest rate per period
    # print "annuity_factor"+str(r)
    annuity_factor = (1.0 - (1.0 / (1.0 + r)) ** operational_lifetime) / r
    # print "annuity_factor"+str(annuity_factor)
    # ----------------------------------------------------- Investment Costs - Input ----------------------------------------------------------------
    # Project development
    engineering_per_watt = Cost1(0.037, 'USD', 2003)  # [$/Watt]

    # Procurement & Installation-Support structure
    # tower_price = Cost1(2.04, 'USD', 2002)  # [$/kg]
    # transition_piece_price = Cost1(3.75, 'Euro', 2007)  # [euro/kg]
    # grout_price = Cost1(0.1, 'Euro', 2003)  # [euro/kg] (This value is not supported by literature/data and based on some information on the web about concrete
    # monopile_price = Cost1(2.25, 'Euro', 2007)  # [euro/kg]
    boat_landing_costs = Cost1(60000.0, 'USD', 2003)  # [$/turbine]
    # scour_protection_per_volume = Cost1(211.0, 'Euro', 2003)  # [euro/m^3]
    # foundation_installation_per_mass = Cost1(1.4, 'USD', 2010)  # [$/kg]

    # Procurement-Auxiliary
    measuring_tower_costs = Cost1(2050000.0, 'Euro', 2003)  # [Euro]
    onshore_premises_costs = Cost1(1500000.0, 'Euro', 2003)  # [Euro]
    central_platform_modesty_factor = 2.0 / 3.0  # Introduced because the cost model was for a sophisticated platform that didn't match realised platforms
    central_platform_coef_a = Cost1(0.4e-3, 'SEK', 2003)  # [SEK/kg^2]
    central_platform_coef_b = Cost1(-50.0, 'SEK', 2003)  # [SEK/kg]
    central_platform_coef_c = Cost1(-80.0e6, 'SEK', 2003)  # [SEK]
    jacket_mass_coef_a = 582.0
    jacket_mass_exp_a = 0.19
    jacket_mass_exp_b = 0.48
    topside_mass_coef_a = 3.0e-3
    topside_mass_coef_b = 0.5e6

    # Installation - Rotor-nacelle assembly
    onshore_transport_coef_a = Cost1(5.84e-3, 'Euro', 2001)  # [Euro]
    onshore_transport_coef_b = Cost1(0.4, 'Euro', 2001)  # [Euro]
    onshore_transport_coef_c = Cost1(0.486, 'Euro', 2001)  # [Euro]
    onshore_transport_exp = 2.64
    turbine_installation_per_turbine_coef_a = Cost1(3.4e3, 'USD', 2010)  # [$/(m * turbine)]
    turbine_installation_per_turbine_coef_b = 50.0  # [m]

    # Installation - Auxiliary
    harbour_per_watt = Cost1(0.02, 'USD', 2002)  # [$/Watt]
    measuring_tower_installation_costs = Cost1(550000.0, 'Euro', 2003)  # [Euro]

    # Procurement & Installation - Electrical system
    transformer_coef_A1 = Cost1(0.00306, 'Euro', 2012)  # [euro/W]
    transformer_coef_B1 = Cost1(810.0, 'Euro', 2012)  # [euro]
    transformer_coef_A2 = Cost1(1.16, 'Euro', 2012)  # [euro/'W']
    transformer_coef_B2 = 0.7513  # [-]
    transformer_coef_C1 = 0.039  # [-]
    copper_price = Cost1(5.0, 'Euro', 2003)  # [euro/kg]
    xlpe_insulation_price = Cost1(15.0, 'Euro', 2003)  # [euro/kg]
    cable_costs_offset = Cost1(50.0, 'Euro', 2003)  # [euro/m]
    cable_manufacturing_surcharge = 2.3  # [-] (For manufacturing and materials besides copper and XLPE)
    # cable_laying_infield_per_distance = Cost1(169.0, 'USD', 2010)  # [$/m]
    cable_laying_transmission_per_distance = Cost1(178.0, 'USD', 2010)  # [$/m]
    cable_laying_fixed_costs = Cost1(500000.0, 'Euro', 2003)  # [euro]
    shunt_reactor_coef_a = Cost1(0.807, 'Euro', 2012)  # [~euro/VAr]
    shunt_reactor_exp_a = 0.7513  # [-]
    cable_dune_crossing_costs = Cost1(1.2e6, 'Euro', 2003)  # [euro]

    # --------------------------------------------------- Decommisioning costs/Removal/Disposal - Input  ---------------------------------------------------------------
    # scour_protection_removal_per_volume = Cost1(33.0, 'USD', 2010)  # [$/m^3]
    turbine_removal_factor = 0.91  # [-]
    site_clearance_per_turbine = Cost1(16000.0, 'USD', 2010)  # [$]
    turbine_disposal_per_mass = Cost1(0.15, 'USD', 2010)  # [$/kg]
    substation_and_metmast_removal = Cost1(665000.0, 'USD', 2010)  # [$]
    transmission_cable_removal_price = Cost1(49.0, 'USD', 2010)  # [$/m]
    infield_cable_removal_price = Cost1(53.0, 'USD', 2010)  # [$/m]

    # -------------------------------------------------- LPC Costs Calculation ---------------------------------------------------------------------------------
    voltage_at_turbine = generator_voltage
    onshore_transformer_winding_ratio = transmission_voltage / grid_coupling_point_voltage
    offshore_transformer_winding_ratio = V_rated_voltage[rv] / transmission_voltage
    turbine_transformer_winding_ratio = voltage_at_turbine / V_rated_voltage[rv]
    # print V_rated_voltage[rv]
    transmission_cable_voltage = onshore_transformer_winding_ratio * grid_coupling_point_voltage
    max_current_at_rated = (NT * P_rated) / (math.sqrt(3.0) * transmission_cable_voltage)
    d_conductor = 33.0e-9 * max_current_at_rated ** 2 + 8.9e-6 * max_current_at_rated + 5.7e-3
    a_conductor = 0.25 * math.pi * d_conductor ** 2
    t_conductor_screen = 1.1 * a_conductor
    d_conductor_screen = d_conductor + 2.0 * t_conductor_screen
    t_insulation = 83.0e-9 * V_rated_voltage[rv] + 4.0e-3
    d_insulation = d_conductor_screen + 2.0 * t_insulation
    # t_insulation_screen = 0.016 * d_conductor + 1.0e-3
    # d_insulation_screen = d_insulation + 2.0 * t_insulation_screen

    # ------------------------------------------------------------------ INVESTMENT COSTS ------------------------------------------------------------------
    # Investment costs - Project development 
    inv_project_development_engineering = NT * P_rated * engineering_per_watt.value

    # Investment costs - Procurement - Rotor/nacelle
    inv_procurement_turbines_purchase = NT * purchase_price
    inv_procurement_turbines_warranty = (warranty_percentage / 100.0) * inv_procurement_turbines_purchase

    # Investment costs - Procurement & Installation - Support structure
    inv_procurement_support_structures_boat_landing = NT * boat_landing_costs.value

    #   -----------TEST-------------------------
    # suma = 0.0
    # sum1 = 0.0
    #
    # for item in WT_List:
    #     item.append(25.6)
    # for turbine in range(len(WT_List)):
    #     # for turbine in range(len(WT_List)):
    #     WT_List[turbine][3] = 5.77816518648  # MAXIMUM WATER DEPTH OF THE WHOLE AREA
    #     site_data.water_depth = WT_List[turbine][3]  # EACH TURBINE HAS ITS OWN WATER DEPTH
    #     site_data.water_depth=max_water_depth #MAXIMUM WATER DEPTH FOR EACH INDIVIDUAL
    #     site_data.water_depth=14.0  # MAXIMUM WATER DEPTH OF THE WHOLE AREA
    #      print WT_List[turbine][3]
    #       print site_data.water_depth
    #     dimension_team_support.run(rna, site_data)
    #      print "The water depth of turbine No.",WT_List[turbine][0]+1,"is:",dimension_team_support.physical_environment.site.water_depth,"meters"
    #     print dimension_team_support.properties.support_structure.tower_mass
    #     inv_procurement_support_structures_tower = tower_price.value * dimension_team_support.properties.support_structure.tower_mass
    #      print WT_List[turbine][0]+1, "is:", dimension_team_support.properties.support_structure.tower_mass
    #     print dimension_team_support.properties.support_structure.transition_piece_mass
    #     inv_procurement_support_structures_transition_piece = transition_piece_price.value * dimension_team_support.properties.support_structure.transition_piece_mass
    #     print WT_List[turbine][0]+1, "is:",  dimension_team_support.properties.support_structure.transition_piece_mass
    #     print
    #     inv_procurement_support_structures_grout = grout_price.value * dimension_team_support.properties.support_structure.grout_mass
    #     print WT_List[turbine][0]+1, "is:", dimension_team_support.properties.support_structure.grout_mass
    #     inv_procurement_support_structures_monopile = monopile_price.value * dimension_team_support.properties.support_structure.pile_mass
    #     print WT_List[turbine][0]+1, "is:", dimension_team_support.properties.support_structure.pile_mass
    #     inv_procurement_support_structures_scour_protection = scour_protection_per_volume.value * dimension_team_support.properties.support_structure.scour_protection_volume
    #     print WT_List[turbine][0]+1, "is:", dimension_team_support.properties.support_structure.scour_protection_volume
    #     inv_installation_foundations = foundation_installation_per_mass.value * dimension_team_support.properties.support_structure.pile_mass
    #     print WT_List[turbine][0]+1, "is:", dimension_team_support.properties.support_structure.pile_mass
    #        dimension_team_support.cost_analysts.set_support_structure_costs()
    #     suma += dimension_team_support.total_support_structure_cost
    #     inv_cost_per_turbine_procurement_support_structure = inv_procurement_support_structures_tower + inv_procurement_support_structures_transition_piece + inv_procurement_support_structures_grout + inv_procurement_support_structures_monopile + inv_procurement_support_structures_scour_protection + inv_installation_foundations
    #     suma += inv_cost_per_turbine_procurement_support_structure
    #
    #     print dimension_team_support.properties.support_structure.base_tp
    #     print site_data.water_depth
    #     print suma
    #     decommissioning_removal_foundations = foundation_installation_per_mass.value * dimension_team_support.properties.support_structure.pile_mass
    #     decommissioning_removal_scour_protection = scour_protection_removal_per_volume.value * dimension_team_support.properties.support_structure.scour_protection_volume
    #     dec_per_turbine = decommissioning_removal_foundations + decommissioning_removal_scour_protection
    #     sum1 += dec_per_turbine
    #     # print sum1
    #     print sum1 + suma

    # # Investment costs - Procurement - Auxiliary
    topside_mass = (topside_mass_coef_a * NT * P_rated + topside_mass_coef_b)
    mass_jacket = (jacket_mass_coef_a * depth_central_platform ** jacket_mass_exp_a * topside_mass ** jacket_mass_exp_b)
    inv_procurement_auxiliary_measuring_tower = measuring_tower_costs.value
    inv_procurement_auxiliary_onshore_premises = onshore_premises_costs.value
    inv_procurement_auxiliary_offshore_platform = (central_platform_modesty_factor * (central_platform_coef_a.value * mass_jacket ** 2.0 + central_platform_coef_b.value * mass_jacket + central_platform_coef_c.value))

    # Investment costs - Installation - Rotor-nacelle assembly
    diameter = 2.0 * r0
    transport_per_turbine = ((onshore_transport_coef_a.value * diameter +
                              onshore_transport_coef_b.value) * onshore_transport_distance +
                             onshore_transport_coef_c.value * diameter ** onshore_transport_exp)

    inv_installation_turbines_onshore_transport = NT * transport_per_turbine
    inv_installation_turbines_offshore_works = (NT * turbine_installation_per_turbine_coef_a.value * (dimension_team_support.properties.support_structure.hub_height + turbine_installation_per_turbine_coef_b))

    # Investment costs - Installation - Auxiliary
    inv_installation_auxiliary_harbour = NT * P_rated * harbour_per_watt.value
    inv_installation_auxiliary_measuring_tower = measuring_tower_installation_costs.value

    # Investment costs - Procurement & Installation -Electrical system
    transmission_cable_length = distance_to_grid
    copper_mass_pm = 3 * a_conductor * rho_copper
    xlpe_mass_pm = (3 * (d_insulation ** 2 - d_conductor_screen ** 2) * 0.25 * math.pi * rho_xlpe)
    copper_price_pm = copper_mass_pm * copper_price.value
    xlpe_price_pm = xlpe_mass_pm * xlpe_insulation_price.value
    manufacturing_price_pm = cable_costs_offset.value + cable_manufacturing_surcharge * (copper_price_pm + xlpe_price_pm)
    transmission_cable_capacitance = (2.0 * math.pi * epsilon_0 * epsilon_r / (math.log(d_insulation / d_conductor_screen)))
    power_shunt_reactor_onshore = 1.0 / (2.0 * math.pi ** 2 * frequency ** 2 * transmission_cable_capacitance * transmission_cable_length)
    power_shunt_reactor_offshore = 1.0 / (2.0 * math.pi ** 2 * frequency ** 2 * transmission_cable_capacitance * transmission_cable_length)
    inv_procurement_electrical_system_transformer = (transformer_coef_A1.value * P_rated + transformer_coef_B1.value) * math.exp(transformer_coef_C1 * turbine_transformer_winding_ratio) * NT + (transformer_coef_A2.value * ((NT * P_rated) ** transformer_coef_B2)) * (math.exp(transformer_coef_C1 * offshore_transformer_winding_ratio) + math.exp(transformer_coef_C1 * onshore_transformer_winding_ratio))
    inv_procurement_electrical_system_transmission_cable = manufacturing_price_pm * transmission_cable_length
    inv_procurement_electrical_system_shunt_reactor = shunt_reactor_coef_a.value * (power_shunt_reactor_onshore ** shunt_reactor_exp_a + power_shunt_reactor_offshore ** shunt_reactor_exp_a)

    inv_procurement_electrical_system_infield_cable = g_total_cost  # Infield cable cost based on Hybrid approach
    # inv_installation_electrical_system_infield_cable = (cable_laying_fixed_costs.value + cable_laying_infield_per_distance.value *\
    #                                                         g_cable_length)
    inv_installation_electrical_system_transmission_cable = (
        cable_laying_fixed_costs.value + cable_laying_transmission_per_distance.value * transmission_cable_length)
    inv_installation_electrical_system_dune_crossing = cable_dune_crossing_costs.value

    investment_costs = inv_project_development_engineering + inv_procurement_turbines_purchase + inv_procurement_turbines_warranty + suma + inv_procurement_support_structures_boat_landing + inv_procurement_auxiliary_measuring_tower + inv_procurement_auxiliary_onshore_premises + inv_procurement_auxiliary_offshore_platform + inv_installation_turbines_onshore_transport + inv_installation_turbines_offshore_works + inv_installation_auxiliary_harbour + inv_installation_auxiliary_measuring_tower + inv_procurement_electrical_system_transmission_cable + inv_procurement_electrical_system_shunt_reactor + inv_procurement_electrical_system_transformer + inv_procurement_electrical_system_infield_cable + inv_installation_electrical_system_transmission_cable + inv_installation_electrical_system_dune_crossing  # + inv_installation_electrical_system_infield_cable

    total_investment_costs = investment_costs * (management_percentage / 100.0 + 1.0)
    print "The total Investment costs are", round(total_investment_costs / 10 ** 6, 3), MEuro
    # -------------------------- O&M COSTS --------------------------------
    # total_operation_maintenance_costs = 6.0/100.0 * investment_costs
    total_operation_maintenance_costs = 0.0238 * 628773403.489
    # total_operation_maintenance_costs = 11701551.2237  # This is the average value from the 1st generation

    # print "LPC"+str(total_operation_maintenance_costs)
    print "The total O&M costs are", round(total_operation_maintenance_costs / 10 ** 6, 3), MEuro
    # print "The total decommissioning costs for the support structures is:", sum1/10**6,MEuro
    print "The total cost of the support structures is:", round((suma + sum1) / 10 ** 6, 3), MEuro
    # print "Support structure costs:",(sum + sum1)/10**6
    decommissioning_removal_turbines = turbine_removal_factor * inv_installation_turbines_offshore_works
    decommissioning_removal_site_clearance = NT * site_clearance_per_turbine.value
    decommissioning_removal_substation_and_metmast = substation_and_metmast_removal.value
    decommissioning_removal_transmission_cable = transmission_cable_removal_price.value * transmission_cable_length
    decommissioning_removal_infield_cable = infield_cable_removal_price.value * g_cable_length

    # Decommissioning costs - Disposal
    decommissioning_disposal_turbines = NT * turbine_disposal_per_mass.value * mass

    decommissioning_costs = decommissioning_removal_turbines + decommissioning_removal_site_clearance + decommissioning_removal_substation_and_metmast + decommissioning_removal_transmission_cable + sum1 + decommissioning_removal_infield_cable + decommissioning_disposal_turbines

    total_decommissioning_costs = decommissioning_costs * (management_percentage / 100.0 + 1.0)

    print "The total Decommissioning costs are", round(total_decommissioning_costs / 10 ** 6, 3), MEuro

run()
