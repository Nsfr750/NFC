.. _contribuire:

Contribuire a Lettore/Scrittore NFC
=================================

Grazie per il tuo interesse a contribuire al progetto Lettore/Scrittore NFC! Siamo aperti a tutti i tipi di contributi, inclusi segnalazioni di bug, richieste di funzionalità, miglioramenti alla documentazione e contributi al codice.

Come Contribuire
---------------

1. **Effettua un Fork del Repository**
   - Clicca sul pulsante "Fork" nella `pagina del repository GitHub <https://github.com/Nsfr750/NFC>`_
   - Clona il tuo repository forkato sulla tua macchina locale

2. **Configura l'Ambiente di Sviluppo**
   - Crea un ambiente virtuale:
     ```bash
     python -m venv venv
     source venv/bin/activate  # Su Windows: venv\Scripts\activate
     ```
   - Installa le dipendenze di sviluppo:
     ```bash
     pip install -r requirements-dev.txt
     ```

3. **Crea un Branch**
   - Crea un nuovo branch per le tue modifiche:
     ```bash
     git checkout -b feature/nome-della-tua-funzionalita
     ```

4. **Apporta le Tue Modifiche**
   - Segui le linee guida di stile del codice (PEP 8)
   - Scrivi test per le nuove funzionalità
   - Aggiorna la documentazione se necessario

5. **Testa le Tue Modifiche**
   - Esegui la suite di test:
     ```bash
     pytest
     ```
   - Assicurati che tutti i test passino

6. **Esegui il Commit delle Tue Modifiche**
   - Scrivi messaggi di commit chiari e concisi
   - Riferisci eventuali issue correlate nei tuoi messaggi di commit

7. **Esegui il Push e Crea una Pull Request**
   - Invia le tue modifiche al tuo repository forkato
   - Apri una pull request verso il branch `main` del repository principale
   - Compila il modello della pull request con i dettagli delle tue modifiche

Linee Guida per il Codice
-----------------------

- Segui la guida di stile `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_
- Usa i type hint per tutto il nuovo codice
- Scrivi le docstring seguendo lo stile `Google Style Python Docstrings <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_
- Mantieni le funzioni piccole e focalizzate su un singolo compito
- Usa nomi significativi per variabili e funzioni

Segnalare Bug
------------

Hai trovato un bug? Segnalalo creando una nuova issue nella nostra `pagina delle issue di GitHub <https://github.com/Nsfr750/NFC/issues>`_. Includi:

1. Una descrizione chiara del problema
2. I passaggi per riprodurre il problema
3. Il comportamento atteso
4. Il comportamento effettivo
5. Screenshot o messaggi di errore, se applicabile

Richieste di Funzionalità
------------------------

Hai un'idea per una nuova funzionalità? Saremmo felici di ascoltarti! Crea una nuova issue nella nostra `pagina delle issue di GitHub <https://github.com/Nsfr750/NFC/issues>`_ con:

1. Una descrizione chiara della funzionalità
2. Il problema che risolve
3. Eventuali idee per l'implementazione

Codice di Condotta
-----------------

Ci impegniamo a promuovere una comunità accogliente e inclusiva. Partecipando a questo progetto, accetti di rispettare il nostro `Codice di Condotta <https://github.com/Nsfr750/NFC/CODE_OF_CONDUCT.md>`_.

Licenza
-------

Contribuendo a Lettore/Scrittore NFC, accetti che i tuoi contributi saranno concessi in licenza secondo i termini della `GNU General Public License v3.0 <https://www.gnu.org/licenses/gpl-3.0.html>`_.

Grazie!
------

Apprezziamo il tuo tempo e il tuo impegno nel migliorare Lettore/Scrittore NFC per tutti! I tuoi contributi aiutano a migliorare lo strumento per gli utenti di tutto il mondo.
