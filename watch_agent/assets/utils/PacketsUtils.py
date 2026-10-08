from assets.managers.LogsManager import LOGS

from assets.utils.EncryptUtils import encryptUtils

class OUTGOING_PACKET_TYPES:
    NEW_DEVICE = 0
    TELEMETRY = 10

class INGOING_PACKET_TYPES:
    NEW_DEVICE_RESPONSE = 1
    EMERGENCY_RESPONSE = 11

class PacketsUtilis:
    def get_new_device_packet(self, mac_address):
        raw_bytes = bytes(
            [
                OUTGOING_PACKET_TYPES.NEW_DEVICE,
                mac_address
            ]
        )

        return encryptUtils.encrypt_payload(raw_bytes)

    def get_telemetry_packet(self, bpm: int, button_state: bool, battery_level: int, steps: int = 0):
        raw_bytes = bytes(
            [
                OUTGOING_PACKET_TYPES.TELEMETRY,
                1,
                min(max(int(bpm), 0), 255),
                min(max(int(battery_level), 0), 100),
                min(max(int(steps), 0), 255), #PROBLEMA: Con 1 byte possiamo mandare solo al massimo 255 passi...
                min(max(int(button_state), 0), 1),
                0,
            ]
        )

        return encryptUtils.encrypt_payload(raw_bytes)

    def parse_packet_response(self, device_props):
        name = str(device_props.get("Name", ""))
        msg_data = device_props.get("ManufacturerData", {})

        if 0xFFFF in msg_data:
            raw_bytes = bytes(msg_data[0xFFFF])
            payload_str = raw_bytes.decode('utf-8', errors='ignore')

            return {
                "name": name,
                "payload": payload_str,
                "rssi": int(device_props.get("RSSI", 0)),
                "mac": str(device_props.get("Address", ""))
            }
        else:
            LOGS.warning("[PacketUtils] Non è stato possibile parsare correttamente il pacchetto.")
            return False
        
packetUtils = PacketsUtilis()