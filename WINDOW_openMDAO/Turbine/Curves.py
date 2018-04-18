from WINDOW_openMDAO.src.api import AbsTurbine
from aero_models import AeroLookup
from WINDOW_openMDAO.input_params import cutin_wind_speed as cutin, cutout_wind_speed as cutout

import os


class Curves(AbsTurbine):

    def turbine_model(self, u, power_table, ct_table):

        if u < cutin:
            power = 0.0
        elif u <= cutout:
            p = power_table.interpolation(u)
            power = p
        else:
            power = 0.0

        if u < cutin:
            ct = 0.0000001
        elif u <= cutout:
            ct = ct_table.interpolation(u)
        else:
            ct = 0.0000001

        return ct, power

