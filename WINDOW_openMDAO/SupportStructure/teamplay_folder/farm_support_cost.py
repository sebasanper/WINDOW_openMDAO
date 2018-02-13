from costs.investment_costs.BOS_cost.support_cost.SupportTeam import design_support


def farm_support_cost(depths, turbulences):
    total_cost = 0
    # print depths
    # print turbulences
    for i in range(len(depths)):
        single_cost = design_support(depths[i], turbulences[i])
        total_cost += single_cost

    return total_cost
