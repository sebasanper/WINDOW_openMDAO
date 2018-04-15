from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import max_n_turbines, n_quadrilaterals, separation_equation_y
from transform_quadrilateral import AreaMapping
from numpy import sqrt


class MinDistance(ExplicitComponent):
    def setup(self):
        self.add_input("orig_layout", shape=(max_n_turbines, 2))
        self.add_input("turbine_radius", val=0.0)
        self.add_output("n_constraint_violations", val=0)
        self.add_output("magnitude_violations", val=0)

        #self.declare_partials(of='magnitude_violations', wrt=['turbine_radius', 'orig_layout'], method='fd')

    def compute(self, inputs, outputs):
        layout = inputs["orig_layout"]
        # print layout
        radius = inputs["turbine_radius"]
        count = 0
        magnitude = 0.0
        for t1 in range(len(layout)):
            for t2 in range(t1 + 1, len(layout)):
                dist = self.distance(layout[t1], layout[t2])
                viol = dist <= 2.0 * radius
                if viol > 0:
                    count += viol
                    magnitude += self.distance(layout[t1], layout[t2])
        outputs["n_constraint_violations"] = count
        outputs["magnitude_violations"] = magnitude


    def distance(self, t1, t2):
        return sqrt((t1[0] - t2[0]) ** 2.0 + (t1[1] - t2[1]) ** 2.0)


class WithinBoundaries(ExplicitComponent):
    def setup(self):
        self.add_input("layout", shape=(max_n_turbines, 2))
        self.add_input("areas", shape=(n_quadrilaterals, 4, 2))

        self.add_output("n_constraint_violations", val=0)
        self.add_output("magnitude_violations", val=0.0)
        
        #self.declare_partials(of='magnitude_violations', wrt=['areas', 'layout'], method='fd')

    def compute(self, inputs, outputs):
        layout = inputs["layout"]
        squares = []
        for n in range(n_quadrilaterals):
            square = [[1.0 / n_quadrilaterals * n, 0.0], [n * 1.0 / n_quadrilaterals, 1.0], [(n + 1) * 1.0 / n_quadrilaterals, 1.0], [(n + 1) * 1.0 / n_quadrilaterals, 0.0]]
            squares.append(square)
        area = inputs["areas"]
        maps = [AreaMapping(area[n], squares[n]) for n in range(n_quadrilaterals)]
        count = 0
        magnitude = 0.0
        for t in layout:
            if t[1] > separation_equation_y(t[0]):
                mapped = maps[0].transform_to_rectangle(t[0], t[1])
            else:
                mapped = maps[1].transform_to_rectangle(t[0], t[1])
            c, m = self.inarea(mapped)
            count += c
            magnitude += m
        outputs["n_constraint_violations"] = count
        outputs["magnitude_violations"] = magnitude


    def inarea(self, mapped_turbine):
        count = 0
        magnitude = 0.0
        if mapped_turbine[0] < 0:
            magnitude += - mapped_turbine[0]
            count = 1
        elif mapped_turbine[0] > 1.0:
            magnitude += mapped_turbine[0] - 1.0
            count = 1
        if mapped_turbine[1] < 0:
            magnitude += - mapped_turbine[1]
            count = 1
        elif mapped_turbine[1] > 1.0:
            magnitude += mapped_turbine[1] - 1.0
            count = 1
        return count, magnitude
