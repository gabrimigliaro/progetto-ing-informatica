#include <Arduino.h>
#include "Encrypt.h"
#include "DataManage.h"
#include "MyBLE.h"
#include "freertos/FreeRTOS.h"
#include "data.h"
#include "NVS.h"
#include "Log.h"

QueueHandle_t InQueue;
QueueHandle_t InQueueLogin;
QueueHandle_t OutQueue;
QueueHandle_t OutQueueLogin;
QueueHandle_t InQueueUpdate;
QueueHandle_t OutQueueUpdate;
QueueHandle_t InQueueCred;
QueueHandle_t OutQueueSSID;
QueueHandle_t OutQueuePSW;
BleBroadcaster ble;


extern "C" void app_main() {
    initArduino();

    Serial.begin(115200);
    delay(500);
    Log::stampaNormale("=== Avvio BLE ===");

    InQueue = xQueueCreate(200, sizeof(InData));
    InQueueLogin = xQueueCreate(20,  sizeof(InDataLogin));
    OutQueue = xQueueCreate(20,  sizeof(OutData));
    OutQueueLogin = xQueueCreate(20,  sizeof(OutDataLogin));
    OutQueueUpdate = xQueueCreate(20, sizeof(OutUpdateData));
    InQueueUpdate = xQueueCreate(20, sizeof(InUpdateData));
    InQueueCred = xQueueCreate(20, sizeof(InDataCred));
    OutQueueSSID = xQueueCreate(20, sizeof(OutDataSSID));
    OutQueuePSW = xQueueCreate(20, sizeof(OutDataPSW));

    configASSERT(InQueue && InQueueLogin && OutQueue && OutQueueLogin && OutQueueUpdate && InQueueUpdate && InQueueCred && OutQueueSSID && OutQueuePSW);

    NVSBegin();

    if (!startBleWithRetry(5)) {
        Log::stampaAllarme("BLE: riavvio");
        delay(1000);
        esp_restart();
    }

    initUART();
    DataStart();
    
    Log::stampaNormale("=== Setup BLE completato ===");
}