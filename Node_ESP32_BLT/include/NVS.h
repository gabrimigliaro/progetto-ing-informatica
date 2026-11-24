#pragma once
#include <Arduino.h>
#include <Preferences.h>
#include <string>

class NVSConfig {
public:
    bool begin(bool readOnly = false);
    void end();

    bool getUrl(); 
    bool getKey();

    bool setUrl(const std::string& v);
    bool setKey(const uint8_t* k);

    bool getValidUIDs();
    bool setValidUID(uint8_t index, bool value);

private:
    Preferences _prefs;
};

void NVSBegin();

