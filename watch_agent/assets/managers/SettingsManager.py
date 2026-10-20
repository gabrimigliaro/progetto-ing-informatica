import json
import os
import sys
from pathlib import Path

from assets.managers.ConfigManager import CONFIG
from assets.managers.LogsManager import LOGS

from assets.controllers.SoundController import soundController

class SettingsManager:
    def __init__(self):
        self.settings_file : str = CONFIG.SETTINGS_FILE_PATH

        self.WIFI_SSID : str = None
        self.WIFI_PASSWORD : str = None
        self.UID : int = None

        self.data = {}

        self.load_settings()
        self.parse_settings()

    def load_settings(self) -> bool:
        Path(self.settings_file).parent.mkdir(parents=True, exist_ok=True)

        if not Path(self.settings_file).exists() or Path(self.settings_file).stat().st_size == 0:
            LOGS.info(f"[SettingsManager] File {self.settings_file} non trovato. Creazione nuovo file...")
            
            with open(Path(self.settings_file), "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)
                return True

    def parse_settings(self) -> bool:
        try:
            with open(Path(self.settings_file), "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except json.JSONDecodeError as e:
            LOGS.error(f"[SettingsManager] File JSON corrotto ({e}). Ripristino file vuoto.")

            with open(Path(self.settings_file), "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

            return False

        self.WIFI_SSID = self.data.get("wifi_ssid", None)
        self.WIFI_PASSWORD = self.data.get("wifi_password", None)
        self.UID = self.data.get("uid", None)

        return True

    def save_wifi_info(self, ssid: str, password: str) -> bool:
        if not Path(self.settings_file).exists():
            LOGS.error(f"[SettingsManager] Errore: File '{self.settings_file}' non trovato.")
            sys.exit(1)
        
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    
        data["wifi_ssid"] = ssid
        data["wifi_password"] = password
    
        temp_file = f"{self.settings_file}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
        os.replace(temp_file, self.settings_file)
    
        self.WIFI_SSID = ssid
        self.WIFI_PASSWORD = password

        LOGS.success(f"[SettingsManger] Informazioni WiFi salvate con successo.")
    
        return True

    def save_uid(self, uid: int) -> bool:
            if not Path(self.settings_file).exists():
                LOGS.error(f"[SettingsManager] Errore: File '{self.settings_file}' non trovato.")
                sys.exit(1)
            
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        
            data["uid"] = str(uid)
        
            temp_file = f"{self.settings_file}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        
            os.replace(temp_file, self.settings_file)
        
            self.UID = uid
    
            LOGS.success(f"[SettingsManger] UID salvato con successo.")
            soundController.play_sound(CONFIG.DEFAULT_START_SOUND_PATH)
        
            return True

SETTINGS = SettingsManager()