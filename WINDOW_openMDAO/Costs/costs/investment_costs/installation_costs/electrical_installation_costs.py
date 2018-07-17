from WINDOW_openMDAO.Costs.costs.currency import Cost1
from WINDOW_openMDAO.input_params import distance_to_grid


def electrical_installation_costs():

    cable_laying_transmission_per_distance = Cost1(178.0, 'USD', 2010)  # [$/m]
    cable_laying_fixed_costs = Cost1(500000.0, 'Euro', 2003)  # [euro]
    cable_dune_crossing_costs = Cost1(1.2e6, 'Euro', 2003)  # [euro]

    inv_installation_electrical_system_transmission_cable = (cable_laying_fixed_costs + cable_laying_transmission_per_distance * distance_to_grid)

    inv_installation_electrical_system_dune_crossing = cable_dune_crossing_costs

    electrical_installation_total = inv_installation_electrical_system_dune_crossing + inv_installation_electrical_system_transmission_cable
    # print electrical_installation_total
    return electrical_installation_total

if __name__ == '__main__':
    print electrical_installation_costs()
