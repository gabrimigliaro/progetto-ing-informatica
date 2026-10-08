#include "MyBLE.h"
#include <vector>

static constexpr uint16_t CompanyID  = 0xFFFF;
static constexpr uint16_t ADVMS      = 200;
static constexpr uint16_t SCAN_INT_MS = 160;
static constexpr uint16_t SCAN_WIN_MS = 160;

static uint8_t vet[50][6];
static int vetCount = 0;
static int next  = 0;

bool SearchDuplicate(const uint8_t* data, size_t len) {
    for (int i = 0; i < vetCount; i++) {
        if (memcmp(vet[i], data, 6) == 0) 
        return true;
    }
    memcpy(vet[next], data, 6);
    next = (next + 1) % 50;
    if (vetCount < 50) vetCount++;
    return false;
}

 void BleBroadcaster::ScanCb::onResult(const NimBLEAdvertisedDevice* d) {
    std::string md = d->getManufacturerData();

    if (md.size() != 2 + BLOCK_LEN) return;

    if ((uint8_t)md[0] != (CompanyID & 0xFF) || (uint8_t)md[1] != (CompanyID >> 8)) return;

    if (d->getName() != AcceptName) return;

    if (SearchDuplicate((const uint8_t*)md.data() + 2, md.size() - 2) == 1) return;

    Decrypt((const uint8_t*)md.data() + 2, md.size() - 2, d->getRSSI());
}

bool BleBroadcaster::begin(const char* deviceName) {
    if (_task) return true;

    if (!NimBLEDevice::init(deviceName)) {
        NimBLEDevice::deinit(true);
        return false;
    }

    NimBLEAdvertising* adv = NimBLEDevice::getAdvertising();
    adv->setConnectableMode(BLE_GAP_CONN_MODE_NON);
    adv->setMinInterval((ADVMS * 8) / 5);
    adv->setMaxInterval((ADVMS * 8) / 5);

    NimBLEScan* scan = NimBLEDevice::getScan();
    scan->setScanCallbacks(&_scanCb, true);
    scan->setActiveScan(false);
    scan->setInterval(SCAN_INT_MS);
    scan->setWindow(SCAN_WIN_MS);
    scan->setDuplicateFilter(0);
    scan->setMaxResults(0);
    if (!scan->start(0, false, true)) {
        NimBLEDevice::deinit(true);
        return false;
    }

    _stop = false;
    if (xTaskCreatePinnedToCore(taskEntry, "ble_bcast", 8192, this, 2, &_task, 1) != pdPASS) {
        scan->stop();
        NimBLEDevice::deinit(true);
        return false;
    }
    return true;
}



void BleBroadcaster::end() {
    if (!_task) return;
    _stop = true;
    while (_task) vTaskDelay(pdMS_TO_TICKS(10));
    NimBLEDevice::getScan()->stop();
    NimBLEDevice::getAdvertising()->stop();
    NimBLEDevice::deinit(true);
}

bool BleBroadcaster::send(const uint8_t* data, size_t len) {
    if (len > MAXPAYLOAD) return false;

    std::vector<uint8_t> md;
    md.reserve(2 + len);
    md.push_back(CompanyID & 0xFF);
    md.push_back(CompanyID >> 8);
    md.insert(md.end(), data, data + len);

    NimBLEAdvertisementData ad;
    ad.setName(AcceptName);
    ad.setManufacturerData(md);

    NimBLEAdvertising* adv = NimBLEDevice::getAdvertising();
    adv->stop();
    adv->setAdvertisementData(ad);
    return adv->start(0);
}

void BleBroadcaster::stopSend() {
    NimBLEDevice::getAdvertising()->stop();
}

void BleBroadcaster::taskEntry(void* arg) {
    auto* self = static_cast<BleBroadcaster*>(arg);
    while (!self->_stop) {
    NimBLEScan* scan = NimBLEDevice::getScan();
    if (!scan->isScanning()) scan->start(0, false, true);
    vTaskDelay(pdMS_TO_TICKS(1000));
    }
    self->_task = nullptr;
    vTaskDelete(nullptr);
}