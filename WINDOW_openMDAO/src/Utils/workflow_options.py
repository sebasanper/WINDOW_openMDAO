class Models():
	def __init__(self):
		self.wake = None
		self.merge = None
		self.turbulence = None
		self.turbine = None
		self.aep = None
		self.electrical = None
		self.support = None
		self.opex = None
		self.apex = None


class Samples():
	def __init__(self):
		self.wind_speeds = 7
		self.wind_sector_angle = 6.0


class Input():
	def __init__(self):		
		self.site = Site()
		self.turbine = Turbine()


class Site():
	def __init__(self):
		self.windrose_file = None
		self.bathymetry_file = None


class Turbine():
	def __init__(self):
		self.power_file = None
		self.ct_file = None
		self.num_pegged = None
		self.num_airfoils = None
		self.num_nodes = None
		self.num_bins= None
		self.safety_factor = None
		self.gearbox_stages = None
		self.gear_configuration = None
		self.mb1_type = None
		self.mb2_type = None
		self.drivetrain_design = None
		self.uptower_transformer = None
		self.has_crane = None
		self.reference_turbine = None
		self.reference_turbine_cost = None


class WorkflowOptions():
	def __init__(self):
		self.samples = Samples()
		self.models = Models()
		self.input = Input()
