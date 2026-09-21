# Progetto Ingegneria Informatica POLIMI 2026/2027

Sistema IoT di monitoraggio pazienti basato su wearable Bluetooth, nodi ESP, Sistema Centralizzato Intelligente (SCI) e Dashboard Web.

---

## 📋 Descrizione del Progetto

Il sistema permette il monitoraggio continuo dei parametri sanitari e della sicurezza dei pazienti all'interno di una struttura sanitaria o abitativa. Attraverso dispositivi indossabili (orologi BLE), antenne di ricezione (ESP) dislocate nell'ambiente, un sistema centralizzato presente in loco e un server centralizzato esterno. Il sistema raccoglie dati biometrici, rileva emergenze (richieste d'aiuto e cadute) e fornisce una dashboard web in tempo reale per gli operatori.

---

## 🛠️ Realizzazione

Acquisteremo uno smartwatch programmabile su cui flasheremo una versione di [AsteroidOS](https://asteroidos.org/). A quel punto svilupperemo gli script python
per:
1. **Gestire l'invio dei pacchetti tramite Bluethooth**
2. **Inviare l'allarme quando il paziente preme il tasto fisico laterale**
3. **La rilevazione delle cadute tramite accelerometro e giroscopio con relativa notifica** *(in via di valutazione)*

L'[architettura](#-architettura-e-flussi-di-comunicazione) è semplice:
1. L'orologio invia il pacchetto Bluethooth alle antenne presenti in loco.
2. Le antenne inviano sulla rete WiFi il pacchetto al SCI.
3. SCI deciderà se scartare il pacchetto (deduplicato) o inviarlo al server esterno per aggiorare i campi presenti sulla WebApp.
4. La WebApp mostrerà i dati aggiornati all'operatore connesso e salverà sul DataBase eventuali anomalie (Battiti alti/bassi, caduta rilevata, richiesta d'aiuto)

---

## 🛠️ Architettura e Flussi di Comunicazione

### 1. Riconoscimento e Registrazione Dispositivo (Orologio)
- **Broadcast BLE**: Gli orologi inviano pacchetti Bluetooth in broadcast intercettati dalle antenne ESP.
- **Protocollo di Identificazione**: Viene definito un protocollo per identificare univocamente il dispositivo e associarlo a uno specifico paziente.
- **Aggiunta Automatizzata nel Database**:
  1. Il dispositivo comunica con l'antenna ESP inviando un segnale "alive".
  2. L'ESP inoltra la richiesta di aggiunta al SCI.
  3. SCI verrà forzato ad inviare la richiesta al server e si salverà l'ID della stessa sul DataBase.
  4. L'operatore visualizza la richiesta sul sito e conferma la registrazione nel database tramite pressione di un tasto.
  5. La WebApp salverà sul DataBase l'ID univoco del dispositivo.

### 2. Gestione delle Allerte e Localizzazione
- **Attivazione Allerta**: In caso di emergenza, l'orologio vibra e modifica il payload del pacchetto inserendo il flag `"alert"` (Inviando immediatamente il pacchetto).
- **Inoltro a SCI**: L'ESP riceve il pacchetto e lo inoltra a SCI
- **Gestione Pacchetto**: SCI sarà forzato ad inviare immediatamente il pacchetto saltando la coda.
- **Notifica su Dashboard**: La web app mostra l'allerta indicando la posizione approssimativa del paziente (basata sull'antenna che ha ricevuto il segnale).
- **Disattivazione Allerta**: 
  1. L'operatore spegne l'allerta premendo il pulsante dedicato sulla dashboard.
  2. La WebApp parlerà allo SCI tramite protocollo MQTT (per evitare di fare Polling inutile).
  3. SCI invierà un pacchetto di rete a tutte le antenne.
  4. Le antenne invieranno in Broadcast il pacchetto Bluethooth a tutti gli orologi.
  5. Gli orologi non interessati scarteranno il pacchetto. Quello interessato, invece, disattiverà l'allerta.

### 3. Gestione Coda ESP e Deduplicazione (SCI)
L'orologio invia un pacchetto Bluetooth alle antenne ogni minuto con i dati attuali del paziente. Per evitare la saturazione della rete dovuta all'invio duplicato da parte di più antenne ESP che capta lo stesso segnale:

- **Coda sul nodo ESP**:
  - Ogni ESP gestisce una queue interna per le richieste multiple.
  - Se la coda è vuota, invia direttamente il pacchetto; in caso contrario, lo accoda.
- **Sistema Centralizzato Intelligente (SCI)**:
  1. **Checksum**: L'ESP appende al pacchetto un Checksum calcolato su `ID Orologio` + `Dati del paziente` (BPM, ecc.).
  2. **Verifica Duplicati**: Il SCI riceve il pacchetto e controlla la propria tabella interna:
     - **Checksum uguale (dati non variati)**: Il pacchetto viene scartato, ma viene aggiornato il campo `TIMESTAMP`.
     - **Checksum diverso (nuovi dati)**: Rimuove il vecchio pacchetto, salva il nuovo e lo inoltra al Server principale.
  3. **Watchdog Disconnessione**: La tabella sul SCI è ordinata per `ID Orologio`. Se non giungono pacchetti da uno specifico ID per più di $N$ minuti (verificato tramite il `TIMESTAMP`), il SCI invia una notifica al Server per segnalare la potenziale disconnessione del dispositivo.

### 4. Aggiunta di nuova antenna ESP
Il firmware dell'ESP hosterà una piccola rete Wi-Fi per ciascuna antenna. Collegandosi ad essa è possibile accedere ad una piccola interfaccia WEB dove sarà possibile scegliere l'SSID della rete Wi-Fi del luogo, la sua Password e il nome dell'antenna (per mostrare all'operatore la posizione approssimativa del paziente all'interno della struttura)

 ---
 Manzoni Simone e Migliaro Gabriele