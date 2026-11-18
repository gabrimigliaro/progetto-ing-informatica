# Tipi di pacchetti

## BLE

| Tipo | Evento | Inviante | Descrizione |
|:----:|--------|----------|-------------|
| `0`  | Nuovo orologio nella rete           | Orologio | Sezione [`1.1 - Orologio`](./PROTOCOLS.md#11-nuovo-orologio-nella-rete)
| `1`  | Risposta a pacchetto `0`            | ESP32 | Sezione [`1.1 - ESP32`](./PROTOCOLS.md#11-nuovo-orologio-nella-rete)
| `2`  | Richiesta presenza aggiornamento    | Orologio | Sezione [`1.3.1`](./PROTOCOLS.md#13-aggiornamento-da-remoto)
| `3`  | Risposta al pacchetto `2`           | ESP32 | Sezione [`1.3.2`](./PROTOCOLS.md#13-aggiornamento-da-remoto)
| `4`  | Richiesta credenziali Wi-Fi         | Orologio | Sezione [`1.3.3`](./PROTOCOLS.md#13-aggiornamento-da-remoto)
| `5`  | Risposta al pacchetto `4` - SSID    | ESP32 | Sezione [`1.3.4`](./PROTOCOLS.md#13-aggiornamento-da-remoto)
| `6`  | Risposta al pacchetto `4` - PSW     | ESP32 | Sezione [`1.3.4`](./PROTOCOLS.md#13-aggiornamento-da-remoto)
| `10` | Invio periodico dei dati            | Orologio | Sezione [`1.2`](./PROTOCOLS.md#12-invio-periodico-dei-dati)
| `11` | Risposta emergenza risolta          | ESP32 | Sezione [`1.2.1 / 1.2.2`](./PROTOCOLS.md#12-invio-periodico-dei-dati)

| Tipi | Identificativo |
|:----:|----------------|
| Da `0` a `9`   | Eventi sulla rete
| Da `10` a `19` | Invio dati pazienti

## WebSocket
| Tipo | Evento | Inviante | Descrizione |
|:----:|--------|----------|-------------|
| `0`                 | Nuovo orologio nella rete           | SCI | Sezione [`3.1`](./PROTOCOLS.md#31-nuovo-orologio-sulla-rete))
| `NEW_DEVICE`        | Risposta a pacchetto `0`            | Server | Sezione [`3.1.1`](./PROTOCOLS.md#31-nuovo-orologio-sulla-rete))
| `DEVICE_CONNECTED`  | Risposta a pacchetto `0`            | Server | Sezione [`3.1.2`](./PROTOCOLS.md#31-nuovo-orologio-sulla-rete))
| `10`                | Invio periodico dei dati            | SCI | Sezione [`3.2`](./PROTOCOLS.md#32-invio-periodico-dei-dati)
| `DEVICE_UPDATE`     | Risposta al pacchetto `10`          | Server | Sezione [`3.2.1`](./PROTOCOLS.md#32-invio-periodico-dei-dati)
| `NEW_EMERGENCY`     | Risposta al pacchetto `10`          | Server | Sezione [`3.2.2`](./PROTOCOLS.md#32-invio-periodico-dei-dati)