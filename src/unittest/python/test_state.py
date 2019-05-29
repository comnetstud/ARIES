import json
import unittest

import unittest_utils
from aries.core.grid import grid_utils
from aries.core.grid.state import State

STATE_TEST = 'state.json'
MODIFIED_STATE_TEST = 'modified_state.json'
GRID_ELEMENTS = 'grid_elements.json'
AGENT_NAME = "AGENT0"


class TestState(unittest.TestCase):
    """Tests for checking State and update state behaviour"""

    def setUp(self):
        with unittest_utils.readfile(STATE_TEST, __file__) as f:
            j = json.load(f)
            self.state = State(j)

    def test_if_all_properties_set(self):
        """Test if State is loaded from file"""
        unittest_utils.check_if_properties_is_set(self, "state", self.state)

    def test_if_properties_updated_or_not(self):
        """Test how update state update agent state"""
        with unittest_utils.readfile(GRID_ELEMENTS, __file__) as f:
            j = json.load(f)
            agents, lines = grid_utils.create_grid_elements(j)

        agent = agents[AGENT_NAME]
        self.assertIsNotNone(agent, "Agent is none")

        agent.update_state(self.state)

        self.assertEqual(agent.power_rating, self.state.power_rating, "agent.power_rating was not updated")
        self.assertEqual(agent.power_factor, self.state.power_factor, "agent.power_factor was not updated")
        self.assertEqual(agent.incoming_power, self.state.incoming_power, "agent.incoming_power was not updated")
        self.assertEqual(agent.request_inject_power, self.state.request_inject_power,
                         "agent.request_inject_power was not updated")
        self.assertEqual(agent.request_power_factor, self.state.request_power_factor,
                         "agent.request_power_factor was not updated")

        self.assertEqual(agent.battery.contribution_active, self.state.battery["contribution_active"],
                         "battery.contribution_active was not updated")
        self.assertEqual(agent.battery.contribution_reactive, self.state.battery["contribution_reactive"],
                         "battery.contribution_reactive was not updated")
        self.assertEqual(agent.battery.active, self.state.battery["active"], "battery.active was not updated")

        self.assertEqual(agent.electrical_vehicle.contribution_active,
                         self.state.electrical_vehicle["contribution_active"],
                         "electrical_vehicle.contribution_active was not updated")
        self.assertEqual(agent.electrical_vehicle.contribution_reactive,
                         self.state.electrical_vehicle["contribution_reactive"],
                         "electrical_vehicle.contribution_reactive was not updated")
        self.assertEqual(agent.electrical_vehicle.power_supplier, self.state.electrical_vehicle["power_supplier"],
                         "electrical_vehicle.power_supplier was not updated")
        self.assertEqual(agent.electrical_vehicle.active, self.state.electrical_vehicle["active"],
                         "electrical_vehicle.active was not updated")

        self.assertEqual(agent.pv_panel.solar_irradiance, self.state.pv_panel["solar_irradiance"],
                         "pv_panel.solar_irradiance was not updated")
        self.assertEqual(agent.pv_panel.heating_contribution, self.state.pv_panel["heating_contribution"],
                         "pv_panel.heating_contribution was not updated")
        self.assertEqual(agent.pv_panel.active, self.state.pv_panel["active"],
                         "pv_panel.active was not updated")

        self.assertEqual(agent.water_tank.active, self.state.water_tank["active"],
                         "water_tank.active was not updated")

        self.assertEqual(agent.wind_generator.wind_speed, self.state.wind_generator["wind_speed"],
                         "wind_generator.wind_speed was not updated")
        self.assertEqual(agent.wind_generator.active, self.state.wind_generator["active"],
                         "wind_generator.active was not updated")

    def test_if_some_state_is_missed(self):
        """Tests partial agent update"""
        with unittest_utils.readfile(MODIFIED_STATE_TEST, __file__) as f:
            j = json.load(f)
            modified_state = State(j)

        with unittest_utils.readfile(GRID_ELEMENTS, __file__) as f:
            j = json.load(f)
            agents, lines = grid_utils.create_grid_elements(j)

        agent = agents[AGENT_NAME]
        agent.update_state(modified_state)

        unittest_utils.check_if_properties_is_set(test=self, obj=agent, object_name="Agent")
