from src.api import AbstractWaterDepth
from scipy.interpolate import interp2d
import pickle
import numpy as np


class RoughInterpolation(AbstractWaterDepth):

    def depth_model(self, layout):
        bathymetry_grid_x = []
        bathymetry_grid_y = []
        bathymetry_grid_depths = []

        with open("bathymetry2.dat", "r") as bathymetry_file:
            for line in bathymetry_file:
                cols = line.split()
                bathymetry_grid_x.append(float(cols[0]))
                bathymetry_grid_y.append(float(cols[1]))
                bathymetry_grid_depths.append(float(cols[2]))

        degree = 'linear'  # 'cubic' 'quintic'
        interpfunction = interp2d(bathymetry_grid_x, bathymetry_grid_y, bathymetry_grid_depths, kind=degree)
        water_depths = []
        if len(layout[0]) == 3:
            layout = [[i[1], i[2]] for i in layout]
        for coordinate in layout:
            water_depths.append(interpfunction(coordinate[0], coordinate[1])[0])  # Minimum water depth 6 m.
            # water_depths.append(5.8)
        return water_depths

class RoughClosestNode(AbstractWaterDepth):

    def depth_model(self, layout):

        pick_file = open("WaterDepth/bathymetry.pkl", "rb")
        bathymetry = pickle.load(pick_file)
        pick_file.close()


        def closest_node(node, nodes):
            nodes = np.asarray(nodes)
            dist_2 = np.sum((nodes - node)**2, axis=1)
            return np.argmin(dist_2)

        def depth(x, y):
            return bathymetry[closest_node([x, y], bathymetry[:,[0, 1]])][2]

        water_depths = []
        if len(layout[0]) == 3:
            layout = [[i[1], i[2]] for i in layout]
        for coordinate in layout:
            water_depths.append(depth(coordinate[0], coordinate[1]))  # Minimum water depth 6 m.
        return water_depths
