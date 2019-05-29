"""Provide classes for simulation"""

import json

import cerberus
from bson import json_util

from aries.core import utils

# Schema for line validation
line_schema = {
    'name': {'type': 'string', 'required': False},
    'resistance': {'type': 'float', 'required': True},
    'reactance': {'type': 'float', 'required': True},
    'shunt_resistance': {'type': 'float', 'required': False, "default": None, "empty": True},
    'shunt_reactance': {'type': 'float', 'required': False, "default": None, "empty": True},

}
line_validator = cerberus.Validator(line_schema)
line_validator.ignore_none_values = True


class Line(object):
    """Representation of line in simulation"""
    name = None
    resistance = None
    reactance = None
    shunt_resistance = None
    shunt_reactance = None

    def __init__(self, params_dict):
        """Initialization from dictionary"""
        self.__dict__ = params_dict

    @classmethod
    def from_properties(cls, name, resistance, reactance, shunt_resistance, shunt_reactance):
        """Initialization from parameters"""
        return cls({
            "name": name,
            "resistance": resistance,
            "reactance": reactance,
            "shunt_resistance": shunt_resistance,
            "shunt_reactance": shunt_reactance
        })

    def dump(self):
        """Dump object to json string"""
        return json_util.dumps(self, cls=LineEncoder)

    @classmethod
    def load(cls, name, j):
        """Create Line object from json"""
        j = line_validator.normalized(j)
        Line.validate(j)
        return Line.from_properties(name, j["resistance"], j["reactance"], j["shunt_resistance"], j["shunt_reactance"])

    @staticmethod
    def validate(data):
        """Validate object according to agent_schema"""
        return utils.validate(data, 'Line', line_validator)


class LineEncoder(json.JSONEncoder):
    """Line Encoder for JSON serialization"""

    def default(self, o):
        return dict(o.__dict__)
