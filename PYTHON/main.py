# Author: Jacob Hoffer
# Purpose: Verify Specifications

import sys
import csv
import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate
from scipy import signal
from simulation import *

# CONSTANTS
m_0 = 4 * np.pi * 10 ** -7
f = 60
T_MAX = 1  # seconds
ft = 8000

# USER CHOICE
FILE_NAME = 'variable_sheet.csv'
ENABLE_GRAPH = False
TEST_NUM = [5, 6]


def main():

    new_simulation = initialization()

    for current_test in [test for test in new_simulation.tests if any(np.round(test.test_id) == TEST_NUM)]:
        # print('%.3E\t%3.0f' % (current_test.phase_vision.sensitivity, current_test.phase_vision.sample_rate))
        if current_test.check_for_error():
            continue
        t, ts, b_3d, b_samples_3d = sample_magnetic_field(current_test)
        ts, b_interpolate_3d = interpolate_samples(ts, b_samples_3d, ENABLE_GRAPH)
        rms = find_rms(ts, b_interpolate_3d)
        t, b_interpolate_3d = interpolate_samples(t, b_3d, False)
        rms_ref = find_rms(t, b_interpolate_3d)
        per_error = np.abs((rms - rms_ref) / rms_ref) * 100
        new_simulation.add_result(Result(current_test.test_id, per_error))

    new_simulation.print_results()
    new_simulation.graph_results()

    return


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

    return Test(test_id, new_a_phase, new_b_phase, new_c_phase, new_phase_vision)


def has_error(test_id, lines_xyz, current_magnitudes, phase_angles, fs, sensitivity):

    if test_id >= 0 and fs > 0 and sensitivity > 0 and any(current_magnitudes != 0):
        return False

    return True


def sample_magnetic_field(current_test):

    fs = current_test.phase_vision.sample_rate

    t = np.arange(0, T_MAX, 1/ft)
    ts = np.arange(0, T_MAX, 1/fs)

    b_3p = [(phase.current * m_0 / (2 * np.pi * phase.dist)) * np.sin(2 * np.pi * f * t + phase.phase)
                    for phase in current_test.phases]
    bs_3p = [(phase.current * m_0 / (2 * np.pi * phase.dist)) * np.sin(2 * np.pi * f * ts + phase.phase)
                    for phase in current_test.phases]
    if ENABLE_GRAPH:
        [plt.plot(t,  b_1p, '--') for b_1p in b_3p]
        [plt.axvline(x=dt, color='r') for dt in ts]
        plt.show()

    angle_matrix = np.array([
        [np.cos(phase.angle) for phase in current_test.phases],
        [0, 0, 0],
        [np.sin(phase.angle) for phase in current_test.phases]
    ])

    b_3d = angle_matrix @ b_3p
    b_samples_3d = angle_matrix @ bs_3p

    if ENABLE_GRAPH:
        plt.title('Sample Locations of Each Dimension')
        [plt.plot(t, b_1d, '--') for b_1d in b_3d]
        [plt.axvline(x=dt, color='r') for dt in ts]
        plt.show()

    sense = current_test.phase_vision.sensitivity
    b_samples_3d = [[np.round(sample / sense) * sense for sample in b_samples] for b_samples in b_samples_3d]

    return t, ts, b_3d, b_samples_3d


def interpolate_samples(ts, b_samples_3d, enable_graph):

    # t = np.arange(0, T_MAX - 1/120, 1 / 8000)

    # b_interpolate_3p = [interpolate.interp1d(ts, b_samples, kind='cubic', fill_value="extrapolate") for b_samples in
    #                     b_samples_3d]

    ret = [signal.resample(b_samples, int(8000*T_MAX), ts, domain='time') for b_samples in b_samples_3d]

    b_interpolate_3p = [tup[0] for tup in ret]
    t = [tup[1] for tup in ret]

    if enable_graph:
        plt.title('Interpolated in Each Dimension with Samples Shown')
        [plt.plot(ts, b_samples, 'o') for b_samples in b_samples_3d]
        [plt.plot(tt, b_interpolate, '-') for tt, b_interpolate in zip(t, b_interpolate_3p)]
        plt.show()

    return t, b_interpolate_3p


def find_rms(t, b_interpolate_3d):

    # b_interpolate_3d_values = [b_interpolate(t) for b_interpolate in b_interpolate_3d]
    b_interpolate_3d_values = b_interpolate_3d
    b_values = np.sum(b_interpolate_3d_values, axis=0)

    rms = np.sqrt(np.sum(b_values ** 2) / np.size(b_values))

    return rms


if __name__ == '__main__':
    main()
