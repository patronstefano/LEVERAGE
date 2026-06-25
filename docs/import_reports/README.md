# LEVERAGE - Import reports

Questa cartella conserva report derivati dai tool di import, separati dal database operativo.

I file qui presenti servono per:

- audit del popolamento massivo;
- tracciamento dei record non importati;
- eventuale recupero manuale futuro;
- documentazione metodologica per il diario di bordo.

Le regole decisionali riutilizzabili dal tool Gymternet sono documentate in:

```text
docs/GYMTERNET_IMPORT_DECISION_MEMORY.md
```

## Report presenti

| File | Descrizione |
|---|---|
| `gymternet_2018_athlete_collision_review.csv` | Review finale semplificata delle 48 collisioni atleta/country 2018. |
| `gymternet_2018_name_order_audit.csv` | Audit dei 15 merge automatici name-order rilevati durante la review 2018. |
| `gymternet_2018_orphan_dscores.csv` | D-score del file Gymternet 2018 non agganciati automaticamente a un result con final score. Sono stati lasciati fuori dal database operativo, ma conservati per review futura. |
| `gymternet_2019_preview_summary.json` | Sintesi tecnica della preview 2019 eseguita sul DB post-2018, senza commit. |
| `gymternet_2019_athlete_match_decisions.json` | Payload tecnico generato dalle decisioni admin 2019. Aggiornato dopo la risoluzione dei conflitti post-decisione. |
| `gymternet_2019_preview_with_decisions_summary.json` | Preview 2019 eseguita con decisioni admin applicate su copia temporanea del DB, senza modificare `leverage.db`. |
| `gymternet_2019_post_decision_conflicts.csv` | Audit dei conflitti post-decisione 2019. Inizialmente conteneva 24 conflitti; dopo le decisioni admin `keep separate`, e stato rigenerato vuoto e non blocca piu il commit. |
| `gymternet_2019_orphan_dscores.csv` | D-score del file Gymternet 2019 non agganciati automaticamente a un result con final score. |
| `gymternet_2019_athlete_review.csv` | Review atleta/country 2019 completa e tecnica. Conservata come report aggregato di riferimento. |
| `gymternet_2019_existing_athlete_match_review.csv` | CSV operativo principale per verificare se un atleta importato nel 2019 corrisponde a un atleta gia presente nel DB 2018. Include le gare 2018 dell'atleta gia esistente. |
| `gymternet_2019_existing_athlete_repeat_audit.csv` | Audit delle righe 2019 in cui lo stesso atleta gia esistente viene suggerito piu volte per varianti di nome/country. |
| `gymternet_2019_new_athlete_country_conflicts.csv` | CSV operativo separato per nuovi atleti 2019 che presentano solo conflitti di country nel file 2019. Completato dall'admin e convertito da Numbers il 25 giugno 2026. |

## Convenzione review atleta/country

Nei CSV semplificati:

- `decision`: usare `merge as same athlete` oppure `keep separate`;
- `action`: usare `canonical country` se una country e un errore da correggere, oppure `country history` se si tratta di storico/cambio country;
- `country`: country corretta nel caso `canonical country`, oppure country finale/corrente nel caso `country history`.
- `future_country_evidence`: mostra la country rappresentata negli anni successivi. Nel CSV 2019 copre 2020-2025; nel CSV 2018 copre 2019-2025.

Per la review manuale 2019 si usano preferibilmente i due CSV separati:

- `gymternet_2019_existing_athlete_match_review.csv`: casi in cui il sistema suggerisce un possibile collegamento tra atleta importato 2019 e atleta gia presente dal 2018;
- `gymternet_2019_new_athlete_country_conflicts.csv`: casi in cui il nuovo atleta 2019 ha country discordanti all'interno del file 2019.

Nel primo CSV la colonna `existing_athlete_2018_results_by_country` mostra le gare 2018 dell'atleta gia salvato nel DB, cosi l'admin puo valutare se si tratta dello stesso atleta o di due atleti diversi.

Nel CSV `gymternet_2019_new_athlete_country_conflicts.csv`, i valori inseriti come `Merge` e `Correct` nel file Numbers sono stati normalizzati rispettivamente in `merge as same athlete` e `canonical country`.

Nel CSV `gymternet_2019_existing_athlete_match_review.csv`, i valori inseriti come `Merge`, `Separate`, `Correct`, `History` e `Histroy` nel file Numbers sono stati normalizzati rispettivamente in `merge as same athlete`, `keep separate`, `canonical country` e `country history`.

Regola metodologica aggiunta durante la review 2019: se due atleti hanno stessa country, nome molto simile e l'evidenza degli anni successivi mostra che una variante non viene piu trovata, il sistema potra trattare il caso come merge automatico/candidato diretto, riducendo le review manuali future.

Regola metodologica persistente: se una proposta di merge atleta produce lo stesso contesto sportivo di result ma con score o D-score diversi, il tool deve raccomandare `keep separate`. Nel backend questa regola e tracciata con `same_context_different_score_keep_separate`.
