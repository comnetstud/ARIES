import json
import numpy as np
import unittest

import unittest_utils
from aries.core.grid import grid_utils
from aries.core.grid.state import State
from aries.simulation import simulation_utils, simulation

INCOMING_POWER_TEST_GRID_ELEMENTS = 'incoming_power_test_grid_elements.json'
INCOMING_POWER_TEST_STATE_1 = 'incoming_power_test_state_1.json'


class TestProcessSimulationStep(unittest.TestCase):
    def setUp(self):
        with unittest_utils.readfile(INCOMING_POWER_TEST_GRID_ELEMENTS, __file__) as f:
            j = json.load(f)
            self.agents, _ = grid_utils.create_grid_elements(j)
        with unittest_utils.readfile(INCOMING_POWER_TEST_STATE_1, __file__) as f:
            j = json.load(f)
            self.state_1 = State(j)

    def test_process_simulation_step(self):
        agent = self.agents['AGENT0']
        initial_battery_status = agent.battery.status
        agent.update_state(state=self.state_1)
        name, imp, demand_power, inject_power, _, _ = simulation.process_simulation_step(agent=agent, time_scale=1)
        expected_battery_status = initial_battery_status + (((1500 - 1500 * 0.05) - 1000) / 24) * 1

        self.assertEqual(name, "AGENT0", "Name mismatch")
        self.assertEqual(np.real(demand_power), 1500 - 1500 * 0.05, "Real power demand mismatch")
        self.assertEqual(np.imag(demand_power), 0, "Imag power demand mismatch")
        self.assertEqual(agent.battery.status, expected_battery_status, "Battery status mismatch")

