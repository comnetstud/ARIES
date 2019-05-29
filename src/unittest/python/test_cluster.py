import json
import unittest

import unittest_utils
from aries import controller
from aries.controller import cluster_utils
from aries.controller.cluster import Cluster
from aries.core.exceptions import ValidationError

NAME = "Line1"
CLUSTER_AGENTS = ["A1", "A2"]
CONTROLLER = "LoadSharingCluster"
PRIORITY = 100
DELAY = 5

CLUSTER = 'clusters.json'
CLUSTER_EMPTY = 'cluster_empty.json'
CLUSTER_WITH_AGENT_OVERLAPPING = 'cluster_with_agent_overlapping.json'
CLUSTER_WRONG_CONTROLLER = 'cluster_wrong_controller.json'


class TestCluster(unittest.TestCase):
    """Tests for Cluster"""

    def setUp(self):
        self.cluster = Cluster.from_properties(name=NAME, cluster_agents=CLUSTER_AGENTS, controller=CONTROLLER,
                                               priority=PRIORITY,
                                               delay=DELAY)

    def test_assigned_properties(self):
        self.assertEqual(self.cluster.name, NAME, "name is not equal")
        self.assertEqual(self.cluster.cluster_agents, CLUSTER_AGENTS, "agents is not equal")
        self.assertEqual(self.cluster.controller, CONTROLLER, "controller is not equal")
        self.assertEqual(self.cluster.priority, PRIORITY, "priority is not equal")
        self.assertEqual(self.cluster.delay, DELAY, "delay is not equal")


class TestClusterConfig(unittest.TestCase):
    """Tests for Cluster initializer"""

    def test_if_all_properties_read(self):
        with unittest_utils.readfile(CLUSTER, __file__) as f:
            j = json.load(f)
            clusters = cluster_utils.create_clusters(j)
            self.assertTrue(isinstance(clusters['cluster0'], controller.cluster.LoadSharingCluster),
                            'LoadSharingCluster type is not initialized')
            self.assertTrue(isinstance(clusters['cluster1'], controller.cluster.StayingAliveCluster),
                            'StayingAliveCluster type is not initialized')

    def test_if_config_is_empty(self):
        with unittest_utils.readfile(CLUSTER_EMPTY, __file__) as f:
            j = json.load(f)
            cluster_utils.create_clusters(j)

    def test_if_config_has_wrong_controller(self):
        with unittest_utils.readfile(CLUSTER_WRONG_CONTROLLER, __file__) as f:
            j = json.load(f)
            with self.assertRaises(AttributeError):
                cluster_utils.create_clusters(j)

    def test_if_config_has_overlapped_agents(self):
        with unittest_utils.readfile(CLUSTER_WITH_AGENT_OVERLAPPING, __file__) as f:
            j = json.load(f)
            with self.assertRaises(ValidationError):
                cluster_utils.create_clusters(j)

    def test_cluster_serialization(self):
        with unittest_utils.readfile(CLUSTER, __file__) as f:
            j = json.load(f)
            clusters = cluster_utils.create_clusters(j)

            for name, cluster in clusters.items():
                cluster_dumped = cluster.dump()
                cluster_dict = json.loads(cluster_dumped)
                self.assertTrue(Cluster.validate(cluster_dict),
                                'Cluster is not valid after serialization/deserialization')
