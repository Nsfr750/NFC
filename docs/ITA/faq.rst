.. _domande-frequenti:

Domande Frequenti
================

Generale
--------

Quali tipi di tag NFC sono supportati?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
L'applicazione supporta tutti i principali tipi di tag NFC tra cui:

- NTAG (NTAG213, NTAG215, NTAG216)
- MIFARE Classic (1K, 4K)
- MIFARE Ultralight
- FeliCa
- ISO 14443 Tipo A e B
- ISO 15693

C'è un limite al numero di tag che posso memorizzare nel database?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
No, non c'è un limite massimo al numero di tag che puoi memorizzare. Il database crescerà secondo necessità.

Posso utilizzare più lettori NFC contemporaneamente?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sì, l'applicazione supporta più lettori. Puoi selezionare il lettore attivo dal menu delle impostazioni.

Utilizzo
--------

Come faccio a sapere se il mio lettore NFC è correttamente connesso?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
La barra di stato nella parte inferiore dell'applicazione mostrerà lo stato della connessione. Un indicatore verde significa che il lettore è connesso e pronto.

Perché non riesco a scrivere sul mio tag NFC?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Potrebbero esserci diverse ragioni:

1. Il tag potrebbe essere di sola lettura o bloccato
2. Il tag potrebbe essere pieno
3. Il tag potrebbe non supportare l'operazione di scrittura che stai tentando di eseguire

Controlla le specifiche del tag e assicurati che non sia protetto da scrittura.

Posso usare questa applicazione per clonare carte NFC?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
L'applicazione può leggere e scrivere dati su tag compatibili, ma alcune funzionalità di sicurezza (come quelle utilizzate nelle carte di credito) non possono essere clonate a causa di crittografia e altre misure di sicurezza.

Tecnico
-------

In quale linguaggio di programmazione è scritta questa applicazione?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
L'applicazione è scritta in Python, con un'interfaccia grafica basata su Qt.

Il codice sorgente è disponibile?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sì, l'applicazione è open source e disponibile su `GitHub <https://github.com/Nsfr750/NFC>`_.

Come posso contribuire al progetto?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Puoi contribuire:

1. Segnalando bug o suggerendo funzionalità nel `tracciamento dei problemi <https://github.com/Nsfr750/NFC/issues>`_
2. Inviando pull request con miglioramenti
3. Migliorando la documentazione
4. Traducendo l'applicazione in altre lingue

Risoluzione dei Problemi
-----------------------

Il mio lettore NFC non viene rilevato
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Assicurati che il lettore sia correttamente connesso al computer
2. Controlla se i driver sono installati correttamente
3. Prova una diversa porta USB
4. Riavvia l'applicazione

L'applicazione si blocca durante la lettura di un tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Segnala questo problema nella nostra `pagina delle issue di GitHub <https://github.com/Nsfr750/NFC/issues>`_ con le seguenti informazioni:

1. Il tipo di tag che stavi cercando di leggere
2. Il messaggio di errore (se presente)
3. La versione dell'applicazione
4. La versione del tuo sistema operativo

L'applicazione è lenta durante la lettura di più tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Prova queste ottimizzazioni:
1. Chiudi altre applicazioni che utilizzano il lettore NFC
2. Riduci il ritardo di lettura nelle impostazioni
3. Aggiorna all'ultima versione dell'applicazione

Per ulteriore aiuto, consulta la guida alla :ref:`risoluzione-problemi`.
