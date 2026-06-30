# LEVERAGE - Gymternet Import Decision Memory

Questo documento raccoglie le decisioni metodologiche che il tool Gymternet deve ricordare negli import futuri.

La finalita non e sostituire l'ADMIN, ma ridurre lavoro ripetitivo: quando un problema gia affrontato si ripresenta, il backend deve riconoscerlo, proporre una soluzione coerente e mostrare all'ADMIN il motivo della raccomandazione.

## Regola: Same Context Different Score

ID tecnico:

```text
same_context_different_score_keep_separate
```

### Problema

Durante la review atleta/country, il tool puo proporre di fondere due nomi molto simili, per esempio:

- `Jake Stanley` e `Jack Stanley`;
- `Cen Yu` e `Chen Yu`;
- `Sonia Bertoli` e `Sofia Bertoli`.

Se pero, dopo la fusione, due righe diventano lo stesso result sportivo ma mantengono score o D-score diversi, il caso non va trattato come duplicato innocuo.

Il contesto sportivo e considerato lo stesso quando coincidono:

- athlete risolto dopo la fusione proposta;
- event/year;
- discipline;
- category;
- apparatus;
- format;
- round;
- day;
- vt_attempt.

### Decisione

In questo caso il tool deve raccomandare `keep separate`.

Per le review di tipo `possible_existing_athlete_match`, l'equivalente operativo nel backend e:

```json
{"action": "create_new", "reason": "same_context_different_score_keep_separate"}
```

Per i conflitti post-decisione, il payload deve riportare:

```json
{
  "learned_rule_match": {
    "rule_id": "same_context_different_score_keep_separate",
    "recommended_action": "keep_separate"
  }
}
```

### Motivazione

Due punteggi diversi nello stesso identico contesto sportivo indicano che probabilmente si tratta di atleti diversi con nomi simili, oppure di un errore sorgente che richiede prova ufficiale prima di fondere i dati.

La scelta conservativa per LEVERAGE e non fondere automaticamente.

### Eccezione

La fusione puo essere valutata solo se una fonte ufficiale dimostra che:

- i due record si riferiscono davvero allo stesso atleta;
- uno dei due punteggi e un errore sorgente identificato.

In assenza di questa prova, il dato resta separato.

### Esempi 2019

La regola e stata formalizzata dopo la review Gymternet 2019. I gruppi che l'hanno originata sono:

| Variante importata | Atleta suggerito | Decisione |
|---|---|---|
| Carolina Martin | Carla Martin | keep separate |
| Cen Yu | Chen Yu | keep separate |
| Jake Stanley | Jack Stanley | keep separate |
| Lee Jung-hyo | Lee Jun-ho | keep separate |
| Maja Skalska | Kaja Skalska | keep separate |
| Riddhi Hattekar | Siddhi Hattekar | keep separate |
| Sonia Bertoli | Sofia Bertoli | keep separate |

### Esempio 2020

La regola e stata riapplicata durante la review Gymternet 2020 sul caso:

| Variante importata | Atleta suggerito | Contesto | Decisione |
|---|---|---|---|
| Nao Kobayashi | Kaho Kobayashi | All-Japan Student Championships 2020, stessi apparatus e score diversi | keep separate |

In questo caso il merge avrebbe creato 5 conflitti post-decisione, perche i due atleti risultavano presenti nello stesso evento, nello stesso round/format e sugli stessi apparatus con punteggi diversi. La decisione finale e stata trattarli come due atleti distinti.

### Esempi 2021

La regola e stata riapplicata durante la review Gymternet 2021 sui casi:

| Variante importata | Atleta suggerito | Contesto | Decisione |
|---|---|---|---|
| Ona Garcia | Ana Garcia | 1st Spanish League 2021, stessi apparatus e score diversi | keep separate |
| Ariadna Sanchez | Aitana Sanchez | 1st Spanish League 2021, stessi apparatus e score diversi | keep separate |

## Regola: Correzione Nome Target Esistente

ID tecnico:

```text
target_name_update
```

### Problema

Durante la review `possible_existing_athlete_match`, puo emergere che l'atleta importato e lo stesso atleta gia presente nel DB, ma il nome salvato nella scheda atleta esistente contiene un errore di data entry.

### Decisione

Quando l'ADMIN verifica ufficialmente il caso, il payload decisionale puo includere:

```json
{
  "target_name_update": {
    "first_name": "Daniel",
    "last_name": "Carrion",
    "reason": "admin_verified_existing_db_name_typo"
  }
}
```

Il commit deve aggiornare la scheda atleta esistente e collegare i nuovi result allo stesso `athlete_id`, senza creare un duplicato atleta.

### Esempi 2021

| Nome errato nel DB | Nome corretto |
|---|---|
| Hirohito Obama | Hirohito Kohama |
| Dawiel Carrion | Daniel Carrion |
| Yuta Sasaki | Yutaro Sasaki |
| Ai Takada | Airi Takada |
| Hung Yuang-His | Hung Yuan-Hsi |

## Regola: Riuso Decisioni Same-Country

ID tecnico:

```text
same_country_review_reuse
```

### Problema

Durante gli import annuali Gymternet ricompaiono spesso gli stessi casi di nomi molto simili gia controllati dall'ADMIN negli anni precedenti.

Quando il country non cambia, questi casi sono spesso:

- errori di battitura;
- differenze di accento;
- differenze di trattino/spazio;
- varianti di romanizzazione gia validate.

Ricontrollare ogni anno gli stessi atleti rallenta la review senza aggiungere reale qualita al dato.

### Decisione

Il tool puo riusare come raccomandazione forte le decisioni `merge as same athlete` o `keep separate` gia verificate dall'ADMIN solo quando:

- la country importata e la country dell'atleta suggerito coincidono;
- la disciplina coincide;
- il caso riguarda lo stesso atleta o la stessa coppia di varianti nome gia controllata;
- non emerge un conflitto `same_context_different_score_keep_separate`.

In questi casi il tool puo ridurre la review manuale ripetitiva precompilando o raccomandando la stessa decisione gia presa.

Il riuso operativo legge le review CSV degli anni precedenti e viene applicato solo se la memoria storica e univoca per quella coppia atleta/variante nome. Se negli anni precedenti emergono decisioni discordanti sullo stesso caso, il tool non precompila nulla e lascia la review manuale.

### Limite obbligatorio

Se la country cambia, la decisione non deve essere riusata automaticamente.

Ogni caso con country diversa deve tornare in review admin manuale, perche potrebbe indicare:

- cambio reale di rappresentanza;
- errore di country nel file sorgente;
- fusione errata di due atleti diversi;
- caso storico da preservare su `Result.represented_country`.

Quindi la regola `same_country_review_reuse` vale solo per casi same-country. Le collisioni o i match con country diversa restano sempre da controllare uno per uno.

## Uso futuro

Quando verranno importati nuovi file Gymternet:

1. Il tool continua a proporre possibili match atleta quando il nome e simile.
2. Se il match produrrebbe un conflitto same-context/different-score, il tool aggiunge la rule memory al payload.
3. La UI admin potra mostrare una raccomandazione gia motivata.
4. Le decisioni gia verificate possono essere riusate come raccomandazione forte solo nei casi same-country.
5. I casi con country diversa restano sempre in review manuale admin.
6. L'ADMIN potra comunque approvare, modificare o rifiutare la proposta, ma la scelta predefinita consigliata sara conservativa.
