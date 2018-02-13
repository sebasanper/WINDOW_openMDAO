# -*- coding: utf-8 -*-
"""
Created on Mon Nov 09 16:16:43 2015

@author: Αλβέρτος
"""

class Value:
    def __init__(self):
        
        self.economic = Economic()
        
        
class Economic:
    def __init__(self):
        
        self.capex = Capex()
        self.decommissioning = Decommissioning()
        

# Capex **************************************************

class Capex:
    total = 0.0 # [Euro]
   
    
    def __init__(self):
        
        self.procurement = Procurement()
        self.installation = Installation()
        
    def set_total(self):
      
        self.procurement.set_total()
        self.installation.set_total()
        self.total = (self.procurement.total +
                      self.installation.total)

# Procurement **************************************************

class Procurement:
    total = 0.0 # [Euro]
    
    def __init__(self):
      
        self.support_structures = ProcureSupportStructures()
        
        
    def set_total(self):
        
        self.support_structures.set_total()
        
        self.total = (self.support_structures.total)                    


# Procure support structures **************************************************

class ProcureSupportStructures:
    total = 0.0 # [Euro]
    tower = 0.0 # [Euro]
    transition_piece = 0.0 # [Euro]
#    boat_landing = 0.0 # [Euro]
#    grout = 0.0 # [Euro]
    monopile = 0.0 # [Euro]
    scour_protection = 0.0 # [Euro]
    
    def __init__(self):
        pass
        
    def set_total(self):
        self.total = (self.tower +
                      self.transition_piece +
                      self.monopile +
                      self.scour_protection)


# Installation **************************************************

class Installation:
    total = 0.0 # [Euro]
    foundations = 0.0 # [Euro]
    
    def __init__(self):
        pass
       
    def set_total(self):
        
        self.total = self.foundations 
                      
# Decommissioning **************************************************

class Decommissioning:
    total = 0.0 # [Euro]
        
    def __init__(self):
        self.removal = Removal()
        pass
        
    def set_total(self):
        self.removal.set_total()
        
        self.total = self.removal.total 
                      
# Removal **************************************************

class Removal:
    total = 0.0 # [Euro]
    
    foundations = 0.0 # [Euro]
    scour_protection = 0.0 # [Euro]
    
    
    def __init__(self):
        pass
        
    def set_total(self):
        self.total = (self.foundations + self.scour_protection)

