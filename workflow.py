from WakeModel.wake_linear_solver import WakeModel, OrderLayout
from openmdao.api import IndepVarComp, Problem, Group, view_model
import numpy as np
from time import time

n_turbines = 8

class WorkingGroup(Group):
    def setup(self):
        indep2 = self.add_subsystem('indep2', IndepVarComp())
        indep2.add_output('layout', val=read_layout('horns_rev9.dat'))
        # indep2.add_output('layout', val=np.array([[0, 0.0, 0.0], [1, 560.0, 560.0], [2, 1120.0, 1120.0], [3, 1120.0, 0.0], [4, 0.0, 1120.0]]))
        indep2.add_output('angle', val=0.0)
        self.add_subsystem('order', OrderLayout())
        self.add_subsystem('wakemodel', WakeModel())
        self.connect('indep2.layout', 'order.original')
        self.connect('indep2.angle', 'order.angle')
        self.connect('order.ordered', 'wakemodel.layout')
        self.connect('indep2.angle', 'wakemodel.angle')

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
prob['indep2.angle'] = 276.0
start = time()
prob.run_model()
print time() - start, "seconds"
# prob.model.list_outputs()


print prob['order.ordered']
print
results = prob['order.ordered'].tolist()
indices = [i[0] for i in results]
final = [[indices[n], prob['wakemodel.speed{}.U'.format(int(n))][0]] for n in range(len(indices))]
final = sorted(final)
for n in range(n_turbines):
    print(final[n][1])

# with open("angle_speedhorns8newt.dat", 'w') as out:
#     start= time()
#     for ang in range(57, 58):
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
