# Author: Jacob Hoffer
# Purpose: Proof of concenpt
#           Show use of python in simulation

import csv
import numpy as np
from matplotlib import pyplot as plt

FILE_NAME = 'variable_sheet.csv'


def main():

    test_variables, test_values = initialization()

    for test in test_values:
        sampled_magnetic_field = find_sampled_magnetic_field(test, test_variables)

    return


def initialization():

    with open(FILE_NAME, mode='r', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='|')
        file = [row for row in reader]

    header_list = file[0][1:]
    tests_list = [list(map(float, row[1:])) for row in file[1:]]

    test_variables = np.array(header_list)
    test_values = np.array(tests_list)

    return test_variables, test_values


def find_sampled_magnetic_field(test, test_variables):

    # Dimension definition with respect to Phase Vision
    #   Up Vertical: +z axis
    #   Right Horizontal: +x axis
    #   Out of Screen: +y axis

    phases_xyz = np.array([[test[5]-test[8], 0, test[2]],
                          [test[6]-test[8], 0, test[3]],
                          [test[7]-test[8], 0, test[4]]])
    phases_current_magnitude = test[10:13]
    phases_angles = test[13:16]
    fs = test[np.where(test_variables == 'Sampling Rate (Hz)')]
    sensitivity = 150

    f = 60
    m_0 = 4 * 3.14 * 10 ** -7
    t = np.arange(0, 0.1, 1/fs)

    phases = set(zip(phases_current_magnitude, phases_angles))
    current_waveforms = [phase[0] * np.sin(2*np.pi*f*t + np.deg2rad(phase[1])) for phase in phases]

    phase_dists = [np.linalg.norm(phase_xyz) for phase_xyz in phases_xyz]

    magnetic_waveforms = [m_0 * current_waveform / (2 * np.pi * phase_dist)
                          for current_waveform, phase_dist
                          in zip(current_waveforms, phase_dists)]

    plt.plot(t, sum(magnetic_waveforms), '-')
    # [plt.plot(t, magnetic_waveforms, '-') for magnetic_waveforms in magnetic_waveforms]
    plt.show()


    return 0


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
