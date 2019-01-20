# workflow_regular.py only defines the workflow to be built. Class WorkingGroup needs to be imported from another working directory. As an example we provide a working directory in the example folder. Run IEA_borssele_regular.py from the 'example' folder instead

from openmdao.api import IndepVarComp, Group, ExecComp
from WINDOW_openMDAO.input_params import max_n_turbines, max_n_substations, interest_rate, central_platform, areas, n_quadrilaterals, separation_equation_y, operational_lifetime, number_turbines_per_cable, wind_directions, weibull_shapes, weibull_scales, direction_probabilities, layout, n_turbines, TI_ambient, coll_electrical_efficiency, transm_electrical_efficiency, number_substations
from WINDOW_openMDAO.src.api import AEP, NumberLayout, MinDistance, WithinBoundaries
from WINDOW_openMDAO.WaterDepth.water_depth_models import RoughClosestNode
from WINDOW_openMDAO.Finance.LCOE import LCOE
from WINDOW_openMDAO.RNA.rna import RNA

class WorkingGroup(Group):
    def __init__(self, options):
        super(WorkingGroup, self).__init__()
        self.aep_model = options.models.aep
        self.wake_model = options.models.wake
        self.merge_model = options.models.merge
        self.turbine_model = options.models.turbine
        self.turbulence_model = options.models.turbulence
        self.electrical_model = options.models.electrical
        self.support_model = options.models.support
        self.opex_model = options.models.opex
        self.apex_model = options.models.apex
        self.windspeed_sampling_points = options.samples.wind_speeds
        self.direction_sampling_angle = options.samples.wind_sectors_angle
        # self.n_cases = int((360.0 / self.direction_sampling_angle) * (self.windspeed_sampling_points + 1.0))
        self.windrose_file = options.input.site.windrose_file
        self.bathymetry_file = options.input.site.bathymetry_file
        
        self.power_curve_file = options.input.turbine.power_file
        self.ct_curve_file = options.input.turbine.ct_file
        self.num_pegged = options.input.turbine.num_pegged
        self.num_airfoils = options.input.turbine.num_airfoils
        self.num_nodes = options.input.turbine.num_nodes
        self.num_bins = options.input.turbine.num_bins
        self.safety_factor = options.input.turbine.safety_factor
        self.gearbox_stages = options.input.turbine.gearbox_stages
        self.gear_configuration = options.input.turbine.gear_configuration
        self.mb1_type = options.input.turbine.mb1_type
        self.mb2_type = options.input.turbine.mb2_type
        self.drivetrain_design = options.input.turbine.drivetrain_design
        self.uptower_transformer = options.input.turbine.uptower_transformer
        self.has_crane = options.input.turbine.has_crane
        self.reference_turbine = options.input.turbine.reference_turbine
        self.reference_turbine_cost = options.input.turbine.reference_turbine_cost
         

    def setup(self):
        indep2 = self.add_subsystem('indep2', IndepVarComp())

        indep2.add_output("areas", val=areas)
        indep2.add_output('layout', val=layout)
        indep2.add_output('turbine_radius', val=95.4)
        indep2.add_output('n_turbines', val=n_turbines)
        indep2.add_output('n_turbines_p_cable_type', val=number_turbines_per_cable)  # In ascending order, but 0 always at the end. 0 is used for requesting only two or one cable type.
        indep2.add_output('substation_coords', val=central_platform)
        indep2.add_output('n_substations', val=number_substations)
        indep2.add_output('coll_electrical_efficiency', val=coll_electrical_efficiency)
        indep2.add_output('transm_electrical_efficiency', val=transm_electrical_efficiency)
        indep2.add_output('operational_lifetime', val=operational_lifetime)
        indep2.add_output('interest_rate', val=interest_rate)
        
        indep2.add_output('design_tsr', desc='design tip speed ratio')
        indep2.add_output('blade_number', desc='number of blades')
        indep2.add_output('chord_coefficients', units = 'm', desc = 'coefficients of polynomial chord profile', shape=self.num_pegged)
        indep2.add_output('twist_coefficients', units = 'deg', desc = 'coefficients of polynomial twist profile', shape=self.num_pegged)       
        indep2.add_output('span_airfoil_r', units='m', desc='list of blade node radial location at which the airfoils are specified', shape=self.num_airfoils)
        indep2.add_output('span_airfoil_id', desc='list of blade node Airfoil ID', shape=self.num_airfoils)
        indep2.add_output('pitch', units='deg', desc = 'pitch angle')
        indep2.add_output('thickness_factor', desc='scaling factor for laminate thickness')
        indep2.add_output('shaft_angle', units='deg', desc='angle of the LSS inclindation with respect to the horizontal')
        indep2.add_output('cut_in_speed', units = 'm/s', desc = 'cut-in wind speed')
        indep2.add_output('cut_out_speed', units = 'm/s', desc = 'cut-out wind speed')
        indep2.add_output('machine_rating', units='kW', desc='machine rating')
        indep2.add_output('drive_train_efficiency', desc='efficiency of aerodynamic to electrical conversion')
        indep2.add_output('gear_ratio', desc='overall gearbox ratio')
        indep2.add_output('Np', desc='number of planets in each stage', shape=3)
        
        self.add_subsystem('rad2dia', ExecComp('rotor_diameter = turbine_radius*2.0', \
                                               rotor_diameter = {'units': 'm'}))
        self.add_subsystem('rna', RNA(num_pegged=self.num_pegged, \
                                       num_airfoils=self.num_airfoils, \
                                       num_nodes=self.num_nodes, \
                                       num_bins=self.num_bins, \
                                       safety_factor=self.safety_factor, \
                                       gearbox_stages=self.gearbox_stages, \
                                       gear_configuration=self.gear_configuration, \
                                       mb1_type=self.mb1_type, \
                                       mb2_type=self.mb2_type, \
                                       drivetrain_design=self.drivetrain_design, \
                                       uptower_transformer=self.uptower_transformer, \
                                       has_crane=self.has_crane, \
                                       reference_turbine=self.reference_turbine, \
                                       reference_turbine_cost=self.reference_turbine_cost, \
                                       power_file=self.power_curve_file, \
                                       ct_file=self.ct_curve_file))
        self.add_subsystem('usd2eur', ExecComp('cost_rna_eur = cost_rna_usd * 0.88'))
        
        self.add_subsystem('numbersubstation', NumberLayout(max_n_substations))
        self.add_subsystem('numberlayout', NumberLayout(max_n_turbines))
        self.add_subsystem('depths', RoughClosestNode(max_n_turbines, self.bathymetry_file))
        self.add_subsystem('platform_depth', RoughClosestNode(max_n_substations, self.bathymetry_file))

        self.add_subsystem('AeroAEP', self.aep_model(self.wake_model, self.turbulence_model, self.merge_model, self.direction_sampling_angle, self.windspeed_sampling_points, self.windrose_file, self.power_curve_file, self.ct_curve_file))

        self.add_subsystem('electrical', self.electrical_model())

        self.add_subsystem('support', self.support_model())
        self.add_subsystem('OandM', self.opex_model())
        self.add_subsystem('AEP', AEP())
        self.add_subsystem('Costs', self.apex_model())
        self.add_subsystem('lcoe', LCOE())
        self.add_subsystem('constraint_distance', MinDistance())
        self.add_subsystem('constraint_boundary', WithinBoundaries())
        
        self.connect('indep2.turbine_radius', 'rad2dia.turbine_radius')
        self.connect('rad2dia.rotor_diameter', 'rna.rotor_diameter')
        self.connect('indep2.design_tsr', 'rna.design_tsr')
        self.connect('indep2.blade_number', 'rna.blade_number')
        self.connect('indep2.chord_coefficients', 'rna.chord_coefficients')
        self.connect('indep2.twist_coefficients', 'rna.twist_coefficients')
        self.connect('indep2.span_airfoil_r', 'rna.span_airfoil_r')
        self.connect('indep2.span_airfoil_id', 'rna.span_airfoil_id')
        self.connect('indep2.pitch', 'rna.pitch')
        self.connect('indep2.thickness_factor', 'rna.thickness_factor')
        self.connect('indep2.shaft_angle', 'rna.shaft_angle')
        self.connect('indep2.cut_in_speed', 'rna.cut_in_speed')
        self.connect('indep2.cut_out_speed', 'rna.cut_out_speed')
        self.connect('indep2.machine_rating', 'rna.machine_rating')
        self.connect('indep2.drive_train_efficiency', 'rna.drive_train_efficiency')
        self.connect('indep2.gear_ratio', 'rna.gear_ratio')
        self.connect('indep2.Np', 'rna.Np')
        self.connect('rna.cost_rna', 'usd2eur.cost_rna_usd')
        
        self.connect('indep2.turbine_radius', 'AeroAEP.turbine_radius')
        self.connect('indep2.cut_in_speed', 'AeroAEP.cut_in_speed')
        self.connect('indep2.cut_out_speed', 'AeroAEP.cut_out_speed')
        self.connect('indep2.machine_rating', 'AeroAEP.machine_rating')
        self.connect('rna.rated_wind_speed', 'AeroAEP.rated_wind_speed')

        self.connect("indep2.layout", ["numberlayout.orig_layout", "AeroAEP.layout", "constraint_distance.orig_layout", "constraint_boundary.layout"])
        self.connect("indep2.substation_coords", "numbersubstation.orig_layout")
        self.connect("indep2.turbine_radius", "constraint_distance.turbine_radius")
        self.connect("indep2.areas", "constraint_boundary.areas")

        self.connect('numberlayout.number_layout', 'depths.layout')

        self.connect('indep2.n_turbines', ['AeroAEP.n_turbines', 'electrical.n_turbines', 'support.n_turbines', 'Costs.n_turbines'])

        self.connect('numberlayout.number_layout', 'electrical.layout')
        self.connect('indep2.n_turbines_p_cable_type', 'electrical.n_turbines_p_cable_type')
        self.connect('indep2.substation_coords', 'electrical.substation_coords')
        self.connect('indep2.n_substations', 'electrical.n_substations')
        self.connect('rna.turbine_rated_current', 'electrical.turbine_rated_current')

        self.connect('depths.water_depths', 'support.depth')
        self.connect('AeroAEP.max_TI', 'support.max_TI')
        self.connect('indep2.turbine_radius', 'support.rotor_radius')
        self.connect('rna.rated_wind_speed', 'support.rated_wind_speed')
        self.connect('rna.rotor_thrust', 'support.rotor_thrust')
        self.connect('rna.rna_mass', 'support.rna_mass')
        self.connect('rna.solidity_rotor', 'support.solidity_rotor')
        self.connect('rna.cd_rotor_idle_vane', 'support.cd_rotor_idle_vane')
        self.connect('rna.cd_nacelle', 'support.cd_nacelle')
        self.connect('rna.tower_top_diameter', 'support.yaw_diameter')
        self.connect('rna.front_area_nacelle', 'support.front_area_nacelle')
        self.connect('rna.yaw_to_hub_height', 'support.yaw_to_hub_height')
        self.connect('rna.mass_eccentricity', 'support.mass_eccentricity')

        self.connect('AeroAEP.efficiency', 'OandM.array_efficiency')
        self.connect('AeroAEP.AEP', ['AEP.aeroAEP', 'OandM.AEP'])
        self.connect('OandM.availability', 'AEP.availability')
        self.connect('indep2.coll_electrical_efficiency', 'AEP.electrical_efficiency')

        self.connect('numbersubstation.number_layout', 'platform_depth.layout')
        self.connect('platform_depth.water_depths', 'Costs.depth_central_platform', src_indices=[0])

        self.connect('indep2.n_substations', 'Costs.n_substations')
        self.connect('electrical.length_p_cable_type', 'Costs.length_p_cable_type')
        self.connect('electrical.cost_p_cable_type', 'Costs.cost_p_cable_type')
        self.connect('support.cost_support', 'Costs.support_structure_costs')
        self.connect('indep2.machine_rating', 'Costs.machine_rating')
        self.connect('indep2.turbine_radius', 'Costs.rotor_radius')
        self.connect('rna.hub_height', 'Costs.hub_height')
        self.connect('usd2eur.cost_rna_eur', 'Costs.purchase_price')
        self.connect('rna.warranty_percentage', 'Costs.warranty_percentage')
        self.connect('rna.rna_mass', 'Costs.rna_mass')
        self.connect('rna.generator_voltage', 'Costs.generator_voltage')
        self.connect('rna.collection_voltage', 'Costs.collection_voltage')

        self.connect('Costs.investment_costs', 'lcoe.investment_costs')
        self.connect('OandM.annual_cost_O&M', 'lcoe.oandm_costs')
        self.connect('Costs.decommissioning_costs', 'lcoe.decommissioning_costs')
        self.connect('AEP.AEP', 'lcoe.AEP')
        self.connect('indep2.transm_electrical_efficiency', 'lcoe.transm_electrical_efficiency')
        self.connect('indep2.operational_lifetime', 'lcoe.operational_lifetime')
        self.connect('indep2.interest_rate', 'lcoe.interest_rate')