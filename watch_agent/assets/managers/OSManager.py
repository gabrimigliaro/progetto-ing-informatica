import os

from assets.managers.ConfigManager import CONFIG
from assets.managers.LogsManager import LOGS

class OSManager:
    def __init__(self):
        self.name : str = CONFIG.DEVICE_NAME_OS
        self.GID : int = CONFIG.OS_CERES_GID

    def set_wake_lock(self, lock: bool):
        path = CONFIG.WAKE_LOCK_PATH if lock else CONFIG.WAKE_UNLOCK_PATH
        try:
            if os.path.exists(path):
                with open(path, "w") as f:
                    f.write(self.name)
        except Exception as e:
            LOGS.error(f"[POWER] Impossibile impostare wake_lock ({lock}): {e}")

    def drop_to_ceres(self):
        os.setgroups([self.GID])
        os.setgid(self.GID)
        os.setuid(self.GID)

OSMANAGER = OSManager()