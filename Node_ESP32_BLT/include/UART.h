#pragma once
#include <Arduino.h>
#include "freertos/FreeRTOS.h"
#include "data.h"
#include "freertos/semphr.h"


#define UART_RX_PIN         16
#define UART_TX_PIN         17
#define UART_BAUD           115200
#define UART_MAX_PAYLOAD    200
#define UART_RETRIES        3
#define UART_ACK_TIMEOUT_MS 100

void initUART();

bool sendUART(const void* data, size_t len);
