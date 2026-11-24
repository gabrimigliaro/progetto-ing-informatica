#pragma once
#include <stdint.h>
#include <stdbool.h>
#include "data.h"

void tcpStart(const char* host = nullptr, uint16_t port = 0);

bool tcpSendLogin(const InDataLogin& d);

bool tcpSendData(const InData& d);

bool tcpSendUpdate(const InUpdateData& d);