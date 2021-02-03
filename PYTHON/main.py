# Author: Jacob Hoffer
# Purpose: Verify Specifications

import csv
import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate

# CONSTANTS
m_0 = 4 * np.pi * 10 ** -7
f = 60
T_MAX = 1/10

# USER CHOICE
FILE_NAME = 'variable_sheet.csv'


def main():

    simulation = initialization()

    for test in simulation.tests:
        if test.check_for_error():
            continue
        magnetic_field_sampled = sample_magnetic_field(test)

    return


class Simulation:

    def __init__(self):
        self.tests = []
        self.results = []

    def add_test(self, new_test):
        self.tests.append(new_test)

    def add_result(self, new_result):
        self.results.append(new_result)


class Test:
    def __init__(self, a_phase, b_phase, c_phase, phase_vision):
        self.phases = [a_phase, b_phase, c_phase]
        self.phase_vision = phase_vision

    def check_for_error(self):
        for phase in self.phases:
            if phase.check_for_error():
                return True
            return False


class Result:
    def __init__(self, test_id, rms):
        self.test_id = test_id
        self.rms = rms


class Phase:
    def __init__(self, current, phase, dist, angle):
        self.current = current
        self.phase = phase
        self.dist = dist
        self.angle = angle

    def check_for_error(self):
        if any([self.current == 0, self.dist == 0]):
            return True
        return False


class PhaseVision:
    def __init__(self, sensitivity, sample_rate):
        self.sensitivity = sensitivity
        self.sample_rate = sample_rate


def initialization():

    header_list, test_matrix = read_file()

    new_simulation = Simulation()

    for test_list in test_matrix:
        new_test = create_test(header_list, test_list)
        new_simulation.add_test(new_test)

    return new_simulation


def read_file():

    with open(FILE_NAME, mode='r', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='|')
        file = [row for row in reader]

    header_list = file[0][1:]
    tests_lists = [list(map(float, row[1:])) for row in file[2:]]

    header_list = np.array(header_list)
    test_matrix = np.array(tests_lists)

    return header_list, test_matrix


def create_test(header, test_list):

    test_id = test_list[np.where(header == "testID")[0][0]]

    a_to_gnd = test_list[np.where(header == "phAToGnd")[0][0]]
    b_to_gnd = test_list[np.where(header == "phBToGnd")[0][0]]
    c_to_gnd = test_list[np.where(header == "phCToGnd")[0][0]]

    a_to_center = test_list[np.where(header == "phAToCenter")[0][0]]
    b_to_center = test_list[np.where(header == "phBToCenter")[0][0]]
    c_to_center = test_list[np.where(header == "phCToCenter")[0][0]]

    a_current = test_list[np.where(header == "phACurrMag")[0][0]]
    b_current = test_list[np.where(header == "phBCurrMag")[0][0]]
    c_current = test_list[np.where(header == "phCCurrMag")[0][0]]

    a_phase = np.deg2rad(test_list[np.where(header == "phAAngle")[0][0]])
    b_phase = np.deg2rad(test_list[np.where(header == "phBAngle")[0][0]])
    c_phase = np.deg2rad(test_list[np.where(header == "phCAngle")[0][0]])

    pv_to_center = test_list[np.where(header == "pvDistFromCenter")[0][0]]

    a_dist = np.linalg.norm([a_to_gnd, pv_to_center - a_to_center])
    b_dist = np.linalg.norm([b_to_gnd, pv_to_center - b_to_center])
    c_dist = np.linalg.norm([c_to_gnd, pv_to_center - c_to_center])

    a_angle = np.arctan2(a_to_gnd, pv_to_center - a_to_center)
    b_angle = np.arctan2(b_to_gnd, pv_to_center - b_to_center)
    c_angle = np.arctan2(c_to_gnd, pv_to_center - c_to_center)

    sensitivity = test_list[np.where(header == "sensitivity")[0][0]] * 10 ** -9

    sample_rate = test_list[np.where(header == "smplRate")[0][0]]

    new_a_phase = Phase(a_current, a_phase, a_dist, a_angle)
    new_b_phase = Phase(b_current, b_phase, b_dist, b_angle)
    new_c_phase = Phase(c_current, c_phase, c_dist, c_angle)

    new_phase_vision = PhaseVision(sensitivity, sample_rate)

    return Test(new_a_phase, new_b_phase, new_c_phase, new_phase_vision)


def has_error(test_id, lines_xyz, current_magnitudes, phase_angles, fs, sensitivity):

    if test_id >= 0 and fs > 0 and sensitivity > 0 and any(current_magnitudes != 0):
        return False

    return True


def sample_magnetic_field(test):

    fs = test.phase_vision.sample_rate

    t = np.arange(0, 1/10, 1/fs)

    sampled_magnetic_field = [(phase.current * m_0 / (2 * np.pi * phase.dist)) * np.sin(2 * np.pi * f * t + phase.phase)
                              for phase in test.phases]

    return


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
