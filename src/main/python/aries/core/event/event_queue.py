import json

CLUSTER_QUEUE = 'cluster_queue'
EVENT_QUEUE = 'event_queue'


class EventQueue(object):
    redis = None

    def __init__(self, redis):
        self.redis = redis

    def cleanup(self):
        """Clear event queue"""
        self.redis.delete(CLUSTER_QUEUE)
        self.redis.delete(EVENT_QUEUE)

    def read_states(self):
        """Read one state event in one go"""
        event = self.redis.lpop(EVENT_QUEUE)
        if event is not None:
            return json.loads(event)
        return None

    def write_states(self, states):
        """Write event to queue"""
        event = json.dumps(states)
        self.redis.rpush(EVENT_QUEUE, event)

    def read_clusters(self):
        """Read one clusters event in one go"""
        event = self.redis.lpop(CLUSTER_QUEUE)
        if event is not None:
            return json.loads(event)
        return None

    def write_clusters(self, clusters):
        """Write clusters to queue"""
        event = json.dumps(clusters)
        self.redis.rpush(CLUSTER_QUEUE, event)
