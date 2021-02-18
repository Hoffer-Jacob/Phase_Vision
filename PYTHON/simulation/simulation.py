from matplotlib import pyplot as plt
import numpy as np

m_0 = 4 * np.pi * 10 ** -7


class Simulation:

    def __init__(self):
        self.tests = []
        self.results = []

    def add_test(self, new_test):
        self.tests.append(new_test)

    def add_result(self, new_result):
        self.results.append(new_result)

    def print_results(self):
        for result in self.results:
            print('%4.2f: %6.2f' % (result.test_id, result.rms_error))

    def graph_results(self, test_num):

        x = [str(result.test_id) for result in self.results if np.round(result.test_id) == test_num]
        rms_error = [result.rms_error for result in self.results if np.round(result.test_id) == test_num]
        plt.bar(x, rms_error)
        plt.xlabel('Test ID')
        plt.ylabel('RMS Percent Error')
        plt.grid(True)
        plt.show()

        return

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

    def analytic(self):
        phasors = [phase.current * m_0 / (2 * np.pi * phase.dist) * np.exp(1j * phase.phase) for phase in self.phases]

        return


class Result:
    def __init__(self, test_id, rms_error):
        self.test_id = test_id
        self.rms_error = rms_error


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
