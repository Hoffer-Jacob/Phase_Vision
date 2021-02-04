# Author: Jacob Hoffer
# Purpose: Verify Specifications

import csv
import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate
import simulation.simulation

# CONSTANTS
m_0 = 4 * np.pi * 10 ** -7
f = 60
T_MAX = 1/10

# USER CHOICE
FILE_NAME = 'variable_sheet.csv'

class Simulation:

    def __init__(self):
        self.tests = []
        self.results = []

    def add_test(self, new_test):
        self.tests.append(new_test)

    def add_result(self, new_result):
        self.results.append(new_result)


class Test:
    def __init__(self, test_id, a_phase, b_phase, c_phase, phase_vision):
        self.test_id = test_id
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


def main():

    simulation = initialization()

    for test in simulation.tests:
        if test.check_for_error():
            continue
        ts, b_samples_3d = sample_magnetic_field(test)
        t, b_interpolate_3d = interpolate_samples(ts, b_samples_3d)
        rms = find_rms(t, b_interpolate_3d)
        simulation.add_result(Result(test.test_id, rms))
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


def sample_magnetic_field(test):

    fs = test.phase_vision.sample_rate

    t = np.arange(0, T_MAX, 1/8000)
    ts = np.arange(0, 1/10, 1/fs)

    b_3p = [(phase.current * m_0 / (2 * np.pi * phase.dist)) * np.sin(2 * np.pi * f * t + phase.phase)
                    for phase in test.phases]
    bs_3p = [(phase.current * m_0 / (2 * np.pi * phase.dist)) * np.sin(2 * np.pi * f * ts + phase.phase)
                    for phase in test.phases]

    [plt.plot(t,  b_1p, '--') for b_1p in b_3p]
    [plt.axvline(x=dt, color='r') for dt in ts]
    plt.show()

    angle_matrix = np.array([
        [np.cos(phase.angle) for phase in test.phases],
        [0, 0, 0],
        [np.sin(phase.angle) for phase in test.phases]
    ])

    b_3d = angle_matrix @ b_3p
    b_samples_3d = angle_matrix @ bs_3p

    [plt.plot(t, b_1d, '--') for b_1d in b_3d]
    [plt.axvline(x=dt, color='r') for dt in ts]
    plt.show()

    sense = test.phase_vision.sensitivity
    b_samples_3d = [[round(sample / sense) * sense for sample in b_samples] for b_samples in b_samples_3d]

    return ts, b_samples_3d


def interpolate_samples(ts, b_samples_3d):

    t = np.arange(0, T_MAX - 1/120, 1 / 8000)

    b_interpolate_3p = [interpolate.interp1d(ts, b_samples, kind='cubic', fill_value="extrapolate") for b_samples in
                        b_samples_3d]

    [plt.plot(ts, b_samples, 'o') for b_samples in b_samples_3d]
    [plt.plot(t, b_interpolate(t), '-') for b_interpolate in b_interpolate_3p]
    plt.show()

    return t, b_interpolate_3p


def find_rms(t, b_interpolate_3d):

    b_interpolate_3d_values = [b_interpolate(t) for b_interpolate in b_interpolate_3d]
    b_values = np.sum(b_interpolate_3d_values, axis=0)

    rms = np.sqrt(np.sum(b_values ** 2) / np.size(b_values))

    return rms


if __name__ == '__main__':
    main()
