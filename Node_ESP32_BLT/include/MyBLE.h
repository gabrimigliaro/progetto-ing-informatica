#pragma once

#include <Arduino.h>
#include <NimBLEDevice.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include "data.h"
#include "Encrypt.h"

class BleBroadcaster {
public:
    bool begin(const char* deviceName = "Node");
    void end();

    bool send(const void*, size_t);
    void stopSend();

private:

    class ScanCb : public NimBLEScanCallbacks {
        void onResult(const NimBLEAdvertisedDevice* d) override;
    };

    static void taskEntry(void* arg);

    ScanCb       _scanCb;
    TaskHandle_t _task = nullptr;
    volatile bool _stop = false;
};

bool send(const void* body, size_t bodyLen);
bool startBleWithRetry(int tries);