"""Constants for simulation"""

# PV cell peak values
PV_PEAK_CURRENT = 0.056  # Amps
PV_PEAK_VOLTAGE = 7  # V

PCC_VOLTAGE = 230  # Vrms

TIME_SCALE = 1  # 1 step of simulation is 1 second

# Solver types
LINEAR_SOLVER = "linear"
NON_LINEAR_SOLVER = "non_linear"
CUSTOM_SOLVER = "custom"  # Provided by user
