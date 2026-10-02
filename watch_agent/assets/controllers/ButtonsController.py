import sys
import os
import struct

from gi.repository import GLib #type: ignore

from assets.managers.ConfigManager import CONFIG
from assets.managers.LogsManager import LOGS

from assets.controllers.VibrationController import vibrationController
from assets.controllers.HeartSensorController import heartSensorController
from assets.controllers.BatteryController import batteryController
from assets.controllers.BluetoothController import bluethoothController
from assets.utils.PacketsUtils import packetUtils

class ButtonsController:
    def __init__(self):
        self.btn_fd = None
        self.is_pressed : bool = False
        self._EVENT_FORMAT : str = CONFIG.BUTTON_EVENT_FORMAT
        self._EVENT_SIZE = struct.calcsize(self._EVENT_FORMAT)

        if not self.open(): sys.exit(1)

    def open(self) -> bool:
        try:
            self.btn_fd = os.open(CONFIG.BUTTON_DEV, os.O_RDONLY | os.O_NONBLOCK)
            LOGS.info(f"[BUTTONS] Bottone {CONFIG.BUTTON_DEV} aperto correttamente.")
            return True
        except Exception as e:
            LOGS.error(f"[BUTTONS] Errore nell'apertura di {CONFIG.BUTTON_DEV}: {e}")
            self.btn_fd = None
            return False

    def process_events(self) -> bool:
        if not self.btn_fd: return False

        state_changed = False

        try:
            while True:
                data = os.read(self.btn_fd, self._EVENT_SIZE)
                if len(data) < self._EVENT_SIZE:
                    break

                _, _, ev_type, ev_code, ev_value = struct.unpack(self._EVENT_FORMAT, data)

                if ev_type == 1:
                    new_state = (ev_value != 0)

                    if new_state != self.is_pressed:
                        self.is_pressed = new_state
                        state_changed = True

        except BlockingIOError:
            pass
        except Exception as e:
            LOGS.error(f"[BUTTONS] Errore durante la lettura dell'evento: {e}")

        return state_changed

    def handle_timeout(self):
        heartSensorController.isMesuring = True
        LOGS.info("[MAIN] Ripresa misurazione cardio.")

    def handle_response(self, received_info):
        LOGS.success("[MAIN] Ricevuto pacchetto dall'esp!")
        
        heartSensorController.isMesuring = True
        LOGS.info("[MAIN] Ripresa misurazione cardio.")

        vibrationController.vibrate()
        GLib.timeout_add(CONFIG.VIB_DELAY_MS, vibrationController.vibrate)

    def on_button_event(self, channel, condition):
        if self.process_events():
            bluethoothController.isButtonPressed = self.is_pressed

            if self.is_pressed:
                heartSensorController.stop()
                heartSensorController.isMesuring = False
                LOGS.warning("[MAIN] Messo in pausa sensore cardio.")

                vibrationController.vibrate()
                packetUtils.send_telemetry_packet(heartSensorController.currentBPM, True, batteryController.battery_level)

                bluethoothController.listen_for_packet(response_callback=self.handle_response, timeout_callback=self.handle_timeout)

            return True

    def close(self) -> bool:
        if self.btn_fd is not None:
            try:
                os.close(self.btn_fd)
                LOGS.info("[BUTTONS] File descriptor del tasto chiuso.")
            except Exception as e:
                LOGS.error(f"[BUTTONS] Errore durante la chiusura del fd: {e}")
                return False
            finally:
                self.btn_fd = None
            return True

buttonsController = ButtonsController()