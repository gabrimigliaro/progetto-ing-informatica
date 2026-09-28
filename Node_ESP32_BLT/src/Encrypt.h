#pragma once
#include <Arduino.h>
#include "mbedtls/aes.h"
#include "esp_random.h"
#include <cstdint>
#include <cstddef>

extern const unsigned char key[32];
extern uint8_t bpm;
extern bool fall;
extern bool emergency;

void Encrypt (const uint8_t *payload, size_t payload_len, uint8_t *out_packet);
void Decrypt(const uint8_t *encrypted_packet, size_t total_len, uint8_t *out_payload);
void ParsePacket(const uint8_t *payload);