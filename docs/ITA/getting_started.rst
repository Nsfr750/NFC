.. _getting-started:

Guida Introduttiva
=================

Questa guida ti aiuterà a iniziare rapidamente con l'applicazione Lettore/Scrittore NFC.

Installazione
------------

Prerequisiti
~~~~~~~~~~~
- Python 3.8 o superiore
- pip (gestore pacchetti Python)
- Hardware lettore NFC
- Librerie di sistema richieste (vedi :ref:`prerequisiti`)

Installazione su Windows
~~~~~~~~~~~~~~~~~~~~~~~

1. Scarica l'ultima versione dalla `pagina delle release di GitHub <https://github.com/Nsfr750/NFC/releases>`_
2. Estrai il file ZIP nella cartella preferita
3. Esegui ``nfc-reader-writer.exe`` dalla cartella estratta

Installazione su Linux
~~~~~~~~~~~~~~~~~~~~~

1. Scarica l'ultima versione dalla `pagina delle release di GitHub <https://github.com/Nsfr750/NFC/releases>`_
2. Estrai l'archivio:
   .. code-block:: bash

      tar -xzf nfc-reader-writer-linux-x86_64.tar.gz

3. Avvia l'applicazione:
   .. code-block:: bash

      cd nfc-reader-writer-linux-x86_64
      ./nfc-reader-writer

Primo Avvio
-----------

1. Collega il tuo lettore NFC al computer
2. Avvia l'applicazione Lettore/Scrittore NFC
3. L'applicazione rileverà automaticamente il lettore NFC
4. Avvicina un tag NFC al lettore per iniziare la lettura

Utilizzo Base
-------------

Lettura di un Tag
~~~~~~~~~~~~~~~~
1. Fai clic sul pulsante "Leggi Tag" o premi ``Ctrl+R``
2. Avvicina il tuo tag NFC al lettore
3. I dati del tag verranno visualizzati nella finestra principale

Scrittura su un Tag
~~~~~~~~~~~~~~~~~~
1. Fai clic sul pulsante "Scrivi" o premi ``Ctrl+W``
2. Inserisci i dati da scrivere
3. Seleziona le opzioni di scrittura
4. Avvicina il tuo tag NFC al lettore
5. Fai clic su "Inizia Scrittura"

Salvataggio Dati del Tag
~~~~~~~~~~~~~~~~~~~~~~
1. Leggi un tag
2. Fai clic sul pulsante "Salva" o premi ``Ctrl+S``
3. Scegli una posizione e un nome file
4. Fai clic su "Salva"

Prossimi Passi
-------------
- Scopri di più sulle :ref:`funzionalità-avanzate`
- Consulta la :ref:`guida-utente` per istruzioni dettagliate
- Visita la guida :ref:`risoluzione-problemi` se riscontri problemi
