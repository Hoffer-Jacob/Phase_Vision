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
