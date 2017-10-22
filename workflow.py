from WakeModel.wake_linear_solver import WakeModel, OrderLayout
from openmdao.api import IndepVarComp, Problem, Group, view_model
import numpy as np
from time import time
from input_params import jensen_k, turbine_radius, n_turbines
from Power.abstract_power import PowerPolynomial, FarmAeroPower


class WorkingGroup(Group):
    def setup(self):
        indep2 = self.add_subsystem('indep2', IndepVarComp())
        # indep2.add_output('layout', val=read_layout('horns_rev9.dat'))
        indep2.add_output('layout', val=np.array([[0, 0.0, 0.0], [1, 560.0, 560.0], [2, 1120.0, 1120.0], [3, 1120.0, 0.0], [4, 0.0, 1120.0]]))
        indep2.add_output('angle', val=180.0)
        indep2.add_output('r', val=turbine_radius)
        indep2.add_output('k', val=jensen_k)
        self.add_subsystem('wakemodel', WakeModel())
        self.add_subsystem('power', PowerPolynomial())
        self.add_subsystem('farmpower', FarmAeroPower())
        self.connect('indep2.layout', 'wakemodel.original')
        self.connect('indep2.angle', 'wakemodel.angle')
        self.connect('indep2.k', 'wakemodel.k')
        self.connect('indep2.r', 'wakemodel.r')
        self.connect('wakemodel.U', 'power.U')
        self.connect('power.p', 'farmpower.ind_powers')

def read_layout(layout_file):

    layout_file = open(layout_file, 'r')
    layout = []
    i = 0
    for line in layout_file:
        columns = line.split()
        layout.append([i, float(columns[0]), float(columns[1])])
        i += 1

    return np.array(layout)

prob = Problem()
prob.model = WorkingGroup()
prob.setup()
# view_model(prob)
start = time()
prob.run_model()
print time() - start, "seconds"
# prob.model.list_outputs()
print prob['farmpower.farm_power']


# with open("angle_5square.dat", 'w') as out:
#     start= time()
#     for ang in range(360):
#         prob['indep2.angle'] = ang
#         prob.run_model()
#         indices = [i[0] for i in prob['order.ordered']]
#         final = [[indices[n], prob['wakemodel.speed{}.U'.format(int(n))][0]] for n in range(len(indices))]
#         final =sorted(final)
#         out.write('{}'.format(ang))
#         for n in range(n_turbines):
#             out.write(' {}'.format(final[n][1]))
#         out.write('\n')
#     print time() - start, "seconds"
