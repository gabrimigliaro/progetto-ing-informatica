#include "DataManage.h"
#include "freertos/semphr.h"
#include "Log.h"
#include "TCP.h"

static void InDataTask(void *arg) {
    InData rx;
    for (;;) {
        if (xQueueReceive(InQueue, &rx, portMAX_DELAY) != pdTRUE) continue;

        Log::stampaNormale("DATA: PID:%u UID:%u BPM:%u BAT:%u STEPS:%u RSSI:%d emerg:%u fall:%u\n",
            rx.PID, rx.UID, rx.bpm, rx.battery, rx.steps, rx.rssi, rx.emergency, rx.fall);
        tcpSendData(rx);
    }
}


static void InLoginDataTask(void *arg) {
    InDataLogin rxLogin;
    for (;;) {
        if (xQueueReceive(InQueueLogin, &rxLogin, pdMS_TO_TICKS(100)) == pdTRUE) {
            Log::stampaInfo("UART RX: pacchetto login");
            tcpSendLogin(rxLogin);
        }
        vTaskDelay(pdMS_TO_TICKS(100)); 
    }
}

static void OutDataTask(void *arg) {
    OutData rx;
    for (;;) {
        if (xQueueReceive(OutQueue, &rx, portMAX_DELAY) != pdTRUE) continue;
        
        Log::stampaNormale("TCP RX: pacchetto 10");
        Log::stampaNormale("DATA: PID:%u UID:%u\n", rx.PID, rx.UID);
        sendUART(&rx, sizeof(rx));
    }
}



static void OutLoginDataTask(void *arg) {
    OutDataLogin rxLogin;
    for (;;) {
        if (xQueueReceive(OutQueueLogin, &rxLogin, pdMS_TO_TICKS(100)) == pdTRUE) {

            Log::stampaInfo("TCP RX: pacchetto login");
            Log::stampaNormale("DATA: PID:%u MAC:%02X:%02X:%02X:%02X:%02X:%02X UID:%u\n",
                rxLogin.PID, rxLogin.MAC[0], rxLogin.MAC[1], rxLogin.MAC[2],
                rxLogin.MAC[3], rxLogin.MAC[4], rxLogin.MAC[5], rxLogin.UID); 
            sendUART(&rxLogin, sizeof(rxLogin));
        }
        vTaskDelay(pdMS_TO_TICKS(100)); 
    }
}

static void InUpdateDataTask(void *arg) {
    InUpdateData rxUpdate;
    for (;;) {
        if (xQueueReceive(InQueueUpdate, &rxUpdate, pdMS_TO_TICKS(100)) == pdTRUE) {
            Log::stampaInfo("UART RX: pacchetto update");
            tcpSendUpdate(rxUpdate);
        }
        vTaskDelay(pdMS_TO_TICKS(100)); 
    }
}

static void OutUpdateDataTask(void *arg) {
    OutUpdateData rxUpdate;
    for (;;) {
        if (xQueueReceive(OutQueueUpdate, &rxUpdate, pdMS_TO_TICKS(100)) == pdTRUE) {
            Log::stampaInfo("TCP RX: pacchetto update");
            Log::stampaNormale("DATA: PID:%u UID:%u updateAvailable:%d\n",
                rxUpdate.PID, rxUpdate.UID, rxUpdate.updateAvailable);
            sendUART(&rxUpdate, sizeof(rxUpdate));
        }
        vTaskDelay(pdMS_TO_TICKS(100)); 
    }
}

static void InCredDataTask(void *arg) {
    InDataCred rx;
    OutDataSSID rxSSID;
    OutDataPSW  rxPSW;

    for (;;) {
        if (xQueueReceive(InQueueCred, &rx, pdMS_TO_TICKS(100)) == pdTRUE) {
            Log::stampaInfo("UART TX: invio credenziali SSID e PSW (pacchetti 5 e 6)");

            memset(&rxSSID, 0, sizeof(rxSSID));
            memset(&rxPSW, 0, sizeof(rxPSW));

            rxSSID.PID = 5;
            rxSSID.UID = rx.UID;

            rxPSW.PID = 6;
            rxPSW.UID = rx.UID;

            strncpy(rxSSID.ssid, ssid.c_str(), sizeof(rxSSID.ssid) - 1);
            strncpy(rxPSW.pass, pass.c_str(), sizeof(rxPSW.pass) - 1);

            sendUART(&rxSSID, sizeof(rxSSID));
            sendUART(&rxPSW, sizeof(rxPSW));
        }
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
void DataStart() {
    xTaskCreate(InDataTask, "InDataTask", 3072, nullptr, 3, nullptr);
    xTaskCreate(InLoginDataTask, "InLoginDataTask", 3072, nullptr, 3, nullptr);
    xTaskCreate(InUpdateDataTask, "InUpdateDataTask", 3072, nullptr, 3, nullptr);
    xTaskCreate(OutDataTask, "OutDataTask", 3072, nullptr, 3, nullptr);
    xTaskCreate(OutLoginDataTask, "OutLoginDataTask", 3072, nullptr, 3, nullptr);
    xTaskCreate(OutUpdateDataTask, "OutUpdateDataTask", 3072, nullptr, 3, nullptr);
    xTaskCreate(InCredDataTask, "InCredDataTask", 3072, nullptr, 3, nullptr);
}

