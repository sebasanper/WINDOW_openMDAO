from WINDOW_openMDAO.src.api import AbstractElectricDesign
from hybrid_heuristic import choose_cables
import numpy as np
from WINDOW_openMDAO.input_params import max_n_substations, max_n_turbines_p_branch, max_n_branches


def distance(turb, sub):
	return np.sqrt((turb[0] - sub[0]) ** 2.0 + (turb[1] - sub[1]) ** 2.0)

class RadialElectrical(AbstractElectricDesign):

    def topology_design_model(self, layout, substation_coords, n_turbines_p_cable_type):

    	length = 0.0
    	ns = len(substation_coords)
    	trees = [[] for _ in range(ns)]
    	for i, turb in enumerate(layout):
    		distances = []
    		for j, sub in enumerate(substation_coords):
    			distances.append([distance(turb, sub), i, j])

    		trees[min(distances)[2]].append(i)


    	costs = length * factor

        return lengths, np.zeros((max_n_substations, max_n_branches, max_n_turbines_p_branch, 2)), costs
