import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def _series(rows, key):
    return [float(row[key]) for row in rows]


def plot_glucose_comparison(results, output_path):
    plt.figure(figsize=(10, 5))
    for name, rows in results.items():
        plt.plot(_series(rows, "time_hr"), _series(rows, "glucose"), label=name)
    plt.axhline(85, color="black", linestyle="--", linewidth=1, label="target")
    plt.axhline(60, color="red", linestyle=":", linewidth=1, label="low limit")
    plt.axhline(150, color="red", linestyle=":", linewidth=1, label="high limit")
    plt.xlabel("Time (hr)")
    plt.ylabel("Glucose (mg/dL)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_insulin_comparison(results, output_path):
    plt.figure(figsize=(10, 5))
    for name, rows in results.items():
        plt.plot(_series(rows, "time_hr"), _series(rows, "delivered_command"), label=name)
    plt.xlabel("Time (hr)")
    plt.ylabel("Delivered insulin command (mU/min)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_blocked_events(rows, output_path):
    blocked_rows = [row for row in rows if row["blocked"] == "1"]
    plt.figure(figsize=(10, 4))
    if blocked_rows:
        plt.scatter(
            _series(blocked_rows, "time_hr"),
            _series(blocked_rows, "requested_command"),
            color="red",
            label="blocked command",
        )
    plt.xlabel("Time (hr)")
    plt.ylabel("Requested insulin command (mU/min)")
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_confusion_matrix(
    counts,
    output_path,
    x_labels=None,
    y_labels=None,
    x_axis_label="Monitor decision",
    y_axis_label="Attack active",
):
    matrix = [[counts["tn"], counts["fp"]], [counts["fn"], counts["tp"]]]
    labels = [["TN", "FP"], ["FN", "TP"]]
    x_labels = x_labels or ["not blocked", "blocked"]
    y_labels = y_labels or ["no attack", "attack"]
    plt.figure(figsize=(5, 4))
    plt.imshow(matrix, cmap="Blues")
    plt.xticks([0, 1], x_labels)
    plt.yticks([0, 1], y_labels)
    for row_index, row in enumerate(matrix):
        for col_index, value in enumerate(row):
            plt.text(col_index, row_index, f"{labels[row_index][col_index]}={value}", ha="center", va="center")
    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
