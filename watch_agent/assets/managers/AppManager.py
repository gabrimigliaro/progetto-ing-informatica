import threading
import os
import sys
from functools import partial

from gi.repository import GLib  # type: ignore

from assets.managers.LogsManager import LOGS
from assets.managers.ConfigManager import CONFIG
from assets.managers.OSManager import OSMANAGER
from assets.managers.SettingsManager import SETTINGS

from assets.managers.UpdateManager import updateManager

from assets.controllers.HeartSensorController import heartSensorController
from assets.controllers.BatteryController import batteryController
from assets.controllers.AccelerometerSensorController import accelerometerSensorController
from assets.controllers.BluetoothController import bluethoothController
from assets.controllers.ButtonsController import buttonsController
from assets.controllers.WiFiController import wifiController
from assets.controllers.SoundController import soundController
from assets.controllers.VibrationController import vibrationController

from assets.utils.PacketsUtils import packetUtils, INGOING_PACKET_TYPES

from assets.lib.threading import ThreadWithReturnValue

class AppManager:
    def __init__(self):
        self.isUpdating: bool = False
        self.updateTries: int = 1

    def save_uid_and_start(self, uid):
        SETTINGS.save_uid(uid)

        if not heartSensorController.session_id: heartSensorController.init_sensor()

    def stop_emergency(self, received_data):
        if received_data:
            accelerometerSensorController.set_fall(False)
            soundController.stop_sound()
            heartSensorController.isMesuring = True
            LOGS.warning("[MAIN] Ripreso sensore cardio.")
    
    def send_generic_emergency(self, channel, condition, is_timeout: bool = False):
        if not SETTINGS.UID and buttonsController.process_events() and buttonsController.is_pressed:
            LOGS.warning("[AppManager] Non posso inviare il pacchetto d'emergenza perchè l'orologio non ha ancora un UID.")
            return True
        
        if is_timeout:
            LOGS.warning(f"[AppManager] Nessun pacchetto ricevuto in risposta a pacchetto emergenza, riinvio.")
            bluethoothController.send(packetUtils.get_telemetry_packet(heartSensorController.currentBPM, True, batteryController.battery_level, accelerometerSensorController.get_step_counter()))
            bluethoothController.listen_for_packet(INGOING_PACKET_TYPES.EMERGENCY_RESPONSE, response_callback=self.stop_emergency, timeout_callback=lambda: self.send_generic_emergency("c", "c", True))
            return True

        if buttonsController.process_events() and buttonsController.is_pressed:
            if heartSensorController.session_id:
                heartSensorController.stop()
                heartSensorController.isMesuring = False

            LOGS.warning("[MAIN] Messo in pausa sensore cardio.")

            vibrationController.vibrate()
            soundController.play_sound(CONFIG.DEFAULT_ALARM_SOUND_PATH, True, True)

            bluethoothController.send(packetUtils.get_telemetry_packet(heartSensorController.currentBPM, True, batteryController.battery_level, accelerometerSensorController.get_step_counter()))
            bluethoothController.listen_for_packet(INGOING_PACKET_TYPES.EMERGENCY_RESPONSE, response_callback=self.stop_emergency, timeout_callback=lambda: self.send_generic_emergency("c", "c", True))

        return True
            

    def send_fall_emergency(self, fall, is_timeout: bool = False):
        if not SETTINGS.UID:
            LOGS.warning("[AppManager] Non posso inviare il pacchetto d'emergenza (caduta) perchè l'orologio non ha ancora un UID.")
            return True

        if is_timeout:
            LOGS.warning(f"[AppManager] Nessun pacchetto ricevuto in risposta a pacchetto emergenza (caduta), riinvio.")
            bluethoothController.send(packetUtils.get_telemetry_packet(heartSensorController.currentBPM, False, batteryController.battery_level, accelerometerSensorController.get_step_counter(), True))
            bluethoothController.listen_for_packet(INGOING_PACKET_TYPES.EMERGENCY_RESPONSE, response_callback=self.stop_emergency, timeout_callback=lambda: self.send_fall_emergency(True, True))
            return True

        if fall:
            heartSensorController.stop()
            heartSensorController.isMesuring = False
            LOGS.warning("[MAIN] Messo in pausa sensore cardio.")

            vibrationController.vibrate()
            soundController.play_sound(CONFIG.DEFAULT_ALARM_SOUND_PATH, True, True)

            bluethoothController.send(packetUtils.get_telemetry_packet(heartSensorController.currentBPM, False, batteryController.battery_level, accelerometerSensorController.get_step_counter(), True))
            bluethoothController.listen_for_packet(INGOING_PACKET_TYPES.EMERGENCY_RESPONSE, response_callback=self.stop_emergency, timeout_callback=lambda: self.send_fall_emergency(True, True))

    def stop_and_send(self):
        if not heartSensorController.isMesuring:
            return False

        try:
            LOGS.info("[MAIN] HeartSensor fermato. Invio bluethooth.")

            heartSensorController.stop()

            batteryController.get_battery_level()

            bluethoothController.send(packetUtils.get_telemetry_packet(heartSensorController.currentBPM, False, batteryController.battery_level, accelerometerSensorController.get_step_counter()))
        
            soundController.play_sound()
        finally:
            OSMANAGER.set_wake_lock(False)

        return False

    def main_loop(self):
        if not SETTINGS.UID: 
            bluethoothController.send(packetUtils.get_new_device_packet(bluethoothController.get_mac_address()))
            bluethoothController.listen_for_packet(INGOING_PACKET_TYPES.NEW_DEVICE_RESPONSE, response_callback=self.save_uid_and_start, timeout_callback=lambda: LOGS.warning(f"[AppManager] Nessun pacchetto ricevuto in risposta a pacchetto 0."))
            
            return True

        if not heartSensorController.isMesuring: return True
        if not heartSensorController.session_id: heartSensorController.init_sensor()

        OSMANAGER.set_wake_lock(True)

        threading.Thread(target=LOGS.rotate_and_compress_logs, daemon=True).start()

        heartSensorController.start()
        GLib.timeout_add_seconds(CONFIG.H_MEASURMENTS_TIME, self.stop_and_send)

        return True

    def update_loop(self):
        if SETTINGS.UID and not self.isUpdating:
            bluethoothController.send(packetUtils.get_update_presence_packet())
            bluethoothController.listen_for_packet(INGOING_PACKET_TYPES.CAN_UPDATE, response_callback=self.wait_and_try_update, timeout_callback=lambda: LOGS.warning(f"[AppManager] Nessun pacchetto ricevuto in risposta a pacchetto 2."))

        return True

    def wait_and_try_update(self, can_update):
        LOGS.warning(f"[AppManager] CanUpdate: {can_update}")
        if not can_update: return False

        heartSensorController.stop()
        heartSensorController.isMesuring = False
        LOGS.warning("[MAIN] Messo in pausa sensore cardio per aggiornarsi.")

        self.isUpdating = True
        GLib.timeout_add_seconds(3, self.try_to_update)

    def try_to_update(self, c=None):
        if not SETTINGS.WIFI_SSID or not SETTINGS.WIFI_PASSWORD:
            LOGS.warning("[AppManager] Non ho alcune credenziali del wifi, le richiedo.")
            bluethoothController.send(packetUtils.get_request_wifi_credentials_packet())
            bluethoothController.listen_for_packet(INGOING_PACKET_TYPES.WIFI_SSID, response_callback=lambda *args: GLib.timeout_add_seconds(3, self.try_to_update), timeout_callback=lambda *args: GLib.timeout_add_seconds(3, self.try_to_update))
        else:
            LOGS.info(f"[AppManager] Avvio update (Tentativo {self.updateTries} di {CONFIG.UPDATE_MAX_RETRIES})")

            update_thread = ThreadWithReturnValue(target=updateManager.update, daemon=True)
            update_thread.start()
            update_status = update_thread.join()

            if update_status:
                self.reload_app()
            else:
                SETTINGS.delete_wifi_info()

                if (self.updateTries > CONFIG.UPDATE_MAX_RETRIES):
                    self.updateTries = 0
                    self.isUpdating = False

                    heartSensorController.isMesuring = True
                    LOGS.warning("[MAIN] Ciclo MAIN ripreso.")
                else:
                    self.updateTries += 1
                    GLib.timeout_add_seconds(3, self.try_to_update)

    def reload_app(self):
        LOGS.warning("[UpdateManager] Reloading app...")

        self.close_app()

        os.execv(sys.executable, [sys.executable] + sys.argv)

    def close_app(self):
        LOGS.info("[MAIN] Pulizia risorse...")
        
        if heartSensorController.session_id is not None:
            heartSensorController.exit()

        if hasattr(buttonsController, "close"):
            buttonsController.close()

        if accelerometerSensorController.session_id is not None:
            accelerometerSensorController.exit()

        wifiController.exit()

        LOGS.success("[MAIN] Chiusura completata.")

appManager = AppManager()