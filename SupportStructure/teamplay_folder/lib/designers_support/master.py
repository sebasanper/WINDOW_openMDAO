class MasterDesigners:
    def __init__(self, support_team):
        self.support_team = support_team
#        self.design_variables = self.support_team.design_variables.linking_variables
        pass

    def initialyse(self):
        # print "4001"
        self.support_team.site_conditions_analysts.set_conditions()  # it uses the layout module!!
        # print "4002"
        self.support_team.rna_analysts.initialyse()
        #  print "4003"
