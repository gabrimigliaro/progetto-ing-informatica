#include <Arduino.h>
#include "Encrypt.h"
#include "MyWiFi.h"
#include "DataManage.h"
#include "MyBLE.h"
#include "freertos/FreeRTOS.h"
#include "data.h"

QueueHandle_t InQueue;
QueueHandle_t InQueueLogin;
static BleBroadcaster ble;

static bool startBleWithRetry(int tries) {
    for (int i = 1; i <= tries; i++) {
        if (ble.begin("Node")) return true;
        Serial.printf("BLE: tentativo %d/%d fallito\n", i, tries);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
    return false;
}

extern "C" void app_main() {
    initArduino();

    Serial.begin(115200);
    delay(500);
    Serial.println(F("\n=== Avvio ==="));

    InQueue = xQueueCreate(200, sizeof(InData));
    InQueueLogin = xQueueCreate(20,  sizeof(InDataLogin));
    configASSERT(InQueue && InQueueLogin);

    WifiStart();
    DataStart();

    if (!startBleWithRetry(5)) {
        Serial.println(F("BLE non parte, riavvio"));
        delay(1000);
        esp_restart();
    }
    
    Serial.println(F("=== Setup completato ==="));
}