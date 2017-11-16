from random import random
from math import sin, cos, radians
from transform_quadrilateral import AreaMapping
from openmdao.api import ExplicitComponent
from input_params import n_quadrilaterals, max_n_turbines


class RegularLayout(ExplicitComponent):
    def setup(self):
        self.add_input("area", shape=(n_quadrilaterals, 4, 2))
        self.add_input("downwind_spacing", val=0.0)
        self.add_input("crosswind_spacing", val=0.0)
        self.add_input("odd_row_shift_spacing", val=0.0)
        self.add_input("layout_angle", val=0.0)

        self.add_output("regular_layout", shape=(max_n_turbines, 2))
        self.add_output("n_turbines_regular", val=0)

    def compute(self, inputs, outputs):
        area = inputs["area"]
        downwind_spacing = inputs["downwind_spacing"]
        crosswind_spacing = inputs["crosswind_spacing"]
        odd_row_shift_spacing = inputs["odd_row_shift_spacing"]
        layout_angle = inputs["layout_angle"]

        outputs["regular_layout"] = regular_layout(downwind_spacing, crosswind_spacing, odd_row_shift_spacing, area, layout_angle)
        outputs["n_turbines_regular"] = len(outputs["regular_layout"])


def centroid(area):
    return sum([place[0] for place in area]) / len(area), sum([place[1] for place in area]) / len(area)

def rotate(turbine1, angle, origin):

    turbine = [turbine1[0] - origin[0], turbine1[1] - origin[1]]
    rotated = [turbine[0] * (cos(angle)) - turbine[1] * sin(angle), turbine[0] * (sin(angle)) + turbine[1] * cos(angle)]
    return [rotated[0] + origin[0], rotated[1] + origin[1]]

def regular_layout(dx, dy, dh, area, angle):
    centroid_small = centroid(area)
    angle = radians(angle)
    with open("area.dat", "w") as areaout:
        for n in range(len(area)) + [0]:
            areaout.write("{} {}\n".format(area[n][0], area[n][1]))

    n_rows = int((max([rotate(place, angle, centroid_small)[0] for place in area]) - min([rotate(place, angle, centroid_small)[0] for place in area])) / dx) + 10
    n_columns = int((max([rotate(place, angle, centroid_small)[1] for place in area]) - min([rotate(place, angle, centroid_small)[1] for place in area])) / dy) + 10
    layout = [[[0, 0] for _ in range(n_columns)] for _ in range(n_rows)]
    layout_translated = [[[0, 0] for _ in range(n_columns)] for _ in range(n_rows)]
    layout_rotated = [[[0, 0] for _ in range(n_columns)] for _ in range(n_rows)]
    x0, y0 = min([place[0] for place in area]), min([place[1] for place in area])
    layout[0][0] = [x0, y0]
    last_x = layout[0][0][0] + dx * n_rows
    last_y = layout[0][0][1] + dy * n_columns
    big_area = [layout[0][0], [last_x, layout[0][0][1]], [last_x, last_y], [layout[0][0][0], last_y]]
    centroid_big = centroid(big_area)
    for j in range(1, n_columns):
        if j % 2 == 0:
            layout[0][j] = [layout[0][j - 1][0] - dh, layout[0][j - 1][1] + dy]

        else:
            layout[0][j] = [layout[0][j - 1][0] + dh, layout[0][j - 1][1] + dy]

    for i in range(1, n_rows):
        layout[i][0] = [layout[i - 1][0][0] + dx, layout[i - 1][0][1]]

        for j in range(1, n_columns):
            if j % 2 == 0:
                layout[i][j] = [layout[i][j - 1][0] - dh, layout[i][j - 1][1] + dy]

            else:
                layout[i][j] = [layout[i][j - 1][0] + dh, layout[i][j - 1][1] + dy]

    for i in range(n_rows):
        for j in range(n_columns):
            layout_translated[i][j] = [layout[i][j][0] - (centroid_big[0] - centroid_small[0]), layout[i][j][1] - (centroid_big[1] - centroid_small[1])]
            layout_rotated[i][j] = rotate(layout_translated[i][j], angle, centroid_small)
    eps = 1e-8
    with open("regular_3x5_rotated2_dh0.dat", "w") as regular_file:

        desired_rectangle_coordinates = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]
        mapping1 = AreaMapping(area, desired_rectangle_coordinates)

        for i in range(n_rows):
            for j in range(n_columns):

                mapped = mapping1.transform_to_rectangle(layout_rotated[i][j][0], layout_rotated[i][j][1])

                if mapped[0] >= 0.0 - eps and mapped[0] <= 1.0 + eps and mapped[1] >= 0.0 - eps and mapped[1] <= 1.0 + eps:
                    extra = 0
                else:
                    extra = 1
                regular_file.write("{} {} {}\n".format(layout_rotated[i][j][0], layout_rotated[i][j][1], extra))
    return layout


if __name__ == '__main__':
    area = [[- 2000.0, - 2000.0], [0.0, - 2000.0], [3000.0, - 1000.0], [- 3000.0, 500.0]]
    regular_layout(482.0, 250.0, 241.0, area, 150.0)
