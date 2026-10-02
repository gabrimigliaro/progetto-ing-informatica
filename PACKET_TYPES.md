# Tipi di pacchetti

| Tipo | Evento | Inviante | Descrizione |
|:----:|--------|----------|-------------|
| `0`  | Nuovo orologio nella rete   | Orologio | Sezione [`1.1 - Orologio`](./PROTOCOLS.md#11-nuovo-orologio-nella-rete)
| `1`  | Risposta a pacchetto `0`    | ESP32 | Sezione [`1.1 - ESP32`](./PROTOCOLS.md#11-nuovo-orologio-nella-rete)
| `10` | Invio periodico dei dati    | Orologio | Sezione [`1.2`](./PROTOCOLS.md#12-invio-periodico-dei-dati)
| `11` | Risposta emergenza risolta  | ESP32 | Sezione [`1.2.1 / 1.2.2`](./PROTOCOLS.md#12-invio-periodico-dei-dati)

| Tipi | Identificativo |
|:----:|----------------|
| Da `0` a `9`   | Eventi sulla rete
| Da `10` a `19` | Invio dati pazienti