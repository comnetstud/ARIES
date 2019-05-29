"""Provide classes for simulation"""


class ClusterController(object):
    """Representation of cluster controller in simulation"""

    clusters = {}

    def run(self, agents, lines, paths, nodes, parameters):
        for name, cluster in self.clusters.items():
            cluster.run(agents, lines, paths, nodes, parameters)
