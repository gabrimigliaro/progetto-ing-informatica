# Node ESP32 WIFI

`Node_ESP32_WIFI` è il modulo firmware per ESP32 incaricato della connettività di rete Wi-Fi, della comunicazione TCP verso il server centrale (SCI) e dell'inoltro bidirezionale dei dati verso il nodo Bluetooth (`Node_ESP32_BLT`) tramite connessione seriale UART.

## Funzionalità principali

- connessione a rete Wi-Fi locale in modalità Station (`WIFI_STA`) con configurazione di IP statico, gateway e subnet mask;
- captive portal e access point di fallback (`WIFI_AP_STA`) con server DNS e web server asincrono (`ESPAsyncWebServer`) per la configurazione dei parametri di rete da browser;
- salvataggio persistente dei parametri di rete (SSID, password, nome AP, IP statico, gateway, subnet mask, IP server SCI) su memoria NVS tramite `Preferences`;
- connessione TCP client verso il server centrale SCI (`WiFiClient`) su porta configurabile (default 8000);
- disaccoppiamento e sincronizzazione concorrente delle operazioni tramite code FreeRTOS dedicate;
- comunicazione seriale full-duplex con protocollo a frame delimitato da start byte, lunghezza e checksum CRC-8 verso il modulo BLE (`Node_ESP32_BLT`);
- meccanismo di ritrasmissione UART su errore o timeout con gestione di ACK e NACK;
- trasmissione periodica e su evento di telemetria e richieste di associazione formattate come stringhe CSV tramite socket TCP;
- ricezione a stream e parsing delle risposte dal server TCP (conferma emergenza, assegnazione UID login, notifiche aggiornamento) con gestione di buffer di riga;
- monitoraggio continuo dello stato di connessione Wi-Fi e riconnessione automatica in background (`WifiUpdate`);
- lettura e persistenza della configurazione di base su memoria NVS (Non-Volatile Storage);
- sistema di logging strutturato su porta seriale con timestamp in millisecondi e codici colore ANSI;

## Struttura del progetto

```text
Node_ESP32_WIFI/
|-- CMakeLists.txt                              # Configurazione build per ESP-IDF
|-- platformio.ini                              # Configurazione ambiente PlatformIO e librerie
|-- Prova.csv                                   # Tabella delle partizioni della memoria flash (NVS, OTA, SPIFFS)
|-- README.md
|-- sdkconfig.esp32dev                          # File di configurazione hardware e parametri ESP-IDF
|-- include/
|   |-- data.h                                  # Definizioni dei tipi di pacchetto, code e parametri globali
|   |-- DataManage.h                            # Interfaccia di creazione e avvio dei task FreeRTOS
|   |-- Log.h                                   # Utility di logging seriale con timestamp e formattazione ANSI
|   |-- MyWiFi.h                                # Gestore Wi-Fi, interfaccia captive portal e web server
|   |-- NVS.h                                   # Wrapper su Preferences per la persistenza su memoria NVS
|   |-- TCP.h                                   # Gestore client TCP per comunicazione con il server SCI
|   `-- UART.h                                  # Definizioni e API del protocollo di comunicazione seriale
`-- src/
    |-- CMakeLists.txt                          # Registrazione componenti sorgente per build ESP-IDF
    |-- DataManage.cpp                          # Task FreeRTOS di smistamento dati tra code, UART e TCP
    |-- MyWiFi.cpp                              # Connessione Wi-Fi, portale captive AP e server HTTP
    |-- NVS.cpp                                 # Lettura delle chiavi di cifratura e parametri da NVS
    |-- TCP.cpp                                 # Client TCP, formattazione CSV, parsing risposte e task RX
    |-- UART.cpp                                # Macchina a stati di ricezione, calcolo CRC8 e invio su Serial2
    `-- main.cpp                                # Entry point app_main, allocazione code e avvio dei sottosistemi
```

## Flusso di avvio

All'avvio, l'entry point `app_main()` in `main.cpp` esegue la seguente sequenza di inizializzazione:

1. inizializza il core Arduino (`initArduino`) e la porta seriale principale di debug a 115200 baud;
2. crea le code FreeRTOS per il routing asincrono dei dati (`InQueue`, `InQueueLogin`, `OutQueue`, `OutQueueLogin`, `InQueueUpdate`, `OutQueueUpdate`);
3. verifica l'allocazione corretta delle code con `configASSERT`;
4. apre il namespace NVS `space` e carica in memoria i parametri di configurazione;
5. inizializza l'interfaccia hardware `Serial2` per la comunicazione UART e avvia il task di ricezione con macchina a stati;
6. avvia i task FreeRTOS di gestione dati (`DataStart`) per elaborare in parallelo code e comunicazioni;
7. avvia il task dedicato alla gestione Wi-Fi (`WifiStart`) avviando la connessione al router o il captive portal se necessario;
8. avvia il client TCP (`tcpStart`) verso l'indirizzo del server SCI configurato (`sciIP:sciSP`).

## Architettura e code FreeRTOS

La comunicazione tra l'interfaccia seriale UART e il socket TCP è completamente disaccoppiata tramite code FreeRTOS e gestita da task dedicati in `DataManage.cpp`:

- `InDataTask`: preleva dalla coda `InQueue` i pacchetti di telemetria ricevuti via UART dal modulo BLE e li trasmette al server SCI tramite TCP (`tcpSendData`);
- `InLoginDataTask`: preleva dalla coda `InQueueLogin` le richieste di associazione dello smartwatch arrivate da UART e le invia al server via TCP (`tcpSendLogin`);
- `OutDataTask`: preleva da `OutQueue` la conferma di ricezione dell'emergenza arrivata dal server TCP (pacchetto tipo 11) e la trasmette al modulo BLE via UART (`sendUART`);
- `OutLoginDataTask`: preleva da `OutQueueLogin` la risposta di associazione con UID assegnato arrivata da TCP (pacchetto tipo 1) e la trasmette al modulo BLE via UART (`sendUART`).

## Gestione Wi-Fi e Captive Portal

La connettività di rete è orchestrata dal modulo `MyWiFi.cpp`:

### Connessione ordinaria Station (STA)

All'avvio, la funzione `WiFiInit` recupera dal namespace NVS `WiFi` le credenziali del router (`ssid`, `password`) e i parametri di rete statica (`ip`, `gw`, `sn`):

1. applica la configurazione di IP statico tramite `WiFi.config`;
2. tenta la connessione al punto di accesso per 10 secondi;
3. se la connessione ha successo, la scheda rimane operativa in modalità `WIFI_STA`.

### Captive Portal di configurazione (SoftAP + DNS + HTTP)

Se le credenziali sono assenti o la connessione al router fallisce:

1. la scheda commuta in modalità mista `WIFI_AP_STA`, attivando un Access Point con SSID configurato (default `Nodo_ESP32` o `ESP32-Setup`);
2. un server DNS interno (`dnsServer`) intercetta qualsiasi richiesta su porta 53 reindirizzandola all'IP dell'Access Point;
3. un server web asincrono (`AsyncWebServer`) su porta 80 presenta una pagina web responsive (`PAGE[] PROGMEM`) per configurare i parametri:
   - SSID e password della rete Wi-Fi del router;
   - nome dell'Access Point;
   - indirizzo IP statico del nodo ESP32;
   - Gateway di rete e Subnet Mask;
   - indirizzo IP del server centrale SCI (`sciIP`).
4. all'invio del form sull'endpoint HTTP POST `/save`, i parametri vengono validati, memorizzati in modo persistente tramite `WiFiCredentials` e viene avviato immediatamente il tentativo di connessione con le nuove credenziali;
5. stabilita la connessione, l'Access Point e il server DNS vengono disattivati (`stopApSta`).

### Monitoraggio continuo della linea

Il task `WifiTask` richiama periodicamente `WifiUpdate`: se la connessione con il router cade, viene avviata una nuova procedura di connessione ogni 10 secondi per ripristinare il collegamento.

## Protocollo di comunicazione seriale UART

Il modulo comunica con il nodo Bluetooth (`Node_ESP32_BLT`) tramite la periferica hardware `Serial2` (pin RX 16, pin TX 17) a 115200 baud, 8N1.

Le specifiche del protocollo a livello di linea e di frame (formato delimitato da `START_BYTE` `0xAA`, calcolo del checksum CRC-8 con polinomio `0x07`, trasmissione affidabile con semaforo ricorsivo, riscontri `ACK`/`NACK`, timeout a 100 ms con massimo 3 tentativi e macchina a stati di ricezione a 4 stadi con timeout a 50 ms) sono identiche a quelle del nodo Bluetooth. Per tutti i dettagli implementativi e la descrizione approfondita, fare riferimento al [README di Node_ESP32_BLT](../Node_ESP32_BLT/README.md#protocollo-di-comunicazione-seriale-uart).

Nello specifico di questo nodo, la funzione `manageQueue` smista i pacchetti validati in arrivo da UART verso le code FreeRTOS interne:
- pacchetto tipo `10` (`InData`): inserito in `InQueue` per l'inoltro via TCP;
- pacchetto tipo `0` (`InDataLogin`): inserito in `InQueueLogin` per la richiesta di associazione via TCP;
- pacchetto tipo `4` (`InUpdateData`): inserito in `InQueueUpdate`.

## Comunicazione TCP con il server SCI

Il modulo `TCP.cpp` gestisce il socket client verso il server centrale SCI (`sciIP:sciSP`):

### Connessione e invio dati

Tutte le trasmissioni sul socket sono protette da mutex (`clientMutex`). Se la connessione cade, `checkConnection` ritenta automaticamente il collegamento.

I pacchetti in uscita sono formattati come stringhe CSV terminate da newline (`\n`):

- **Login / Associazione** (`tcpSendLogin`):
  ```text
  <apName>,<PID>,<MAC>\n
  ```
  *(es. `Nodo_ESP32,0,AA:BB:CC:DD:EE:FF\n`)*

- **Telemetria / Emergenze** (`tcpSendData`):
  ```text
  <apName>,<PID>,<UID>,<bpm>,<battery>,<steps>,<emergency>,<fall>,<rssi>\n
  ```
  *(es. `Nodo_ESP32,10,1,72,95,1420,0,0,-65\n`)*

### Ricezione e parsing dello stream TCP

Il task `tcpRxTask` monitora i byte ricevuti dal socket, li accumula riga per riga e passa ogni stringa completata a `manageLine`:

1. divide la riga in token separati da virgole o spazi;
2. ignora il nome AP se presente all'inizio del messaggio;
3. esamina il PID ricevuto:
   - `PID 1` (`manageLogin`): estrae MAC address e UID assegnato, popolando `OutDataLogin` e accodandolo in `OutQueueLogin`;
   - `PID 11` (`manageData`): estrae lo UID di riscontro emergenza, popolando `OutData` e accodandolo in `OutQueue`;
   - `PID 5` (`manageUpdate`): estrae lo UID per notifica disponibilità aggiornamento, popolando `OutUpdateData` e accodandolo in `OutQueueUpdate`.

## Tipi di pacchetto

| Tipo (PID) | Canale &rarr; Destinazione | Struttura dati | Formato TCP | Descrizione |
|---|---|---|---|---|
| `0` | UART &rarr; TCP | `InDataLogin` | `apName,0,MAC\n` | Richiesta di associazione smartwatch (MAC a 6 byte) |
| `1` | TCP &rarr; UART | `OutDataLogin` | `[apName,]1,MAC,UID\n` | Risposta associazione con UID assegnato |
| `4` | UART &rarr; TCP | `InUpdateData` | - | Richiesta di controllo disponibilità aggiornamento per lo UID |
| `5` | TCP &rarr; UART | `OutUpdateData` | `[apName,]5,UID\n` | Notifica di disponibilità aggiornamento firmware |
| `10` | UART &rarr; TCP | `InData` | `apName,10,UID,bpm,bat,steps,emerg,fall,rssi\n` | Telemetria periodica o stato di emergenza/caduta |
| `11` | TCP &rarr; UART | `OutData` | `[apName,]11,UID\n` | Conferma di ricezione emergenza o pressione pulsante |

## Memoria non volatile (NVS)

La partizione NVS e lo spazio dedicato alle immagini di boot e OTA sono definiti nella tabella partizioni `Prova.csv`, condivisa con il nodo Bluetooth (per lo schema delle partizioni e l'uso del namespace `space` per le chiavi crittografiche e l'URL, fare riferimento al [README di Node_ESP32_BLT](../Node_ESP32_BLT/README.md#memoria-non-volatile-nvs)).

Su questo nodo, la libreria `Preferences` gestisce inoltre in modo dedicato il namespace `WiFi`, impiegato per salvare in forma persistente la configurazione di rete:
- `ssid` e `password`: credenziali di accesso alla rete locale del router;
- `ap`: nome dell'Access Point per la modalità captive portal (default `Nodo_ESP32`);
- `ip`, `gw`, `sn`: indirizzo IP statico del nodo, gateway e subnet mask;
- `sci`: indirizzo IP del server centrale SCI.

## Compilazione e caricamento

L'ambiente di compilazione PlatformIO, i requisiti di toolchain (framework congiunto `arduino` ed `espidf` su board `esp32dev`) e i comandi di build, upload e monitor seriale (`pio run`, `pio run -t upload`, `pio device monitor`) sono identici a quelli del modulo BLE. Per la guida e i dettagli fare riferimento al [README di Node_ESP32_BLT](../Node_ESP32_BLT/README.md#compilazione-e-caricamento).

## Logging seriale

Il sistema di logging su porta seriale a 115200 baud adotta la medesima classe template `Log` con timestamp nel formato `[HH:MM:SS.mmm]` calcolato dall'avvio e codici escape colore ANSI per i vari livelli di severità (Normale, Info, Warning, Allarme). Per le specifiche fare riferimento al [README di Node_ESP32_BLT](../Node_ESP32_BLT/README.md#logging-seriale).
