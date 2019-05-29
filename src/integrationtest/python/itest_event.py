import json
import shutil
import unittest

import integrationtest_utils
from aries.controller import cluster_utils
from aries.controller.cluster import Cluster
from aries.core.event.event_queue import EventQueue, CLUSTER_QUEUE
from aries.core.grid.state import State
from integration_test_support import RedisTemporaryInstance

STATES = 'states.json'
CLUSTERS = 'clusters.json'
AGENT_NAME = 'agent_12345'
CLUSTER_NAME = 'cluster0'
EVENT_QUEUE = 'event_queue'
ANOTHER_EVENT_QUEUE = 'another_event_queue'
TEST_QUEUE_NUMBER = 100


class TestEvent(unittest.TestCase):
    """TestCase with an redislite - lightweight python implementation of redis."""

    def setUp(self):
        self.redis = RedisTemporaryInstance.get_instance().client
        self.event_queue = EventQueue(redis=self.redis)
        self.event_queue.cleanup()

    def test_read_and_write_states_events(self):
        """Write and read event from redis"""
        with integrationtest_utils.readfile(STATES, __file__) as f:
            j = json.load(f)
            state = State(j)

            self.event_queue.write_states(states={'states': {AGENT_NAME: state.dump()}})

            ev = self.event_queue.read_states()
            ev = ev['states']
            agent_name = next(iter(ev))
            state = ev[agent_name]
            self.assertEqual(agent_name, AGENT_NAME, "Agent name is not equal")
            self.assertTrue(State.validate(json.loads(state)), "State is not valid")

    def test_read_and_write_clusters_events(self):
        """Write and read event from redis"""
        with integrationtest_utils.readfile(CLUSTERS, __file__) as f:
            j = json.load(f)
            clusters = cluster_utils.create_clusters(j)

            clusters_dict = {}
            for name, cluster in clusters.items():
                clusters_dict[name] = cluster.dump()

            self.event_queue.write_clusters(clusters={'clusters': clusters_dict})

            ev = self.event_queue.read_clusters()
            ev = ev['clusters']
            cluster_name = next(iter(ev))
            cluster = json.loads(ev[cluster_name])
            self.assertEqual(cluster_name, CLUSTER_NAME, "Cluster name is not equal")
            self.assertTrue(Cluster.validate(cluster), 'Cluster is not valid')

    def test_wrong_event_queue(self):
        """Write data to ANOTHER_EVENT_QUEUE but read it from EVENT_QUEUE and check the result"""
        with integrationtest_utils.readfile(STATES, __file__) as f:
            j = json.load(f)
            state = State(j)

            self.event_queue.write_states(states={'states': {AGENT_NAME: state.dump()}})

            ev = self.event_queue.read_clusters()
            self.assertIsNone(ev, "Read state from clusters queue")

            ev = self.event_queue.read_states()
            self.assertIsNotNone(ev, "Could not read event from states queue")

    def test_read_and_write_multiple_state_events(self):
        """Write TEST_QUEUE_NUMBER states to redis and read it afterwards"""
        with integrationtest_utils.readfile(STATES, __file__) as f:
            j = json.load(f)
            state = State(j)

            for i in range(TEST_QUEUE_NUMBER):
                state.power_factor += i
                self.event_queue.write_states(states={'states': {AGENT_NAME: state.dump()}})

        self.assertEqual(self.redis.llen(EVENT_QUEUE), TEST_QUEUE_NUMBER, "Number of objects in Redis is different")
        for i in range(TEST_QUEUE_NUMBER):
            ev = self.event_queue.read_states()
            for agent_name, state in ev['states'].items():
                self.assertTrue(State.validate(json.loads(state)), "State is not valid")

    def test_read_and_write_multiple_cluster_events(self):
        """Write TEST_QUEUE_NUMBER states to redis and read it afterwards"""
        with integrationtest_utils.readfile(CLUSTERS, __file__) as f:
            j = json.load(f)
            clusters = cluster_utils.create_clusters(j)

            clusters_dict = {}
            for name, cluster in clusters.items():
                clusters_dict[name] = cluster.dump()

            for i in range(TEST_QUEUE_NUMBER):
                self.event_queue.write_clusters(clusters={'clusters': clusters_dict})
        self.assertEqual(self.redis.llen(CLUSTER_QUEUE), TEST_QUEUE_NUMBER, "Number of objects in Redis is different")

        for i in range(TEST_QUEUE_NUMBER):
            ev = self.event_queue.read_clusters()
            for name, cluster in ev['clusters'].items():
                self.assertTrue(Cluster.validate(json.loads(cluster)), "State is not valid")

    def test_cleanup(self):
        """Test cleanup method"""
        with integrationtest_utils.readfile(STATES, __file__) as f:
            j = json.load(f)
            state = State(j)

            for i in range(TEST_QUEUE_NUMBER):
                state.power_factor += i
                self.event_queue.write_states(states={'states': {AGENT_NAME: state.dump()}})

        with integrationtest_utils.readfile(CLUSTERS, __file__) as f:
            j = json.load(f)
            clusters = cluster_utils.create_clusters(j)

            clusters_dict = {}
            for name, cluster in clusters.items():
                clusters_dict[name] = cluster.dump()

            for i in range(TEST_QUEUE_NUMBER):
                self.event_queue.write_clusters(clusters={'clusters': clusters_dict})

        self.event_queue.cleanup()

        self.assertEqual(self.redis.llen(EVENT_QUEUE), 0, "Number of objects in Redis is different")
        self.assertEqual(self.redis.llen(CLUSTER_QUEUE), 0, "Number of objects in Rfedis is diferent")


if __name__ == '__main__':
    if integrationtest_utils.is_event_queue_exists():
        unittest.main()
