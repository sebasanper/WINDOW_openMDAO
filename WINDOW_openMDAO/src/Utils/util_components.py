from __future__ import print_function
from __future__ import absolute_import
from builtins import range
from openmdao.api import ExplicitComponent
from WINDOW_openMDAO.input_params import max_n_turbines, n_quadrilaterals, areas, separation_equation_y
from .transform_quadrilateral import AreaMapping
from random import uniform
import numpy as np


class NumberLayout(ExplicitComponent):
    def __init__(self, n):
      super(NumberLayout, self).__init__()
      self.n = n

    def setup(self):
        self.add_input("orig_layout", shape=(self.n, 2))
        self.add_output("number_layout", shape=(self.n, 3))

    def compute(self, inputs, outputs):
        orig_layout = inputs["orig_layout"]
        outputs["number_layout"] = [[n, orig_layout[n][0], orig_layout[n][1]] for n in range(len(orig_layout))]


def create_random_layout(n_turbs):
    squares = []
    for n in range(n_quadrilaterals):
       square = [[1.0 / n_quadrilaterals * n, 0.0], [n * 1.0 / n_quadrilaterals, 1.0], [(n + 1) * 1.0 / n_quadrilaterals, 1.0], [(n + 1) * 1.0 / n_quadrilaterals, 0.0]]
       squares.append(square)
    borssele_mapping1 = AreaMapping(areas[0], squares[0])
    borssele_mapping2 = AreaMapping(areas[1], squares[1])
    def create_random():
       xt, yt = 2.0, 2.0
       while (xt < 0.0 or xt > 1.0) or (yt < 0.0 or yt > 1.0):
          xb, yb = uniform(min(min([item[0] for item in areas[0]]), min([item[0] for item in areas[1]])), max(max([item[0] for item in areas[0]]), max([item[0] for item in areas[1]]))), uniform(min(min([item[1] for item in areas[0]]), min([item[1] for item in areas[1]])), max(max([item[1] for item in areas[0]]), max([item[1] for item in areas[1]])))
          if yb > separation_equation_y(xb):
            xt, yt = borssele_mapping1.transform_to_rectangle(xb, yb)
          else:
            xt, yt = borssele_mapping2.transform_to_rectangle(xb, yb)
       return [xb, yb]
    print(n)
    layout = np.array([create_random() for _ in range(n_turbs)])
    return layout
