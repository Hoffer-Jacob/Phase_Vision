# Whittaker–Shannon interpolation formula

import numpy as np


def sinc_interpolation(samples, fs):

    sample_interval = 1 / fs
    t_end = np.shape(samples)[1] * sample_interval

    t = np.arange(0, t_end, 1/1000)

    num_rows = np.shape(samples)[0]
    num_columns = np.size(t)

    ret = np.zeros((num_rows, num_columns))
    for k in range(0, num_rows):
        for i in range(0, num_columns):
            temp = 0
            for j in range(0, np.shape(samples)[1]):
                temp += np.sum(samples[k][j] * np.sinc((t[i] - j*sample_interval) / sample_interval))
            ret[k][i] = temp

    return t, ret
