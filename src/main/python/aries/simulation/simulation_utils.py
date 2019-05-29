import numpy as np

from aries.core.constants import NON_LINEAR_SOLVER, LINEAR_SOLVER
from aries.simulation.solver.linear_solver import LinearSolver
from aries.simulation.solver.non_linear_solver import NonLinearSolver


def reactive_power(power_rating, power_factor):
    """Calculate reactive power"""
    if power_rating is not None and power_factor is not None:
        return power_rating * np.tan(np.arccos(power_factor))
    else:
        return None


def apparent_power(power_rating, power_factor):
    """Calculate apparent power"""
    if power_rating is not None:
        return np.complex(power_rating, reactive_power(power_rating, power_factor))
    else:
        return None


def impedance(voltage_rating, power_rating, power_factor):
    """Calculate impedance"""
    if reactive_power(power_rating, power_factor) is not None:
        if np.abs(apparent_power(power_rating, power_factor)) == 0:
            return np.complex(1e9, 0)
        return np.conj(np.square(voltage_rating) / apparent_power(power_rating, power_factor))
    else:
        return None


def current_from_power(voltage_rating, power):
    return np.conj(power / voltage_rating)


def create_solver(solver_type, paths, nodes, lines):
    """Factory for creating solver according to solver_type"""
    if solver_type == NON_LINEAR_SOLVER:
        return NonLinearSolver(paths=paths, nodes=nodes, lines=lines)
    if solver_type == LINEAR_SOLVER:
        return LinearSolver(paths=paths, nodes=nodes, lines=lines)


def get_pv_power(agent):
    """ Check if the pv panel is active. If it is, get the power out of it, otherwise return 0"""
    pv_power = 0

    if agent.pv_panel.is_active():
        pv_power = agent.pv_panel.erogate()
    return pv_power


def get_wind_power(agent):
    """ Check if the wind generator is active. If it is, get the power out of it, otherwise return 0"""
    wind_power = 0

    if agent.wind_generator.is_active():
        wind_power = agent.wind_generator.erogate()
    return wind_power


def set_heating_contribution(agent, pv_power):
    """ If the water tank is currently in use, compute and return the part of the pv_power used for heating the water"""
    pv_power_to_heating = 0
    if agent.water_tank.is_active():
        pv_power_to_heating = pv_power * agent.pv_panel.heating_contribution
    return pv_power_to_heating


def manage_power(agent):
    """ Handle the power demand, the incoming power from network overproduction, and the request to inject power"""
    total_active_power = agent.power_rating
    total_reactive_power = reactive_power(power_rating=total_active_power, power_factor=agent.power_factor)
    # power_surplus > 0 ==> incoming_power exceeds power demand
    if agent.incoming_power > 0:
        incoming_power = agent.incoming_power - agent.incoming_power * 0.05
        # if there is incoming power i overrule the clusters, no matter what
        request_inject_power = (0, 0)
    else:
        incoming_power = 0
    power_surplus = incoming_power - total_active_power

    # If the incoming power exceeds my demand, I update my power demand so that i will absorb the incoming excess too
    if power_surplus >= 0:
        total_active_power = incoming_power
        total_reactive_power = 0
        total_power = (total_active_power, total_reactive_power)
        return total_power, (0,0)

    # -- If there is incoming power, then no more power will be injected into the network
    #   this will overwrite any kind of external control that is running in the cluster, No matter if it exceeds my
    #   demand or not.
    #
    # -- If there is NO incoming power (incoming_power <= 0 just for rounding errors safety), then I manage all the
    #   external controls
    request_inject_active_power = 0
    request_inject_reactive_power = 0
    if incoming_power <= 0:
        request_inject_active_power = agent.request_inject_power
        request_inject_reactive_power = reactive_power(power_rating=agent.request_inject_power,
                                                       power_factor=agent.request_power_factor)
    # Return these two tuples just for the sake of line length
    total_power = (total_active_power, total_reactive_power)
    request_inject_power = (request_inject_active_power, request_inject_reactive_power)
    return total_power, request_inject_power


# If the EV is active, that means that it doesn't need to be in charging mode
# so there is no need to account for the battery state of the EV
# but we have to take care of the case in which we want the EV to recharge the battery
def manage_ev(agent, total_power, time_scale):
    """ Manage the EV mode (supplier or storage), and act accordingly """
    # Dismantle the tuple, it was there just for compactness
    total_active_power, total_reactive_power = total_power
    if agent.electrical_vehicle.is_active():
        # If EV is in supply mode, then it acts as an additional battery
        if agent.electrical_vehicle.power_supplier == 1:

            # Compute the desired active and reactive powers according to the power demand and
            # the contribution of the EV
            desired_active_power_from_electrical_vehicle = total_active_power * \
                                                           agent.electrical_vehicle.contribution_active
            desired_reactive_power_from_electrical_vehicle = total_reactive_power * \
                                                             agent.electrical_vehicle.contribution_reactive
            desired_power_from_electrical_vehicle = np.abs(
                np.complex(desired_active_power_from_electrical_vehicle,
                           desired_reactive_power_from_electrical_vehicle))

            # Try to get the power out of the EV
            if agent.electrical_vehicle.erogate(power=desired_power_from_electrical_vehicle, time_scale=time_scale):
                # If you manage to get the power that you want, then update the demand
                total_active_power -= desired_active_power_from_electrical_vehicle
                total_reactive_power -= desired_reactive_power_from_electrical_vehicle

        # If EV is in charging mode, then it gets power from the grid
        else:
            total_active_power += agent.electrical_vehicle.charge_current * agent.voltage_rating  # To be checked (
            # Riccardo)
            agent.electrical_vehicle.charge(current=agent.electrical_vehicle.charge_current, time_scale=time_scale)
    return total_active_power, total_reactive_power


def manage_battery(agent, total_power, request_inject_power, power_to_battery, time_scale):
    """ Manage the battery contribution, and update the battery condition """
    # Dismantle tuples and do some little computation

    # power demand of the agent
    rated_active_power = agent.power_rating
    rated_reactive_power = reactive_power(power_rating=rated_active_power, power_factor=agent.power_factor)

    # power demand including the incoming power
    total_active_power, total_reactive_power = total_power
    total_apparent_power = np.abs(np.complex(total_active_power, total_reactive_power))
    if total_apparent_power > 0:
        total_power_factor = total_active_power / total_apparent_power
    else:
        total_power_factor = 1
    demand_power = np.complex(total_active_power, total_reactive_power)

    # power that the agent should inject into the grid
    request_inject_active_power, request_inject_reactive_power = request_inject_power
    request_inject_apparent_power = np.abs(np.complex(request_inject_active_power, request_inject_reactive_power))
    # power from the energy sources to the battery
    pv_power_to_battery, wind_power_to_battery = power_to_battery
    # power from the grid into the battery (related to the incoming power)

    # actual injected power taken from the battery
    inject_active_power = 0
    inject_reactive_power = 0

    inject_power = 0

    total_active_power_from_battery = 0
    total_reactive_power_from_battery = 0
    if agent.incoming_power > 0:
        incoming_power = agent.incoming_power - agent.incoming_power * 0.05
    else:
        incoming_power = 0
    power_surplus = incoming_power - rated_active_power

    # If the battery is installed / working
    if agent.battery.is_active():
        # if the incoming power is less than the actual demand
        if power_surplus <= 0:
            desired_active_power_from_battery = rated_active_power * agent.battery.contribution_active
            desired_reactive_power_from_battery = rated_reactive_power * agent.battery.contribution_reactive
            desired_power_from_battery = np.abs(
                np.complex(desired_active_power_from_battery, 1e-2 * desired_reactive_power_from_battery))  # check
            #  this 1e-2
            if agent.battery.erogate(desired_power_from_battery, time_scale):
                total_active_power_from_battery = desired_active_power_from_battery
                total_reactive_power_from_battery = desired_reactive_power_from_battery

                total_active_power -= total_active_power_from_battery
                total_reactive_power -= total_reactive_power_from_battery
        # If there is no incoming power I try to inject what I'm asked to inject, otherwise I just bypass the injecting
        # thing
        if incoming_power <= 0:
            if agent.battery.erogate(request_inject_apparent_power, time_scale):
                inject_active_power = request_inject_active_power
                inject_reactive_power = request_inject_reactive_power

                total_active_power_from_battery += request_inject_active_power
                total_reactive_power_from_battery += request_inject_reactive_power

        # manage excess incoming power
        current_surplus_to_battery = 0
        if power_surplus > 0:
            current_surplus_to_battery = power_surplus / agent.battery.voltage
        current_pv_to_battery = pv_power_to_battery * agent.pv_panel.battery_coupling_efficiency / agent.battery.voltage
        current_wind_to_battery = wind_power_to_battery * agent.wind_generator.battery_coupling_efficiency / \
                                  agent.battery.voltage
        energy_left = agent.battery.charge(
            current=current_pv_to_battery + current_wind_to_battery + current_surplus_to_battery, time_scale=time_scale)

        # If the battery is full, I just send the excess to the water tank
        if energy_left > 0:
            agent.water_tank.charge(energy_left / time_scale, time_scale)

        if np.abs(np.complex(total_active_power, total_reactive_power)) != 0:
            total_power_factor = total_active_power / np.abs(np.complex(total_active_power, total_reactive_power))
            demand_power = np.complex(total_active_power, total_reactive_power)
            inject_power = np.complex(inject_active_power, inject_reactive_power)
        else:
            total_power_factor = 1
            demand_power = np.complex(0, 0)
            inject_power = np.complex(inject_active_power, inject_reactive_power)
    power_from_battery = np.complex(total_active_power_from_battery, total_reactive_power_from_battery)
    return total_active_power, total_power_factor, demand_power, inject_power, power_from_battery
