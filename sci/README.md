# SCI

`SCI` è il server asincrono in Python incaricato della raccolta dati dai **Nodi ESP** tramite socket TCP, della deduplicazione dei pacchetti ricevuti da più nodi e dell'inoltro bidirezionale verso un server WebSocket esterno.

## Funzionalità principali

- server TCP asincrono (`asyncio.start_server`) su porta `8000` per la gestione concorrente dei **Nodi ESP**;
- client WebSocket asincrono (`websockets.connect`) con riconnessione automatica per la comunicazione bidirezionale verso `WS_SERVER_URL`;
- disaccoppiamento e sincronizzazione concorrente dei flussi tramite doppia coda asincrona (`inQueue` per il traffico Nodi ESP &rarr; WebSocket e `outQueue` per il traffico WebSocket / SCI &rarr; Nodi ESP);
- deduplicazione su finestra temporale (`TEMPO_ATTESA = 2.0` secondi) con selezione automatica del pacchetto ricevuto dal nodo con segnale `rssi` migliore;
- watchdog di inattività (`watchdogLoop`) configurabile tramite `WATCHDOG_TIMEOUT` che monitora l'ultimo pacchetto ricevuto per ogni `uid` e invia la segnalazione `20,<uid>` via WebSocket in caso di timeout;
- parsing e validazione a stream delle righe TCP nel formato `apName|t<PID>,campi...` con scarto delle righe malformate;
- scambio messaggi via WebSocket tramite stringhe CSV delimitate da virgole;
- persistenza su file JSON (`data/watches.json`) della tabella di associazione `knownWatches` (`MAC -> UID`) tramite `storage.py`;
- trasmissione broadcast asincrona (`asyncio.gather`) verso tutti i **Nodi ESP** connessi per le risposte di login (`PID 1`) e i comandi di stop emergenza (`PID 11`);
- predisposizione per la gestione delle richieste di aggiornamento (`PID 2` &rarr; `PID 3`) tramite `manageUpdate`;
- sistema di logging strutturato su console con timestamp `HH:MM:SS` e codici colore ANSI (`log.py`);
- supporto all'esecuzione containerizzata tramite `Dockerfile`, `docker-compose.yml` e `requirements.txt`.

## Struttura del progetto

```text
SCI/
|-- Dockerfile                                  # Definizione immagine Docker Python
|-- docker-compose.yml                          # Orchestrazione container, volume data/ ed esposizione porta 8000
|-- requirements.txt                            # Dipendenze Python esterne (websockets)
|-- README.md
|-- main.py                                     # Entry point asincrono, avvio loop code, watchdog, TCP e WS
|-- server.py                                   # Server TCP (Nodi ESP), client WebSocket e parsing messaggi
|-- router.py                                   # Smistamento pacchetti, watchdog, broadcast ai Nodi ESP e TX WS
|-- deduplicator.py                             # Finestra temporale di deduplicazione e selezione rssi migliore
|-- state.py                                    # Stato globale condiviso (dizionari, code, timer watchdog)
|-- storage.py                                  # Caricamento e salvataggio atomico di data/watches.json
|-- data.py                                     # Dataclass tipizzate per pacchetti in ingresso e in uscita
|-- log.py                                      # Utility di logging su console con timestamp e colori ANSI
`-- data/
    `-- watches.json                            # File persistente delle associazioni MAC -> UID