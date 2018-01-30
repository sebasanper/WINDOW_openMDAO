from utils_iea import create_random_layout

central_platform = [0, 498000.0, 5731000.0]
number_turbines_per_cable = [2, 4, 7]
Crossing_penalty = 0
Transmission = [[central_platform[i],[463000,5918000]] for i in range(len(central_platform))]
transm_electrical_efficiency = 0.95
coll_electrical_efficiency = 0.99

distance_to_grid = 60000.0  # [m]
distance_to_harbour = 40000.0  # [m]
onshore_transport_distance = 100000.0  # [m]
frequency = 50  # [Hz]
transmission_voltage = 220000.0  # [V]
grid_coupling_point_voltage = 169000.0  # [V]

max_n_turbines = 9

max_n_substations = 1
max_n_branches = max_n_turbines_p_branch = max_n_turbines
cable_types = [[95, 300, 206], [120, 340, 221], [150, 375, 236], [185, 420, 256], [240, 480, 287], [300, 530, 316], [400, 590, 356], [500, 655, 406], [630, 715, 459], [800, 775, 521], [1000, 825, 579]]  # List of cable types: [Cross section [mm^2], Capacity [A], Cost [EUR/m]] in increasing order (maximum 3 cable types)

# For irregular layouts.
# layout = create_random_layout(74)
layout = [[0.0, 0.0], [882.0, 0.0], [1764.0, 0.0], [0.0, 882.0], [882.0, 882.0], [1764.0, 882.0], [0.0, 1764.0], [882.0, 1764.0], [1764.0, 1764.0]]
n_turbines = len(layout)

# For regular layouts use the parameters below.
downwind_spacing = 2100.0  # [m]
crosswind_spacing = 800.0  # [m]
odd_row_shift_spacing = 0.0  # [m] How many meters to shift every other row in the crosswind direction.
layout_angle = 0.0  # [m] Rotation angle of the entire layout.
