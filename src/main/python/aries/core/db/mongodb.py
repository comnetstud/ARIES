"""MongoDB implementation of storage"""
import datetime

import pymongo

from aries.core.db.db import DB
from aries.core.grid.grid_utils import dict_to_json

DATABASE = 'aries'
SIMULATION = 'simulation'
SIMULATION_STEP = 'simulation_step'
AGENTS = 'agents'
STATE_QUEUE = 'state_queue'
CLUSTER_QUEUE = 'cluster_queue'


class MongoDB(DB):
    """MongoDB storage"""

    def __init__(self, url=None, client=None):
        if url is not None:
            self.client = pymongo.MongoClient(url)
        else:
            self.client = client

    def get_active_simulation(self):
        return self.client[DATABASE][SIMULATION].find({}).sort('$natural', -1).limit(1)

    def write_simulation(self, agents, lines, paths, nodes, solver, clusters=None):
        """Store simulation start step"""
        simulation = {
            'agents': dict_to_json(agents),
            'lines': dict_to_json(lines),
            'paths': dict_to_json(paths),
            'nodes': dict_to_json(nodes),
            'start_time': datetime.datetime.utcnow(),
            'solver': solver,
            'clusters': dict_to_json(clusters) if clusters else None
        }
        return self.client[DATABASE][SIMULATION].insert_one(simulation).inserted_id

    def get_active_simulation_step(self):
        """Get current simulation_step by simulation id"""
        return self.client[DATABASE][SIMULATION_STEP].find().sort('$natural', -1).limit(1)

    def get_last_active_sumulation_step(self, simulation_id, number_of_steps):
        """Get current simulation_step by simulation id"""
        return self.client[DATABASE][SIMULATION_STEP].find({'simulation_id': simulation_id}).sort('$natural', -1).limit(
            number_of_steps)

    def get_simulation_step_by_simulation(self, simulation_id):
        """Get simulation step by simulation id"""
        return self.client[DATABASE][SIMULATION_STEP].find({'simulation_id': simulation_id})

    def write_simulation_step(self, simulation_step, simulation_id, simulation_result, agents_states, total_pv_power):
        """Store simulation step"""
        return self.client[DATABASE][SIMULATION_STEP].insert_one(
            {'simulation_step': simulation_step, 'simulation_id': simulation_id,
             'simulation_result': simulation_result, 'agents_states': agents_states, 'total_pv_power': total_pv_power,
             'valid': False}).inserted_id

    def finalize_simulation_step(self, simulation_step_id):
        self.client[DATABASE][SIMULATION_STEP].update({'_id': simulation_step_id}, {'$set': {'valid': True}})

    def get_agents_by_simulation_step(self, simulation_step_id):
        return self.client[DATABASE][AGENTS].find({'simulation_step_id': simulation_step_id})

    def get_agents_by_simulation(self, simulation_id):
        return self.client[DATABASE][AGENTS].find({'simulation_id': simulation_id})

    def get_agents_by_active_simulation(self):
        simulation_cursor = self.get_active_simulation()
        if simulation_cursor is not None:
            simulation = next(simulation_cursor, None)
            if simulation is not None:
                return self.get_agents_by_simulation(simulation_id=simulation['_id'])
        return None

    def write_agents(self, agents, simulation_step_id, simulation_id):
        """Store agents for each simulation step"""
        agents_to_db = []
        for name, agent in agents.items():
            agents_to_db.append({
                'name': name,
                'agent': agent.dump(),
                'simulation_step_id': simulation_step_id,
                'simulation_id': simulation_id
            })
        return self.client[DATABASE][AGENTS].insert_many(agents_to_db)

    def write_states(self, states, simulation_id, simulation_step, is_applied):
        """Store state's events"""
        states_to_db = {
            'states': states,
            'simulation_step': simulation_step,
            'simulation_id': simulation_id,
            'is_applied': is_applied
        }
        return self.client[DATABASE][STATE_QUEUE].insert_one(states_to_db)

    def read_states(self, simulation_id, simulation_step=None, is_applied=None):
        """Store state's events"""
        search_dict = {'simulation_id': simulation_id}
        if simulation_step:
            search_dict['simulation_step'] = simulation_step
        if is_applied:
            search_dict['is_applied'] = is_applied
        return self.client[DATABASE][STATE_QUEUE].find(search_dict)

    def write_clusters(self, clusters, simulation_id, simulation_step, is_applied):
        """Store cluster's events"""
        clusters_to_db = {
            'clusters': clusters,
            'simulation_step': simulation_step,
            'simulation_id': simulation_id,
            'is_applied': is_applied
        }
        return self.client[DATABASE][CLUSTER_QUEUE].insert_one(clusters_to_db)

    def read_clusters(self, simulation_id, simulation_step=None, is_applied=None):
        """Store cluster's events"""
        search_dict = {'simulation_id': simulation_id}
        if simulation_step:
            search_dict['simulation_step'] = simulation_step
        if is_applied:
            search_dict['is_applied'] = True
            if 'simulation_step' in search_dict:
                del search_dict['simulation_step']
            if 'simulation_id' in search_dict:
                del search_dict['simulation_id']
        return self.client[DATABASE][CLUSTER_QUEUE].find(search_dict)

    def get_last_cluster_for_simulation_id(self, simulation_id):
        """Store cluster's events"""
        search_dict = {'simulation_id': simulation_id, 'is_applied': True}
        return self.client[DATABASE][CLUSTER_QUEUE].find(search_dict).sort('$natural', -1).limit(1)

    def get_last_cluster(self):
        """Store cluster's events"""
        simulations = self.client[DATABASE][SIMULATION].find({}).sort('$natural', -1).limit(1)
        if simulations:
            simulation = next(simulations)
            simulation_id = simulation['_id']
            search_dict = {'simulation_id': simulation_id, 'is_applied': True}
            return self.client[DATABASE][CLUSTER_QUEUE].find(search_dict).sort('$natural', -1).limit(1)
        return None

    def clear_clusters(self, simulation_id=None):
        """Clear clusters"""
        search_dict = {}
        if simulation_id:
            search_dict['simulation_id'] = simulation_id
        return self.client[DATABASE][CLUSTER_QUEUE].delete_many(search_dict)

    def clear_states(self, simulation_id=None):
        """Clear states """
        search_dict = {}
        if simulation_id:
            search_dict['simulation_id'] = simulation_id
        return self.client[DATABASE][STATE_QUEUE].delete_many(search_dict)

    def clear_agents(self, simulation_step_id=None, simulation_id=None):
        """Clear agents """
        search_dict = {}
        if simulation_id:
            search_dict['simulation_id'] = simulation_id
        if simulation_step_id:
            search_dict['simulation_step_id'] = simulation_step_id
        return self.client[DATABASE][AGENTS].delete_many(search_dict)

    def clear_simulation_step(self, simulation_step_id=None, simulation_id=None):
        """Clear simulation_step """
        search_dict = {}
        if simulation_step_id:
            search_dict['_id'] = simulation_step_id
        if simulation_id:
            search_dict['simulation_id'] = simulation_id
        return self.client[DATABASE][SIMULATION_STEP].delete_many(search_dict)

    def clear_simulation(self, simulation_id=None):
        """Clear simulation """
        search_dict = {}
        if simulation_id:
            search_dict['_id'] = simulation_id
        return self.client[DATABASE][SIMULATION].delete_many(search_dict)
