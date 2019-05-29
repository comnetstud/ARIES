"""Provide classes for simulation"""
import json
import logging
import time

import numpy as np

from aries.controller import cluster_utils
from aries.core.constants import TIME_SCALE
from aries.core.grid.state import State
from aries.simulation import simulation_utils

logger = logging.getLogger(__name__)


def process_simulation_step(agent, time_scale):
    """Determine the new Agent state according to external factors contained in state"""

    # Get the power output of the pv panel. Assume that it will remain constant during TIME_SCALE
    # If the pv is switched off / not installed, then pv_power will be zero
    pv_power = simulation_utils.get_pv_power(agent=agent)

    # Get the power output of the wind generator. Assume that it will remain constant during TIME_SCALE
    # Wind power is all going to the battery for now
    # If the wind generator is switched off  / not installed, then wind_power_to_battery will be zero
    wind_power_to_battery = simulation_utils.get_wind_power(agent=agent)
    # Manage the contribution of the pv panel to the water tank. If the water tank is switched off/ not installed,
    # then pv_power_to_heating = 0
    pv_power_to_heating = simulation_utils.set_heating_contribution(agent=agent, pv_power=pv_power)

    # Update the power going to the storage from the pv panel. If water tank is non active, then pv_power_to_heating = 0
    # and pv_power_to_battery = pv_power
    pv_power_to_battery = pv_power - pv_power_to_heating

    power_to_battery = (pv_power_to_battery, wind_power_to_battery)

    # Heat the water
    # I check if pv_power_to_heating > 0 to avoid unnecessary function calls, I trust in the branch predictor
    if pv_power_to_heating > 0:
        agent.water_tank.charge(power=pv_power_to_heating, time_scale=time_scale)

    # Process the power demand, the optional incoming power due to network overproduction, and the request for power
    # injection. Power injection comes from external controllers operating at higher level
    total_power, request_inject_power = simulation_utils.manage_power(agent=agent)
    # Update the total_power values according to the EV contribution
    # The manage_ev function handles the state update of the ev storage unit

    total_power = simulation_utils.manage_ev(agent=agent, total_power=total_power, time_scale=time_scale)

    ret_vals = simulation_utils.manage_battery(agent=agent, total_power=total_power,
                                               request_inject_power=request_inject_power,
                                               power_to_battery=power_to_battery, time_scale=time_scale)
    total_active_power = ret_vals[0]
    total_power_factor = ret_vals[1]
    demand_power = ret_vals[2]
    inject_power = ret_vals[3]
    total_power_from_battery = ret_vals[4]

    return (agent.name, simulation_utils.impedance(voltage_rating=agent.voltage_rating, power_factor=total_power_factor,
                                                   power_rating=total_active_power), demand_power, inject_power,
            total_power_from_battery, pv_power)


class Simulation(object):
    """Representation of simulation"""
    simulation_id = None
    agents = None
    lines = None
    paths = None
    nodes = None
    clusters = None
    storage = None
    event_queue = None
    latency = None
    solver = None

    env = None
    process = None

    def __init__(self, agents, lines, paths, nodes, storage, event_queue, solver, simulation_id, latency,
                 clusters=None):
        self.agents = agents
        self.lines = lines
        self.paths = paths
        self.nodes = nodes
        self.storage = storage
        self.event_queue = event_queue
        self.solver = solver
        self.simulation_id = simulation_id
        self.latency = latency
        self.clusters = clusters

    def check_and_update_state(self):
        """Read events and update state of agent"""
        ev = self.event_queue.read_states()
        if ev is None:
            return
        is_applied = True
        for agent_name, j in ev['states'].items():
            try:
                # state = State(json.loads(j))
                print(agent_name, j)
                state = State(j)
                self.agents[agent_name].update_state(state)
            except Exception as e:
                is_applied = False
                logging.exception('check_and_update_state', e)

        # Store state events
        self.storage.write_states(ev['states'], simulation_id=self.simulation_id, simulation_step=self.env.now,
                                  is_applied=is_applied)

    def check_and_update_cluster(self):
        """Read cluster events and update agent configuration"""
        try:
            ev = self.event_queue.read_clusters()
            if ev is not None:
                is_applied = True
                for agent in self.agents.values():
                    agent.request_inject_power = 0
                    agent.request_power_factor = 1
                if ev['clusters']:
                    self.clusters = cluster_utils.create_clusters(ev['clusters'])
                else:
                    self.clusters = {}

                # Store cluster events
                self.storage.write_clusters(ev['clusters'], simulation_id=self.simulation_id,
                                            simulation_step=self.env.now,
                                            is_applied=is_applied)
        except Exception as e:
            logging.exception('check_and_update_cluster', e)

        if self.clusters:
            for name, cluster in self.clusters.items():
                cluster.run(agents=self.agents, lines=self.lines, nodes=self.nodes, paths=self.paths)

    def init_simulation(self, env):
        """Init simulation, needed to be called before running simualation"""
        self.env = env
        self.process = env.process(self.run())

    def run(self):
        """Run cluster method"""
        while True:
            if self.latency and self.latency > 0:
                time.sleep(self.latency / 1000)

            self.check_and_update_state()
            self.check_and_update_cluster()

            agents_states = {}
            total_pv_power = 0
            for agent in self.agents.values():
                ret_vals = process_simulation_step(
                    agent=agent, time_scale=TIME_SCALE)
                agent_name, impedance, demand_power, inject_power, power_from_battery, pv_power = ret_vals
                # With this we have all the data we need to solve the power flow equations
                # Initial conditions for voltages at the buses are to be set to the pcc voltage_rating, i.e., 230V for
                # single phase and 400V for three-phase systems

                # impedance is already computed on the actual power demand that accounts for the incoming power
                # hence no need for recomputing it
                total_pv_power += pv_power
                agents_states[agent_name] = {"impedance": {"resistance": np.real(impedance),
                                                           "reactance": np.imag(impedance)},
                                             "inject_power": {"active_power": np.real(inject_power),
                                                              "reactive_power": np.imag(inject_power)},
                                             "demand_power": {"active_power": np.real(demand_power),
                                                              "reactive_power": np.imag(demand_power)},
                                             "battery_power": {"active_power": np.real(power_from_battery),
                                                               "reactive_power": np.imag(power_from_battery)}}

            simulation_result = self.solver.solve(agents_states)
            # simulation_result['pv_power'] = total_pv_power
            self.write_simulation_result(simulation_result=simulation_result, agents_states=agents_states,
                                         total_pv_power=total_pv_power)
            logger.info("{} {}".format(self.env.now, simulation_result))
            yield self.env.timeout(1)

    def write_simulation_result(self, simulation_result, agents_states, total_pv_power):
        """Help method to write simulation result in one go"""
        simulation_step_id = self.storage.write_simulation_step(simulation_step=self.env.now,
                                                                simulation_id=self.simulation_id,
                                                                simulation_result=simulation_result,
                                                                agents_states=agents_states,
                                                                total_pv_power=total_pv_power)
        self.storage.write_agents(agents=self.agents, simulation_step_id=simulation_step_id,
                                  simulation_id=self.simulation_id)
        self.storage.finalize_simulation_step(simulation_step_id)
