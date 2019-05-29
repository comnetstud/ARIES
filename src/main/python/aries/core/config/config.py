import json

import cerberus
from bson import json_util

import aries.core.utils
from aries.core.constants import LINEAR_SOLVER, NON_LINEAR_SOLVER, CUSTOM_SOLVER

config_schema = {
    "topology": {'type': 'string', 'required': True},
    "grid_elements": {'type': 'string', 'required': True},
    "simulation_steps": {'type': 'integer', 'required': True, 'default': 100},
    "latency": {'type': 'integer', 'required': False, 'default': 0},
    "mongodb_uri": {'type': 'string', 'required': True, 'default': 'mongodb://localhost:27017/'},
    "redis_host": {'type': 'string', 'required': True, 'default': "localhost"},
    "redis_port": {'type': 'integer', 'required': True, 'default': 6379},
    "solver_type": {'type': 'string', 'required': True, 'default': LINEAR_SOLVER,
                    'allowed': [LINEAR_SOLVER, NON_LINEAR_SOLVER, CUSTOM_SOLVER]},
    "clusters": {'type': 'string', 'required': False, 'default': '', "empty": True},
}
config_validator = cerberus.Validator(config_schema)


class Config(object):
    """Representation of initial Config in simulation process"""
    topology = None
    grid_elements = None
    simulation_steps = None
    latency = None
    mongodb_uri = None
    redis_host = None
    redis_port = None
    solver_type = None
    clusters = None

    def __init__(self, params_dict):
        self.__dict__ = params_dict

    @classmethod
    def from_properties(cls, topology, grid_elements, simulation_steps, latency, mongodb_uri,
                        redis_host, redis_port, solver_type, clusters=None):
        """Initialization from parameters"""
        return cls({"topology": topology,
                    "grid_elements": grid_elements,
                    "simulation_steps": simulation_steps,
                    "latency": latency,
                    "mongodb_uri": mongodb_uri,
                    "redis_host": redis_host,
                    "redis_port": redis_port,
                    "solver_type": solver_type,
                    "clusters": clusters})

    @classmethod
    def load(cls, j):
        """Create State object from json"""
        j = config_validator.normalized(j)
        Config.validate(j)
        return cls.from_properties(topology=j['topology'],
                                   grid_elements=j['grid_elements'],
                                   simulation_steps=j['simulation_steps'],
                                   latency=j['latency'],
                                   mongodb_uri=j["mongodb_uri"],
                                   redis_host=j["redis_host"],
                                   redis_port=j['redis_port'],
                                   solver_type=j['solver_type'],
                                   clusters=j['clusters'])

    def dump(self):
        """Dump object to json string"""
        return json_util.dumps(self, cls=ConfigEncoder)

    @staticmethod
    def validate(data):
        """Validate object according to state_schema"""
        return aries.core.utils.validate(data, 'Config', config_validator)


class ConfigEncoder(json.JSONEncoder):
    """State Encoder for JSON serialization"""

    def default(self, o):
        return dict(o.__dict__)
