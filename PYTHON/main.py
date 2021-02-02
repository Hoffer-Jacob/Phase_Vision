# Author: Jacob Hoffer
# Purpose: Verify Specifications

import csv
import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate

# CONSTANTS
M_0 = 4 * np.pi * (10 ** -7)
f = 60
T_MAX = 1/10

# USER CHOICE
FILE_NAME = 'variable_sheet.csv'
DO_GRAPH = True


def main():

    header, test_matrix = initialization()

    test_results = np.empty(shape=(np.shape(test_matrix)[0], 2))
    i = 0

    for test_values in test_matrix:
        test_id, lines_xyz, current_magnitudes, phase_angles, fs, sensitivity = assign_variables(header, test_values)
        if has_error(test_id, lines_xyz, current_magnitudes, phase_angles, fs, sensitivity):
            test_results = test_results[0:-1]
            continue
        interpolated_rms = find_rms_interpolated(lines_xyz, current_magnitudes, phase_angles, fs, sensitivity)
        approx_rms = find_rms_interpolated(lines_xyz, current_magnitudes, phase_angles, 120, 10**-12)
        error = 100 * (approx_rms - interpolated_rms) / approx_rms
        print("The percent error of test %4.2f is %6.2f%%" % (test_id, error))
        test_results[i] = [test_id, error]
        i += 1

    plot_data = test_results.T

    plot_results(['Title', 'x-axis', 'y-axis'], plot_data, 5)

    return


def initialization():

    with open(FILE_NAME, mode='r', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='|')
        file = [row for row in reader]

    header_list = file[0][1:]
    tests_lists = [list(map(float, row[1:])) for row in file[2:]]

    test_variables = np.array(header_list)
    test_matrix = np.array(tests_lists)

    return test_variables, test_matrix


def assign_variables(header, test_values):
    test_id = test_values[0]
    lines_xyz = np.array([[test_values[5]-test_values[8], 0, test_values[2]],
                          [test_values[6]-test_values[8], 0, test_values[3]],
                          [test_values[7]-test_values[8], 0, test_values[4]]]) * 0.3048
    current_magnitudes = test_values[10:13]
    phase_angles = test_values[13:16]
    fs = test_values[np.where(header == 'smplRate')]
    sensitivity = test_values[np.where(header == 'sensitivity')] * (10**-9)

    return test_id, lines_xyz, current_magnitudes, phase_angles, fs, sensitivity


def has_error(test_id, lines_xyz, current_magnitudes, phase_angles, fs, sensitivity):

    if test_id >= 0 and fs > 0 and sensitivity > 0 and any(current_magnitudes != 0):
        return False

    return True


def find_magnetic_field(current_magnitudes, lines_xyz, phase_angles, t, f, fs):

    #  Create a list of the current in each line at sample times
    current_samples_3p = [I_mag * np.sin(2 * np.pi * f * t + np.deg2rad(angle)) for I_mag, angle in
                          zip(current_magnitudes, phase_angles)]

    #  Calculate the magnetic field magnitude from the current of each line
    lines_dist = [np.linalg.norm(line_xyz) for line_xyz in lines_xyz]
    lines_dist = np.array(lines_dist).T
    magnetic_samples_3p = [M_0 * current / (2 * np.pi * line_dist) for current, line_dist in
                           zip(current_samples_3p, lines_dist)]

    # Covert the magnetic field magnitude to vector via matrix multiplication
    line_angles = [np.arctan2(line_xyz[2], line_xyz[0]) - np.pi/2 for line_xyz in lines_xyz]

    angle_matrix = np.array([[np.cos(line_angle) for line_angle in line_angles],
                            [0, 0, 0],
                            [np.sin(line_angle) for line_angle in line_angles]])
    magnetic_samples_xyz = angle_matrix @ magnetic_samples_3p

    return magnetic_samples_xyz


def create_graph(magnetic_samples_xyz_r, magnetic_interpolated_txyz, t):

    plt.plot(magnetic_interpolated_txyz[0], np.sum(magnetic_interpolated_txyz[1:4], axis=0), 'b.')
    plt.plot(t, np.sum(magnetic_samples_xyz_r, axis=0), 'r.')
    plt.show()

    return


def find_rms_interpolated(lines_xyz, current_magnitudes, phase_angles, fs, sensitivity):

    # Dimension definition with respect to Phase Vision
    #   Up Vertical: +z axis
    #   Right Horizontal: +x axis
    #   Out of Screen: +y axis

    t = np.arange(0, T_MAX, 1 / fs)

    #  Calculate the magnetic field vector at the point of measurement
    magnetic_samples_xyz = find_magnetic_field(current_magnitudes, lines_xyz, phase_angles, t, f, fs)

    # Measure the field: Simulate sensitivity by rounding
    magnetic_samples_xyz_r = [[np.round(magnetic_sample / sensitivity) * sensitivity for magnetic_sample
                               in magnetic_samples] for magnetic_samples in magnetic_samples_xyz]
    magnetic_samples_xyz_r = np.reshape(magnetic_samples_xyz_r, np.shape(magnetic_samples_xyz))

    magnetic_interpolated_x = interpolate.interp1d(t, magnetic_samples_xyz_r[0], kind='cubic')

    t_new = np.arange(0, T_MAX-1/60, 1/(fs*100))
    y = magnetic_interpolated_x(t_new)

    plt.plot(t, magnetic_samples_xyz_r[0], 'o', t_new, y, '-')
    plt.show()


    print(y)

    magnetic_interpolated_txyz = np.array([magnetic_interpolated_xtytzt[0][1],
                                           magnetic_interpolated_xtytzt[0][0],
                                           magnetic_interpolated_xtytzt[1][0],
                                           magnetic_interpolated_xtytzt[2][0]])

    magnetic_interpolated_magnitude = np.sum(magnetic_interpolated_txyz[1:4], axis=0)

    magnetic_interpolated_rms = np.sqrt(np.sum(magnetic_interpolated_magnitude**2) /
                                        np.size(magnetic_interpolated_magnitude))

    if DO_GRAPH:
        create_graph(magnetic_samples_xyz_r, magnetic_interpolated_txyz, t)

    return magnetic_interpolated_rms


def plot_results(labels, plot_data, test_num):

    # Filter Data
    plot_data_filtered = np.array([[id, abs(value)] for value, id in zip(plot_data[1], plot_data[0])
                                   if np.floor(id) == test_num])

    plot_data_filtered = plot_data_filtered.T

    # Create Graph
    plt.bar([str(label) for label in plot_data_filtered[0]], plot_data_filtered[1])

    # Set String Labels
    plt.title(labels[0])
    plt.xlabel(labels[1])
    plt.ylabel(labels[2])

    # Set Grid
    plt.grid(b=True, which='major', linestyle='-')
    plt.grid(b=True, which='minor', linestyle='--')
    plt.minorticks_on()

    # Display Plot
    plt.show()

    return


if __name__ == '__main__':
    main()
