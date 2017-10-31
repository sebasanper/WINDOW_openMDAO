from src.api import AbstractCollectionDesign
from hybrid_heuristic import cable_design, choose_cables


class TopologyHybridHeuristic(AbstractCollectionDesign):

    def topology_design_model(self, layout, substation_coords, n_turbines_p_cable_type):

        cable_list = choose_cables(n_turbines_p_cable_type)

        return cable_design(layout, substation_coords, n_turbines_p_cable_type, cable_list)
