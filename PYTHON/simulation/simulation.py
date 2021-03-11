from matplotlib import pyplot as plt
from scipy import special
from scipy import interpolate
import numpy as np

from sinc_interpolation import sinc_interpolation

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
    def __init__(self, test_id, a_phase, b_phase, c_phase, phase_vision, t_end, f):
        self.test_id = test_id
        self.phases = [a_phase, b_phase, c_phase]
        self.phase_vision = phase_vision

        self.sampled_signals = self.sample(t_end, f)
        self.interpolated_signals = self.interpolate()
        self.interpolated_rms = self.find_rms()
        self.analytic_rms = self.calculate_rms()

    def check_for_error(self):
        for phase in self.phases:
            if phase.check_for_error():
                return True
            return False

    def sample(self, t_end, f):

        fs = self.phase_vision.sample_rate
        sense = self.phase_vision.sensitivity

        ts = np.arange(0, t_end, 1 / fs)
        bs_3p = [(phase.current * m_0 / (2 * np.pi * phase.dist)) * np.cos((2 * np.pi * f * ts) + phase.phase)
                 for phase in self.phases]

        plt.figure()
        [plt.plot(ts[0:10], bs_1p[0:10], '.') for bs_1p in bs_3p]
        plt.show()

        angle_matrix = np.array([
            [np.cos(phase.angle) for phase in self.phases],
            [0, 0, 0],
            [np.sin(phase.angle) for phase in self.phases]
        ])
        bs_3d = np.matmul(angle_matrix, bs_3p)

        plt.figure()
        [plt.plot(ts[0:10], bs_1p[0:10], '.') for bs_1p in bs_3d]
        plt.show()

        ret = [[np.round(sample / sense) * sense for sample in b_samples] for b_samples in bs_3d]

        return ret

    def interpolate(self):
        fs = self.phase_vision.sample_rate

        t, ret = sinc_interpolation(self.sampled_signals, fs)

        plt.figure()
        [plt.plot(t, bs_1d, '-') for bs_1d in ret]
        plt.show()

        return ret

    def find_rms(self):

        magnitude = np.sum(self.interpolated_signals, axis=0)

        return np.sqrt(np.sum([value ** 2 for value in magnitude]) / np.size(magnitude))

    def calculate_rms(self):

        # print([phase.dist for phase in self.phases])

        phasors = [(phase.current * m_0 / (2 * np.pi * phase.dist)) * np.exp(1j * phase.phase) for phase in self.phases]
        [print(phasor) for phasor in phasors]

        phasor = np.sum(phasors)

        print(phasor)

        magnitude = np.abs(phasor)

        return magnitude / np.sqrt(2)


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
