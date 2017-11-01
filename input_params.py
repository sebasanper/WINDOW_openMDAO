from numpy import sqrt

max_n_turbines = max_n_branches = 61
turbine_radius = 40.0
max_n_substations = 2
max_n_turbines_p_branch = 61

turbine_rated_power = 3600000.0
turbine_voltage = 33000.0
turbine_rated_current = sqrt(3.0) * turbine_rated_power / (turbine_voltage)  # A = Power * sqrt(3) / Voltage. 3 phase current per line.

cable_types = [[95, 300, 206], [120, 340, 221], [150, 375, 236], [185, 420, 256], [240, 480, 287], [300, 530, 316], [400, 590, 356], [500, 655, 406], [630, 715, 459], [800, 775, 521], [1000, 825, 579]]
