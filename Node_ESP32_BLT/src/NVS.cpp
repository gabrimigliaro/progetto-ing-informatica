#include "NVS.h"
#include "data.h"
#include "Log.h"

uint8_t key[32] = {0};
std::string url;
NVSConfig nvs;

bool NVSConfig::begin(bool readOnly) {
  return _prefs.begin("space", readOnly);
}

void NVSConfig::end() {
  _prefs.end();
}

bool NVSConfig::getUrl() {
  url = _prefs.getString("url", "").c_str();
  return !url.empty();
}

bool NVSConfig::getKey() {
  if (_prefs.getBytesLength("key") != sizeof(key)) {
    memset(key, 0, sizeof(key));
    return false;
  }
  return _prefs.getBytes("key", key, sizeof(key)) == sizeof(key);
}

bool NVSConfig::setUrl(const std::string& v) {
  url = v;
  return _prefs.putString("url", v.c_str()) == v.size();
}

bool NVSConfig::setKey(const uint8_t* k) {
  memcpy(key, k, sizeof(key));
  return _prefs.putBytes("key", k, sizeof(key)) == sizeof(key);
}

bool NVSConfig::getValidUIDs() {
  size_t len = _prefs.getBytesLength("validUIDs");
  if (len != sizeof(validUID)) {
    memset(validUID, 0, sizeof(validUID));
    return false;
  }
  return _prefs.getBytes("validUIDs", validUID, sizeof(validUID)) == sizeof(validUID);
}

bool NVSConfig::setValidUID(uint8_t index, bool value) {
  validUID[index] = value;

  if (!begin(false)) {
    Log::stampaAllarme("NVS: impossibile aprire il namespace");
    return false;
  }
  bool ok = _prefs.putBytes("validUIDs", validUID, sizeof(validUID)) == sizeof(validUID);
  end();

  if (!ok) Log::stampaAllarme("NVS: salvataggio validUIDs fallito");
  return ok;
}

void NVSBegin() {
  if (!nvs.begin(false)) {
    Log::stampaAllarme("NVS: namespace non apribile");
    return;
  }
  if (!nvs.getKey()) Log::stampaAllarme("NVS: KEY assente");
  if (!nvs.getUrl()) Log::stampaAllarme("NVS: URL assente");
  if (!nvs.getValidUIDs()) Log::stampaAllarme("NVS: validUIDs non presenti o resettati");
  nvs.end();
}