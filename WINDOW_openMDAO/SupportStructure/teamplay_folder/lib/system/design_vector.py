# -*- coding: utf-8 -*-
"""
Created on Wed Nov 04 13:10:18 2015

@author: Αλβέρτος
"""

# TOTAL SYSTEM **************************************************


class DesignVector:
    def __init__(self):
#        self.linking_variables = None
         self.support_structure = SupportStructure()
        
# LINKING VARIABLES **************************************************

#class LinkingVariables:
#    operational_lifetime = 20 # [years] - FIXED VALUE NOTE: The fixed price in PPA is valid for a number of full load hours that is reached in appr. 10 years. After that, market prices apply.
#    #location_id = 0 # [-]
#    number_wts_row = 8 # [-] Horns Rev website
#    number_wts_column = 10 # [-] Horns Rev website
#    
#    def __init__(self):
#        pass

# SUPPORT STRUCTURE **************************************************


class SupportStructure:
    def __init__(self):
        self.monopile = Monopile()
        self.transition_piece = TransitionPiece()
        self.tower = Tower()
        self.scour_protection = ScourProtection()
#        self.boat_landing = BoatLanding()
#        self.platform = Platform()
#        self.access_facilities = AccessFacilities()
#        self.platform_crane = PlatformCrane()


class Monopile:
    diameter = 0.0  # [m]
    wall_thickness = 0.0  # [m]
    length = 0.0  # [m]
    penetration_depth = 0.0  # [m]

    def __init__(self):
        pass


class TransitionPiece:
    diameter = 0.0 # [m]
    wall_thickness = 0.0 # [m]
    length = 0.0 # [m]
    overlap_monopile = 0.0 # [m] 

    def __init__(self):
        pass


class Tower:
    base_diameter = 0.0  # [m]
    top_diameter = 0.0  # [m]
    length = 0.0  # [m]
    
    def __init__(self):
        self.wall_thickness = []  # per segment - index 0 indicates lowest segment [m]


class ScourProtection:
    diameter = 0.0  # [m]

    def __init__(self):
        self.armour = [0.0, 0.0, 0.0, 0.0, 0.0] # [m, m, m, m, m] - [d15, d50, d85, thickness in annulus up to 1 times pile diameter, thickness further away from pile]
        self.filter = [[0.0, 0.0, 0.0, 0.0]] # [m, m, m, m] - [d15, d50, d85, thickness]

#class BoatLanding:
#    TBD = 0 # [?]
#
#    def __init__(self):
#        pass
#
#class Platform:
#    TBD = 0 # [?]
#
#    def __init__(self):
#        pass
#
#class AccessFacilities:
#    TBD = 0 # [?]
#
#    def __init__(self):
#        pass
#
#class PlatformCrane:
#    TBD = 0 # [?]
#
#    def __init__(self):
#        pass

