"""Provided Cluster class for simulation"""

import json

import cerberus
import numpy as np
from bson import json_util

from aries.core import utils
from aries.simulation import simulation_utils

# Schema for cluster validation
cluster_schema = {
    'cluster_agents': {'type': 'list', 'schema': {'type': 'string'}},
    'controller': {'type': 'string', 'required': True},
    'priority': {'type': 'integer', 'required': False},
    'delay': {'type': 'integer', 'required': False},
}

cluster_validator = cerberus.Validator(cluster_schema)
cluster_validator.ignore_none_values = True


class Cluster(object):
    """Representation of cluster in simulation"""
    name = None
    # List of agents name belonging to the cluster
    cluster_agents = None
    priority = None
    controller = None
    delay = None

    def __init__(self, params_dict):
        """Initialization from dictionary"""
        self.__dict__ = params_dict

    @classmethod
    def from_properties(cls, name, cluster_agents, controller, priority, delay):
        """Initialization from parameters"""
        return cls({
            "name": name,
            "cluster_agents": cluster_agents,
            "controller": controller,
            "priority": priority,
            "delay": delay
        })

    def dump(self):
        """Dump object to json string"""
        return json_util.dumps(self, cls=ClusterEncoder)

    @staticmethod
    def validate(data):
        """Validate object according to agent_schema"""
        return utils.validate(data, 'Cluster', cluster_validator)

    def run(self, agents, lines, nodes, paths):
        print('Cluster')
        pass


class ClusterEncoder(json.JSONEncoder):
    """Cluster Encoder for JSON serialization"""

    def default(self, o):
        cluster_dict = dict(o.__dict__)
        del cluster_dict['name']
        return cluster_dict


class LoadSharingCluster(Cluster):
    """LoadSharingCluster ..."""

    def run(self, agents, lines, nodes, paths):
        total_active_power = 0
        total_reactive_power = 0
        # states_sum = 0
        # params = {}
        agents_names = self.cluster_agents
        agents_number = len(agents_names)
        passive_agents_number = int(agents_number / 2)
        # passive_agents_list = list(np.random.choice(agents_names, passive_agents_number, replace=False))
        passive_agents_list = agents_names[:passive_agents_number]

        for agent_name in self.cluster_agents:
            agent = agents[agent_name]
            battery = agent.battery
            if (agent_name in passive_agents_list) and (battery.active == 1):
                tmp_ap = agent.power_rating
                tmp_rp = simulation_utils.reactive_power(power_rating=agent.power_rating,
                                                         power_factor=agent.power_factor)
                desired_power = np.abs(np.complex(tmp_ap, 1e-2 * tmp_rp))
                required_amps = (desired_power / battery.voltage / battery.inverter_efficiency)
                if battery.status - required_amps >= 0:
                    total_active_power += tmp_ap - tmp_ap * battery.contribution_active
                    total_reactive_power += tmp_rp - tmp_rp * battery.contribution_reactive
                else:
                    total_active_power += tmp_ap
                    total_reactive_power += tmp_rp
            else:
                total_active_power += agent.power_rating
                total_reactive_power += simulation_utils.reactive_power(power_rating=agent.power_rating,
                                                                        power_factor=agent.power_factor)
            # tmp_state = agent.battery.status / agent.battery.capacity
            # params[agent_name] = tmp_state
            # states_sum += tmp_state
        # print('total_a_p: ', total_active__power)

        for agent_name in self.cluster_agents:
            # alpha = params[agent_name] / states_sum
            # active_power_share = total_active__power * alpha
            # reactive_power_share = total_reactive_power * alpha
            # agents[agent_name].request_inject_power = active_power_share
            # agents[agent_name].request_power_factor = active_power_share / np.abs(
            #     np.complex(active_power_share, reactive_power_share))
            if agent_name not in passive_agents_list:
                active_power = total_active_power / (agents_number - passive_agents_number)

                # reactive_power = simulation_utils.reactive_power(power_rating=agent.power_rating,
                #                                                  power_factor=agent.power_factor)
                reactive_power = total_reactive_power / (agents_number - passive_agents_number)
                # print(active_power, reactive_power)
                agents[agent_name].request_inject_power = active_power
                agents[agent_name].request_power_factor = active_power / np.abs(
                    np.complex(active_power, reactive_power))
                agents[agent_name].battery.contribution_active = 0
                agents[agent_name].battery.contribution_reactive = 0


class StayingAliveCluster(Cluster):
    """StayingAliveCluster ..."""

    def run(self, agents, lines, nodes, paths):
        print('StayingAliveCluster')
        pass
