import json
import unittest

import unittest_utils
from aries.core.grid import grid_utils
from aries.core.grid.state import State
from aries.simulation import simulation

PV_POWER_TEST_GRID_ELEMENTS = 'pv_power_test_grid_elements.json'
PV_POWER_TEST_STATE_1 = 'pv_power_test_state_1.json'


class TestPvPower(unittest.TestCase):
    def setUp(self):
        with unittest_utils.readfile(PV_POWER_TEST_GRID_ELEMENTS, __file__) as f:
            j = json.load(f)
            self.agents, _ = grid_utils.create_grid_elements(j)
        with unittest_utils.readfile(PV_POWER_TEST_STATE_1, __file__) as f:
            j = json.load(f)
            self.state_1 = State(j)

    def test_pv_power(self):
        agent = self.agents['AGENT0']
        original_battery_status = agent.battery.status
        agent.update_state(state=self.state_1)
        name, imp, demand_power, inject_power, _, pv_power = simulation.process_simulation_step(agent=agent,
                                                                                                time_scale=1)

        expected_pv_power = 4000

        expected_battery_status = original_battery_status + expected_pv_power * \
                                  agent.pv_panel.battery_coupling_efficiency / agent.battery.voltage
        self.assertEqual(name, "AGENT0", "Name mismatch")
        self.assertEqual(expected_pv_power, pv_power, "Pv Power mismatch")
        self.assertEqual(expected_battery_status, agent.battery.status, "Battery power mismatch")
