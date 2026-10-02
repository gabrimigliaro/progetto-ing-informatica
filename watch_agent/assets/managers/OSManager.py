import os

from assets.managers.ConfigManager import CONFIG
from assets.managers.LogsManager import LOGS

class OSManager:
    def __init__(self):
        self.name = CONFIG.DEVICE_NAME_OS

    def set_wake_lock(self, lock: bool):
        path = CONFIG.WAKE_LOCK_PATH if lock else CONFIG.WAKE_UNLOCK_PATH
        try:
            if os.path.exists(path):
                with open(path, "w") as f:
                    f.write(self.name)
        except Exception as e:
            LOGS.error(f"[POWER] Impossibile impostare wake_lock ({lock}): {e}")

OSMANAGER = OSManager()