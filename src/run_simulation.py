import csv
from pathlib import Path

from attack_scenarios import apply_attack
from baseline_adapter import BaselineSimulator, SimulationState
from metrics import confusion_counts, summarize_run, write_metrics
from plotting import (
    plot_blocked_events,
    plot_confusion_matrix,
    plot_glucose_comparison,
    plot_insulin_comparison,
)
from safety_monitor import SafetyMonitor


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"


FIELDNAMES = [
    "run",
    "time_hr",
    "glucose",
    "remote_insulin",
    "insulin",
    "baseline_command",
    "requested_command",
    "delivered_command",
    "disturbance",
    "attack_active",
    "attack_name",
    "blocked",
    "mode",
    "reason",
]


def run_case(name, attack_enabled=False, defense_enabled=False, attack_scenario="combined"):
    simulator = BaselineSimulator(seed=7)
    monitor = SafetyMonitor() if defense_enabled else None
    state = SimulationState()
    times = simulator.time_grid()
    rows = []

    for index in range(len(times) - 1):
        start_time = float(times[index])
        end_time = float(times[index + 1])
        delta_t = end_time - start_time
        current_glucose = float(state.y0[0])
        current_insulin = float(state.y0[2])

        disturbance = simulator.next_disturbance(index, state)
        baseline_command = simulator.controller_command(state, current_glucose, delta_t)

        attack = apply_attack(
            end_time,
            baseline_command,
            current_glucose,
            current_insulin,
            scenario=attack_scenario,
        )
        requested_command = attack.command if attack_enabled else baseline_command
        attack_active = attack.active if attack_enabled else False
        attack_name = attack.name if attack_active else ""

        delivered_command = requested_command
        blocked = False
        mode = "NORMAL"
        reasons = []

        if monitor is not None:
            decision = monitor.evaluate(end_time, requested_command, current_glucose, current_insulin)
            delivered_command = decision.command
            blocked = not decision.allowed
            mode = decision.mode
            reasons = decision.reasons

        next_values = simulator.step(state, start_time, end_time, delivered_command, disturbance)
        rows.append(
            {
                "run": name,
                "time_hr": f"{end_time:.6f}",
                "glucose": f"{next_values['glucose']:.6f}",
                "remote_insulin": f"{next_values['remote_insulin']:.9f}",
                "insulin": f"{next_values['insulin']:.6f}",
                "baseline_command": f"{baseline_command:.6f}",
                "requested_command": f"{requested_command:.6f}",
                "delivered_command": f"{delivered_command:.6f}",
                "disturbance": f"{disturbance:.6f}",
                "attack_active": "1" if attack_active else "0",
                "attack_name": attack_name,
                "blocked": "1" if blocked else "0",
                "mode": mode,
                "reason": "|".join(reasons),
            }
        )

    return rows


def write_log(path, rows):
    with open(path, "w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_blocked_events(path, rows):
    blocked_rows = [row for row in rows if row["blocked"] == "1"]
    with open(path, "w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(blocked_rows)


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results = {
        "baseline": run_case("baseline", attack_enabled=False, defense_enabled=False),
        "attacked": run_case("attacked", attack_enabled=True, defense_enabled=False),
        "defended": run_case("defended", attack_enabled=True, defense_enabled=True),
    }

    write_log(RESULTS_DIR / "baseline_log.csv", results["baseline"])
    write_log(RESULTS_DIR / "attacked_log.csv", results["attacked"])
    write_log(RESULTS_DIR / "defended_log.csv", results["defended"])
    write_blocked_events(RESULTS_DIR / "blocked_events.csv", results["defended"])

    metric_rows = [summarize_run(name, rows) for name, rows in results.items()]
    write_metrics(RESULTS_DIR / "metrics.csv", metric_rows)

    counts = confusion_counts(results["defended"])
    plot_glucose_comparison(results, RESULTS_DIR / "glucose_comparison.png")
    plot_insulin_comparison(results, RESULTS_DIR / "insulin_comparison.png")
    plot_blocked_events(results["defended"], RESULTS_DIR / "blocked_events.png")
    plot_confusion_matrix(counts, RESULTS_DIR / "confusion_matrix.png")

    print(f"Wrote results to {RESULTS_DIR}")
    for row in metric_rows:
        print(
            f"{row['run']}: min_glucose={row['min_glucose']:.2f}, "
            f"max_glucose={row['max_glucose']:.2f}, blocked={row['blocked_events']}"
        )


if __name__ == "__main__":
    main()
