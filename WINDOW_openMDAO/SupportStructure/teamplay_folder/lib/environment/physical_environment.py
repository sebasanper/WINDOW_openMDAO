from WINDOW_openMDAO.input_params import ref_height_wind_speed, alpha, hat, lat, storm_surge_pos, storm_surge_neg, Hs_50_year, Hs_1_year, current_depth_averaged_50_year, angle_wave_current_50_year, water_density, d50_soil, d90_soil, friction_angle, submerged_unit_weight

# TOTAL PHYSICAL ENVIRONMENT **************************************************


class PhysicalEnvironment:
    def __init__(self):
        self.site = Site()


# SITE **************************************************

class Site:
    def __init__(self):
        pass

    #  TODO: Test the program with extreme conditions, such as zero wave height or zero current velocity

    # # DATA FROM DATABASE **************************************************
    # scale_factor = scale_factor  # [m/s] Horns Rev website: Data fitted, resulting in average wind speed of 9.6, which is close to given value of 9.7
    # shape_factor = shape_factor  # [-] Horns Rev website: Data fitted, resulting in average wind speed of 9.6, which is close to given value of 9.7
    ref_height_wind_speed = ref_height_wind_speed
    alpha = alpha  # Approximate mean value of fits to data in ECN report and paper of Tambke (EWEC 2004)
    # water_depth = 13.5  # 6 - 14 m according to 'Facts', 6.5 - 13.5 according to turbine and support structure dimensions
    hat = hat  # Horns Rev website: Tides are approximately 1.2 m; Paper ICCE: appr. 1.5 m - A little more than half of this is taken for 'extrapolation'
    lat = lat  # Horns Rev website: Tides are approximately 1.2 m; Paper ICCE: appr. 1.5 m - A little more than half of this is taken for 'extrapolation'
    storm_surge_pos = storm_surge_pos  # Paper ICCE
    storm_surge_neg = storm_surge_neg  # Guess
    Hs_50_year = Hs_50_year  # Horns Rev website: Highest value in graph of Hm0 is 4.3. Somewhat higher value taken for 'extrapolation' (note: graph is for 1 hour values) - Support structure design tool description derives Hs_1_year = 0.64 * Hs_50_year
    Hs_1_year = Hs_1_year  # Horns Rev website: waves of more than 6 m height reached every year. Divided by 1.86 to estimate significant wave height
    current_depth_averaged_50_year = current_depth_averaged_50_year  # [m/s] Horns Rev website: Currents may reach 0.8 m/s during storms (doesn't mention return period and whether this is depth averaged)
    angle_wave_current_50_year = angle_wave_current_50_year  # [degrees] (Arbitrary default)
    # water_temperature = water_temperature  # [degrees Celsius] 'Temperature-report' gives 17 degrees surface temp in August and 'Temperature variation-report' gives variation of 2 degrees (highest temperature, so: August, is the worst case)
    water_density = water_density  # [kg/m^3] Generic value
    d50_soil = d50_soil  # [m]  Values given as 'range' in baggrund8 IEA report and confirmed by figure 2.2. in fish IEA report
    d90_soil = d90_soil  # [m]  Values given as 'range' in baggrund8 IEA report and confirmed by figure 2.2. in fish IEA report
    friction_angle = friction_angle  # [degrees] Depth averaged friction angle from 'friction angle-report'
    submerged_unit_weight = submerged_unit_weight  # [N/m^3] From 'friction angle-report', lighter layer ignored, because it is at great depth.
    # ref_storm_fraction = ref_storm_fraction  # [-] (Storm fraction of time for Hs_ref) Slides of O&M lecture Gerard ('Accessibility of site (Vessel)') - Spare part optimisation report says vessels can sail out about 40% of the time
    # ref_storm_scale = ref_storm_scale  # [h] (Storm scale factor for Hs_ref - Lightning study ECN part 1 - IJmuiden minutiestortplaats) No data for Horns Rev found (not searched explicitly)
    # ref_storm_shape = ref_storm_shape  # [-] (Storm shape factor for Hs_ref - Lightning study ECN part 1 - IJmuiden minutiestortplaats) No data for Horns Rev found (not searched explicitly)
    # ref_hs_accessibility = ref_hs_accessibility  # [m] (Significant wave height for which the previous reference values apply) - Slides of O&M lecture Gerard ('Access systems considered')

    # PROCESSED DATA **************************************************
    Hmax_50_year = 0.0  # [m]
    Tmax_50_year = 0.0  # [s]
    Tpeak_50_year = 0.0  # [s]
    kmax_50_year = 0.0  # [m^-1]
    Uw_50_year = 0.0  # [m/s]
    Hred_50_year = 0.0  # [m]
    Tred_50_year = 0.0  # [s]
    kred_50_year = 0.0  # [m^-1]
    Hmax_1_year = 0.0  # [m]
    Tmax_1_year = 0.0  # [s]
    kmax_1_year = 0.0  # [m^-1]
    max_crest = 0.0  # [m]
    min_crest = 0.0  # [m]
    Vaverage = 0.0  # [m/s]
    Vreference = 0.0  # [m/s]
    Vmax_50_year = 0.0  # [m/s]
    Vred_50_year = 0.0  # [m/s]
    angle_wave_current_50_year_rad = 0.0  # [rad]

# def __init__(self):
#        self.wind_rose_probability = [] # [-]
#        self.wind_speed_probability = [] # [-]
