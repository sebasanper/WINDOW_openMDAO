from copy import deepcopy

from ..system.design_vector import DesignVector
from ..system.properties import Properties
from ..system.value import Value

from ..environment.physical_environment import PhysicalEnvironment

from master import MasterDesigners

from .support_structures import SupportDesigners

from ..analysts_physics.rna import RNAAnalysts
from ..analysts_physics.site_conditions import SiteConditionsAnalysts
from ..analysts_physics.hydrodynamics import HydrodynamicAnalysts
from ..analysts_physics.aerodynamics import AerodynamicAnalysts
from ..analysts_physics.gravity import GravityAnalysts
from ..analysts_physics.geophysics import GeophysicalAnalysts
from ..analysts_physics.mechanics import MechanicalAnalysts

from ..analysts_physics.rocks import RockAnalysts

from ..analysts_humanities.cost_support_structure import CostAnalysts


class DimensionTeamSupport:
    def __init__(self):
        #        self.domain_top = domain_top
        #        self.previous_score = 0.0
        #        self.improvement = 100.0
        self.total_support_structure_cost = None
        # self.fsf = 1.5

    def run(self, rna, site_data):
        #        print "start run"
        self.design_variables = DesignVector()
        # print "2"
        #        self.design_variables.linking_variables = deepcopy(linking_variables)
        self.properties = Properties()
        self.properties.rna = deepcopy(rna)
        self.physical_environment = PhysicalEnvironment()
        self.physical_environment.site = deepcopy(site_data)
        #        self.optimisation = optimisation
        self.value = Value()

        self.master_designers = MasterDesigners(self)
        self.support_designers = SupportDesigners(self)
        self.support_designers.fatigue_safety_factor = self.fsf
        # print "3"
        self.rna_analysts = RNAAnalysts(self)
        self.site_conditions_analysts = SiteConditionsAnalysts(self)
        self.hydrodynamic_analysts = HydrodynamicAnalysts(self)
        self.aerodynamic_analysts = AerodynamicAnalysts(self)
        self.gravity_analysts = GravityAnalysts(self)
        self.geophysical_analysts = GeophysicalAnalysts(self)
        self.mechanical_analysts = MechanicalAnalysts(self)

        self.rock_analysts = RockAnalysts(self)
        self.cost_analysts = CostAnalysts(self)
        # print "4"
        self.initialyse()
        # print "41"
        self.set_initial_values()
        # print "5"
        # t0 = time()

    #        self.domain_top.display.discipline = 'Evaluating'
    #        self.multi_criteria_analysts.evaluate_objective_function("support_structure")

    #        self.previous_score = self.multi_criteria_analysts.score
    #        self.domain_top.display.previous_score = str(self.previous_score)
    # t1 = time(); print "  Objective function:", 1000*(t1 - t0), "ms"; t0 = time()
    #        if self.optimisation:
    #            if self.optimise() != True:
    #                return False
    #        return True

    def initialyse(self):
        # print "401"
        self.master_designers.initialyse()  # Master designers have to be initialysed first. The order of the other designers is arbitrary
        # print "402"
        self.support_designers.initialyse()
        # print "403"
        # @@@self.cost_analysts.initialyse() #Cost analysts have to be initialysed last
        # print "404"

    def set_initial_values(self):
        # print "Set initial values:"

        #        self.domain_top.display.discipline = 'Support structure'
        self.support_designers.set_initial_values()

        self.cost_analysts.initialyse()
        # print 6
