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
