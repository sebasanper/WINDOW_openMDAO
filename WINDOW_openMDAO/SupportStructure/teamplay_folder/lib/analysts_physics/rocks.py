# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 14:04:24 2015

@author: Αλβέρτος
"""

from math import exp, pi, sqrt, sin, cos, log

# from scipy.optimize import brentq


class RockAnalysts:
    rho_stone = 2700  # [kg/m^3]
    nu_water = 1.2e-6  # [m^2/s]
    g = 9.81  # [m/s^2]

    '''
    # [designation, d15, d50(min.), d85]
    standard_gradings = ([["none", 0.0, 0.0, 0.0],
                          ["2/8inch", 0.005, 0.0118, 0.02],
                          ["30/60", 0.03, 0.0423, 0.06],
                          ["40/100", 0.04, 0.0658, 0.1],
                          ["50/150", 0.05, 0.094, 0.15],
                          ["80/200", 0.08, 0.132, 0.2],
                          ["5-40", 0.152, 0.201, 0.305],
                          ["10-60", 0.192, 0.253, 0.349],
                          ["40-200", 0.305, 0.386, 0.521],
                          ["60-300", 0.349, 0.454, 0.596],
                          ["100-500", 0.413, 0.524, 0.707],
                          ["0.3-1", 0.596, 0.719, 0.891],
                          ["1-3", 0.891, 1.04, 1.28],
                          ["3-6", 1.28, 1.38, 1.62],
                          ["6-10", 1.62, 1.67, 1.92]])
    '''

    def __init__(self, support_team):
        self.support_team = support_team

    def get_critical_friction(self, d50):
        s = self.rho_stone / self.support_team.physical_environment.site.water_density
        d_star = ((self.g * (s - 1.0)) / self.nu_water**2)**(1.0/3.0) * d50
        critical_shields_factor = (0.30 / (1.0 + 1.2 * d_star)) + (0.055 * (1.0 - exp(-0.020 * d_star)))
        return critical_shields_factor * self.g * (self.rho_stone - self.support_team.physical_environment.site.water_density) * d50
    
    def get_characteristic_friction(self, d50, current, amplitude_bottom_velocity, wave_period, wave_current_angle):
        wave_friction = self.get_wave_friction(d50, amplitude_bottom_velocity, wave_period)
        current_friction = self.get_current_friction(d50, current)
        mean_friction = current_friction * (1.0 + 1.2 * (wave_friction / (current_friction + wave_friction))**3.2)
        return sqrt((mean_friction + wave_friction * cos(wave_current_angle))**2 + (wave_friction * sin(wave_current_angle))**2)
        
    def get_wave_friction(self, d50, amplitude_bottom_velocity, wave_period):
        amplitude_bottom_motion = (amplitude_bottom_velocity * wave_period) / (2.0 * pi)
        r_w = amplitude_bottom_velocity * amplitude_bottom_motion / self.nu_water
        r = amplitude_bottom_motion / (2.5 * d50)
        
        # f_w = brentq(self.f_w_factor, 0.001, 1.0, args = (r_w, r), xtol = 0.001) # This equation gives problems for small waves
        f_wr = 0.237 * r ** (- 0.52)
        if r_w < 100000:
            f_ws = 2.0 * r_w ** (- 0.5)
        else: 
            f_ws = 0.0521 * r_w ** (- 0.187)
        
        f_w = max(f_wr, f_ws)

        return 0.5 * self.support_team.physical_environment.site.water_density * f_w * amplitude_bottom_velocity ** 2.0

    def f_w_factor(self, d, *args):
        f_w = d
        r_w = args[0]
        r = args[1]
        
        lefthand_side = 0.32 / f_w 
        righthand_side = ((log(6.36 * r * sqrt(f_w)) -
                           log(1.0 - exp(- 0.0262 * r_w * sqrt(f_w) / r)) +
                           4.71 * r / (r_w * sqrt(f_w))) ** 2.0 + 1.64)
        
        return (lefthand_side / righthand_side) - 1.0

    def get_current_friction(self, d50, current):
        z_0 = 2.5 * d50 / 30.0
        c_d = (0.40 / (1.0 + log(z_0 / self.support_team.physical_environment.site.water_depth))) ** 2.0
        return self.support_team.physical_environment.site.water_density * c_d * current ** 2.0
