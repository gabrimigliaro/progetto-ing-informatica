# Watch Agent

`watch_agent` è il programma dell'orologio che raccoglie dati dal sensore cardiaco, gestisce il pulsante fisico e comunica con un dispositivo esterno tramite Bluetooth Low Energy (BLE).

## Funzionalita principali

- inizializza e controlla il sensore del battito cardiaco;
- legge i dati del sensore tramite D-Bus e socket UNIX;
- esegue misurazioni periodiche, configurabili nel file INI;
- legge il livello della batteria tramite il servizio MCE;
- rileva la pressione del pulsante fisico tramite `/dev/input/event0`;
- attiva il motore di vibrazione attraverso i file sysfs;
- invia pacchetti telemetrici cifrati via BLE advertisement;
- ascolta una risposta BLE dopo la pressione del pulsante;
- mantiene il dispositivo sveglio durante la misurazione tramite wake lock;
- scrive log a terminale e su file, comprimendo gli archivi troppo grandi.

## Struttura del progetto

```text
watch_agent/
|-- app.py                         # Entry point e ciclo principale GLib
|-- config.ini                     # Configurazione hardware e servizi (viene poi spostato in /etc/watch_agent/)
|-- .env.example                   # Esempio del file .env
|-- assets/
|   |-- controllers/               # Driver e controllo delle periferiche
|   |   |-- HeartSensorController.py
|   |   |-- BluetoothController.py
|   |   |-- ButtonsController.py
|   |   |-- BatteryController.py
|   |   `-- VibrationController.py
|   |-- managers/                  # Configurazione, log e gestione alimentazione
|   |   |-- ConfigManger.py
|   |   |-- LogsManager.py
|   |   `-- OSManager.py
|   `-- utils/                     # Cifratura e costruzione dei pacchetti
|   |   |-- EncryptUtils.py
|   |   `-- PacketsUtils.py
`-- logs/                          # Archivi compressi dei log
```

## Come funziona

All'avvio `app.py` crea il loop principale GLib e registra il file descriptor del pulsante. Dopo il ritardo configurato in `config.ini`, viene avviata una misurazione del battito.

Durante una misurazione:

1. viene attivato il plugin `hrmsensor` tramite D-Bus;
2. viene richiesta una sessione al sensore;
3. il programma apre `/var/run/sensord.sock` e completa l'handshake;
4. i campioni ricevuti aggiornano il valore corrente dei BPM;
5. al termine viene letto il livello della batteria;
6. viene costruito e cifrato un pacchetto telemetrico;
7. il pacchetto viene trasmesso per un breve periodo tramite BLE advertisement;
8. il wake lock viene rimosso.

Quando viene premuto il pulsante, la misurazione viene messa in pausa, il dispositivo vibra e viene inviata una telemetria con il campo `button_state` impostato a `1`. Il dispositivo avvia quindi una scansione BLE in attesa di una risposta dell'ESP. Se la risposta arriva, l'orologio vibra due volte e riprende la misurazione; in caso di timeout la misurazione riprende comunque.

## Configurazione

### `config.ini`

Il file contiene i percorsi e i parametri relativi a:

- sensore cardiaco e socket UNIX;
- intervalli e durata delle misurazioni;
- dispositivo BLE e servizio BlueZ;
- pulsante fisico;
- batteria e servizio MCE;
- vibrazione;
- log e wake lock.

All'avvio `ConfigManager` cerca una configurazione locale e, se la trova, la sposta in `/etc/watch_agent/config.ini`. Il processo deve quindi avere i permessi necessari per creare e scrivere in `/etc/watch_agent`.

## Avvio

```bash
python3 /usr/share/watch_agent/app.py
```

oppure con servizio:

```bash
systemctl enable watch-agent.service
systemctl start watch-agent.service
```

## Log

I log vengono stampati a terminale e salvati nel file indicato da `LOGS.logs_path`. Quando superano la dimensione configurata, vengono compressi in `logs/` in formato `.txt.gz`. Il numero massimo di archivi conservati e' controllato da `LOGS.max_backups`.

## Cose da aggiungere

- **Protocollo di registrazione:** `send_new_device_packet()` costruisce il pacchetto usando `bytes([tipo, mac_address])`; va preso l'effettivo indirizzo MAC e completata la gestione della risposta `NEW_DEVICE_RESPONSE`.
- **Pacchetto di emergenza:** e' definito il tipo `EMERGENCY_RESPONSE`, ma nel codice attuale non esiste ancora una gestione completa.
- **Passi:** il campo `steps` esiste nel formato della telemetria ma viene sempre inviato con valore predefinito `0`.
- **Rilevamento cadute**: va implementato da zero.
