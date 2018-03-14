from WINDOW_openMDAO.src.api import AbsTurbine
from aero_models import AeroLookup
from WINDOW_openMDAO.input_params import cutin_wind_speed as cutin, cutout_wind_speed as cutout

print cutin
from WINDOW_openMDAO.input_params import power_curve_path, ct_curve_path
import os


class Curves(AbsTurbine):

    def turbine_model(self, u):

        table = AeroLookup(power_curve_path)
        if u < cutin:
            power = 0.0
        elif u <= cutout:
            p = table.interpolation(u)
            power = p
        else:
            power = 0.0

        table = AeroLookup(ct_curve_path)
        if u < cutin:
            ct = 0.0000001
        elif u <= cutout:
            ct = table.interpolation(u)
        else:
            ct = 0.0000001

        return ct, power

