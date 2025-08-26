.. _guida-utente:

Guida Utente
===========

Questa guida fornisce informazioni dettagliate sull'utilizzo dell'applicazione Lettore/Scrittore NFC.

Panoramica dell'Interfaccia
--------------------------

.. image:: ../images/interface_overview.png
   :alt: Interfaccia Lettore/Scrittore NFC
   :align: center

1. **Barra dei Menu**: Accesso a tutte le funzioni dell'applicazione
2. **Barra degli strumenti**: Accesso rapido alle funzioni comuni
3. **Pannello Informazioni Tag**: Visualizza i dettagli del tag
4. **Visualizzazione Dati**: Mostra i dati del tag in vari formati
5. **Barra di stato**: Mostra lo stato della connessione e i messaggi

Lettura dei Tag
--------------

Lettura Manuale
~~~~~~~~~~~~~~
1. Fai clic sul pulsante "Leggi" nella barra degli strumenti o premi ``Ctrl+R``
2. L'applicazione leggerà il tag e ne visualizzerà i dati

Lettura Automatica
~~~~~~~~~~~~~~~~~
1. Attiva la modalità "Lettura Automatica" dal menu Impostazioni
2. L'applicazione leggerà automaticamente i tag quando rilevati

Scrittura sui Tag
----------------

Scrittura di Testo
~~~~~~~~~~~~~~~~
1. Seleziona la scheda "Scrivi"
2. Scegli "Testo" come tipo di contenuto
3. Inserisci il testo nell'editor
4. Fai clic su "Scrivi" e segui le istruzioni a schermo

Scrittura di URL
~~~~~~~~~~~~~~~
1. Seleziona la scheda "Scrivi"
2. Scegli "URL" come tipo di contenuto
3. Inserisci l'URL
4. Fai clic su "Scrivi" e segui le istruzioni a schermo

Scrittura di Informazioni di Contatto
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Seleziona la scheda "Scrivi"
2. Scegli "vCard" come tipo di contenuto
3. Inserisci i dettagli del contatto
4. Fai clic su "Scrivi" e segui le istruzioni a schermo

Gestione del Database dei Tag
---------------------------

Salvataggio dei Tag
~~~~~~~~~~~~~~~~~~
1. Leggi un tag
2. Fai clic su "Salva nel Database"
3. Inserisci un nome e una descrizione opzionale
4. Fai clic su "Salva"

Ricerca dei Tag
~~~~~~~~~~~~~~
1. Apri la visualizzazione Database
2. Utilizza la barra di ricerca per trovare tag specifici
3. Fai clic su un tag per visualizzarne i dettagli

Funzionalità Avanzate
-------------------

Emulazione Tag
~~~~~~~~~~~~~
1. Attiva "Emulazione Tag" dal menu Strumenti
2. Configura le impostazioni di emulazione
3. L'applicazione si comporterà come un tag NFC

Elaborazione in Batch
~~~~~~~~~~~~~~~~~~~
1. Seleziona "Modalità Batch" dal menu Strumenti
2. Configura le operazioni di lettura/scrittura
3. Elabora più tag in sequenza

Risoluzione dei Problemi
----------------------

Problemi Comuni
~~~~~~~~~~~~~~
- **Tag non rilevato**: Assicurati che il tag sia posizionato correttamente sul lettore
- **Scrittura fallita**: Verifica se il tag è protetto da scrittura
- **Connessione persa**: Controlla che il lettore sia correttamente connesso

Per ulteriore aiuto, consulta la guida alla :ref:`risoluzione-problemi`.

Scorciatoie da Tastiera
---------------------

+----------------+--------------------------+
| Scorciatoia   | Azione                  |
+================+==========================+
| ``Ctrl+N``    | Nuovo Progetto          |
+----------------+--------------------------+
| ``Ctrl+O``    | Apri Progetto           |
+----------------+--------------------------+
| ``Ctrl+S``    | Salva Dati Tag          |
+----------------+--------------------------+
| ``Ctrl+R``    | Leggi Tag               |
+----------------+--------------------------+
| ``Ctrl+W``    | Scrivi sul Tag          |
+----------------+--------------------------+
| ``F1``        | Guida                   |
+----------------+--------------------------+
