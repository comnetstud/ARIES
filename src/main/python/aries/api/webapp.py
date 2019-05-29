import json
import os

import jsend
from bson.json_util import dumps, loads
from flask import Flask, render_template, Response, request

from aries.api.utils.objectid_converter import ObjectIdConverter
from aries.core import utils
from aries.core.config.config import Config
from aries.core.db.mongodb import MongoDB
from aries.core.event.event_queue import EventQueue

API_URL = '/api/aries/'


def load_config():
    with open(os.environ['ARIES_CONF'], 'rt') as f:
        j = json.load(f)
        config = Config.load(j)

    mongo_client = utils.check_if_mongodb_is_running(config.mongodb_uri)
    storage = MongoDB(client=mongo_client)
    redis_client = utils.check_if_redis_is_running(host=config.redis_host, port=config.redis_port)
    event_queue = EventQueue(redis=redis_client)
    return storage, event_queue


def create_app():
    storage, event_queue = load_config()

    app = Flask(__name__, static_folder='../../static/build/static', template_folder='../../static/build')

    ObjectIdConverter.register_in_flask(app)

    @app.route(API_URL + 'simulation/active')
    def get_active_simulation():
        simulations = storage.get_active_simulation()
        if simulations:
            simulation = next(simulations, None)
            if simulation is not None:
                simulation['_id'] = str(simulation['_id'])
                simulation['start_time'] = str(simulation['start_time'])
                for name, agent in simulation['agents'].items():
                    simulation['agents'][name] = loads(agent)
                for name, line in simulation['lines'].items():
                    simulation['lines'][name] = loads(line)
                for name, node in simulation['nodes'].items():
                    simulation['nodes'][name] = loads(node)
                for name, path in simulation['paths'].items():
                    simulation['paths'][name] = loads(path)
                if 'clusters' in simulation and simulation['clusters']:
                    for name, cluster in simulation['clusters'].items():
                        simulation['clusters'][name] = loads(cluster)
                return Response(jsend.success(simulation).stringify(), mimetype='application/json')
        return Response(jsend.fail({}).stringify(), mimetype='application/json')

    @app.route(API_URL + 'simulationstep/active')
    def get_active_simulation_step():
        simulation_steps = storage.get_active_simulation_step()
        if simulation_steps:
            simulation_step = next(simulation_steps, None)
            simulation_step['_id'] = str(simulation_step['_id'])
            simulation_step['simulation_id'] = str(simulation_step['simulation_id'])
            return Response(jsend.success(simulation_step).stringify(), mimetype='application/json')
        return Response(jsend.fail({}).stringify(), mimetype='application/json')

    @app.route(API_URL + 'simulationstep/simulation/<ObjectId:simulation_id>')
    def get_simulation_step_by_simulation(simulation_id):
        def generate():
            simulation_steps = storage.get_simulation_step_by_simulation(simulation_id)
            yield '{ "status": "success", "data": { "simulation_steps" : ['
            if simulation_steps:
                add_comma = False
                for simulation_step in simulation_steps:
                    if add_comma:
                        yield ','
                    else:
                        add_comma = True

                    simulation_step['_id'] = str(simulation_step['_id'])
                    simulation_step['simulation_id'] = str(simulation_step['simulation_id'])
                    yield dumps(simulation_step)
            yield ']}}'

        return Response(generate(), mimetype='application/json')

    @app.route(API_URL + 'agent/simulationstep/<ObjectId:simulation_step_id>')
    # @accept('application/vnd.aries.v1')
    def get_agents_by_simulation_step(simulation_step_id):
        def generate():
            agents = storage.get_agents_by_simulation_step(simulation_step_id)
            yield '{ "status": "success", "data": { "agents" : ['
            if agents:
                add_comma = False
                for agent in agents:
                    if add_comma:
                        yield ','
                    else:
                        add_comma = True
                    yield agent['agent']
            yield ']}}'

        return Response(generate(), mimetype='application/json')

    @app.route(API_URL + 'agent/simulation/<ObjectId:simulation_id>')
    # @accept('application/vnd.aries.v1')
    def get_agents_by_simulation(simulation_id):
        def generate():
            agents = storage.get_agents_by_simulation(simulation_id)
            yield '{ "status": "success", "data": { "agents" : ['
            if agents:
                add_comma = False
                for agent in agents:
                    if add_comma:
                        yield ','
                    else:
                        add_comma = True
                    yield agent['agent']
            yield ']}}'

        return Response(generate(), mimetype='application/json')

    @app.route(API_URL + 'state', methods=['POST'])
    def write_states():
        try:
            states = request.get_json()
            event_queue.write_states({'states': states})
        except Exception as e:
            return Response(jsend.fail({'message': str(e)}).stringify())
        return Response(jsend.success({}).stringify(), mimetype='application/json')

    @app.route(API_URL + 'cluster', methods=['POST'])
    def write_clusters():
        try:
            clusters = request.get_json()
            event_queue.write_clusters({'clusters': clusters})
        except Exception as e:
            return Response(jsend.fail({'message': str(e)}).stringify())
        return Response(jsend.success({}).stringify(), mimetype='application/json')

    @app.route(API_URL + 'cluster/<ObjectId:simulation_id>')
    def get_clusters(simulation_id):
        clusters = storage.get_last_cluster_for_simulation_id(simulation_id=simulation_id)
        if clusters:
            cluster = next(clusters, None)
            print(cluster)
            if cluster:
                cluster['_id'] = str(cluster['_id'])
                cluster['simulation_id'] = str(cluster['simulation_id'])
                cluster['simulation_step'] = str(cluster['simulation_step'])
                return Response(jsend.success(cluster).stringify(), mimetype='application/json')
        return Response(jsend.fail({}).stringify(), mimetype='application/json')

    @app.route('/')
    def index():
        return json.dumps({'status': 'success', 'data': None}), 200, {'ContentType': 'application/json'}

    return app


if __name__ == '__main__':
    webapp = create_app()
    webapp.run(host='0.0.0.0', debug=True)
