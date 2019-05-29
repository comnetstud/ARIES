import json
import unittest

import unittest_utils
from aries.core.grid import grid_utils
from aries.core.grid.state import State
from aries.simulation import simulation

WATER_TANK_TEST_GRID_ELEMENTS = 'water_tank_test_grid_elements.json'
WATER_TANK_TEST_STATE_1 = 'water_tank_test_state_1.json'
WATER_TANK_TEST_STATE_2 = 'water_tank_test_state_2.json'


class TestWaterTank(unittest.TestCase):
    def setUp(self):
        with unittest_utils.readfile(WATER_TANK_TEST_GRID_ELEMENTS, __file__) as f:
            j = json.load(f)
            self.agents, _ = grid_utils.create_grid_elements(j)
        with unittest_utils.readfile(WATER_TANK_TEST_STATE_1, __file__) as f:
            j = json.load(f)
            self.state_1 = State(j)
        with unittest_utils.readfile(WATER_TANK_TEST_STATE_2, __file__) as f:
            j = json.load(f)
            self.state_2 = State(j)

    def test_water_tank(self):
        agent = self.agents['AGENT0']

        # TEST THAT THE WATER HEATS UP
        original_water_temp = agent.water_tank.temp
        capacity = agent.water_tank.capacity
        self.assertEqual(original_water_temp, 20, "Wrong initial temp")
        self.assertEqual(capacity, 100, "Wrong capacity")

        # TANK TEMP UPDATE RULE: temp += (power * 3.412 / (4 * capacity)) * time_scale

        agent.update_state(state=self.state_1)

        expected_pv_power = 4000
        expected_temp = original_water_temp + (expected_pv_power * 3.412 / (4 * capacity)) * 1
        name, imp, demand_power, inject_power, _, pv_power = simulation.process_simulation_step(agent=agent,
                                                                                                time_scale=1)
        self.assertEqual(name, "AGENT0", "Name mismatch")
        self.assertEqual(expected_pv_power, pv_power, "Pv Power mismatch")
        self.assertEqual(expected_temp, agent.water_tank.temp, "Water temperature mismatch")

        # TEST THAT THE BATTERY CHARGES AND THE WATER HEATS UP
        agent.water_tank.temp = 20
        original_water_temp = agent.water_tank.temp
        original_battery_status = agent.battery.status
        self.assertEqual(original_water_temp, 20, "Wrong initial temp")
        agent.update_state(state=self.state_2)
        expected_pv_power = 4000
        expected_temp = original_water_temp + (expected_pv_power/2 * 3.412 / (4 * capacity)) * 1
        expected_battery_status = original_battery_status + expected_pv_power / 2 * \
                                  agent.pv_panel.battery_coupling_efficiency / agent.battery.voltage
        name, imp, demand_power, inject_power, _, pv_power = simulation.process_simulation_step(agent=agent,
                                                                                                time_scale=1)
        self.assertEqual(name, "AGENT0", "Name mismatch")
        self.assertEqual(expected_pv_power, pv_power, "Pv Power mismatch")
        self.assertEqual(expected_temp, agent.water_tank.temp, "Water temperature mismatch")
        self.assertEqual(expected_battery_status, agent.battery.status, "Battery power mismatch")

        # TEST THAT THE BATTERY CHARGES WHILE THE WATER TANK STAYS AT 60 DEGREES
        agent.water_tank.temp = 60
        original_water_temp = agent.water_tank.temp
        original_battery_status = agent.battery.status
        self.assertEqual(original_water_temp, 60, "Wrong initial temp")
        agent.update_state(state=self.state_2)
        expected_pv_power = 4000
        expected_temp = 60
        expected_battery_status = original_battery_status + expected_pv_power / 2 * \
                                  agent.pv_panel.battery_coupling_efficiency / agent.battery.voltage
        name, imp, demand_power, inject_power, _, pv_power = simulation.process_simulation_step(agent=agent,
                                                                                                time_scale=1)
        self.assertEqual(name, "AGENT0", "Name mismatch")
        self.assertEqual(expected_pv_power, pv_power, "Pv Power mismatch")
        self.assertEqual(expected_temp, agent.water_tank.temp, "Water temperature mismatch")
        self.assertEqual(expected_battery_status, agent.battery.status, "Battery power mismatch")