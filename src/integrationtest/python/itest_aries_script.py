import imp
import io
import os
import shutil
import unittest
from contextlib import redirect_stdout, redirect_stderr

import integrationtest_utils
from integration_test_support import MongoTemporaryInstance, RedisTemporaryInstance

# Please don't remove this imports from this test
from aries.core.config.config import Config
from aries.core import utils
from aries.core.constants import LINEAR_SOLVER
from aries.core.db.mongodb import MongoDB
from aries.core.exceptions import ValidationError
from aries.core.log import log
from aries.simulation.run_simulation import run_simulation

aries = imp.load_source('aries', 'src/main/scripts/aries')

GRID_ELEMENTS = "grid_elements.json"
TOPOLOGY = "topology.json"
ARIES_CONFIG = "aries.json"


def run_aries(argv, external_mongodb_client=None, external_redis_client=None):
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout):
        with redirect_stderr(stderr):
            aries.main(argv=['aries', *argv], external_mongodb_client=external_mongodb_client,
                       external_redis_client=external_redis_client)
    return stdout.getvalue(), stderr.getvalue()


class Test(unittest.TestCase):

    def test_help(self):
        stdout, stderr = run_aries(['--help'])
        self.assertTrue('--conf' in stdout, 'Could not find --conf key')
        self.assertTrue('--validate' in stdout, 'Could not find --validate key')
        self.assertTrue('--version' in stdout, 'Could not find --version key')

    def test_run_without_parameters(self):
        stdout, stderr = run_aries([])
        self.assertTrue('--conf' in stdout, 'Could not find --conf key')
        self.assertTrue('--validate' in stdout, 'Could not find --validate key')
        self.assertTrue('--version' in stdout, 'Could not find --version key')

    def test_validate_simulation(self):
        stdout, stderr = run_aries(
            ['--conf', 'src/integrationtest/python/resources/itest_aries_script/aries.json',
             '--validate'])
        self.assertTrue('Agent' in stdout, 'Could not find Agent validation')
        self.assertTrue('Line' in stdout, 'Could not find Line validation')
        self.assertTrue('Path' in stdout, 'Could not find Path validation')
        self.assertTrue('Node' in stdout, 'Could not find Node validation')
        self.assertTrue('Validation is ok.' in stdout, 'Validation is not ok')

    def test_if_config_file_is_wrong(self):
        stdout, stderr = run_aries(['--conf', 'wrong_path_to_config', '--validate'])
        self.assertTrue("Could not find file 'wrong_path_to_config' " in stderr,
                        'Wrong path is not processed correctly')

    def test_if_config_file_has_wrong_grid_elements_path(self):
        stdout, stderr = run_aries(['--conf',
                                    'src/integrationtest/python/resources/itest_aries_script'
                                    '/aries_wrong_grid_elements_path.json',
                                        '--validate'])
        self.assertTrue("Could not find file 'wrong_grid_elements' " in stderr,
                        'Wrong paths of grid_elements in config is not processed correctly.')

    def test_if_config_file_has_wrong_topology_path(self):
        stdout, stderr = run_aries(['--conf',
                                    'src/integrationtest/python/resources/itest_aries_script'
                                    '/aries_wrong_topology_path.json',
                                        '--validate'])
        self.assertTrue("Could not find file 'wrong_topology_path' " in stderr,
                        'Wrong paths of topology in config is not processed correctly.')

    def test_if_config_file_is_empty_json(self):
        stdout, stderr = run_aries(['--conf',
                                    'src/integrationtest/python/resources/itest_aries_script'
                                    '/aries_empty_json.json',
                                        '--validate'])
        self.assertTrue(
            "Config is not valid. Please take a look to these field(s) : {'grid_elements': ['required field'], "
            "'topology': ['required field']}" in stderr,
            'Empty config is not processed properly')

    def test_if_config_file_is_empty(self):
        stdout, stderr = run_aries(['--conf',
                                    'src/integrationtest/python/resources/itest_aries_script/aries_empty'
                                        '.json',
                                        '--validate'])
        self.assertTrue(
            "Config is not valid. Please take a look to these field(s) : {'grid_elements': ['required field'], "
            "'topology': ['required field']}" in stderr,
            'Empty config is not processed properly')

    def test_if_number_of_agent_and_paths_are_different_agent(self):
        stdout, stderr = run_aries(['--conf',
                                    'src/integrationtest/python/resources/itest_aries_script'
                                    '/aries_vary_agents_from_paths.json',
                                        '--validate'])
        self.assertTrue(
            "Agent names is not the same. Please check these name(s): {'AGENT2'} in grid elements paths." in
            stderr,
            'Different number of agents and paths is not processed correctly.')

    def test_if_number_of_paths_and_agents_are_different_agent(self):
        stdout, stderr = run_aries(['--conf',
                                    'src/integrationtest/python/resources/itest_aries_script'
                                    '/aries_vary_paths_from_agents.json',
                                        '--validate'])
        self.assertTrue(
            "Path agent names is not the same. Please check these name(s): {'AGENT2'} in topology paths." in
            stderr,
            'Different number of agents and paths is not processed correctly.')

    def test_with_wrong_arguments(self):
        stdout, stderr = run_aries(['--asdfs'])
        self.assertTrue(
            "unrecognized arguments:" in
            stderr,
            'Wrong arguments is not processed correctly.')

    def test_if_simulation_can_start(self):
        if shutil.which('monogod') and shutil.which('redis-server'):
            mongodb_client = MongoTemporaryInstance.get_instance().client
            redis_client = RedisTemporaryInstance.get_instance().client
            stdout, stderr = run_aries(argv=['--conf',
                                             'src/integrationtest/python/resources/itest_aries_script'
                                             '/aries.json'],
                                       external_mongodb_client=mongodb_client,
                                       external_redis_client=redis_client)
            self.assertEquals(len(stdout.split('\n')), 101, 'Simulation does not run properly')

    @classmethod
    def tearDownClass(cls):
        if os.path.exists("errors.log"):
            os.remove("errors.log")
        if os.path.exists("aries.log"):
            os.remove("aries.log")


if __name__ == '__main__':
    if integrationtest_utils.is_storage_exists() and integrationtest_utils.is_event_queue_exists():
        unittest.main()
