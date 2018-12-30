from WINDOW_openMDAO.Costs.costs.currency import Cost1
from WINDOW_openMDAO.input_params import transmission_voltage, grid_coupling_point_voltage, distance_to_grid, frequency, number_substations
from numpy import sqrt, pi, exp, log
#from WINDOW_openMDAO.input_params import generator_voltage#, turbine_rated_power as P_rated

rho_copper = 8940.0  # [kg/m^3]
rho_xlpe = 940.0  # [kg/m^3]
epsilon_0 = 8.85e-12  # [F/m]
epsilon_r = 2.3  # [-] (XLPE)


def electrical_procurement_costs(NT, P_rated, generator_voltage, collection_voltage, n_substations=number_substations):
    # Procurement - Electrical system
    transformer_coef_A1 = Cost1(0.00306, 'Euro', 2012)  # [euro/W]
    transformer_coef_B1 = Cost1(810.0, 'Euro', 2012)  # [euro]
    transformer_coef_A2 = Cost1(1.16, 'Euro', 2012)  # [euro/'W']
    transformer_coef_B2 = 0.7513  # [-]
    transformer_coef_C1 = 0.039  # [-]
    copper_price = Cost1(5.0, 'Euro', 2003)  # [euro/kg]
    xlpe_insulation_price = Cost1(15.0, 'Euro', 2003)  # [euro/kg]
    cable_costs_offset = Cost1(50.0, 'Euro', 2003)  # [euro/m]
    cable_manufacturing_surcharge = 2.3  # [-] (For manufacturing and materials besides copper and XLPE)
    shunt_reactor_exp_a = 0.7513  # [-]
    shunt_reactor_coef_a = Cost1(0.807, 'Euro', 2012)  # [~euro/VAr]

    # Investment costs - Procurement -Electrical system
    voltage_at_turbine = generator_voltage
    onshore_transformer_winding_ratio = transmission_voltage / grid_coupling_point_voltage
    offshore_transformer_winding_ratio = collection_voltage / transmission_voltage
    turbine_transformer_winding_ratio = voltage_at_turbine / collection_voltage
    transmission_cable_voltage = onshore_transformer_winding_ratio * grid_coupling_point_voltage
    max_current_at_rated = (NT * P_rated) / (sqrt(3.0) * transmission_cable_voltage)
    d_conductor = 33.0e-9 * max_current_at_rated ** 2 + 8.9e-6 * max_current_at_rated + 5.7e-3
    a_conductor = 0.25 * pi * d_conductor ** 2
    t_conductor_screen = 1.1 * a_conductor
    d_conductor_screen = d_conductor + 2.0 * t_conductor_screen
    t_insulation = 83.0e-9 * collection_voltage + 4.0e-3
    d_insulation = d_conductor_screen + 2.0 * t_insulation

    transmission_cable_length = distance_to_grid
    copper_mass_pm = 3 * a_conductor * rho_copper
    xlpe_mass_pm = (3 * (d_insulation ** 2 - d_conductor_screen ** 2) * 0.25 * pi * rho_xlpe)
    # print copper_mass_pm, copper_price
    copper_price_pm = copper_mass_pm * copper_price
    xlpe_price_pm = xlpe_mass_pm * xlpe_insulation_price
    # print cable_costs_offset ,cable_manufacturing_surcharge, copper_price_pm ,xlpe_price_pm
    manufacturing_price_pm = cable_costs_offset + cable_manufacturing_surcharge * (copper_price_pm + xlpe_price_pm)
    transmission_cable_capacitance = (2.0 * pi * epsilon_0 * epsilon_r / (log(d_insulation / d_conductor_screen)))
    power_shunt_reactor_onshore = 1.0 / (2.0 * pi ** 2 * frequency ** 2 * transmission_cable_capacitance * transmission_cable_length)
    power_shunt_reactor_offshore = 1.0 / (2.0 * pi ** 2 * frequency ** 2 * transmission_cable_capacitance * transmission_cable_length)
    # print power_shunt_reactor_offshore, "inductance"
    inv_procurement_electrical_system_transformer = (transformer_coef_A1 * P_rated + transformer_coef_B1) * exp(transformer_coef_C1 * turbine_transformer_winding_ratio) * NT + (transformer_coef_A2 * ((NT/n_substations * P_rated) ** transformer_coef_B2)) * (exp(transformer_coef_C1 * offshore_transformer_winding_ratio) + exp(transformer_coef_C1 * onshore_transformer_winding_ratio)) * n_substations
    # inv_procurement_electrical_system_transformer = (transformer_coef_A1 * P_rated + transformer_coef_B1) * exp(transformer_coef_C1 * turbine_transformer_winding_ratio) * NT + (transformer_coef_A2 * ((NT * P_rated) ** transformer_coef_B2)) * (exp(transformer_coef_C1 * offshore_transformer_winding_ratio) + exp(transformer_coef_C1 * onshore_transformer_winding_ratio)) * n_substations
    # print "transf", inv_procurement_electrical_system_transformer
    # print manufacturing_price_pm
    inv_procurement_electrical_system_transmission_cable = manufacturing_price_pm * transmission_cable_length
    inv_procurement_electrical_system_shunt_reactor = shunt_reactor_coef_a * (power_shunt_reactor_onshore ** shunt_reactor_exp_a + power_shunt_reactor_offshore ** shunt_reactor_exp_a)

    electrical_total_costs = inv_procurement_electrical_system_transformer + inv_procurement_electrical_system_transmission_cable + inv_procurement_electrical_system_shunt_reactor
    # print inv_procurement_electrical_system_transformer, inv_procurement_electrical_system_transmission_cable, inv_procurement_electrical_system_shunt_reactor
    return electrical_total_costs

if __name__ == '__main__':
    print electrical_procurement_costs()
