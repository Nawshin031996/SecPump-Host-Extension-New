from collections import deque

from anomaly_detector import SuddenInsulinSpikeDetector
from safety_monitor import SafetyDecision


class AdaptiveSafetyMonitor:
    def __init__(
        self,
        max_insulin_window=180.0,
        window_hours=1.0,
        mismatch_glucose_threshold=90.0,
        mismatch_insulin_threshold=25.0,
        dropping_threshold=5.0,
    ):
        self.max_insulin_window = max_insulin_window
        self.window_hours = window_hours
        self.mismatch_glucose_threshold = mismatch_glucose_threshold
        self.mismatch_insulin_threshold = mismatch_insulin_threshold
        self.dropping_threshold = dropping_threshold
        self.detector = SuddenInsulinSpikeDetector()
        self.recent_commands = deque()
        self.recent_glucose = deque(maxlen=2)

    def adaptive_injection_limit(self, glucose):
        if glucose < 70.0:
            return 0.0
        if glucose < 90.0:
            return 25.0
        if glucose <= 180.0:
            return 65.0
        return 80.0

    def glucose_is_dropping(self, glucose):
        if not self.recent_glucose:
            return False
        return self.recent_glucose[-1] - glucose >= self.dropping_threshold

    def evaluate(self, time_hr, command, glucose, insulin):
        reasons = []

        while self.recent_commands and time_hr - self.recent_commands[0][0] > self.window_hours:
            self.recent_commands.popleft()

        injection_limit = self.adaptive_injection_limit(glucose)
        if self.glucose_is_dropping(glucose):
            injection_limit = max(0.0, injection_limit * 0.5)

        window_total = sum(item[1] for item in self.recent_commands) + command

        if command > injection_limit:
            reasons.append("ADAPTIVE_MAX_INSULIN_PER_INJECTION")
        if window_total > self.max_insulin_window:
            reasons.append("MAX_INSULIN_PER_TIME_WINDOW")
        if glucose < self.mismatch_glucose_threshold and command > self.mismatch_insulin_threshold:
            reasons.append("GLUCOSE_INSULIN_CONSISTENCY")
        if self.detector.check(command):
            reasons.append("SUDDEN_INSULIN_SPIKE")

        self.recent_glucose.append(glucose)

        if reasons:
            return SafetyDecision(False, 0.0, "FAIL_SAFE", reasons)

        self.recent_commands.append((time_hr, command))
        return SafetyDecision(True, command, "NORMAL", reasons)
