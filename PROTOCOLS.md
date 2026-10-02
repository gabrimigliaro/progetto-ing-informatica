# Protocolli

Questo file descrive in maniera dettagliata tutti i protocolli da stabilire e implementare per le comunicazioni BLE, WiFi e MQTT.

**IN FASE DI AGGIORNAMENTO**

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

---

## 1. Protocolli comunicazione ESP32 e Orologio

### Generale
Tutti i pacchetti inviati seguiranno questo schema di `Byte`:
- Byte 0: Identifica il tipo di pacchetto (fino a 2^8 = 256 tipi diversi di pacchetti).
> Importante: il tipo del Byte 0 sarà `UNSIGNED` (solo numeri positivi).
- Byte 1: `UID` (`UNSIGNED`) dell'orologio.
- Byte 2 - 26: Payload effettivo del pacchetto.
- Byte 27 - 32: Garbage, usato come spazio per la generazione casuale della stringa.

### 1.1 Nuovo Orologio nella rete
Quando un nuovo orologio verrà acceso verificherà se è presente in `/usr/share/watch_agent/data/` il file `device_uid.env`.
Questo file conterrà l'`UID` (valore `UNSIGNED`) che lo indentifica univocamente nella rete.  
Verrà, infatti, salvata sullo *SCI* l'associazione *Mac-Address orologio -- `UID` `(UNSIGNED)`*.  
Dal momento in cui l'orologio ha salvato sul filesystem il proprio UID userà quello per identificarsi sulla rete.

##### Specifiche - Orologio
L'orologio manderà un pacchetto BLE contenente il seguente payload:
- Byte 0: `0` `UNSIGNED`
- Byte 1 - 6: Mac-Address dell'orologio
- Byte 7 - 26: Vuoto/Garbage/Necessità future

##### Specifiche - ESP32
L'ESP32 dovrà mandare il pacchetto allo *SCI*, il quale risponderà con `Mac-Address` salvato + `UID` generato.
A questo punto l'ESP32 dovrà inviare il seguente pacchetto:
- Byte 0: `1` `UNSIGNED`
- Byte 1 - 6: Mac-Address dell'orologio
- Byte 7: `UID` `UNSIGNED`
- Byte 8 - 26: Vuoto/Garbage/Necessità future

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
- Byte 4: Steps `UNSIGNED`
- Byte 5: Emergency Call `UNSIGNED/BOOLEAN`
- Byte 6: Fall `UNSIGNED/BOOLEAN`
- Byte 7 - 26: Vuoto/Garbage/Necessità future

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
- Byte 2 - 26: Vuoto/Garbage/Necessità future

> Nota: si potrebbe pensare di inviare dall'orologio pacchetti con il payload definiti al punto 1.2 più frequentemente in regime di allerta. Questo servirebbe per far terminare l'emergenza anche nel caso in cui il pacchetto di tipo `11` venga perso o non ricevuto dall'orologio.  
In questo caso allora sarebbe utile definire un algortimo di identificazione univoca anche delle emergenze (anche uno molto semplice, magari con un contatore sull'orologio che aumenta di uno ad ogni emergenza chiamata e che non aumenti fino a quando non viene ricevuto il pacchetto di tipo `11` dall'orologio) per non far arrivare notifiche doppie all'operatore.  
A questo punto basterebbe aggiungere nel pacchetto precedente (1.2) al Byte 7 l'ID dell'emergenza.

> Nota: Dovremmo anche lasciare aperta la possibilità di annullare o fermare l'emergenza premendo il tasto dell'orologio per un determinato tempo.

#### 1.2.2 Invio periodico dei dati - Fall
Se il Byte 6 (Fall) è positivo (1) allora verrà seguito questo iter:

*Identico a quello descritto in 1.2.1*

> Nota: Lascio la sezione perchè è importante sottolineare che si può seguire lo stesso iter sicuramente nella comunicazione ESP32-Orologio (alla fine la caduta resta sempre un'emergenza e lato Orologio/ESP non ci interessa sapere di quale si tratti [Generica o Caduta]).  
Sarà, invece, da decidere come affrontare il problema durante la trasmissione *SCI-Server*: lo *SCI* invierà semplicemente tutto il pacchetto con il payload al *Server* e sarà quest'ultimo a decidere quale emergenza è in atto, o decideremo di inviare dallo *SCI* due tipi di pacchetti differenti per notificare il *Server* dell'emergenza?