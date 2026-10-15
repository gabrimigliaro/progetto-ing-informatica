import threading

from gi.repository import GLib  # type: ignore

from assets.managers.LogsManager import LOGS
from assets.managers.ConfigManager import CONFIG
from assets.managers.OSManager import OSMANAGER

from assets.controllers.HeartSensorController import heartSensorController
from assets.controllers.BatteryController import batteryController
from assets.controllers.AccelerometerSensorController import accelerometerSensorController
from assets.controllers.BluetoothController import bluethoothController
from assets.controllers.ButtonsController import buttonsController
from assets.controllers.WiFiController import wifiController

from assets.utils.PacketsUtils import packetUtils

class AppManager:
    def send_fall_emergency(self, fall):
        if fall:
            bluethoothController.send(packetUtils.get_telemetry_packet(heartSensorController.currentBPM, False, batteryController.battery_level, accelerometerSensorController.get_step_counter(), True))
            accelerometerSensorController.set_fall(False)

    def stop_and_send(self):
        try:
            LOGS.info("[MAIN] HeartSensor fermato. Invio bluethooth.")

            heartSensorController.stop()

            batteryController.get_battery_level()

            bluethoothController.send(packetUtils.get_telemetry_packet(heartSensorController.currentBPM, False, batteryController.battery_level, accelerometerSensorController.get_step_counter()))
        finally:
            OSMANAGER.set_wake_lock(False)

        return False

    def main_loop(self):
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