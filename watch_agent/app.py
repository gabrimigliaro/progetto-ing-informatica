import os
import threading

from gi.repository import GLib  # type: ignore
import dbus.mainloop.glib # type: ignore
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

from assets.managers.LogsManager import LOGS
from assets.managers.ConfigManager import CONFIG
from assets.managers.SettingsManager import SETTINGS

from assets.controllers.ButtonsController import buttonsController
from assets.controllers.BatteryController import batteryController
from assets.controllers.AccelerometerSensorController import accelerometerSensorController

from assets.managers.UpdateManager import updateManager
from assets.managers.AppManager import appManager

from assets.controllers.SoundController import soundController
from assets.utils.EncryptUtils import encryptUtils


def main():
    loop = GLib.MainLoop()

    if buttonsController.btn_fd is not None:
        #GLib.io_add_watch(buttonsController.btn_fd, GLib.IO_IN, buttonsController.on_button_event)
        GLib.io_add_watch(buttonsController.btn_fd, GLib.IO_IN, appManager.send_generic_emergency)

    GLib.timeout_add_seconds(int(CONFIG.H_MEASURMENTS_DELAY), appManager.main_loop)

    accelerometerSensorController.on_fall_callback = appManager.send_fall_emergency
    threading.Thread(target=accelerometerSensorController.start, daemon=True).start()

    SETTINGS.save_wifi_info(encryptUtils.encrypt_string(os.environ.get("DEMO_WIFI_NAME")), encryptUtils.encrypt_string(os.environ.get("DEMO_WIFI_PASSWORD")))

    #threading.Thread(target=updateManager.update, daemon=True).start()

    appManager.main_loop()
    batteryController.get_battery_level()
    LOGS.success(f"[MAIN] Loop principale avviato (V{os.environ.get("VERSION")}).")

    soundController.play_sound(CONFIG.DEFAULT_START_SOUND_PATH)

    try:
        loop.run()
    except KeyboardInterrupt:
        LOGS.info("[MAIN] Interruzione da tastiera (Ctrl+C).")
    finally:
        appManager.close_app()

if __name__ == "__main__":
    main()