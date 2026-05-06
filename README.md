Note: All project source code and outputs are located inside the SecPump-Host-Extension/ directory.
# SecPump Host Safety Extension

Author: Nawshin Tabassum Tanny
Course: CS 7389F

---

## Overview

In this project, I extend the SecPump software-only insulin pump simulation by adding a runtime safety and security monitoring layer. The goal is to detect unsafe or malicious insulin delivery behavior and prevent life-threatening outcomes using rule-based validation and anomaly detection.

The extension builds on the existing SecPump simulation (`Scripts/Model-Sim.py`) and enhances it with attack scenarios, monitoring mechanisms, fail-safe control, logging, and evaluation.

---

## Quick Start

Clone the repository and install dependencies:

```bash
git clone https://github.com/Nawshin031996/SecPump-Host-Extension.git
cd SecPump-Host-Extension/SecPump-Host-Extension
pip install -r requirements.txt
```

Run the main evaluation:

```bash
python src/run_multi_attack_evaluation.py
```

Run the two-terminal secure communication demo:

Terminal 1:

```bash
python src/secure_receiver.py
```

Terminal 2:

```bash
python src/secure_sender.py
```

---

## Background

The SecPump platform provides a software-based simulation of an insulin pump system, including glucose dynamics, insulin delivery, and control logic using a Bergman-style physiological model.

I successfully ran the original `Scripts/Model-Sim.py` after applying a minimal Python 3 compatibility fix (`print(log)`), confirming the baseline system behavior.

---

## What I Implemented

This extension introduces a host-side safety monitoring framework without modifying the original SecPump implementation.

### 1. Baseline Adapter

* Reuses Bergman-style glucose-insulin equations
* Maintains PID controller parameters
* Uses SciPy `odeint` for numerical integration
* Preserves:

  * 24-hour simulation horizon
  * 10-minute sampling interval
  * Meal disturbance timing

---

### 2. Attack Scenarios

Simulated unsafe insulin delivery behaviors:

* **Overdose attack** (sudden large insulin spike)
* **Rapid repeated injections**
* **Glucose-insulin mismatch** (low glucose with high insulin)

---

### 3. Safety Monitoring Layer

The system enforces:

* Maximum insulin per injection
* Maximum insulin within a rolling time window
* Glucose-insulin consistency checks
* Sudden insulin spike anomaly detection

---

### 4. Anomaly Detection

Detects abnormal command patterns such as:

* Rapid insulin spikes
* Unusual deviation from normal insulin behavior

---

### 5. Fail-Safe Mechanism

When unsafe behavior is detected:

* Command is **BLOCKED**
* Insulin delivery is set to `0.0`
* System enters **FAIL_SAFE mode**
* Reason for blocking is logged

---

### 6. Logging

The system generates structured logs:

* `baseline_log.csv`
* `attacked_log.csv`
* `defended_log.csv`
* `blocked_events.csv`

---

### 7. Evaluation Metrics

The system computes:

* Accuracy
* Precision
* Recall
* F1-score
* Detection rate
* Glucose safety range statistics

---

### 8. Visualization

Generated plots include:

* Glucose comparison (baseline vs attacked vs defended)
* Insulin comparison
* Blocked events over time
* Confusion matrix

---

### 9. Adaptive Safety and Secure Communication

Additional defensive extensions include:

* Adaptive safety monitoring
* HMAC-based secure command verification
* Two-terminal sender/receiver communication demo

---

## Architecture

```text
SecPump Simulation (Model-Sim.py)
        ↓
Baseline Adapter
        ↓
Attack Injection
        ↓
Safety Monitor + Anomaly Detection
        ↓
Decision: ALLOW / BLOCK (FAIL_SAFE)
        ↓
Logging + Metrics + Plots
```

---

## How to Run

Install required dependencies:

```bash
pip install -r SecPump-Host-Extension/requirements.txt
# OR
python -m pip install -r Scripts/requirements-modern.txt
```

Run the simulation:

```bash
python SecPump-Host-Extension/src/run_simulation.py
```

---

## Outputs

All outputs are saved in:

```text
SecPump-Host-Extension/results/
```

Generated files:

* `baseline_log.csv` – Normal system behavior
* `attacked_log.csv` – System under attack
* `defended_log.csv` – System with safety monitoring
* `blocked_events.csv` – Blocked unsafe commands
* `metrics.csv` – Evaluation results
* `glucose_comparison.png` – Glucose behavior comparison
* `insulin_comparison.png` – Insulin command comparison
* `blocked_events.png` – Blocked command visualization
* `confusion_matrix.png` – Detection performance

---

## Results Summary

The attack scenario caused glucose levels to drop to unsafe ranges (~50 mg/dL), indicating dangerous insulin delivery behavior.

With the safety monitoring layer enabled:

* Unsafe insulin commands were blocked (45 events)
* Glucose levels remained in a safer range (~86 mg/dL)
* The system successfully prevented critical hypoglycemia conditions

This demonstrates the effectiveness of the proposed safety monitoring framework.

---

## Alignment with Project Proposal

This implementation directly satisfies the project objectives:

* Enforces strict safety limits on insulin delivery
* Detects abnormal or malicious insulin command patterns
* Identifies inconsistencies between glucose levels and insulin delivery
* Triggers fail-safe mode when unsafe behavior is detected
* Logs and analyzes blocked unsafe events

The system follows the planned workflow:
baseline simulation → attack injection → monitoring → evaluation.

---

## Limitations

* Uses simulated data, not real patient data
* Simplified physiological model
* No integration with physical insulin pump hardware
* Safety thresholds are heuristic, not clinically validated
* The safety monitoring layer is intentionally conservative and may block some necessary insulin commands in normal conditions. This behavior prioritizes patient safety by preventing potentially dangerous insulin delivery, but may lead to suboptimal glucose control in certain cases.

---

## Future Work

* Integration with real hardware systems
* Advanced machine learning-based anomaly detection
* Formal verification of safety constraints
* Real-time deployment in embedded systems

---

## Disclaimer

This project is for academic and research purposes only. It is not a medical device and must not be used for real healthcare decisions.

---

## Extended Evaluation: Isolated Attack Analysis

The original `run_simulation.py` workflow evaluates a combined attack configuration that includes overdose, rapid repeated injection, and glucose-insulin mismatch behavior in one run. The additional multi-attack evaluator was added to isolate each attack type and make it easier to compare how the monitor performs against each class independently.

Run it from the repository root:

```bash
python SecPump-Host-Extension/src/run_multi_attack_evaluation.py
```

It generates these additional files in `SecPump-Host-Extension/results/`:

* `attacked_overdose_only_log.csv`
* `defended_overdose_only_log.csv`
* `attacked_repeat_only_log.csv`
* `defended_repeat_only_log.csv`
* `attacked_mismatch_only_log.csv`
* `defended_mismatch_only_log.csv`
* `multi_attack_metrics.csv`
* `multi_attack_glucose_comparison.png`
* `multi_attack_insulin_comparison.png`
* `multi_attack_blocked_events.png`
* `confusion_matrix_overdose_only.png`
* `confusion_matrix_repeat_only.png`
* `confusion_matrix_mismatch_only.png`

`multi_attack_metrics.csv` reports glucose statistics, total delivered insulin command, blocked events, safety-band counts, detection rate, and per-attack confusion matrix counts for runs where attack labels are available. This strengthens the evaluation by separating combined-attack behavior from per-attack detection behavior, making it clearer which safety rules are responsible for each blocked class.

---

## Interactive Attack Demo

Run the interactive command-line demo from the repository root:

```bash
python SecPump-Host-Extension/src/interactive_attack_demo.py
```

This demo allows a user to manually submit insulin commands, including malicious or unsafe commands, and observe whether the safety monitor allows delivery or blocks the command in fail-safe mode.

---

## Optional Extension: Adaptive Safety and Secure Command Demo

The project includes both a single-terminal secure interactive demo and a two-terminal sender/receiver secure communication demo.

Run the single-terminal secure adaptive command-line demo from the repository root:

```bash
python SecPump-Host-Extension/src/secure_interactive_demo.py
```

This optional extension adds adaptive insulin thresholds that respond to current glucose and glucose trend, making the safety rules more real-time than fixed thresholds alone. It also simulates secure command handling with tamper-resistant packet integrity checks. Tampered packets are rejected before reaching the monitor, while valid but unsafe commands are still passed to the adaptive safety monitor and blocked in fail-safe mode.

The two-terminal sender/receiver demo extends this idea by sending HMAC-protected command packets over localhost TCP between separate processes.

---

## Two-Terminal Secure Communication Demo

This demo simulates real-time communication between a sender/controller/attacker and a receiver/pump monitor. The sender sends glucose and insulin command packets to the receiver over localhost TCP. The receiver verifies message integrity using HMAC before applying the `IntelligentDefenseMonitor`, which reports adaptive thresholds, risk score, detected attack type, and final ALLOW/BLOCK decision.

The sender-side scenario is used only to generate test cases. The receiver does not rely on this information. All detection and decision-making are performed independently based on the received packet, HMAC verification, and runtime safety analysis.

It demonstrates three cases:

* Normal command: valid HMAC and safe insulin command -> ALLOW / NORMAL
* Malicious command: valid HMAC but unsafe insulin command -> BLOCK / FAIL_SAFE
* Tampered command: invalid HMAC after packet modification -> COMMUNICATION_INTEGRITY_FAILURE

How to run:

Terminal 1 receiver:

```bash
python SecPump-Host-Extension/src/secure_receiver.py
```

Terminal 2 sender interactive mode:

```bash
python SecPump-Host-Extension/src/secure_sender.py
```

The sender supports an interactive loop when run without command-line arguments. It prompts for glucose, requested insulin command, and a sender scenario to simulate, then asks whether to send another command.

CLI examples:

```bash
python SecPump-Host-Extension/src/secure_sender.py --glucose 120 --command 30 --mode normal
python SecPump-Host-Extension/src/secure_sender.py --glucose 120 --command 120 --mode malicious
python SecPump-Host-Extension/src/secure_sender.py --glucose 120 --command 30 --mode tamper
```

Expected behavior:

* normal: HMAC verification PASSED, decision ALLOW
* malicious: HMAC verification PASSED, decision BLOCK, mode FAIL_SAFE, risk score shown
* tamper: HMAC verification FAILED, communication integrity failure

Note:
This is a software-only communication simulation. It does not implement real BLE hardware communication, but it models the security effect of authenticated command transmission and tamper detection.

---

## Advanced Intelligent Defense Extension

This optional extension adds `IntelligentDefenseMonitor`, a runtime defense module that expands the adaptive safety idea with learned behavior, HMAC/hash authentication, and richer detection output.

It includes:

* Adaptive threshold learning from recent allowed insulin command history
* Glucose-aware dynamic dose limits that become stricter during low or dropping glucose
* Explicit attack type labeling for overdose, rapid repeat, glucose-insulin mismatch, sudden spike, tampering, and unknown high-risk behavior
* A risk score from `0.0` to `1.0` for each evaluated command
* Interactive command entry with HMAC/hash verification before monitor evaluation

Run the interactive demo from the repository root:

```bash
python SecPump-Host-Extension/src/intelligent_defense_demo.py
```

This extension is optional and does not modify the core simulation outputs.

---

## Final Summary

This project demonstrates how security through HMAC-based integrity verification and safety through runtime insulin validation can be combined to protect a cyber-physical healthcare system from both communication-level and control-level attacks.
