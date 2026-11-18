# Protocolli

Questo file descrive in maniera dettagliata tutti i protocolli da stabilire e implementare per le comunicazioni BLE, WiFi e WebSocket.

---

È disponibile una [overview](./PACKET_TYPES.md) sintetica dei protocolli implementati.

---
### Contenuti della pagina
- [1. Protocolli comunicazione ESP32 e Orologio](#1-protocolli-comunicazione-esp32-e-orologio)
  - [Generale](#generale)
  - [1.1 Nuovo Orologio nella rete](#11-nuovo-orologio-nella-rete)
  - [1.2 Invio periodico dei dati](#12-invio-periodico-dei-dati)
      - [1.2.1 Emergency Call](#12-invio-periodico-dei-dati)
      - [1.2.2 Fall](#12-invio-periodico-dei-dati)
  - [1.3 Aggiornamento da remoto](#13-aggiornamento-da-remoto)
      - [1.3.1 Orologio](#13-aggiornamento-da-remoto)
- [2. Protocolli comunicazione ESP32 e SCI](#2-protocolli-comunicazione-esp32-e-sci)
- [3. Protocolli comunicazione SCI e Server](#3-protocolli-comunicazione-sci-e-server)
  - [3.1 Nuovo orologio sulla rete](#31-nuovo-orologio-sulla-rete)
      - [3.1.1 Nuovo orologio sulla rete - Creazione](#311-nuovo-orologio-sulla-rete---creazione)
      - [3.1.2 Nuovo orologio sulla rete - Connessione](#312-nuovo-orologio-sulla-rete---connessione)
  - [3.2 Invio periodico dei dati](#32-invio-periodico-dei-dati)
      - [3.2.1 Invio periodico dei dati - Paziente stabile](#321-invio-periodico-dei-dati---paziente-stabile)
      - [3.2.1 Invio periodico dei dati - Emergenza](#322-invio-periodico-dei-dati---emergenza)

---

## 1. Protocolli comunicazione ESP32 e Orologio

### Generale
Tutti i pacchetti inviati seguiranno questo schema di `Byte`:
- Byte 0: Identifica il tipo di pacchetto (fino a 2^8 = 256 tipi diversi di pacchetti).
> Importante: il tipo del Byte 0 sarà `UNSIGNED` (solo numeri positivi).
- Byte 1: `UID` (`UNSIGNED`) dell'orologio.
- Byte 2 - 21: Payload effettivo del pacchetto.
- Byte 22 - 23: Garbage, usato come spazio per la generazione casuale della stringa.

### 1.1 Nuovo Orologio nella rete
Quando un nuovo orologio verrà acceso verificherà se è presente in `/usr/share/watch_agent/data/` il file `device_uid.env`.
Questo file conterrà l'`UID` (valore `UNSIGNED`) che lo indentifica univocamente nella rete.  
Verrà, infatti, salvata sullo *SCI* l'associazione *Mac-Address orologio -- `UID` `(UNSIGNED)`*.  
Dal momento in cui l'orologio ha salvato sul filesystem il proprio UID userà quello per identificarsi sulla rete.

##### Specifiche - Orologio
L'orologio manderà un pacchetto BLE contenente il seguente payload:
- Byte 0: `0` `UNSIGNED`
- Byte 1 - 6: Mac-Address dell'orologio
- Byte 7 - 23: Vuoto/Garbage/Necessità future

##### Specifiche - ESP32
L'ESP32 dovrà mandare il pacchetto allo *SCI*, il quale risponderà con `Mac-Address` salvato + `UID` generato.
A questo punto l'ESP32 dovrà inviare il seguente pacchetto:
- Byte 0: `1` `UNSIGNED`
- Byte 1 - 6: Mac-Address dell'orologio
- Byte 7: `UID` `UNSIGNED`
- Byte 8 - 23: Vuoto/Garbage/Necessità future

> Nota: scriviamo `1` `UNSIGNED` al Byte 0 per semplificare il lavoro dell'orologio/ESP32. `0` è l'invio di richiesta, `1` la ricezione.  
È necessario perchè altrimenti l'ESP non saprebbe decidere con certezza se il pacchetto arrivatogli sia una richiesta o già una risposta. (Ovviamente nel caso in cui l'ESP ricevi un pacchetto bluethooth di risposta da un altro ESP)


### 1.2 Invio periodico dei dati
I pacchetti verranno spediti dall'orologio all'ESP32 con un rate di 1 per minuto.

##### Specifiche - Orologio
L'orologio manderà un pacchetto BLE contenente il seguente payload: 
- Byte 0: `10` `UNSIGNED`
- Byte 1: `UID` `UNSIGNED`
- Byte 2: HeartRate `UNSIGNED`
- Byte 3: Battery `UNSIGNED`
- Byte 4 e 5: Steps `UNSIGNED`
- Byte 6: Emergency Call `UNSIGNED/BOOLEAN`
- Byte 7: Fall `UNSIGNED/BOOLEAN`
- Byte 8 - 23: Vuoto/Garbage/Necessità future

> Nota: si protrebbe pensare addirittura di unificare il Byte 5 e 6 poichè le informazioni occupano solo 1 bit (non 4). Sarebbe molto più complicato gestire la situazione lato software. Lascio l'idea solo perchè in futuro magari ci potrebbe servire più spazio.


#### 1.2.1 Invio periodico dei dati - Emergency Call
Se il Byte 5 (Emergency Call) è positivo (1) allora verrà seguito questo iter:
1. l'ESP lo notificherà allo *SCI*
2. Lo *SCI* lo notificherà al *Server*
3. Verrà inviata una notifica PUSH agli operatori e verrà mostrato un alert sulla Dashboard.
4. Alla pressione (eseguita da un operatore) del tasto "Ferma emergenza" presente sulla Dashboard il *SERVER* notificherà allo *SCI* che l'emergenza sull' `UID` orologio si è conclusa.
5. Lo *SCI* manderà in broadcast agli ESP32 il pacchetto (da definire).
6. Gli ESP32 invieranno in broadcast il seguente pacchetto:
- Byte 0: `11` `UNSIGNED`
- Byte 1: `UID` `UNSIGNED`
- Byte 2 - 23: Vuoto/Garbage/Necessità future

> Nota: si potrebbe pensare di inviare dall'orologio pacchetti con il payload definiti al punto 1.2 più frequentemente in regime di allerta. Questo servirebbe per far terminare l'emergenza anche nel caso in cui il pacchetto di tipo `11` venga perso o non ricevuto dall'orologio.  
In questo caso allora sarebbe utile definire un algortimo di identificazione univoca anche delle emergenze (anche uno molto semplice, magari con un contatore sull'orologio che aumenta di uno ad ogni emergenza chiamata e che non aumenti fino a quando non viene ricevuto il pacchetto di tipo `11` dall'orologio) per non far arrivare notifiche doppie all'operatore.  
A questo punto basterebbe aggiungere nel pacchetto precedente (1.2) al Byte 7 l'ID dell'emergenza.

> Nota: Dovremmo anche lasciare aperta la possibilità di annullare o fermare l'emergenza premendo il tasto dell'orologio per un determinato tempo.

#### 1.2.2 Invio periodico dei dati - Fall
Se il Byte 6 (Fall) è positivo (1) allora verrà seguito questo iter:

*Identico a quello descritto in 1.2.1*

> Nota: Lascio la sezione perchè è importante sottolineare che si può seguire lo stesso iter sicuramente nella comunicazione ESP32-Orologio (alla fine la caduta resta sempre un'emergenza e lato Orologio/ESP non ci interessa sapere di quale si tratti [Generica o Caduta]).  
Sarà, invece, da decidere come affrontare il problema durante la trasmissione *SCI-Server*: lo *SCI* invierà semplicemente tutto il pacchetto con il payload al *Server* e sarà quest'ultimo a decidere quale emergenza è in atto, o decideremo di inviare dallo *SCI* due tipi di pacchetti differenti per notificare il *Server* dell'emergenza?

### 1.3 Aggiornamento da remoto
#### 1.3.1 Aggiornamento da remoto - Orologio
L'orologio, una volta al giorno, invierà il pacchetto di tipo `2` in broadcast BLE, strutturato come segue:
- Byte 0: `2` `UNSIGNED`
- Byte 1: `UID` `UNSIGNED`
- Byte 2 - 23: Vuoto/Garbage/Necessità future

#### 1.3.2 Aggiornamento da remoto - ESP32
L'ESP32 chiederà allo SCI se è presente un nuovo aggiornamento e risponderà con un pacchetto di tipo `3` come segue:
- Byte 0: `3` `UNSIGNED`
- Byte 1: `UID` `UNSIGNED`
- Byte 2: `CAN_UPDATE` `BOOLEAN`
- Byte 3 - 23: Vuoto/Garbage/Necessità future

Se `CAN_UPDATE` è `True` allora l'orologio si collegherà al Wi-Fi e scaricherà dall'endpoint l'aggiornamento seguendo la procedura spiegata nel [README](./watch_agent/README.md#aggiornamento-remoto).

#### 1.3.3 Aggiornamento da remoto - Orologio | Credenziali errate/mancanti
Se le credenziali della rete Wi-Fi sull'orologio non sono corrette (dopo un aggiornamento di queste ultime oppure perchè è semplicemente il suo primo tentativo di connessione ad Internet) succederà come segue:
L'orologio manderà un pacchetto di tipo `4` strutturato come segue:
- Byte 0: `4` `UNSIGNED`
- Byte 1: `UID` `UNSIGNED`
- Byte 2 - 23: Vuoto/Garbage/Necessità future

#### 1.3.4 Aggiornamento da remoto - ESP32 | Credenziali errate/mancanti
L'ESP32, ricevuto il pacchetto di tipo `4` risponderà con due pacchetti (tipo `5` e `6`) così strutturati:
Pacchetto di tipo `5`:
- Byte 0: `5` `UNSIGNED`
- Byte 1: `UID` `UNSIGNED`
- Byte 2 - 23: SSID rete Wi-Fi

Pacchetto di tipo `6`:
- Byte 0: `6` `UNSIGNED`
- Byte 1: `UID` `UNSIGNED`
- Byte 2 - 23: Password rete Wi-Fi

A questo punto l'orologio salverà le informazioni su un file, si collegherà al Wi-Fi e scaricherà dall'endpoint l'aggiornamento seguendo la procedura spiegata nel [README](./watch_agent/README.md#aggiornamento-remoto).



## 2. Protocolli comunicazione ESP32 e SCI
L'ESP32, in generale, quando riceve un pacchetto dall'orologio lo accoda e lo manda (via UART) alla scheda che gestisce il protocollo TCP. Essa sì limiterà ad inviare dei pacchetti con lo stesso contenuto di quelli ricevuti, avendo come unica accortezza quella di aggiungere l'identificativo dell'antenna (il suo nome, scelto in fase di configurazione) e l'RSSI dell'orologio (potenza in ingresso).



## 3. Protocolli comunicazione SCI e Server
Lo SCI e il Server comunicheranno tra loro solo per i pacchetti di tipo `0`, `1`, `10` e `11`.
I due comunicheranno tramite WebSocket per garantire una connessione bilaterale.
Il canale è protetto in due modi:
1. Dashboard - Server: viene sfruttato il JWT che autentica la sessione del browser.
2. SCI - Server: i due condividono la stessa chiave privata dalla quale, tramite la libreria PyOtp, viene generata una chiave simmetrica (uguale
per entrambe le controparti) che autentica una sessione di 30 secondi.

> Lo `SCI` si limiterà a prendere il pacchetto ricevuto in ingresso dall'ESP32 e pubblicarlo sul WebSocket.

### 3.1 Nuovo orologio sulla rete
#### 3.1.1 Nuovo orologio sulla rete - Creazione
Lo SCI riceve dagli ESP32 il pacchetto di tipo `0` e lo pubblicherà sul WebSocket.
Il Server creerà un record della tabella `DEVICES` con `STATUS = PENDING` e risponderà con il seguente JSON allo SCI tramite il WebSocket:
```json
{"event": "NEW_DEVICE", "payload": saved_device}
```
Dove `saved_device` è un dizionario con tutte le informazioni salvate sul Database (tra cui il MacAddress dell'orologio).

#### 3.1.2 Nuovo orologio sulla rete - Connessione
Quando un operatore deciderà di collegare un dispositivo sulla rete il Server pubblicherà questo messaggio JSON sul WebSocket:
```json
{
"event": "DEVICE_CONNECTED",
"payload": {
             device_id: deviceId,
             mac_address: deviceMacAddress
           }
}
```
A questo punto lo SCI dovrà notificare l'orologio (passando dalle antenne ESP32) il suo deviceId (UID).

### 3.2 Invio periodico dei dati
Lo SCI riceve dagli ESP32 il pacchetto di tipo `10` e lo pubblicherà sul WebSocket.

#### 3.2.1 Invio periodico dei dati - Paziente stabile
Il Server aggiornerà le informazioni presenti sulla dashbord tramite l'UID dell'orologio e l'assiociazione tra esso ed un paziente precedentemente creato. Nessun dato viene salvato sul Database ma solo nel LocalStorage.
Il Server risponderà con il seguente messaggio:
```json
{
"event": "DEVICE_UPDATE",
"payload": {
        device_id: deviceId,
        ... -> Informazioni contenute nel pacchetto
    }
}
```
Quest'ultimo non serve tanto allo SCI, bensì alla Dashboard: in questo modo sà quando aggiornarsi con sicurezza sapendo che non si sono verificare emergenze.

#### 3.2.2 Invio periodico dei dati - Emergenza
In risposta a qualsiasi emergenza il Server risponderà con un messaggio del tipo: 
```json
{
    "event":"NEW_EMERGENCY",
    "payload": {
        "id": deviceId,
        "p_id": patientId,
        "bpm": patientBpm,
        "type": emergency_type,
        "resolved": false,
        "created_at": date,
        "resolved_at":null,
        "resolved_by":null,
        "patient":{
            "id": patientId,
            "name": patientName,
            "surname": patientSurname
        }
    }
}
```

Ci sono 4 tipi di emergenze: 
1. Battiti troppo alti
2. Battiti troppo bassi
3. Caduta rilevata
4. Emergenza generica

Le prime due (Battiti alti e bassi) sono gestite lato Server: quando viene letto il messaggio di tipo `10` valuterà se i battiti sono più alti (o bassi) di una certa soglia. Se sì, salverà nel Database la nuova emergenza e pubblicherà il messaggio sul WebSocket.
  
Per gli ultimi due tipi (Caduta rilevata e Emergenza generica) invece il Server si limiterà a guardare lo stato dei byte `6` e `7`.
Se uno dei due è positivo (== 1) allora salverà l'emergenza sul Database e pubblicherà il messaggio sul WebSocket.

> Lo SCI avrà premura di verificare prima dell'invio del messaggio di tipo `10` sul WebSocket di verificare se entrambi i byte `6` e `7` sono positivi (== 1). Se sì imporrà a zero il byte `6` poichè è l'emergenza meno grave (Caduta rilevata >> Supporto generico).