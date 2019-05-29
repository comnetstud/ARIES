import json
import unittest

import numpy as np
import pandapower as pp
from pandas import DataFrame as df

import unittest_utils
from aries.core.constants import PCC_VOLTAGE
from aries.core.grid import grid_utils
from aries.simulation.solver.non_linear_solver import NonLinearSolver

SOLVER_TEST_GRID_ELEMENTS_1 = 'power_flow_solver_test_grid_elements_1.json'

SOLVER_TEST_TOPOLOGY_1 = 'power_flow_solver_test_topology_1.json'


class TestNonLinearSolver(unittest.TestCase):
    def setUp(self):
        with unittest_utils.readfile(SOLVER_TEST_GRID_ELEMENTS_1, __file__) as f:
            j = json.load(f)
            agents, lines = grid_utils.create_grid_elements(j)
            self.agents = agents
            self.lines = lines

        with unittest_utils.readfile(SOLVER_TEST_TOPOLOGY_1, __file__) as f:
            j = json.load(f)
            paths, nodes = grid_utils.create_topology(j)

        self.solver = NonLinearSolver(paths=paths, nodes=nodes, lines=self.lines)

    def test_solver(self):
        agents_states = {}
        agents_states['AGENT0'] = {
            'impedance': {'resistance': 0, 'reactance': 0},
            'inject_power': {'active_power': 100, 'reactive_power': 200},
            'demand_power': {'active_power': 200, 'reactive_power': 100}}
        agents_states['AGENT1'] = {
            'impedance': {'resistance': 0, 'reactance': 0},
            'inject_power': {'active_power': 1000, 'reactive_power': 50},
            'demand_power': {'active_power': 10000, 'reactive_power': 50}}

        net = pp.create_empty_network()
        buses_dict = {
            'SLACK': pp.create_bus(net=net, vn_kv=PCC_VOLTAGE / 1000, name='SLACK'),
            'N0': pp.create_bus(net=net, vn_kv=PCC_VOLTAGE / 1000, name='N0'),
            'N1': pp.create_bus(net=net, vn_kv=PCC_VOLTAGE / 1000, name='N1'),
            'N2': pp.create_bus(net=net, vn_kv=PCC_VOLTAGE / 1000, name='N2')
        }
        bus_to_idx = {'SLACK': 0, 'N0': 1, 'N1': 2, 'N2': 3}

        pp.create_ext_grid(net, bus=buses_dict['SLACK'], vm_pu=1, va_degree=0, name='Grid Connection')

        demand_active_power_1 = agents_states['AGENT0']['demand_power']['active_power']
        demand_reactive_power_1 = agents_states['AGENT0']['demand_power']['reactive_power']
        inject_active_power_1 = agents_states['AGENT0']['inject_power']['active_power']
        inject_reactive_power_1 = agents_states['AGENT0']['inject_power']['reactive_power']
        net_active_power_1 = inject_active_power_1 - demand_active_power_1
        net_reactive_power_1 = inject_reactive_power_1 - demand_reactive_power_1

        demand_active_power_2 = agents_states['AGENT1']['demand_power']['active_power']
        demand_reactive_power_2 = agents_states['AGENT1']['demand_power']['reactive_power']
        inject_active_power_2 = agents_states['AGENT1']['inject_power']['active_power']
        inject_reactive_power_2 = agents_states['AGENT1']['inject_power']['reactive_power']
        net_active_power_2 = inject_active_power_2 - demand_active_power_2
        net_reactive_power_2 = inject_reactive_power_2 - demand_reactive_power_2

        pp.create_sgen(net=net, bus=buses_dict['N1'], p_kw=-net_active_power_1 / 1000,
                       q_kvar=-net_reactive_power_1 / 1000, name='AGENT0')
        pp.create_sgen(net=net, bus=buses_dict['N2'], p_kw=-net_active_power_2 / 1000,
                       q_kvar=-net_reactive_power_2 / 1000, name='AGENT1')

        lines_dict = {
            'B0': pp.create_line_from_parameters(net=net, from_bus=buses_dict['SLACK'], to_bus=buses_dict['N0'],
                                                 length_km=1, r_ohm_per_km=self.lines['B0'].resistance,
                                                 x_ohm_per_km=self.lines['B0'].reactance, c_nf_per_km=0, max_i_ka=1,
                                                 name='B0'),
            'B1': pp.create_line_from_parameters(net=net, from_bus=buses_dict['N0'], to_bus=buses_dict['N1'],
                                                 length_km=1, r_ohm_per_km=self.lines['B1'].resistance,
                                                 x_ohm_per_km=self.lines['B1'].reactance, c_nf_per_km=0, max_i_ka=1,
                                                 name='B1'),
            'B2': pp.create_line_from_parameters(net=net, from_bus=buses_dict['N0'], to_bus=buses_dict['N2'],
                                                 length_km=1, r_ohm_per_km=self.lines['B2'].resistance,
                                                 x_ohm_per_km=self.lines['B2'].reactance, c_nf_per_km=0, max_i_ka=1,
                                                 name='B2')}
        line_to_idx = {'B0': 0, 'B1': 1, 'B2': 2}

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

        power_from_main = self.solver.power_from_main(grid_solution=solution_dict)
        distribution_loss = self.solver.power_distribution_loss(grid_solution=solution_dict)

        solution_dict['power_from_main'] = {'real': np.real(power_from_main), 'imag': np.imag(power_from_main)}
        solution_dict['distribution_loss'] = {'real': distribution_loss, 'imag': 0}

        solution_dict_test = self.solver.solve(agents_state=agents_states)

        self.assertEqual(solution_dict, solution_dict_test, 'Solutions do not match')
