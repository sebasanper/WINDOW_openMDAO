from Input.site_parameters import n_quadrilaterals, areas, separation_equation_y
from transform_quadrilateral_iea import AreaMapping
from random import uniform
import numpy as np

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
    layout = np.array([create_random() for _ in range(n_turbs)])
    return layout
