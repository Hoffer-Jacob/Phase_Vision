# Author: Jacob Hofffer

import csv
import numpy as np
from matplotlib import pyplot as plt
from processing import *

FILE_NAME = 'data.csv'


def main():

    test = initialization()

    plt.figure()
    [plt.plot(x, test.time) for x in test.values]
    plt.show()

    return


def initialization():

    data_matrix = read_file()

    unix_time_ref = data_matrix[0][3]
    millisecond_ref = data_matrix[0][4]

    time_ref = unix_time_ref * 1000 + millisecond_ref

    samples = [Sample(row[0:3], row[3]*1000 + row[4] - time_ref) for row in data_matrix]

    test = Test(samples)

    return test


def read_file():

    with open(FILE_NAME, mode='r', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='|')
        file = [list(map(float, row)) for row in reader]

    return file


if __name__ == '__main__':
    main()
