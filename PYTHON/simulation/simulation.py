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
