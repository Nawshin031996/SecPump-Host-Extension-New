import json
import socket
import time

from intelligent_defense_monitor import IntelligentDefenseMonitor
from secure_channel import create_secure_packet, verify_and_decode_packet


HOST = "127.0.0.1"
PORT = 5050


def handle_packet(packet, monitor):
    payload = packet.get("payload", {})
    received_tag = packet.get("signature", "")
    expected_tag = ""
    if isinstance(payload, dict):
        time_hr = payload.get("time_hr", 0.0)
        glucose = payload.get("glucose", 0.0)
        command = payload.get("insulin_command", 0.0)
        expected_tag = create_secure_packet(time_hr, glucose, command)["signature"]

    print("\nReceived packet")
    print(json.dumps(packet, indent=2, sort_keys=True))
    print(f"Received HMAC: {received_tag}")
    print(f"Expected HMAC: {expected_tag}")

    try:
        decoded = verify_and_decode_packet(packet)
    except ValueError:
        print("HMAC verification: FAILED")
        print("COMMUNICATION_INTEGRITY_FAILURE")
        print("Detected attack type: tampering_attack")
        return

    print("HMAC verification: PASSED")

    glucose = float(decoded["glucose"])
    requested_command = float(decoded["insulin_command"])
    time_hr = float(decoded["time_hr"])

    decision = monitor.evaluate(
        time_hr=time_hr,
        command=requested_command,
        glucose=glucose,
    )

    status = "ALLOW" if decision.allowed else "BLOCK"
    print(f"Glucose: {glucose:.2f}")
    print(f"Requested command: {requested_command:.2f}")
    print(f"Detected attack type: {decision.detected_attack_type}")
    print(f"Risk score: {decision.risk_score:.2f}")
    print(f"Decision: {status}")
    print(f"Delivered command: {decision.command:.2f}")
    print(f"Mode: {decision.mode}")
    print(f"Reasons: {'|'.join(decision.reasons) if decision.reasons else 'NONE'}")


def main(host=HOST, port=PORT):
    monitor = IntelligentDefenseMonitor()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print("SecPump secure receiver started...")
        print(f"Listening on localhost:{port}")

        while True:
            try:
                connection, address = server.accept()
            except KeyboardInterrupt:
                print("\nReceiver stopped.")
                break

            with connection:
                data = connection.recv(65536)
                if not data:
                    continue
                try:
                    packet = json.loads(data.decode())
                    handle_packet(packet, monitor)
                except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                    print(f"\nInvalid packet from {address}: {exc}")
                time.sleep(0.01)


if __name__ == "__main__":
    main()
