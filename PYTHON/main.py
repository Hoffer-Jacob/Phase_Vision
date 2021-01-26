# Author: Jacob Hoffer
# Purpose: Proof of concenpt
#           Show use of python in simulation

import numpy as np

FILE_NAME = 'TestSet.txt'
SEP = ','

def main():

    initialization()

    return


def initialization():

    f = open(FILE_NAME, "r")
    file_str = f.read()

    line_str = file_str.split('\n')
    test_set_list = [line.split(SEP) for line in line_str]

    return test_set_list


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
