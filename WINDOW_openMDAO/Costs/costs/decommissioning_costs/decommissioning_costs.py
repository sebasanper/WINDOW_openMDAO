from __future__ import print_function
from __future__ import division

from WINDOW_openMDAO.Costs.costs.currency import Cost1
from WINDOW_openMDAO.input_params import mass, hub_height, management_percentage, distance_to_grid


def decommissioning_costs(infield_cable_length, NT):

    # ----------------- Decommisioning costs/Removal/Disposal - Input  --------------------
    scour_protection_removal_per_volume = Cost1(33.0, 'USD', 2010)  # [$/m^3]
    turbine_removal_factor = 0.91  # [-]
    site_clearance_per_turbine = Cost1(16000.0, 'USD', 2010)  # [$]
    turbine_disposal_per_mass = Cost1(0.15, 'USD', 2010)  # [$/kg]
    substation_and_metmast_removal = Cost1(665000.0, 'USD', 2010)  # [$]
    transmission_cable_removal_price = Cost1(49.0, 'USD', 2010)  # [$/m]
    infield_cable_removal_price = Cost1(53.0, 'USD', 2010)  # [$/m]
    turbine_installation_per_turbine_coef_a = Cost1(3.4e3, 'USD', 2010)  # [$/(m * turbine)]
    turbine_installation_per_turbine_coef_b = 50.0  # [m]

    inv_installation_turbines_offshore_works = (NT * turbine_installation_per_turbine_coef_a * (hub_height + turbine_installation_per_turbine_coef_b))

    decommissioning_removal_turbines = turbine_removal_factor * inv_installation_turbines_offshore_works
    decommissioning_removal_site_clearance = NT * site_clearance_per_turbine
    decommissioning_removal_substation_and_metmast = substation_and_metmast_removal
    decommissioning_removal_transmission_cable = transmission_cable_removal_price * distance_to_grid
    decommissioning_removal_infield_cable = infield_cable_removal_price * infield_cable_length

    # Decommissioning costs - Disposal
    decommissioning_disposal_turbines = NT * turbine_disposal_per_mass * mass

    decommissioning_costs = decommissioning_removal_turbines + decommissioning_removal_site_clearance + decommissioning_removal_substation_and_metmast + decommissioning_removal_transmission_cable + decommissioning_removal_infield_cable + decommissioning_disposal_turbines

    total_decommissioning_costs = decommissioning_costs * (management_percentage / 100.0 + 1.0)

    return total_decommissioning_costs

if __name__ == '__main__':
    print(decommissioning_costs(800000))
