import dbus #type: ignore
from gi.repository import GLib #type: ignore
import time
import sys
import os
import socket
import struct

from assets.managers.ConfigManager import CONFIG
from assets.managers.LogsManager import LOGS

class HeartSensorController:
    def __init__(self):
        self.session_id : int = None
        self.bus = None
        self.manager = None
        self.sensor = None

        self.data_socket = None
        self.socket_watch_id = None
        self.socket_buffer = bytearray()
        self.socket_path : str = CONFIG.H_SOCKET_PATH

        self.pid : int = os.getpid()

        self.isMesuring : bool = True
        self.currentBPM : int = 0

        try:
            self.bus = dbus.SystemBus()

            mgr_obj = self.bus.get_object(CONFIG.SENSOR_SERVICE, CONFIG.SENSOR_MANAGER_PATH)
            self.manager = dbus.Interface(mgr_obj, CONFIG.SENSOR_MANAGER_LOCAL)

            sensor_obj = self.bus.get_object(CONFIG.SENSOR_SERVICE, CONFIG.H_SENSOR_PATH)
            self.sensor = dbus.Interface(sensor_obj, CONFIG.H_SENSOR_LOCAL)

            LOGS.info("[HeartSensor] Connessione inizializzata con successo.")
        except dbus.DBusException as e:
            LOGS.error(f"[HeartSensor] Errore inizializzazione connessione: {e}")
            sys.exit(1)

    def init_sensor(self) -> bool:
        if not self.init_plugin(): sys.exit(1)
        if not self.init_session(): sys.exit(1)
        if not self.init_socket(): sys.exit(1)

        return True

    def init_plugin(self) -> bool:
        if not self.manager or not self.sensor:
            LOGS.error("[HeartSensor] Interfacce non pronte.")
            return False

        LOGS.info("[HeartSensor] Attivo il plugin hrmsensor.")

        try:
            self.manager.loadPlugin(CONFIG.H_SENSOR_NAME)
            LOGS.success("[HeartSensor] Plugin attivato con successo.")
            return True
        except dbus.DBusException as e:
            LOGS.error(f"[HeartSensor] Errore durante la attivazione del plugin: {e}")
            return False

    def init_session(self, max_attempts : int = CONFIG.H_MAX_ATTEMPTS, delay : int = CONFIG.H_ATTEMPTS_DELAY) -> bool:
        if not self.sensor: return False

        for attempt in range(1, max_attempts + 1):
            try:
                self.session_id = int(self.manager.requestSensor(CONFIG.H_SENSOR_NAME, dbus.Int64(self.pid)))
                LOGS.success(f"[HeartSensor] Sessione ottenuta al tentativo {attempt}: ID {self.session_id}")

                return True
            except dbus.DBusException:
                    LOGS.warning(f"[HeartSensor] Warning: Tentativo {attempt}/{max_attempts} fallito. Riprovo tra {delay}s...")
            
            time.sleep(delay)
        else:
            LOGS.error(f"[HeartSensor] Errore: Impossibile ottenere l'ID sessione dopo {max_attempts} tentativi.")
            return False

    def init_socket(self) -> bool:
        if not self.session_id: return False

        self.cleanup_socket()

        if not os.path.exists(self.socket_path):
            LOGS.error(f"[HeartSensor] Socket file non trovato in {self.socket_path}")
            return False

        try:
            self.data_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.data_socket.connect(self.socket_path)

            handshake_payload = struct.pack("<I", self.session_id)
            self.data_socket.sendall(handshake_payload)
            self.data_socket.setblocking(False)

            self.socket_watch_id = GLib.io_add_watch(self.data_socket.fileno(), GLib.IO_IN, self.on_socket_data)

            LOGS.success(f"[HeartSensor] Socket UNIX connessa e Handshake completato per ID {self.session_id}.")
            return True
        except Exception as e:
            LOGS.error(f"[HeartSensor] Errore connessione socket UNIX: {e}")
            return False

    def on_socket_data(self, source, condition) -> bool:
        if not self.data_socket: return False

        try:
            raw_data = self.data_socket.recv(1024)
            if not raw_data:
                return True

            self.socket_buffer.extend(raw_data)

            if len(self.socket_buffer) > 0 and self.socket_buffer[0] == 0x0A:
                self.socket_buffer = self.socket_buffer[1:]

            while len(self.socket_buffer) >= 20:
                packet = self.socket_buffer[:20]
                self.socket_buffer = self.socket_buffer[20:]

                valid, timestamp, accuracy, bpm = struct.unpack("<IqIi", packet)

                if valid == 1 and bpm > 0:
                    self.currentBPM = int(bpm)
                    LOGS.info(f"[HeartSensor] Current BPM: {self.currentBPM}")

        except Exception:
            pass

        return True

    def start(self) -> bool:
        if not self.session_id or not self.sensor: return False

        try:
            self.sensor.start(dbus.Int32(self.session_id))
            LOGS.success(f"[HeartSensor] Sensore attivo (ID Sessione: {self.session_id})")

            self.isMesuring = True
            return True
        except dbus.DBusException as e:
            LOGS.error(f"[HeartSensor] Errore durante l'attivazione del servizio: {e}")
            return False

    def cleanup_socket(self):
        if self.socket_watch_id is not None:
            try:
                GLib.source_remove(self.socket_watch_id)
            except Exception:
                pass
            self.socket_watch_id = None

        if self.data_socket is not None:
            try:
                self.data_socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.data_socket.close()
            except Exception:
                pass
            self.data_socket = None

        self.socket_buffer.clear()

    def stop(self) -> bool:
        LOGS.info(f"[HeartSensor] Arresto il sensore {self.session_id}.")

        try:
            self.sensor.stop(dbus.Int32(self.session_id))
        except dbus.DBusException as e:
            LOGS.error(f"[HeartSensor] Errore durante lo stop: {e}")

        return False

    def exit(self) -> bool:
        if self.session_id is None: return False

        try:
            LOGS.info(f"[HeartSensor] Arresto e rilascio sessione {self.session_id}.")

            self.sensor.stop(dbus.Int32(self.session_id))

            result = self.manager.releaseSensor(CONFIG.H_SENSOR_NAME, dbus.Int32(self.session_id), dbus.Int64(os.getpid()))

            self.session_id = None

            if bool(result): return True
            else:
                LOGS.warning(f"[HeartSensor] Il rilascio del sensore ha restituito False.")
                return False

        except dbus.DBusException as e:
            LOGS.error(f"[HeartSensor] Errore durante l'arresto completo: {e}")
            return False

heartSensorController = HeartSensorController()