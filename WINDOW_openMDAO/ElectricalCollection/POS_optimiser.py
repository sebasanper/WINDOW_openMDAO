from WINDOW_openMDAO.src.api import AbstractElectricDesign
from POS_electrical import cable_design, choose_cables


class POSHeuristic(AbstractElectricDesign):

    def topology_design_model(self, layout, substation_coords, n_turbines_p_cable_type, turbine_rated_current):
        cable_list = choose_cables([max(n_turbines_p_cable_type), 0, 0], turbine_rated_current)
        return cable_design(layout, substation_coords, [max(n_turbines_p_cable_type), 0, 0], cable_list)
