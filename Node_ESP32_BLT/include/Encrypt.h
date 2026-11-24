#pragma once
#include <Arduino.h>
#include "mbedtls/aes.h"
#include "esp_random.h"
#include <cstdint>
#include <cstddef>
#include <cstring>
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include <algorithm>
#include "data.h"

constexpr size_t BLOCK_LEN = 16;

bool Encrypt(const uint8_t *payload, size_t len, uint8_t *out_packet);
bool Decrypt(const uint8_t *encrypted_packet, uint8_t* decryptedOutput);
bool ParsePacket(const uint8_t *payload, int rssi);