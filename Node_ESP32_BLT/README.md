# Node ESP32 BLT

`Node_ESP32_BLT` è il modulo firmware per ESP32 che gestisce la comunicazione Bluetooth Low Energy, BLE, con lo smartwatch, `watch_agent`. Inoltra i dati in entrambe le direzioni verso il nodo Wi-Fi tramite connessione seriale UART.

## Funzionalità principali

- scansione continua BLE non connettibile ad alte prestazioni tramite NimBLE (`NimBLEScan`);

- filtraggio e identificazione dei pacchetti orologio tramite UUID di servizio (`0xFFE0`) o nome del dispositivo (`WA`);

- decifratura e cifratura dei pacchetti tramite mbedTLS con algoritmo AES-256 ECB e chiave a 256 bit;

- rimozione dei pacchetti duplicati mediante cache circolare software degli ultimi payload ricevuti;

- validazione e parsing dei pacchetti di telemetria (BPM, batteria, passi, RSSI, caduta, emergenza);

- gestione delle richieste di pairing/login del dispositivo tramite indirizzo MAC;

- gestione delle richieste di verifica disponibilità aggiornamenti remoti;

- disaccoppiamento e sincronizzazione concorrente delle operazioni tramite code FreeRTOS dedicate;

- comunicazione seriale full-duplex con protocollo a frame delimitato da start byte, lunghezza e checksum CRC-8;

- meccanismo di ritrasmissione UART su errore o timeout con gestione di ACK e NACK;

- trasmissione periodica delle risposte BLE tramite advertisement non connettibile con UUID di servizio `0xFEE0`;

- lettura e persistenza della chiave di cifratura e dei parametri di configurazione su memoria NVS (Non-Volatile Storage);

- sistema di logging strutturato su porta seriale con timestamp in millisecondi e codici colore ANSI;

- riavvio automatico controllato (`esp_restart`) in caso di fallimento critico nell'inizializzazione del controller BLE;

## Struttura del progetto

```text

Node_ESP32_BLT/

# CMakeLists.txt # Build configuration for ESP-IDF

|-- platformio.ini # Configurazione ambiente PlatformIO e librerie

|-- Prova.csv # Tabella delle partizioni della memoria flash (NVS, OTA, SPIFFS)

|-- README.md

|-- sdkconfig.esp32dev # File di configurazione hardware e parametri ESP-IDF

|-- include/

| |-- data.h # Definizioni dei tipi di pacchetto, code e parametri BLE

| |-- DataManage.h # Interfaccia per creare e avviare i task FreeRTOS

| |-- Encrypt.h # Funzioni AES-256 e lettura dei pacchetti

| |-- Log.h # Funzione di logging seriale con timestamp e formattazione ANSI

| | MyBLE.h, gestore NimBLE per scansione continua e broadcast

| | NVS.h # Wrapper for Preferences to store data in NVS memory

| `-- UART.h # Definizioni e API per il protocollo di comunicazione seriale

`-- src/

|-- CMakeLists.txt # File per registrare i componenti sorgente nella build ESP-IDF

|-- DataManage.cpp # Task FreeRTOS that moves data between queues, BLE, and UART

|-- Encrypt.cpp # Implementazione cifratura e decifratura mbedTLS. Include la validazione

|-- MyBLE.cpp # BLE scanner, duplicate filter, and advertiser implementation

|-- NVS.cpp # Lettura delle chiavi di cifratura e parametri da NVS

|-- UART.cpp # State machine for receiving, CRC8 calculation, and sending on Serial2

main.cpp # Entry point app_main, code allocation, and startup of subsystems

```

## Flusso di avvio

All'avvio, la funzione di ingresso `app_main()` in `main.cpp` esegue questa sequenza di avvio.

1. inizializza la parte principale di Arduino (`initArduino`) e la porta seriale di debug principale a 115200 baud.

2. crea il codice FreeRTOS per il routing asincrono dei dati (InQueue, InQueueLogin, OutQueue, OutQueueLogin, OutQueueUpdate, InQueueUpdate);

3. Controlla che le code siano allocate in modo corretto usando `configASSERT`.

4. apre il namespace NVS `space` e carica in memoria la chiave AES-256 e l'URL di configurazione.

5. inizializza lo stack BLE tramite NimBLE. Effettua fino a 5 tentativi. Se fallisce, forza il riavvio del microcontrollore con `esp_restart()`.

6. inizializza l'interfaccia hardware `Serial2` per la comunicazione UART. Avvia il task di ricezione con macchina a stati.

7. Avvia i task FreeRTOS di gestione dati (`DataStart`). Questi task elaborano in parallelo code, trasmissioni seriali e risposte BLE.

## Architettura e code FreeRTOS

La comunicazione tra lo stack BLE e l'interfaccia seriale UART è separata tramite code FreeRTOS. Task dedicati in `DataManage.cpp` la gestiscono.

- `InDataTask`: preleva dalla coda `InQueue` i pacchetti di telemetria ricevuti via BLE e li invia tramite UART al nodo Wi-Fi (pacchetto tipo 10);

- `InLoginDataTask`: preleva dalla coda `InQueueLogin` le richieste di associazione dello smartwatch e le invia via UART (pacchetto tipo 1);

- `OutDataTask`: preleva da `OutQueue` la conferma di ricezione dell'emergenza arrivata da UART (pacchetto tipo 11), attende 1500 ms e la trasmette tramite advertisement BLE;

- `OutLoginDataTask`: preleva da `OutQueueLogin` la risposta di associazione (pacchetto tipo 0 con UID assegnato) arrivata da UART e la trasmette via BLE;

- `InUpdateDataTask`: preleva da `InQueueUpdate` la richiesta di verifica aggiornamenti proveniente dallo smartwatch e la inoltra a UART (pacchetto tipo 4);

- `OutUpdateDataTask` prende da `OutQueueUpdate` il risultato della verifica aggiornamento ricevuto da UART (pacchetto tipo 5). Poi lo invia tramite BLE.

## Comunicazione Bluetooth Low Energy (BLE)

La gestione BLE utilizza la libreria `NimBLE-Arduino` ed è incapsulata nella classe `BleBroadcaster`:

### Scansione e ricezione

La scansione passiva si svolge in modo continuo. L'intervallo e la finestra di scansione durano entrambi 100 ms.

2. Il callback `ScanCb::onResult` controlla i pacchetti di advertisement ricevuti. Verifica se è presente il Service Data UUID `0xFFE0` oppure il nome dispositivo `WA` (Watch Agent).

3. La funzione `SearchDuplicate` confronta gli ultimi 6 byte del payload con una tabella circolare di 50 elementi. Serve a eliminare frame ripetuti.

4. Se il pacchetto è inedito, il sistema lo decifra usando `Decrypt` con AES-256 ECB. Poi lo manda a `ParsePacket` per controllare l'integrità e aggiungerlo alla coda FreeRTOS corrispondente.

### Trasmissione delle risposte

1. Il payload da trasmettere viene messo in un blocco di 16 byte già riempito con byte pseudocasuali usando `esp_fill_random`. Poi viene cifrato con AES-256 ECB.

2. L'advertisement BLE si imposta con UUID di servizio `0xFEE0` e nome dispositivo `ESP_REPLY`.

3. L'advertising non connettibile parte per 1000 ms. Tra un pacchetto e l'altro passa un intervallo di 50 ms. Questo serve a fare in modo che lo smartwatch riceva i dati prima che il processo si fermi.

## Protocollo di comunicazione seriale UART

Il modulo parla con il nodo Wi-Fi usando la periferica hardware `Serial2` sui pin RX 16 e TX 17. La velocità è di 115200 baud con il formato 8N1.

### Formato del frame

Ogni messaggio trasmesso sul bus seriale rispetta la seguente struttura:

| Byte 0 | Byte 1 | Byte 2 to N+1 | Byte N+2 |

|---|---|---|---|

| `START_BYTE` (`0xAA`) | `LEN` (lunghezza payload) | `PAYLOAD` (dati pacchetto) | `CRC-8` (checksum) |

Il checksum CRC-8 si calcola sul gruppo che comprende il byte di lunghezza e tutto il payload. Si usa il polinomio generatore `0x07`.

### Trasmissione con handshake e ritrasmissione

La funzione `sendUART` garantisce l'affidabilità del canale:

1. prende in modo esclusivo il semaforo ricorsivo `UARTMutex`;

2. manda il frame sulla porta seriale.

3. aspetta fino a 100 ms (`UART_ACK_TIMEOUT_MS`) un byte di risposta dall'altro nodo;

4. Se riceve `ACK_BYTE` (`0x06`), la trasmissione si considera conclusa con successo.

5. Se riceve `NACK_BYTE` (`0x15`) o scade il timeout, ripete la trasmissione. Può fare al massimo 3 tentativi (`UART_RETRIES`).

### Ricezione a stati

Il task `rxTask` elabora il flusso di byte in ingresso tramite una macchina a stati finiti:

- `ATTESA_START`: attende il byte `0xAA` oppure registra i byte di riscontro `ACK`/`NACK` se riferiti a un invio in corso;

- `LEGGI_LEN`: legge la lunghezza dichiarata del payload e valida che rientri nel limite massimo di 200 byte;

- `LEGGI_DATI`: accumula i byte del payload nel buffer;

- `LEGGI_CRC`: confronta il CRC ricevuto con quello calcolato localmente. Se coincide, invia `ACK_BYTE` e chiama `manageQueue` per instradare i dati. Se non coincide, risponde con `NACK_BYTE` e scarta il pacchetto.

Se tra due byte di fila passano più di 50 ms, la macchina a stati si reimposta in modo automatico su `ATTESA_START`.

## Tipi di pacchetto e cifratura

Tutti i pacchetti inviati o ricevuti via radio BLE hanno una dimensione di 16 byte (`BLOCK_LEN = 16`). Sono cifrati con AES-256 in modalità ECB. All'avvio, il sistema recupera la chiave a 32 byte dalla partizione NVS.

| Tipo (PID) | Direzione | Struttura dati | Descrizione |

|---|---|---|---|

| `0` | BLE &rarr; UART | `InDataLogin` | Richiesta di associazione con indirizzo MAC (6 byte) |

| `1` | UART &rarr; BLE | `OutDataLogin` | Risposta di associazione contenente MAC e UID assegnato |

| `4` | BLE &rarr; UART | `InUpdateData` | Richiesta di controllo disponibilità aggiornamento per lo UID |

| `5` | UART &rarr; BLE | `OutUpdateData` | Risposta con flag booleano di disponibilità aggiornamento |

| `10` | BLE &rarr; UART | `InData` | Telemetria periodica o d'emergenza (UID, BPM, batteria, passi, emergenza pulsante, caduta, RSSI) |

| `11` | UART &rarr; BLE | `OutData` | Conferma di ricezione emergenza o pressione pulsante |

In ricezione, `ParsePacket` controlla il senso dei dati su `InData` e scarta i frame con valori fuori scala. Ad esempio, elimina quelli con `battery > 100`, `bpm > 254`, `rssi < -110` o `rssi > 10`, oppure con stati booleani non validi.

## Memoria non volatile (NVS)

La classe `NVSConfig` sfrutta la libreria `Preferences` per salvare e recuperare in modo sicuro i parametri essenziali nel namespace `space`:

- `key`: chiave crittografica AES-256 binaria di 32 byte utilizzata per tutte le operazioni crittografiche BLE;

- `url`: stringa che imposta l'indirizzo del servizio.

La partizione NVS e lo spazio per le immagini di boot e OTA sono indicati nel file `Prova.csv`.

## Compilazione e caricamento

Il firmware è sviluppato per ESP32 usando PlatformIO con i framework `arduino` ed `espidf` insieme.

### Requisiti

- PlatformIO Core o estensione PlatformIO per Visual Studio Code;
- toolchain Espressif 32.

### Comandi principali

Compilazione del firmware:

```bash
pio run
```

Caricamento sulla scheda ESP32:

```bash
pio run -t upload
```

Apertura del monitor seriale:

```bash
pio device monitor
```

## Logging seriale

I messaggi di sistema vengono stampati a 115200 baud tramite la classe template `Log`. Ogni riga include il timestamp nel formato `[HH:MM:SS.mmm]` calcolato dall'avvio e adotta codici escape ANSI per distinguere la severità:

- **Normale** (bianco): tracciamento ordinario del flusso e avvio;
- **Info** (blu): transito pacchetti UART e BLE;
- **Warning** (giallo): CRC errati, pacchetti non gestiti o anomalie di validazione;
- **Allarme** (rosso): errori crittografici, fallimenti di allocazione o problemi nell'avvio BLE.

