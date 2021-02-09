class Simulation:

    def __init__(self):
        self.tests = []
        self.results = []

    def add_test(self, new_test):
        self.tests.append(new_test)

    def add_result(self, new_result):
        self.results.append(new_result)
