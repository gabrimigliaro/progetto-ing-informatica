from assets.utils.EncryptUtils import encryptUtils
from assets.controllers.BluetoothController import bluethoothController

class OUTGOING_PACKET_TYPES:
    NEW_DEVICE = 0
    TELEMETRY = 10

class INGOING_PACKET_TYPES:
    NEW_DEVICE_RESPONSE = 1
    EMERGENCY_RESPONSE = 11

class PacketsUtilis:
    #Non mi piace tanto... magari da cambiare in futuro
    #         |
    #         V  
    def __init__(self): pass

    def send_new_device_packet(self, mac_address):
        raw_bytes = bytes(
            [
                OUTGOING_PACKET_TYPES.NEW_DEVICE,
                mac_address
            ]
        )

        payload = encryptUtils.encrypt_payload(raw_bytes)

        return bluethoothController.send(payload)

    def send_telemetry_packet(self, bpm: int, button_state: bool, battery_level: int, steps: int = 0):
        raw_bytes = bytes(
            [
                OUTGOING_PACKET_TYPES.TELEMETRY,
                1,
                min(max(int(bpm), 0), 255),
                min(max(int(battery_level), 0), 100),
                min(max(int(steps), 0), 255),
                min(max(int(button_state), 0), 1),
                0,
            ]
        )

        payload = encryptUtils.encrypt_payload(raw_bytes)

        return bluethoothController.send(payload)

packetUtils = PacketsUtilis()