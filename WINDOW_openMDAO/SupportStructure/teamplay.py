from WINDOW_openMDAO.src.api import AbstractSupportStructureDesign
from WINDOW_openMDAO.SupportStructure.teamplay_folder.teamplay_file import teamplay
import numpy as np


class TeamPlay(AbstractSupportStructureDesign):

    def support_design_model(self, TI, depth, rotor_radius, rated_wind_speed, \
                             rotor_thrust, rna_mass, \
                             solidity_rotor, cd_rotor_idle_vane, cd_nacelle, \
                             yaw_diameter, front_area_nacelle, yaw_to_hub_height, mass_eccentricity):
        costs = []
        for i in range(len(TI)):
            costs.append(teamplay(TI[i], depth[i], rotor_radius, rated_wind_speed, \
                                  rotor_thrust, rna_mass, \
                                  solidity_rotor, cd_rotor_idle_vane, cd_nacelle, \
                                  yaw_diameter, front_area_nacelle, yaw_to_hub_height, mass_eccentricity))
        return np.array(costs)
