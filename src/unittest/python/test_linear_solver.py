import json
import unittest

import numpy as np

import unittest_utils
from aries.core.grid import grid_utils
from aries.simulation import simulation_utils
from aries.simulation.solver.linear_solver import LinearSolver

SOLVER_TEST_GRID_ELEMENTS_1 = 'solver_test_grid_elements_1.json'
SOLVER_TEST_GRID_ELEMENTS_2 = 'solver_test_grid_elements_2.json'
SOLVER_TEST_TOPOLOGY_1 = 'solver_test_topology_1.json'


class TestLinearSolver(unittest.TestCase):
    def setUp(self):
        with unittest_utils.readfile(SOLVER_TEST_GRID_ELEMENTS_1, __file__) as f:
            j = json.load(f)
            agents, lines = grid_utils.create_grid_elements(j)
            self.agents_1 = agents
            self.lines_1 = lines

        with unittest_utils.readfile(SOLVER_TEST_GRID_ELEMENTS_2, __file__) as f:
            j = json.load(f)
            agents, lines = grid_utils.create_grid_elements(j)
            self.agents_2 = agents
            self.lines_2 = lines

        with unittest_utils.readfile(SOLVER_TEST_TOPOLOGY_1, __file__) as f:
            j = json.load(f)
            paths, nodes = grid_utils.create_topology(j)

        self.solver1 = LinearSolver(paths=paths, nodes=nodes, lines=self.lines_1)
        self.solver2 = LinearSolver(paths=paths, nodes=nodes, lines=self.lines_2)

    def test_solver(self):
        line0_imp_1 = np.complex(self.lines_1['B0'].resistance, self.lines_1['B0'].reactance)
        line1_imp_1 = np.complex(self.lines_1['B1'].resistance, self.lines_1['B1'].reactance)
        line2_imp_1 = np.complex(self.lines_1['B2'].resistance, self.lines_1['B2'].reactance)

        agents_states_1 = {a: {
            'impedance': {
                'resistance': np.real(simulation_utils.impedance(voltage_rating=self.agents_1[a].voltage_rating,
                                                                 power_rating=self.agents_1[a].power_rating,
                                                                 power_factor=self.agents_1[a].power_factor)),
                'reactance': np.imag(simulation_utils.impedance(voltage_rating=self.agents_1[a].voltage_rating,
                                                                power_rating=self.agents_1[a].power_rating,
                                                                power_factor=self.agents_1[a].power_factor))},
            'inject_power': {'active_power': 0, 'reactive_power': 0},
            'demand_power': {'active_power': 1000, 'reactive_power': 0},
            'battery_power': {'active_power': 0, 'reactive_power': 0}} for a in self.agents_1.keys()}

        b_1 = np.array([2 * 1000 / 230, 1000 / 230, 1000 / 230], dtype=np.complex)
        drops = np.array([line0_imp_1, line1_imp_1, line2_imp_1]) * b_1
        voltages = np.array([230 - (drops[0] + drops[1]), 230 - (drops[0] + drops[2])])
        agents_currents = np.array([np.conj(1000 / voltages[0]), np.conj(1000 / voltages[1])])

        solution_1 = np.array(
            [np.sum(agents_currents), agents_currents[0], agents_currents[1], agents_currents[0], agents_currents[1]])

        tmp_names = ['B0', 'B1', 'B2', 'AGENT0', 'AGENT1']
        solution_1 = {name: {'real': np.real(i), 'imag': np.imag(i)} for name, i in zip(tmp_names, solution_1)}

        power_from_main = self.solver1.power_from_main(grid_solution=solution_1)
        distribution_loss = self.solver1.power_distribution_loss(grid_solution=solution_1)

        solution_1['power_from_main'] = {'real': np.real(power_from_main), 'imag': np.imag(power_from_main)}
        solution_1['distribution_loss'] = {'real': distribution_loss, 'imag': 0}

        solution_dict_1 = self.solver1.solve(agents_states_1)

        self.assertEqual(np.around(solution_1['B0']['real'], 3), np.around(solution_dict_1['B0']['real'], 3),
                         'Solution 1 for B0 does not match (real part)')
        self.assertEqual(np.around(solution_1['B0']['imag'], 3), np.around(solution_dict_1['B0']['imag'], 3),
                         'Solution 1 for B0 does not match (imag part)')
        self.assertEqual(np.around(solution_1['B1']['real'], 3), np.around(solution_dict_1['B1']['real'], 3),
                         'Solution 1 for B1 does not match (real part)')
        self.assertEqual(np.around(solution_1['B1']['imag'], 3), np.around(solution_dict_1['B1']['imag'], 3),
                         'Solution 1 for B1 does not match (imag part)')
        self.assertEqual(np.around(solution_1['B2']['real'], 3), np.around(solution_dict_1['B2']['real'], 3),
                         'Solution 1 for B2 does not match (real part)')
        self.assertEqual(np.around(solution_1['B2']['imag'], 3), np.around(solution_dict_1['B2']['imag'], 3),
                         'Solution 1 for B2 does not match (imag part)')

        self.assertEqual(np.around(solution_1['AGENT0']['real'], 3), np.around(solution_dict_1['AGENT0']['real'], 3),
                         'Solution 1 for AGENT0 does not match (real part)')
        self.assertEqual(np.around(solution_1['AGENT0']['imag'], 3), np.around(solution_dict_1['AGENT0']['imag'], 3),
                         'Solution 1 for AGENT0 does not match (imag part)')
        self.assertEqual(np.around(solution_1['AGENT1']['real'], 3), np.around(solution_dict_1['AGENT1']['real'], 3),
                         'Solution 1 for AGENT1 does not match (real part)')
        self.assertEqual(np.around(solution_1['AGENT1']['imag'], 3), np.around(solution_dict_1['AGENT1']['imag'], 3),
                         'Solution 1 for AGENT1 does not match (imag part)')

        self.assertEqual(np.around(solution_1['power_from_main']['real'], 3),
                         np.around(solution_dict_1['power_from_main']['real'], 3),
                         'Solution 1 for power_from_main does not match (real part)')
        self.assertEqual(np.around(solution_1['power_from_main']['imag'], 3),
                         np.around(solution_dict_1['power_from_main']['imag'], 3),
                         'Solution 1 for power_from_main does not match (imag part)')

        self.assertEqual(np.around(solution_1['distribution_loss']['real'], 3),
                         np.around(solution_dict_1['distribution_loss']['real'], 3),
                         'Solution 1 for distribution_loss does not match (real part)')
        self.assertEqual(np.around(solution_1['distribution_loss']['imag'], 3),
                         np.around(solution_dict_1['distribution_loss']['imag'], 3),
                         'Solution 1 for distribution_loss does not match (imag part)')

        line0_imp_2 = np.complex(self.lines_2['B0'].resistance, self.lines_2['B0'].reactance)
        line1_imp_2 = np.complex(self.lines_2['B1'].resistance, self.lines_2['B1'].reactance)
        line2_imp_2 = np.complex(self.lines_2['B2'].resistance, self.lines_2['B2'].reactance)

        agents_states_2 = {
            'AGENT0': {
                'impedance': {
                    'resistance': np.real(simulation_utils.impedance(voltage_rating=self.agents_2['AGENT0'].voltage_rating,
                                                                     power_rating=self.agents_2['AGENT0'].power_rating,
                                                                     power_factor=self.agents_2['AGENT0'].power_factor)),
                    'reactance': np.imag(simulation_utils.impedance(voltage_rating=self.agents_2['AGENT0'].voltage_rating,
                                                                    power_rating=self.agents_2['AGENT0'].power_rating,
                                                                    power_factor=self.agents_2['AGENT0'].power_factor))},
                'inject_power': {'active_power': 0, 'reactive_power': 0},
                'demand_power': {'active_power': 0, 'reactive_power': 0},
                'battery_power': {'active_power': 0, 'reactive_power': 0}
            },
            'AGENT1': {
                'impedance': {
                    'resistance': np.real(
                        simulation_utils.impedance(voltage_rating=self.agents_2['AGENT1'].voltage_rating,
                                                   power_rating=self.agents_2['AGENT1'].power_rating,
                                                   power_factor=self.agents_2['AGENT1'].power_factor)),
                    'reactance': np.imag(
                        simulation_utils.impedance(voltage_rating=self.agents_2['AGENT1'].voltage_rating,
                                                   power_rating=self.agents_2['AGENT1'].power_rating,
                                                   power_factor=self.agents_2['AGENT1'].power_factor))},
                'inject_power': {'active_power': 0, 'reactive_power': 0},
                'demand_power': {'active_power': 1500, 'reactive_power': 1500 * np.tan(np.arccos(0.95))},
                'battery_power': {'active_power': 0, 'reactive_power': 0}
            },
        }

        ap = 1500
        rp = 1500 * np.tan(np.arccos(0.95))
        pq = np.complex(ap, rp)
        b_2 = np.array([np.conj(pq / 230), np.conj(0 / 230), np.conj(pq / 230)], dtype=np.complex)

        drops = np.array([line0_imp_2, line1_imp_2, line2_imp_2], dtype=np.complex) * b_2
        voltages = np.real(np.array([230 - (drops[0] + drops[1]), 230 - (drops[0] + drops[2])]))
        agents_currents = np.array([np.conj(0 / voltages[0]), np.conj(pq / voltages[1])])

        solution_2 = np.array(
            [np.sum(agents_currents), agents_currents[0], agents_currents[1], agents_currents[0], agents_currents[1]])

        tmp_names = ['B0', 'B1', 'B2', 'AGENT0', 'AGENT1']
        solution_2 = {name: {'real': np.real(i), 'imag': np.imag(i)} for name, i in zip(tmp_names, solution_2)}

        power_from_main = self.solver2.power_from_main(grid_solution=solution_2)
        distribution_loss = self.solver2.power_distribution_loss(grid_solution=solution_2)

        solution_2['power_from_main'] = {'real': np.real(power_from_main), 'imag': np.imag(power_from_main)}
        solution_2['distribution_loss'] = {'real': distribution_loss, 'imag': 0}

        solution_dict_2 = self.solver2.solve(agents_states_2)
        self.assertEqual(np.around(solution_2['B0']['real'], 3), np.around(solution_dict_2['B0']['real'], 3),
                         'Solution 2 for B0 does not match (real part)')
        self.assertEqual(np.around(solution_2['B0']['imag'], 3), np.around(solution_dict_2['B0']['imag'], 3),
                         'Solution 2 for B0 does not match (imag part)')
        self.assertEqual(np.around(solution_2['B1']['real'], 3), np.around(solution_dict_2['B1']['real'], 3),
                         'Solution 2 for B1 does not match (real part)')
        self.assertEqual(np.around(solution_2['B1']['imag'], 3), np.around(solution_dict_2['B1']['imag'], 3),
                         'Solution 2 for B1 does not match (imag part)')
        self.assertEqual(np.around(solution_2['B2']['real'], 3), np.around(solution_dict_2['B2']['real'], 3),
                         'Solution 2 for B2 does not match (real part)')
        self.assertEqual(np.around(solution_2['B2']['imag'], 3), np.around(solution_dict_2['B2']['imag'], 3),
                         'Solution 2 for B2 does not match (imag part)')

        self.assertEqual(np.around(solution_2['AGENT0']['real'], 3), np.around(solution_dict_2['AGENT0']['real'], 3),
                         'Solution 2 for AGENT0 does not match (real part)')
        self.assertEqual(np.around(solution_2['AGENT0']['imag'], 3), np.around(solution_dict_2['AGENT0']['imag'], 3),
                         'Solution 2 for AGENT0 does not match (imag part)')
        self.assertEqual(np.around(solution_2['AGENT1']['real'], 3), np.around(solution_dict_2['AGENT1']['real'], 3),
                         'Solution 2 for AGENT1 does not match (real part)')
        self.assertEqual(np.around(solution_2['AGENT1']['imag'], 3), np.around(solution_dict_2['AGENT1']['imag'], 3),
                         'Solution 2 for AGENT1 does not match (imag part)')

        self.assertEqual(np.around(solution_2['power_from_main']['real'], 3),
                         np.around(solution_dict_2['power_from_main']['real'], 3),
                         'Solution 2 for power_from_main does not match (real part)')
        self.assertEqual(np.around(solution_2['power_from_main']['imag'], 3),
                         np.around(solution_dict_2['power_from_main']['imag'], 3),
                         'Solution 2 for power_from_main does not match (imag part)')

        self.assertEqual(np.around(solution_2['distribution_loss']['real'], 3),
                         np.around(solution_dict_2['distribution_loss']['real'], 3),
                         'Solution 2 for distribution_loss does not match (real part)')
        self.assertEqual(np.around(solution_2['distribution_loss']['imag'], 3),
                         np.around(solution_dict_2['distribution_loss']['imag'], 3),
                         'Solution 2 for distribution_loss does not match (imag part)')