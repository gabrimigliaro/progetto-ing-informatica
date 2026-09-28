#include "MyWiFi.h"

AsyncWebServer server(80);
Preferences prefs;
static volatile bool newCreds = false;
static bool routesSet = false;
String apName = "Nuovo_Nodo";

static const char PAGE[] PROGMEM = R"rawliteral(
<!DOCTYPE html><html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Configurazione ESP32</title>
<style>
  body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
       font-family:system-ui,sans-serif;background:linear-gradient(135deg,#1e3c72,#2a5298)}
  .card{background:#fff;padding:28px;border-radius:16px;width:85%;max-width:340px;
        box-shadow:0 10px 30px rgba(0,0,0,.3)}
  h2{margin:0 0 20px;text-align:center;color:#1e3c72}
  label{display:block;font-size:13px;color:#555;margin:12px 0 4px}
  input{width:100%;padding:10px;border:1px solid #ccc;border-radius:8px;
        box-sizing:border-box;font-size:15px}
  input:focus{outline:none;border-color:#2a5298}
  button{width:100%;margin-top:22px;padding:12px;border:0;border-radius:8px;
         background:#2a5298;color:#fff;font-size:16px;cursor:pointer}
  button:active{background:#1e3c72}
</style></head><body>
<div class="card">
  <h2>Configurazione WiFi</h2>
  <form method="POST" action="/save">
    <label>SSID router</label>
    <input name="ssid" required>
    <label>Password router</label>
    <input name="pass" type="password">
    <label>Nome access point</label>
    <input name="ap" required>
    <button>Salva</button>
  </form>
</div></body></html>
)rawliteral";


void WiFiCredentials(const char* ssid, const char* password) {
    prefs.begin("WiFi", false);
    prefs.putString("ssid", ssid);
    prefs.putString("password", password);
    prefs.putString("ap", apName);
    prefs.end();
}



static void readCreds(String& ssid, String& pass) {
    prefs.begin("WiFi", false);
    ssid = prefs.getString("ssid", "");
    pass = prefs.getString("password", "");
    apName = prefs.getString("ap", "ESP32-Setup");
    prefs.end();
}

void startApSta(const char* apSsid = "ESP32-Setup", const char* apPass = "12345678") {
    WiFi.mode(WIFI_AP_STA);
    WiFi.softAP(apSsid, apPass);

    Serial.print("AP attivo, IP: ");
    Serial.println(WiFi.softAPIP());   //192.168.4.1!!!

    if (!routesSet) {
        routesSet = true;

        server.on("/", HTTP_GET, [](AsyncWebServerRequest* r) {
            r->send(200, "text/html", PAGE);
        });

        server.on("/save", HTTP_POST, [](AsyncWebServerRequest* r) {
            if (r->hasParam("ssid", true) && r->hasParam("ap", true)) {
                String ssid = r->getParam("ssid", true)->value();
                String pass = r->hasParam("pass", true) ? r->getParam("pass", true)->value() : "";
                String ap   = r->getParam("ap", true)->value();

                WiFiCredentials(ssid.c_str(), pass.c_str());
                newCreds = true;

                r->send(200, "text/html",
                "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                "<body style='font-family:system-ui;text-align:center;padding:40px'>"
                "<h2>Salvato &#10003;</h2><p>Dati memorizzati.</p></body>");
            } else {
                r->send(400, "text/plain", "Dati mancanti");
            }
        });
    }

    server.begin();
}

void stopApSta() {
    server.end();
    WiFi.softAPdisconnect(true);
    WiFi.mode(WIFI_STA);
}

void WiFiInit() {
    WiFi.persistent(false);
    String ssid, pass;
    readCreds(ssid, pass);

    WiFi.mode(WIFI_STA);
    if (ssid.length() > 0) {
        WiFi.begin(ssid.c_str(), pass.c_str());
        unsigned long t = millis();
        while (WiFi.status() != WL_CONNECTED && millis() - t < 10000) {
            delay(200);
        }
        if (WiFi.status() == WL_CONNECTED) return;
    }

    startApSta(apName.c_str());
    Serial.println("Tentativo di connessione al router...");
    unsigned long lastTry = millis();
    while (WiFi.status() != WL_CONNECTED) {
        if (newCreds) {
            newCreds = false;
            readCreds(ssid, pass);
            WiFi.begin(ssid.c_str(), pass.c_str());
            lastTry = millis();
        } else if (ssid.length() > 0 && millis() - lastTry >= 10000) {
            lastTry = millis();
            WiFi.begin(ssid.c_str(), pass.c_str());
        }
        Serial.print(".");
        delay(200);
    }
    stopApSta();
}

void WifiUpdate() {
    static unsigned long lastAttempt = 0;
    if (WiFi.status() != WL_CONNECTED && millis() - lastAttempt > 10000) {
        lastAttempt = millis();
        WiFiInit();
    }
}