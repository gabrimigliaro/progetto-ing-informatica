#pragma once
#include <string>
#include <cstdint>
#include <cstddef>
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

extern QueueHandle_t InQueue;
extern QueueHandle_t OutQueue;
extern QueueHandle_t InQueueLogin;
extern QueueHandle_t OutQueueLogin;

constexpr char AcceptName[] = "Watch";
constexpr size_t AcceptNameLen = sizeof(AcceptName) - 1;
constexpr TickType_t ticksToWait = 0;
constexpr size_t MaxAdvData = 31 - 4 - (2 + AcceptNameLen);


struct __attribute__((packed)) InData {
    uint8_t UID;
    uint8_t bpm;
    uint8_t battery;
    uint8_t steps;
    uint8_t emergency;
    uint8_t fall;
    int8_t  rssi;
};

struct __attribute__((packed)) OutData {
    uint8_t UID;
};

struct __attribute__((packed)) InDataLogin {
    uint8_t MAC[6];
};

struct __attribute__((packed)) OutDataLogin
{
    uint8_t MAC[6];
    uint8_t UID;
};