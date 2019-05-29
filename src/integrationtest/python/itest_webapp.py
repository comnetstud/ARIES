"""
    A integration test which runs the flask application and asserts that
    it responds with the "Hello world"-page when
    requesting "http://127.0.0.1:5000/".
"""
import json
import os
from random import randint

from bson import ObjectId
from bson.json_util import loads
from pyassert import assert_that

import integrationtest_utils
from aries.controller import cluster_utils
from aries.core.constants import LINEAR_SOLVER
from aries.core.grid import grid_utils
from aries.core.grid.state import State

__author__ = 'Ilya Sychev'

from pyfix import given, test, run_tests

from integration_test_support import IntegrationTestServerFixture

GRID_ELEMENT_FILE = 'grid_elements.json'
TOPOLOGY_FILE = 'topology.json'
TEST_STRING = 'test_string'
STATE_FILE = 'state.json'
CLUSTER_FILE = 'clusters.json'
AGENT_NAME = 'AGENT123'
AGENT_NAMES = ['AGENT1', 'AGENT2', 'AGENT3', 'AGENT4', 'AGENT5']
TOTAL_PV_POWER = 32.343

if integrationtest_utils.mongodb_test_url():
    os.environ['ARIES_CONF'] = integrationtest_utils.filepath('aries_gitlab.json', __file__)
else:
    os.environ['ARIES_CONF'] = integrationtest_utils.filepath('aries_local.json', __file__)


@test
@given(server=IntegrationTestServerFixture)
def if_agent_stored_and_retrieved_from_api_simulation_id(server):
    """Put agent data to DB and retrieve it over API
    """
    with integrationtest_utils.readfile(GRID_ELEMENT_FILE, __file__) as f:
        j = json.load(f)
        agents, _ = grid_utils.create_grid_elements(j)

        simulation_id = ObjectId()
        simulation_step_id = ObjectId()

        server.storage.write_agents(agents=agents, simulation_id=simulation_id, simulation_step_id=simulation_step_id)

        data = server.get_page('/api/aries/agent/simulation/' + str(simulation_id))
        assert_that(data.status_code).equals(200)
        json_data = loads(data.content)
        assert_that(len(json_data['data']['agents'])).equals(2)


@test
@given(server=IntegrationTestServerFixture)
def if_agent_stored_and_retrieved_from_api_simulation_step_id(server):
    """Put agent data to DB and retrieve it over API
    """
    with integrationtest_utils.readfile(GRID_ELEMENT_FILE, __file__) as f:
        j = json.load(f)
        agents, _ = grid_utils.create_grid_elements(j)

        simulation_id = ObjectId()
        simulation_step_id = ObjectId()

        server.storage.write_agents(agents=agents, simulation_id=simulation_id, simulation_step_id=simulation_step_id)

        data = server.get_page('/api/aries/agent/simulationstep/' + str(simulation_step_id))
        assert_that(data.status_code).equals(200)
        json_data = loads(data.content)
        assert_that(len(json_data['data']['agents'])).equals(2)


@test
@given(server=IntegrationTestServerFixture)
def if_simulation_stored_and_retrieved_from_api(server):
    """Put simulation data to DB and retrieve it over API
    """
    with integrationtest_utils.readfile(GRID_ELEMENT_FILE, __file__) as f:
        j = json.load(f)
        agents, lines = grid_utils.create_grid_elements(j)

    with integrationtest_utils.readfile(TOPOLOGY_FILE, __file__) as f:
        j = json.load(f)
        paths, nodes = grid_utils.create_topology(j)

    with integrationtest_utils.readfile(CLUSTER_FILE, __file__) as f:
        j = json.load(f)
        clusters = cluster_utils.create_clusters(j)

        server.storage.write_simulation(agents=agents, paths=paths, nodes=nodes, lines=lines, solver=LINEAR_SOLVER,
                                        clusters=clusters)

        data = server.get_page('/api/aries/simulation/active')

        assert_that(data.status_code).equals(200)
        json_data = loads(data.content)
        assert_that(len(json_data['data']['agents'])).equals(2)
        assert_that(len(json_data['data']['lines'])).equals(3)
        assert_that(len(json_data['data']['nodes'])).equals(4)
        assert_that(len(json_data['data']['paths'])).equals(2)
        assert_that(len(json_data['data']['clusters'])).equals(2)


@test
@given(server=IntegrationTestServerFixture)
def if_simulation_step_stored_and_retrieved_from_api(server):
    """Put simulation_step data to DB and retrieve it over API
    """
    simulation_id = ObjectId()
    simulation_step = randint(1, 10000)
    server.storage.write_simulation_step(simulation_step=simulation_step, simulation_id=simulation_id,
                                         simulation_result={"result": TEST_STRING},
                                         agents_states={"agents_states": TEST_STRING},
                                         total_pv_power=TOTAL_PV_POWER)
    data = server.get_page('/api/aries/simulationstep/active')
    assert_that(data.status_code).equals(200)
    json_data = loads(data.content)
    assert_that(json_data['data']['simulation_id']).equals(str(simulation_id))
    assert_that(json_data['data']['simulation_step']).equals(simulation_step)
    assert_that(json_data['data']['simulation_result']['result']).equals(TEST_STRING)
    assert_that(json_data['data']['agents_states']['agents_states']).equals(TEST_STRING)


@test
@given(server=IntegrationTestServerFixture)
def if_simulation_step_stored_and_retrieved_from_api_simulation_id(server):
    """Put multiple simulation_step data to DB and retrieve it over API
    """
    simulation_id = ObjectId()
    simulation_step = randint(1, 10000)
    simulation_step_id = server.storage.write_simulation_step(simulation_step=simulation_step,
                                                              simulation_id=simulation_id,
                                                              simulation_result={"result": TEST_STRING},
                                                              agents_states={"agents_states": TEST_STRING},
                                                              total_pv_power=TOTAL_PV_POWER)
    server.storage.finalize_simulation_step(simulation_step_id)

    simulation_step = randint(1, 10000)
    simulation_step_id = server.storage.write_simulation_step(simulation_step=simulation_step,
                                                              simulation_id=simulation_id,
                                                              simulation_result={"result": TEST_STRING},
                                                              agents_states={"agents_states": TEST_STRING},
                                                              total_pv_power=TOTAL_PV_POWER)
    server.storage.finalize_simulation_step(simulation_step_id)

    data = server.get_page('/api/aries/simulationstep/simulation/' + str(simulation_id))

    assert_that(data.status_code).equals(200)

    json_data = loads(data.content)
    assert_that(len(json_data['data']['simulation_steps'])).equals(2)


@test
@given(server=IntegrationTestServerFixture)
def if_put_and_read_states_is_working(server):
    """Post event over POST and check if it comes to Redis Queue or not
    """
    with integrationtest_utils.readfile(STATE_FILE, __file__) as f:
        j = json.load(f)
        state = State(j)

    data = {AGENT_NAME: state.dump()}
    server.post_page(url='/api/aries/state', data=data)
    ev = server.event_queue.read_states()
    assert_that(ev).is_not_none()


@test
@given(server=IntegrationTestServerFixture)
def if_put_and_read_multiple_states_is_working(server):
    """Post event over POST and check if it comes to Redis Queue or not
    """
    with integrationtest_utils.readfile(STATE_FILE, __file__) as f:
        j = json.load(f)
        state = State(j)

    for agent_name in AGENT_NAMES:
        server.post_page(url='/api/aries/state', data={agent_name: state.dump()})

    for agent_name in AGENT_NAMES:
        ev = server.event_queue.read_states()
        assert_that(next(iter(ev['states']))).equals(agent_name)


@test
@given(server=IntegrationTestServerFixture)
def if_put_and_read_clusters_is_working(server):
    """Post event over POST and check if it comes to Redis Queue or not
    """
    with integrationtest_utils.readfile(CLUSTER_FILE, __file__) as f:
        j = json.load(f)
        clusters = cluster_utils.create_clusters(j)

    clusters_dict = {}
    for name, cluster in clusters.items():
        clusters_dict[name] = cluster.dump()
    server.post_page(url='/api/aries/cluster', data=clusters_dict)
    ev = server.event_queue.read_clusters()
    assert_that(ev).is_not_none()


@test
@given(server=IntegrationTestServerFixture)
def if_put_and_read_multiple_clusters_is_working(server):
    """Post event over POST and check if it comes to Redis Queue or not
    """
    with integrationtest_utils.readfile(CLUSTER_FILE, __file__) as f:
        j = json.load(f)
        clusters = cluster_utils.create_clusters(j)

    clusters_dict = {}
    for name, cluster in clusters.items():
        clusters_dict[name] = cluster.dump()

    for i in range(100):
        server.post_page(url='/api/aries/cluster', data=clusters_dict)

    for i in range(100):
        ev = server.event_queue.read_clusters()
        assert_that(next(iter(ev['clusters']))).equals(next(iter(clusters_dict)))


if __name__ == '__main__':
    if integrationtest_utils.is_storage_exists() and integrationtest_utils.is_event_queue_exists():
        run_tests()
