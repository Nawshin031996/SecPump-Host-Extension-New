import json

from intelligent_defense_monitor import IntelligentDefenseMonitor
from secure_channel import (
    create_secure_packet,
    tamper_packet,
    verify_and_decode_packet,
)


TIME_STEP_HOURS = 1.0 / 6.0


def read_float(prompt):
    while True:
        value = input(prompt).strip()
        try:
            return float(value)
        except ValueError:
            print("Please enter a numeric value.")


def read_mode():
    choices = {
        "1": "normal",
        "2": "malicious",
        "3": "tampered",
    }
    while True:
        print("Communication mode:")
        print("  1 = normal valid packet")
        print("  2 = malicious valid packet")
        print("  3 = tampered packet")
        value = input("Select mode: ").strip()
        if value in choices:
            return choices[value]
        print("Please choose 1, 2, or 3.")


def print_packet(packet):
    print("raw payload:")
    print(json.dumps(packet["payload"], indent=2, sort_keys=True))
    print(f"HMAC tag/hash: {packet['signature']}")


def print_decision(glucose, requested_command, decision):
    status = "ALLOW" if decision.allowed else "BLOCK"
    print(f"glucose: {glucose:.2f}")
    print(f"requested command: {requested_command:.2f}")
    print(f"dynamic max threshold: {decision.dynamic_max_threshold:.2f}")
    print(f"risk score: {decision.risk_score:.2f}")
    print(f"detected attack type: {decision.detected_attack_type}")
    print(f"decision: {status}")
    print(f"mode: {decision.mode}")
    print(f"reasons: {'|'.join(decision.reasons) if decision.reasons else 'NONE'}")


def main():
    monitor = IntelligentDefenseMonitor()
    time_hr = 0.0

    print("Interactive Intelligent Defense Demo")

    while True:
        glucose = read_float("\nEnter glucose: ")
        requested_command = read_float("Enter insulin command: ")
        mode = read_mode()

        packet = create_secure_packet(time_hr, glucose, requested_command)
        if mode == "tampered":
            packet = tamper_packet(packet, insulin_command=requested_command + 100.0)

        print_packet(packet)

        try:
            decoded = verify_and_decode_packet(packet)
            print("verification result: PASSED")
        except ValueError:
            print("verification result: FAILED")
            print("COMMUNICATION_INTEGRITY_FAILURE")
            print(f"glucose: {glucose:.2f}")
            print(f"requested command: {packet['payload']['insulin_command']:.2f}")
            print("dynamic max threshold: N/A")
            print("risk score: 1.00")
            print("detected attack type: tampering_attack")
            print("decision: BLOCK")
            print("mode: FAIL_SAFE")
            print("reasons: COMMUNICATION_INTEGRITY_FAILURE")
            time_hr += TIME_STEP_HOURS
        else:
            decision = monitor.evaluate(
                time_hr=decoded["time_hr"],
                command=decoded["insulin_command"],
                glucose=decoded["glucose"],
                communication_integrity_failed=False,
            )
            print_decision(decoded["glucose"], decoded["insulin_command"], decision)
            time_hr += TIME_STEP_HOURS

        again = input("Run again? (y/n): ").strip().lower()
        if again != "y":
            break

    print("Demo ended.")


if __name__ == "__main__":
    main()
