from WINDOW_openMDAO.src.api import AbstractSupportStructureDesign
import numpy as np


class ConstantSupport(AbstractSupportStructureDesign):

    def support_design_model(self, TI, depth):
        costs = []
        for i in range(len(TI)):
            costs.append(5000000.0)
        return np.array(costs)
