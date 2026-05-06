# Extended SecPump: Host-Side Security Defense Framework for Insulin Pump Systems

This repository is based on the original SecPump open insulin pump security workbench and adds a software-only host-side defense framework for attack simulation, runtime insulin command validation, HMAC/hash integrity checking, interactive demos, logging, metrics, and plots.

## Overview

This work transforms SecPump from a hardware-focused security demonstration into a software-driven security evaluation framework with runtime defense, attack simulation, and measurable evaluation metrics.

Original SecPump provides:

* Bergman-style glucose-insulin simulation scripts in `Scripts/`
* STM32 firmware projects in `SecPump-Vanilla/` and `SecPump-Vuln/`
* a RISC-V version under `SecPump-RISC-V/`
* BLE-oriented scripts such as `BlueCmd.py` and `Exploit.py`

My extension adds a host-side software defense layer that can be run without flashing STM32 firmware or using BLE hardware. It reuses the original software simulation behavior as a baseline, injects unsafe insulin command scenarios, evaluates runtime safety monitors, and demonstrates secure command transmission over localhost TCP.

## Quick Start

```bash
git clone https://github.com/Nawshin031996/SecPump-Host-Extension-New.git
cd SecPump-Host-Extension-New
pip install -r requirements.txt
python src/intelligent_defense_demo.py
```

## Key Contributions

* Interactive attack simulation for manually entering glucose and insulin commands.
* Automatic safe or attack-like command classification from glucose and requested insulin command values.
* HMAC/hash-based integrity checking for command packets.
* Rule-based, adaptive, and intelligent runtime defense monitors.
* Attack type labeling and risk scoring in the intelligent defense path.
* CSV logging, metrics, blocked-event records, comparison plots, and confusion matrices.
* Two-terminal sender/receiver demo that separates command sender behavior from receiver-side automatic verification and risk classification.

## System Architecture

The extended software path is:

```text
SecPump model baseline
  -> attack scenario or user-entered command
  -> optional secure packet creation
  -> HMAC/hash verification
  -> runtime defense monitor
  -> ALLOW or BLOCK decision
  -> logs, metrics, plots, or console output
```

For the two-terminal demo:

```text
secure_sender.py
  -> localhost TCP packet
  -> secure_receiver.py
  -> HMAC verification
  -> IntelligentDefenseMonitor
  -> detected attack type + risk score + ALLOW/BLOCK
```

The sender acts as a test generator and is not trusted by the receiver. The receiver does not trust a scenario label; it verifies the HMAC and classifies risk from the received packet contents.

The system does not require a user-selected attack mode. Unsafe or malicious behavior is inferred automatically from glucose values, requested insulin commands, dynamic thresholds, and recent command history. HMAC verification ensures that tampered packets are rejected before any safety evaluation.

## Repository Structure

```text
.
├── README.md
├── COPYING
├── sonar-project.properties
├── requirements.txt
├── results/
└── src/
    ├── baseline_adapter.py
    ├── attack_scenarios.py
    ├── safety_monitor.py
    ├── adaptive_safety_monitor.py
    ├── intelligent_defense_monitor.py
    ├── anomaly_detector.py
    ├── run_simulation.py
    ├── run_multi_attack_evaluation.py
    ├── metrics.py
    ├── plotting.py
    ├── secure_channel.py
    ├── secure_sender.py
    ├── secure_receiver.py
    ├── secure_interactive_demo.py
    ├── intelligent_defense_demo.py
    └── interactive_attack_demo.py
```

## Setup Instructions

Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

`requirements.txt` currently lists:

```text
numpy
scipy
matplotlib
pandas
scikit-learn
```

The current source code directly uses NumPy, SciPy, and Matplotlib. `pandas` and `scikit-learn` are listed but are not currently imported by the source files.

## How to Run

Run commands from the repository root.

### Main Combined Evaluation

```bash
python src/run_simulation.py
```

This produces:

* `baseline`: no attack, no monitor
* `attacked`: combined attack scenario, no blocking
* `defended`: combined attack scenario passed through `SafetyMonitor`

### Isolated Attack Evaluation

```bash
python src/run_multi_attack_evaluation.py
```

This separately evaluates:

* `overdose_only`
* `repeat_only`
* `mismatch_only`

### Interactive Single-Terminal Demos

```bash
python src/interactive_attack_demo.py
python src/secure_interactive_demo.py
python src/intelligent_defense_demo.py
```

These demos prompt for glucose and requested insulin command values and print monitor decisions.

The interactive demos now require only:

* glucose input
* requested insulin command

In `intelligent_defense_demo.py`, the system automatically:

* creates a secure packet
* verifies HMAC integrity
* computes dynamic safety thresholds
* evaluates risk score
* detects attack type
* decides `ALLOW` or `BLOCK`

Example inputs:

* glucose `120`, command `10`, tamper = `n`: HMAC `PASSED`, expected `ALLOW`
* glucose `120` or `130`, command `80`, tamper = `n`: HMAC `PASSED`, expected `BLOCK`
* glucose `80`, command above the displayed threshold, tamper = `n`: expected `BLOCK`

### HMAC Integrity Test (Optional)

The demo also supports testing packet tampering.

After entering glucose and insulin command, the user is prompted:

```text
Tamper packet before verification? (y/n)
```

* If `n`: HMAC verification passes, the monitor computes threshold/risk/attack type, and the command is decided as `ALLOW` or `BLOCK`.
* If `y`: the packet is modified after signing, HMAC verification fails, detected attack type is `tampering_attack`, and the decision is `REJECT`.

Expected behavior:

* verification result: `FAILED`
* detected attack type: `tampering_attack`
* decision: `REJECT`

The safety monitor is not executed if HMAC verification fails.

Tamper example:

* glucose `120`, command `10`, tamper = `y`: HMAC `FAILED`, decision `REJECT`

### Two-Terminal Secure Communication Demo

The two-terminal demo simulates command transmission over localhost TCP. The sender only asks for glucose and requested insulin command; it does not ask the user to choose a normal, malicious, or tampered scenario. The receiver verifies HMAC integrity and independently detects unsafe behavior from the received command, glucose, dynamic thresholds, risk score, and recent command history.

Terminal 1 starts the receiver:

```bash
python src/secure_receiver.py
```

Terminal 2 starts the interactive sender:

```bash
python src/secure_sender.py
```

`secure_sender.py` also supports CLI usage:

```bash
python src/secure_sender.py --glucose 120 --command 30
python src/secure_sender.py --glucose 120 --command 30 --tamper
```

Interactive sender mode prompts only for glucose and requested insulin command. It sends a valid HMAC packet by default, and the receiver independently decides whether the command is safe or unsafe. Tampering is tested separately with the explicit CLI tamper option.

## Attack Scenarios

Implemented scripted simulation attacks in `attack_scenarios.py`:

* `overdose_only`: large insulin spike around hour 6.
* `repeat_only`: rapid repeated injection commands around hour 10.
* `mismatch_only`: high insulin command during lower-glucose behavior around hour 18.5.
* `combined`: all three scripted attacks in one run.

Implemented sender behavior in `secure_sender.py`:

* interactive mode: prompts only for glucose and requested insulin command, then sends a valid HMAC packet.
* CLI mode without `--tamper`: sends the provided glucose and command with a valid HMAC.
* `--tamper`: signs a valid packet and then modifies `insulin_command`, causing receiver-side HMAC verification failure.

## Defense Mechanisms

### Rule-Based Safety Monitor

`SafetyMonitor` checks:

* max insulin per injection
* max insulin per rolling time window
* glucose-insulin consistency
* sudden insulin spike anomaly

Unsafe commands are blocked, delivered command is set to `0.0`, and mode becomes `FAIL_SAFE`.

### Adaptive Safety Monitor

`AdaptiveSafetyMonitor` adds glucose-dependent thresholds:

* glucose below 70: no insulin allowed
* glucose below 90: lower max command
* glucose 90 to 180: normal max command
* glucose above 180: higher max command
* dropping glucose makes thresholds stricter

### Intelligent Defense Monitor

`IntelligentDefenseMonitor` adds:

* adaptive thresholds from recent allowed command history
* risk score from `0.0` to `1.0`
* detected attack type labels:
  * `none`
  * `overdose_attack`
  * `rapid_repeat_attack`
  * `glucose_insulin_mismatch_attack`
  * `sudden_spike_attack`
  * `tampering_attack`
  * `unknown_high_risk`

### Hash / Integrity Verification

`secure_channel.py` implements HMAC-based packet integrity:

* `create_secure_packet(...)`
* `verify_and_decode_packet(...)`
* `tamper_packet(...)`

The secure demos reject tampered packets before passing them to a monitor.

## Outputs & Logs

Generated outputs are written under:

```text
results/
```

Main evaluation outputs:

* `baseline_log.csv`
* `attacked_log.csv`
* `defended_log.csv`
* `blocked_events.csv`
* `metrics.csv`
* `glucose_comparison.png`
* `insulin_comparison.png`
* `blocked_events.png`
* `confusion_matrix.png`

Isolated attack outputs:

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

## Evaluation

`metrics.csv` includes:

* min, max, and mean glucose
* total delivered insulin command
* blocked event count
* hypoglycemia sample count
* hyperglycemia sample count

`multi_attack_metrics.csv` additionally includes:

* attack type
* detection rate
* true positives
* false positives
* true negatives
* false negatives

The confusion matrix logic is time-step based:

* actual unsafe = `attack_active`
* predicted unsafe = command was blocked

## Original SecPump Functionality

The original SecPump hardware-oriented project remains in this repository:

* `Scripts/Model-Sim.py`: software-only model simulation path.
* `Scripts/Sec-Interface.py`: original interface script for pump simulation.
* `Scripts/BlueCmd.py`: BLE command helper.
* `Scripts/Exploit.py`: original exploit demonstration helper.
* `SecPump-Vanilla/`: original non-vulnerable STM32 pump project.
* `SecPump-Vuln/`: vulnerable STM32 pump project.
* `SecPump-RISC-V/`: RISC-V version.

Hardware flashing and BLE setup are not required to run the host extension demos and evaluations. They remain relevant only if you are working with the original SecPump hardware workflow.

## Why This Matters

This framework demonstrates how cyber-physical systems can be protected against unsafe or malicious control commands using runtime validation, integrity verification, and adaptive decision-making.

## Limitations / Future Work

* This extension is software-only and does not implement real BLE command transmission.
* The localhost TCP sender/receiver demo models communication security behavior but is not a hardware transport.
* HMAC uses a hard-coded demonstration key in `secure_channel.py`; real deployments need key management.
* Safety thresholds and the physiological model are simplified and not clinically validated.
* Conservative blocking can improve safety but may also block commands that could improve glucose control in some simulated cases.
* `pandas` and `scikit-learn` are listed in the extension requirements but are not currently used by the source code.
* TODO: add automated tests for monitor decisions, HMAC verification, generated CSVs, and plots.
* TODO: document any intended use of `pandas` or `scikit-learn`, or remove them from requirements if they remain unused.

## Disclaimer

This project is for academic and research demonstration only. It is not a medical device, is not clinically validated, and must not be used for real healthcare decisions.

## License and Attribution

The repository is based on SecPump and retains the original license file (`COPYING`). If using the original SecPump work for research, cite the SecPump publication referenced by the upstream project:

C. Bresch, D. Hely, S. Chollet, and R. Lysecky, "SecPump: A Connected Open Source Infusion Pump for Security Research Purposes," IEEE Embedded Systems Letters, 2020.
