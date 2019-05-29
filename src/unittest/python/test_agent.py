"""Test agent"""
import unittest

# from aries.core.grid.agent import Agent, Battery, ElectricalVehicle, PVPanel, WaterTank, WindGenerator
import aries.core.grid.agent as agent

# Agent constants
AGENT_NAME = "agent1"
VOLTAGE_RATING = 230
POWER_RATING = 1900
POWER_FACTOR = 0.95
INCOMING_POWER = 1234
REQUEST_INJECT_POWER = 123
REQUEST_POWER_FACTOR = 0.95

# Battery constants
VOLTAGE = 24
CAPACITY = 1296000
STATUS = 123414
CONTRIBUTION_ACTIVE = 0.5
CONTRIBUTION_REACTIVE = 0.3
INVERTER_INPUT_VOLTAGE = 24
INVERTER_OUTPUT_VOLTAGE = 230
INVERTER_EFFICIENCY = 0.87
ACTIVE = 0

# ElectricalVehicle constants
CONSUMPTION = 20
CHARGE_CURRENT = 123
POWER_SUPPLIER = 1

# PV panel constants
UNIT_AREA = 1
SERIES = 50
PARALLELS = 50
EFFICIENCY = 0.8
SOLAR_IRRADIANCE = 100
BATTERY_COUPLING_EFFICIENCY = 1
HEATING_CONTRIBUTION = 200

# Water tank properties
TEMP = 80
RESISTANCE = 50

# Wind generator properties
WIND_SPEED = 10
POWER_COEFFICIENT = 0.59
AIR_DENSITY = 1.225
AREA = 2


class TestAgent(unittest.TestCase):
    """Tests for agent"""

    def test_agent_assigned_properties(self):
        self.agent = agent.Agent.from_properties(name=AGENT_NAME, voltage_rating=VOLTAGE_RATING, power_rating=POWER_RATING,
                                                 power_factor=POWER_FACTOR, incoming_power=INCOMING_POWER,
                                                 request_inject_power=REQUEST_INJECT_POWER,
                                                 request_power_factor=REQUEST_POWER_FACTOR)
        self.assertEqual(self.agent.name, AGENT_NAME, "name is not equal")
        self.assertEqual(self.agent.voltage_rating, VOLTAGE_RATING, "voltage_rating is not equal")
        self.assertEqual(self.agent.power_rating, POWER_RATING, "power_rating is not equal")
        self.assertEqual(self.agent.power_factor, POWER_FACTOR, "power_factor is not equal")
        self.assertEqual(self.agent.incoming_power, INCOMING_POWER, "incoming_power is not equal")
        self.assertEqual(self.agent.request_inject_power, REQUEST_INJECT_POWER, "request_inject_power is not equal")
        self.assertEqual(self.agent.request_power_factor, REQUEST_POWER_FACTOR, "request_power_factor is not equal")

    def test_validation(self):
        """Tests agent validation"""
        j = {
            "name": "test",
            "voltage_rating": 123,
            "power_rating": 1,
            "power_factor": 1,
            "incoming_power": 1,
            "request_inject_power": 456,
            "request_power_factor": 0.95
        }

        self.assertTrue(agent.Agent.validate(j), "Agent is not valid")


class TestBattery(unittest.TestCase):
    """Tests for battery"""

    def setUp(self):
        self.battery = agent.Battery.from_properties(voltage=VOLTAGE, capacity=CAPACITY, status=STATUS,
                                                     contribution_active=CONTRIBUTION_ACTIVE,
                                                     contribution_reactive=CONTRIBUTION_REACTIVE,
                                                     inverter_input_voltage=INVERTER_INPUT_VOLTAGE,
                                                     inverter_output_voltage=INVERTER_OUTPUT_VOLTAGE,
                                                     inverter_efficiency=INVERTER_EFFICIENCY,
                                                     active=ACTIVE)

    def test_battery_assigned_properties(self):
        """Test if properties assigned correctly"""
        self.assertEqual(self.battery.voltage, VOLTAGE, "voltage is not equal")
        self.assertEqual(self.battery.capacity, CAPACITY, "capacity is not equal")
        self.assertEqual(self.battery.status, STATUS, "status is not equal")
        self.assertEqual(self.battery.contribution_active, CONTRIBUTION_ACTIVE, "contribution_active is not equal")
        self.assertEqual(self.battery.contribution_reactive, CONTRIBUTION_REACTIVE,
                         "contribution_reactive is not equal")
        self.assertEqual(self.battery.inverter_input_voltage, INVERTER_INPUT_VOLTAGE,
                         "inverter_input_voltage is not equal")
        self.assertEqual(self.battery.inverter_output_voltage, INVERTER_OUTPUT_VOLTAGE,
                         "inverter_output_voltage is not equal")
        self.assertEqual(self.battery.inverter_efficiency, INVERTER_EFFICIENCY, "inverter_efficiency is not equal")
        self.assertEqual(self.battery.active, ACTIVE, "active is not equal")


class TestElectricalVehicle(unittest.TestCase):
    """Tests for electrical vehicle"""

    def setUp(self):
        self.electrical_vehicle = agent.ElectricalVehicle.from_properties(voltage=VOLTAGE, capacity=CAPACITY,
                                                                          status=STATUS,
                                                                          consumption=CONSUMPTION,
                                                                          contribution_active=CONTRIBUTION_ACTIVE,
                                                                          contribution_reactive=CONTRIBUTION_REACTIVE,
                                                                          inverter_input_voltage=INVERTER_INPUT_VOLTAGE,
                                                                          inverter_output_voltage=INVERTER_OUTPUT_VOLTAGE,
                                                                          inverter_efficiency=INVERTER_EFFICIENCY,
                                                                          charge_current=CHARGE_CURRENT,
                                                                          power_supplier=POWER_SUPPLIER,
                                                                          active=ACTIVE)

    def test_electrical_vehicle_assigned_properties(self):
        """Test if properties assigned correctly"""
        self.assertEqual(self.electrical_vehicle.voltage, VOLTAGE, "voltage is not equal")
        self.assertEqual(self.electrical_vehicle.capacity, CAPACITY, "capacity is not equal")
        self.assertEqual(self.electrical_vehicle.status, STATUS, "status is not equal")
        self.assertEqual(self.electrical_vehicle.consumption, CONSUMPTION, "consumption is not equal")
        self.assertEqual(self.electrical_vehicle.contribution_active, CONTRIBUTION_ACTIVE,
                         "contribution_active is not equal")
        self.assertEqual(self.electrical_vehicle.contribution_reactive, CONTRIBUTION_REACTIVE,
                         "contribution_reactive is not equal")
        self.assertEqual(self.electrical_vehicle.inverter_input_voltage, INVERTER_INPUT_VOLTAGE,
                         "inverter_input_voltage is not equal")
        self.assertEqual(self.electrical_vehicle.inverter_output_voltage, INVERTER_OUTPUT_VOLTAGE,
                         "inverter_output_voltage is not equal")
        self.assertEqual(self.electrical_vehicle.inverter_efficiency, INVERTER_EFFICIENCY,
                         "inverter_efficiency is not equal")
        self.assertEqual(self.electrical_vehicle.charge_current, CHARGE_CURRENT, "charge_current is not equal")
        self.assertEqual(self.electrical_vehicle.power_supplier, POWER_SUPPLIER, "power_supplier is not equal")
        self.assertEqual(self.electrical_vehicle.active, ACTIVE, "active is not equal")


class TestPVPanel(unittest.TestCase):
    """Test for PV panel"""

    def setUp(self):
        self.pv_panel = agent.PVPanel.from_properties(unit_area=UNIT_AREA, series=SERIES, parallels=PARALLELS,
                                                      efficiency=EFFICIENCY,
                                                      solar_irradiance=SOLAR_IRRADIANCE,
                                                      battery_coupling_efficiency=BATTERY_COUPLING_EFFICIENCY,
                                                      heating_contribution=HEATING_CONTRIBUTION,
                                                      active=ACTIVE)

    def test_pv_panel_assigned_properties(self):
        """Test if properties assigned correctly"""
        self.assertEqual(self.pv_panel.series, SERIES, "series is not equal")
        self.assertEqual(self.pv_panel.parallels, PARALLELS, "parallels is not equal")
        self.assertEqual(self.pv_panel.efficiency, EFFICIENCY, "efficiency is not equal")
        self.assertEqual(self.pv_panel.solar_irradiance, SOLAR_IRRADIANCE, "solar_irradiance is not equal")
        self.assertEqual(self.pv_panel.heating_contribution, HEATING_CONTRIBUTION, "heating_contribution is not equal")
        self.assertEqual(self.pv_panel.active, ACTIVE, "active is not equal")


class TestWaterTank(unittest.TestCase):
    """Tests for water tank"""

    def setUp(self):
        self.water_tank = agent.WaterTank.from_properties(capacity=CAPACITY, temp=TEMP,
                                                          active=ACTIVE)

    def test_water_tank_assigned_properties(self):
        """Test if properties assigned correctly"""
        self.assertEqual(self.water_tank.capacity, CAPACITY, "capacity is not equal")
        self.assertEqual(self.water_tank.temp, TEMP, "temp is not equal")
        self.assertEqual(self.water_tank.active, ACTIVE, "active is not equal")


class TestWindGenerator(unittest.TestCase):
    """Tests for wind generator"""

    def setUp(self):
        self.wind_generator = agent.WindGenerator.from_properties(power_coefficient=POWER_COEFFICIENT,
                                                                  air_density=AIR_DENSITY, area=AREA, wind_speed=WIND_SPEED,
                                                                  battery_coupling_efficiency=BATTERY_COUPLING_EFFICIENCY,
                                                                  active=ACTIVE)

    def test_wind_generator_assigned_properties(self):
        """Test if properties assigned correctly"""
        self.assertEqual(self.wind_generator.power_coefficient, POWER_COEFFICIENT, "efficiency is not equal")
        self.assertEqual(self.wind_generator.air_density, AIR_DENSITY, "air_density is not equal")
        self.assertEqual(self.wind_generator.area, AREA, "area is not equal")
        self.assertEqual(self.wind_generator.wind_speed, WIND_SPEED, "wind_speed is not equal")
        self.assertEqual(self.wind_generator.active, ACTIVE, "active is not equal")
