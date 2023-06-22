import matplotlib.pyplot as plt
import time
import sys
import math
import numpy as np


# Number of points on the string
NUMBER_OF_POINTS = 500000

# Time variables
TIMESTEP_LENGTH = 10
TIMESTEP_MAX = 500
TIMESTEP_DURATION_SECONDS = 0.00

# Multiplier on acceleration based on distance
SPRING_MULTIPLIER = 1

# Velocity is multiplied by this value before other calculations, adds a damping effect over time
VELOCITY_MULTIPLIER = 1

# Returns a dictionary of all pre-allocated arrays to be used in the rest of the simulation
def preallocate_arrays() -> dict:
    state = {
    "point_magnitudes_current"  : np.zeros(NUMBER_OF_POINTS),
    "point_magnitudes_previous" : np.zeros(NUMBER_OF_POINTS),
    "point_magnitudes_new"      : np.zeros(NUMBER_OF_POINTS),
    "point_velocities"          : np.zeros(NUMBER_OF_POINTS),
    "point_accelerations"       : np.zeros(NUMBER_OF_POINTS),
    "rolled_array"              : np.zeros(NUMBER_OF_POINTS),
    "relative_total"            : np.zeros(NUMBER_OF_POINTS),
    "array_ends"                : np.zeros(NUMBER_OF_POINTS, dtype= bool),
    "time_current"     : 0,
    "timestep_current" : 0
    }
    np.put(state["array_ends"], [0,NUMBER_OF_POINTS-1], 1)
    return state

# Calculates a new array with updated magnitudes when given an array at a timestep and the previous timestep
def update_point_magnitudes(state: dict):
    # Get current velocity of all points
    np.subtract(state["point_magnitudes_current"], state["point_magnitudes_previous"], out= state["point_velocities"])
    np.divide(state["point_velocities"], TIMESTEP_LENGTH, out= state["point_velocities"])
    np.multiply(state["point_velocities"], VELOCITY_MULTIPLIER, out= state["point_velocities"])

    # Get total relative magnitude of neighboring points
    for i in [-1,1]:
        np.copyto(state["rolled_array"], state["point_magnitudes_current"])
        np.roll(state["rolled_array"], i)
        # Copy current values into ends of rolled array to return zero during the math for the end bits
        np.copyto(state["rolled_array"], state["point_magnitudes_current"], where= state["array_ends"])
        np.subtract(state["rolled_array"], state["point_magnitudes_current"], out= state["rolled_array"])
        np.add(state["relative_total"], state["rolled_array"], out= state["relative_total"])

    # Calculate point accelerations
    np.multiply(state["relative_total"], SPRING_MULTIPLIER, out= state["point_accelerations"])

    # Update point velocities
    np.divide(state["point_accelerations"], TIMESTEP_LENGTH, out= state["point_accelerations"])
    np.add(state["point_velocities"], state["point_accelerations"], out= state["point_velocities"])

    # Calculate delta based on velocity, then assign it to velocity array
    np.multiply(state["point_velocities"], TIMESTEP_LENGTH, out= state["point_velocities"])

    # Update magnitudes based on the delta
    np.add(state["point_magnitudes_current"], state["point_velocities"], out= state["point_magnitudes_current"])


# Iterates the simulation by one timestep
def iterate_timestep(state: dict):
    # Tick the clock up
    state["timestep_current"] += 1
    state["time_current"]     += TIMESTEP_LENGTH

    update_point_magnitudes(state)


# Function from ChatGPT to handle closing the program when the plot is closed
def handle_close(evt):
    sys.exit()

# Matplotlib function from ChatGPT to plot the values
def plot_values(values):
    # Turn on interactive mode
    plt.ion()

    # Create a list for x-axis values
    x_values = range(len(values))
    
    # Create the plot
    plt.plot(x_values, values)
    
    # Add title and labels
    plt.title("Waves :)")
    plt.xlabel("X")
    plt.ylabel("Y")

    # Set fixed axes limits
    plt.ylim([-20, 20])
    
    # Display the plot
    plt.draw()
    plt.pause(TIMESTEP_DURATION_SECONDS)

    # Clear the plot for the next update
    plt.cla()

    # Connect the 'close_event' to the 'handle_close' function
    plt.gcf().canvas.mpl_connect('close_event', handle_close)

def main():
    state = preallocate_arrays()
    while state["timestep_current"] <= TIMESTEP_MAX:
        # Oscillate a specific point
        OSC_TIME = 360
        OSC_STRENGTH = 5.0
        OSC_TARGET_INDEX = 100
        if state["time_current"] <= OSC_TIME:
            osc_angle = (state["time_current"]) % 360
            state["point_magnitudes_current"][OSC_TARGET_INDEX] = math.sin(math.radians(osc_angle)) * OSC_STRENGTH
            #print(osc_angle, state["point_magnitudes_current"][OSC_TARGET_INDEX])
        elif state["time_current"] < OSC_TIME + 50:
            state["point_magnitudes_current"][OSC_TARGET_INDEX] = 0

        # Freeze a specific point, in this case the one on the far end
        state["point_magnitudes_current"][NUMBER_OF_POINTS - 1] = 0

        #print(point_magnitudes_current)
        #plot_values(point_magnitudes_current)
        time.sleep(TIMESTEP_DURATION_SECONDS)
        iterate_timestep(state)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- {0} seconds for {1} timesteps of {2} points = {3} FPS ---".format(time.time() - start_time, TIMESTEP_MAX, NUMBER_OF_POINTS, TIMESTEP_MAX/(time.time() - start_time)))