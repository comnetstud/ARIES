import numpy as np

from aries.core.constants import PCC_VOLTAGE, LINEAR_SOLVER
from aries.simulation import simulation_utils
from aries.simulation.solver.solver import Solver


class LinearSolver(Solver):
    """Solver to determine the electrical state of the grid"""

    # The constructor just takes the topology and the lines specs as parameters
    # That's because to build the network matrix, we need to know the actual state of the loads
    # and this (possibly) changes at every time step.
    def __init__(self, paths, nodes, lines):
        """Initialize the grid configuration"""
        super().__init__(paths=paths, nodes=nodes, lines=lines)
        self.type = LINEAR_SOLVER

    def build(self, agents_state):
        """Build the KCL-KVL matrix"""

        # Init the nodes matrix to zero
        lines_to_idx = {j: i for i, j in enumerate(self.lines.keys())}
        agents_to_idx = {j: i for i, j in enumerate(agents_state.keys())}

        b = np.zeros(len(self.lines), dtype=np.complex)

        for agent in agents_state.keys():
            for path in self.paths[agent].active_paths():
                if path['active'] == 1:
                    for line_name in path['path']:
                        inject_power = np.complex(agents_state[agent]['inject_power']['active_power'],
                                                  agents_state[agent]['inject_power']['reactive_power'])
                        demand_power = np.complex(agents_state[agent]['demand_power']['active_power'],
                                                  agents_state[agent]['demand_power']['reactive_power'])

                        net_power = demand_power - inject_power

                        b[lines_to_idx[line_name]] += simulation_utils.current_from_power(
                            voltage_rating=PCC_VOLTAGE,
                            power=net_power)
        drops = np.zeros(len(b), dtype=np.complex)
        for line in self.lines.keys():
            line_idx = lines_to_idx[line]
            line_imp = np.complex(self.lines[line].resistance, self.lines[line].reactance)
            drops[line_idx] = line_imp * b[line_idx]
        voltages = np.zeros(len(agents_state))
        for agent in agents_state.keys():
            inject_power = np.complex(agents_state[agent]['inject_power']['active_power'],
                                      agents_state[agent]['inject_power']['reactive_power'])
            demand_power = np.complex(agents_state[agent]['demand_power']['active_power'],
                                      agents_state[agent]['demand_power']['reactive_power'])

            net_power = demand_power - inject_power
            if np.real(net_power) <= 0:
                voltages[agents_to_idx[agent]] = 230
            else:
                for path in self.paths[agent].active_paths():
                    if path['active'] == 1:
                        voltage = 0
                        for branch in path['path']:
                            branch_idx = lines_to_idx[branch]
                            voltage += drops[branch_idx]
                            if branch == path['path'][-1]:
                                voltages[agents_to_idx[agent]] = 230 - np.real(voltage)

        b = np.zeros(len(self.lines), dtype=np.complex)
        for agent in agents_state.keys():
            for path in self.paths[agent].active_paths():
                if path['active'] == 1:
                    for line_name in path['path']:
                        inject_power = np.complex(agents_state[agent]['inject_power']['active_power'],
                                                  agents_state[agent]['inject_power']['reactive_power'])
                        demand_power = np.complex(agents_state[agent]['demand_power']['active_power'],
                                                  agents_state[agent]['demand_power']['reactive_power'])

                        net_power = demand_power - inject_power

                        b[lines_to_idx[line_name]] += simulation_utils.current_from_power(
                            voltage_rating=voltages[agents_to_idx[agent]],
                            power=net_power)

        # Map the dictionary keys to the column indices
        solution = np.zeros(len(self.lines) + len(agents_state), dtype=np.complex)

        variables_to_idx = list(self.lines.keys()) + list(agents_state.keys())
        variables_to_idx = {variables_to_idx[i]: i for i in range(len(variables_to_idx))}

        for l in self.lines.keys():
            l_idx = variables_to_idx[l]
            solution[l_idx] = b[lines_to_idx[l]]
        for a in agents_state.keys():
            a_idx = variables_to_idx[a]
            inject_power = np.complex(agents_state[a]['inject_power']['active_power'],
                                      agents_state[a]['inject_power']['reactive_power'])
            demand_power = np.complex(agents_state[a]['demand_power']['active_power'],
                                      agents_state[a]['demand_power']['reactive_power'])

            net_power = demand_power - inject_power

            solution[a_idx] = simulation_utils.current_from_power(voltage_rating=voltages[agents_to_idx[a]],
                                                                  power=net_power)
        return solution, variables_to_idx

    def power_from_main(self, grid_solution):
        complex_current = np.complex(grid_solution['B0']['real'], grid_solution['B0']['imag'])
        return PCC_VOLTAGE * np.conj(complex_current)

    def power_distribution_loss(self, grid_solution):
        power = 0
        for line_name in self.lines.keys():
            line_impedance = np.complex(self.lines[line_name].resistance, self.lines[line_name].reactance)
            line_current = np.complex(grid_solution[line_name]['real'], grid_solution[line_name]['imag'])
            power += np.real(line_impedance * line_current * np.conj(line_current))
        return power

    def solve(self, agents_state):
        """Solve the linearized approximation of the grid"""
        solution, variables_to_idx = self.build(agents_state)

        solution_dict = {
            key: {'real': np.real(solution[variables_to_idx[key]]), 'imag': np.imag(solution[variables_to_idx[key]])}
            for key in variables_to_idx.keys()}
        power_from_main = self.power_from_main(grid_solution=solution_dict)
        distribution_loss = self.power_distribution_loss(grid_solution=solution_dict)
        solution_dict['power_from_main'] = {'real': np.real(power_from_main), 'imag': np.imag(power_from_main)}
        solution_dict['distribution_loss'] = {'real': distribution_loss, 'imag': 0}

        # Returns the currents flowing through all the lines and agents
        return solution_dict
