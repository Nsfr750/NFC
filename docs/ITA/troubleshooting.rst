.. _risoluzione-problemi:

Guida alla Risoluzione dei Problemi
================================

Questa guida ti aiuta a risolvere i problemi comuni che potresti incontrare utilizzando l'applicazione Lettore/Scrittore NFC.

Problemi di Connessione
----------------------

Lettore NFC Non Rilevato
~~~~~~~~~~~~~~~~~~~~~~~
**Sintomi:**
- L'applicazione mostra "Nessun lettore connesso"
- Il lettore non è elencato nel menu dei dispositivi

**Soluzioni:**
1. **Controlla le connessioni fisiche:**
   - Assicurati che il lettore sia correttamente connesso al computer
   - Prova una diversa porta USB
   - Se usi un hub USB, collega direttamente al computer

2. **Verifica i driver:**
   - Windows: controlla il Gestione dispositivi per eventuali punti esclamativi gialli
   - Linux: assicurati di avere i permessi necessari (aggiungi il tuo utente al gruppo `plugdev`)
   - Prova a reinstallare i driver del lettore

3. **Riavvia i servizi:**
   - Riavvia il servizio PC/SC:
     ```bash
     sudo systemctl restart pcscd  # Linux
     net stop "Smart Card" && net start "Smart Card"  # Windows
     ```

4. **Prova con altro software:**
   - Prova a utilizzare il lettore con altro software NFC per isolare il problema

Problemi di Lettura Tag
----------------------

Tag Non Rilevato
~~~~~~~~~~~~~~~
**Sintomi:**
- Il lettore è rilevato ma non riconosce i tag
- Appare il messaggio "Nessun tag trovato"

**Soluzioni:**
1. **Controlla la posizione del tag:**
   - Assicurati che il tag sia correttamente allineato con l'antenna del lettore
   - Muovi il tag per trovare la posizione ottimale

2. **Prova un tag diverso:**
   - Prova con più tag per escludere un tag difettoso

3. **Controlla il tipo di tag:**
   - Verifica che il tipo di tag sia supportato dal tuo lettore
   - Alcuni lettori hanno compatibilità limitata con certi tipi di tag

4. **Modifica le impostazioni:**
   - Aumenta il timeout di lettura nelle impostazioni dell'applicazione
   - Prova diverse modalità di lettura se disponibili

Problemi di Scrittura
-------------------

Impossibile Scrivere sul Tag
~~~~~~~~~~~~~~~~~~~~~~~~~~
**Sintomi:**
- L'operazione di scrittura fallisce con un errore
- I dati non vengono salvati sul tag

**Soluzioni:**
1. **Controlla la protezione in scrittura:**
   - Alcuni tag hanno una protezione di scrittura che può essere bloccata
   - Verifica se il tag è di sola lettura

2. **Verifica la capacità del tag:**
   - Assicurati che i dati che stai cercando di scrivere rientrino nella capacità del tag
   - Alcuni tag hanno layout di memoria specifici e aree riservate

3. **Problemi di formattazione:**
   - Prova a formattare il tag prima di scrivere
   - Alcuni tag richiedono una formattazione specifica per certi tipi di dati

4. **Stato del tag:**
   - Il tag potrebbe essere danneggiato o usurato
   - Prova con un tag diverso

Problemi dell'Applicazione
------------------------

Arresti Improvvisi
~~~~~~~~~~~~~~~~
**Sintomi:**
- L'applicazione si chiude inaspettatamente
- Appaiono messaggi di errore prima della chiusura

**Soluzioni:**
1. **Controlla i log:**
   - Cerca i log di errore nella directory dei log dell'applicazione
   - Su Windows: `%APPDATA%\NFC Reader Writer\logs`
   - Su Linux: `~/.local/share/NFC Reader Writer/logs`

2. **Aggiorna l'applicazione:**
   - Assicurati di utilizzare l'ultima versione
   - Controlla gli aggiornamenti nel menu Aiuto

3. **Reimposta le impostazioni:**
   - Prova a ripristinare le impostazioni predefinite dell'applicazione
   - Elimina il file di configurazione (eseguendo prima un backup se necessario)

4. **Verifica i requisiti di sistema:**
   - Assicurati che il tuo sistema soddisfi i requisiti minimi
   - Aggiorna il sistema operativo e i driver

Problemi di Prestazioni
----------------------

Lettura/Scrittura Lenta
~~~~~~~~~~~~~~~~~~~~~
**Sintomi:**
- Le operazioni richiedono più tempo del previsto
- L'applicazione diventa non reattiva durante le operazioni

**Ottimizzazioni:**
1. **Chiudi altre applicazioni:**
   - Altre applicazioni potrebbero utilizzare le risorse di sistema
   - Chiudi i programmi non necessari

2. **Modifica le impostazioni:**
   - Riduci il numero di tentativi di lettura/scrittura
   - Aumenta i timeout se stai riscontrando problemi di timeout

3. **Controlla le interferenze:**
   - Allontanati da fonti di interferenza elettromagnetica
   - Prova in una posizione diversa

4. **Aggiorna il firmware:**
   - Verifica se è disponibile un aggiornamento del firmware per il tuo lettore NFC
   - Aggiorna il firmware del lettore se disponibile

Messaggi di Errore Comuni
------------------------

"Lettore Non Trovato"
~~~~~~~~~~~~~~~~~~~~
- Verifica che il lettore sia correttamente connesso
- Controlla se il lettore è supportato dall'applicazione
- Prova a reinstallare i driver del lettore

"Tag Non Supportato"
~~~~~~~~~~~~~~~~~~~
- Controlla se il tipo di tag è supportato
- Prova un tag diverso
- Alcuni tag potrebbero richiedere configurazioni specifiche

"Memoria Insufficiente"
~~~~~~~~~~~~~~~~~~~~~
- Il tag non ha abbastanza spazio per l'operazione
- Riduci la quantità di dati che stai cercando di scrivere
- Usa un tag con capacità maggiore

Come Ottenere Aiuto
------------------

Se stai ancora riscontrando problemi:

1. **Consulta la sezione** :ref:`domande-frequenti` per ulteriori soluzioni
2. **Cerca nella documentazione** per argomenti specifici
3. **Segnala il problema** sulla nostra `pagina delle issue di GitHub <https://github.com/Nsfr750/NFC/issues>`_
   - Includi il messaggio di errore
   - Descrivi cosa stavi facendo quando si è verificato il problema
   - Allega i file di log rilevanti

Per ulteriore supporto, puoi anche visitare il nostro `server Discord <https://discord.gg/ryqNeuRYjD>`.
