import dbus #type: ignore
import secrets

from assets.managers.SettingsManager import SETTINGS
from assets.managers.LogsManager import LOGS

from assets.utils.EncryptUtils import encryptUtils

class OUTGOING_PACKET_TYPES:
    NEW_DEVICE = 0
    UPDATE_PRESENCE = 2
    WIFI_CREDENTIALS_REQUEST = 4
    TELEMETRY = 10

class INGOING_PACKET_TYPES:
    NEW_DEVICE_RESPONSE = 1
    CAN_UPDATE = 3
    WIFI_SSID = 5
    WIFI_PSW = 6
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

    def get_update_presence_packet(self) -> bytes:
        if not SETTINGS.UID:
            LOGS.warning("[PacketsUtils] Non ho trovato l'UID dell'orologio, non posso generare il pacchetto.")
            return None
        
        raw_bytes = bytes(
            [
                OUTGOING_PACKET_TYPES.UPDATE_PRESENCE,
                min(max(int(SETTINGS.UID), 0), 255),
            ]
        )

        LOGS.info("[PacketUtils] Invio pacchetto per update.")

        return encryptUtils.encrypt_payload(raw_bytes)

    def get_request_wifi_credentials_packet(self) -> bytes:
        if not SETTINGS.UID:
            LOGS.warning("[PacketsUtils] Non ho trovato l'UID dell'orologio, non posso generare il pacchetto.")
            return None
        
        raw_bytes = bytes(
            [
                OUTGOING_PACKET_TYPES.WIFI_CREDENTIALS_REQUEST,
                min(max(int(SETTINGS.UID), 0), 255),
            ]
        )

        LOGS.info("[PacketUtils] Invio pacchetto per wifi credentials.")

        return encryptUtils.encrypt_payload(raw_bytes)

    def get_telemetry_packet(self, bpm: int, button_state: bool, battery_level: int, steps: int = 0, fall: bool = False):
        if not SETTINGS.UID:
            LOGS.warning("[PacketsUtils] Non ho trovato l'UID dell'orologio, non posso generare il pacchetto.")
            return None

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

    def parse_packet_response(self, payload, watch_mac, raw_payload):
        LOGS.success(f"[PacketsUtils] Pacchetto di tipo {payload[0]} arrivato | Payload ricevuto: {payload}")

        if payload[0] == INGOING_PACKET_TYPES.NEW_DEVICE_RESPONSE:
            if not self.are_mac_addresses_equal(payload[1:7], watch_mac):
                LOGS.warning(f"[PacketsUtils] Arrivato un pacchetto per un altro orologio.")
                return None

            return [INGOING_PACKET_TYPES.NEW_DEVICE_RESPONSE, payload[7]]
        
        if payload[0] == INGOING_PACKET_TYPES.EMERGENCY_RESPONSE:
            if not str(payload[1]) == str(SETTINGS.UID):
                LOGS.warning(f"[PacketsUtils] Arrivato un pacchetto per un altro orologio.")
                return None

            return [INGOING_PACKET_TYPES.EMERGENCY_RESPONSE, payload[2]]
        
        if payload[0] == INGOING_PACKET_TYPES.CAN_UPDATE:
            if not str(payload[1]) == str(SETTINGS.UID):
                LOGS.warning(f"[PacketsUtils] Arrivato un pacchetto per un altro orologio.")
                return None

            LOGS.success(f"[PacketUtils] Arrivato pacchetto di tipo {INGOING_PACKET_TYPES.CAN_UPDATE} con CanUpdate a {payload[2]}")
            if payload[2] == 1: return [INGOING_PACKET_TYPES.CAN_UPDATE, True]
            else: return [INGOING_PACKET_TYPES.CAN_UPDATE, False]

        if payload[0] == INGOING_PACKET_TYPES.WIFI_SSID:
            if not str(payload[1]) == str(SETTINGS.UID):
                LOGS.warning(f"[PacketsUtils] Arrivato un pacchetto per un altro orologio.")
                return None

            SETTINGS.save_wifi_SSID(encryptUtils.encrypt_string(raw_payload[2:18]))
            return [INGOING_PACKET_TYPES.WIFI_SSID, True]
        
        if payload[0] == INGOING_PACKET_TYPES.WIFI_PSW:
            if not str(payload[1]) == str(SETTINGS.UID):
                LOGS.warning(f"[PacketsUtils] Arrivato un pacchetto per un altro orologio.")
                return None

            #SETTINGS.save_wifi_PSW(encryptUtils.encrypt_string(raw_payload[2:18]))
            SETTINGS.save_wifi_PSW("e98a35608e29ebcd7b836e0fe414de16")
            return [INGOING_PACKET_TYPES.WIFI_SSID, True]
        
packetUtils = PacketsUtilis()