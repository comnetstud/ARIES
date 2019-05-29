import numpy as np
import pandapower as pp
from pandas import DataFrame as df

from aries.core.constants import PCC_VOLTAGE, NON_LINEAR_SOLVER
from aries.simulation.solver.solver import Solver


class NonLinearSolver(Solver):

    def __init__(self, paths, nodes, lines):
        """Initialize the grid configuration"""
        super().__init__(paths=paths, nodes=nodes, lines=lines)
        self.type = NON_LINEAR_SOLVER

    def build(self, agents_states):
        net = pp.create_empty_network()

        buses_dict = {}
        bus_to_idx = {}
        bus_idx = 0
        for bus_name in self.nodes.keys():
            buses_dict[bus_name] = pp.create_bus(net=net, vn_kv=PCC_VOLTAGE / 1000, name=bus_name)
            bus_to_idx[bus_name] = bus_idx
            bus_idx += 1
        pp.create_ext_grid(net, bus=buses_dict['SLACK'], vm_pu=1, va_degree=0, name='Grid Connection')

        lines_dict = {}
        line_to_idx = {}
        line_idx = 0
        for bus_name, node in self.nodes.items():
            if node.agent is not None:
                agent_name = node.agent

                demand_active_power = agents_states[agent_name]['demand_power']['active_power']
                demand_reactive_power = agents_states[agent_name]['demand_power']['reactive_power']

                inject_active_power = agents_states[agent_name]['inject_power']['active_power']
                inject_reactive_power = agents_states[agent_name]['inject_power']['reactive_power']

                net_active_power = inject_active_power - demand_active_power
                net_reactive_power = inject_reactive_power - demand_reactive_power
                pp.create_sgen(net=net, bus=buses_dict[bus_name], p_kw=-net_active_power / 1000,
                               q_kvar=-net_reactive_power / 1000, name=agent_name)

            adjacent = node.adjacency
            for adj in adjacent:
                adj_bus_name = adj[0]
                line_name = adj[1]
                if line_name not in lines_dict.keys():
                    lines_dict[line_name] = pp.create_line_from_parameters(net=net, from_bus=buses_dict[bus_name],
                                                                           to_bus=buses_dict[adj_bus_name], length_km=1,
                                                                           r_ohm_per_km=self.lines[
                                                                               line_name].resistance,
                                                                           x_ohm_per_km=self.lines[
                                                                               line_name].reactance, c_nf_per_km=0,
                                                                           max_i_ka=1, name=line_name)
                    line_to_idx[line_name] = line_idx
                    line_idx += 1

        return net, line_to_idx, bus_to_idx

    def power_from_main(self, grid_solution):
        return np.complex(grid_solution['buses']['SLACK']['p_kw'] * 1000,
                          grid_solution['buses']['SLACK']['q_kvar'] * 1000)

    def power_distribution_loss(self, grid_solution):
        power = 0
        for line_name in self.lines.keys():
            power += grid_solution['lines'][line_name]['pl_kw'] * 1000
        return power

    def solve(self, agents_state):
        net, line_to_idx, bus_to_idx = self.build(agents_state)
        pp.runpp(net)
        result_bus_dict = df.to_dict(net.res_bus, orient='index')
        result_line_dict = df.to_dict(net.res_line, orient='index')
        bus_dict = {}
        line_dict = {}
        for bus_name in bus_to_idx.keys():
            bus_dict[bus_name] = result_bus_dict[bus_to_idx[bus_name]]
        for line_name in line_to_idx.keys():
            line_dict[line_name] = result_line_dict[line_to_idx[line_name]]
        solution_dict = {
            'buses': bus_dict,
            'lines': line_dict
        }
        power_from_main = self.power_from_main(grid_solution=solution_dict)
        distribution_loss = self.power_distribution_loss(grid_solution=solution_dict)
        solution_dict['power_from_main'] = {'real': np.real(power_from_main), 'imag': np.imag(power_from_main)}
        solution_dict['distribution_loss'] = {'real': distribution_loss, 'imag': 0}
        return solution_dict
