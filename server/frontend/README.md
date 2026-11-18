# Frontend

Il frontend è una single-page application React. Presenta al personale della
RSA una dashboard responsive per controllare pazienti, dispositivi ed
emergenze. Le richieste HTTP passano da Axios verso `/api`; gli aggiornamenti
immediati arrivano dal WebSocket autenticato.

## Flusso dell'applicazione

`App.jsx` configura il router. La root reindirizza a `/dashboard`; login e
registrazione sono disponibili agli utenti non autenticati, mentre tutte le
route della dashboard sono protette da `ProtectedRoute`. `GuestRoute` impedisce
di tornare alle pagine di accesso quando esiste già una sessione.

All'avvio `AuthProvider` chiama `/users/me` per verificare il cookie JWT. Dopo
il login ripete la richiesta per ottenere i dati dell'utente. Il logout rimuove
prima la subscription push del browser e poi chiama l'endpoint di logout.

Quando l'utente è autenticato, `WebSocketProvider` apre la connessione verso
`/api/ws`, espone funzioni di iscrizione agli eventi e tenta la riconnessione
dopo tre secondi da una disconnessione. `DeviceProvider` e
`EmergencyProvider` usano questi eventi per aggiornare i dati senza ricaricare
la pagina.

## Pagine e funzionalità

La dashboard contiene:

- **Overview**: riepilogo di pazienti, dispositivi e situazioni attive;
- **Pazienti/associazioni**: inserimento pazienti, elenco delle associazioni
  attive e collegamento di un dispositivo connesso a un paziente;
- **Dispositivi**: dispositivi connessi e in attesa, approvazione o rifiuto e
  dati realtime ricevuti dal dispositivo;
- **Emergenze**: separazione tra emergenze attive e risolte, con azione di
  risoluzione;
- **Dettaglio paziente**: informazioni del paziente, dati del dispositivo
  associato e storico delle emergenze;
- **Impostazioni**: gestione dell'account e attivazione/disattivazione delle
  notifiche push.

Le pagine di login e registrazione gestiscono rispettivamente accesso e
creazione dell'account. Gli errori di navigazione mostrano la pagina `404`.

## Stato e comunicazione con il backend

I servizi in `src/api` incapsulano le chiamate Axios:

- `authService.js`: sessione e account;
- `patientsService.js`: pazienti e associazioni;
- `devicesService.js`: elenco e stato dei dispositivi;
- `emergenciesService.js`: elenco e risoluzione delle emergenze.

I context condividono lo stato tra le pagine. `AuthContext` gestisce l'utente,
`DeviceContext` mantiene liste pending/connesse, `EmergencyContext` separa
emergenze attive e risolte, mentre `WsContext` gestisce connessione,
subscription e invio di messaggi. Gli eventi ricevuti sono
`NEW_DEVICE`, `DEVICE_UPDATE` e `NEW_EMERGENCY`; l'evento in uscita usato dalla
dashboard è `DEVICE_CONNECTED`.

Per le notifiche browser, `PushNotificationButton` usa il service worker e
`PushManager`, invia endpoint e chiavi a `/api/push/subscribe` e revoca la
subscription con `/api/push/unsubscribe`.

## Organizzazione degli stili e dei componenti

Le pagine specifiche della dashboard vivono sotto `assets/pages/dashboard`.
I componenti riutilizzabili di interfaccia sono in `assets/ui`, mentre gli
stili locali sono organizzati accanto ai componenti tramite CSS module. I
guard di routing, i context, i servizi API, le costanti WebSocket e gli hook
sono separati per evitare di accoppiare la presentazione alla comunicazione
con il backend.

## Directory del progetto

```text
frontend/
└── src/
    ├── api/                 Client Axios e servizi REST per dominio
    ├── assets/
    │   ├── fonts/           Font usati dall'interfaccia
    │   ├── pages/           Login, registrazione, dashboard e pagina 404
    │   └── ui/              Alert, card, liste e toggle riutilizzabili
    ├── components/          ProtectedRoute e GuestRoute
    ├── constants/           Nomi degli eventi WebSocket
    ├── context/             Stato condiviso di autenticazione, device, eventi
    ├── hooks/               Hook locali, incluso il toggle della password
    ├── utils/               Funzioni di supporto, come la formattazione oraria
    ├── App.jsx              Router e composizione dei provider
    ├── App.css              Stili dell'applicazione
    ├── index.css            Stili globali
    └── main.jsx             Punto di ingresso React
```

