# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 15:10:53 2015

@author: Αλβέρτος
"""

from math import pi


class RNAAnalysts:
    rho_air = 1.225  # [kg/m^3]

    def __init__(self, support_team):
        self.support_team = support_team
        self.properties = self.support_team.properties.rna

    def initialyse(self):
        pass
        # self.power_curve = InterpolatedArray(self.support_team.properties.rna.power_curve)
        # self.thrust_curve = InterpolatedArray(self.support_team.properties.rna.thrust_curve)
        # self.properties.rated_power = max([x[1] for x in self.support_team.properties.rna.power_curve])

    def get_loads(self, wind_condition, wind_speed, height):

        if wind_condition == "operation":
            fx = self.properties.max_thrust
        elif wind_condition == "max_50_year":
            nacelle_force = 0.5 * self.rho_air * wind_speed ** 2 * self.properties.front_area_nacelle * self.properties.cd_nacelle
            rotor_force = 0.5 * self.rho_air * wind_speed ** 2 * self.properties.solidity_rotor * pi * self.properties.rotor_radius ** 2 * self.properties.cd_rotor_idle_vane
            fx = nacelle_force + rotor_force
        elif wind_condition == "red_50_year":
            nacelle_force = 0.5 * self.rho_air * wind_speed ** 2 * self.properties.front_area_nacelle * self.properties.cd_nacelle
            rotor_force = 0.5 * self.rho_air * wind_speed ** 2 * self.properties.solidity_rotor * pi * self.properties.rotor_radius ** 2 * self.properties.cd_rotor_idle_vane
            fx = nacelle_force + rotor_force

        my = fx * (self.support_team.properties.support_structure.hub_height - height)
        return [fx, 0.0, 0.0, 0.0, my, 0.0]

    # def get_Ct(self, wind_speed):
    #     """
    #     if wind_speed < 25.0:
    #         return min(0.8, 7.0 / wind_speed) # Expression is based on Figure 1 of the article of frohboese (in 'wakes' directory)
    #     return 0.0
    #     """
    #     return self.thrust_curve[wind_speed]
    #
    # # def get_power(self, wind_speed):
    # #     """
    # #     if wind_speed < 25.0:
    # #         return min (0.5 * self.rho_air * 0.48 * 0.9 * pi * self.properties.rotor_radius**2 * wind_speed**3, 3600000.0)
    # #     return 0.0
    # #     """
    # #     return self.power_curve[wind_speed]


class InterpolatedArray(object):
    # Based on: www.zovirl.com/2008/11/04/interpolated-lookup-tables-in-python/
    # Faster, but more complicated:
    # www.shocksolution.com/2008/12/a-lookup-table-for-fast-python-math/
    # www.shocksolution.com/2009/01/optimizing-python-code-for-fast-math/
    # www.shocksolution.com/2009/04/lookup-tables-and-spline-fitting-in-python/
    """An array-like object that provides
    interpolated values between set points."""

    def __init__(self, points):
        self.points = sorted(points)

    def __getitem__(self, x):
        if x < self.points[0][0] or x > self.points[-1][0]:
            raise ValueError
        lower_point, upper_point = self._get_bounding_points(x)
        return self._interpolate(x, lower_point, upper_point)

    def _get_bounding_points(self, x):
        """Get the lower/upper points that bound x."""
        lower_point = None
        upper_point = self.points[0]
        for point in self.points[1:]:
            lower_point = upper_point
            upper_point = point
            if x <= upper_point[0]:
                break
        return lower_point, upper_point

    def _interpolate(self, x, lower_point, upper_point):
        """Interpolate a Y value for x given lower & upper
        bounding points."""
        slope = (float(upper_point[1] - lower_point[1]) /
                 (upper_point[0] - lower_point[0]))
        return lower_point[1] + (slope * (x - lower_point[0]))


class InterpolatedArrayOriginal(object):
    def __init__(self, points):
        self.points = sorted(points)

    def __getitem__(self, x):
        if x < self.points[0][0] or x > self.points[-1][0]:
            raise ValueError
        lower_point, upper_point = self._GetBoundingPoints(x)
        return self._Interpolate(x, lower_point, upper_point)

    def _GetBoundingPoints(self, x):
        """Get the lower/upper points that bound x."""
        lower_point = None
        upper_point = self.points[0]
        for point in self.points[1:]:
            lower_point = upper_point
            upper_point = point
            if x <= upper_point[0]:
                break
        return lower_point, upper_point

    def _Interpolate(self, x, lower_point, upper_point):
        """Interpolate a Y value for x given lower & upper
        bounding points."""
        slope = (float(upper_point[1] - lower_point[1]) /
                 (upper_point[0] - lower_point[0]))
        return lower_point[1] + (slope * (x - lower_point[0]))


'''
points = ((1, 0), (5, 10), (10, 0))
table = InterpolatedArray(points)
print table[1]
print table[3.2]
print table[7]
'''
