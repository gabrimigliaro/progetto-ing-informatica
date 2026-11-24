#include "MyWiFi.h"
#include "Log.h"

AsyncWebServer server(80);
Preferences prefs;
static volatile bool newCreds = false;
static bool routesSet = false;
String apName = "Nodo_ESP32";
DNSServer dnsServer;
String ssid, pass;

String sciIP = "";
static String staticIP = "";
static String gatewayIP = "";
static String subnetMask = "";

static const char PAGE[] PROGMEM = R"rawliteral(
<!DOCTYPE html><html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Configurazione NodoESP</title>
<style>
  * { box-sizing: border-box; }

    html, body {
    margin: 0;
    padding: 0;
    min-height: 100%;
    background-color: #2a5298;
    overscroll-behavior: none;
    }

    body {
    min-height: 100svh;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: system-ui, -apple-system, sans-serif;
    padding: clamp(12px, 4vw, 24px);
    position: relative;
    z-index: 1;
    }

    body::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: -1;
    background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    pointer-events: none;
    }
  .card {
    background: #fff;
    padding: clamp(20px, 5vw, 32px);
    border-radius: 16px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 10px 30px rgba(0,0,0,.3);
  }
  h2 {
    margin: 0 0 16px;
    text-align: center;
    color: #1e3c72;
    font-size: clamp(1.2rem, 5vw, 1.5rem);
  }
  label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: #555;
    margin: 10px 0 4px;
  }
  input {
    width: 100%;
    padding: 12px;
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 16px; /* Previene lo zoom automatico su iPhone */
    outline: none;
    transition: border-color .2s;
    -webkit-appearance: none;
  }
  input:focus { border-color: #2a5298; }
  input.invalid { border-color: #ef4444 !important; }
  .error-msg {
    display: none;
    color: #ef4444;
    font-size: 12px;
    margin-top: 4px;
    font-weight: 500;
  }
  .error-msg.visible { display: block; }
  button {
    width: 100%;
    margin-top: 20px;
    padding: 14px;
    border: 0;
    border-radius: 8px;
    background: #2a5298;
    color: #fff;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: background .2s;
    -webkit-tap-highlight-color: transparent;
  }
  button:active { background: #1e3c72; }
</style></head><body>
<div class="card">
  <h2>Configurazione WiFi</h2>
  <form id="cfgForm" method="POST" action="/save">
    <label>SSID router</label>
    <input name="ssid" required placeholder="Nome rete WiFi">
    <label>Password router</label>
    <input name="pass" type="password" required minlength="8" placeholder="Password (min 8 caratteri)">
    <label>Nome access point</label>
    <input id="apInput" name="ap" required maxlength="32" placeholder="Es. Nodo_ESP32">
    <span id="apError" class="error-msg">Il nome non può contenere la sequenza "|t"</span>
    <label>IP Nodo ESP</label>
    <input name="ip" required placeholder="192.168.1.2">
    <label>Gateway</label>
    <input name="gw" required placeholder="192.168.1.1">
    <label>Subnet Mask</label>
    <input name="sn" required placeholder="255.255.255.0">
    <label>IP Server SCI</label>
    <input name="sci" required placeholder="192.168.1.3">
    <button type="submit">Salva</button>
  </form>
</div>
<script>
  const form = document.getElementById('cfgForm');
  const apInput = document.getElementById('apInput');
  const apError = document.getElementById('apError');

  function checkApValidity() {
    if (apInput.value.includes('|t')) {
      apInput.classList.add('invalid');
      apError.classList.add('visible');
      return false;
    } else {
      apInput.classList.remove('invalid');
      apError.classList.remove('visible');
      return true;
    }
  }

  apInput.addEventListener('input', checkApValidity);
  form.addEventListener('submit', function(e) {
    if (!checkApValidity()) {
      e.preventDefault();
      apInput.focus();
    }
  });
</script>
</body></html>
)rawliteral";

static void applyStaticIPConfig() {
    IPAddress ip, gw, sn;
    if (ip.fromString(staticIP) && gw.fromString(gatewayIP) && sn.fromString(subnetMask)) {
        WiFi.config(ip, gw, sn);
        Log::stampaInfo("WI-FI: IP Statico applicato");
    } else {
        Log::stampaWarning("WI-FI: Errore parsing IP statico");
    }
}

void WiFiCredentials(const char* ssid, const char* password, const char* ip, const char* gw, const char* sn, const char* sci) {
    prefs.begin("WiFi", false);
    prefs.putString("ssid", ssid);
    prefs.putString("password", password);
    prefs.putString("ap", apName);
    prefs.putString("ip", ip);
    prefs.putString("gw", gw);
    prefs.putString("sn", sn);
    prefs.putString("sci", sci);
    prefs.end();
}

static void readCreds(String& ssid, String& pass) {
    prefs.begin("WiFi", true);
    ssid = prefs.getString("ssid", "");
    pass = prefs.getString("password", "");
    apName = prefs.getString("ap", "Nodo_ESP32");
    staticIP = prefs.getString("ip", "");
    gatewayIP = prefs.getString("gw", "");
    subnetMask = prefs.getString("sn", "");
    sciIP = prefs.getString("sci", "");
    prefs.end();
}

void WifiDisconnect() {
    WiFi.disconnect(true);
    Log::stampaInfo("WI-FI: disconnesso");
}

static void startApSta(const char* apSsid = "ESP32-Setup", const char* apPass = "12345678") {
    WiFi.mode(WIFI_AP_STA);
    WiFi.softAP(apSsid, apPass);

    Log::stampaInfo("WI-FI AP: attivo");
    dnsServer.start(53, "*", WiFi.softAPIP());

    if (!routesSet) {
        routesSet = true;

        server.on("/", HTTP_GET, [](AsyncWebServerRequest* r) {
            r->send(200, "text/html", PAGE);
        });

        server.on("/save", HTTP_POST, [](AsyncWebServerRequest* r) {
            if (r->hasParam("ssid", true) && r->hasParam("ap", true) &&
                r->hasParam("ip", true)   && r->hasParam("gw", true) &&
                r->hasParam("sn", true)   && r->hasParam("sci", true)) {
                
                String ssid = r->getParam("ssid", true)->value();
                String pass = r->hasParam("pass", true) ? r->getParam("pass", true)->value() : "";
                String ap = r->getParam("ap", true)->value();
                String ip = r->getParam("ip", true)->value();
                String gw = r->getParam("gw", true)->value();
                String sn = r->getParam("sn", true)->value();
                String sci = r->getParam("sci", true)->value();

                if (ssid.length() == 0 || ap.length() == 0 || ip.length() == 0 ||
                    gw.length() == 0 || sn.length() == 0 || sci.length() == 0) {
                    r->send(400, "text/plain", "Tutti i campi (tranne la password) sono obbligatori");
                    return;
                }
                
                if (ssid.length() > 32 || ap.length() > 32 ||
                    (pass.length() > 0 && (pass.length() < 8 || pass.length() > 63))) {
                    r->send(400, "text/plain", "Lunghezza SSID/password non valida");
                    return;
                }

                if (ap.indexOf("|t") != -1) {
                    r->send(400, "text/plain", "Il nome access point non puo' contenere la sequenza '|t'");
                    return;
                }

                IPAddress testIP, testGW, testSN, testSCI;
                if (!testIP.fromString(ip) || !testGW.fromString(gw) || 
                    !testSN.fromString(sn) || !testSCI.fromString(sci)) {
                    r->send(400, "text/plain", "Uno o piu' indirizzi IP non sono validi (es. 192.168.1.1)");
                    return;
                }

                apName = ap;
                staticIP = ip;
                gatewayIP = gw;
                subnetMask = sn;
                sciIP = sci;

                WiFiCredentials(ssid.c_str(), pass.c_str(), ip.c_str(), gw.c_str(), sn.c_str(), sci.c_str());
                newCreds = true;

                r->send(200, "text/html",
                "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                "<body style='font-family:system-ui;text-align:center;padding:40px'>"
                "<h2>Salvato &#10003;</h2><p>Dati memorizzati.</p></body>");
            } else {
                r->send(400, "text/plain", "Dati obbligatori mancanti");
            }
        });

        server.onNotFound([](AsyncWebServerRequest *r) {
            r->redirect(String("http://") + WiFi.softAPIP().toString() + "/");
        });
    }

    server.begin();
}

static void stopApSta() {
    dnsServer.stop();
    server.end();
    WiFi.softAPdisconnect(true);
    WiFi.mode(WIFI_STA);
}

void WiFiInit() {
    WiFi.persistent(false);
    WiFi.setAutoReconnect(false);
    readCreds(ssid, pass);

    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);
    if (ssid.length() > 0) {
        applyStaticIPConfig();
        WiFi.begin(ssid.c_str(), pass.c_str());
        unsigned long t = millis();
        while (WiFi.status() != WL_CONNECTED && millis() - t < 10000) {
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
        if (WiFi.status() == WL_CONNECTED) return;
    }

    startApSta(apName.c_str());
    Log::stampaWarning("WI-FI: Tentativo di connessione al router...");
    unsigned long lastTry = millis();
    unsigned long lastDot = 0;
    while (WiFi.status() != WL_CONNECTED) {
        dnsServer.processNextRequest();
        if (newCreds) {
            newCreds = false;
            readCreds(ssid, pass);
            applyStaticIPConfig();
            WiFi.begin(ssid.c_str(), pass.c_str());
            lastTry = millis();
        } else if (ssid.length() > 0 && millis() - lastTry >= 10000
                && WiFi.softAPgetStationNum() == 0) {
                lastTry = millis();
                Log::stampaWarning("RETRY WiFi.begin()");
                applyStaticIPConfig();
                WiFi.begin(ssid.c_str(), pass.c_str());
        }
        if (millis() - lastDot >= 1000) {
            lastDot = millis();
            Log::stampaWarning(".");
        }
        delay(10);
    }
    Log::stampaInfo("WI-FI: connesso");
    stopApSta();
}

void WifiUpdate() {
    static unsigned long lastAttempt = 0;
    if (WiFi.status() != WL_CONNECTED && millis() - lastAttempt > 10000) {
        lastAttempt = millis();
        WiFiInit();
        lastAttempt = millis();
    }
}

static void WifiTask(void *arg) {
    WiFiInit();
    for (;;) {
        WifiUpdate();
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void WifiStart() {
    xTaskCreatePinnedToCore(WifiTask, "WifiTask", 8192, nullptr, 2, nullptr, 1);
}