from input_params import max_n_turbines
import numpy as np
from src.api import AbstractPower
from aero_models import AeroLookup


class PowerPolynomial(AbstractPower):

    def power_model(self, u0):
        if u0 < 4.0:
            power = 0.0
        elif u0 <= 10.0:
            power = (3.234808e-4 * u0 ** 7.0 - 0.0331940121 * u0 ** 6.0 + 1.3883148012 * u0 ** 5.0 - 30.3162345004 * u0 ** 4.0 + 367.6835557011 * u0 ** 3.0 - 2441.6860655008 * u0 ** 2.0 + 8345.6777042343 * u0 - 11352.9366182805) * 1000.0
        elif u0 <= 25.0:
            power = 2000000.0
        else:
            power = 0.0
        return power


class PowerDTU10(AbstractPower):

    def power_model(self, u0):
        table_power = AeroLookup("Input/power_dtu10.dat")
        if wind_speed < cutin:
            return 0.0
        elif wind_speed <= cutout:
            p = table_power.interpolation(wind_speed)
            return p
        else:
            return 0.0
 