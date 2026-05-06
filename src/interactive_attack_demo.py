from safety_monitor import SafetyMonitor


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


def main():
    monitor = SafetyMonitor()
    time_hr = 0.0
    simulated_insulin = 0.0

    print("Interactive SecPump safety monitor demo")
    print("Enter q at any prompt to quit.")

    while True:
        glucose = read_number("\nCurrent glucose (mg/dL): ")
        if glucose is None:
            break

        requested_command = read_number("Requested insulin command (mU/min): ")
        if requested_command is None:
            break

        decision = monitor.evaluate(
            time_hr=time_hr,
            command=requested_command,
            glucose=glucose,
            insulin=simulated_insulin,
        )

        status = "ALLOW" if decision.allowed else "BLOCK"
        print(f"requested command: {requested_command:.2f}")
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
