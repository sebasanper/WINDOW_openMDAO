from numpy import sqrt

max_n_turbines = 9
turbine_radius = 40.0
max_n_substations = 2
turbine_rated_power = 2000000.0
turbine_voltage = 33000.0
turbine_rated_current = turbine_rated_power / (sqrt(3.0) * turbine_voltage)  # A = Power / sqrt(3) / Voltage. 3 phase.

cable_types = [[95, 300, 206], [120, 340, 221], [150, 375, 236], [185, 420, 256], [240, 480, 287], [300, 530, 316], [400, 590, 356], [500, 655, 406], [630, 715, 459], [800, 775, 521], [1000, 825, 579]]
