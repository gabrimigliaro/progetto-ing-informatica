import threading

from gi.repository import GLib  # type: ignore
import dbus.mainloop.glib # type: ignore
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

from assets.managers.LogsManager import LOGS
from assets.managers.ConfigManager import CONFIG

from assets.managers.OSManager import OSMANAGER

from assets.controllers.HeartSensorController import heartSensorController
from assets.controllers.ButtonsController import buttonsController
from assets.controllers.BatteryController import batteryController
from assets.controllers.AccelerometerSensorController import accelerometerSensorController
from assets.controllers.BluetoothController import bluethoothController

from assets.utils.PacketsUtils import packetUtils

def stop_and_send():
    try:
        LOGS.info("[MAIN] HeartSensor fermato. Invio bluethooth.")

        heartSensorController.stop()

        batteryController.get_battery_level()

        bluethoothController.send(packetUtils.get_telemetry_packet(heartSensorController.currentBPM, False, batteryController.battery_level))
    finally:
        OSMANAGER.set_wake_lock(False)

    return False

def main_loop():
    if not heartSensorController.isMesuring: return True
    if not heartSensorController.session_id: heartSensorController.init_sensor()

    OSMANAGER.set_wake_lock(True)

    threading.Thread(target=LOGS.rotate_and_compress_logs, daemon=True).start()

    heartSensorController.start()
    GLib.timeout_add_seconds(CONFIG.H_MEASURMENTS_TIME, stop_and_send)

    return True

def main():
    loop = GLib.MainLoop()

    if buttonsController.btn_fd is not None:
        GLib.io_add_watch(buttonsController.btn_fd, GLib.IO_IN, buttonsController.on_button_event)

    GLib.timeout_add_seconds(int(CONFIG.H_MEASURMENTS_DELAY), main_loop)

    threading.Thread(target=accelerometerSensorController.start, daemon=True).start()

    main_loop()
    batteryController.get_battery_level()
    LOGS.success("[MAIN] Loop principale avviato.")

    try:
        loop.run()
    except KeyboardInterrupt:
        LOGS.info("[MAIN] Interruzione da tastiera (Ctrl+C).")
    finally:
        LOGS.info("[MAIN] Pulizia risorse...")

        if heartSensorController.session_id is not None:
            heartSensorController.exit()

        if hasattr(buttonsController, "close"):
            buttonsController.close()

        if accelerometerSensorController.session_id is not None:
            accelerometerSensorController.exit()

        LOGS.success("[MAIN] Chiusura completata.")

if __name__ == "__main__":
    main()