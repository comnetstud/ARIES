"""Provide topology classes for simulation"""

import json

import cerberus
from bson import json_util


# Schema for path validation
from aries.core import utils

path_schema = {
    'active': {'type': 'integer', 'min': 0, 'max': 1, 'required': True},
    'path': {'type': 'list', 'schema': {'type': 'string'}}
}
path_validator = cerberus.Validator(path_schema)

# Schema for node validation
node_schema = {
    'branches_in': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
    'branches_out': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
    'adjacency': {'type': 'list', 'schema': {'type': 'list', 'schema': {'type': 'string'}}, 'required': True},
    'agent': {'type': 'string', 'required': False, 'default': None}
}
node_validator = cerberus.Validator(node_schema)
node_validator.ignore_none_values = True


class Path(object):
    """Representation of path in simulation"""

    paths = None

    def __init__(self, params_dict):
        """Initialization from dictionary"""
        self.__dict__ = params_dict

    @classmethod
    def from_properties(cls, paths):
        """Initialization from parameters"""
        return cls({
            "paths": paths
        })

    def active_paths(self):
        """Return all active paths"""
        result = []
        for p in self.paths:
            if p['active'] == 1:
                result.append(p)
        return result

    def dump(self):
        """Dump object to json string"""
        return json_util.dumps(self, cls=PathEncoder)

    @classmethod
    def load(cls, j):
        """Create Path object from json"""
        paths = []
        for p in j:
            Path.validate(p)
            paths.append(p)
        return Path.from_properties(paths)

    @staticmethod
    def validate(data):
        """Validate object according to agent_schema"""
        return utils.validate(data, 'Path', path_validator)

    @staticmethod
    def validate_list(data):
        if isinstance(data, list):
            for d in data:
                utils.validate(d, 'Path', path_validator)
            return True
        return False


class PathEncoder(json.JSONEncoder):
    """Path Encoder for JSON serialization"""

    def default(self, o):
        result = []
        for p in o.paths:
            result.append(dict(p))
        return result


class Node(object):
    """Representation of node in simulation"""
    branches_in = None
    branches_out = None
    adjacency = None
    agent = None

    def __init__(self, params_dict):
        """Initialization from dictionary"""
        self.__dict__ = params_dict

    @classmethod
    def from_properties(cls, branches_in, branches_out, adjacency, agent):
        """Initialization from parameters"""
        return cls({
            "branches_in": branches_in,
            "branches_out": branches_out,
            "adjacency": adjacency,
            "agent": agent
        })

    def dump(self):
        """Dump object to json string"""
        return json_util.dumps(self, cls=NodeEncoder)

    @classmethod
    def load(cls, j):
        """Create Node object from json"""
        j = node_validator.normalized(j)
        Node.validate(j)
        return Node.from_properties(branches_in=j["branches_in"], branches_out=j["branches_out"],
                                    adjacency=j["adjacency"], agent=j["agent"])

    @staticmethod
    def validate(data):
        """Validate object according to agent_schema"""
        return utils.validate(data, 'Node', node_validator)


class NodeEncoder(json.JSONEncoder):
    """Node Encoder for JSON serialization"""

    def default(self, o):
        return dict(o.__dict__)
