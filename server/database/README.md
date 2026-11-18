# Database

Il database usa PostgreSQL e conserva sia i dati anagrafici sia gli eventi
generati dal monitoraggio. Lo schema è idempotente: utilizza `CREATE TABLE IF
NOT EXISTS` e può essere applicato senza ricreare tabelle già presenti.

## Modello dei dati

- **USERS**: account degli operatori, password già hashata, email e data di
  creazione.
- **PATIENTS**: nome, cognome e data di inserimento degli ospiti monitorati.
- **DEVICES**: indirizzo MAC, nome, stato online, stato amministrativo e data
  di registrazione. Un dispositivo nuovo parte da `PENDING`; l'operatore può
  portarlo a `CONNECTED` o `REFUSED`.
- **PATIENT_DEVICE**: storico delle associazioni tra pazienti e dispositivi.
  `IS_ACTIVE` distingue l'associazione corrente da quelle chiuse.
- **EMERGENCIES**: tipo di evento, BPM eventualmente rilevati, paziente,
  stato di risoluzione, data di apertura e operatore/data di chiusura.
- **push_subscriptions**: endpoint e chiavi Web Push legati all'utente che ha
  autorizzato le notifiche nel browser.

## Vincoli e comportamento

Le emergenze appartengono a un paziente tramite una foreign key con cancellazione
a cascata. L'operatore che risolve un'emergenza è referenziato da `USERS`; se
l'utente viene rimosso, il campo `RESOLVED_BY` viene impostato a `NULL`.
Anche le associazioni appartengono a pazienti e dispositivi: cancellare un
paziente elimina le associazioni, mentre un dispositivo associato non può
essere cancellato in modo da lasciare riferimenti invalidi.

Gli indici sulle emergenze velocizzano l'elenco per paziente e la ricerca delle
emergenze attive più recenti. Gli indici sulle associazioni velocizzano le
ricerche per paziente e dispositivo. Due indici univoci parziali impediscono
che un dispositivo sia associato attivamente a più pazienti o che un paziente
abbia più dispositivi attivi.

L'indirizzo MAC è unico. L'endpoint di una subscription push è unico e
l'eliminazione dell'utente elimina anche le sue subscription.

## Flusso dei dati

Il backend apre una sessione SQLAlchemy per ogni richiesta REST. Le route
chiamano i moduli CRUD, che eseguono query, `commit` e `refresh` degli oggetti.
Per i dati inviati dal dispositivo, il parser WebSocket individua il paziente
attraverso l'associazione attiva, salva eventuali emergenze e poi trasmette
l'evento alle dashboard collegate.