import csv

from attack_scenarios import MISMATCH_ONLY, OVERDOSE_ONLY, REPEAT_ONLY
from metrics import confusion_counts, summarize_run
from plotting import (
    plot_blocked_events,
    plot_confusion_matrix,
    plot_glucose_comparison,
    plot_insulin_comparison,
)
from run_simulation import RESULTS_DIR, run_case, write_log


ATTACK_TYPES = [OVERDOSE_ONLY, REPEAT_ONLY, MISMATCH_ONLY]


def detection_rate(rows):
    attack_rows = [row for row in rows if row["attack_active"] == "1"]
    if not attack_rows:
        return 0.0

    detected_rows = [row for row in attack_rows if row["blocked"] == "1"]
    return len(detected_rows) / len(attack_rows)


def write_multi_attack_metrics(path, metric_rows):
    fieldnames = [
        "run",
        "attack_type",
        "min_glucose",
        "max_glucose",
        "mean_glucose",
        "total_insulin_command",
        "blocked_events",
        "hypoglycemia_samples",
        "hyperglycemia_samples",
        "detection_rate",
        "true_positive",
        "false_positive",
        "true_negative",
        "false_negative",
    ]
    with open(path, "w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metric_rows)


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # The original run_simulation.py workflow evaluates the combined attack
    # configuration. This script isolates each attack type to evaluate monitor
    # behavior per attack class without changing the combined workflow.
    plotted_results = {}
    blocked_rows = []
    metric_rows = []

    for attack_type in ATTACK_TYPES:
        attacked_name = f"attacked_{attack_type}"
        defended_name = f"defended_{attack_type}"

        attacked_rows = run_case(
            attacked_name,
            attack_enabled=True,
            defense_enabled=False,
            attack_scenario=attack_type,
        )
        defended_rows = run_case(
            defended_name,
            attack_enabled=True,
            defense_enabled=True,
            attack_scenario=attack_type,
        )

        write_log(RESULTS_DIR / f"{attacked_name}_log.csv", attacked_rows)
        write_log(RESULTS_DIR / f"{defended_name}_log.csv", defended_rows)

        plotted_results[attacked_name] = attacked_rows
        plotted_results[defended_name] = defended_rows
        blocked_rows.extend(row for row in defended_rows if row["blocked"] == "1")

        for run_name, rows in ((attacked_name, attacked_rows), (defended_name, defended_rows)):
            counts = confusion_counts(rows)
            summary = summarize_run(run_name, rows)
            summary["attack_type"] = attack_type
            summary["detection_rate"] = detection_rate(rows)
            summary["true_positive"] = counts["tp"]
            summary["false_positive"] = counts["fp"]
            summary["true_negative"] = counts["tn"]
            summary["false_negative"] = counts["fn"]
            metric_rows.append(summary)

        defended_counts = confusion_counts(defended_rows)
        plot_confusion_matrix(
            defended_counts,
            RESULTS_DIR / f"confusion_matrix_{attack_type}.png",
            x_labels=["Safe / Allowed", "Unsafe / Blocked"],
            y_labels=["Safe / Allowed", "Unsafe / Blocked"],
            x_axis_label="Predicted unsafe",
            y_axis_label="Actual unsafe",
        )

    write_multi_attack_metrics(RESULTS_DIR / "multi_attack_metrics.csv", metric_rows)
    plot_glucose_comparison(plotted_results, RESULTS_DIR / "multi_attack_glucose_comparison.png")
    plot_insulin_comparison(plotted_results, RESULTS_DIR / "multi_attack_insulin_comparison.png")
    plot_blocked_events(blocked_rows, RESULTS_DIR / "multi_attack_blocked_events.png")

    print(f"Wrote multi-attack results to {RESULTS_DIR}")
    for row in metric_rows:
        rate = row["detection_rate"]
        rate_text = f", detection_rate={rate:.2f}" if isinstance(rate, float) else ""
        print(
            f"{row['run']}: min_glucose={row['min_glucose']:.2f}, "
            f"max_glucose={row['max_glucose']:.2f}, blocked={row['blocked_events']}"
            f"{rate_text}"
        )


if __name__ == "__main__":
    main()
