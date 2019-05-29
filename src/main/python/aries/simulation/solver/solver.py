class Solver(object):
    """Solver to determine the electrical state of the grid"""

    type = None

    # The constructor just takes the topology and the lines specs as parameters
    # That's because to build the network matrix, we need to know the actual state of the loads
    # and this (possibly) changes at every time step.
    def __init__(self, paths, nodes, lines):
        """Initialize the grid configuration"""
        self.paths = paths
        self.nodes = nodes
        self.lines = lines

    def build(self, agents_state):
        pass

    def solve(self, agents_state):
        pass
