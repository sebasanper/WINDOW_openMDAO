from src.api import AbsTurbine
from aero_models import AeroLookup
from input_params import cutin_wind_speed as cutin, cutout_wind_speed as cutout


class Curves(AbsTurbine):

    def turbine_model(self, u):

        table = AeroLookup("Turbine/power_dtu10.dat")
        if u < cutin:
            power = 0.0
        elif u <= cutout:
            p = table.interpolation(u)
            power = p * 1000.0
        else:
            power = 0.0

        table = AeroLookup("Turbine/ct_dtu10.dat")
        if u < cutin:
            ct = 0.0000001
        elif u <= cutout:
            ct = table.interpolation(u)
        else:
            ct = 0.0000001

        return ct, power
