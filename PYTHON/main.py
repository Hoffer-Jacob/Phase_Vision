# Author: Jacob Hoffer
# Purpose: Proof of concenpt
#           Show use of python in simulation

import csv
import numpy as np
from matplotlib import pyplot as plt
from scipy import signal

FILE_NAME = 'variable_sheet.csv'


def main():

    test_variables, test_matrix = initialization()

    for test in test_matrix:
        interpolated_rms = find_sampled_magnetic_field(test, test_variables)
        print(interpolated_rms)
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


def find_sampled_magnetic_field(test, test_variables):

    # Dimension definition with respect to Phase Vision
    #   Up Vertical: +z axis
    #   Right Horizontal: +x axis
    #   Out of Screen: +y axis

    phases_xyz = np.array([[test[5]-test[8], 0, test[2]],
                          [test[6]-test[8], 0, test[3]],
                          [test[7]-test[8], 0, test[4]]]) * 0.3048
    phases_current_magnitude = test[10:13]
    phases_angles = test[13:16]
    fs = test[np.where(test_variables == 'smplRate')]
    sensitivity = test[np.where(test_variables == 'sensitivity')] * 10**-9

    f = 60
    m_0 = 4 * 3.14 * 10 ** -7
    t = np.arange(0, 0.1, 1/fs)

    phases = set(zip(phases_current_magnitude, phases_angles))
    current_samples_3p = [phase[0] * np.sin(2*np.pi*f*t + np.deg2rad(phase[1])) for phase in phases]

    phase_dists = [np.linalg.norm(phase_xyz) for phase_xyz in phases_xyz]
    line_angles = [-np.arctan(phase_xyz[0] / phase_xyz[2]) for phase_xyz in phases_xyz]

    angle_matrix = np.array([[np.cos(line_angle) for line_angle in line_angles],
                            [0, 0, 0],
                            [np.sin(line_angle) for line_angle in line_angles]])

    magnetic_samples_3p = [m_0 * current_waveform / (2 * np.pi * phase_dist) for current_waveform, phase_dist in
                           zip(current_samples_3p, phase_dists)]

    magnetic_samples_xyz = angle_matrix @ magnetic_samples_3p

    magnetic_samples_xyz_r = [[np.round(magnetic_sample / sensitivity) * sensitivity for magnetic_sample
                                    in magnetic_samples] for magnetic_samples in magnetic_samples_xyz]

    magnetic_samples_xyz_r = np.reshape(magnetic_samples_xyz_r, (3, 10))

    magnetic_interpolated_xtytzt = np.array([signal.resample(magnetic_samples_r, np.shape(magnetic_samples_xyz_r)[1] * 10, t)
                                    for magnetic_samples_r in magnetic_samples_xyz_r])

    magnetic_interpolated_txyz = np.array([magnetic_interpolated_xtytzt[0][1],
                                           magnetic_interpolated_xtytzt[0][0],
                                           magnetic_interpolated_xtytzt[1][0],
                                           magnetic_interpolated_xtytzt[2][0]])

    # plt.plot(magnetic_interpolated_txyz[0], magnetic_interpolated_txyz[1], 'b.')
    # plt.plot(t, magnetic_samples_xyz_r[0], 'r.')
    # plt.show()

    magnetic_interpolated_magnitude = np.sum(magnetic_interpolated_txyz[1:4], axis=0)
    magnetic_interpolated_rms = np.sqrt(np.sum(magnetic_interpolated_magnitude**2) /
                                        np.size(magnetic_interpolated_magnitude))

    return magnetic_interpolated_rms


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
