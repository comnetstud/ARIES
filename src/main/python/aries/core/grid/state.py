"""Provide State classes for simulation"""
import json

import cerberus
from bson import json_util

from aries.core import utils

# Schema for state validation
state_schema = {
    'power_rating': {'type': 'float', 'required': False},
    'power_factor': {'type': 'float', 'required': False},
    'incoming_power': {'type': 'float', 'required': False},
    'request_inject_power': {'type': 'float', 'required': False},
    'request_power_factor': {'type': 'float', 'required': False},

    'battery': {
        'type': 'dict',
        'schema': {
            'status': {'type': 'float', 'required': False},
            'contribution_active': {'type': 'float', 'min': 0, 'max': 1, 'required': False},
            'contribution_reactive': {'type': 'float', 'min': 0, 'max': 1, 'required': False},
            'active': {'type': 'integer', 'min': 0, 'max': 1, 'required': False}
        },
        'required': False
    },
    'pv_panel': {
        'type': 'dict',
        'schema': {
            'solar_irradiance': {'type': 'float', 'required': False},
            'heating_contribution': {'type': 'float', 'required': False},
            'active': {'type': 'integer', 'min': 0, 'max': 1, 'required': False}
        },
        'required': False
    },
    'wind_generator': {
        'type': 'dict',
        'schema': {
            'wind_speed': {'type': 'float', 'required': False},
            'heating_contribution': {'type': 'float', 'required': False},
            'active': {'type': 'integer', 'min': 0, 'max': 1, 'required': False}
        },
        'required': False
    },
    'electrical_vehicle': {
        'type': 'dict',
        'schema': {
            'status': {'type': 'float', 'required': False},
            'contribution_active': {'type': 'float', 'required': False},
            'contribution_reactive': {'type': 'float', 'required': False},
            'power_supplier': {'type': 'float', 'required': False},
            'active': {'type': 'integer', 'min': 0, 'max': 1, 'required': False}
        },
        'required': False
    },
    'water_tank': {
        'type': 'dict',
        'schema': {
            'active': {'type': 'integer', 'min': 0, 'max': 1, 'required': False}
        },
        'required': False
    }
}

state_validator = cerberus.Validator(state_schema)


class State(object):
    """Representation of State in simulation process"""
    power_rating = None
    power_factor = None
    incoming_power = None
    request_inject_power = None
    request_power_factor = None

    battery = None
    electrical_vehicle = None
    pv_panel = None
    water_tank = None
    wind_generator = None

    def __init__(self, params_dict):
        self.__dict__ = params_dict

    @classmethod
    def load(cls, j):
        """Create State object from json"""
        State.validate(j)
        return State(j)

    def dump(self):
        """Dump object to json string"""
        return json_util.dumps(self, cls=StateEncoder)

    @staticmethod
    def validate(data):
        """Validate object according to state_schema"""
        return utils.validate(data, 'State', state_validator)


class StateEncoder(json.JSONEncoder):
    """State Encoder for JSON serialization"""

    def default(self, o):
        return dict(o.__dict__)
