import dbus #type: ignore
import sys
from gi.repository import GLib #type: ignore

import os
import socket
import struct
import time
import math

from assets.managers.ConfigManager import CONFIG
from assets.managers.LogsManager import LOGS

from assets.controllers.VibrationController import vibrationController

class MotionAnalyzer:
    def __init__(self):
        self.FREEFALL_THRESHOLD = CONFIG.FREEFALL_THRESHOLD
        self.IMPACT_THRESHOLD = CONFIG.IMPACT_THRESHOLD
        
        self.freefall_detected = False
        self.freefall_time = 0

    def process_frame(self, x: float, y: float, z: float, timestamp: int):
        a_mag = math.sqrt(x**2 + y**2 + z**2)
        now = time.time()

        if a_mag < self.FREEFALL_THRESHOLD:
            self.freefall_detected = True
            self.freefall_time = now
            LOGS.warning(f"[MotionAnalyzer] Caduta libera rilevata! A_mag: {a_mag/1000:.2f} G")

        if self.freefall_detected and (now - self.freefall_time > 1.0):
            self.freefall_detected = False

        if a_mag > self.IMPACT_THRESHOLD:
            if self.freefall_detected:
                LOGS.warning(f"[MotionAnalyzer] PROBABILE CADUTA RILEVATA! Impatto: {a_mag:.1f} mG ({a_mag/1000:.2f}G)")
                self.freefall_detected = False

                vibrationController.vibrate()
                return "FALL"
            else:
                LOGS.warning(f"[MotionAnalyzer] Impulso/Urtata rilevata: {a_mag:.1f} mG ({a_mag/1000:.2f}G)")

                vibrationController.vibrate(100, 150)
                return "IMPULSE"

        return "NORMAL"

class AccelerometerSensorController:
    def __init__(self):
        self.bus = None
        self.manager : dbus.Interface = None
        self.sensor : dbus.Interface = None
        self.sensor_props : dbus.Interface = None

        self.data_socket : socket.socket = None
        self.socket_watch_id = None
        self.socket_buffer = bytearray()
        self.socket_path : str = CONFIG.H_SOCKET_PATH

        self.pid : int = os.getpid()
        self.session_id : int = None

        self.motion_analyzer = MotionAnalyzer()

        try:
            self.bus = dbus.SystemBus()

            mgr_obj = self.bus.get_object(CONFIG.SENSOR_SERVICE, CONFIG.SENSOR_MANAGER_PATH)
            self.manager = dbus.Interface(mgr_obj, CONFIG.SENSOR_MANAGER_LOCAL)

            if not self.init_system(): sys.exit(-1)

            LOGS.info("[AccelerometerSensor] Connessione D-Bus inizializzata.")
        except dbus.DBusException as e:
            LOGS.error(f"[AccelerometerSensor] Errore inizializzazione connessione: {e}")

    def init_system(self) -> bool:
        if not self.manager: return False

        if not self.init_plugin(): return False
        if not self.init_sensor(): return False
        if not self.init_session(): return False
        if not self.init_socket(): return False

        return True

    def init_plugin(self) -> bool:
        try:
            return bool(self.manager.loadPlugin(CONFIG.AC_SENSOR_NAME))
        except dbus.DBusException as e:
            LOGS.error(f"[AccelerometreSensor] Errore attivazione plugin: {e}")
            return False

    def init_sensor(self):
        try: 
            sensor_obj = self.bus.get_object(CONFIG.SENSOR_SERVICE, CONFIG.AC_SENSOR_PATH)
            self.sensor = dbus.Interface(sensor_obj, CONFIG.AC_SENSOR_LOCAL)
            self.sensor_props = dbus.Interface(sensor_obj, CONFIG.DBUS_PROPRIETIES)

            return True
        except dbus.DBusException as e:
            LOGS.error(f"[AccelerometreSensor] Errore inizializzazione sensore: {e}")
            return False

    def init_session(self) -> bool:
        try:
            self.session_id = int(self.manager.requestSensor(CONFIG.AC_SENSOR_NAME, dbus.Int64(self.pid)))

            LOGS.success(f"[AccelerometerSensor] Sessione ottenuta (ID: {self.session_id})")
            return True
        except dbus.DBusException as e:
            LOGS.error(f"[AccelerometerSensor] Errore durante la richiesta della sessione: {e}")
            return False

    def init_socket(self) -> bool:
        if not self.session_id: return False

        self.cleanup_socket()

        if not os.path.exists(self.socket_path):
            LOGS.error(f"[AccelerometerSensor] Socket file non trovato in {self.socket_path}")
            return False

        try:
            self.data_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.data_socket.connect(self.socket_path)
            self.data_socket.sendall(struct.pack("<I", self.session_id))
            self.data_socket.setblocking(False)

            self.handshake_done = False
            self.socket_watch_id = GLib.io_add_watch(self.data_socket.fileno(), GLib.IO_IN | GLib.IO_HUP | GLib.IO_ERR, self.on_socket_data)

            LOGS.success(f"[AccelerometerSensor] Socket connessa e handshake inviato per ID {self.session_id}.")
            return True
        except Exception as e:
            LOGS.error(f"[AccelerometerSensor] Errore connessione socket UNIX: {e}")
            self.cleanup_socket()
            return False

    def on_socket_data(self, source, condition) -> bool:
        if not self.data_socket:
            return False

        try:
            raw_data = self.data_socket.recv(1024)
            if not raw_data: return True

            self.socket_buffer.extend(raw_data)

            while len(self.socket_buffer) >= 28:
                if self.socket_buffer[:4] == b"\x01\x00\x00\x00":
                    packet = self.socket_buffer[:28]
                    self.socket_buffer = self.socket_buffer[28:]

                    valid, ts, x, y, z, accuracy = struct.unpack("<IqfffI", packet)

                    event = self.motion_analyzer.process_frame(x, y, z, ts)
                else:
                    self.socket_buffer = self.socket_buffer[1:]

        except Exception as e:
            LOGS.error(f"[AccelerometerSensor] Errore lettura socket: {e}")

        return True

    def start(self) -> bool:
        if not self.session_id or not self.sensor: return False

        try:
            self.sensor.start(dbus.Int32(self.session_id))

            LOGS.success(f"[AccelerometerSensor] Sensore avviato (ID Sessione: {self.session_id})")
            return True
        except dbus.DBusException as e:
            LOGS.error(f"[AccelerometerSensor] Errore durante l'avvio: {e}")
            return False

    def cleanup_socket(self):
        if self.socket_watch_id is not None:
            try: GLib.source_remove(self.socket_watch_id)
            except Exception: pass

            self.socket_watch_id = None

        if self.data_socket is not None:
            try: self.data_socket.shutdown(socket.SHUT_RDWR)
            except Exception: pass
            try: self.data_socket.close()
            except Exception: pass
            self.data_socket = None

        self.socket_buffer.clear()

    def exit(self) -> bool:
        if self.session_id is None: return False

        try:
            self.sensor.stop(dbus.Int32(self.session_id))
            result = self.manager.releaseSensor(CONFIG.AC_SENSOR_NAME, dbus.Int32(self.session_id), dbus.Int64(self.pid))

            return bool(result)
        except dbus.DBusException as e:
            LOGS.error(f"[AccelerometerSensor] Errore durante il rilascio: {e}")
            return False
        finally:
            self.session_id = None
            self.started = False
            self.cleanup_socket()

accelerometerSensorController = AccelerometerSensorController()