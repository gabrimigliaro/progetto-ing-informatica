import configparser
import os
import sys
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ETC_DIR = "/etc/watch_agent"

class ConfigManager:
    def __init__(self):
        self.config_file = os.path.join(ETC_DIR, "config.ini")
        self.env_file = os.path.join(BASE_DIR, ".env")

        self.load_config()
        self.parse_config()
        self.parse_env()
        
    def load_config(self):
        os.makedirs(ETC_DIR, exist_ok=True)

        if os.path.exists(os.path.join(BASE_DIR, "config.ini")):
            shutil.move(os.path.join(BASE_DIR, "config.ini"), self.config_file)
            print("[CONFIG] Rilevata nuova configurazione locale: aggiornata /etc/watch_agent/config.ini")

    def parse_config(self):
        self.parser = configparser.ConfigParser()
                
        if not os.path.exists(self.config_file):
            print(f"[CONFIG] Errore: File '{self.config_file}' non trovato.")
            sys.exit(1)
            
        self.parser.read(self.config_file)
        
        try:
            self.DEVICE_NAME = self.parser.get('General', 'device_name')
            self.DEVICE_NAME_OS = self.parser.get('General', 'device_name_os')

            self.VIB_DUR_PATH = self.parser.get('Vibration', 'vibrator_duration_path')
            self.VIB_ACT_PATH = self.parser.get('Vibration', 'vibrator_activate_path')
            self.VIB_GAIN_PATH = self.parser.get('Vibration', 'vibrator_gain_path')

            self.VIB_DUR_MS = self.parser.getint('Vibration', 'vibration_duration_ms')
            self.VIB_DELAY_MS = self.parser.getint('Vibration', 'vibration_delay_ms')
            self.VIB_GAIN = self.parser.getint('Vibration', 'vibration_gain')

            self.H_SERVICE = self.parser.get('HeartSensor', 'service')
            self.H_MANAGER_PATH = self.parser.get('HeartSensor', 'manager_path')
            self.H_SENSOR_PATH = self.parser.get('HeartSensor', 'sensor_path')
            self.H_SENSOR_NAME = self.parser.get('HeartSensor', 'sensor_name')
            self.H_SOCKET_PATH = self.parser.get('HeartSensor', 'socket_path')
            self.H_SENSOR_MANAGER_LOCAL = self.parser.get('HeartSensor', 'sensor_manager_local')
            self.H_SENSOR_LOCAL = self.parser.get('HeartSensor', 'sensor_local')

            self.H_MAX_ATTEMPTS = self.parser.getint('HeartSensor', 'max_attempts')
            self.H_ATTEMPTS_DELAY = self.parser.getfloat('HeartSensor', 'attemps_delay')
            self.H_MEASURMENTS_DELAY = self.parser.getfloat('HeartSensor', 'measurements_delay')
            self.H_MEASURMENTS_DELAY_MS = int(self.H_MEASURMENTS_DELAY * 1000)
            self.H_MEASURMENTS_TIME = self.parser.getfloat('HeartSensor', 'measurements_time')

            self.BLE_SERVICE_UUID = self.parser.get('Bluethooth', 'service_uuid')
            self.BLE_TIMEOUT_RECEIVE_TIME = self.parser.getint('Bluethooth', 'timeout_receive_time')
            self.BLE_ADVERTISEMENT = self.parser.get('Bluethooth', 'advertisement')
            self.BLE_ADVERTISEMENT_PATH = self.parser.get('Bluethooth', 'advertisement_path')
            self.BLE_ADVERTISEMENT_MANAGER = self.parser.get('Bluethooth', 'advertisement_manager')
            self.BLE_ADAPTER_PATH = self.parser.get('Bluethooth', 'adapter_path')
            self.BLE_BLUEZ_GENERAL_PATH = self.parser.get('Bluethooth', 'bluez_general_path')
            self.BLE_BLUEZ_ADAPTER_PATH = self.parser.get('Bluethooth', 'bluez_adapter_path')
            self.BLE_BLUEZ_DEVICE_PATH = self.parser.get('Bluethooth', 'bluez_device_path')

            self.DBUS_PROPRIETIES = self.parser.get('DBus', 'properties')
            self.DBUS_OBJECT_MANAGER = self.parser.get('DBus', 'object_manager')

            self.BATTERY_SERVICE = self.parser.get('Battery', 'service')
            self.BATTERY_REQUEST_PATH = self.parser.get('Battery', 'request_path')
            self.BATTERY_REQUEST_SERVICE = self.parser.get('Battery', 'request_service')

            self.BUTTON_DEV = self.parser.get('Buttons', 'button_dev')
            self.BUTTON_EVENT_FORMAT = self.parser.get('Buttons', 'event_format')

            self.LOGS_PATH = self.parser.get('Logs', 'logs_path')
            self.LOGS_MAX_SIZE_KB = self.parser.getint('Logs', 'max_size_kb')
            self.LOGS_MAX_BACKUPS = self.parser.getint('Logs', 'max_backups')

            self.WAKE_LOCK_PATH = self.parser.get('OS', 'wake_lock_path')
            self.WAKE_UNLOCK_PATH = self.parser.get('OS', 'wake_unlock_path')
            
        except configparser.NoSectionError as e:
            print(f"[CONFIG] Errore: Manca una sezione nel file INI - {e}")
            sys.exit(1)
        except configparser.NoOptionError as e:
            print(f"[CONFIG] Errore: Manca un parametro nel file INI - {e}")
            sys.exit(1)

    def parse_env(self):
        if not os.path.exists(self.env_file):
            print(f"[CONFIG] Errore: File '{self.env_file}' non trovato.")
            sys.exit(-1)

        with open(self.env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"): continue

                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")

                    os.environ[key] = value

CONFIG = ConfigManager()