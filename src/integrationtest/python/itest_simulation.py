import csv
import imp
import io
import json
import multiprocessing as mp
import os
import shutil
from contextlib import redirect_stdout, redirect_stderr
from time import sleep

from pyfix import given, test, run_tests

import integrationtest_utils
from integration_test_support import IntegrationTestServerFixture

# Please don't remove this imports from this test
from aries.core.config.config import Config
from aries.core import utils
from aries.core.constants import LINEAR_SOLVER
from aries.core.db.mongodb import MongoDB
from aries.core.exceptions import ValidationError
from aries.core.grid import grid_utils
from aries.core.grid.agent import Agent
from aries.core.grid.state import State
from aries.core.log import log
from aries.simulation.run_simulation import run_simulation

aries = imp.load_source('aries', 'src/main/scripts/aries')

GRID_ELEMENTS = "grid_elements.json"
TOPOLOGY = "topology.json"
ARIES_CONFIG = "aries.json"
STATE_FILE = 'state.json'

if integrationtest_utils.mongodb_test_url():
    os.environ['ARIES_CONF'] = integrationtest_utils.filepath('aries_gitlab.json', __file__)
else:
    os.environ['ARIES_CONF'] = integrationtest_utils.filepath('aries_local.json', __file__)


def run_aries(argv, external_mongodb_client=None, external_redis_client=None):
    aries.main(argv=['aries', *argv], external_mongodb_client=external_mongodb_client,
                   external_redis_client=external_redis_client)
    # stdout = io.StringIO()
    # stderr = io.StringIO()
    # with redirect_stdout(stdout):
    #     with redirect_stderr(stderr):
    #         aries.main(argv=['aries', *argv], external_mongodb_client=external_mongodb_client,
    #                        external_redis_client=external_redis_client)
    # return stdout.getvalue(), stderr.getvalue()


# @test
# @given(server=IntegrationTestServerFixture)
# def test_simulation_with_controllers(server):
#     """Put agent data to DB and retrieve it over API
#     """
#
#     os.environ['ARIES_CONF'] = integrationtest_utils.filepath('aries.json', __file__)
#
#     stdout, stderr = run_aries(
#         ['--conf', 'src/integrationtest/python/resources/itest_simulation/aries.json'])
#
#     # TODO: Add check for data here
#

# @test
# @given(server=IntegrationTestServerFixture)
# def test_simulation_with_controllers_and_async_calls_from_api(server):
#     """Put agent data to DB and retrieve it over API
#     """
#
#     with integrationtest_utils.readfile(STATE_FILE, __file__) as f:
#         j = json.load(f)
#         state = State(j)
#
#     p = mp.Process(target=run_aries,
#                    args=(['--conf', 'src/integrationtest/python/resources/itest_simulation/aries_10000.json'],))
#     p.start()
#
#     # Retrieve info from simulation
#     sleep(1)
#     data = server.get_page('/api/aries/simulation/active')
#     json_data = json.loads(data.content)
#     print(json_data)
#
#     for i in range(20):
#         sleep(1)
#
#         data = {'AGENT0': state.dump()}
#         server.post_page(url='/api/aries/state', data=data)
#
#         data = server.get_page('/api/aries/simulationstep/active')
#         json_data = json.loads(data.content)
#         print(json_data)
#
#         sleep(1)
#
#         data = {'AGENT1': state.dump()}
#         server.post_page(url='/api/aries/state', data=data)
#
#         data = server.get_page('/api/aries/simulationstep/active')
#         json_data = json.loads(data.content)
#         print(json_data)
#
#     p.join()
#
#     # Get & analyze data
#
#     server.storage.get_active_simulation_step()
#     data = server.get_page('/api/aries/simulation/active')
#     json_data = json.loads(data.content)
#
#     print(json_data)
#     server.storage.read_clusters()


@test
@given(server=IntegrationTestServerFixture)
def test_simulation_with_activate_things_in_agents(server):
    """Put agent data to DB and retrieve it over API
    """

    aries_config = 'src/integrationtest/python/resources/itest_simulation/aries_local_10000.json'
    if integrationtest_utils.mongodb_test_url():
        aries_config = 'src/integrationtest/python/resources/itest_simulation/aries_gitlab_10000.json'

    # Start simulator in background
    p = mp.Process(target=run_aries,
                   args=(
                       ['--conf', aries_config,
                        '--loglevel', 'ERROR'],))
    p.start()

    # Create state object
    with integrationtest_utils.readfile(STATE_FILE, __file__) as f:
        j = json.load(f)
        state = State(j)

    # Switch on battery
    sleep(0.5)
    state.battery['active'] = 1
    data = {'AGENT0': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on EV
    sleep(0.5)
    state.electrical_vehicle['active'] = 1
    data = {'AGENT0': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on wind_generator
    sleep(0.5)
    state.wind_generator['active'] = 1
    data = {'AGENT0': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on wind_generator
    sleep(0.5)
    state.pv_panel['active'] = 1
    data = {'AGENT0': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on water_tank
    sleep(0.5)
    state.water_tank['active'] = 1
    data = {'AGENT0': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # reset State
    state.battery['active'] = 0
    state.electrical_vehicle['active'] = 0
    state.wind_generator['active'] = 0
    state.pv_panel['active'] = 0
    state.water_tank['active'] = 0

    # Switch on battery
    sleep(0.5)
    state.battery['active'] = 1
    data = {'AGENT1': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on EV
    sleep(0.5)
    state.electrical_vehicle['active'] = 1
    data = {'AGENT1': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on wind_generator
    sleep(0.5)
    state.wind_generator['active'] = 1
    data = {'AGENT1': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on wind_generator
    sleep(0.5)
    state.pv_panel['active'] = 1
    data = {'AGENT1': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on water_tank
    sleep(0.5)
    state.water_tank['active'] = 1
    data = {'AGENT1': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # reset State
    state.battery['active'] = 0
    state.electrical_vehicle['active'] = 0
    state.wind_generator['active'] = 0
    state.pv_panel['active'] = 0
    state.water_tank['active'] = 0

    # Switch on battery
    sleep(0.5)
    state.battery['active'] = 1
    data = {'AGENT2': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on EV
    sleep(0.5)
    state.electrical_vehicle['active'] = 1
    data = {'AGENT2': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on wind_generator
    sleep(0.5)
    state.wind_generator['active'] = 1
    data = {'AGENT2': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on wind_generator
    sleep(0.5)
    state.pv_panel['active'] = 1
    data = {'AGENT2': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on water_tank
    sleep(0.5)
    state.water_tank['active'] = 1
    data = {'AGENT2': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # reset State
    state.battery['active'] = 1
    state.electrical_vehicle['active'] = 1
    state.wind_generator['active'] = 1
    state.pv_panel['active'] = 1
    state.water_tank['active'] = 1

    # Switch on battery
    sleep(0.5)
    state.battery['active'] = 0
    data = {'AGENT0': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on EV
    sleep(0.5)
    state.electrical_vehicle['active'] = 0
    data = {'AGENT0': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on wind_generator
    sleep(0.5)
    state.wind_generator['active'] = 0
    data = {'AGENT0': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on wind_generator
    sleep(0.5)
    state.pv_panel['active'] = 0
    data = {'AGENT0': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on water_tank
    sleep(0.5)
    state.water_tank['active'] = 0
    data = {'AGENT0': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # reset State
    state.battery['active'] = 1
    state.electrical_vehicle['active'] = 1
    state.wind_generator['active'] = 1
    state.pv_panel['active'] = 1
    state.water_tank['active'] = 1

    # Switch on battery
    sleep(0.5)
    state.battery['active'] = 0
    data = {'AGENT1': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on EV
    sleep(0.5)
    state.electrical_vehicle['active'] = 0
    data = {'AGENT1': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on wind_generator
    sleep(0.5)
    state.wind_generator['active'] = 0
    data = {'AGENT1': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on wind_generator
    sleep(0.5)
    state.pv_panel['active'] = 0
    data = {'AGENT1': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on water_tank
    sleep(0.5)
    state.water_tank['active'] = 0
    data = {'AGENT1': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # reset State
    state.battery['active'] = 1
    state.electrical_vehicle['active'] = 1
    state.wind_generator['active'] = 1
    state.pv_panel['active'] = 1
    state.water_tank['active'] = 1

    # Switch on battery
    sleep(0.5)
    state.battery['active'] = 0
    data = {'AGENT2': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on EV
    sleep(0.5)
    state.electrical_vehicle['active'] = 0
    data = {'AGENT2': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on wind_generator
    sleep(0.5)
    state.wind_generator['active'] = 0
    data = {'AGENT2': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on wind_generator
    sleep(0.5)
    state.pv_panel['active'] = 0
    data = {'AGENT2': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    # Switch on water_tank
    sleep(0.5)
    state.water_tank['active'] = 0
    data = {'AGENT2': state.dump()}
    server.post_page(url='/api/aries/state', data=data)

    p.join()

    simulation_cursor = server.storage.get_active_simulation()

    if simulation_cursor is not None:
        simulation = next(simulation_cursor, None)
        if simulation is not None:
            simulation_id = simulation['_id']

            agents = server.storage.get_agents_by_simulation(simulation_id=simulation_id)
            with open('agents.csv', 'w') as f:
                for a in agents:
                    ag = Agent.load(a['name'], json.loads(a['agent']))
                    f.write('{},{},{},{},{},{},{}\n'.format(ag.name, a['simulation_step_id'], ag.battery.active,
                                                            ag.electrical_vehicle.active, ag.pv_panel.active,
                                                            ag.water_tank.active,
                                                            ag.wind_generator.active))

            states = server.storage.read_states(simulation_id=simulation_id)
            with open('states.json', 'w') as f:
                for s in states:
                    f.write('{} : {}\n'.format(s['is_applied'], s['states']))


if __name__ == '__main__':
    if integrationtest_utils.is_storage_exists() and integrationtest_utils.is_event_queue_exists():
        run_tests()
