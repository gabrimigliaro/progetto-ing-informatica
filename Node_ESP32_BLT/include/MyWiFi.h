#pragma once
#include <Arduino.h>
#include <WiFi.h>
#include <Preferences.h>
#include <ESPAsyncWebServer.h>
#include <DNSServer.h>
#include "freertos/FreeRTOS.h"
#include "data.h"

void WiFiInit();
void WifiUpdate();
void WifiStart();