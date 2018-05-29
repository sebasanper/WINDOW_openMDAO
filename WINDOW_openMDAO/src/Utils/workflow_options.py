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
		self.turbine = Site()


class Site():
	def __init__(self):
		self.windrose_file = None
		self.bathymetry_file = None


class Turbine():
	def __init__(self):
		self.power_file = None
		self.ct_file = None


class WorkflowOptions():
	def __init__(self):
		self.samples = Samples()
		self.models = Models()
		self.input = Input()
