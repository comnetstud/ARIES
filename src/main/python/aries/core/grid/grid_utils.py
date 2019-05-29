from aries.core.grid.agent import Agent
from aries.core.grid.line import Line
from aries.core.grid.topology import Path, Node


def dict_to_json(dict_obj):
    """Converter dict with obj to JSON"""
    result = {}
    for name, obj in dict_obj.items():
        result[name] = obj.dump()
    return result


def create_grid_elements(j):
    """Create grid elements (agents and lines) from json"""
    agents = {}
    for name, item in j['agents'].items():
        agent = Agent.load(name=name, j=item)
        agents[name] = agent

    lines = {}
    for name, item in j['lines'].items():
        line = Line.load(name=name, j=item)
        lines[name] = line

    return agents, lines


def create_topology(j):
    """Create topology (paths and nodes) from json"""
    paths = {}
    for name, item in j['paths'].items():
        path = Path.load(j=item)
        # list(map(Path.validate, item))
        paths[name] = path

    nodes = {}
    for name, item in j['nodes'].items():
        node = Node.load(j=item)
        nodes[name] = node

    return paths, nodes


