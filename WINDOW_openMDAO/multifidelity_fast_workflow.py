"""Summary
"""
# workflow_regular.py only defines the workflow to be built. Class WorkingGroup needs to be imported from another working directory. As an example we provide a working directory in the example folder. Run IEA_borssele_regular.py from the 'example' folder instead

from openmdao.api import IndepVarComp, Group
from WINDOW_openMDAO.input_params import rotor_radius, max_n_turbines, max_n_substations, interest_rate, central_platform, areas, n_quadrilaterals, separation_equation_y, cutin_wind_speed, cutout_wind_speed, operational_lifetime, number_turbines_per_cable, wind_directions, weibull_shapes, weibull_scales, direction_probabilities, layout, n_turbines, TI_ambient, coll_electrical_efficiency, transm_electrical_efficiency, number_substations
from WINDOW_openMDAO.src.api import AEP, MinDistance, WithinBoundaries
from WINDOW_openMDAO.WaterDepth.water_depth_models import RoughClosestNode
from WINDOW_openMDAO.Finance.LCOE import LCOE


class WorkingGroup(Group):

    """Summary
    
    Attributes:
        aep_model (TYPE): Description
        apex_model (TYPE): Description
        bathymetry_file (TYPE): Description
        ct_curve_file (TYPE): Description
        direction_sampling_angle (TYPE): Description
        electrical_model (TYPE): Description
        merge_model (TYPE): Description
        opex_model (TYPE): Description
        power_curve_file (TYPE): Description
        support_model (TYPE): Description
        turbine_model (TYPE): Description
        turbulence_model (TYPE): Description
        wake_model (TYPE): Description
        windrose_file (TYPE): Description
        windspeed_sampling_points (TYPE): Description
    """
    
    def __init__(self, options):
        """Summary
        
        Args:
            options (TYPE): Description
        """
        super(WorkingGroup, self).__init__()
        self.options = options
        # self.aep_model = options.models.aep
        # self.wake_model = options.models.wake
        # self.merge_model = options.models.merge
        # self.turbine_model = options.models.turbine
        # self.turbulence_model = options.models.turbulence
        # self.electrical_model = options.models.electrical
        # self.support_model = options.models.support
        # self.opex_model = options.models.opex
        # self.apex_model = options.models.apex
        # self.windspeed_sampling_points = options.samples.wind_speeds
        # self.direction_sampling_angle = options.samples.wind_sectors_angle
        # # self.n_cases = int((360.0 / self.direction_sampling_angle) * (self.windspeed_sampling_points + 1.0))
        # self.windrose_file = options.input.site.windrose_file
        # self.bathymetry_file = options.input.site.bathymetry_file
        # self.power_curve_file = options.input.turbine.power_file
        # self.ct_curve_file = options.input.turbine.ct_file

    def setup(self):
        """Summary
        """
        indep2 = self.add_subsystem('indep2', IndepVarComp())

        indep2.add_output("areas", val=areas)
        indep2.add_output('layout', val=layout)
        indep2.add_output('rotor_radius', val=rotor_radius)
        indep2.add_output('n_turbines', val=n_turbines)
        indep2.add_output('n_turbines_p_cable_type', val=number_turbines_per_cable)  # In ascending order, but 0 always at the end. 0 is used for requesting only two or one cable type.
        indep2.add_output('substation_coords', val=central_platform)
        indep2.add_output('n_substations', val=number_substations)
        indep2.add_output('coll_electrical_efficiency', val=coll_electrical_efficiency)
        indep2.add_output('transm_electrical_efficiency', val=transm_electrical_efficiency)
        indep2.add_output('operational_lifetime', val=operational_lifetime)
        indep2.add_output('interest_rate', val=interest_rate)

        # self.add_subsystem('numbersubstation', NumberLayout(max_n_substations)) # To be deleted
        # self.add_subsystem('numberlayout', NumberLayout(max_n_turbines)) # To be deleted
        self.add_subsystem('depths', RoughClosestNode(max_n_turbines, self.options.input.site.bathymetry_file))
        self.add_subsystem('platform_depth', RoughClosestNode(max_n_substations, self.options.input.site.bathymetry_file))

        self.add_subsystem('AeroAEP', self.options.models.aep(self.options))

        self.add_subsystem('electrical', self.options.models.electrical())

        self.add_subsystem('support', self.options.models.support())
        self.add_subsystem('OandM', self.options.models.opex())
        self.add_subsystem('AEP', AEP())
        self.add_subsystem('Costs', self.options.models.capex())
        self.add_subsystem('lcoe', LCOE())
        # self.add_subsystem('constraint_distance', MinDistance())
        # self.add_subsystem('constraint_boundary', WithinBoundaries())

        self.connect("indep2.layout", ["AeroAEP.layout", "electrical.layout", "depths.layout"])
        # self.connect("indep2.substation_coords", "numbersubstation.orig_layout") # To be deleted
        # self.connect("indep2.turbine_radius", "constraint_distance.turbine_radius")
        # self.connect("indep2.areas", "constraint_boundary.areas")

        # self.connect('numberlayout.number_layout', 'depths.layout') # To be deleted

        self.connect('indep2.n_turbines', ['depths.n_turbines', 'AeroAEP.n_turbines', 'electrical.n_turbines', 'support.n_turbines', 'Costs.n_turbines'])

        # self.connect('numberlayout.number_layout', 'electrical.layout') # To be deleted
        self.connect('indep2.n_turbines_p_cable_type', 'electrical.n_turbines_p_cable_type')
        self.connect('indep2.substation_coords', 'electrical.substation_coords')
        self.connect('indep2.n_substations', 'electrical.n_substations')

        self.connect('depths.water_depths', 'support.depth')
        self.connect('AeroAEP.max_TI', 'support.max_TI')

        self.connect('AeroAEP.efficiency', 'OandM.array_efficiency')
        self.connect('AeroAEP.AEP', ['AEP.aeroAEP', 'OandM.AEP'])
        self.connect('OandM.availability', 'AEP.availability')
        self.connect('indep2.coll_electrical_efficiency', 'AEP.electrical_efficiency')

        # self.connect('numbersubstation.number_layout', 'platform_depth.layout') # To be deleted
        self.connect('indep2.substation_coords', 'platform_depth.layout') # To be deleted
        self.connect('indep2.n_substations', "platform_depth.n_turbines")
        self.connect('platform_depth.water_depths', 'Costs.depth_central_platform', src_indices=[0])

        self.connect('indep2.n_substations', 'Costs.n_substations')
        self.connect('electrical.length_p_cable_type', 'Costs.length_p_cable_type')
        self.connect('electrical.cost_p_cable_type', 'Costs.cost_p_cable_type')
        self.connect('support.cost_support', 'Costs.support_structure_costs')


        self.connect('Costs.investment_costs', 'lcoe.investment_costs')
        self.connect('OandM.annual_cost_O&M', 'lcoe.oandm_costs')
        self.connect('Costs.decommissioning_costs', 'lcoe.decommissioning_costs')
        self.connect('AEP.AEP', 'lcoe.AEP')
        self.connect('indep2.transm_electrical_efficiency', 'lcoe.transm_electrical_efficiency')
        self.connect('indep2.operational_lifetime', 'lcoe.operational_lifetime')
        self.connect('indep2.interest_rate', 'lcoe.interest_rate')
