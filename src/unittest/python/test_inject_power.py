import json
import unittest

import numpy as np

import unittest_utils
from aries.core.grid import grid_utils
from aries.simulation import simulation_utils
from aries.simulation.solver.linear_solver import LinearSolver

INJECT_POWER_TEST_GRID_ELEMENTS = 'inject_power_test_grid_elements.json'
INJECT_POWER_TEST_TOPOLOGY = 'inject_power_test_topology.json'


class TestInjectPower(unittest.TestCase):
    def setUp(self):
        with unittest_utils.readfile(INJECT_POWER_TEST_GRID_ELEMENTS, __file__) as f:
            j = json.load(f)
            agents, lines = grid_utils.create_grid_elements(j)
            self.agents = agents
            self.lines = lines

        with unittest_utils.readfile(INJECT_POWER_TEST_TOPOLOGY, __file__) as f:
            j = json.load(f)
            paths, nodes = grid_utils.create_topology(j)

        self.solver = LinearSolver(paths=paths, nodes=nodes, lines=self.lines)

    def test_solver(self):
        line0_imp = np.complex(self.lines['B0'].resistance, self.lines['B0'].reactance)
        line1_imp = np.complex(self.lines['B1'].resistance, self.lines['B1'].reactance)
        line2_imp = np.complex(self.lines['B2'].resistance, self.lines['B2'].reactance)

        agents_states = {
            'AGENT0': {
                'impedance': {
                    'resistance': np.real(simulation_utils.impedance(voltage_rating=self.agents['AGENT0'].voltage_rating,
                                                                     power_rating=self.agents['AGENT0'].power_rating,
                                                                     power_factor=self.agents['AGENT0'].power_factor)),
                    'reactance': np.imag(simulation_utils.impedance(voltage_rating=self.agents['AGENT0'].voltage_rating,
                                                                    power_rating=self.agents['AGENT0'].power_rating,
                                                                    power_factor=self.agents['AGENT0'].power_factor))},
                'inject_power': {'active_power': 500, 'reactive_power': 0},
                'demand_power': {'active_power': 1000, 'reactive_power': 0},
                'battery_power': {'active_power': 0, 'reactive_power': 0}},
            'AGENT1': {
                'impedance': {
                    'resistance': np.real(simulation_utils.impedance(voltage_rating=self.agents['AGENT1'].voltage_rating,
                                                                     power_rating=self.agents['AGENT1'].power_rating,
                                                                     power_factor=self.agents['AGENT1'].power_factor)),
                    'reactance': np.imag(simulation_utils.impedance(voltage_rating=self.agents['AGENT1'].voltage_rating,
                                                                    power_rating=self.agents['AGENT1'].power_rating,
                                                                    power_factor=self.agents['AGENT1'].power_factor))},
                'inject_power': {'active_power': 1500, 'reactive_power': 0},
                'demand_power': {'active_power': 1000, 'reactive_power': 0},
                'battery_power': {'active_power': 0, 'reactive_power': 0}},
        }

        b = np.array([0 / 230, 500 / 230, (-500) / 230], dtype=np.complex)
        drops = np.array([line0_imp, line1_imp, line2_imp]) * b
        voltages = np.array([230 - (drops[0] + drops[1]), 230])
        agents_currents = np.array([np.conj(500 / voltages[0]), np.conj(-500 / voltages[1])])

        solution = np.array(
            [np.sum(agents_currents), agents_currents[0], agents_currents[1], agents_currents[0], agents_currents[1]])

        tmp_names = ['B0', 'B1', 'B2', 'AGENT0', 'AGENT1']
        solution = {name: {'real': np.real(i), 'imag': np.imag(i)} for name, i in zip(tmp_names, solution)}

        power_from_main = self.solver.power_from_main(grid_solution=solution)
        distribution_loss = self.solver.power_distribution_loss(grid_solution=solution)

        solution['power_from_main'] = {'real': np.real(power_from_main), 'imag': np.imag(power_from_main)}
        solution['distribution_loss'] = {'real': distribution_loss, 'imag': 0}

        solution_dict = self.solver.solve(agents_states)
        self.assertEqual(np.around(solution['B0']['real'], 3), np.around(solution_dict['B0']['real'], 3),
                         'Solution 1 for B0 does not match (real part)')
        self.assertEqual(np.around(solution['B0']['imag'], 3), np.around(solution_dict['B0']['imag'], 3),
                         'Solution 1 for B0 does not match (imag part)')
        self.assertEqual(np.around(solution['B1']['real'], 3), np.around(solution_dict['B1']['real'], 3),
                         'Solution 1 for B1 does not match (real part)')
        self.assertEqual(np.around(solution['B1']['imag'], 3), np.around(solution_dict['B1']['imag'], 3),
                         'Solution 1 for B1 does not match (imag part)')
        self.assertEqual(np.around(solution['B2']['real'], 3), np.around(solution_dict['B2']['real'], 3),
                         'Solution 1 for B2 does not match (real part)')
        self.assertEqual(np.around(solution['B2']['imag'], 3), np.around(solution_dict['B2']['imag'], 3),
                         'Solution 1 for B2 does not match (imag part)')

        self.assertEqual(np.around(solution['AGENT0']['real'], 3), np.around(solution_dict['AGENT0']['real'], 3),
                         'Solution 1 for AGENT0 does not match (real part)')
        self.assertEqual(np.around(solution['AGENT0']['imag'], 3), np.around(solution_dict['AGENT0']['imag'], 3),
                         'Solution 1 AGENT0 does not match (imag part)')
        self.assertEqual(np.around(solution['AGENT1']['real'], 3), np.around(solution_dict['AGENT1']['real'], 3),
                         'Solution 1 for AGENT1 does not match (real part)')
        self.assertEqual(np.around(solution['AGENT1']['imag'], 3), np.around(solution_dict['AGENT1']['imag'], 3),
                         'Solution 1 for AGENT1 does not match (imag part)')

        self.assertEqual(np.around(solution['power_from_main']['real'], 3),
                         np.around(solution_dict['power_from_main']['real'], 3),
                         'Solution 1 for power_from_main does not match (real part)')
        self.assertEqual(np.around(solution['power_from_main']['imag'], 3),
                         np.around(solution_dict['power_from_main']['imag'], 3),
                         'Solution 1 for power_from_main does not match (imag part)')

        self.assertEqual(np.around(solution['distribution_loss']['real'], 3),
                         np.around(solution_dict['distribution_loss']['real'], 3),
                         'Solution 1 for distribution_loss does not match (real part)')
        self.assertEqual(np.around(solution['distribution_loss']['imag'], 3),
                         np.around(solution_dict['distribution_loss']['imag'], 3),
                         'Solution 1 for distribution_loss does not match (imag part)')
