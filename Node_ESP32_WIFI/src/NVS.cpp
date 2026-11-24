#include "NVS.h"
#include "data.h"
#include "Log.h"

uint8_t key[32] = {0};
std::string url;
NVSConfig nvs;

bool NVSConfig::begin(bool readOnly) {
  return _prefs.begin("space", readOnly);
}

void NVSConfig::end() {
  _prefs.end();
}

bool NVSConfig::getUrl() {
  url = _prefs.getString("url", "").c_str();
  return !url.empty();
}

bool NVSConfig::getKey() {
  if (_prefs.getBytesLength("key") != sizeof(key)) {
    memset(key, 0, sizeof(key));
    return false;
  }
  return _prefs.getBytes("key", key, sizeof(key)) == sizeof(key);
}

bool NVSConfig::setUrl(const std::string& v) {
  url = v;
  return _prefs.putString("url", v.c_str()) == v.size();
}

bool NVSConfig::setKey(const uint8_t* k) {
  memcpy(key, k, sizeof(key));
  return _prefs.putBytes("key", k, sizeof(key)) == sizeof(key);
}

void buttonTask(void *pvParameters) {
  String del = "";
  const int BTN = 4;
  const TickType_t reqTime = pdMS_TO_TICKS(5000);
  
  pinMode(BTN, INPUT_PULLDOWN);
  
  TickType_t pressStartTime = 0;
  bool pressed = false;
  bool actionTriggered = false;

  for(;;) {
    bool isPressed = (digitalRead(BTN) == HIGH);

    if (isPressed) {
      if (!pressed) {
        pressed = true;
        pressStartTime = xTaskGetTickCount();
        actionTriggered = false;
      } else if (!actionTriggered) {
        if ((xTaskGetTickCount() - pressStartTime) >= reqTime) {
          actionTriggered = true;
          Log::stampaWarning("NVS DELETE: Pulsante premuto per 5 secondi"); 
          WiFiCredentials(del.c_str(), del.c_str(), del.c_str(), del.c_str(), del.c_str(), del.c_str());
          WifiDisconnect();
        }
      }
    } else {
      pressed = false;
    }

    vTaskDelay(pdMS_TO_TICKS(100));
  }
}

void NVSBegin() {
  xTaskCreate(buttonTask, "BTN", 3072, nullptr, 3, nullptr);
  if (!nvs.begin(false)) {
    Log::stampaAllarme("NVS: namespace non apribile");
    return;
  }
  if (!nvs.getKey()) Log::stampaAllarme("NVS: KEY assente");
  if (!nvs.getUrl()) Log::stampaAllarme("NVS: URL assente");
  nvs.end();
}