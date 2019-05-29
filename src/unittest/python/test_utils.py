import json
import unittest

import numpy as np

import unittest_utils
from aries.core.grid import grid_utils
from aries.core.grid.agent import Agent
from aries.simulation import simulation_utils

GRID_ELEMENTS_TEST_1 = 'grid_elements_test_1.json'
TOPOLOGY_1 = 'topology_1.json'


class TestSimulationUtils(unittest.TestCase):

    def test_impedance(self):
        self.assertEqual(simulation_utils.impedance(voltage_rating=230,
                                                    power_rating=None,
                                                    power_factor=1), None, "Impedance not None")

        voltage_rating = 230
        power_rating = 1000
        power_factor = 1
        rp = power_rating * np.tan(np.arccos(power_factor))
        s = np.complex(power_rating, rp)
        imp = np.conj(np.square(voltage_rating) / s)
        self.assertEqual(simulation_utils.impedance(voltage_rating=230,
                                                    power_rating=1000,
                                                    power_factor=1), imp, "Impedance does not match theoretical computation")

    def test_apparent_power(self):
        self.assertEqual(simulation_utils.apparent_power(power_rating=None,
                                                         power_factor=1), None, "Apparent power not None")

        self.assertEqual(simulation_utils.apparent_power(power_rating=1000,
                                                         power_factor=1), np.complex(1000, 0), "Apparent power not "
                                                                                               "Real")

    def test_reactive_power(self):
        self.assertEqual(simulation_utils.reactive_power(power_rating=None,
                                                         power_factor=1), None, "Reactive power not None")

        self.assertEqual(simulation_utils.reactive_power(power_rating=1000,
                                                         power_factor=1), 0, "Reactive power not 0 with power factor 1")

        self.assertEqual(simulation_utils.reactive_power(power_rating=1000,
                                                         power_factor=0.9),
                         1000 * np.tan(np.arccos(0.9)),
                         "Reactive power does not match theoretical computation")


class TestGridUtils(unittest.TestCase):
    def test_if_all_properties_set_in_grid_elements(self):
        """Test if read_grid_element from utils set all properties"""
        with unittest_utils.readfile(GRID_ELEMENTS_TEST_1, __file__) as f:
            j = json.load(f)
            agents, lines = grid_utils.create_grid_elements(j)

            self.assertEqual(len(agents), 1, "number of agents is not equal")

            agent = agents['AGENT1']
            unittest_utils.check_if_properties_is_set(self, "agent", agent)
            unittest_utils.check_if_properties_is_set(self, "battery", agent.battery)
            unittest_utils.check_if_properties_is_set(self, "pv_panel", agent.pv_panel)
            unittest_utils.check_if_properties_is_set(self, "wind_generator", agent.wind_generator)
            unittest_utils.check_if_properties_is_set(self, "electrical_vehicle", agent.electrical_vehicle)
            unittest_utils.check_if_properties_is_set(self, "water_tank", agent.water_tank)

            self.assertEqual(len(lines), 3, "number of lines is not equal")
            unittest_utils.check_if_properties_is_set(self, "line", lines['B0'])
            unittest_utils.check_if_properties_is_set(self, "line", lines['B1'])
            unittest_utils.check_if_properties_is_set(self, "line", lines['B2'])

    def test_if_object_is_valid_to_grid_elements_schema(self):
        """Test agent schema validation for agent"""
        with unittest_utils.readfile(GRID_ELEMENTS_TEST_1, __file__) as f:
            j = json.load(f)

            for name, item in j['agents'].items():
                item['name'] = name
                self.assertTrue(Agent.validate(item))

    def test_if_all_properties_set_in_topology(self):
        """Test if read_topology from utils set all properties"""
        with unittest_utils.readfile(TOPOLOGY_1, __file__) as f:
            j = json.load(f)
            paths, nodes = grid_utils.create_topology(j)

            self.assertEqual(len(paths), 2, "number of paths is not equal")
            self.assertEqual(len(nodes), 4, "number of nodes is not equal")

            node = nodes['N2']
            unittest_utils.check_if_properties_is_set(self, "node", node)

            path = paths['AGENT0']

            self.assertEqual(len(path.paths), 2, 'number of path is not equal')
            p = path.paths[0]
            self.assertEqual(p['active'], 1, 'path.active is not equal')
            self.assertEqual(p['path'], ['B0', 'B1'], 'path.active is not equal')
