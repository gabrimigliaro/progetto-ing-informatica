#include "TCP.h"
#include <WiFi.h>
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "data.h"
#include "Log.h"
#include <stdio.h>
#include <string.h>

static uint16_t sciSP = 8000;
extern String apName;

static WiFiClient client;
static SemaphoreHandle_t clientMutex = nullptr;
static bool tcpInitialized = false;

static bool parseByte(const char* token, uint8_t& value) {
    if (!token || *token == '\0' || *token == '-') return false;
    char* end = nullptr;
    const unsigned long parsed = strtoul(token, &end, 10);
    if (*end != '\0' || parsed > UINT8_MAX) return false;
    value = static_cast<uint8_t>(parsed);
    return true;
}

static bool parseMac(const char* token, uint8_t mac[6]) {
    if (!token) return false;
    unsigned int bytes[6];
    char trailing;
    if (sscanf(token, "%x:%x:%x:%x:%x:%x%c",
               &bytes[0], &bytes[1], &bytes[2],
               &bytes[3], &bytes[4], &bytes[5], &trailing) != 6) {
        return false;
    }
    for (size_t i = 0; i < 6; ++i) {
        if (bytes[i] > UINT8_MAX) return false;
        mac[i] = static_cast<uint8_t>(bytes[i]);
    }
    return true;
}

static void manageLogin(char** savePointer) {
    OutDataLogin response{};
    response.PID = 1;

    char* macToken = strtok_r(nullptr, ", \t", savePointer);
    char* uidToken = strtok_r(nullptr, ", \t", savePointer);

    if (parseMac(macToken, response.MAC)) {
        if (!parseByte(uidToken, response.UID)) {
            Log::stampaWarning("TCP RX: UID non valido per PID 1");
            return;
        }
    } else {
        if (!parseByte(macToken, response.MAC[0]) || !parseByte(uidToken, response.MAC[1])) {
            Log::stampaWarning("TCP RX: MAC non valido per PID 1");
            return;
        }
        for (size_t i = 2; i < 6; ++i) {
            if (!parseByte(strtok_r(nullptr, ", \t", savePointer), response.MAC[i])) {
                Log::stampaWarning("TCP RX: MAC incompleto per PID 1");
                return;
            }
        }
        if (!parseByte(strtok_r(nullptr, ", \t", savePointer), response.UID)) {
            Log::stampaWarning("TCP RX: UID non valido per PID 1");
            return;
        }
    }

    if (OutQueueLogin != nullptr) {
        if (xQueueSend(OutQueueLogin, &response, 0) != pdTRUE) {
            Log::stampaWarning("TCP RX: OutQueueLogin piena!");
        }
    }
}

static void manageData(char** savePointer) {
    OutData response{};
    response.PID = 11;

    if (!parseByte(strtok_r(nullptr, ", \t", savePointer), response.UID)) {
        Log::stampaWarning("TCP RX: UID non valido per PID 11");
        return;
    }

    if (OutQueue != nullptr) {
        if (xQueueSend(OutQueue, &response, 0) != pdTRUE) {
            Log::stampaWarning("TCP RX: OutQueue piena!");
        }
    }
}

static void manageUpdate(char** savePointer) {
    OutUpdateData response{};
    response.PID = 3;

    if (!parseByte(strtok_r(nullptr, ", \t", savePointer), response.UID)) {
        Log::stampaWarning("TCP RX: UID non valido per PID 3");
        return;
    }

    uint8_t flag = 0;
    char* tok = strtok_r(nullptr, ", \t", savePointer);
    if (tok && parseByte(tok, flag)) response.updateAvailable = flag;

    if (OutQueueUpdate != nullptr) {
        if (xQueueSend(OutQueueUpdate, &response, 0) != pdTRUE) {
            Log::stampaWarning("TCP RX: OutQueueUpdate piena!");
        }
    }
}


static void manageLine(char* line) {
    char* savePointer = nullptr;
    char* token = strtok_r(line, ", \t", &savePointer);
    if (!token) return;

    if (strcmp(token, apName.c_str()) == 0) {
        token = strtok_r(nullptr, ", \t", &savePointer);
    }

    uint8_t packetType = 0;
    if (!parseByte(token, packetType)) {
        Log::stampaWarning("TCP RX: PID pacchetto non valido");
        return;
    }

    switch (packetType) {
        case 1:
            manageLogin(&savePointer);
            break;

        case 11:
            manageData(&savePointer);
            break;

        case 3:
            manageUpdate(&savePointer);
            break;

        default:
            Log::stampaWarning("TCP RX: PID %u non gestito", packetType);
            break;
    }
}

static bool checkConnection() {
    if (WiFi.status() != WL_CONNECTED) return false;
    if (client.connected()) return true;

    client.stop();
    Log::stampaInfo("TCP: Connessione a %s:%u...", sciIP.c_str(), sciSP);
    if (client.connect(sciIP.c_str(), sciSP, 2000)) {
        Log::stampaInfo("TCP: Connesso con successo");
        return true;
    }

    Log::stampaAllarme("TCP: Connessione non riuscita nel tempo massimo");
    return false;
}

static bool sendBuffer(const char* buffer, size_t length) {
    if (!tcpInitialized || clientMutex == nullptr) return false;

    if (xSemaphoreTake(clientMutex, pdMS_TO_TICKS(1000)) != pdTRUE) {
        Log::stampaWarning("TCP TX: Impossibile acquisire il mutex");
        return false;
    }

    bool success = false;
    if (checkConnection()) {
        if (client.write(reinterpret_cast<const uint8_t*>(buffer), length) == length) {
            success = true;
        } else {
            Log::stampaAllarme("TCP TX: Errore invio socket, chiusura connessione");
            client.stop();
        }
    }

    xSemaphoreGive(clientMutex);
    return success;
}

bool tcpSendLogin(const InDataLogin& d) {
    char buffer[128];
    int len = snprintf(buffer, sizeof(buffer), "%s|t%u,%02X:%02X:%02X:%02X:%02X:%02X\n",
                       apName.c_str(),
                       d.PID,
                       d.MAC[0], d.MAC[1], d.MAC[2],
                       d.MAC[3], d.MAC[4], d.MAC[5]);

    if (len <= 0 || static_cast<size_t>(len) >= sizeof(buffer)) {
        Log::stampaWarning("TCP TX: Errore formattazione Login");
        return false;
    }

    return sendBuffer(buffer, static_cast<size_t>(len));
}

bool tcpSendData(const InData& d) {
    char buffer[128];
    int len = snprintf(buffer, sizeof(buffer), "%s|t%u,%u,%u,%u,%u,%u,%u,%d\n",
                       apName.c_str(),
                       d.PID,
                       d.UID,
                       d.bpm,
                       d.battery,
                       d.steps,
                       d.emergency,
                       d.fall,
                       d.rssi);

    if (len <= 0 || static_cast<size_t>(len) >= sizeof(buffer)) {
        Log::stampaWarning("TCP TX: Errore formattazione Dati");
        return false;
    }

    return sendBuffer(buffer, static_cast<size_t>(len));
}

bool tcpSendUpdate(const InUpdateData& d) {
    char buffer[128];
    int len = snprintf(buffer, sizeof(buffer), "%s|t%u,%u\n",
                       apName.c_str(),
                       d.PID,
                       d.UID);

    if (len <= 0 || static_cast<size_t>(len) >= sizeof(buffer)) {
        Log::stampaWarning("TCP TX: Errore formattazione Update");
        return false;
    }

    return sendBuffer(buffer, static_cast<size_t>(len));
}

static void tcpRxTask(void* arg) {
    char rxBuffer[128];
    size_t rxIndex = 0;

    for (;;) {
        if (WiFi.status() != WL_CONNECTED) {
            vTaskDelay(pdMS_TO_TICKS(1000));
            continue;
        }

        if (xSemaphoreTake(clientMutex, pdMS_TO_TICKS(20)) == pdTRUE) {
            if (client.connected() && client.available() > 0) {
                while (client.available() > 0) {
                    char c = static_cast<char>(client.read());
                    if (c == '\n') {
                        if (rxIndex > 0) {
                            rxBuffer[rxIndex] = '\0';
                            manageLine(rxBuffer);
                        }
                        rxIndex = 0;
                    } else if (c != '\r') {
                        if (rxIndex < sizeof(rxBuffer) - 1) {
                            rxBuffer[rxIndex++] = c;
                        } else {
                            rxIndex = 0;
                            Log::stampaWarning("TCP RX: Buffer riga superato");
                        }
                    }
                }
            }
            xSemaphoreGive(clientMutex);
        }

        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

void tcpStart(const char* host, uint16_t port) {
    if (tcpInitialized) return;

    if (host != nullptr && strlen(host) > 0) {
        sciIP = host;
    }
    if (port > 0) {
        sciSP = port;
    }

    clientMutex = xSemaphoreCreateMutex();
    if (clientMutex == nullptr) {
        Log::stampaAllarme("TCP: Impossibile creare il mutex!");
        return;
    }

    if (xTaskCreate(tcpRxTask, "tcpRxTask", 4096, nullptr, 2, nullptr) != pdPASS) {
        Log::stampaAllarme("TCP: Impossibile avviare task RX!");
        return;
    }

    tcpInitialized = true;
    Log::stampaInfo("TCP: Modulo avviato su %s:%u", sciIP.c_str(), sciSP);
}