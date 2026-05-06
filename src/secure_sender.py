import argparse
import json
import socket
import sys
import time

from secure_channel import create_secure_packet, tamper_packet


HOST = "127.0.0.1"
PORT = 5050


def send_packet(packet, host=HOST, port=PORT):
    encoded = json.dumps(packet).encode()
    with socket.create_connection((host, port), timeout=5) as client:
        client.sendall(encoded)


def build_packet(glucose, command, mode):
    packet = create_secure_packet(time.time() / 3600.0, glucose, command)

    if mode == "tamper":
        packet = tamper_packet(packet, insulin_command=float(command) + 100.0)

    return packet


def send_and_print(glucose, command, mode):
    packet = build_packet(glucose, command, mode)

    print("Sending packet...")
    print("Payload:")
    print(json.dumps(packet["payload"], indent=2, sort_keys=True))
    print(f"HMAC: {packet['signature']}")
    if mode == "tamper":
        print("Packet modified after signing for integrity-check demo")

    send_packet(packet)


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
        "3": "tamper",
    }
    while True:
        print("Select sender scenario to simulate:")
        print("  1 = normal sender")
        print("  2 = malicious sender")
        print("  3 = tampered sender")
        value = input("Scenario: ").strip()
        if value in choices:
            return choices[value]
        print("Please choose 1, 2, or 3.")


def interactive_main():
    while True:
        glucose = read_float("Enter glucose: ")
        command = read_float("Enter requested insulin command: ")
        mode = read_mode()
        send_and_print(glucose, command, mode)

        again = input("Send another? (y/n): ").strip().lower()
        if again != "y":
            break


def main():
    if len(sys.argv) == 1:
        interactive_main()
        return

    parser = argparse.ArgumentParser(description="Send a secure SecPump command packet.")
    parser.add_argument("--glucose", type=float, required=True)
    parser.add_argument("--command", type=float, required=True)
    parser.add_argument("--mode", choices=["normal", "malicious", "tamper"], required=True)
    args = parser.parse_args()

    send_and_print(args.glucose, args.command, args.mode)


if __name__ == "__main__":
    main()
