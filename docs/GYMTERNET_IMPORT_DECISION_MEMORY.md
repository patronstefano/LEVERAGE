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

## Uso futuro

Quando verranno importati nuovi file Gymternet:

1. Il tool continua a proporre possibili match atleta quando il nome e simile.
2. Se il match produrrebbe un conflitto same-context/different-score, il tool aggiunge la rule memory al payload.
3. La UI admin potra mostrare una raccomandazione gia motivata.
4. L'ADMIN potra comunque approvare, modificare o rifiutare la proposta, ma la scelta predefinita consigliata sara conservativa.
