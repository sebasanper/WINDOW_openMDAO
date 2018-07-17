from WINDOW_openMDAO.src.api import AbstractElectricDesign
from hybrid_heuristic import choose_cables
import numpy as np
from WINDOW_openMDAO.input_params import max_n_substations, max_n_turbines_p_branch, max_n_branches
from copy import deepcopy

def distance(turb, sub):
	return np.sqrt((turb[0] - sub[0]) ** 2.0 + (turb[1] - sub[1]) ** 2.0)

class RadialElectrical(AbstractElectricDesign):

    def topology_design_model(self, layout, substation_coords, n_turbines_p_cable_type):
        layout = [[item[1], item[2]] for item in layout]

        def fun(layout, substation_coords):
            copy_layout = deepcopy(layout)
            ordered = {}
            for i, sub in enumerate(substation_coords):
                ordered[i] = []
            for j, turb in enumerate(copy_layout):
                distances = []
                dist = [[distance(turb, sub), index] for index, sub in enumerate(substation_coords)]
                dist.sort()
                ordered[dist[0][1]].append(j)
            return ordered

        def topology(layout, list_turbines, substation, n_turbines_p_cable_type):
            copy_list_turbines = deepcopy(list_turbines)
            length = 0.0
            string = []
            n = 0
            while copy_list_turbines != []:
                if n % n_turbines_p_cable_type == 0:
                    n = 0
                    last_node = substation
                    distances = []
                    string.append([0])
                dist = [[distance(layout[turb], last_node), turb] for turb in copy_list_turbines]
                dist.sort()
                last_node = layout[dist[0][1]]
                length += dist[0][0]
                string[-1].append(dist[0][1])
                copy_list_turbines.remove(dist[0][1])
                n += 1
            return length

        cost_per_m = choose_cables([max(n_turbines_p_cable_type)])[0][1]

        ordered = fun(layout, substation_coords)
        total_length = 0.0
        for sub in ordered:
            total_length += topology(layout, ordered[sub], substation_coords[sub], max(n_turbines_p_cable_type))
        # print max(n_turbines_p_cable_type), ordered
        costs = [total_length * cost_per_m, 0, 0]
        lengths = [total_length, 0, 0]
        return costs, np.zeros((max_n_substations, max_n_branches, max_n_turbines_p_branch, 2)), lengths


# def fun(layout, substation_coords):
#     copy_layout = deepcopy(layout)
#     ordered = {}
#     for i, sub in enumerate(substation_coords):
#         ordered[i] = []
#     for j, turb in enumerate(copy_layout):
#         distances = []
#         dist = [[distance(turb, sub), index] for index, sub in enumerate(substation_coords)]
#         dist.sort()
#         ordered[dist[0][1]].append(j)
#     return ordered

# def topology(layout, list_turbines, substation, n_turbines_p_cable_type):
#     copy_list_turbines = deepcopy(list_turbines)
#     length = 0.0
#     string = []
#     n = 0
#     while copy_list_turbines != []:
#         if n % n_turbines_p_cable_type == 0:
#             n = 0
#             last_node = substation
#             distances = []
#             string.append([0])
#         dist = [[distance(layout[turb], last_node), turb] for turb in copy_list_turbines]
#         dist.sort()
#         last_node = layout[dist[0][1]]
#         length += dist[0][0]
#         string[-1].append(dist[0][1])
#         copy_list_turbines.remove(dist[0][1])
#         n += 1
#     return length


#     # print string

#     # for sub in substation_coords:
#     #     for tur in copy_layout:

# if __name__ == '__main__':

#     def read_layout(layout_file):
#         layout_file = open(layout_file, 'r')
#         layout = []
#         i = 0
#         for line in layout_file:
#             columns = line.split()
#             layout.append([float(columns[0]), float(columns[1])])
#             i += 1

#         return layout

#     layout = read_layout("/home/sebasanper/PycharmProjects/IEA_RWP/horns_rev.dat")
#     substation_coords = [[424140.,  6150340.], [424850.,  6150780.], [428450., 6148900.0]]
#     ordered = fun(layout, substation_coords)
#     # print ordered
#     # with open("/home/sebasanper/PycharmProjects/IEA_RWP/horns_rev_substations.dat", "w") as outf:
#     #     for sub in ordered:
#     #         for turb in ordered[sub]:
#     #             outf.write("{} {} {}\n".format(layout[turb][0], layout[turb][1], sub))
#     #         outf.write("{} {} {}\n".format(substation_coords[sub][0], substation_coords[sub][1], 3))
#     total_length = 0
#     for sub in ordered:
#         total_length += topology(layout, ordered[sub], substation_coords[sub], n_turbines_p_cable_type=7)

#     print total_length
