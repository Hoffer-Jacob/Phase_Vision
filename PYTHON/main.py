# Author: Jacob Hoffer
# Purpose: Verify Specifications

import csv
from scipy import signal
from simulation import *

# CONSTANTS
f = 60
T_MAX = 0.4  # seconds
ft = 8000

# USER CHOICE
FILE_NAME = 'variable_sheet.csv'
MODE = 'RMS Error'  # RMS Error, Error over time
INTERPOLATION_TYPE = 'resample'  # resample
ENABLE_GRAPH = False
TEST_NUM = [4]


def main():

    new_simulation = initialization()

    for current_test in new_simulation.tests:
        if current_test.check_for_error():
            continue

        per_error = 100 * np.abs(current_test.analytic_rms - current_test.interpolated_rms) / current_test.analytic_rms

        print(current_test.test_id)
        print(current_test.analytic_rms)
        print(current_test.interpolated_rms)

        new_simulation.add_result(Result(current_test.test_id, per_error))

    new_simulation.print_results()

    for num in TEST_NUM:
        new_simulation.graph_results(num)

    return


def initialization():

    header_list, test_matrix = read_file()

    new_simulation = Simulation()

    for test_list in test_matrix:
        new_test = create_test(header_list, test_list)
        if new_test is not None:
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

    if all(np.round(test_id) != TEST_NUM):
        return None

    a_to_gnd = test_list[np.where(header == "phAToGnd")[0][0]] * 0.3048
    b_to_gnd = test_list[np.where(header == "phBToGnd")[0][0]] * 0.3048
    c_to_gnd = test_list[np.where(header == "phCToGnd")[0][0]] * 0.3048

    a_to_center = test_list[np.where(header == "phAToCenter")[0][0]] * 0.3048
    b_to_center = test_list[np.where(header == "phBToCenter")[0][0]] * 0.3048
    c_to_center = test_list[np.where(header == "phCToCenter")[0][0]] * 0.3048

    a_current = test_list[np.where(header == "phACurrMag")[0][0]]
    b_current = test_list[np.where(header == "phBCurrMag")[0][0]]
    c_current = test_list[np.where(header == "phCCurrMag")[0][0]]

    a_phase = np.deg2rad(test_list[np.where(header == "phAAngle")[0][0]])
    b_phase = np.deg2rad(test_list[np.where(header == "phBAngle")[0][0]])
    c_phase = np.deg2rad(test_list[np.where(header == "phCAngle")[0][0]])

    pv_to_center = test_list[np.where(header == "pvDistFromCenter")[0][0]]

    a_dist = np.linalg.norm([a_to_gnd, -pv_to_center + a_to_center])
    b_dist = np.linalg.norm([b_to_gnd, -pv_to_center + b_to_center])
    c_dist = np.linalg.norm([c_to_gnd, -pv_to_center + c_to_center])

    a_angle = np.arctan2(a_to_gnd, -pv_to_center + a_to_center) - np.pi/2
    b_angle = np.arctan2(b_to_gnd, -pv_to_center + b_to_center) - np.pi/2
    c_angle = np.arctan2(c_to_gnd, -pv_to_center + c_to_center) - np.pi/2

    sensitivity = test_list[np.where(header == "sensitivity")[0][0]] * 10 ** -9

    sample_rate = test_list[np.where(header == "smplRate")[0][0]]

    new_a_phase = Phase(a_current, a_phase, a_dist, a_angle)
    new_b_phase = Phase(b_current, b_phase, b_dist, b_angle)
    new_c_phase = Phase(c_current, c_phase, c_dist, c_angle)

    new_phase_vision = PhaseVision(sensitivity, sample_rate)

    return Test(test_id, new_a_phase, new_b_phase, new_c_phase, new_phase_vision, T_MAX, f)


if __name__ == '__main__':
    main()
