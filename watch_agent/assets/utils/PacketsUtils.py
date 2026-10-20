import dbus #type: ignore
import secrets

from assets.managers.SettingsManager import SETTINGS
from assets.managers.LogsManager import LOGS

from assets.utils.EncryptUtils import encryptUtils

class OUTGOING_PACKET_TYPES:
    NEW_DEVICE = 0
    TELEMETRY = 10

class INGOING_PACKET_TYPES:
    NEW_DEVICE_RESPONSE = 1
    WIFI_INFO = 2
    EMERGENCY_RESPONSE = 11

class PacketsUtilis:
    def are_mac_addresses_equal(self, mac1: bytes | list, mac2: bytes | list) -> bool:
        try:
            b1 = bytes(mac1)
            b2 = bytes(mac2)

            return len(b1) == 6 and len(b2) == 6 and b1 == b2
        except (TypeError, ValueError):
            return False

    def get_new_device_packet(self, mac_address: bytes) -> bytes:
        raw_bytes = bytes([OUTGOING_PACKET_TYPES.NEW_DEVICE]) + mac_address

        return encryptUtils.encrypt_payload(raw_bytes)

    def get_telemetry_packet(self, bpm: int, button_state: bool, battery_level: int, steps: int = 0, fall: bool = False):
        if not SETTINGS.UID:
            LOGS.warning("[PacketsUtils] Non ho trovato l'UID dell'orologio, non posso generare il pacchetto.")

        steps_val = min(max(int(steps), 0), 65535)
        steps_bytes = steps_val.to_bytes(2, byteorder="little")

        raw_bytes = bytes(
            [
                OUTGOING_PACKET_TYPES.TELEMETRY,
                min(max(int(SETTINGS.UID), 0), 255),
                min(max(int(bpm), 0), 255),
                min(max(int(battery_level), 0), 100),
                steps_bytes[0],
                steps_bytes[1],
                min(max(int(button_state), 0), 1),
                min(max(int(fall), 0), 1),
            ]
        )

        LOGS.info(f"[PacketsUtils] Invio pacchetto con payload: TYPE: {OUTGOING_PACKET_TYPES.TELEMETRY} | UID: 1 | BPM: {bpm} | BATTERY: {battery_level} | STEPS: {steps} | BUTTON_STATE: {button_state} | FALL: {fall}")

        encrypted_data = encryptUtils.encrypt_payload(raw_bytes) + secrets.token_bytes(2)

        return dbus.Array([dbus.Byte(b) for b in encrypted_data], signature="y")


    def parse_packet_response(self, payload, watch_mac):
        LOGS.success(f"[PacketsUtils] Payload ricevuto: {payload}")

        if payload[0] == INGOING_PACKET_TYPES.NEW_DEVICE_RESPONSE:
            if not self.are_mac_addresses_equal(payload[1:7], watch_mac):
                LOGS.warning(f"[PacketsUtils] Arrivato un pacchetto per un altro orologio.")
                return None

            return payload[7]
        if payload[0] == INGOING_PACKET_TYPES.EMERGENCY_RESPONSE:
            if not str(payload[1]) == str(SETTINGS.UID):
                LOGS.warning(f"[PacketsUtils] Arrivato un pacchetto per un altro orologio.")
                return None

            return True
        
packetUtils = PacketsUtilis()