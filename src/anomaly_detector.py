from collections import deque


class SuddenInsulinSpikeDetector:
    def __init__(self, max_delta=25.0, history_size=6):
        self.max_delta = max_delta
        self.history = deque(maxlen=history_size)

    def check(self, command):
        if not self.history:
            self.history.append(command)
            return False

        previous = self.history[-1]
        self.history.append(command)
        return command - previous > self.max_delta
