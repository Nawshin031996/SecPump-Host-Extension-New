from collections import deque
from dataclasses import dataclass

from anomaly_detector import SuddenInsulinSpikeDetector


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    command: float
    mode: str
    reasons: list


class SafetyMonitor:
    def __init__(
        self,
        max_insulin_per_injection=65.0,
        max_insulin_window=180.0,
        window_hours=1.0,
        mismatch_glucose_threshold=90.0,
        mismatch_insulin_threshold=25.0,
    ):
        self.max_insulin_per_injection = max_insulin_per_injection
        self.max_insulin_window = max_insulin_window
        self.window_hours = window_hours
        self.mismatch_glucose_threshold = mismatch_glucose_threshold
        self.mismatch_insulin_threshold = mismatch_insulin_threshold
        self.detector = SuddenInsulinSpikeDetector()
        self.recent_commands = deque()

    def evaluate(self, time_hr, command, glucose, insulin):
        reasons = []

        while self.recent_commands and time_hr - self.recent_commands[0][0] > self.window_hours:
            self.recent_commands.popleft()

        window_total = sum(item[1] for item in self.recent_commands) + command

        if command > self.max_insulin_per_injection:
            reasons.append("MAX_INSULIN_PER_INJECTION")
        if window_total > self.max_insulin_window:
            reasons.append("MAX_INSULIN_PER_TIME_WINDOW")
        if glucose < self.mismatch_glucose_threshold and command > self.mismatch_insulin_threshold:
            reasons.append("GLUCOSE_INSULIN_CONSISTENCY")
        if self.detector.check(command):
            reasons.append("SUDDEN_INSULIN_SPIKE")
        if reasons:
            return SafetyDecision(False, 0.0, "FAIL_SAFE", reasons)

        self.recent_commands.append((time_hr, command))
        return SafetyDecision(True, command, "NORMAL", reasons)
