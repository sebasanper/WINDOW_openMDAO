from src.api import AbstractWaterDepth
from scipy.interpolate import interp2d


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
        # interpfunction = interp2d(bathymetry_grid_x, bathymetry_grid_y, bathymetry_grid_depths, kind=degree)
        water_depths = []
        if len(layout[0]) == 3:
            layout = [[i[1], i[2]] for i in layout]
        for coordinate in layout:
            water_depths.append(interpfunction(coordinate[0], coordinate[1])[0])  # Minimum water depth 6 m.
            # water_depths.append(5.8)
        return water_depths
