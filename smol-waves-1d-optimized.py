import matplotlib.pyplot as plt
import time
import sys
import math
import numpy as np

# Number of points on the string
NUMBER_OF_POINTS = 500

# Point magnitude setup
point_magnitudes_current  = np.zeros(NUMBER_OF_POINTS)
point_magnitudes_previous = np.copy(point_magnitudes_current)

# Time setup
TIMESTEP_LENGTH = 10
TIMESTEP_MAX = 5000
TIMESTEP_DURATION_SECONDS = 0.01

time_current = 0
timestep_current = 0

# Multiplier on acceleration based on distance
SPRING_MULTIPLIER = 1

# Velocity is multiplied by this value before other calculations, adds a damping effect over time
VELOCITY_MULTIPLIER = 1

# Rolls a 1D array by the specified amount, pads the extra space with zeros instead of rolling over edge
def roll_padded_array(array: np.ndarray, roll_distance: int) -> np.ndarray:
    if roll_distance != 0:
        new_array = np.insert(array, 0, np.zeros(abs(roll_distance)))
        new_array = np.append(new_array, np.zeros(abs(roll_distance)))

        new_array = np.roll(new_array, roll_distance)

        # Crate array of indices based on input number to delete the added space
        deletion_array = np.arange(abs(roll_distance))
        deletion_array = np.append(deletion_array, deletion_array + (new_array.size-1) - (deletion_array.size-1) )

        new_array = np.delete(new_array, deletion_array)
        return new_array
    else:
        return array

# Calculates a new array with updated magnitudes when given an array at a timestep and the previous timestep
def calculate_new_magnitudes(current_magnitudes: np.ndarray, previous_magnitudes: np.ndarray) -> np.ndarray:
    # Get the velocity of all points based on current and previous magnitudes
    point_velocities = ((current_magnitudes - previous_magnitudes) / TIMESTEP_LENGTH) * VELOCITY_MULTIPLIER

    # Get the total relative magnitude of neighboring points
    relative_neighbor_magnitudes_left  = roll_padded_array(current_magnitudes, 1) - current_magnitudes
    relative_neighbor_magnitudes_right = roll_padded_array(current_magnitudes, -1) - current_magnitudes
    relative_neighbor_magnitudes_total = relative_neighbor_magnitudes_left + relative_neighbor_magnitudes_right

    # Calculate point accelerations
    point_accelerations = relative_neighbor_magnitudes_total * SPRING_MULTIPLIER

    # Calculate new point velocities
    new_point_velocities = point_velocities + (point_accelerations / TIMESTEP_LENGTH)

    # Calculate change in magnitude for points based on velocity
    point_magnitude_deltas = new_point_velocities * TIMESTEP_LENGTH

    # Calculate new magnitudes based on distance based on magnitude deltas
    new_current_point_magnitudes = current_magnitudes + point_magnitude_deltas

    return new_current_point_magnitudes


# Iterates the simulation by one timestep
def iterate_timestep():
    global point_magnitudes_current
    global point_magnitudes_previous
    global time_current
    global timestep_current

    # Tick the clock up
    timestep_current += 1
    time_current     += TIMESTEP_LENGTH

    # Use function to make new point magnitudes list
    point_magnitudes_new = calculate_new_magnitudes(point_magnitudes_current, point_magnitudes_previous)

    # Update the other two point magnitude lists
    point_magnitudes_previous = np.copy(point_magnitudes_current)
    point_magnitudes_current  = np.copy(point_magnitudes_new)

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
    while timestep_current <= TIMESTEP_MAX:
        # Oscillate a specific point
        OSC_TIME = 360
        OSC_STRENGTH = 5.0
        OSC_TARGET_INDEX = 100
        if time_current <= OSC_TIME:
            osc_angle = (time_current) % 360
            point_magnitudes_current[OSC_TARGET_INDEX] = math.sin(math.radians(osc_angle)) * OSC_STRENGTH
            #print(osc_angle, point_magnitudes_current[OSC_TARGET_INDEX])
        elif time_current < OSC_TIME + 50:
            point_magnitudes_current[OSC_TARGET_INDEX] = 0

        # Freeze a specific point, in this case the one on the far end
        point_magnitudes_current[NUMBER_OF_POINTS - 1] = 0

        #print(point_magnitudes_current)
        #plot_values(point_magnitudes_current)
        time.sleep(TIMESTEP_DURATION_SECONDS)
        iterate_timestep()

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))