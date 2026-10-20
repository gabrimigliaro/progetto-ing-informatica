import os
import signal
import subprocess

from assets.managers.ConfigManager import CONFIG
from assets.managers.OSManager import OSMANAGER
from assets.managers.LogsManager import LOGS

_ENV = {**os.environ, "XDG_RUNTIME_DIR": f"/run/user/{CONFIG.OS_CERES_GID}", "HOME": "/home/ceres"}

class SoundController:
    def __init__(self):
        self._sound_looping: bool = False

    def play_sound(self, path: str = CONFIG.DEFAULT_NOTIFICATION_SOUND_PATH, wait: bool = CONFIG.DEFAULT_SOUND_WAIT, loop: bool = False):
        if self._sound_looping:
            self.stop_sound()

        script = ('gst-launch-1.0 -q filesrc location="$1" ! decodebin '
                '! audioconvert ! audioresample ! pulsesink')
        if loop:
            script = f"while {script}; do :; done"

        self.sound_process = subprocess.Popen(
            ["sh", "-c", script, "sh", path],
            env=_ENV, preexec_fn=OSMANAGER.drop_to_ceres, start_new_session=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        self._sound_looping = loop
        if wait and not loop:
            self.sound_process.wait()

    def stop_sound(self):
        p = self.sound_process
        if p and p.poll() is None:
            try:
                os.killpg(p.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            p.wait()
        self._sound_looping = False

soundController = SoundController()