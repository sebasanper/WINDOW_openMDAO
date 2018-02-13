# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 15:35:19 2015

@author: Αλβέρτος
"""

from math import pi


class GravityAnalysts:
    g = 9.81
    rho_steel = 7850.0  # [kg/m^3]
    rho_grout = 2600.0  # [kg/m^3]
    
    def __init__(self, support_team):
        self.support_team = support_team

    def get_loads(self, height):
        
        fz = self.support_team.properties.rna.mass * -self.g
        my = -fz * self.support_team.properties.rna.mass_eccentricity
        
        base_diameter = self.support_team.design_variables.support_structure.tower.base_diameter
        top_diameter = self.support_team.design_variables.support_structure.tower.top_diameter
        base = self.support_team.properties.support_structure.platform_height
        top = self.support_team.properties.support_structure.platform_height + self.support_team.design_variables.support_structure.tower.length 

        for i in range(self.support_team.properties.support_structure.nr_segments):
            z_from = base + i * self.support_team.properties.support_structure.segment_length
            z_to = base + (i + 1) * self.support_team.properties.support_structure.segment_length
            if z_from < height < z_to:
                z_from = height
            if z_to > height:
                t = self.support_team.design_variables.support_structure.tower.wall_thickness[i]
                fz -= self.g * self.rho_steel * self.get_integrated_volume(base, top, base_diameter, top_diameter,
                                                                           z_from, z_to, t)
        
        if height < self.support_team.properties.support_structure.platform_height:
            base_diameter = self.support_team.design_variables.support_structure.transition_piece.diameter
            top_diameter = base_diameter
            base = self.support_team.properties.support_structure.base_tp 
            top = self.support_team.properties.support_structure.platform_height
            z_from = base
            if z_from < height:
                z_from = height
            z_to = top
            t = self.support_team.design_variables.support_structure.transition_piece.wall_thickness
            fz -= self.g * self.rho_steel * self.get_integrated_volume(base, top, base_diameter, top_diameter, z_from,
                                                                       z_to, t)
        
        pile_top = self.support_team.properties.support_structure.base_tp + self.support_team.design_variables.support_structure.transition_piece.overlap_monopile
        if height < pile_top:
            base_diameter = (self.support_team.design_variables.support_structure.transition_piece.diameter -
                             2 * self.support_team.design_variables.support_structure.transition_piece.wall_thickness)
            top_diameter = base_diameter
            base = self.support_team.properties.support_structure.base_tp 
            top = pile_top
            z_from = base
            if z_from < height:
                z_from = height
            z_to = top
            t = (base_diameter - self.support_team.design_variables.support_structure.monopile.diameter) / 2.0
            fz -= self.g * self.rho_grout * self.get_integrated_volume(base, top, base_diameter, top_diameter, z_from,
                                                                       z_to, t)

            base_diameter = self.support_team.design_variables.support_structure.monopile.diameter
            top_diameter = base_diameter
            t = self.support_team.design_variables.support_structure.monopile.wall_thickness
            fz -= self.g * self.rho_steel * self.get_integrated_volume(base, top, base_diameter, top_diameter, z_from,
                                                                       z_to, t)
        
        if height < self.support_team.properties.support_structure.base_tp:
            base_diameter = self.support_team.design_variables.support_structure.monopile.diameter
            top_diameter = base_diameter
            base = height 
            top = self.support_team.properties.support_structure.base_tp
            z_from = base
            z_to = top
            t = self.support_team.design_variables.support_structure.monopile.wall_thickness
            fz -= self.g * self.rho_steel * self.get_integrated_volume(base, top, base_diameter, top_diameter, z_from,
                                                                       z_to, t)

        return [0.0, 0.0, fz, 0.0, my, 0.0]

    def get_mass(self, component):
        mass = 0.0
#        print component
        if component == 'tower':
            base_diameter = self.support_team.design_variables.support_structure.tower.base_diameter
            top_diameter = self.support_team.design_variables.support_structure.tower.top_diameter
            base = self.support_team.properties.support_structure.platform_height
            top = self.support_team.properties.support_structure.platform_height + self.support_team.design_variables.support_structure.tower.length 
    
            for i in range(self.support_team.properties.support_structure.nr_segments):
                z_from = base + i * self.support_team.properties.support_structure.segment_length
                z_to = base + (i + 1) * self.support_team.properties.support_structure.segment_length
                t = self.support_team.design_variables.support_structure.tower.wall_thickness[i]
                mass += self.rho_steel * self.get_integrated_volume(base, top, base_diameter, top_diameter, z_from, z_to, t)
            mass *= 1.10  # 10% extra for secondary steel, such as flanges, stairs and platforms
        
        if component == 'transition piece':
            base_diameter = self.support_team.design_variables.support_structure.transition_piece.diameter
            top_diameter = base_diameter
            base = self.support_team.properties.support_structure.base_tp 
            top = self.support_team.properties.support_structure.platform_height
            z_from = base
            z_to = top
            t = self.support_team.design_variables.support_structure.transition_piece.wall_thickness
            mass = self.rho_steel * self.get_integrated_volume(base, top, base_diameter, top_diameter, z_from, z_to, t)
            mass *= 1.10  # 10% extra for secondary steel, such as flange, boat landing, stairs and platforms

        pile_top = self.support_team.properties.support_structure.base_tp + self.support_team.design_variables.support_structure.transition_piece.overlap_monopile
        if component == 'grout':
            base_diameter = (self.support_team.design_variables.support_structure.transition_piece.diameter -
                             2 * self.support_team.design_variables.support_structure.transition_piece.wall_thickness)
            top_diameter = base_diameter
            base = self.support_team.properties.support_structure.base_tp 
            top = pile_top
            z_from = base
            z_to = top
            t = (base_diameter - self.support_team.design_variables.support_structure.monopile.diameter) / 2.0
            mass = self.rho_grout * self.get_integrated_volume(base, top, base_diameter, top_diameter, z_from, z_to, t)

        if component == 'monopile':
            base_diameter = self.support_team.design_variables.support_structure.monopile.diameter
            top_diameter = base_diameter
            base = pile_top - self.support_team.design_variables.support_structure.monopile.length
            top = pile_top
            z_from = base
            z_to = top
            t = self.support_team.design_variables.support_structure.monopile.wall_thickness
            mass = self.rho_steel * self.get_integrated_volume(base, top, base_diameter, top_diameter, z_from, z_to, t)
        
        return mass

    def get_integrated_volume(self, base, top, base_diameter, top_diameter, z_from, z_to, t):
        a = z_from
        b = z_to
        l = top - base
        d_diameter = top_diameter - base_diameter
        
        if d_diameter == 0.0:
            return (1.0 / 4.0) * pi * (base_diameter**2 - (base_diameter - 2.0 * t)**2) * (b - a)
        
        else:
            return ((1.0 / 4.0) * pi * (l / (3.0 * d_diameter)) *
                    (((base_diameter + (b - base) * d_diameter / l) ** 3.0 - (base_diameter - 2.0 * t + (b - base) * d_diameter / l) ** 3) -
                     ((base_diameter + (a - base) * d_diameter / l) ** 3.0 - (base_diameter - 2.0 * t + (a - base) * d_diameter / l) ** 3.0)
                     ))
