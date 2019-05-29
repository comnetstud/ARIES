"""Run simulation within simpy"""
import logging
import sys
import traceback

import simpy

logger = logging.getLogger(__name__)


def run_simulation(simulation, number_of_steps):
    """Run simulation with given parameters"""
    try:
        env = simpy.Environment()
        simulation.init_simulation(env)
        if number_of_steps > 0:
            env.run(until=number_of_steps)
        else:
            env.run()
    except Exception as e:
        logger.exception(e)
