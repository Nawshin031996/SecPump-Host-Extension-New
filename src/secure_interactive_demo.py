from adaptive_safety_monitor import AdaptiveSafetyMonitor
from secure_channel import (
    create_secure_packet,
    tamper_packet,
    verify_and_decode_packet,
)


TIME_STEP_HOURS = 1.0 / 6.0
INSULIN_DECAY = 0.85
INSULIN_RESPONSE_SCALE = 0.2


def read_number(prompt):
    value = input(prompt).strip()
    if value.lower() == "q":
        return None
    try:
        return float(value)
    except ValueError:
        print("Please enter a numeric value, or q to quit.")
        return read_number(prompt)


def read_choice():
    print("1. send normally")
    print("2. tamper with command")
    print("3. send malicious but valid high insulin command")
    value = input("Choose send mode (1/2/3, or q to quit): ").strip()
    if value.lower() == "q":
        return None
    if value in {"1", "2", "3"}:
        return value
    print("Please choose 1, 2, 3, or q.")
    return read_choice()


def main():
    monitor = AdaptiveSafetyMonitor()
    time_hr = 0.0
    simulated_insulin = 0.0

    print("Secure SecPump adaptive safety demo")
    print("Enter q at any prompt to quit.")

    while True:
        glucose = read_number("\nCurrent glucose (mg/dL): ")
        if glucose is None:
            break

        requested_command = read_number("Requested insulin command (mU/min): ")
        if requested_command is None:
            break

        choice = read_choice()
        if choice is None:
            break

        packet = create_secure_packet(time_hr, glucose, requested_command)
        if choice == "2":
            packet = tamper_packet(packet, insulin_command=requested_command + 100.0)
        elif choice == "3":
            packet = create_secure_packet(time_hr, glucose, max(120.0, requested_command))

        try:
            decoded = verify_and_decode_packet(packet)
            communication_status = "VERIFIED"
        except ValueError as exc:
            print(f"communication status: REJECTED ({exc})")
            print(f"requested command: {requested_command:.2f}")
            print("delivered command: 0.00")
            print("decision: BLOCK")
            print("mode: FAIL_SAFE")
            print("reason: COMMUNICATION_INTEGRITY_FAILURE")
            time_hr += TIME_STEP_HOURS
            continue

        decision = monitor.evaluate(
            time_hr=decoded["time_hr"],
            command=decoded["insulin_command"],
            glucose=decoded["glucose"],
            insulin=simulated_insulin,
        )

        status = "ALLOW" if decision.allowed else "BLOCK"
        print(f"communication status: {communication_status}")
        print(f"requested command: {decoded['insulin_command']:.2f}")
        print(f"delivered command: {decision.command:.2f}")
        print(f"decision: {status}")
        print(f"mode: {decision.mode}")
        if decision.reasons:
            print(f"reason: {'|'.join(decision.reasons)}")

        simulated_insulin = simulated_insulin * INSULIN_DECAY + decision.command * INSULIN_RESPONSE_SCALE
        time_hr += TIME_STEP_HOURS

    print("Demo ended.")


if __name__ == "__main__":
    main()
