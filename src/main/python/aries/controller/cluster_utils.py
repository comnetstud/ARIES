import importlib

from aries.controller.cluster import Cluster, cluster_validator
from aries.core.exceptions import ValidationError


def create_clusters(j):
    """Create grid elements (agents and lines) from json"""
    clusters = {}
    agents = []
    for name, item in j.items():
        cluster = create_cluster_factory(name=name, j=item)
        clusters[name] = cluster
        overlapped_agents = [i for i in cluster.cluster_agents if i in agents]
        if overlapped_agents:
            raise ValidationError('Agents {} are already in cluster.'.format(overlapped_agents))
        agents.extend(cluster.cluster_agents)
    return clusters


def create_cluster_factory(name, j):
    module = importlib.import_module('aries.controller.cluster')
    class_ = getattr(module, j['controller'])
    j = cluster_validator.normalized(j)
    Cluster.validate(j)
    return class_.from_properties(name, j["cluster_agents"], j["controller"], j["priority"], j["delay"])
