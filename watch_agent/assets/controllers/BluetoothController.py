import sys

import dbus # type: ignore
import dbus.service # type: ignore
import dbus.mainloop.glib # type: ignore
from gi.repository import GLib  # type: ignore

from assets.managers.ConfigManager import CONFIG
from assets.managers.LogsManager import LOGS

ADVERTISEMENT = CONFIG.BLE_ADVERTISEMENT
ADVERTISING_MANAGER = CONFIG.BLE_ADVERTISEMENT_MANAGER

class TelemetryAdvertisement(dbus.service.Object):
    def __init__(self, bus, payload):
        self.path = CONFIG.BLE_ADVERTISEMENT_PATH
        self.bus = bus
        
        self.service_uuid = CONFIG.BLE_SERVICE_UUID

        self.payload = payload
        
        super().__init__(bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(CONFIG.DBUS_PROPRIETIES, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != ADVERTISEMENT:
            raise dbus.exceptions.DBusException('Interface non valida')

        return {
            "Type": "peripheral",
            "LocalName": dbus.String(CONFIG.DEVICE_NAME),
            "ServiceData": dbus.Dictionary(
                {self.service_uuid: dbus.Array(self.payload, signature="y")},
                signature="sv",
            ),
        }

    @dbus.service.method(ADVERTISEMENT, in_signature='', out_signature='')
    def Release(self):
        LOGS.info("[BLE] Broadcast rilasciato da BlueZ.")

class BluetoothController:
    def __init__(self):
        self.bus = None
        self.adapter_props = None
        self.active_ad = None
        self.ad_manager = None
        self.adapter_path = CONFIG.BLE_ADAPTER_PATH

        self.timeout_time : int = CONFIG.BLE_TIMEOUT_RECEIVE_TIME

        self.scan_active : bool = False
        self.signal_match = None
        self.timeout_id = None
        self.response_callback = None
        self.timeout_callback = None

        if not self.init_dbus(): sys.exit(-1)

    def init_dbus(self) -> bool:
        try:
            self.bus = dbus.SystemBus()

            adapter_obj = self.bus.get_object(CONFIG.BLE_BLUEZ_GENERAL_PATH, self.adapter_path)
            self.adapter_props = dbus.Interface(adapter_obj, CONFIG.DBUS_PROPRIETIES)

            self.ad_manager = dbus.Interface(adapter_obj, ADVERTISING_MANAGER)

            LOGS.info("[Bluetooth] Interfaccia D-Bus BlueZ pronta.")

            return True
        except dbus.DBusException as e:
            LOGS.error(f"[Bluetooth] Impossibile connettersi a BlueZ: {e}")

            return False

    def set_power(self, state: bool) -> bool:
        if not self.adapter_props:
            if not self.init_dbus(): return False

        try:
            self.adapter_props.Set(CONFIG.BLE_BLUEZ_ADAPTER_PATH, "Powered", dbus.Boolean(state))

            LOGS.info(f"[Bluetooth] Stato radio impostato a: {state}")

            return True
        except dbus.DBusException as e:
            LOGS.error(f"[Bluetooth] Errore cambio stato Powered({state}): {e}")
            return False

    def is_powered(self) -> bool:
        try:
            return bool(self.adapter_props.Get(CONFIG.BLE_ADAPTER_PATH, "Powered"))
        except Exception:
            return False

    def start_advertising(self, payload) -> bool:
        try:
            self.active_ad = TelemetryAdvertisement(self.bus, payload)
            self.ad_manager.RegisterAdvertisement(
                self.active_ad.get_path(),
                dbus.Dictionary({}, signature='sv'),
                reply_handler=lambda: LOGS.success("[Bluetooth] Pacchetto BLE in trasmissione!"),
                error_handler=lambda e: LOGS.error(f"[Bluetooth] Errore registrazione: {e}")
            )
        except Exception as e:
            LOGS.error(f"[Bluetooth] Eccezione nell'avvio advertisement: {e}")
            self.set_power(False)

        return False

    def stop_advertising(self):
        if self.active_ad and self.ad_manager:
            try:
                if self.ad_manager:
                    self.ad_manager.UnregisterAdvertisement(self.active_ad.get_path())

                self.active_ad.remove_from_connection()
            except Exception:
                LOGS.error("[Bluetooth] Non è stato possibile fermare correttamente il bluethooth.")
                
            self.active_ad = None

            self.set_power(False)
            LOGS.info("[Bluetooth] Trasmissione completata. Radio SPENTA.")
        return False

    def send(self, payload, duration_sec: int = 2) -> bool:
        if not self.is_powered() and not self.set_power(True): return False

        GLib.timeout_add(300, self.start_advertising, payload)

        GLib.timeout_add_seconds(duration_sec + 1, self.stop_advertising)

        return True

    def stop_scanning(self):
        if not self.scan_active: return
        self.scan_active = False

        if self.timeout_id != None:
            GLib.source_remove(self.timeout_id)
            self.timeout_id = None

        if self.signal_match != None:
            self.signal_match.remove()
            self.signal_match = None

        try:
            adapter_obj = self.bus.get_object(CONFIG.BLE_BLUEZ_GENERAL_PATH, self.adapter_path)
            adapter_iface = dbus.Interface(adapter_obj, CONFIG.BLE_BLUEZ_ADAPTER_PATH)
            adapter_iface.StopDiscovery()
        except Exception:
            pass

        self.set_power(False)
        LOGS.info("[Bluetooth] Scansione BLE terminata. Radio SPENTA.")

    # Qua c'è da dividere in funzioni: chiamare classe packetUtils per il parsing
    # |
    # V
    def interfaces_added(self, object_path, interfaces):
        if not self.scan_active: return

        if CONFIG.BLE_BLUEZ_DEVICE_PATH in interfaces:
            device_props = interfaces[CONFIG.BLE_BLUEZ_DEVICE_PATH]
            name = str(device_props.get("Name", ""))
            mfg_data = device_props.get("ManufacturerData", {})

            if name == "ESP_REPLY" or 0xFFFF in mfg_data:
                LOGS.success(f"[Bluetooth] Pacchetto RICEVUTO da '{name}' ({object_path})")

                payload_str = ""
                if 0xFFFF in mfg_data:
                    raw_bytes = bytes(mfg_data[0xFFFF])
                    payload_str = raw_bytes.decode('utf-8', errors='ignore')

                received_info = {
                    "name": name,
                    "payload": payload_str,
                    "rssi": int(device_props.get("RSSI", 0)),
                    "mac": str(device_props.get("Address", ""))
                }

                self.stop_scanning()

                if self.response_callback:
                    self.response_callback(received_info)

                self.response_callback = None
                self.timeout_callback = None

    def on_timeout(self):
        LOGS.warning("[Bluetooth] Timeout scansione: nessun pacchetto ricevuto.")
        self.stop_scanning()

        if self.timeout_callback:
            self.timeout_callback()

        self.response_callback = None
        self.timeout_callback = None

        return False

    def listen_for_packet(self, response_callback=None, timeout_callback = None):
        LOGS.info(f"[Bluetooth] Avvio scansione BLE in ricezione per {self.timeout_time}s...")

        if not self.is_powered() and not self.set_power(True): return False

        self.scan_active = True
        self.response_callback = response_callback
        self.timeout_callback = timeout_callback

        self.signal_match = self.bus.add_signal_receiver(self.interfaces_added, dbus_interface=CONFIG.DBUS_OBJECT_MANAGER, signal_name="InterfacesAdded")

        try:
            adapter_obj = self.bus.get_object(CONFIG.BLE_BLUEZ_GENERAL_PATH, self.adapter_path)
            adapter = dbus.Interface(adapter_obj, CONFIG.BLE_BLUEZ_ADAPTER_PATH)
            
            try:
                adapter.SetDiscoveryFilter({'Transport': dbus.String('le')})
            except Exception:
                pass

            adapter.StartDiscovery()
        except dbus.DBusException as e:
            LOGS.error(f"[Bluetooth] Errore avvio StartDiscovery: {e}")
            self.stop_scanning()
            return False

        self.timeout_id = GLib.timeout_add_seconds(self.timeout_time, self.on_timeout)
        return True
    
bluethoothController = BluetoothController()