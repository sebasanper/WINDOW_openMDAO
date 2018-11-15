from __future__ import division
from past.utils import old_div
def management_costs(total_investment):
    management_percentage = 3.0  # [%]
    return total_investment * (old_div(management_percentage, 100.0))
