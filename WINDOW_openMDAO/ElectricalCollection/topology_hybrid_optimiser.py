from WINDOW_openMDAO.src.api import AbstractElectricDesign
from hybrid_heuristic import cable_design, choose_cables


class TopologyHybridHeuristic(AbstractElectricDesign):

    def topology_design_model(self, layout, substation_coords, n_turbines_p_cable_type, turbine_rated_current):
        cable_list = choose_cables(n_turbines_p_cable_type, turbine_rated_current)
        return cable_design(layout, substation_coords, n_turbines_p_cable_type, cable_list)
