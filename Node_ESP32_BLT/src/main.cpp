#include <Arduino.h>
#include "BLE.h"
#include "Encrypt.h"
#include "MyWiFi.h"

unsigned long lastSendMs = 0;
const unsigned long sendInt = 2000;
const extern unsigned char key[32] = "Chiave"; 
uint8_t bpm = 0;
bool fall = false;
bool emergency = false;

extern "C" void app_main() {
    initArduino();

    Serial.begin(115200);
    delay(500);
    Serial.println(F("\n=== Avvio ESP32 secure link ==="));

    WiFiInit();

    Serial.println(F("=== Setup completato ==="));

    while (true) {
        WifiUpdate();
        delay(10);
    }
}