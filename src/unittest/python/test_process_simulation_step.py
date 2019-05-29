import json
import unittest

import unittest_utils
from aries.core.grid import grid_utils
from aries.core.grid.state import State
from aries.simulation import simulation_utils, simulation

PROCESS_SIMULATION_STEP_TEST_GRID_ELEMENTS = 'process_simulation_step_test_grid_elements.json'
PROCESS_SIMULATION_STEP_TEST_STATE_1 = 'process_simulation_step_test_state_1.json'


class TestProcessSimulationStep(unittest.TestCase):
    def setUp(self):
        with unittest_utils.readfile(PROCESS_SIMULATION_STEP_TEST_GRID_ELEMENTS, __file__) as f:
            j = json.load(f)
            self.agents, _ = grid_utils.create_grid_elements(j)
        with unittest_utils.readfile(PROCESS_SIMULATION_STEP_TEST_STATE_1, __file__) as f:
            j = json.load(f)
            self.state_1 = State(j)

    def test_process_simulation_step(self):
        agent = self.agents['AGENT0']
        agent.update_state(state=self.state_1)
        name, imp, demand_power, inject_power, _, _ = simulation.process_simulation_step(agent=agent, time_scale=1)
        expected_power_rating = 1000
        expected_power_factor = 1

        expected_battery_active = 1
        expected_battery_contribution_active = 0.5
        expected_battery_contribution_reactive = 0
        expected_battery_status = 1296000 - ((1000 / 2) / 24 / 0.87) * 1

        expected_electrical_vehicle_active = 1
        expected_electrical_vehicle_power_supplier = 0
        expected_electrical_vehicle_status = 1296000
        expected_impedance = simulation_utils.impedance(230, 1190, 1)
        # the battery by design works only on the rated power, not the total power that is influenced by the EV and the
        # possible incoming power
        self.assertEqual(name, "AGENT0", "Name mismatch")
        self.assertEqual(expected_impedance, imp, "Impedance mismatch")
        self.assertEqual(expected_power_rating, agent.power_rating, "power rating mismatch")
        self.assertEqual(expected_power_factor, agent.power_factor, "power factor mismatch")
        self.assertEqual(expected_battery_active, agent.battery.active, "Battery activity mismatch")
        self.assertEqual(expected_battery_contribution_active, agent.battery.contribution_active,
                         "Battery contribution to active power mismatch")
        self.assertEqual(expected_battery_contribution_reactive, agent.battery.contribution_reactive,
                         "Battery contribution to reactive power mismatch")
        self.assertEqual(expected_battery_status, agent.battery.status, "Battery status mismatch")
        self.assertEqual(expected_electrical_vehicle_active, agent.electrical_vehicle.active, "EV activity mismatch")
        self.assertEqual(expected_electrical_vehicle_power_supplier, agent.electrical_vehicle.power_supplier,
                         "EV configuration mismatch")
        self.assertEqual(expected_electrical_vehicle_status, agent.electrical_vehicle.capacity,
                         "EV battery capacity mismatch")
