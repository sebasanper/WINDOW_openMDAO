from openmdao.api import ExplicitComponent
from input_params import max_n_turbines, n_quatrilaterials, separation_value_y
from transform_quadrilateral import AreaMapping


class MinDistance(ExplicitComponent):
    def setup(self):
        self.add_input("orig_layout", shape=(max_n_turbines, 2))
        self.add_input("turbine_radius", val=0.0)
        self.add_output("n_constraint_violations", val=0)
        self.add_output("magnitude_violations", val=0.0)


    def compute(self, inputs, outputs):
        layout = inputs["orig_layout"]
        radius = inputs["turbine_radius"]
        count = 0
        for t1 in layout:
            for t2 in layout:
                count += distance(t1, t2) <= 2.0 * radius
        outputs["n_constraint_violations"] = count


    def distance(self, t1, t2):
        return sqrt((t1[0] - t2[0]) ** 2.0 + (t1[1] - t2[1]) ** 2.0)


class WithinBoundaries(ExplicitComponent):
    def setup(self):
        self.add_input("layout", shape=(max_n_turbines, 2))
        self.add_input("area", shape=(n_quatrilaterials, 4, 2))

        self.add_output("n_constraint_violations", val=0)
        self.add_output("magnitude_violations", val=0.0)

    def compute(self, inputs. outputs):
        square1 = [[0.0, 0.0], [1.0, 0.0], [0.0, 0.5], [1.0, 0.5]]
        square2 = [[0.0, 0.5], [1.0, 0.5], [0.0, 1.0], [1.0, 1.0]]
        area1 = inputs["area"][0]
        area2 = inputs["area"][1]
        map1 = AreaMapping(area1, square)
        map2 = AreaMapping(area2, square)

    def inarea(self, turbine, area):
        X = separation_value_y
        if turbine[1] <= X