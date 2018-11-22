from __future__ import print_function
from __future__ import division
# VERTICAL HEIGHTS W.R.T. MSL
from builtins import range
from past.utils import old_div
from math import pi, atan

from scipy.optimize import brentq  # fmin_slsqp  # , fminbound, newton
# from numpy import array

from .designers import Designers


class SupportDesigners(Designers):
    platform_bladetip_clearance = 4.0
    water_bladetip_clearance = 20.0
    max_length_tower_segment = 2.4
    loadcases = [0, 1, 2]
    loadcases_wind = ["operation", "red_50_year", "max_50_year"]
    loadcases_wave = ["max_1_year", "max_50_year", "red_50_year"]
    dynamic_amplification_factor = 1.0  # Note: This factor applies to all loads, but the thrust entered by the user already includes dynamic amplification
    # fatigue_safety_factor = 1.5
    partial_safety_loads = 1.35
    partial_safety_gravity = 1.1
    partial_safety_favourable_loads = 0.9
    partial_safety_material_uls = 1.1
    bearing_resistance_factor = 0.8

    tp_base_above_seabed = 6.0
    stress_concentration_tp = 1.2

    yield_stress_steel = 200000000.0

    d_tp_minus_d_pile = 0.300
    d_over_t_guess_tower = 200.0
    d_over_t_guess_tp = 100.0

    def __init__(self, support_team):
        Designers.__init__(self, support_team)
        self.design_variables = self.support_team.design_variables.support_structure
        self.properties = self.support_team.properties.support_structure
        self.verbose = False

    def initialyse(self):

        # Set generally useful variables
        self._splash_platform_clearance = max(1.0, 0.2 * self.support_team.physical_environment.site.Hmax_50_year)
        # self._base_tp_below_splashzone = max(1.0, 0.2 * self.support_team.physical_environment.site.Hmax_50_year)
        # self.properties.base_tp = self.support_team.physical_environment.site.min_crest - self._base_tp_below_splashzone
        if self.verbose is True:
            print("water depth")
        if self.verbose is True:
            print(self.support_team.physical_environment.site.water_depth)
        self.properties.base_tp = min(
            self.tp_base_above_seabed - self.support_team.physical_environment.site.water_depth,
            self.support_team.physical_environment.site.min_crest)
        self.properties.platform_height = self.support_team.physical_environment.site.max_crest + self._splash_platform_clearance
        if self.verbose is True:
            print("platform height")
        if self.verbose is True:
            print(self.properties.platform_height)
        self.lowest_hub_height = max(self.properties.platform_height + self.platform_bladetip_clearance + self.support_team.properties.rna.rotor_radius, self.support_team.physical_environment.site.hat + self.water_bladetip_clearance + self.support_team.properties.rna.rotor_radius)
        self.shortest_tower = self.lowest_hub_height - self.properties.platform_height - self.support_team.properties.rna.yaw_to_hub_height

    def set_initial_values(self):
        # Set not-iterated design variables
        self.design_variables.tower.top_diameter = self.support_team.properties.rna.yaw_diameter
        if self.verbose is True:
            print("tower top diameter")
        if self.verbose is True:
            print(self.design_variables.tower.top_diameter)
        self.design_variables.transition_piece.length = self.properties.platform_height - self.properties.base_tp
        if self.verbose is True:
            print("transition piece length")
        if self.verbose is True:
            print(self.design_variables.transition_piece.length)
        # Set initial guesses of other design variables and update properties
        self.design_variables.tower.length = self.lowest_hub_height - self.support_team.properties.rna.yaw_to_hub_height - self.properties.platform_height

        self.set_other_variables_and_properties()

    def set_other_variables_and_properties(self):
        self.properties.hub_height = (
            self.properties.platform_height + self.design_variables.tower.length + self.support_team.properties.rna.yaw_to_hub_height)
        if self.verbose is True:
            print("tower length")
        if self.verbose is True:
            print(self.design_variables.tower.length)
        # Initialise list for segment wall thicknesses
        self.properties.nr_segments = int(
            round((old_div(self.design_variables.tower.length, self.max_length_tower_segment)) + 0.5, 0))
        self.properties.segment_length = old_div(self.design_variables.tower.length, self.properties.nr_segments)
        self.design_variables.tower.wall_thickness = list(range(self.properties.nr_segments))

        # Determine monopile diameter (from loads and resistance with fixed D:t relation)
        # self.support_team.domain_top.display.optimising = 'Tower length - Monopile diameter'
        self.design_monopile_diameter()
        # Determine penetration depth (from Blum and loads (and scour hole))
        # self.support_team.domain_top.display.optimising = 'Tower length - Monopile penetration depth'
        self.design_penetration_depth()
        # Determine monopile length (from penetration, water depth, base_tp and overlap)
        self.design_variables.monopile.length = self.design_variables.monopile.penetration_depth + self.support_team.physical_environment.site.water_depth + self.properties.base_tp + self.design_variables.transition_piece.overlap_monopile
        if self.verbose is True:
            print("monopile length")
        if self.verbose is True:
            print(self.design_variables.monopile.length)
        # Determine tower wall thickness (from loads and resistance)
        # self.support_team.domain_top.display.optimising = 'Tower length - Tower wall thicknesses'
        self.design_tower_wall_thicknesses()
        # Determine transition piece wall thickness (from loads and TBD constraint for wall thickness (?))
        # self.support_team.domain_top.display.optimising = 'Tower length - Transition piece wall thickness'
        self.design_tp_wall_thickness()
        # Determine scour protection armour grading and thickness
        # self.support_team.domain_top.display.optimising = 'Tower length - Scour protection armour'
        self.design_armour_layer()
        # Determine scour protection filter layer(s) grading(s) and thickness(es)
        # self.support_team.domain_top.display.optimising = 'Tower length - Scour protection filter'
        self.design_filter_layers()
        # Determine scour protection diameter
        if len(self.design_variables.scour_protection.armour) != 0:
            self.design_variables.scour_protection.diameter = 6.0 * self.design_variables.monopile.diameter
            self.set_scour_protection_volume()
        else:
            self.design_variables.scour_protection.diameter = 0.0
            self.support_team.properties.support_structure.scour_protection_volume = 0.0
        # Determine other design variables, such as selection of lifting equipment

        # self.support_team.domain_top.display.optimising = 'Tower length - Other parameters'
        self.properties.tower_mass = self.support_team.gravity_analysts.get_mass('tower')
        self.properties.transition_piece_mass = self.support_team.gravity_analysts.get_mass('transition piece')
        self.properties.grout_mass = self.support_team.gravity_analysts.get_mass('grout')
        self.properties.pile_mass = self.support_team.gravity_analysts.get_mass('monopile')

    def design_monopile_diameter(self):
        if self.verbose is True:
            print("monopile diameter")
        # print self.support_team.physical_environment.site.water_depth, self.fatigue_safety_factor
        monop_diam = brentq(self.stress_reserve_pile, 0.01, 100.0, xtol=0.01, full_output=True)[0]
        if self.verbose is True:
            print(monop_diam)

        if self.verbose is True:
            print("monopile wall thickness")
        if self.verbose is True:
            print(self.design_variables.monopile.wall_thickness)

        if self.verbose is True:
            print("transition piece overlap length")
        if self.verbose is True:
            print(self.design_variables.transition_piece.overlap_monopile)
    #        if result[1].converged != True:
    #            self.optimisation_succeeded = False

    def design_penetration_depth(self):
        self.support_team.geophysical_analysts.initialise_clamping_analysis()

        max_pile_penetration = 0.0
        for loadcase in self.loadcases:
            loads_with_safety = self.get_loads(loadcase, - self.support_team.physical_environment.site.water_depth)
            fx = old_div(abs(loads_with_safety[0]), (self.bearing_resistance_factor * self.fatigue_safety_factor))
            my = old_div(abs(loads_with_safety[4]), (self.bearing_resistance_factor * self.fatigue_safety_factor))

            pile_penetration = self.support_team.geophysical_analysts.get_clamping_depth(fx, my)

            if pile_penetration > max_pile_penetration:
                max_pile_penetration = pile_penetration

        self.design_variables.monopile.penetration_depth = max_pile_penetration
        if self.verbose is True:
            print("monopile penetration depth")
        if self.verbose is True:
            print(self.design_variables.monopile.penetration_depth)

    def design_tower_wall_thicknesses(self):
        for i in range(self.properties.nr_segments):
            diameter = (self.design_variables.tower.base_diameter +
                        (i * self.properties.segment_length / self.design_variables.tower.length) *
                        (self.design_variables.tower.top_diameter - self.design_variables.tower.base_diameter))
            height = self.properties.platform_height + i * self.properties.segment_length
            max_wall_thickness = 0.0
            for loadcase in self.loadcases:
                loads_with_safety = self.get_loads(loadcase, height)
                fz = abs(loads_with_safety[2])
                my = abs(loads_with_safety[4])
                l = self.properties.hub_height + self.support_team.physical_environment.site.water_depth
                minimum_thickness = self.support_team.mechanical_analysts.get_min_thickness_euler(diameter / 2.0, fz, l)
                result = brentq(self.stress_reserve_tower, minimum_thickness, 0.5 * diameter, args=(diameter, fz, my),
                                xtol=0.001, full_output=True)
                wall_thickness = result[0]
                #                if result[1].converged != True:
                #                    self.optimisation_succeeded = False

                if wall_thickness > max_wall_thickness:
                    max_wall_thickness = wall_thickness

            self.design_variables.tower.wall_thickness[i] = max_wall_thickness
        if self.verbose is True:
            print("tower wall thicknesses")
        if self.verbose is True:
            print(self.design_variables.tower.wall_thickness[0], self.design_variables.tower.wall_thickness[-1])

    def design_tp_wall_thickness(self):
        if self.verbose is True:
            print("transition piece diameter")
        if self.verbose is True:
            print(self.design_variables.transition_piece.diameter)
        diameter = self.design_variables.transition_piece.diameter
        height = self.properties.base_tp + self.design_variables.transition_piece.overlap_monopile
        max_wall_thickness = 0.0
        for loadcase in self.loadcases:
            loads_with_safety = self.get_loads(loadcase, height)
            fz = abs(loads_with_safety[2])
            my = self.stress_concentration_tp * abs(loads_with_safety[4])
            l = self.properties.hub_height + self.support_team.physical_environment.site.water_depth
            minimum_thickness = self.support_team.mechanical_analysts.get_min_thickness_euler(diameter / 2.0, fz, l)
            result = brentq(self.stress_reserve_tower, minimum_thickness, 0.5 * diameter, args=(diameter, fz, my),
                            xtol=0.001, full_output=True)
            wall_thickness = result[0]
            #            if result[1].converged != True:
            #                self.optimisation_succeeded = False

            if wall_thickness > max_wall_thickness:
                max_wall_thickness = wall_thickness

            self.design_variables.transition_piece.wall_thickness = max_wall_thickness
        pass
        if self.verbose is True:
            print("transition piece wall thickness")
        if self.verbose is True:
            print(self.design_variables.transition_piece.wall_thickness)

    def stress_reserve_pile(self, d):
        self.design_variables.monopile.diameter = d
        # Set transition piece and tower base dimensions
        self.design_variables.transition_piece.diameter = self.design_variables.monopile.diameter + self.d_tp_minus_d_pile
        self.design_variables.tower.base_diameter = self.design_variables.transition_piece.diameter
        self.design_variables.monopile.wall_thickness = 0.00635 + (self.design_variables.monopile.diameter / 100.0)
        # Set transition piece overlap for estimates of gravity loading
        self.design_variables.transition_piece.overlap_monopile = 1.44 * self.design_variables.monopile.diameter

        # Guess wall thicknesses for estimates of gravity loading (for tower diameter / 200, for transition piece diameter / 100, for monopile according to API)
        d_base = self.design_variables.tower.base_diameter
        d_top = self.design_variables.tower.top_diameter
        for i in range(self.properties.nr_segments):
            self.design_variables.tower.wall_thickness[i] = old_div((d_base + i * self.properties.segment_length * (
                d_top - d_base) / self.design_variables.tower.length), self.d_over_t_guess_tower)
        self.design_variables.transition_piece.wall_thickness = old_div(self.design_variables.transition_piece.diameter, self.d_over_t_guess_tp)

        max_stress_factor = -1.0
        d_outer = self.design_variables.monopile.diameter
        d_inner = d_outer - 2.0 * self.design_variables.monopile.wall_thickness
        # loads_with_safety = range(6)
        for loadcase in self.loadcases:
            loads_with_safety = self.get_loads(loadcase, - self.support_team.physical_environment.site.water_depth)

            [stress, critical_stress] = self.support_team.mechanical_analysts.get_stress_pile(d_outer, d_inner,
                                                                                              loads_with_safety[2],
                                                                                              loads_with_safety[4])

            stress_factor = (old_div(stress, (old_div(critical_stress, self.partial_safety_material_uls)))) - 1.0
            if stress_factor > max_stress_factor:
                max_stress_factor = stress_factor

        return max_stress_factor

    def stress_reserve_tower(self, d, *args):
        t = d
        radius = args[0] / 2.0
        fz = args[1]
        my = args[2]
        l = self.properties.hub_height + self.support_team.physical_environment.site.water_depth

        [stress, critical_stress] = self.support_team.mechanical_analysts.get_stress_tower(t, radius, fz, my, l)
        stress_factor = (old_div(stress, (old_div(critical_stress, self.partial_safety_material_uls)))) - 1.0

        return stress_factor

    def get_loads(self, loadcase, height):
        wind_speed_height = self.properties.hub_height
        alpha = self.support_team.physical_environment.site.alpha
        if self.loadcases_wind[loadcase] == "operation":
            wind_speed = self.support_team.properties.rna.wind_speed_at_max_thrust
        elif self.loadcases_wind[loadcase] == "red_50_year":
            wind_speed = self.support_team.site_conditions_analysts.get_Vred_50_year(self.properties.hub_height)
        elif self.loadcases_wind[loadcase] == "max_50_year":
            wind_speed = self.support_team.site_conditions_analysts.get_Vmax_50_year(self.properties.hub_height)

        if self.loadcases_wave[loadcase] == "max_1_year":
            wave_height = self.support_team.physical_environment.site.Hmax_1_year
            wave_number = self.support_team.physical_environment.site.kmax_1_year
        elif self.loadcases_wave[loadcase] == "red_50_year":
            wave_height = self.support_team.physical_environment.site.Hred_50_year
            wave_number = self.support_team.physical_environment.site.kred_50_year
        elif self.loadcases_wave[loadcase] == "max_50_year":
            wave_height = self.support_team.physical_environment.site.Hmax_50_year
            wave_number = self.support_team.physical_environment.site.kmax_50_year

        loads_rna = self.support_team.rna_analysts.get_loads(self.loadcases_wind[loadcase], wind_speed, height)
        loads_aero = self.support_team.aerodynamic_analysts.get_loads(wind_speed, wind_speed_height, alpha, height)
        loads_hydro = self.support_team.hydrodynamic_analysts.get_loads(wave_height, wave_number, height)
        loads_gravity = self.support_team.gravity_analysts.get_loads(height)

        loads_safety = list(range(6))
        for i in range(6):
            loads_safety[i] = self.partial_safety_loads * (loads_rna[i] + loads_aero[i] + loads_hydro[i])
            if i == 4 and loads_gravity[i] < 0.0:
                loads_safety[i] = (self.dynamic_amplification_factor * self.fatigue_safety_factor *
                                   (loads_safety[i] + self.partial_safety_favourable_loads * loads_gravity[i]))
            else:
                loads_safety[i] = (self.dynamic_amplification_factor * self.fatigue_safety_factor *
                                   (loads_safety[i] + self.partial_safety_gravity * loads_gravity[i]))

        return loads_safety

    def design_armour_layer(self):
        u_w = self.support_team.physical_environment.site.Uw_50_year
        t_w = self.support_team.physical_environment.site.Tpeak_50_year
        KC = u_w * t_w / self.design_variables.monopile.diameter
        u_w *= 1.5 + old_div(atan(1.0 * (KC - 6.0) - 1.0), pi)
        u_c = 1.5 * self.support_team.physical_environment.site.current_depth_averaged_50_year
        wave_current_angle = self.support_team.physical_environment.site.angle_wave_current_50_year_rad

        result = brentq(self.friction_reserve_rock, 1e-9, self.support_team.physical_environment.site.water_depth,
                        xtol=50e-6, full_output=True, args=(u_c, u_w, t_w, wave_current_angle))
        d50 = result[0]
        #        if result[1].converged != True:
        #            self.optimisation_succeeded = False

        if d50 > self.support_team.physical_environment.site.d50_soil:
            self.design_variables.scour_protection.armour = [0.8 * d50, d50, 1.2 * d50, max(0.3, 2.5 * d50),
                                                             max(0.3, 1.7 * d50)]
        else:
            self.design_variables.scour_protection.armour = []

    def friction_reserve_rock(self, d, *args):
        d50 = d
        u_c = args[0]
        u_w = args[1]
        t_w = args[2]
        wave_current_angle = args[3]
        critical_friction = self.support_team.rock_analysts.get_critical_friction(d50)
        characteristic_friction = self.support_team.rock_analysts.get_characteristic_friction(d50, u_c, u_w, t_w,
                                                                                              wave_current_angle)

        return old_div((critical_friction - characteristic_friction), critical_friction)

    def design_filter_layers(self):
        self.design_variables.scour_protection.filter = []

        if len(self.design_variables.scour_protection.armour) != 0:
            d15f = self.design_variables.scour_protection.armour[0]

            _filter_needed = True
            while _filter_needed:
                d85b = d15f / 4.5

                if d85b > self.support_team.physical_environment.site.d90_soil:
                    self.design_variables.scour_protection.filter.append(
                        [0.4 * d85b, 0.7 * d85b, d85b, max(0.3, 1.7 * 0.7 * d85b)])
                    d15f = 0.4 * d85b
                else:
                    _filter_needed = False

    def set_scour_protection_volume(self):

        extra_thickness_near_pile = self.design_variables.scour_protection.armour[3]
        total_thickness = self.design_variables.scour_protection.armour[4]
        for layer in self.design_variables.scour_protection.filter:
            total_thickness += layer[3]

        self.support_team.properties.support_structure.scour_protection_volume = ((1.0 / 4.0) * pi * (self.design_variables.scour_protection.diameter ** 2 * total_thickness + (3.0 * self.design_variables.monopile.diameter) ** 2 * extra_thickness_near_pile - self.design_variables.monopile.diameter ** 2 * (total_thickness + extra_thickness_near_pile)))
