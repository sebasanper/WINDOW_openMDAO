def other_costs(depth_central_platform, n_turbines, infield_length, n_substations, \
                turbine_rated_power, rotor_radius, purchase_price, warranty_percentage, \
                rna_mass, hub_height, generator_voltage, collection_voltage):
    #from WINDOW_openMDAO.input_params import turbine_rated_power
    from investment_costs.project_development_cost import project_development_cost
    from investment_costs.management_cost import management_costs
    from investment_costs.procurement_costs.auxiliary_costs.auxiliary_costs import auxiliary_procurement
    from investment_costs.procurement_costs.electrical_system_costs.electrical_costs import electrical_procurement_costs
    from investment_costs.procurement_costs.RNA_costs.RNA_costs import rna_costs
    from investment_costs.installation_costs.auxiliary_installation_costs import auxiliary_installation_costs
    from investment_costs.installation_costs.electrical_installation_costs import electrical_installation_costs
    from investment_costs.installation_costs.RNA_installation_costs import rna_installation_costs
    from decommissioning_costs.decommissioning_costs import decommissioning_costs

    project_development = project_development_cost(n_turbines, turbine_rated_power)

    procurement_auxiliary = auxiliary_procurement(depth_central_platform, n_substations, n_turbines, turbine_rated_power)

    procurement_rna = rna_costs(n_turbines, purchase_price, warranty_percentage)

    procurement_electrical = electrical_procurement_costs(n_turbines, turbine_rated_power, generator_voltage, collection_voltage)

    installation_auxiliary = auxiliary_installation_costs(n_turbines, turbine_rated_power)

    installation_electrical = electrical_installation_costs()

    installation_rna = rna_installation_costs(n_turbines, rotor_radius, hub_height)

    decommissioning = decommissioning_costs(infield_length, n_turbines, rna_mass, hub_height)

    investment_costs = project_development + procurement_auxiliary + procurement_rna + procurement_electrical + installation_auxiliary + installation_electrical + installation_rna
    # print "project_development ", project_development
    # print "procurement_auxiliary", procurement_auxiliary 
    # print "procurement_rna" ,procurement_rna 
    # print "procurement_electrical" ,procurement_electrical 
    # print "installation_auxiliary" ,installation_auxiliary 
    # print "installation_electrical", installation_electrical
    # print  "installation_rna", installation_rna
    # print "installation + procurement turbines"
    # print procurement_rna + installation_rna
    #
    # print "installation + procurement electrical"
    # print installation_electrical + procurement_electrical
    #
    # print "project development"
    # print project_development
    #
    # print "auxiliary costs"
    # print procurement_auxiliary + installation_auxiliary
    #
    # print "decommissioning costs"
    # print decommissioning

    management_investment = management_costs(investment_costs)

    # print "investment costs"
    # print investment_costs + management_investment

    return investment_costs + management_investment, decommissioning


if __name__ == '__main__':
    print total_costs(20.0, 5, 230000)
