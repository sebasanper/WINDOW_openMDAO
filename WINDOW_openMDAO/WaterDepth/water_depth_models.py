"""Summary
"""
from WINDOW_openMDAO.src.api import AbstractWaterDepth
# from scipy.interpolate import interp2d
import numpy as np


# class RoughInterpolation(AbstractWaterDepth):

#     """Summary
#     """
    
#     def depth_model(self, layout):
#         """Summary
        
#         Args:
#             layout (TYPE): Description
        
#         Returns:
#             TYPE: Description
#         """
#         bathymetry_grid_x = []
#         bathymetry_grid_y = []
#         bathymetry_grid_depths = []

#         with open(bathymetry_path, "r") as bathymetry_file:
#             for line in bathymetry_file:
#                 cols = line.split()
#                 bathymetry_grid_x.append(float(cols[0]))
#                 bathymetry_grid_y.append(float(cols[1]))
#                 bathymetry_grid_depths.append(float(cols[2]))

#         degree = 'linear'  # 'cubic' 'quintic'
#         interpfunction = interp2d(bathymetry_grid_x, bathymetry_grid_y, bathymetry_grid_depths, kind=degree)
#         water_depths = []
#         if len(layout[0]) == 3:
#             layout = [[i[1], i[2]] for i in layout]
#         for coordinate in layout:
#             water_depths.append(interpfunction(coordinate[0], coordinate[1])[0])  # Minimum water depth 6 m.
#             # water_depths.append(5.8)
#         return water_depths


class RoughClosestNode(AbstractWaterDepth):

    """Summary
    """
    @vectorize(float64(float64))
    def depth_model(self, layout):
        """Summary
        
        Args:
            layout (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        bathymetry = np.loadtxt(self.bathymetry_path)
        bathymetry_inside = bathymetry[~np.isnan(bathymetry).any(axis=1)]
        deltas = np.subtract(layout, bathymetry_inside[:,:2][:,np.newaxis])
        dist_2 = np.sum(deltas ** 2., axis=2)
        idx_closest_nodes = np.argmin(dist_2, axis=0)
        water_depths = bathymetry_inside[idx_closest_nodes][:,2]

        return water_depths
