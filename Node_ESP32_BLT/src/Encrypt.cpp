#include "Encrypt.h"

bool Encrypt(const uint8_t *payload, size_t len, uint8_t *out_packet) {
    if (len == 0 || len > BLOCK_LEN) return false;

    uint8_t block[BLOCK_LEN];
    esp_fill_random(block, BLOCK_LEN);
    memcpy(block, payload, len);

    mbedtls_aes_context aes;
    mbedtls_aes_init(&aes);
    if (mbedtls_aes_setkey_enc(&aes, key, 256) != 0) {
        Serial.println("Errore AES");
        mbedtls_aes_free(&aes);
        return false;
    }

    int ret = mbedtls_aes_crypt_ecb(&aes, MBEDTLS_AES_ENCRYPT, block, out_packet);
    mbedtls_aes_free(&aes);
    return ret == 0;
}

bool Decrypt(const uint8_t *encrypted_packet, size_t len, int8_t rssi) {
    if (len != BLOCK_LEN) return false;

    uint8_t plain[BLOCK_LEN];
    mbedtls_aes_context aes;
    mbedtls_aes_init(&aes);
    if (mbedtls_aes_setkey_dec(&aes, key, 256) != 0) {
        mbedtls_aes_free(&aes);
        return false;
    }

    int ret = mbedtls_aes_crypt_ecb(&aes, MBEDTLS_AES_DECRYPT, encrypted_packet, plain);
    mbedtls_aes_free(&aes);
    if (ret != 0) return false;

    return ParsePacket(plain, BLOCK_LEN, rssi);
}

bool ParsePacket(const uint8_t *p, size_t len, int8_t rssi) {
    if (len < 1) return false;
    const uint8_t *body = p + 1;
    size_t blen = len - 1;

    if (p[0] == 0) {
        if (blen < sizeof(InDataLogin)) return false;
        InDataLogin tmp;
        memcpy(&tmp, body, sizeof(tmp));
        return xQueueSend(InQueueLogin, &tmp, ticksToWait) == pdTRUE;
    }

    else if (p[0] == 10) {
        if (blen < sizeof(InData)) return false;
        InData tmp;
        memcpy(&tmp, body, sizeof(tmp));
        if (tmp.battery > 100 || tmp.fall > 1 || tmp.emergency > 1 || tmp.bpm > 255 || rssi < -110 || rssi > 10) {
            Serial.println("Pacchetto scartato per dati non validi");
            return false;
        }
        tmp.rssi = rssi;
        return xQueueSend(InQueue, &tmp, ticksToWait) == pdTRUE;
    }
    return false;
}