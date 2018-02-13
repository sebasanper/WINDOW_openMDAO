from openmdao.api import ExplicitComponent, Group
from WINDOW_openMDAO.input_params import max_n_turbines
from numpy import sqrt
import numpy as np
from WINDOW_openMDAO.src.api import AbstractWakeMerge


class MergeRSS(AbstractWakeMerge):

    def merge_model(self, defs):  

        sq = defs ** 2.0
        summation = sum(sq)
        case_ans = sqrt(summation)
        return case_ans


if __name__ == '__main__':
    rss = MergeRSS()
    print rss.merge_model
