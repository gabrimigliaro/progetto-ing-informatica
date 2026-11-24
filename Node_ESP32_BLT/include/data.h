#pragma once
#include <string>
#include <cstdint>
#include <cstddef>
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "NVS.h"  

extern QueueHandle_t InQueue;
extern QueueHandle_t OutQueue;
extern QueueHandle_t InQueueLogin;
extern QueueHandle_t OutQueueLogin;
extern QueueHandle_t InQueueUpdate;
extern QueueHandle_t OutQueueUpdate;
extern QueueHandle_t UIDQueue;
extern QueueHandle_t InQueueCred;
extern QueueHandle_t OutQueueSSID;
extern QueueHandle_t OutQueuePSW;

extern Preferences preferences;

extern bool validUID[256];

extern NVSConfig nvs;
extern uint8_t key[32];
extern std::string url;
constexpr char AcceptName[] = "WA";
constexpr char NodeName[] = "ESP_REPLY";
constexpr uint16_t ReplyServiceUUID = 0xFEE0;
constexpr size_t AcceptNameLen = sizeof(AcceptName) - 1;
constexpr TickType_t ticksToWait = 0;
constexpr size_t MaxAdvData = 31 - 4 - (2 + AcceptNameLen);


struct __attribute__((packed)) InData {
    uint8_t PID;
    uint8_t UID;
    uint8_t bpm;
    uint8_t battery;
    uint16_t steps;
    uint8_t emergency;
    uint8_t fall;
    int8_t  rssi;
};

struct __attribute__((packed)) OutData {
    uint8_t PID;
    uint8_t UID;
};

struct __attribute__((packed)) InDataLogin {
    uint8_t PID;
    uint8_t MAC[6];
};

struct __attribute__((packed)) OutDataLogin
{
    uint8_t PID;
    uint8_t MAC[6];
    uint8_t UID;
};

struct __attribute__((packed)) InUpdateData {
    uint8_t PID;
    uint8_t UID;
};

struct __attribute__((packed)) OutUpdateData {
    uint8_t PID;
    uint8_t UID;
    uint8_t updateAvailable;
};

struct __attribute__((packed)) InDataCred {
    uint8_t PID;
    uint8_t UID;  
};

struct __attribute__((packed)) OutDataSSID {
    uint8_t PID;
    uint8_t UID;
    char ssid[12];
};

struct __attribute__((packed)) OutDataPSW {
    uint8_t PID;
    uint8_t UID;
    char pass[12];
};