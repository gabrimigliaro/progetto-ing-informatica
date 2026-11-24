#include "MyBLE.h"
#include <vector>
#include <Log.h>

static constexpr uint16_t ADVMS      = 50;
static constexpr uint16_t SCAN_INT_MS = 100;
static constexpr uint16_t SCAN_WIN_MS = 100;

static SemaphoreHandle_t BLEMutex = NULL;

static uint8_t vet[50][6];
static int vetCount = 0;
static int next  = 0;

extern BleBroadcaster ble;

bool SearchDuplicate(const uint8_t* data, size_t len) {
    if (len <   6) return false;

    const uint8_t* tail = data + len - 6;

    for (int i = 0; i < vetCount; i++) {
        if (memcmp(vet[i], tail, 6) == 0) {
            //Log::stampaInfo("BLE DUPLICATE: pacchetto doppio trovato");
            return true;
        }
    }

    memcpy(vet[next], tail, 6);
    next = (next + 1) % 50;
    if (vetCount < 50) vetCount++;
    //Log::stampaInfo("BLE DUPLICATE: pacchetto nuovo trovato");
    return false;
}


void BleBroadcaster::ScanCb::onResult(const NimBLEAdvertisedDevice* d) {
    std::string serviceData;

    if (d->haveServiceData()) {
        serviceData = d->getServiceData();
    } else return;

    bool isOurDevice = false;
    if (d->getServiceDataUUID().equals(BLEUUID("FFE0"))) {
        isOurDevice = true;

        if (SearchDuplicate((const uint8_t*)serviceData.data() + 2, serviceData.size() - 2) == 1) return;
        Log::stampaInfo("BLE RX: ricevuto pacchetto ");
    } else if (d->haveName() && d->getName() == "WA") {
        isOurDevice = true;

        if (SearchDuplicate((const uint8_t*)serviceData.data() + 2, serviceData.size() - 2) == 1) return;
        Log::stampaInfo("BLE RX: ricevuto pacchetto ");
    }

    if (isOurDevice) {

        const uint8_t* encryptedBytes = (const uint8_t*)serviceData.data();
        uint8_t decrypted[16] = {0};

        if (Decrypt(encryptedBytes, decrypted)) {
            if(ParsePacket(decrypted, (int) d->getRSSI()) != 1) {
                Log::stampaWarning("PARSING: errore");
            }
        }
    }
}

bool BleBroadcaster::begin(const char* deviceName) {
    if (!BLEMutex) BLEMutex = xSemaphoreCreateMutex();
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

bool BleBroadcaster::send(const void* body, size_t bodyLen) {
    if (bodyLen + 1 > BLOCK_LEN) return false;

    uint8_t plain[BLOCK_LEN];
    memcpy(plain, body, bodyLen);

    uint8_t cipher[BLOCK_LEN];
    if (!Encrypt(plain, bodyLen, cipher)) return false;

    xSemaphoreTake(BLEMutex, portMAX_DELAY);
    NimBLEAdvertisementData ad;
    ad.setServiceData(NimBLEUUID(ReplyServiceUUID), std::vector<uint8_t>(cipher, cipher + BLOCK_LEN));
    
    ad.setName(NodeName, true); 

    NimBLEAdvertising* adv = NimBLEDevice::getAdvertising();
    adv->stop();
    adv->setAdvertisementData(ad);
    bool ok = adv->start(5000);
    if (ok) vTaskDelay(pdMS_TO_TICKS(1500));
    xSemaphoreGive(BLEMutex);
    if(!ok) Log::stampaAllarme("BLE TX: errore");
    return ok;
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

bool startBleWithRetry(int tries) {
    for (int i = 1; i <= tries; i++) {
        if (ble.begin("Node")) return true;
        Log::stampaAllarme("BLE INIT: tentativo %d/%d fallito", i, tries);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
    return false;
}