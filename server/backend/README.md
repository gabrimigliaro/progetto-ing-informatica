# Backend

Il backend espone il servizio applicativo di RSA Monitoring. È una API FastAPI
con prefisso comune `/api`, collegata a PostgreSQL tramite SQLAlchemy. Gestisce
autenticazione, utenti, pazienti, dispositivi, associazioni, emergenze,
WebSocket e iscrizioni alle notifiche push.

## Avvio e configurazione

L'applicazione viene creata in `main.py` con titolo `RSA Monitoring`, registra
il router principale e abilita il middleware CORS per il dominio del frontend.
La connessione al database è letta da `DATABASE_URL`.

La sicurezza richiede le variabili d'ambiente `SECRET_KEY` e, opzionalmente,
`ALGORITHM` e `ACCESS_TOKEN_EXPIRE_MINUTES`. Il WebSocket usa
`WEBSOCKET_SECRET` per verificare i codici TOTP dei dispositivi. Le notifiche
Web Push richiedono `VAPID_PRIVATE_KEY`.

## Autenticazione

La registrazione salva la password usando Argon2. Il login confronta la
password con l'hash, crea un JWT con `sub`, `iat` ed `exp` e lo restituisce in
un cookie `access_token`. Il cookie viene usato da `get_current_user` per
proteggere le route della dashboard; se manca, è scaduto o l'utente non esiste,
la richiesta termina con `401`.

Il logout elimina il cookie. Le route `/users/me` permettono al frontend di
ricostruire la sessione al caricamento e di eliminare l'account corrente.

## API REST

Tutti gli endpoint sono inclusi sotto `/api`:

- `/auth`: login e logout;
- `/users`: registrazione, utente corrente, lettura e cancellazione utenti;
- `/patients`: creazione, elenco, dettaglio e cancellazione pazienti;
- `/devices`: elenco dispositivi, dispositivi in attesa o connessi, approvazione,
  rifiuto e cancellazione;
- `/associations`: associazione attiva paziente-dispositivo e disassociazione;
- `/emergencies`: creazione, elenco completo o solo non risolto, risoluzione e
  cancellazione;
- `/push`: registrazione e rimozione delle subscription Web Push;
- `/ws`: endpoint WebSocket per dispositivi e dashboard.

Le route gestionali usano gli schemi Pydantic per validare i dati in ingresso e
restituire risposte con una forma stabile. La logica di persistenza è delegata
ai moduli CRUD, mentre gli endpoint coordinano dipendenze, autorizzazione e
codici HTTP.

## WebSocket e dispositivi

Il WebSocket accetta una connessione se presenta un codice TOTP valido tramite
header/query oppure un cookie JWT valido. `ConnectionManager` mantiene le
connessioni attive e inoltra gli eventi alle dashboard.

`parsePacket` interpreta due formati principali:

- pacchetto di tipo `0`: registra un nuovo indirizzo MAC e invia
  `NEW_DEVICE`;
- pacchetto di tipo `10`: legge identificativo del dispositivo, BPM, batteria,
  passi e flag di emergenza/caduta. Se il dispositivo è associato a un
  paziente, invia `DEVICE_UPDATE` e, quando necessario, salva e inoltra
  `NEW_EMERGENCY`.

Le emergenze generate dal pacchetto di monitoraggio sono: caduta (tipo `1`),
BPM alto (tipo `2`, almeno `140`), BPM basso (tipo `3`, al massimo `40`) e
supporto richiesto (tipo `4`). La prima condizione verificata determina il tipo
salvato.

## Persistenza e organizzazione del codice

I moduli `core` definiscono il motore SQLAlchemy, le sessioni per richiesta,
l'hashing Argon2 e la creazione/verifica dei JWT. I modelli in `assets/models`
rappresentano le tabelle, gli schemi in `assets/schemas` definiscono i
contratti API e `assets/crud` contiene le operazioni sul database. Le
operazioni WebSocket che bloccano sono eseguite in thread pool per non fermare
il loop asincrono.

## Directory del progetto

```text
backend/
├── api/
│   ├── api.py              Aggrega i router e assegna prefissi/tag
│   ├── deps.py             Dipendenze FastAPI, sessione e utente corrente
│   └── endpoints/          Route REST e WebSocket per ogni area funzionale
├── assets/
│   ├── crud/               Query e operazioni di creazione/aggiornamento
│   ├── models/             Modelli SQLAlchemy di utenti e dominio RSA
│   ├── schemas/            Schemi Pydantic per input e output API
│   └── utils/               Parsing dei pacchetti e gestione eventi WebSocket
├── core/
│   ├── database.py         Engine, session factory e dependency del database
│   └── security.py         Argon2, JWT e configurazione della sicurezza
└── main.py                 Istanza FastAPI, router principale e CORS
```

