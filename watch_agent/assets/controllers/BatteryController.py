import dbus #type: ignore

from assets.managers.ConfigManager import CONFIG
from assets.managers.LogsManager import LOGS

class BatteryController:
    def __init__(self):
        self.bus = None
        self.mce = None

        self.battery_level : int = -1
        
        self.init_dbus()

    def init_dbus(self):
        try:
            self.bus = dbus.SystemBus()
            mce_obj = self.bus.get_object(CONFIG.BATTERY_SERVICE, CONFIG.BATTERY_REQUEST_PATH)
            self.mce = dbus.Interface(mce_obj, CONFIG.BATTERY_REQUEST_SERVICE)

            LOGS.info("[Battery] Connessione D-Bus MCE inizializzata.")
        except dbus.DBusException as e:
            LOGS.error(f"[Battery] Errore connessione D-Bus MCE: {e}")

    def get_battery_level(self) -> int:
        if not self.mce: self.init_dbus()

        try:
            if self.mce:
                self.battery_level = self.mce.get_battery_level()

                LOGS.success(f"[Battery] Battery Level: {self.battery_level}%")
                return self.battery_level
        except dbus.DBusException as e:
            LOGS.error(f"[Battery] Errore lettura batteria via D-Bus: {e}")
            return -1

batteryController = BatteryController()