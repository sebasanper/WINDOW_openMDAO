from openmdao.api import Group
from WINDOW_openMDAO.src.api import DeficitMatrix, CtMatrix


class TIWorkflow(Group):

	def __init__(self, n_cases, turbulence_model):
		super(TIWorkflow, self).__init__()
		self.n_cases = n_cases
		self.turbulence_model = turbulence_model

	def setup(self):

		self.add_subsystem('dU_matrix', DeficitMatrix(self.n_cases))
		self.add_subsystem('ct_matrix', CtMatrix(self.n_cases))
		self.add_subsystem('TI', self.turbulence_model(self.n_cases), promotes_outputs=['TI_eff'], promotes_inputs=['ordered', 'TI_amb', 'freestream', 'n_turbines', 'radius'])

		self.connect('dU_matrix.dU_matrix', 'TI.dU_matrix')
		self.connect('ct_matrix.ct_matrix', 'TI.ct')
