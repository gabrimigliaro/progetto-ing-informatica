#include "UART.h"
#include "Log.h"

#define START_BYTE  0xAA
#define ACK_BYTE    0x06
#define NACK_BYTE   0x15

static SemaphoreHandle_t UARTMutex = NULL;

static volatile uint8_t ackState = 0;   // 0 = niente, 1 = ACK, 2 = NACK

static uint8_t crc8(const uint8_t* buf, size_t len) {
  uint8_t crc = 0;
  while (len--) {
    crc ^= *buf++;
    for (int i = 0; i < 8; i++)
      crc = (crc & 0x80) ? (crc << 1) ^ 0x07 : (crc << 1);
  }
  return crc;
}

bool sendUART(const void* data, size_t len) {
  if (len == 0 || len > UART_MAX_PAYLOAD) {
    return false;
  }

  if (xSemaphoreTakeRecursive(UARTMutex, portMAX_DELAY) != pdTRUE) {
    return false;
  }

  uint8_t frame[UART_MAX_PAYLOAD + 3];
  frame[0] = START_BYTE;
  frame[1] = (uint8_t)len;
  memcpy(&frame[2], data, len);
  frame[2 + len] = crc8(&frame[1], len + 1);

  bool success = false;

  for (int tentativo = 0; tentativo < UART_RETRIES; tentativo++) {
    ackState = 0;
    Serial2.write(frame, len + 3);

    uint32_t t0 = millis();
    while (millis() - t0 < UART_ACK_TIMEOUT_MS) {
      if (ackState == 1) {
        success = true;
        break;
      }
      if (ackState == 2) {
        break;
      }
      vTaskDelay(pdMS_TO_TICKS(1));
    }

    if (success) {
      break;
    }
  }

  xSemaphoreGiveRecursive(UARTMutex);
  return success;
}

static void manageQueue(const uint8_t* p, size_t len) {
  if (len == sizeof(InData) && p[0] == 10) {
    InData rx;
    memcpy(&rx, p, sizeof(rx));
    Log::stampaInfo("UART RX: pacchetto 10");
    xQueueSend(InQueue, &rx, ticksToWait);
  } else if (len == sizeof(InDataLogin) && p[0] == 0) {
    InDataLogin rxLogin;
    memcpy(&rxLogin, p, sizeof(rxLogin));
    Log::stampaInfo("UART RX: pacchetto 0");
    xQueueSend(InQueueLogin, &rxLogin, ticksToWait);
  } else if (len == sizeof(InUpdateData) && p[0] == 2) {
    InUpdateData rxUpdate;
    memcpy(&rxUpdate, p, sizeof(rxUpdate));
    Log::stampaInfo("UART RX: pacchetto 2");
    xQueueSend(InQueueUpdate, &rxUpdate, ticksToWait);
  } 
  else if (len == sizeof(InDataCred) && p[0] == 4) {
    InDataCred rxUpdate;
    memcpy(&rxUpdate, p, sizeof(rxUpdate));
    Log::stampaInfo("UART RX: pacchetto 4");
    xQueueSend(InQueueCred, &rxUpdate, ticksToWait);
  } else {
    Log::stampaInfo("UART RX: pacchetto di lunghezza %u non gestito", len);
  }
}

static void rxTask(void* param) {
  enum { ATTESA_START, LEGGI_LEN, LEGGI_DATI, LEGGI_CRC } stato = ATTESA_START;
  uint8_t  payload[UART_MAX_PAYLOAD];
  uint8_t  len = 0, idx = 0;
  uint32_t ultimoByte = 0;

  for (;;) {
    if (stato != ATTESA_START && millis() - ultimoByte > 50) stato = ATTESA_START;

    if (!Serial2.available()) {
      vTaskDelay(1);
      continue;
    }

    uint8_t b = Serial2.read();
    ultimoByte = millis();

    switch (stato) {
      case ATTESA_START:
        if (b == START_BYTE)     stato = LEGGI_LEN;
        else if (b == ACK_BYTE)  ackState = 1;
        else if (b == NACK_BYTE) ackState = 2;
        break;

      case LEGGI_LEN:
        len = b;
        idx = 0;
        if (len == 0 || len > UART_MAX_PAYLOAD) stato = ATTESA_START;
        else stato = LEGGI_DATI;
        break;

      case LEGGI_DATI:
        payload[idx++] = b;
        if (idx == len) stato = LEGGI_CRC;
        break;

      case LEGGI_CRC: {
        uint8_t tmp[UART_MAX_PAYLOAD + 1];
        tmp[0] = len;
        memcpy(&tmp[1], payload, len);

        if (crc8(tmp, len + 1) == b) {
          Serial2.write((uint8_t)ACK_BYTE);
          manageQueue(payload, len);
        } else {
          Serial2.write((uint8_t)NACK_BYTE);
          Log::stampaInfo("UART: pacchetto con CRC errato, scartato");
        }
        stato = ATTESA_START;
        break;
      }
    }
  }
}

void initUART() {
  UARTMutex = xSemaphoreCreateRecursiveMutex();
  Serial2.begin(UART_BAUD, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);
  xTaskCreate(rxTask, "uartRx", 4096, NULL, 2, NULL);
}
