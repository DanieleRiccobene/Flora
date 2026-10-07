# Riferimento floristico, non immagini di training

I file `sicilia_*_2023.*` sono estratti dalla Checklist FlorItaly 27 aprile 2023 distribuita in `gibedini/floritaly`, commit `6c4c7b08dc167a943907b2249b0a6b9684096f1d`.

Autori del pacchetto: Gianni Bedini e Matteo Conti. Fonte botanica: [FlorItaly](https://dryades.units.it/floritaly/). La licenza MIT del repository sorgente è conservata in `FLORITALY_LICENSE.md`.

- `sicilia_species_reference_2023.json`: 2.916 nomi a livello di specie, inclusi ibridi con nome; sottospecie/varietà aggregate.
- `sicilia_taxa_reference_2023.csv`: righe regionali e corrispondenza con la classe a livello di specie.
- `sicilia_unparsed_reference_2023.csv`: cinque record di sezioni di Taraxacum, che non sono specie e non diventano classi.
- `sicilia_ambiguous_names_2023.csv`: nomi non abbinati automaticamente perché riferibili a più classi.
- `sicilia_reference_provenance.json`: fonte, versione, checksum, criteri e conteggi.

Sono selezionate le presenze `P` nella colonna `SIC`, inclusi codici parentali `(P)`, aliene naturalizzate, invasive e casuali. Assenza, estinzione, presenze dubbie e vecchie segnalazioni non confermate non sono incluse. Questa non è una checklist aggiornata al 2026 e non è l'elenco di tutte le piante coltivate nei giardini siciliani. Le classi effettivamente allenabili dipendono dal CSV dell'utente e sono prodotte dal notebook v3.
