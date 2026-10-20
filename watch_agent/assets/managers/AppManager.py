import threading

from gi.repository import GLib  # type: ignore

from assets.managers.LogsManager import LOGS
from assets.managers.ConfigManager import CONFIG
from assets.managers.OSManager import OSMANAGER
from assets.managers.SettingsManager import SETTINGS

from assets.controllers.HeartSensorController import heartSensorController
from assets.controllers.BatteryController import batteryController
from assets.controllers.AccelerometerSensorController import accelerometerSensorController
from assets.controllers.BluetoothController import bluethoothController
from assets.controllers.ButtonsController import buttonsController
from assets.controllers.WiFiController import wifiController
from assets.controllers.SoundController import soundController
from assets.controllers.VibrationController import vibrationController

from assets.utils.PacketsUtils import packetUtils

class AppManager:
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
            bluethoothController.listen_for_packet(response_callback=self.stop_emergency, timeout_callback=lambda: self.send_generic_emergency("c", "c", True))
            return True

        if buttonsController.process_events() and buttonsController.is_pressed:
            if heartSensorController.session_id:
                heartSensorController.stop()
                heartSensorController.isMesuring = False

            LOGS.warning("[MAIN] Messo in pausa sensore cardio.")

            vibrationController.vibrate()
            soundController.play_sound(CONFIG.DEFAULT_ALARM_SOUND_PATH, True, True)

            bluethoothController.send(packetUtils.get_telemetry_packet(heartSensorController.currentBPM, True, batteryController.battery_level, accelerometerSensorController.get_step_counter()))
            bluethoothController.listen_for_packet(response_callback=self.stop_emergency, timeout_callback=lambda: self.send_generic_emergency("c", "c", True))

        return True
            

    def send_fall_emergency(self, fall, is_timeout: bool = False):
        if not SETTINGS.UID:
            LOGS.warning("[AppManager] Non posso inviare il pacchetto d'emergenza (caduta) perchè l'orologio non ha ancora un UID.")
            return True

        if is_timeout:
            LOGS.warning(f"[AppManager] Nessun pacchetto ricevuto in risposta a pacchetto emergenza (caduta), riinvio.")
            bluethoothController.send(packetUtils.get_telemetry_packet(heartSensorController.currentBPM, False, batteryController.battery_level, accelerometerSensorController.get_step_counter(), True))
            bluethoothController.listen_for_packet(response_callback=self.stop_emergency, timeout_callback=lambda: self.send_fall_emergency(True, True))
            return True

        if fall:
            heartSensorController.stop()
            heartSensorController.isMesuring = False
            LOGS.warning("[MAIN] Messo in pausa sensore cardio.")

            vibrationController.vibrate()
            soundController.play_sound(CONFIG.DEFAULT_ALARM_SOUND_PATH, True, True)

            bluethoothController.send(packetUtils.get_telemetry_packet(heartSensorController.currentBPM, False, batteryController.battery_level, accelerometerSensorController.get_step_counter(), True))
            bluethoothController.listen_for_packet(response_callback=self.stop_emergency, timeout_callback=lambda: self.send_fall_emergency(True, True))

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
            bluethoothController.listen_for_packet(response_callback=self.save_uid_and_start, timeout_callback=lambda: LOGS.warning(f"[AppManager] Nessun pacchetto ricevuto in risposta a pacchetto 0."))
            
            return True

        if not heartSensorController.isMesuring: return True
        if not heartSensorController.session_id: heartSensorController.init_sensor()

        OSMANAGER.set_wake_lock(True)

        threading.Thread(target=LOGS.rotate_and_compress_logs, daemon=True).start()

        heartSensorController.start()
        GLib.timeout_add_seconds(CONFIG.H_MEASURMENTS_TIME, self.stop_and_send)

        return True

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