import json
import shutil
import unittest

from bson import ObjectId

import integrationtest_utils
from integration_test_support import MongoTemporaryInstance
from aries.controller import cluster_utils
from aries.core.db.mongodb import *
from aries.core.grid import grid_utils
from aries.core.grid.agent import Agent
from aries.core.grid.line import Line
from aries.core.grid.state import State
from aries.core.grid.topology import Node, Path

GRID_ELEMENT_FILE = "grid_elements.json"
SOLVER_TEST_TOPOLOGY = "topology.json"
STATES_FILE = "state.json"
CLUSTERS_FILE = "clusters.json"
SIMULATION_STEP_NUMBER = 10
SIMULATION_STEP_ID = ObjectId()
SIMULATION_ID_1 = ObjectId()
SIMULATION_ID_2 = ObjectId()
SIMULATION_ID_3 = ObjectId()
SOLVER = "linear_solver"
NUMBER_OF_CLUSTERS = 100
TOTAL_PV_POWER = 1234.4324

class TestMongoDB(unittest.TestCase):
    """TestCase with an embedded MongoDB temporary instance."""

    def setUp(self):
        self.client = MongoTemporaryInstance.get_instance().client
        self.storage = MongoDB(client=self.client)
        with integrationtest_utils.readfile(GRID_ELEMENT_FILE, __file__) as f:
            j = json.load(f)
            self.agents, self.lines = grid_utils.create_grid_elements(j)

    def tearDown(self):
        self.storage.clear_agents()
        self.storage.clear_clusters()
        self.storage.clear_states()
        self.storage.clear_simulation_step()
        self.storage.clear_simulation()

    def test_if_agents_is_stored(self):
        """Store agent object to DB and read it"""
        self.storage.write_agents(self.agents, SIMULATION_STEP_ID, SIMULATION_ID_1)
        db = self.client[DATABASE]
        coll = db[AGENTS]
        stored_agent_obj = coll.find_one({'name': "AGENT1"})
        self.assertTrue(Agent.validate(json.loads(stored_agent_obj["agent"])), "Agent is not valid")

    def test_if_simulation_step_is_stored(self):
        """Store agent object to DB and read it"""
        self.storage.write_simulation_step(simulation_step=SIMULATION_STEP_NUMBER, simulation_id=SIMULATION_ID_1,
                                           simulation_result={}, agents_states={}, total_pv_power=TOTAL_PV_POWER)
        db = self.client[DATABASE]
        coll = db[SIMULATION_STEP]
        self.assertTrue(coll.count_documents({}) > 0, "Simulation step was not stored")
        stored_agent_obj = coll.find_one({'simulation_step': SIMULATION_STEP_NUMBER})
        self.assertTrue(stored_agent_obj is not None, "Could not find simulation step by simulation_step_id.")

    def test_if_states_is_stored(self):
        """Store states to DB and read it"""
        with integrationtest_utils.readfile(STATES_FILE, __file__) as f:
            j = json.load(f)
            state = State.load(j)

        self.storage.write_states(states={'states': {'AGENT0': state.dump(), 'AGENT1': state.dump()}},
                                  simulation_step=SIMULATION_STEP_NUMBER, simulation_id=SIMULATION_ID_1,
                                  is_applied=True)
        db = self.client[DATABASE]
        coll = db[STATE_QUEUE]
        self.assertTrue(coll.count_documents({}) > 0, "States were not stored")
        stored_agent_obj = coll.find_one({'simulation_step': SIMULATION_STEP_NUMBER})
        self.assertTrue(stored_agent_obj is not None, "Could not find states step by simulation_step_id.")

    def test_if_clusters_is_stored(self):
        """Store states to DB and read it"""
        with integrationtest_utils.readfile(CLUSTERS_FILE, __file__) as f:
            j = json.load(f)
            clusters = cluster_utils.create_clusters(j)

        clusters_dict = {}
        for name, cluster in clusters.items():
            clusters_dict[name] = cluster.dump()

        self.storage.write_clusters(clusters={'clusters': clusters_dict},
                                    simulation_step=SIMULATION_STEP_NUMBER, simulation_id=SIMULATION_ID_1,
                                    is_applied=True)
        db = self.client[DATABASE]
        coll = db[CLUSTER_QUEUE]
        self.assertTrue(coll.count_documents({}) > 0, "Clusters were not stored")
        stored_agent_obj = coll.find_one({'simulation_step': SIMULATION_STEP_NUMBER})
        self.assertTrue(stored_agent_obj is not None, "Could not find clusters step by simulation_step_id.")

    def test_if_multiple_states_are_stored(self):
        with integrationtest_utils.readfile(CLUSTERS_FILE, __file__) as f:
            j = json.load(f)
            clusters = cluster_utils.create_clusters(j)

        clusters_dict = {}
        for name, cluster in clusters.items():
            clusters_dict[name] = cluster.dump()

        for i in range(NUMBER_OF_CLUSTERS):
            is_applied = ((SIMULATION_STEP_NUMBER + i) % 2 == 1)

            self.storage.write_clusters(clusters={'clusters': clusters_dict},
                                        simulation_step=SIMULATION_STEP_NUMBER + i,
                                        simulation_id=SIMULATION_ID_1, is_applied=is_applied)

        cluster_collection = self.client[DATABASE][CLUSTER_QUEUE]
        self.assertEqual(cluster_collection.count_documents({}), NUMBER_OF_CLUSTERS, 'Number of cluster is not correct')

        result_simulation_id = self.storage.read_clusters(SIMULATION_ID_1)
        count = 0
        for result in result_simulation_id:
            count += 1
        self.assertEqual(count, NUMBER_OF_CLUSTERS, 'Number of cluster is not correct')

        result_simulation_step = self.storage.read_clusters(simulation_id=SIMULATION_ID_1,
                                                            simulation_step=(SIMULATION_STEP_NUMBER + 50))
        cluster_data = next(result_simulation_step, None)
        self.assertEqual(cluster_data['simulation_step'], 60, "Don't find correct cluster")

        result_simulation_step_applied = self.storage.read_clusters(simulation_id=SIMULATION_ID_1, is_applied=True)

        for result in result_simulation_step_applied:
            self.assertTrue(result['is_applied'], 'cluster.is_applied property is not verified')
            self.assertTrue(result['simulation_step'] % 2 == 1, 'Simulation step is not verified')

    def test_if_multiple_clusters_are_stored(self):
        with integrationtest_utils.readfile(CLUSTERS_FILE, __file__) as f:
            j = json.load(f)
            clusters = cluster_utils.create_clusters(j)

        clusters_dict = {}
        for name, cluster in clusters.items():
            clusters_dict[name] = cluster.dump()

        for i in range(NUMBER_OF_CLUSTERS):
            is_applied = ((SIMULATION_STEP_NUMBER + i) % 2 == 1)

            self.storage.write_clusters(clusters={'clusters': clusters_dict},
                                        simulation_step=SIMULATION_STEP_NUMBER + i,
                                        simulation_id=SIMULATION_ID_1, is_applied=is_applied)

        cluster_collection = self.client[DATABASE][CLUSTER_QUEUE]
        self.assertEqual(cluster_collection.count_documents({}), NUMBER_OF_CLUSTERS, 'Number of cluster is not correct')

        result_simulation_id = self.storage.read_clusters(SIMULATION_ID_1)
        count = 0
        for result in result_simulation_id:
            count += 1
        self.assertEqual(count, NUMBER_OF_CLUSTERS, 'Number of cluster is not correct')

        result_simulation_step = self.storage.read_clusters(simulation_id=SIMULATION_ID_1,
                                                            simulation_step=(SIMULATION_STEP_NUMBER + 50))
        cluster_data = next(result_simulation_step, None)
        self.assertEqual(cluster_data['simulation_step'], 60, "Don't find correct cluster")

        result_simulation_step_applied = self.storage.read_clusters(simulation_id=SIMULATION_ID_1, is_applied=True)

        for result in result_simulation_step_applied:
            self.assertTrue(result['is_applied'], 'cluster.is_applied property is not verified')
            self.assertTrue(result['simulation_step'] % 2 == 1, 'Simulation step is not verified')

    def test_if_cluster_get_properly(self):
        with integrationtest_utils.readfile(CLUSTERS_FILE, __file__) as f:
            j = json.load(f)
            clusters = cluster_utils.create_clusters(j)

        clusters_dict = {}
        for name, cluster in clusters.items():
            clusters_dict[name] = cluster.dump()

        self.storage.write_clusters(clusters=clusters_dict, simulation_step=SIMULATION_STEP_NUMBER,
                                    simulation_id=SIMULATION_ID_1, is_applied=True)
        self.assertEqual(self.client[DATABASE][CLUSTER_QUEUE].count_documents({}), 1,
                         'Clusters was not stored properly')
        clusters = self.storage.get_last_cluster_for_simulation_id(simulation_id=SIMULATION_ID_1)
        cluster = next(clusters, None)
        clusters = cluster['clusters']
        for name, cluster in clusters.items():
            print(name)
            print(json.loads(cluster))

    def test_if_cluster_clear_properly(self):
        with integrationtest_utils.readfile(CLUSTERS_FILE, __file__) as f:
            j = json.load(f)
            clusters = cluster_utils.create_clusters(j)

        clusters_dict = {}
        for name, cluster in clusters.items():
            clusters_dict[name] = cluster.dump()

        self.storage.write_clusters(clusters={'clusters': clusters_dict}, simulation_step=SIMULATION_STEP_NUMBER,
                                    simulation_id=SIMULATION_ID_1, is_applied=True)
        self.storage.clear_clusters(simulation_id=SIMULATION_ID_1)
        self.assertEqual(self.client[DATABASE][CLUSTER_QUEUE].count_documents({}), 0,
                         'Clear clusters does not work properly')

        self.storage.write_clusters(clusters={'clusters': clusters_dict}, simulation_step=SIMULATION_STEP_NUMBER,
                                    simulation_id=SIMULATION_ID_1, is_applied=True)
        self.storage.write_clusters(clusters={'clusters': clusters_dict}, simulation_step=SIMULATION_STEP_NUMBER,
                                    simulation_id=SIMULATION_ID_2, is_applied=True)
        self.storage.write_clusters(clusters={'clusters': clusters_dict}, simulation_step=SIMULATION_STEP_NUMBER,
                                    simulation_id=SIMULATION_ID_3, is_applied=True)

        self.assertEqual(self.client[DATABASE][CLUSTER_QUEUE].count_documents({}), 3,
                         'Number of clusters is not correct')
        self.storage.clear_clusters(simulation_id=SIMULATION_ID_1)
        self.assertEqual(self.client[DATABASE][CLUSTER_QUEUE].count_documents({}), 2,
                         'Clear clusters does not work properly')
        self.storage.clear_clusters()
        self.assertEqual(self.client[DATABASE][CLUSTER_QUEUE].count_documents({}), 0,
                         'Clear clusters does not work properly')

    def test_if_state_clear_properly(self):
        with integrationtest_utils.readfile(STATES_FILE, __file__) as f:
            j = json.load(f)
            state = State.load(j)

        self.storage.write_states(states={'states': {'AGENT0': state.dump(), 'AGENT1': state.dump()}},
                                  simulation_step=SIMULATION_STEP_NUMBER, simulation_id=SIMULATION_ID_1,
                                  is_applied=True)

        self.storage.clear_states(simulation_id=SIMULATION_ID_1)

        self.assertEqual(self.client[DATABASE][STATE_QUEUE].count_documents({}), 0,
                         'Clear states does not work properly')

        self.storage.write_states(states={'states': {'AGENT0': state.dump(), 'AGENT1': state.dump()}},
                                  simulation_step=SIMULATION_STEP_NUMBER, simulation_id=SIMULATION_ID_1,
                                  is_applied=True)
        self.storage.write_states(states={'states': {'AGENT0': state.dump(), 'AGENT1': state.dump()}},
                                  simulation_step=SIMULATION_STEP_NUMBER, simulation_id=SIMULATION_ID_2,
                                  is_applied=True)
        self.storage.write_states(states={'states': {'AGENT0': state.dump(), 'AGENT1': state.dump()}},
                                  simulation_step=SIMULATION_STEP_NUMBER, simulation_id=SIMULATION_ID_3,
                                  is_applied=True)

        self.assertEqual(self.client[DATABASE][STATE_QUEUE].count_documents({}), 3,
                         'Number of states is not correct')
        self.storage.clear_states(simulation_id=SIMULATION_ID_1)
        self.assertEqual(self.client[DATABASE][STATE_QUEUE].count_documents({}), 2,
                         'Clear states does not work properly')
        self.storage.clear_states()
        self.assertEqual(self.client[DATABASE][STATE_QUEUE].count_documents({}), 0,
                         'Clear states does not work properly')

    def test_if_simulation_clear_properly(self):
        with integrationtest_utils.readfile(SOLVER_TEST_TOPOLOGY, __file__) as f:
            j = json.load(f)
            paths, nodes = grid_utils.create_topology(j)

        simulation_id = self.storage.write_simulation(agents=self.agents, lines=self.lines, paths=paths, nodes=nodes,
                                                      solver=SOLVER)
        self.storage.clear_simulation(simulation_id=simulation_id)

        self.assertEqual(self.client[DATABASE][SIMULATION].count_documents({}), 0,
                         'Clear simulation does not work properly')

        simulation_id_1 = self.storage.write_simulation(agents=self.agents, lines=self.lines, paths=paths, nodes=nodes,
                                                        solver=SOLVER)
        self.storage.write_simulation(agents=self.agents, lines=self.lines, paths=paths, nodes=nodes,
                                      solver=SOLVER)
        self.storage.write_simulation(agents=self.agents, lines=self.lines, paths=paths, nodes=nodes,
                                      solver=SOLVER)

        self.assertEqual(self.client[DATABASE][SIMULATION].count_documents({}), 3,
                         'Number of simulation is not correct')
        self.storage.clear_simulation(simulation_id=simulation_id_1)
        self.assertEqual(self.client[DATABASE][SIMULATION].count_documents({}), 2,
                         'Clear simulation does not work properly')
        self.storage.clear_simulation()
        self.assertEqual(self.client[DATABASE][SIMULATION].count_documents({}), 0,
                         'Clear simulation does not work properly')

    def test_if_simulation_step_clear_properly(self):
        simulation_step_id = self.storage.write_simulation_step(simulation_step=SIMULATION_STEP_NUMBER,
                                                                simulation_id=SIMULATION_ID_1,
                                                                simulation_result={'result': 'some_result'},
                                                                agents_states={'states': 'some_states'},
                                                                total_pv_power=TOTAL_PV_POWER)

        self.storage.clear_simulation_step(simulation_step_id=simulation_step_id)

        self.assertEqual(self.client[DATABASE][SIMULATION_STEP].count_documents({}), 0,
                         'Clear simulation step does not work properly')

        self.storage.write_simulation_step(simulation_step=SIMULATION_STEP_NUMBER,
                                           simulation_id=SIMULATION_ID_1,
                                           simulation_result={'result': 'some_result'},
                                           agents_states={'states': 'some_states'},
                                           total_pv_power=TOTAL_PV_POWER)

        self.storage.write_simulation_step(simulation_step=SIMULATION_STEP_NUMBER,
                                           simulation_id=SIMULATION_ID_1,
                                           simulation_result={'result': 'some_result'},
                                           agents_states={'states': 'some_states'},
                                           total_pv_power=TOTAL_PV_POWER)

        self.storage.write_simulation_step(simulation_step=SIMULATION_STEP_NUMBER,
                                           simulation_id=SIMULATION_ID_2,
                                           simulation_result={'result': 'some_result'},
                                           agents_states={'states': 'some_states'},
                                           total_pv_power=TOTAL_PV_POWER)
        self.storage.write_simulation_step(simulation_step=SIMULATION_STEP_NUMBER,
                                           simulation_id=SIMULATION_ID_3,
                                           simulation_result={'result': 'some_result'},
                                           agents_states={'states': 'some_states'},
                                           total_pv_power=TOTAL_PV_POWER)

        self.assertEqual(self.client[DATABASE][SIMULATION_STEP].count_documents({}), 4,
                         'Number of simulation step is not correct')
        self.storage.clear_simulation_step(simulation_id=SIMULATION_ID_1)

        self.assertEqual(self.client[DATABASE][SIMULATION_STEP].count_documents({}), 2,
                         'Clear simulation step does not work properly')
        self.storage.clear_simulation_step()
        self.assertEqual(self.client[DATABASE][SIMULATION_STEP].count_documents({}), 0,
                         'Clear simulation step does not work properly')

    def test_if_agent_clear_properly(self):
        self.storage.write_agents(self.agents, SIMULATION_STEP_ID, SIMULATION_ID_1)
        self.storage.clear_agents(simulation_step_id=SIMULATION_STEP_ID)
        self.assertEqual(self.client[DATABASE][AGENTS].count_documents({}), 0,
                         'Clear agents does not work properly')

        self.storage.write_agents(agents=self.agents, simulation_step_id=SIMULATION_STEP_ID,
                                  simulation_id=SIMULATION_ID_1)
        self.storage.write_agents(agents=self.agents, simulation_step_id=ObjectId(), simulation_id=SIMULATION_ID_1)
        self.storage.write_agents(agents=self.agents, simulation_step_id=ObjectId(), simulation_id=SIMULATION_ID_2)
        self.storage.write_agents(agents=self.agents, simulation_step_id=ObjectId(), simulation_id=SIMULATION_ID_3)

        self.assertEqual(self.client[DATABASE][AGENTS].count_documents({}), 4,
                         'Number of agents is not correct')
        self.storage.clear_agents(simulation_id=SIMULATION_ID_1)

        self.assertEqual(self.client[DATABASE][AGENTS].count_documents({}), 2,
                         'Clear agents does not work properly')
        self.storage.clear_agents()
        self.assertEqual(self.client[DATABASE][AGENTS].count_documents({}), 0,
                         'Clear agents does not work properly')

    def test_if_simulation_is_stored(self):
        """Store simulation to DB and verify"""
        with integrationtest_utils.readfile(SOLVER_TEST_TOPOLOGY, __file__) as f:
            j = json.load(f)
            paths, nodes = grid_utils.create_topology(j)
        simulation_id = self.storage.write_simulation(agents=self.agents, lines=self.lines, paths=paths, nodes=nodes,
                                                      solver=SOLVER)

        db = self.client[DATABASE]
        coll = db[SIMULATION]

        simulation = coll.find_one({"_id": simulation_id})

        for name, agent in simulation['agents'].items():
            self.assertTrue(Agent.validate(json.loads(agent)), "Agent is not valid")

        for name, node in simulation['lines'].items():
            self.assertTrue(Line.validate(json.loads(node)), "Line is not valid")

        for name, path in simulation['paths'].items():
            self.assertTrue(Path.validate_list(json.loads(path)), "Path is not valid")

        for name, node in simulation['nodes'].items():
            self.assertTrue(Node.validate(json.loads(node)), "Node is not valid")

        self.assertEqual(simulation['solver'], SOLVER, "Solver is not valid")


if __name__ == '__main__':
    if integrationtest_utils.is_storage_exists():
        unittest.main()
