#include "Encrypt.h"

void Encrypt (const uint8_t *payload, size_t payload_len, uint8_t *out_packet) {
    esp_fill_random(out_packet, 16); 

    uint8_t iv_copy[16];
    memcpy(iv_copy, out_packet, 16);

    mbedtls_aes_context aes;
    mbedtls_aes_init(&aes);
    mbedtls_aes_setkey_enc(&aes, key, 256);

    size_t nc_off = 0;
    unsigned char stream_block[16] = {0};

    mbedtls_aes_crypt_ctr(&aes, payload_len, &nc_off, iv_copy, stream_block, payload, out_packet + 16);

    mbedtls_aes_free(&aes);
}

void Decrypt(const uint8_t *encrypted_packet, size_t total_len, uint8_t *out_payload) {
    uint8_t iv[16];
    memcpy(iv, encrypted_packet, 16);
    
    size_t payload_len = total_len - 16;

    mbedtls_aes_context aes;
    mbedtls_aes_init(&aes);
    mbedtls_aes_setkey_enc(&aes, key, 256);

    size_t nc_off = 0;
    unsigned char stream_block[16] = {0};

    mbedtls_aes_crypt_ctr(&aes, payload_len, &nc_off, iv, stream_block, encrypted_packet + 16, out_payload);

    mbedtls_aes_free(&aes);
}

void ParsePacket(const uint8_t *payload) {
    bpm = payload[0];
    fall = (payload[1] != 0);
    emergency = (payload[2] != 0);
}