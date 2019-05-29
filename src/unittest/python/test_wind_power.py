import json
import unittest

import unittest_utils
from aries.core.grid import grid_utils
from aries.core.grid.state import State
from aries.simulation import simulation

WIND_POWER_TEST_GRID_ELEMENTS = 'wind_power_test_grid_elements.json'
WIND_POWER_TEST_STATE_1 = 'wind_power_test_state_1.json'


class TestWindPower(unittest.TestCase):
    def setUp(self):
        with unittest_utils.readfile(WIND_POWER_TEST_GRID_ELEMENTS, __file__) as f:
            j = json.load(f)
            self.agents, _ = grid_utils.create_grid_elements(j)
        with unittest_utils.readfile(WIND_POWER_TEST_STATE_1, __file__) as f:
            j = json.load(f)
            self.state_1 = State(j)

    def test_wind_power(self):
        agent = self.agents['AGENT0']
        original_battery_status = agent.battery.status
        agent.update_state(state=self.state_1)
        name, imp, demand_power, inject_power, _, pv_power = simulation.process_simulation_step(agent=agent,
                                                                                                time_scale=1)
        air_density = agent.wind_generator.air_density
        power_coefficient = agent.wind_generator.power_coefficient
        area = agent.wind_generator.area
        wind_speed = agent.wind_generator.wind_speed
        expected_wind_power = (air_density * power_coefficient * area * wind_speed ** 3) / 2

        expected_battery_status = original_battery_status + expected_wind_power * \
                                  agent.wind_generator.battery_coupling_efficiency / agent.battery.voltage
        self.assertEqual(name, "AGENT0", "Name mismatch")
        self.assertEqual(expected_battery_status, agent.battery.status, "Battery status mismatch")
