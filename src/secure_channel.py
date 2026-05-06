import copy
import hashlib
import hmac
import json


DEFAULT_KEY = b"secpump-host-extension-demo-key"


def _canonical_payload(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _signature(payload, key):
    return hmac.new(key, _canonical_payload(payload), hashlib.sha256).hexdigest()


def create_secure_packet(time_hr, glucose, insulin_command, key=DEFAULT_KEY):
    payload = {
        "time_hr": float(time_hr),
        "glucose": float(glucose),
        "insulin_command": float(insulin_command),
    }
    return {
        "payload": payload,
        "signature": _signature(payload, key),
    }


def verify_and_decode_packet(packet, key=DEFAULT_KEY):
    payload = packet.get("payload")
    signature = packet.get("signature", "")
    if not isinstance(payload, dict):
        raise ValueError("Packet payload is missing or invalid.")

    expected = _signature(payload, key)
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Packet integrity verification failed.")

    return {
        "time_hr": float(payload["time_hr"]),
        "glucose": float(payload["glucose"]),
        "insulin_command": float(payload["insulin_command"]),
    }


def tamper_packet(packet, insulin_command=None, glucose=None):
    tampered = copy.deepcopy(packet)
    if insulin_command is not None:
        tampered["payload"]["insulin_command"] = float(insulin_command)
    if glucose is not None:
        tampered["payload"]["glucose"] = float(glucose)
    return tampered
