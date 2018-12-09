from WINDOW_openMDAO.src.api import AbstractSupportStructureDesign
from WINDOW_openMDAO.SupportStructure.teamplay_folder.teamplay_file import teamplay
import numpy as np


class TeamPlay(AbstractSupportStructureDesign):

    def support_design_model(self, TI, depth, rotor_radius):
        costs = []
        for i in range(len(TI)):
            costs.append(teamplay(TI[i], depth[i], rotor_radius))
        return np.array(costs)
