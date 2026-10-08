import os
import sys
from gi.repository import GLib #type: ignore

from assets.managers.ConfigManager import CONFIG
from assets.managers.LogsManager import LOGS

class VibrationController:
    def __init__(self):
        self.duration_path : str = CONFIG.VIB_DUR_PATH
        self.activate_path : str = CONFIG.VIB_ACT_PATH
        self.gain_path : str = CONFIG.VIB_GAIN_PATH

    def change_gain(self, gain : int = CONFIG.VIB_GAIN) -> bool:
        if os.path.exists(self.gain_path):
            try:
                with open(self.gain_path, "w") as f:
                    f.write(str(gain))

                LOGS.info(f"[VIB] Gain impostato su {gain}")
                return True
            except Exception as e:
                LOGS.error(f"[VIB] Errore durante la scrittura sysfs: {e}")
                return False
        else:
            LOGS.error(f"[VIB] Errore: non esiste il file {self.gain_path}.")
            return False

    def change_duration(self, duration_ms : int = CONFIG.VIB_DUR_MS) -> bool:
        if os.path.exists(self.duration_path):
            try:
                with open(self.duration_path, "w") as f:
                    f.write(str(duration_ms))
                    return True
            except Exception as e:
                LOGS.error(f"[VIB] Errore durante la scrittura sysfs: {e}")
                return False
        else:
            LOGS.error(f"[VIB] Errore: non esiste il file {self.duration_path}.")
            return False

    def reset_state(self) -> bool:
        self.change_gain(0)
        self.change_duration(0)

        return False

    def vibrate(self, duration_ms : int = CONFIG.VIB_DUR_MS, gain : int = CONFIG.VIB_GAIN) -> bool:
        if not self.change_gain(gain): return False
        if not self.change_duration(duration_ms): return False

        if os.path.exists(self.activate_path):
            try:
                with open(self.activate_path, "w") as f:
                    f.write("1")

                LOGS.info("[VIB] Vibrazione effettuata.")

                GLib.timeout_add(duration_ms + 10, self.reset_state)

                return False
            except Exception as e:
                LOGS.error(f"[VIB] Errore durante la scrittura sysfs: {e}")
                return False
        else:
            LOGS.error(f"[VIB] Errore: non esiste il file {self.duration_path} o il file {self.activate_path} (o entrambi).")
            sys.exit(1)

vibrationController = VibrationController()