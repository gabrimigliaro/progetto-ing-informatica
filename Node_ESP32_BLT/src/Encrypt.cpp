#include "Encrypt.h"
#include "Log.h"


bool Encrypt(const uint8_t *payload, size_t len, uint8_t *out_packet) {
    if (len == 0 || len > BLOCK_LEN) return false;

    uint8_t block[BLOCK_LEN];
    esp_fill_random(block, BLOCK_LEN);
    memcpy(block, payload, len);

    mbedtls_aes_context aes;
    mbedtls_aes_init(&aes);
    if (mbedtls_aes_setkey_enc(&aes, key, 256) != 0) {
        Log::stampaAllarme("ENCRYPT: Errore AES");
        mbedtls_aes_free(&aes);
        return false;
    }

    int ret = mbedtls_aes_crypt_ecb(&aes, MBEDTLS_AES_ENCRYPT, block, out_packet);
    mbedtls_aes_free(&aes);
    return ret == 0;
}


bool Decrypt(const uint8_t* encryptedInput, uint8_t* decryptedOutput) {
    mbedtls_aes_context aes;
    mbedtls_aes_init(&aes);
    
    if (mbedtls_aes_setkey_dec(&aes, key, 256) != 0) {
        mbedtls_aes_free(&aes);
        return false;
    }
    
    int status = mbedtls_aes_crypt_ecb(&aes, MBEDTLS_AES_DECRYPT, encryptedInput, decryptedOutput);
    mbedtls_aes_free(&aes);
    return (status == 0);
}

bool ParsePacket(const uint8_t *packet, int rssi) {
    const uint8_t *body = packet;
    size_t blen = BLOCK_LEN;

    uint8_t  globalPacketType = packet[0];

    if (globalPacketType == 0) {
        Log::stampaInfo("BLE RX: pacchetto 0");
        if (blen < sizeof(InDataLogin)) return false;
        InDataLogin tmp;
        memcpy(&tmp, body, sizeof(tmp));
        return xQueueSend(InQueueLogin, &tmp, ticksToWait) == pdTRUE;
    }

    else if (globalPacketType == 10) {
        Log::stampaInfo("BLE RX: pacchetto 10");

        if (blen < sizeof(InData)) {
            return false;
        }

        InData tmp;
        memcpy(&tmp, body, sizeof(tmp));
        if (!validUID[tmp.UID]) { Log::stampaWarning("ENCRYPT: UID non valido"); return false; }

        if (tmp.battery > 100 || tmp.fall > 1 || tmp.emergency > 1 || tmp.bpm > 254 || rssi < -110 || rssi > 10) {
            Log::stampaWarning("ENCRYPT: dati errati");
            return false;
        }

        tmp.rssi = rssi;
        return xQueueSend(InQueue, &tmp, ticksToWait) == pdTRUE;
    }
    else if (globalPacketType == 2) {
        Log::stampaInfo("BLE RX: pacchetto 2");

        if (blen < sizeof(InUpdateData)) {
            return false;
        }

        InUpdateData tmp;
        memcpy(&tmp, body, sizeof(tmp));
        if (!validUID[tmp.UID]) { Log::stampaWarning("ENCRYPT: UID non valido"); return false; }

        return xQueueSend(InQueueUpdate, &tmp, ticksToWait) == pdTRUE;
    }

    else if (globalPacketType == 4) {

        if (blen < sizeof(InDataCred)) {
            return false;
        }

        InDataCred tmp;
        memcpy(&tmp, body, sizeof(tmp));

        if (!validUID[tmp.UID]) { Log::stampaWarning("ENCRYPT: UID non valido"); return false; }

        return xQueueSend(InQueueCred, &tmp, ticksToWait) == pdTRUE;
    }

    return false;
}