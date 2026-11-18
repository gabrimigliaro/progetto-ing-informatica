# RSA Monitoring

RSA Monitoring è un sito web per il monitoraggio degli ospiti di una residenza
sanitaria assistenziale tramite dispositivi indossabili. Il personale autenticato
può registrare i pazienti, collegare un dispositivo a ciascun paziente,
controllare lo stato dei dispositivi e gestire le emergenze rilevate.

Il progetto è diviso in tre parti:

- **backend**: API REST e WebSocket realizzate con FastAPI, accesso al database,
  autenticazione e logica di gestione delle emergenze;
- **database**: schema PostgreSQL con utenti, pazienti, dispositivi,
  associazioni, emergenze e iscrizioni alle notifiche push;
- **frontend**: interfaccia React della dashboard, con pagine di accesso,
  gestione dei dati e aggiornamenti realtime.

## Funzionamento generale

1. Un operatore crea un account oppure accede con le proprie credenziali.
2. Il backend verifica la password, crea un token JWT e lo salva in un cookie
   `access_token`. Le route protette usano quel cookie per identificare l'utente.
3. I dispositivi possono essere registrati e appaiono inizialmente come
   `PENDING`. L'operatore li accetta o li rifiuta dalla sezione dispositivi.
4. Un dispositivo con stato `CONNECTED` può essere associato a un solo paziente,
   e ogni paziente può avere una sola associazione attiva.
5. Il dispositivo invia pacchetti al WebSocket. Il backend li interpreta,
   aggiorna lo stato mostrato nella dashboard e salva una nuova emergenza quando
   rileva una caduta, una richiesta di aiuto o una frequenza cardiaca fuori
   soglia.
6. La dashboard riceve gli eventi `NEW_DEVICE`, `DEVICE_UPDATE` e
   `NEW_EMERGENCY` in tempo reale. Le emergenze possono essere visualizzate,
   filtrate tra attive e risolte e chiuse indicando l'operatore e l'orario.
7. Il browser può registrare una subscription Web Push. In questo modo il
   backend può inviare notifiche ai dispositivi iscritti; la subscription viene
   rimossa durante il logout.

## Funzionalità principali

- registrazione, login, logout e cancellazione dell'account;
- dashboard protetta con panoramica dei pazienti e delle emergenze;
- inserimento, consultazione e cancellazione dei pazienti;
- approvazione o rifiuto dei dispositivi rilevati;
- associazione e disassociazione tra pazienti e dispositivi;
- visualizzazione del battito, della batteria, dei passi e dello stato del
  dispositivo;
- gestione delle emergenze attive e dello storico delle emergenze risolte;
- aggiornamenti realtime tramite WebSocket;
- notifiche browser tramite Web Push.

## Directory del progetto

Sono riportate solo le directory applicative; sono escluse le directory
`frontend/public`, `node_modules` e i file di configurazione o di dipendenze.

```text
backend/
├── api/       Endpoint REST/WebSocket e dipendenze per l'autenticazione
├── assets/    Modelli SQLAlchemy, schemi Pydantic, CRUD e utilità WebSocket
└── core/      Connessione al database e funzioni di sicurezza
database/
└── schema.sql Definizione delle tabelle, vincoli e indici PostgreSQL
frontend/
└── src/      Applicazione React, servizi API, contesti, pagine e componenti UI
```

Per i dettagli tecnici delle singole parti consultare i README di
[backend](./backend/README.md), [database](./database/README.md) e [frontend](./frontend/README.md).

