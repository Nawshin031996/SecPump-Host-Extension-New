from collections import deque
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class IntelligentDecision:
    allowed: bool
    command: float
    mode: str
    reasons: list
    risk_score: float
    detected_attack_type: str
    dynamic_max_threshold: float


class IntelligentDefenseMonitor:
    def __init__(
        self,
        max_insulin_window=180.0,
        window_hours=1.0,
        history_size=12,
        min_history_for_learning=4,
        mismatch_glucose_threshold=90.0,
        mismatch_insulin_threshold=25.0,
        sudden_spike_delta=25.0,
        dropping_threshold=5.0,
    ):
        self.max_insulin_window = max_insulin_window
        self.window_hours = window_hours
        self.min_history_for_learning = min_history_for_learning
        self.mismatch_glucose_threshold = mismatch_glucose_threshold
        self.mismatch_insulin_threshold = mismatch_insulin_threshold
        self.sudden_spike_delta = sudden_spike_delta
        self.dropping_threshold = dropping_threshold
        self.safe_command_history = deque(maxlen=history_size)
        self.recent_commands = deque()
        self.recent_glucose = deque(maxlen=2)
        self.previous_command = None

    def base_threshold(self, glucose):
        if glucose < 70.0:
            return 0.0
        if glucose < 90.0:
            return 25.0
        if glucose <= 180.0:
            return 65.0
        return 80.0

    def learned_threshold(self):
        if len(self.safe_command_history) < self.min_history_for_learning:
            return None

        values = list(self.safe_command_history)
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        std_dev = math.sqrt(variance)
        return mean + (3.0 * max(std_dev, 1.0))

    def dynamic_threshold(self, glucose):
        threshold = self.base_threshold(glucose)
        learned = self.learned_threshold()
        if learned is not None:
            threshold = min(threshold, learned)

        if self.recent_glucose and self.recent_glucose[-1] - glucose >= self.dropping_threshold:
            threshold *= 0.5

        return max(0.0, threshold)

    def _window_total(self, time_hr, command):
        while self.recent_commands and time_hr - self.recent_commands[0][0] > self.window_hours:
            self.recent_commands.popleft()
        return sum(item[1] for item in self.recent_commands) + command

    def evaluate(self, time_hr, command, glucose, insulin=0.0, communication_integrity_failed=False):
        reasons = []
        risk = 0.0
        threshold = self.dynamic_threshold(glucose)
        window_total = self._window_total(time_hr, command)
        sudden_spike = (
            self.previous_command is not None
            and command - self.previous_command > self.sudden_spike_delta
        )

        overdose_detected = False
        rapid_repeat_detected = False
        mismatch_detected = False
        sudden_spike_detected = False

        if communication_integrity_failed:
            reasons.append("COMMUNICATION_INTEGRITY_FAILURE")
            risk += 0.7

        if command > threshold:
            reasons.append("DYNAMIC_MAX_DOSE_EXCEEDED")
            risk += min(0.5, 0.25 + (command - threshold) / max(threshold, 1.0) * 0.25)
            overdose_detected = True

        if window_total > self.max_insulin_window:
            reasons.append("ROLLING_WINDOW_TOTAL_EXCEEDED")
            risk += 0.45
            rapid_repeat_detected = True

        if glucose < self.mismatch_glucose_threshold and command > self.mismatch_insulin_threshold:
            reasons.append("GLUCOSE_INSULIN_MISMATCH")
            risk += 0.35
            mismatch_detected = True

        if sudden_spike:
            reasons.append("SUDDEN_COMMAND_SPIKE")
            risk += 0.25
            sudden_spike_detected = True

        if len(self.safe_command_history) >= self.min_history_for_learning:
            learned = self.learned_threshold()
            if learned is not None and command > learned:
                reasons.append("HISTORICAL_BEHAVIOR_DEVIATION")
                risk += 0.2

        risk = min(1.0, risk)
        allowed = risk < 0.4
        mode = "NORMAL" if allowed else "FAIL_SAFE"
        delivered = command if allowed else 0.0
        detected_attack_type = self._detected_attack_type(
            communication_integrity_failed,
            mismatch_detected,
            rapid_repeat_detected,
            sudden_spike_detected,
            overdose_detected,
            risk,
        )

        self.recent_glucose.append(glucose)
        self.previous_command = command

        if allowed:
            self.recent_commands.append((time_hr, command))
            self.safe_command_history.append(command)

        return IntelligentDecision(
            allowed=allowed,
            command=delivered,
            mode=mode,
            reasons=reasons,
            risk_score=risk,
            detected_attack_type=detected_attack_type,
            dynamic_max_threshold=threshold,
        )

    def _detected_attack_type(
        self,
        communication_integrity_failed,
        mismatch_detected,
        rapid_repeat_detected,
        sudden_spike_detected,
        overdose_detected,
        risk,
    ):
        if communication_integrity_failed:
            return "tampering_attack"
        if mismatch_detected:
            return "glucose_insulin_mismatch_attack"
        if rapid_repeat_detected:
            return "rapid_repeat_attack"
        if sudden_spike_detected:
            return "sudden_spike_attack"
        if overdose_detected:
            return "overdose_attack"
        if risk >= 0.4:
            return "unknown_high_risk"
        return "none"
