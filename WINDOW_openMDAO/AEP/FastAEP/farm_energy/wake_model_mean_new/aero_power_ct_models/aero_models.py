from util import interpolate
from numpy import pi
from WINDOW_openMDAO.AEP.FastAEP.farm_energy.wake_model_mean_new.memoize import Memoize, countcalls
from WINDOW_openMDAO.input_params import cutout_wind_speed, cutin_wind_speed, rotor_radius, wind_speed_at_max_thrust as rated_wind, turbine_rated_power


class AeroLookup:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def interpolation(self, value):
        ii = 0
        lower = []
        upper = []
        if value <= self.x[0]:
            result = self.y[0]
        elif value < self.x[-1]:
            for x in self.x:
                if x <= value:
                    lower = [x, self.y[ii]]
                else:
                    upper = [x, self.y[ii]]
                    break
                ii += 1
            result = interpolate(float(lower[0]), float(lower[1]), float(upper[0]), float(upper[1]), value)
        else:
            result = self.y[-1]
        return result

# @countcalls
def power(wind_speed, table_power, cutin=cutin_wind_speed, cutout=cutout_wind_speed, rated=rated_wind, r=rotor_radius):
    if all(cp < 10.0 for cp in table_power.y):
        if wind_speed < cutin:
            return 0.0
        elif wind_speed <= rated:
            cp = table_power.interpolation(wind_speed)
            return 0.5 * 1.225 * pi * r ** 2.0 * wind_speed ** 3.0 * cp
        elif wind_speed <= cutout:
            return turbine_rated_power
        else:
            return 0.0
    if wind_speed < cutin:
        return 0.0
    elif wind_speed <= cutout:
        p = table_power.interpolation(wind_speed)
        return p
    else:
        return 0.0


# power = Memoize(power)

# @countcalls
def thrust_coefficient(wind_speed, ct_table):
    ct = ct_table.interpolation(wind_speed)
    if ct > 0.9:
        ct = 0.9
    elif ct < 0.05:
        ct = 0.05
    return ct


# thrust_coefficient = Memoize(thrust_coefficient)
