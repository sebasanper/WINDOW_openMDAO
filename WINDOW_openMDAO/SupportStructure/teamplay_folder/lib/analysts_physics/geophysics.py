# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 17:53:24 2015

@author: Αλβέρτος
"""

from math import pi, sin

from scipy.optimize import brentq  # newton


class GeophysicalAnalysts:
    multiplier_blum = 1.1
    
    def __init__(self, support_team):
        self.support_team = support_team

    def initialise_clamping_analysis(self):
        phi = self.support_team.physical_environment.site.friction_angle
        gamma = self.support_team.physical_environment.site.submerged_unit_weight
        phi_rad = phi * pi / 180.0
        kp = (1.0 + sin(phi_rad) / (1.0 - sin(phi_rad)))
        ka = (1.0 - sin(phi_rad) / (1.0 + sin(phi_rad)))
        
        self.factor = (kp - ka) * gamma * self.support_team.design_variables.support_structure.monopile.diameter / 6.0

    def get_clamping_depth(self, fx, my):    
        pile_penetration = brentq(self.bearing_reserve, 0.1, 1000.0, args=(fx, my), xtol=0.01)
        return self.multiplier_blum * pile_penetration 

    def bearing_reserve(self, d, *args):
        l_pile = d
        fx = args[0]
        my = args[1]

        return self.factor * l_pile ** 2.0 - (fx + my) / l_pile
