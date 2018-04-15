# Project development
from WINDOW_openMDAO.Costs.costs.currency import Cost1


def project_development_cost(number_turbines, rated_power):
    NT = number_turbines
    P_rated = rated_power
    engineering_per_watt = Cost1(0.037, 'USD', 2003)  # [$/Watt]

    # Investment costs - Project development
    inv_project_development_engineering = NT * P_rated * engineering_per_watt
    return inv_project_development_engineering

if __name__ == '__main__':
    number = 3
    rating = 6.0
    print project_development_cost(number, rating)
