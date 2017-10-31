from openmdao.api import ExplicitComponent
from input_params import max_n_turbines, max_n_substations


class AbstractCollectionDesign(ExplicitComponent):

    def setup(self):
        self.add_input('layout', shape=(max_n_turbines, 3))
        self.add_input('n_turbines_p_cable_type', shape=3)
        self.add_input('substation_coords', shape=(max_n_substations, 2))
        self.add_input('n_substations', val=0)

        self.add_output('topology', shape=(1, 3, 3, 2))
        self.add_output('cost', val=0.0)
        self.add_output('cable_lengths', shape=3)

    def compute(self, inputs, outputs):
        layout = [[int(coord[0]), coord[1], coord[2]] for coord in inputs['layout']]
        n_substations = int(inputs['n_substations'])
        n_turbines_p_cable_type = [int(num) for num in inputs['n_turbines_p_cable_type']]
        substation_coords = inputs['substation_coords'][:n_substations]

        cost, topology_dict, cable_lengths = self.topology_design_model(layout, substation_coords, n_turbines_p_cable_type)

        topology = []
        print topology_dict
        for n in range(1, max_n_substations):
            topology.append(topology_dict[n])
        print topology
        outputs['cost'] = cost
        outputs['topology'] = topology
        outputs['cable_lengths'] = cable_lengths

    def topology_design_model(self, layout, substation_coords, n_turbines_p_cable_type, n_substations):
        # Define your own model in a subclass of AbstractCollectionDesign and redefining this method.
        pass
