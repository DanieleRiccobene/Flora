# Flora v2 — guida e verifica

Apri `Flora_v2_PlantCLEF_MobileNetV3_Colab.ipynb` in Google Colab e scegli un runtime GPU.
Il file è autonomo: non richiede questo documento né script esterni.

## Avvio

1. Mantieni il CSV originale in `/content/drive/MyDrive/PlantCLEF2024singleplanttrainingdata.csv`, oppure cambia `METADATA_CSV` nella cella 2.
2. Parti con `MODE='baseline'` e un `RUN_ID` nuovo. Esegui in ordine; autorizza il mount del tuo Drive.
3. I risultati rimangono in `MyDrive/Flora_v2/<RUN_ID>/`. Il primo download può richiedere tempo e spazio: non sono inclusi dati o modelli già allenati.
4. Dopo una pausa, mantieni parametri e RUN_ID ed esegui nuovamente dall'inizio. Le fasi complete sono recuperate e quella interrotta riparte dall'ultimo batch salvato.
5. Per provare la distillazione: completa `MODE='teacher'`, poi esegui `MODE='distill'`. Puoi farlo in sessioni diverse. Il teacher deve battere la baseline su validation macro-F1.
6. Imposta `RUN_FINAL_TEST=True` solo per la valutazione finale e `EXPORT_TFLITE=True` per ottenere i modelli per l'app. INT8 è opzionale.

## Motivazioni delle modifiche

Il notebook originale riportava circa 54,7% di accuratezza train e 52,2% validation alla fine, con validation loss ancora in discesa. Questi risultati non dimostrano un forte overfitting. La nuova versione mantiene MobileNetV3Small ma aumenta la porzione del backbone adattata alle piante, introduce un learning rate decrescente e sceglie i modelli tramite validation macro-F1.

Il limite di 500 osservazioni viene rimosso. Non è però un modo per creare dati: gli output originali riportavano solo 19.860 immagini per 18.674 osservazioni sulle 40 specie prima del limite. Si usa un campionamento bilanciato per specie e osservazione senza scartare sistematicamente le specie più abbondanti. Validation e test non vengono bilanciati artificialmente.

Per risparmiare calcolo si sceglie una foto per osservazione estratta, alternando gli organi disponibili tra epoche. Impostare due viste ha più senso quando il dataset contiene davvero più foto per osservazione. Il report di copertura permette di vedere specie e organi mancanti: il training non può compensare completamente l'assenza di esempi.

EfficientNetB0 è un teacher relativamente contenuto, inizializzato da ImageNet e adattato alle stesse classi. I suoi logits vengono precalcolati sulle immagini train canoniche; lo student distillato usa le stesse viste, senza crop casuali incompatibili con la cache. La distillazione viene confrontata con la baseline e può essere scartata se non migliora la validation.

## Ripresa e limiti

Ogni snapshot contiene pesi correnti e migliori, stato Adam, contatore del learning rate, epoca, prossimo batch, best score e pazienza. Ordine dei campioni e augmentation sono ricostruiti con semi stateless. Si conservano due snapshot completi per fase e si verifica l'integrità; una copia danneggiata può far ripiegare sulla precedente.

Un'interruzione improvvisa può perdere il lavoro successivo all'ultimo salvataggio completato. Non si promette la sincronizzazione immediata del filesystem Drive né identità numerica bit-per-bit tra hardware differenti. Lo stop manuale durante un aggiornamento GPU può avere granularità di un batch.

Il budget di 150 minuti limita i loop della sessione, non il tempo totale del progetto e non i tempi di download, validazione e conversione. Non aggira i limiti di Colab. Per cambiare dati, classi, batch o iperparametri crea un nuovo RUN_ID.

## Verifiche locali

Eseguite su CPU con Python 3.12, TensorFlow 2.19.1 e Keras 3.15.1, con fixture sintetiche. Nessun risultato sulle piante è stato inventato. I dettagli dei controlli completati sono in `Flora_v2_VERIFICA.txt`.

Il dataset PlantCLEF completo, il mount Google Drive e la GPU di Colab non erano disponibili per il test locale. Servono quindi una prima esecuzione nel tuo account e la valutazione reale per sapere se le modifiche migliorano l'accuratezza. I pesi ImageNet non sono stati scaricati durante i test: le architetture sono state verificate con inizializzazione casuale, mentre nel notebook il training parte da ImageNet.

Il notebook originale e il repository Flora non sono stati modificati.
