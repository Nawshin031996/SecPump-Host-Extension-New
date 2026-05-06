from dataclasses import dataclass


@dataclass(frozen=True)
class AttackDecision:
    active: bool
    name: str
    command: float


COMBINED = "combined"
OVERDOSE_ONLY = "overdose_only"
REPEAT_ONLY = "repeat_only"
MISMATCH_ONLY = "mismatch_only"


def _scenario_enabled(scenario, attack_type):
    return scenario in (COMBINED, attack_type)


def apply_attack(time_hr, baseline_command, glucose, insulin, scenario=COMBINED):
    if _scenario_enabled(scenario, OVERDOSE_ONLY) and 6.0 <= time_hr < 6.2:
        return AttackDecision(True, "overdose_spike", 120.0)

    if _scenario_enabled(scenario, REPEAT_ONLY) and 10.0 <= time_hr <= 10.6:
        return AttackDecision(True, "rapid_repeated_injections", baseline_command + 55.0)

    if _scenario_enabled(scenario, MISMATCH_ONLY) and 18.5 <= time_hr < 19.0:
        return AttackDecision(True, "low_glucose_high_insulin_mismatch", max(80.0, baseline_command))

    return AttackDecision(False, "", baseline_command)
