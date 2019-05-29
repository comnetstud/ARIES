"""
    This module provides a IntegrationTestServerFixture which runs a
    IntegrationTestServer on "http://127.0.0.1:5000/".
"""

import atexit
import os
import shutil
import subprocess
import tempfile
import time
from multiprocessing import Process
from time import sleep

import pymongo
import redis
import requests
from pyfix import Fixture
from pymongo.errors import ConnectionFailure

import integrationtest_utils
from aries.core.db import mongodb
from aries.core.db.mongodb import MongoDB
from aries.core.event.event_queue import EventQueue

MONGODB_TEST_PORT = 12345
REDIS_TEST_PORT = 12346

os.environ['MONGO_URI'] = 'mongodb://mongo:27017'
os.environ['REDIS_HOST'] = 'redis'
os.environ['REDIS_PORT'] = '6379'

import aries.api.webapp as webapp


class IntegrationTestServer(object):

    def __init__(self):
        mongodb_client = MongoTemporaryInstance.get_instance().client
        redis_client = RedisTemporaryInstance.get_instance().client
        self.event_queue = EventQueue(redis=redis_client)
        self.storage = MongoDB(client=mongodb_client)

        sleep(1)

        app = webapp.create_app()

        self._process = Process(target=app.run)
        self._process.start()

        sleep(1)

    def stop(self):
        self._process.terminate()

    def get_page(self, url):
        return requests.get('http://127.0.0.1:5000' + url)

    def post_page(self, url, data):
        return requests.post(url='http://127.0.0.1:5000' + url, json=data)


class IntegrationTestServerFixture(Fixture):

    def reclaim(self, integration_test_server):
        integration_test_server.stop()

    def provide(self):
        return [IntegrationTestServer()]


class MongoTemporaryInstance(object):
    """Singleton to manage a temporary MongoDB instance

    Use this for testing purpose only. The instance is automatically destroyed
    at the end of the program.

    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            atexit.register(cls._instance.shutdown)
        return cls._instance

    def __init__(self):
        if integrationtest_utils.mongodb_test_url():
            self._client = pymongo.MongoClient(integrationtest_utils.mongodb_test_url())
            self._client.drop_database(mongodb.DATABASE)
        else:
            self._tmpdir = tempfile.mkdtemp()
            self._process = subprocess.Popen(['mongod', '--bind_ip', 'localhost',
                                              '--port', str(MONGODB_TEST_PORT),
                                              '--dbpath', self._tmpdir,
                                              '--nojournal',
                                              '--noauth', '--smallfiles',
                                              '--syncdelay', '0',
                                              '--maxConns', '10',
                                              '--nssize', '1', ],
                                             stdout=open(os.devnull, 'wb'),
                                             stderr=subprocess.STDOUT)

            # XXX: wait for the instance to be ready
            #      Mongo is ready in a glance, we just wait to be able to open a
            #      Connection.
            for i in range(3):
                time.sleep(0.1)
                try:
                    self._client = pymongo.MongoClient('localhost', MONGODB_TEST_PORT)
                except ConnectionFailure:
                    continue
                else:
                    break
            else:
                self.shutdown()
                assert False, 'Cannot connect to the mongodb test instance'

    @property
    def client(self):
        return self._client

    def shutdown(self):
        if self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None
            shutil.rmtree(self._tmpdir, ignore_errors=True)


class RedisTemporaryInstance(object):
    """Singleton to manage a temporary Redis instance

    Use this for testing purpose only. The instance is automatically destroyed
    at the end of the program.

    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            atexit.register(cls._instance.shutdown)
        return cls._instance

    def __init__(self):
        if integrationtest_utils.redis_test_url():
            self._client = redis.Redis(integrationtest_utils.redis_test_url(), integrationtest_utils.redis_test_port())
        else:
            self._tmpdir = tempfile.mkdtemp()
            self._process = subprocess.Popen(['redis-server',
                                              '--port', str(REDIS_TEST_PORT)],
                                             stdout=open(os.devnull, 'wb'),
                                             stderr=subprocess.STDOUT)

            # XXX: wait for the instance to be ready
            #      Redis is ready in a glance, we just wait to be able to open a
            #      Connection.
            for i in range(3):
                time.sleep(0.1)
                try:
                    self._client = redis.Redis('localhost', REDIS_TEST_PORT)
                except ConnectionFailure:
                    continue
                else:
                    break
            else:
                self.shutdown()
                assert False, 'Cannot connect to the redis test instance'

    @property
    def client(self):
        return self._client

    def shutdown(self):
        if self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None
