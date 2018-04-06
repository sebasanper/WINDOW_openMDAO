from random import random
from transform_quadrilateral import AreaMapping
from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import n_quadrilaterals, max_n_turbines
import numpy as np
from numpy import sin, cos, deg2rad

from random import random, sample
from transform_quadrilateral import AreaMapping
from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import n_quadrilaterals, separation_equation_y, max_n_turbines
import numpy as np
from numpy import sin, cos, deg2rad


class RegularLayout(ExplicitComponent):
    def setup(self):
        self.add_input("area", shape=(n_quadrilaterals, 4, 2))
        self.add_input("downwind_spacing", val=0.0)
        self.add_input("crosswind_spacing", val=0.0)
        self.add_input("odd_row_shift_spacing", val=0.0)
        self.add_input("layout_angle", val=0.0)

        self.add_output("regular_layout", shape=(max_n_turbines, 2))
        self.add_output("n_turbines_regular", val=0.0)

    def compute(self, inputs, outputs):
        area = inputs["area"]
        downwind_spacing = inputs["downwind_spacing"]
        crosswind_spacing = inputs["crosswind_spacing"]
        odd_row_shift_spacing = inputs["odd_row_shift_spacing"]
        layout_angle = inputs["layout_angle"]

        final, count = regular_layout(downwind_spacing, crosswind_spacing, odd_row_shift_spacing, area, layout_angle)
        if count < max_n_turbines:
            to_add = max_n_turbines - count
            final += [[-100.0, -100.0] for _ in range(to_add)]
        elif count > max_n_turbines:
            count = max_n_turbines
        # From the entire regular layout a chunk with size max_n_turbines is taken.
        reduced = final[:max_n_turbines]
        with open("points.dat", "r") as points:
            for line in points:
                cols = line.split()
                reduced += [[float(cols[0]), float(cols[1])]]
        with open("layout_draw.dat", "w") as out:
            for item in reduced:
                out.write("{} {}\n".format(item[0], item[1]))
        outputs["regular_layout"] = reduced
        outputs["n_turbines_regular"] = count


def centroid(areas):
    return sum([place[0] for area in areas for place in area]) / len(areas.flatten()) * 2.0, sum([place[1] for area in areas for place in area]) / len(areas.flatten()) * 2.0

def rotate(turbine1, angle, origin):

    turbine = [turbine1[0] - origin[0], turbine1[1] - origin[1]]
    rotated = [turbine[0] * (cos(angle)) - turbine[1] * sin(angle), turbine[0] * (sin(angle)) + turbine[1] * cos(angle)]
    return [rotated[0] + origin[0], rotated[1] + origin[1]]

def regular_layout(dx, dy, dh, areas, angle):
    layout_final = []
    centroid_small = centroid(areas)
    angle = deg2rad(angle)
    with open("area.dat", "w") as areaout:
        for area in areas:
            for n in range(4) + [0]:
                areaout.write("{} {}\n".format(area[n][0], area[n][1]))

    n_rows = int((max([rotate(place, angle, centroid_small)[0] for area in areas for place in area]) - min([rotate(place, angle, centroid_small)[0] for area in areas for place in area])) / dx) + 10
    n_columns = int((max([rotate(place, angle, centroid_small)[1] for area in areas for place in area]) - min([rotate(place, angle, centroid_small)[1] for area in areas for place in area])) / dy) + 10
    layout = [[[0, 0] for _ in range(n_columns)] for _ in range(n_rows)]
    layout_translated = [[[0, 0] for _ in range(n_columns)] for _ in range(n_rows)]
    layout_rotated = [[[0, 0] for _ in range(n_columns)] for _ in range(n_rows)]
    x0, y0 = min([place[0] for area in areas for place in area]), min([place[1] for area in areas for place in area])
    layout[0][0] = [x0, y0]
    last_x = layout[0][0][0] + dx * n_rows
    last_y = layout[0][0][1] + dy * n_columns
    big_area = np.array([[layout[0][0], [last_x, layout[0][0][1]], [last_x, last_y], [layout[0][0][0], last_y]]])
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

    squares = []
    for n in range(n_quadrilaterals):
        square = [[1.0 / n_quadrilaterals * n, 0.0], [n * 1.0 / n_quadrilaterals, 1.0], [(n + 1) * 1.0 / n_quadrilaterals, 1.0], [(n + 1) * 1.0 / n_quadrilaterals, 0.0]]
        squares.append(square)
    maps = [AreaMapping(areas[n], squares[n]) for n in range(n_quadrilaterals)]
    count = 0
    for i in range(n_rows):
        for j in range(n_columns):
            if separation_equation_y(layout_rotated[i][j][0]) < layout_rotated[i][j][1] or len(areas) == 1:
                mapped = maps[0].transform_to_rectangle(layout_rotated[i][j][0], layout_rotated[i][j][1])
            else:
                mapped = maps[1].transform_to_rectangle(layout_rotated[i][j][0], layout_rotated[i][j][1])

            if mapped[0] >= 0.0 - eps and mapped[0] <= 1.0 + eps and mapped[1] >= 0.0 - eps and mapped[1] <= 1.0 + eps:
                extra = 0
                layout_final.append([layout_rotated[i][j][0][0], layout_rotated[i][j][1][0]])
                count += 1
            else:
                extra = 1
    return layout_final, count


if __name__ == '__main__':
    # areas = np.array([[[- 2000.0, - 2000.0], [0.0, - 2000.0], [3000.0, - 1000.0], [- 3000.0, 500.0]], [[- 3000.0, - 4000.0], [2000, - 4000.0], [0.0, - 2000.0], [- 2000.0, - 2000.0]]])
    areas = np.array([[[- 3000.0, - 4000.0], [2000, - 4000.0], [0.0, - 2000.0], [- 2000.0, - 2000.0]]])
    regular_layout(482.0, 250.0, 0.0, areas, 0.0)
