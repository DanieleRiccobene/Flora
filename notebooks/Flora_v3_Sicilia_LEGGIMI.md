# Flora v3: piante spontanee, ornamentali e coltivate

[Apri il notebook in Colab](https://colab.research.google.com/github/DanieleRiccobene/Flora/blob/main/notebooks/Flora_v3_Sicilia_PlantCLEF_Colab.ipynb)

## Risposta sulla copertura

Le 40 classi della prima versione erano una selezione manuale, non l'elenco delle specie di PlantCLEF. Non sono sufficienti a rappresentare la flora siciliana. La release PlantCLEF 2024 dispone di migliaia di classi; l'implementazione pubblica di riferimento citata sotto ne usa 7.806. Il tuo CSV potrebbe essere completo o essere un sottoinsieme: il nuovo notebook lo misura, senza presumerlo.

Per documentare il riferimento regionale abbiamo usato la checklist FlorItaly del 27 aprile 2023 distribuita dal pacchetto `gibedini/floritaly`. Selezionando le presenze nella colonna SIC si ottengono 3.438 record tassonomici; raggruppando sottospecie/varietà a livello di specie e mantenendo gli ibridi con nome si ricavano **2.916 nomi**. Cinque record di sezioni di Taraxacum non sono specie e vengono riportati separatamente. Non sono 3.438 specie distinte, né questo conteggio è una dichiarazione di completezza della flora siciliana attuale.

La checklist copre piante vascolari registrate allo stato spontaneo, incluse le introdotte. Non elenca ogni pianta coltivata in un giardino: il tuo obiettivo richiede quindi un perimetro più ampio. Non esiste una lista chiusa universale delle specie che potrebbero essere coltivate sull'isola.

## Modalità predefinita: Sicilia più tutte le classi utilizzabili di PlantCLEF

`CLASS_SCOPE='sicilia_plus_dataset'` unisce i target regionali alle specie presenti nel CSV, anche quando non risultano nella checklist regionale. Il confronto comprende sinonimi, nomi accettati, sottospecie e nomi con diacritici. Gli abbinamenti ambigui vengono segnalati, non risolti per somiglianza del nome.

Questo produce un catalogo PlantCLEF esteso, non un inventario certificato delle ornamentali siciliane. Le classi extra sono marcate `additional_dataset_species_region_not_verified`: potrebbero essere spontanee altrove, coltivate in Sicilia oppure non presenti localmente. Il modello non applica un prior geografico alle probabilità. Per renderlo più piccolo e specifico servirebbe una lista verificata delle ornamentali effettivamente di interesse.

Con `CLASS_SCOPE='spontaneous_only'` si considerano solo i target del riferimento siciliano. Cambiare modalità richiede un nuovo RUN_ID.

## Prima esecuzione: audit, senza immagini né training

1. Apri il notebook v3, verifica il percorso del tuo CSV e usa il nuovo `RUN_ID='sicilia_v3_01'`.
2. Lascia `TRAINING_ENABLED=False` ed esegui le prime tre celle. Il messaggio `AUDIT COMPLETATO` è uno stop intenzionale, non un errore nei dati.
3. In `MyDrive/Flora_Sicilia_v3/<RUN_ID>/taxonomy/coverage.csv` trovi ogni classe obiettivo e il suo stato:
   - `trainable`: almeno 20 osservazioni distinte con ID e URL utilizzabili;
   - `insufficient_observations`: dati presenti ma insufficienti alla soglia scelta;
   - `no_usable_match`: nessun abbinamento utilizzabile; può dipendere da assenza nel CSV, sinonimia non risolta o metadati incompleti.
4. `sicilia_reference_2023` identifica le classi della checklist regionale; le altre hanno evidenza geografica non verificata.
5. `all_reference_species.json` contiene i 2.916 nomi del riferimento; `trainable_species.json` contiene esattamente le classi che saranno allenate; `plantclef_inventory.csv` riporta i nomi del tuo CSV. La lista completa scelta prima della soglia e il crosswalk sono in `resolved_scope.json`.
6. Per allenare il sottoinsieme documentato imposta `TRAINING_ENABLED=True` e riesegui. Per richiedere la copertura integrale del riferimento spontaneo attiva `REQUIRE_FULL_REFERENCE_COVERAGE=True`: le lacune bloccano il training.

La soglia di 20 osservazioni consente lo split tecnico, non garantisce un training affidabile o una stima precisa per specie. Le immagini mancanti, i conflitti e i duplicati sono ricontrollati durante la preparazione effettiva del dataset.

## Risorse e checkpoint

Passare da 40 a migliaia di specie cambia radicalmente il costo. Il default v3 seleziona al massimo 60 osservazioni per classe e 30 estrazioni per classe/epoca per una prima prova estesa. Nessuna classe allenabile viene rimossa in base a questo limite; si limita il numero di osservazioni per controllare i costi. Questo è un compromesso iniziale, non un training finale di alta qualità. Puoi aumentare i parametri in un nuovo RUN_ID.

Sono mantenuti split per osservazione, fine-tuning, salvataggi su Drive e ripresa. Le metriche vengono calcolate per blocchi e i logits del teacher sono su disco, evitando matrici enormi in RAM. La cache teacher richiede comunque circa `4 × immagini_train × numero_classi` byte locali e ulteriore spazio su Drive. Un Colab gratuito o il Drive gratuito potrebbero non bastare; i checkpoint non aumentano la quota GPU o disco.

Non riutilizzare checkpoint a 40 classi. Inizia dalla baseline; la distillazione rimane opzionale. Una MobileNetV3Small potrebbe non essere abbastanza capace per migliaia di specie simili: un elenco più ampio non garantisce un riconoscimento migliore.

## Quando servono altri dati

Non cambierei subito dataset. Prima misura le lacune dell'incrocio. Per le specie mancanti o poco rappresentate, raccogli un'integrazione mirata da **iNaturalist** o da **GBIF** con immagini e licenze adeguate. GBIF è un aggregatore di occorrenze: non tutte includono foto e non costituisce di per sé un dataset di training pulito.

Per le ornamentali coltivate, i filtri iNaturalist che selezionano solo organismi selvatici o osservazioni Research Grade possono escludere proprio le piante coltivate. Occorrono controllo tassonomico aggiuntivo, più individui/osservazioni, licenze, deduplica rispetto a PlantCLEF e split per osservazione. Il luogo in cui una foto è stata scattata non basta a certificare la presenza spontanea della specie in Sicilia.

Non serve che ogni foto di training provenga dalla Sicilia: conta l'identificazione corretta. Serve invece un test locale rappresentativo per misurare l'uso reale in Sicilia, inclusi giardini/parchi. Il classificatore rimane a insieme chiuso: se una specie non è tra le classi, può assegnarla erroneamente a una nota. Non è incluso un rilevatore affidabile delle specie sconosciute.

## Fonti e limiti della verifica

- [FlorItaly, Università di Trieste](https://dryades.units.it/floritaly/).
- [Snapshot FlorItaly e sinonimi, commit fissato](https://github.com/gibedini/floritaly/tree/6c4c7b08dc167a943907b2249b0a6b9684096f1d): XLSX del 27 aprile 2023, checksum verificato; non aggiornamento live al 2026.
- [Documentazione dei codici di presenza regionali](https://github.com/gibedini/floritaly/blob/6c4c7b08dc167a943907b2249b0a6b9684096f1d/R/ckl_data.R).
- [PlantCLEF 2024](https://www.imageclef.org/PlantCLEF2024).
- [Implementazione pubblica PlantCLEF 2024: 7.806 classi](https://github.com/dsgt-arc/plantclef-2024/blob/main/plantclef/transforms.py).
- [iNaturalist](https://www.inaturalist.org/) e [GBIF](https://www.gbif.org/occurrence/search).

Le pagine del portale FlorItaly e del challenge non erano accessibili da questo ambiente. Le verifiche effettive delle fonti sono state eseguite sui repository pubblici e sullo snapshot XLSX completo. Il CSV PlantCLEF dell'utente non era disponibile: il numero di classi utilizzabili e la copertura reale verranno calcolati nel suo Colab. Non sono dichiarati miglioramenti di accuratezza non misurati.
