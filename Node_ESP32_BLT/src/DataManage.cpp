#include "DataManage.h"
#include "freertos/semphr.h"

static InData lastData;
static InDataLogin lastDataLogin;
static bool hasData = false;
static bool hasDataLogin = false;  
static SemaphoreHandle_t IndataMutex = NULL;
static SemaphoreHandle_t InLoginDataMutex = NULL;


static void InDataTask(void *arg) {
    InData rx;
    for (;;) {
        if (xQueueReceive(InQueue, &rx, pdMS_TO_TICKS(100)) == pdTRUE) {
            xSemaphoreTake(IndataMutex, portMAX_DELAY);
            lastData = rx;
            hasData = true;
            xSemaphoreGive(IndataMutex);


            //successivamente per TCP verso SCI
            Serial.printf("UID:%u BPM:%u BAT:%u STEPS:%u RSSI:%d fall:%u emerg:%u\n",
              rx.UID, rx.bpm, rx.battery, rx.steps, rx.rssi, rx.fall, rx.emergency);
            
        }
        vTaskDelay(pdMS_TO_TICKS(100)); 
    }
}

static void InLoginDataTask(void *arg) {
    InDataLogin rxLogin;
    for (;;) {
        if (xQueueReceive(InQueueLogin, &rxLogin, pdMS_TO_TICKS(100)) == pdTRUE) {
            xSemaphoreTake(InLoginDataMutex, portMAX_DELAY);
            lastDataLogin = rxLogin;
            hasDataLogin = true;
            xSemaphoreGive(InLoginDataMutex);


            //successivamente per TCP verso SCI
            Serial.printf("MAC: %02X:%02X:%02X:%02X:%02X:%02X\n",
              rxLogin.MAC[0], rxLogin.MAC[1], rxLogin.MAC[2], rxLogin.MAC[3], rxLogin.MAC[4], rxLogin.MAC[5]);
            
        }
        vTaskDelay(pdMS_TO_TICKS(100)); 
    }
}

void DataStart() {
    IndataMutex = xSemaphoreCreateMutex();
    InLoginDataMutex = xSemaphoreCreateMutex();
    xTaskCreate(InDataTask, "InDataTask", 3072, nullptr, 3, nullptr);
    xTaskCreate(InLoginDataTask, "InLoginDataTask", 3072, nullptr, 3, nullptr);
}

