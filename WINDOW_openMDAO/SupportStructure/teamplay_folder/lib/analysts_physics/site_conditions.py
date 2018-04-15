from numpy import pi, sqrt, sinh, tanh, exp
from math import gamma

from scipy.optimize import newton


# VERTICAL HEIGHTS W.R.T. MSL


class SiteConditionsAnalysts:
    g = 9.81

    # number_of_sectors = 144  # MUST BE MULTIPLE OF 4 !!! Number of sectors for which farm power is determined
    # number_of_bins = 25  # Number of wind speeds for which farm power is determined

    def __init__(self, support_team):
        self.support_team = support_team
        self.site_conditions = self.support_team.physical_environment.site
        pass

    def set_conditions(self):

        # self.set_Vaverage()
        # self.set_angle_wave_current_50_year_rad()
        # self.set_wind_pdfs()

        self.site_conditions.Hmax_50_year = 1.86 * self.site_conditions.Hs_50_year

        self.site_conditions.Tmax_50_year = 11.1 * sqrt(self.site_conditions.Hmax_50_year / self.g)
        self.site_conditions.kmax_50_year = self.get_wave_number(self.site_conditions.Tmax_50_year)
        self.site_conditions.Hmax_50_year = min(self.site_conditions.Hmax_50_year,
                                                self.wave_limit(self.site_conditions.kmax_50_year))
        self.site_conditions.Tpeak_50_year = 1.4 * 11.1 * sqrt(self.site_conditions.Hs_50_year / self.g)
        self.site_conditions.Uw_50_year = (pi * self.site_conditions.Hs_50_year /
                                           (self.site_conditions.Tpeak_50_year * sinh(self.get_wave_number(
                                               self.site_conditions.Tpeak_50_year) * self.site_conditions.water_depth)))
        self.site_conditions.Hred_50_year = 1.32 * self.site_conditions.Hs_50_year
        self.site_conditions.Tred_50_year = 11.1 * sqrt(self.site_conditions.Hred_50_year / self.g)
        self.site_conditions.kred_50_year = self.get_wave_number(self.site_conditions.Tred_50_year)
        self.site_conditions.Hred_50_year = min(self.site_conditions.Hred_50_year,
                                                self.wave_limit(self.site_conditions.kred_50_year))
        self.site_conditions.Hmax_1_year = 1.86 * self.site_conditions.Hs_1_year
        self.site_conditions.Tmax_1_year = 11.1 * sqrt(self.site_conditions.Hmax_1_year / self.g)
        self.site_conditions.kmax_1_year = self.get_wave_number(self.site_conditions.Tmax_1_year)
        self.site_conditions.Hmax_1_year = min(self.site_conditions.Hmax_1_year,
                                               self.wave_limit(self.site_conditions.kmax_1_year))
        self.site_conditions.max_crest = self.site_conditions.hat + self.site_conditions.storm_surge_pos + 0.55 * self.site_conditions.Hmax_50_year
        self.site_conditions.min_crest = self.site_conditions.lat + self.site_conditions.storm_surge_pos - 0.45 * self.site_conditions.Hmax_50_year
        self.site_conditions.Vreference = self.site_conditions.Vaverage * 5
        self.site_conditions.Vmax_50_year = 1.2 * self.site_conditions.Vreference
        self.site_conditions.Vred_50_year = (1.2 / 1.1) * self.site_conditions.Vreference
        # print self.site_conditions.water_depth

    # def set_Vaverage(self):
    #     self.site_conditions.Vaverage = self.site_conditions.scale_factor * gamma(
    #         1.0 + 1.0 / self.site_conditions.shape_factor)

    def set_angle_wave_current_50_year_rad(self):
        self.site_conditions.angle_wave_current_50_year_rad = self.site_conditions.angle_wave_current_50_year * pi / 180.0

    # def set_wind_pdfs(self):
    #     _wind_directions = self.get_wind_directions(0.0)
    #     _wind_speeds = self.get_wind_speeds(self.site_conditions.ref_height_wind_speed)
    #     self.site_conditions.wind_rose_probability = []
    #     for wd in range(len(_wind_directions)):
    #         self.site_conditions.wind_rose_probability.append(range(len(_wind_speeds)))
    #         if wd == 0:
    #             _sector_factor = 0.5 * (_wind_directions[wd + 1] - _wind_directions[(len(_wind_directions) - 1)]) / (
    #                 2 * pi)
    #         elif wd == (len(_wind_directions) - 1):
    #             _sector_factor = 0.5 * (_wind_directions[0] - _wind_directions[wd - 1]) / (2 * pi)
    #         else:
    #             _sector_factor = 0.5 * (_wind_directions[wd + 1] - _wind_directions[wd - 1]) / (2 * pi)
    #         if _sector_factor < 0.0:
    #             _sector_factor += 0.5  # Factor 0.5 is the result of + pi / (2 * pi)
    #
    #         for ws in range(len(_wind_speeds)):
    #             if ws == 0:
    #                 _bin_width = 0.5 * (_wind_speeds[ws + 1] - _wind_speeds[0]) + _wind_speeds[0]
    #             elif ws == (len(_wind_speeds) - 1):
    #                 _bin_width = 0.5 * (_wind_speeds[ws] - _wind_speeds[ws - 1])
    #             else:
    #                 _bin_width = 0.5 * (_wind_speeds[ws + 1] - _wind_speeds[ws - 1])
    #
    #             c = self.site_conditions.scale_factor
    #             k = self.site_conditions.shape_factor
    #
    #             _probability_density = (k / c) * (_wind_speeds[ws] / c) ** (k - 1.0) * exp(
    #                 -1.0 * (_wind_speeds[ws] / c) ** k)
    #             self.site_conditions.wind_rose_probability[wd][ws] = _probability_density * _bin_width * _sector_factor
    #
    #     self.site_conditions.wind_speed_probability = []
    #     for ws in range(len(_wind_speeds)):
    #         _probability = 0.0
    #         for wd in range(len(_wind_directions)):
    #             _probability = _probability + self.site_conditions.wind_rose_probability[wd][ws]
    #         self.site_conditions.wind_speed_probability.append(_probability)

    # def get_wind_directions(self, offset):
    #     _sectors = []
    #     for wd in range(self.number_of_sectors):
    #         _sectors.append(self.get_wind_direction(wd) - offset)
    #     return _sectors

    # def get_wind_speeds(self, height):
    #     _bins = []
    #     for ws in range(self.number_of_bins):
    #         _bins.append(self.get_wind_speed(ws, height))
    #     return _bins

    # def get_wind_direction(self, index):
    #     self.support_team.wind_farm_orientation = 0.0  # [degrees w.r.t. north - clockwise positive]
    #     _wind_direction = (float(index) / float(
    #         self.number_of_sectors)) * 2.0 * pi + self.support_team.wind_farm_orientation * pi / 180.0
    #     if _wind_direction >= 2.0 * pi:
    #         _wind_direction -= 2.0 * pi
    #     if _wind_direction < 0.0:
    #         _wind_direction += 2.0 * pi
    #     return _wind_direction

    # def get_wind_speed(self, index, height):
    #
    #     _wind_speed_ref = 1.0 + float(index) * 1.0
    #
    #     return self.get_wind_speed_at_height(_wind_speed_ref, height)
    #     # return 1.0 + float(index) * 1.0

    def get_wave_number(self, period):
        omega = 2 * pi / period

        start_k = omega ** 2.0 / self.g
        return newton(self.dispersion, start_k, args=(omega,), tol=0.001)

    def dispersion(self, d, *args):
        k = d
        omega = args[0]

        return omega ** 2.0 - self.g * k * tanh(k * self.site_conditions.water_depth)

    def wave_limit(self, k):
        shallow_water_limit = 0.78 * self.site_conditions.water_depth
        deep_water_limit = 0.142 * 2.0 * pi / k
        return min(shallow_water_limit, deep_water_limit)

    def get_wind_speed_at_height(self, wind_speed_ref, height):
        return wind_speed_ref * (height / self.site_conditions.ref_height_wind_speed) ** self.site_conditions.alpha

    def get_Vmax_50_year(self, height):
        return self.get_wind_speed_at_height(self.site_conditions.Vmax_50_year, height)

    def get_Vred_50_year(self, height):
        return self.get_wind_speed_at_height(self.site_conditions.Vred_50_year, height)
