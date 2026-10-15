import os
import subprocess

from assets.managers.ConfigManager import CONFIG
from assets.managers.OSManager import OSMANAGER

_ENV = {**os.environ, "XDG_RUNTIME_DIR": f"/run/user/{CONFIG.OS_CERES_GID}", "HOME": "/home/ceres"}

class SoundController:
    def play_sound(self, path: str = CONFIG.DEFAULT_NOTIFICATION_PATH, wait: bool = CONFIG.DEFAULT_WAIT):
        p = subprocess.Popen(
            ["gst-launch-1.0", "-q", "filesrc", f"location={path}", "!", "decodebin",
            "!", "audioconvert", "!", "audioresample", "!", "pulsesink"],
            env=_ENV, preexec_fn=OSMANAGER.drop_to_ceres,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        if wait:
            p.wait()

soundController = SoundController()