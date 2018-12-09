from farm_energy.wake_model_mean_new.aero_power_ct_models.aero_models import AeroLookup
from WINDOW_openMDAO.input_params import TI_ambient


class Workflow:
    def __init__(self, inflow_model, windrose_file, wake_turbulence_model, thrust_coefficient_model, thrust_lookup_file,
                 wake_mean_model, wake_merging_model, power_model, power_lookup_file, \
                 cutin, cutout, rated_wind, rotor_radius, rated_power):

        self.print_output = False

        self.inflow_model = inflow_model
        self.wake_turbulence_model = wake_turbulence_model
        self.thrust_coefficient_model = thrust_coefficient_model
        self.wake_mean_model = wake_mean_model
        self.wake_merging_model = wake_merging_model
        self.power_model = power_model
        self.windrose = self.inflow_model(windrose_file, cutin, cutout)
        self.thrust_lookup_file = thrust_lookup_file
        self.power_lookup_file = power_lookup_file
        self.cutin = cutin
        self.cutout = cutout
        self.rated_wind = rated_wind
        self.rotor_radius= rotor_radius
        self.rated_power = rated_power
        self.ctx = []
        self.cty = []
        self.px = []
        self.py = []

        with open(self.thrust_lookup_file, "r") as data:
            for line in data:
                col = line.split()
                self.ctx.append(float(col[0]))
                self.cty.append(float(col[1]))
        with open(self.power_lookup_file, "r") as data:
            for line in data:
                col = line.split()
                self.px.append(float(col[0]))
                self.py.append(float(col[1]))

        self.table_power = AeroLookup(self.px, self.py)
        self.ct_table = AeroLookup(self.ctx, self.cty)

    def connect(self, turbine_coordinates):
        layout = []
        for t in turbine_coordinates:
            if t[0] >= 0.0 and t[1] >= 0.0:
                layout.append([t[0], t[1]])
        self.number_turbines = len(layout)
        from farm_energy.wake_model_mean_new.wake_1angle import energy_one_angle
        from farm_energy.wake_model_mean_new.wake_1angle_turbulence import max_turbulence_one_angle
        from farm_energy.wake_model_mean_new.downstream_effects import JensenEffects as Jensen
        #from WINDOW_openMDAO.input_params import cutin_wind_speed, cutout_wind_speed

        if self.print_output is True: print("=== PREPARING WIND CONDITIONS ===")

        self.wind_directions, self.direction_probabilities = self.windrose.adapt_directions()

        self.windrose.cutin = self.cutin
        self.windrose.cutout = self.cutout
        self.wind_speeds, self.wind_speeds_probabilities = self.windrose.speed_probabilities()

        self.freestream_turbulence = [TI_ambient for _ in range(len(self.wind_speeds[0]))]

        self.energies_per_angle = []
        self.turbulences_per_angle = []
        self.cable_efficiencies_per_angle = []
        self.array_efficiencies = []

        self.max_turbulence_per_turbine = [0.0 for _ in range(len(turbine_coordinates))]

        if self.print_output is True: print("=== CALCULATING ENERGY, TURBULENCE PER WIND DIRECTION ===")
        for i in range(len(self.wind_directions)):
            self.aero_energy_one_angle, self.powers_one_angle, deficits = energy_one_angle(turbine_coordinates,
                                                                                           self.wind_speeds[i],
                                                                                           self.wind_speeds_probabilities[
                                                                                               i],
                                                                                           self.wind_directions[i],
                                                                                           self.freestream_turbulence,
                                                                                           self.wake_mean_model,
                                                                                           self.power_model,
                                                                                           self.table_power,
                                                                                           self.thrust_coefficient_model,
                                                                                           self.ct_table,
                                                                                           self.wake_merging_model, \
                                                                                           self.cutin, self.cutout, self.rated_wind, self.rotor_radius, self.rated_power)
            self.turbulences = max_turbulence_one_angle(deficits, turbine_coordinates, self.wind_speeds[i],
                                                        self.wind_directions[i], self.freestream_turbulence, Jensen,
                                                        self.thrust_coefficient_model, self.ct_table,
                                                        self.wake_turbulence_model, self.rotor_radius)
            self.energy_one_angle_weighted = self.aero_energy_one_angle * self.direction_probabilities[i] / 100.0
            self.energies_per_angle.append(self.energy_one_angle_weighted)
            self.array_efficiency = self.aero_energy_one_angle / (
                float(self.number_turbines) * max(self.powers_one_angle) * 8760.0)
            self.array_efficiencies_weighted = self.array_efficiency * self.direction_probabilities[i] / 100.0

            self.array_efficiencies.append(self.array_efficiencies_weighted)
            self.turbulences_per_angle.append(self.turbulences)

            for j in range(len(turbine_coordinates)):
                if self.turbulences[j] > self.max_turbulence_per_turbine[j]:
                    self.max_turbulence_per_turbine[j] = self.turbulences[j]

        if self.print_output is True: print(str(self.array_efficiency * 100.0) + " %\n")
        if self.print_output is True: print(" --- Farm annual energy without losses---")
        self.array_efficiency = sum(self.array_efficiencies)
        self.farm_annual_energy = sum(self.energies_per_angle)

        if self.print_output is True: print(str(self.farm_annual_energy / 1000000.0) + " MWh\n")
        if self.print_output is True: print(" --- Maximum wind turbulence intensity ---")

        self.turbulence = self.max_turbulence_per_turbine

        if self.print_output is True: print(
            str([self.turbulence[l] * 100.0 for l in range(len(self.turbulence))]) + " %\n")

        return self.farm_annual_energy, self.turbulence, self.array_efficiency

    def run(self, layout_coordinates):

        from farm_energy.wake_model_mean_new.aero_power_ct_models.aero_models import power, thrust_coefficient
#         from farm_energy.wake_model_mean_new.ainslie1d import ainslie
#         from farm_energy.wake_model_mean_new.ainslie2d import ainslie_full
        from farm_energy.wake_model_mean_new.jensen import determine_if_in_wake, wake_radius, wake_deficit
#         from farm_energy.wake_model_mean_new.larsen import deff, wake_deficit_larsen, wake_radius, x0, rnb, r95, c1, \
#             determine_if_in_wake_larsen, wake_speed
        from farm_energy.wake_model_mean_new.wake_turbulence_models import frandsen2, Quarton, danish_recommendation, \
            frandsen, larsen_turbulence

        self.coordinates = [[i, layout_coordinates[i][0], layout_coordinates[i][1]] for i in
                            range(len(layout_coordinates))]
        answer = self.connect(self.coordinates)
        # self.power_calls = power2.count()
        # self.thrust_calls = thrust_coefficient2.count()
        # power.reset()
        # thrust_coefficient.reset()
        # # ainslie.reset()
        # # ainslie_full.reset()
        # determine_if_in_wake.reset()
        # determine_if_in_wake_larsen.reset()
        # wake_radius.reset()
        # wake_deficit.reset()
        # frandsen2.reset()
        # Quarton.reset()
        # danish_recommendation.reset()
        # larsen_turbulence.reset()
        # frandsen.reset()
        return answer
