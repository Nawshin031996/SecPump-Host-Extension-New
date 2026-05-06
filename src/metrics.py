import csv


def summarize_run(name, rows):
    glucose_values = [float(row["glucose"]) for row in rows]
    command_values = [float(row["delivered_command"]) for row in rows]
    blocked = [row for row in rows if row["blocked"] == "1"]
    unsafe = [row for row in rows if row["glucose"] and float(row["glucose"]) < 60.0]
    high = [row for row in rows if row["glucose"] and float(row["glucose"]) > 150.0]

    return {
        "run": name,
        "min_glucose": min(glucose_values),
        "max_glucose": max(glucose_values),
        "mean_glucose": sum(glucose_values) / len(glucose_values),
        "total_insulin_command": sum(command_values),
        "blocked_events": len(blocked),
        "hypoglycemia_samples": len(unsafe),
        "hyperglycemia_samples": len(high),
    }


def confusion_counts(rows):
    counts = {"tp": 0, "tn": 0, "fp": 0, "fn": 0}
    for row in rows:
        actual = row["attack_active"] == "1"
        predicted = row["blocked"] == "1"
        if actual and predicted:
            counts["tp"] += 1
        elif actual and not predicted:
            counts["fn"] += 1
        elif not actual and predicted:
            counts["fp"] += 1
        else:
            counts["tn"] += 1
    return counts


def write_metrics(path, metrics_rows):
    fieldnames = [
        "run",
        "min_glucose",
        "max_glucose",
        "mean_glucose",
        "total_insulin_command",
        "blocked_events",
        "hypoglycemia_samples",
        "hyperglycemia_samples",
    ]
    with open(path, "w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metrics_rows)
