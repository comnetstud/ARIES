"""Provide Agent (Battery, PVPanel, etc.) classes for simulation"""

import json

import cerberus
from bson import json_util

import aries.core.utils as utils

# Schema for agent validation
agent_schema = {
    'name': {'type': 'string', 'required': False, 'empty': False},
    'voltage_rating': {'type': 'float', 'required': True},
    'power_rating': {'type': 'float', 'required': True},
    'power_factor': {'type': 'float', 'required': True},
    'incoming_power': {'type': 'float', 'required': True},
    'request_inject_power': {'type': 'float', 'required': True},
    'request_power_factor': {'type': 'float', 'required': True},

    'battery': {
        'type': 'dict',
        'schema': {
            'voltage': {'type': 'integer', 'required': True},
            'capacity': {'type': 'integer', 'required': True},
            'status': {'type': 'float', 'required': True},
            'contribution_active': {'type': 'float', 'min': 0, 'max': 1, 'required': True},  # 0-1
            'contribution_reactive': {'type': 'float', 'min': 0, 'max': 1, 'required': True},  # 0-1
            'inverter_input_voltage': {'type': 'float', 'required': True},
            'inverter_output_voltage': {'type': 'float', 'required': True},
            'inverter_efficiency': {'type': 'float', 'min': 0, 'max': 1, 'required': True},  # 0-1
            'active': {'type': 'integer', 'min': 0, 'max': 1, 'required': True}  # 0,1
        }
    },
    'pv_panel': {
        'type': 'dict',
        'schema': {
            'unit_area': {'type': 'float', 'required': True},
            'series': {'type': 'float', 'required': True},
            'parallels': {'type': 'float', 'required': True},
            'efficiency': {'type': 'float', 'required': True},
            'solar_irradiance': {'type': 'float', 'required': True},
            'battery_coupling_efficiency': {'type': 'float', 'required': True},
            'heating_contribution': {'type': 'float', 'required': True},
            'active': {'type': 'integer', 'min': 0, 'max': 1, 'required': True}
        }
    },
    'wind_generator': {
        'type': 'dict',
        'schema': {
            'power_coefficient': {'type': 'float', 'required': True},
            'air_density': {'type': 'float', 'required': True},
            'area': {'type': 'float', 'required': True},
            'wind_speed': {'type': 'float', 'required': True},
            'battery_coupling_efficiency': {'type': 'float', 'required': True},
            'active': {'type': 'integer', 'min': 0, 'max': 1, 'required': True}
        }
    },
    'electrical_vehicle': {
        'type': 'dict',
        'schema': {
            'voltage': {'type': 'integer', 'required': True},
            'capacity': {'type': 'integer', 'required': True},
            'status': {'type': 'float', 'required': True},
            'consumption': {'type': 'float', 'required': True},
            'contribution_active': {'type': 'float', 'min': 0, 'max': 1, 'required': True},
            'contribution_reactive': {'type': 'float', 'min': 0, 'max': 1, 'required': True},
            'inverter_input_voltage': {'type': 'float', 'required': True},
            'inverter_output_voltage': {'type': 'float', 'required': True},
            'inverter_efficiency': {'type': 'float', 'min': 0, 'max': 1, 'required': True},
            'charge_current': {'type': 'float', 'required': True},
            'power_supplier': {'type': 'float', 'min': 0, 'max': 1, 'required': True},  # 0,1
            'active': {'type': 'integer', 'min': 0, 'max': 1, 'required': True}
        }
    },
    'water_tank': {
        'type': 'dict',
        'schema': {
            'capacity': {'type': 'float', 'required': True},
            'temp': {'type': 'float', 'required': True},
            'active': {'type': 'integer', 'min': 0, 'max': 1, 'required': True}
        }
    }
}

agent_validator = cerberus.Validator(agent_schema)


class Agent(object):
    """Representation of Agent in simulation process"""
    name = None
    voltage_rating = None
    power_rating = None
    power_factor = None

    incoming_power = None
    request_inject_power = None
    request_power_factor = None

    battery = None
    pv_panel = None
    wind_generator = None
    electrical_vehicle = None
    water_tank = None

    def __init__(self, params_dict):
        """Initialization from dictionary"""
        self.__dict__ = params_dict

    @classmethod
    def from_properties(cls, name, voltage_rating, power_rating, power_factor, incoming_power, request_inject_power,
                        request_power_factor):
        """Initialization from parameters"""
        return cls({"name": name,
                    "voltage_rating": voltage_rating,
                    "power_rating": power_rating,
                    "power_factor": power_factor,
                    "incoming_power": incoming_power,
                    "request_inject_power": request_inject_power,
                    "request_power_factor": request_power_factor})

    @classmethod
    def load(cls, name, j):
        """Create Agent object from json"""
        Agent.validate(j)
        agent = cls.from_properties(name=name, voltage_rating=j['voltage_rating'],
                                    power_rating=j['power_rating'], power_factor=j['power_factor'],
                                    incoming_power=j['incoming_power'], request_inject_power=j["request_inject_power"],
                                    request_power_factor=j["request_power_factor"])

        battery = Battery(j['battery'])
        agent.battery = battery

        pv_panel = PVPanel(j['pv_panel'])
        agent.pv_panel = pv_panel

        wind_generator = WindGenerator(j['wind_generator'])
        agent.wind_generator = wind_generator

        electrical_vehicle = ElectricalVehicle(j['electrical_vehicle'])
        agent.electrical_vehicle = electrical_vehicle

        water_tank = WaterTank(j['water_tank'])
        agent.water_tank = water_tank

        return agent

    def dump(self):
        """Dump object to json string"""
        return json_util.dumps(self, cls=AgentEncoder)

    def update_state(self, state):
        """Update state of agent from State object"""
        if state.power_factor is not None:
            self.power_factor = state.power_factor
        if state.power_rating is not None:
            self.power_rating = state.power_rating
        if state.incoming_power is not None:
            self.incoming_power = state.incoming_power
        if state.request_inject_power is not None:
            self.request_inject_power = state.request_inject_power
        if state.request_power_factor is not None:
            self.request_power_factor = state.request_power_factor

        if state.electrical_vehicle is not None:
            self.electrical_vehicle.update_state(state.electrical_vehicle)
        if state.battery is not None:
            self.battery.update_state(state.battery)
        if state.pv_panel is not None:
            self.pv_panel.update_state(state.pv_panel)
        if state.water_tank is not None:
            self.water_tank.update_state(state.water_tank)
        if state.wind_generator is not None:
            self.wind_generator.update_state(state.wind_generator)

    @staticmethod
    def validate(data):
        """Validate object according to agent_schema"""
        return utils.validate(data, 'Agent', agent_validator)


class GridElement(object):
    """Base class for all grid elements withing Agent"""
    active = None

    def __init__(self, params_dict):
        """Initialization from dictionary"""
        self.__dict__ = params_dict

    def is_active(self):
        """Check if grid element is active or not"""
        return self.active == 1

    def update_state(self, state):
        """Update grid element state"""
        if 'active' in state:
            self.active = state['active']


class EnergyBuffer(GridElement):
    """Base class for battery-like classes"""
    voltage = None
    capacity = None
    status = None
    contribution_active = None
    contribution_reactive = None
    inverter_input_voltage = None
    inverter_output_voltage = None
    inverter_efficiency = None

    def erogate(self, power, time_scale):
        """Erogate power from energy buffer"""
        required_amps = (power / self.voltage / self.inverter_efficiency) * time_scale
        if self.status >= required_amps:
            self.status -= required_amps
            return True
        return False

    def charge(self, current, time_scale):
        """Charge energy buffer from current"""
        total_coulombs = current * time_scale
        if self.status + total_coulombs <= self.capacity:
            self.status += total_coulombs
            return 0

        energy_left = total_coulombs - (self.capacity - self.status)
        self.status = self.capacity
        return energy_left

    def update_state(self, energy_buffer_state):
        """Update energy buffer state"""
        super().update_state(energy_buffer_state)
        if 'status' in energy_buffer_state:
            self.status = energy_buffer_state['status']
        if 'contribution_active' in energy_buffer_state:
            self.contribution_active = energy_buffer_state['contribution_active']
        if 'contribution_reactive' in energy_buffer_state:
            self.contribution_reactive = energy_buffer_state['contribution_reactive']


class Battery(EnergyBuffer):
    """Representation of battery in simulation process"""

    @classmethod
    def from_properties(cls, voltage, capacity, status, contribution_active, contribution_reactive,
                        inverter_input_voltage, inverter_output_voltage, inverter_efficiency, active):
        """Initialization from parameters"""
        return cls({
            "voltage": voltage, "capacity": capacity, "status": status, "contribution_active": contribution_active,
            "contribution_reactive": contribution_reactive, "inverter_input_voltage": inverter_input_voltage,
            "inverter_output_voltage": inverter_output_voltage, "inverter_efficiency": inverter_efficiency,
            "active": active})

    def update_state(self, battery_state):
        """Update battery state"""
        super().update_state(battery_state)


class ElectricalVehicle(EnergyBuffer):
    """Representation of electrical vehicle in simulation process"""
    consumption = None
    charge_current = None  # some constant model dependent
    power_supplier = None  # 0 or 1

    @classmethod
    def from_properties(cls, voltage, capacity, status, consumption, contribution_active, contribution_reactive,
                        inverter_input_voltage, inverter_output_voltage, inverter_efficiency, charge_current,
                        power_supplier, active):
        """Initialization from parameters"""
        return cls({
            "voltage": voltage, "capacity": capacity, "status": status, "consumption": consumption,
            "contribution_active": contribution_active,
            "contribution_reactive": contribution_reactive,
            "inverter_input_voltage": inverter_input_voltage,
            "inverter_output_voltage": inverter_output_voltage,
            "inverter_efficiency": inverter_efficiency,
            "charge_current": charge_current,
            "power_supplier": power_supplier,
            "active": active})

    def update_state(self, electrical_vehicle_state):
        """Update electrical vehicle state"""
        super().update_state(electrical_vehicle_state)
        if 'power_supplier' in electrical_vehicle_state:
            self.power_supplier = electrical_vehicle_state['power_supplier']

    def move(self):
        """Move electrical vehicle to another agent"""
        pass


class PVPanel(GridElement):
    """Representation of PV panel in simulation process"""
    unit_area = None
    series = None
    parallels = None
    efficiency = None
    solar_irradiance = None
    battery_coupling_efficiency = None
    heating_contribution = None

    @classmethod
    def from_properties(cls, unit_area, series, parallels, efficiency, solar_irradiance, battery_coupling_efficiency,
                        heating_contribution, active):
        """Initialization from parameters"""
        return cls({"unit_area": unit_area,
                    "series": series,
                    "parallels": parallels,
                    "efficiency": efficiency,
                    "solar_irradiance": solar_irradiance,
                    "battery_coupling_efficiency": battery_coupling_efficiency,
                    "heating_contribution": heating_contribution,
                    "active": active})

    def update_state(self, pv_panel_state):
        """Update PV panel state"""
        super().update_state(pv_panel_state)
        if 'solar_irradiance' in pv_panel_state:
            self.solar_irradiance = pv_panel_state['solar_irradiance']
        if 'heating_contribution' in pv_panel_state:
            self.heating_contribution = pv_panel_state['heating_contribution']

    def erogate(self):
        """Erogate power"""
        return self.unit_area * self.series * self.parallels * self.efficiency * self.solar_irradiance


class WindGenerator(GridElement):
    """Representation of wind generator in simulation process"""
    power_coefficient = None
    air_density = None
    area = None
    wind_speed = None
    battery_coupling_efficiency = None

    @classmethod
    def from_properties(cls, power_coefficient, air_density, area, wind_speed, battery_coupling_efficiency, active):
        """Initialization from parameters"""
        return cls({
            "power_coefficient": power_coefficient,
            'air_density': air_density,
            'area': area,
            "wind_speed": wind_speed,
            "battery_coupling_efficiency": battery_coupling_efficiency,
            "active": active
        })

    def update_state(self, wind_generator_state):
        """Update wind generator state"""
        super().update_state(wind_generator_state)
        if 'wind_speed' in wind_generator_state:
            self.wind_speed = wind_generator_state['wind_speed']

    def erogate(self):
        """Erogate power"""
        return (self.air_density * self.power_coefficient * self.area * self.wind_speed ** 3) / 2


class WaterTank(GridElement):
    """Representation of water tank in simulation process"""
    capacity = None
    temp = None

    @classmethod
    def from_properties(cls, capacity, temp, active):
        """Initialization from parameters"""
        return cls({"capacity": capacity,
                    "temp": temp,
                    "active": active})

    def charge(self, power, time_scale):
        """Charge energy from current"""
        self.temp += (power * 3.412 / (4 * self.capacity)) * time_scale
        if self.temp > 60:
            self.temp = 60


class AgentEncoder(json.JSONEncoder):
    """Agent Encoder for JSON serialization"""

    def default(self, o):
        result = dict(o.__dict__)
        if o.battery is not None:
            result['battery'] = dict(o.battery.__dict__)
        if o.pv_panel is not None:
            result['pv_panel'] = dict(o.pv_panel.__dict__)
        if o.wind_generator is not None:
            result['wind_generator'] = dict(o.wind_generator.__dict__)
        if o.electrical_vehicle is not None:
            result['electrical_vehicle'] = dict(o.electrical_vehicle.__dict__)
        if o.water_tank is not None:
            result['water_tank'] = dict(o.water_tank.__dict__)
        return result
