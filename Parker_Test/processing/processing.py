# Author: Jacob Hoffer

from matplotlib import pyplot as plt
import numpy as np


class Sample:

    def __init__(self, values, time):
        self.values = np.array(values)
        self.time = time


class Test:

    def __init__(self, samples):
        self.values = [sample.values for sample in samples]
        self.time = [sample.time for sample in samples]
        self.values_r = []
        self.time_r = []

    def interpolate(self):

        return

    def plot_samples(self):
        plt.figure()
        [plt.plot(x, self.time) for x in self.values]
        plt.show()
        return
