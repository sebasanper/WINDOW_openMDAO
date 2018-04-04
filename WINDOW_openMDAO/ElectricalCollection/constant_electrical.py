from WINDOW_openMDAO.src.api import AbstractElectricDesign
from hybrid_heuristic import choose_cables
import numpy as np
from WINDOW_openMDAO.input_params import max_n_substations, max_n_turbines_p_branch, max_n_branches


class ConstantElectrical(AbstractElectricDesign):

    def topology_design_model(self, layout, substation_coords, n_turbines_p_cable_type):
        cable_list = choose_cables(n_turbines_p_cable_type)
        []
        nt = len(layout)
        lengths = [nt * 195.0 * 5.0, 0, 0]
        costs = [cable_list[-1][1] * lengths[0], 0, 0] 
        return lengths, np.zeros((max_n_substations, max_n_branches, max_n_turbines_p_branch, 2)), costs
