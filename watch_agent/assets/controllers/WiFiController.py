import threading

import dbus # type: ignore
import dbus.service # type: ignore
from dbus.mainloop.glib import DBusGMainLoop # type: ignore
from gi.repository import GLib #type: ignore

import sys

from assets.managers.ConfigManager import CONFIG
from assets.managers.LogsManager import LOGS

from assets.utils.EncryptUtils import encryptUtils

class Agent(dbus.service.Object):
    passphrase = ""

    @dbus.service.method(CONFIG.WIFI_AGENT_SERVICE_NAME, in_signature="oa{sv}", out_signature="a{sv}")
    def RequestInput(self, service, fields):
        return {"Passphrase": self.passphrase}

    @dbus.service.method(CONFIG.WIFI_AGENT_SERVICE_NAME, in_signature="os")
    def ReportError(self, service, error):
        pass

    @dbus.service.method(CONFIG.WIFI_AGENT_SERVICE_NAME)
    def Release(self):
        pass

    @dbus.service.method(CONFIG.WIFI_AGENT_SERVICE_NAME)
    def Cancel(self):
        pass

class WiFiController:
    def __init__(self):
        self.bus = None

        self.connman_name : str = CONFIG.WIFI_CONNMAN_NAME
        self.manager_name : str = CONFIG.WIFI_MANAGER_NAME
        self.manager_service_name : str = CONFIG.WIFI_MANAGER_SERVICE_NAME
        self.service_name : str = CONFIG.WIFI_SERVICE_NAME
        self.service_path : str = CONFIG.WIFI_SERVICE_PATH

        self.interface = None
        self.manager = None

        self.agent = None

        self.done_event = threading.Event()
        self.connected : bool = False

        if not self.init_wifi(): sys.exit(-1)

    def init_wifi(self) -> bool:
        try:
            self.bus = dbus.SystemBus(mainloop=DBusGMainLoop(), private=True)

            self.interface = dbus.Interface(self.bus.get_object(self.connman_name, self.service_path), self.service_name)
            self.manager = dbus.Interface(self.bus.get_object(self.connman_name, "/"), self.manager_name)

            self.agent = Agent(self.bus, CONFIG.WIFI_AGENT_PATH)

            LOGS.success("[WiFi] Connessione DBus stabilita.")
            return True
        except dbus.DBusException as e:
            LOGS.error(f"[WiFi] Impossibile stabilire la connessione DBus: {e}")
            return False

    def set_powered(self, on: bool) -> bool:
        try:
            self.interface.SetProperty("Powered", dbus.Boolean(on, variant_level=1))

            LOGS.success(f"[WiFi] Messo stato su {"acceso" if on else "spento"}")
            return True
        except dbus.DBusException as e:
            pass
            return False

    def on_connected(self, ssid):
        self.manager.UnregisterAgent(CONFIG.WIFI_AGENT_PATH)
        self.connected = True

        LOGS.success(f"[WiFi] Connesso alla rete {ssid}.")
        self.done_event.set()

    def on_error(self, e, ssid):
        self.manager.UnregisterAgent(CONFIG.WIFI_AGENT_PATH)
        self.connected = False

        LOGS.error(f"[WiFi] Impossibile connettersi alla rete {ssid}: {e}")
        self.done_event.set()

    def scan_and_connect(self, ssid: str, password: str) -> bool:
        try:
            self.interface.Scan()
        except dbus.DBusException as e:
            LOGS.error(f"[WiFi] Impossibile iniziare scan delle reti: {e}")
            self.done_event.set()
            return False

        try:
            services = self.manager.GetServices()
        
            for path, props in services:
                if (props.get("Type") == "wifi" and props.get("Name") == ssid
                        and props.get("Ethernet", {}).get("Interface") == "wlan0"):
                    break
            else:
                LOGS.warning("[WiFi] Rete WiFi non trovata. Impossibile connettersi.")
                self.done_event.set()
                return False
        except dbus.DBusException as e:
            LOGS.error(f"[WiFi] Impossibile ottenere tutti i servizi: {e}")
            self.done_event.set()
            return False
    
        service = dbus.Interface(self.bus.get_object(self.connman_name, path), self.manager_service_name)
        if props.get("Favorite"):
            service.Remove()
    
        self.agent.passphrase = password
        self.manager.RegisterAgent(CONFIG.WIFI_AGENT_PATH)

        service.Connect(reply_handler=lambda: self.on_connected(ssid), error_handler=lambda: self.on_error(e, ssid), timeout=CONFIG.WIFI_DEFAULT_TIMEOUT)
        return False

    def connect_wifi(self, ssid: str, password: str) -> bool:
        self.set_powered(True)

        ssid = encryptUtils.decrypt_string(ssid)
        password = encryptUtils.decrypt_string(password)

        GLib.timeout_add(4000, self.scan_and_connect, ssid, password)

        self.done_event.wait(timeout=15)

        return self.connected

    def exit(self):
        try:
            self.set_powered(False)
        finally:
            self.agent.remove_from_connection()
            self.bus.close()

            LOGS.info("[WiFi] Chiudo connessione, imposto a OFF e rilascio l'agent.")

wifiController = WiFiController()