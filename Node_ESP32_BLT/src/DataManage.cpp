#include "DataManage.h"
#include "freertos/semphr.h"

bool validUID[256] = {0};
Preferences preferences;
String ssid;
String pass;

static void InDataTask(void *arg) {
    InData rx;
    for (;;) {
        if (xQueueReceive(InQueue, &rx, portMAX_DELAY) != pdTRUE) continue;
        Log::stampaNormale("UID:%u BPM:%u BAT:%u STEPS:%u RSSI:%d fall:%u emerg:%u",
            rx.UID, rx.bpm, rx.battery, rx.steps, rx.rssi, rx.fall, rx.emergency);

        Log::stampaInfo("UART TX: pacchetto 10");
        sendUART(&rx, sizeof(rx));
    }
}

static void InLoginDataTask(void *arg) {
    InDataLogin rxLogin;
    for (;;) {
        if (xQueueReceive(InQueueLogin, &rxLogin, pdMS_TO_TICKS(100)) == pdTRUE) {
            Log::stampaInfo("UART TX: pacchetto 1");
            sendUART(&rxLogin, sizeof(rxLogin));
        }
        vTaskDelay(pdMS_TO_TICKS(100)); 
    }
}

static void OutDataTask(void *arg) {
    OutData rx;
    for (;;) {
        if (xQueueReceive(OutQueue, &rx, pdMS_TO_TICKS(100)) == pdTRUE){
            vTaskDelay(pdMS_TO_TICKS(1500));
            Log::stampaInfo("BLE TX: pacchetto 11");
            ble.send(&rx, sizeof(rx));
        }
    }
}

static void OutLoginDataTask(void *arg) {
    OutDataLogin rxLogin;
    for (;;) {
        if (xQueueReceive(OutQueueLogin, &rxLogin, pdMS_TO_TICKS(100)) == pdTRUE) {
            nvs.setValidUID(rxLogin.UID, true);
            ble.send(&rxLogin, sizeof(rxLogin));
            Log::stampaInfo("BLE TX: pacchetto 1");
        }
        vTaskDelay(pdMS_TO_TICKS(100)); 
    }
}

static void InUpdateDataTask(void *arg) {
    InUpdateData rxUpdate;
    for (;;) {
        if (xQueueReceive(InQueueUpdate, &rxUpdate, pdMS_TO_TICKS(100)) == pdTRUE) {
            Log::stampaInfo("UART TX: pacchetto 2");
            sendUART(&rxUpdate, sizeof(rxUpdate));
        }
        vTaskDelay(pdMS_TO_TICKS(100)); 
    }
}

static void OutUpdateDataTask(void *arg) {
    OutUpdateData rxUpdate;
    for (;;) {
        if (xQueueReceive(OutQueueUpdate, &rxUpdate, pdMS_TO_TICKS(100)) == pdTRUE) {
            Log::stampaInfo("BLE TX:Paccheto 3");
            ble.send(&rxUpdate, sizeof(rxUpdate));
        }
        vTaskDelay(pdMS_TO_TICKS(100)); 
    }
}

static void InCredDataTask(void *arg) {
    InDataCred rxUpdate;
    for (;;) {
        if (xQueueReceive(InQueueCred, &rxUpdate, pdMS_TO_TICKS(100)) == pdTRUE) {
            sendUART(&rxUpdate, sizeof(rxUpdate));
        }
        vTaskDelay(pdMS_TO_TICKS(100)); 
    }
}

static void OutCredDataTask(void *arg) {
    OutDataSSID rx1;
    OutDataPSW rx2;
    for (;;) {
        if(xQueueReceive(OutQueueSSID, &rx1, pdMS_TO_TICKS(100)) == pdTRUE) {
            ble.send(&rx1, sizeof(rx1));
        }
        if(xQueueReceive(OutQueuePSW, &rx2, pdMS_TO_TICKS(100)) == pdTRUE) {
            ble.send(&rx2, sizeof(rx2));
        }
    }
}

void DataStart() {
    xTaskCreate(InDataTask, "InDataTask", 3072, nullptr, 3, nullptr);
    xTaskCreate(InLoginDataTask, "InLoginDataTask", 3072, nullptr, 3, nullptr);
    xTaskCreate(OutLoginDataTask, "OutLoginDataTask", 3072, nullptr, 3, nullptr);
    xTaskCreate(OutDataTask, "OutDataTask", 3072, nullptr, 3, nullptr);
    xTaskCreate(InUpdateDataTask, "InUpdateDataTask", 3072, nullptr, 3, nullptr);
    xTaskCreate(OutUpdateDataTask, "OutUpdateDataTask", 3072, nullptr, 3, nullptr);
    xTaskCreate(InCredDataTask, "InCredDataTask", 3072, nullptr, 3, nullptr);
    xTaskCreate(OutCredDataTask, "OutCredDataTask", 3072, nullptr, 3, nullptr);
}

