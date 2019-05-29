"""Abstract class for storing data"""


class DB(object):
    """Abstract class for storing data"""

    def read_simulation(self):
        pass

    def write_simulation(self, agents, lines, paths, nodes, solver):
        pass

    def write_agents(self, agents, simulation_step_id, simulation_id):
        pass

    def write_lines(self, lines):
        pass

    def write_simulation_step(self, simulation_step, simulation_id, simulation_result):
        pass
