# Watch Agent

`watch_agent` è il programma dell'orologio che raccoglie dati dal sensore cardiaco, gestisce il pulsante fisico e comunica con un dispositivo esterno tramite Bluetooth Low Energy (BLE).

## Funzionalità principali
 
- misurazione periodica della frequenza cardiaca tramite il plugin `hrmsensor`;
- lettura dei campioni del battito tramite socket UNIX e calcolo del BPM corrente;
- lettura dell'accelerometro tramite il plugin `accelerometersensor`;
- rilevamento di caduta libera seguita da impatto e invio di una telemetria di emergenza;
- rilevamento dei passi tramite analisi dei picchi regolari dell'accelerometro;
- conteggio dei passi incluso nei pacchetti di telemetria;
- lettura del livello della batteria tramite il servizio D-Bus MCE;
- gestione del pulsante fisico tramite `/dev/input/event0`;
- pausa della misurazione cardiaca alla pressione del pulsante;
- invio di una telemetria con `button_state` e attesa di una risposta BLE;
- controllo del motore di vibrazione tramite i file sysfs di durata, attivazione e gain;
- riproduzione di notifiche audio tramite GStreamer e PulseAudio;
- invio di pacchetti cifrati tramite BLE advertisement;
- scansione BLE LE e parsing delle risposte dell'ESP32;
- connessione Wi-Fi tramite ConnMan con agent D-Bus per la password;
- salvataggio persistente delle credenziali Wi-Fi cifrate;
- aggiornamento remoto dell'agente con download ZIP, backup, rollback e riavvio del processo;
- gestione del wake lock durante le misurazioni;
- log su terminale e file, con rotazione, compressione gzip e numero massimo di backup;

## Struttura del progetto

```text
watch_agent/
|-- app.py                                      # Entry point e ciclo principale GLib
|-- config.ini                                  # Configurazione iniziale, spostata in /etc/watch_agent/
|-- .env.example                                # Esempio delle variabili richieste
|-- README.md
|-- logs/                                       # Archivi compressi dei log
|   `-- *.txt.gz
`-- assets/
	|-- __init__.py
	|-- controllers/                            # Controllo delle periferiche
	|   |-- __init__.py
	|   |-- AccelerometerSensorController.py    # Accelerometro, passi e cadute
	|   |-- BatteryController.py                # Batteria via MCE/D-Bus
	|   |-- BluetoothController.py              # Advertisement e scansione BLE
	|   |-- ButtonsController.py                # Pulsante fisico e risposta ESP32
	|   |-- HeartSensorController.py            # Sensore cardiaco e BPM
	|   |-- SoundController.py                  # Riproduzione audio
	|   |-- VibrationController.py              # Motore di vibrazione via sysfs
	|   `-- WiFiController.py                   # Connessione Wi-Fi via ConnMan
	|-- lib/
	|   `-- threading.py                        # Thread con valore di ritorno
	|-- managers/                               # Servizi applicativi
	|   |-- __init__.py
	|   |-- AppManager.py                       # Orchestrazione misure e chiusura
	|   |-- ConfigManager.py                    # Caricamento INI e variabili ambiente
	|   |-- LogsManager.py                      # Log, rotazione e compressione
	|   |-- OSManager.py                        # Wake lock e cambio utente
	|   |-- SettingsManager.py                  # Impostazioni persistenti JSON
	|   `-- UpdateManager.py                    # Update, backup, rollback e reload
	`-- utils/                                  # Funzioni di supporto
		|-- __init__.py
		|-- EncryptUtils.py                     # AES-256 ECB per payload e stringhe
		`-- PacketsUtils.py                     # Costruzione e parsing dei pacchetti
```

## Flusso di avvio

`app.py` esegue queste operazioni:

1. crea il `GLib.MainLoop` e registra il file descriptor del pulsante;
2. programma la prima misurazione dopo `measurements_delay` secondi;
3. avvia il thread dell'accelerometro e registra il callback per le cadute;
4. salva nel file JSON le credenziali Wi-Fi presenti nelle variabili nel file .env;
5. avvia in background il controllo degli aggiornamenti;
6. esegue una prima iterazione della gestione applicativa, legge la batteria e riproduce il suono di avvio;
7. entra nel ciclo principale GLib.

Alla chiusura vengono rilasciate le sessioni dei sensori, chiuso il pulsante e disattivato il Wi-Fi.

## Misurazioni e telemetria

Durante una misurazione `AppManager` acquisisce il wake lock, inizializza il sensore cardiaco se necessario e lo mantiene attivo per `measurements_time` secondi. Al termine:

1. arresta il sensore;
2. aggiorna il livello della batteria;
3. legge il contatore dei passi;
4. costruisce e cifra la telemetria;
5. trasmette il payload tramite advertisement BLE;
6. rimuove il wake lock.

Una caduta rilevata dall'accelerometro invia immediatamente una telemetria con il campo `fall` impostato a `1` e resetta lo stato di caduta. Un impulso senza la sequenza caduta libera-impatto viene registrato e produce una vibrazione, ma non viene trattato come emergenza.

## Pulsante ed emergenze

Alla pressione del pulsante:

1. la misurazione cardiaca viene arrestata e messa in pausa;
2. l'orologio vibra;
3. viene inviata una telemetria con `button_state = 1`;
4. il dispositivo avvia una scansione BLE LE per `timeout_receive_time` secondi;
5. se riceve un dispositivo, esegue il callback di risposta e vibra;
6. se non riceve risposta, il callback di timeout riprende comunque la misurazione.

## Cifratura

Il payload viene cifrato con AES-256 ECB usando la chiave `BLE_KEY`, lunga esattamente 32 byte, e la telemetria aggiunge 2 byte casuali finali.

## Configurazione

### `config.ini`

Il file configura:

- percorsi D-Bus, plugin e socket dei sensori;
- soglie di caduta libera e impatto;
- intervallo e durata delle misurazioni;
- adapter, advertisement, servizio e timeout BLE;
- dispositivo e formato degli eventi del pulsante;
- percorsi sysfs e parametri della vibrazione;
- servizio batteria MCE;
- file audio e comportamento di attesa;
- servizio ConnMan e agent Wi-Fi;
- file log, soglia di rotazione e numero di backup;
- percorsi wake lock e utente `ceres`.

Al primo avvio `ConfigManager` crea `/etc/watch_agent` e sposta li `config.ini` presente nella directory del progetto. Le esecuzioni successive usano `/etc/watch_agent/config.ini`. Il processo deve avere i permessi necessari per creare e modificare questa directory.

Le impostazioni persistenti vengono salvate in `/var/lib/watch_agent/storage.json`. Le credenziali Wi-Fi sono memorizzate nel JSON in forma cifrata.

## Aggiornamento remoto

`UpdateManager` viene avviato in un thread separato. Prima tenta la connessione Wi-Fi usando le credenziali salvate, poi:

1. crea un backup di `/usr/share/watch_agent` in `backup_dir`;
2. scarica lo ZIP da `update_url`;
3. lo estrae in `tmp_dir`;
4. copia i file aggiornati nella directory dell'applicazione;
5. elimina ZIP e directory temporanea;
6. riavvia il processo con `os.execv`.

In caso di errore durante l'aggiornamento viene usato il backup disponibile per eseguire il rollback.

## Avvio

L'agente deve essere eseguito nell'ambiente del dispositivo, con D-Bus, GLib, BlueZ, ConnMan, MCE, GStreamer e i file sysfs dei sensori disponibili.

```bash
python3 /usr/share/watch_agent/app.py
```

In alternativa, se e presente un'unita systemd:

```bash
systemctl enable watch-agent.service
systemctl start watch-agent.service
```

## Log

I log vengono stampati a terminale e scritti nel file configurato da `LOGS.logs_path`. Quando superano `LOGS.max_size_kb`, il file viene compresso in `logs/*.txt.gz`; `LOGS.max_backups` limita il numero di archivi conservati.
