#include <Arduino.h>
#include "DataManage.h"
#include "MyWiFi.h"
#include "TCP.h"
#include "freertos/FreeRTOS.h"
#include "data.h"
#include "Log.h"

QueueHandle_t InQueue;
QueueHandle_t InQueueLogin;
QueueHandle_t OutQueue;
QueueHandle_t OutQueueLogin;
QueueHandle_t InQueueUpdate;
QueueHandle_t OutQueueUpdate;
QueueHandle_t UIDQueue;
QueueHandle_t InQueueCred;

extern "C" void app_main() {
    initArduino();

    Serial.begin(115200);
    delay(500);
    Log::stampaNormale("=== Avvio WI-FI ===");

    InQueue = xQueueCreate(200, sizeof(InData));
    InQueueLogin = xQueueCreate(20,  sizeof(InDataLogin));
    OutQueue = xQueueCreate(20,  sizeof(OutData));
    OutQueueLogin = xQueueCreate(20,  sizeof(OutDataLogin));
    InQueueUpdate = xQueueCreate(20, sizeof(InUpdateData));
    OutQueueUpdate = xQueueCreate(20, sizeof(OutUpdateData));
    InQueueCred = xQueueCreate(20, sizeof(InDataCred));
    configASSERT(InQueue && InQueueLogin && OutQueue && OutQueueLogin && InQueueUpdate && OutQueueUpdate && InQueueCred);

    NVSBegin();
    initUART();
    DataStart();
    WifiStart();
    tcpStart();
    
    Log::stampaNormale("=== Setup WI-FI completato ===");
}