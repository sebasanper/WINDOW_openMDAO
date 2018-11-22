from __future__ import absolute_import
from WINDOW_openMDAO.src.api import AbstractElectricDesign
from .POS_electrical import cable_design, choose_cables


class POSHeuristic(AbstractElectricDesign):

    def topology_design_model(self, layout, substation_coords, n_turbines_p_cable_type):
        cable_list = choose_cables([max(n_turbines_p_cable_type), 0, 0])
        return cable_design(layout, substation_coords, [max(n_turbines_p_cable_type), 0, 0], cable_list)
