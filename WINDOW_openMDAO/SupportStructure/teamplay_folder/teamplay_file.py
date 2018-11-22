from __future__ import absolute_import
from .lib.designers_support.dimension_team_support import DimensionTeamSupport
from .lib.system.properties import RNA
from .lib.environment.physical_environment import Site
from .currency import Cost1


def teamplay(TI, depth):
    dimension_team_support = DimensionTeamSupport()
    dimension_team_support.fsf = TI + 1.4 # 1.4 safety factor to account for wave-induced fatigue and the rest is wind-induced.
    # dimension_team_support.fsf = 1.5
    rna = RNA()
    site_data = Site()
    site_data.water_depth = depth

    # print site_data.water_depth
    dimension_team_support.run(rna, site_data)

    boat_landing_cost = Cost1(60000.0, 'USD', 2003)  # [$/turbine]
    # Investment costs - Procurement & Installation - Support structure

    return dimension_team_support.total_support_structure_cost + boat_landing_cost