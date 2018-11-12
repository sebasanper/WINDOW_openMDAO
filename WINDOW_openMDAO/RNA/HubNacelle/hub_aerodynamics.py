from math import radians, sin, cos
import numpy as np

from WINDOW_openMDAO.src.api import AbsHubAerodynamics


#############################################################################
###########################  MODEL#1: Tanuj-DriveSE #########################
#############################################################################        
class Tanuj(AbsHubAerodynamics):
    def compute(self, inputs, outputs):
        # metadata
        safety_factor = self.metadata['safety_factor']
        g = self.metadata['g']
        
        # inputs    
        hub_assembly_mass = inputs['hub_mass'] + inputs['pitch_mass'] + inputs['spinner_mass']
        blade_number = inputs['blade_number']
        blade_mass = inputs['blade_mass']
        shaft_angle = radians(abs(inputs['shaft_angle']))
        rotor_torque = inputs['rotor_torque']
        rotor_thrust = inputs['rotor_thrust']
        
        # Forces and moments at hub centre
        rotor_mass = (blade_mass * blade_number) + hub_assembly_mass
        fx = rotor_thrust + rotor_mass * g * sin(shaft_angle)
        fy = 0 # cancels for all blades
        fz = -1 * rotor_mass * g * cos(shaft_angle)        
        mx = rotor_torque
        my = 0
        mz = 0
        
        # outputs
        outputs['hub_assembly_mass'] = hub_assembly_mass
        outputs['rotor_mass'] = rotor_mass
        outputs['rotor_force'] = np.array([fx, fy, fz])*safety_factor
        outputs['rotor_moment'] = np.array([mx, my, mz])*safety_factor

        