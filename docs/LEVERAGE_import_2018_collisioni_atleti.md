# LEVERAGE - Revisione collisioni atleta import 2018

Data creazione: 24 giugno 2026  
File sorgente: `import_files/Results 2018.xlsx`  
Stato: revisione manuale completata, commit 2018 eseguito e verificato

---

## 1. Scopo

Questo documento registra le 48 collisioni atleta rilevate dalla preview import 2018.

Una collisione atleta significa:

- stesso nome atleta;
- stessa disciplina;
- country diverse nello stesso file sorgente.

Questi casi non vengono risolti automaticamente prima del commit per evitare due errori opposti:

- fondere atleti diversi che hanno lo stesso nome;
- creare doppioni quando si tratta dello stesso atleta con country/representation diversa o con data entry errato.

Ogni riga e stata verificata e aggiornata con una decisione admin esplicita.

---

## 2. Azioni possibili

| Azione | Significato | Effetto atteso |
|---|---|---|
| `merge_as_same_athlete` | Le varianti country appartengono allo stesso atleta | Viene creata/usata una sola entita Athlete; ogni Result conserva il proprio `represented_country` |
| `keep_separate` | Le varianti country indicano atleti diversi con stesso nome | Vengono create entita Athlete separate per country |
| `manual_target` | La collisione deve essere agganciata manualmente a un atleta specifico | L'admin indica il target corretto |
| `postpone` | Il caso non e risolto in questa sessione | Il caso resta fuori dal commit o viene rimandato a revisione successiva |

Nota metodologica: il campo `Suggested canonical` e solo un aiuto operativo basato sul paese con piu result. Non e una decisione automatica.

### 2.1 Gestione country nei casi `merge_as_same_athlete`

Quando la decisione e `merge_as_same_athlete`, bisogna distinguere due casi:

| Caso | Come annotarlo in `Notes` | Effetto tecnico |
|---|---|---|
| Cambio reale di nazionalita/rappresentanza | `country_history` | Una sola scheda Athlete; ogni Result conserva la propria country storica in `represented_country` |
| Errore di data entry nel file | `country_correction: XXX -> YYY` | Una sola scheda Athlete; i Result con country `XXX` vengono salvati con `represented_country=YYY` |

Esempio:

```text
Decision: merge_as_same_athlete
Notes: country_correction: RUS -> ISR. Alexander Shatilov risulta atleta ISR; la variante RUS appare isolata.
```

Se il caso e un cambio reale:

```text
Decision: merge_as_same_athlete
Notes: country_history. Preservare country diverse sui Result per rappresentare la storia sportiva.
```

---

## 3. Decision log

| Data | Decisione |
|---|---|
| 24 giugno 2026 | Le collisioni country 2018 saranno verificate manualmente una per una prima del commit definitivo del file 2018. Nessuna regola generale di merge automatico country viene applicata senza validazione admin. |
| 24 giugno 2026 | Il flusso tecnico distingue tra `country_history` e `country_correction`. In caso di cambio reale i Result preservano la country sorgente; in caso di errore data entry i Result vengono importati con `represented_country` corretto senza modificare il file Excel sorgente. |
| 24 giugno 2026 | Per aiutare la revisione manuale, ogni collisione 2018 viene incrociata con i file 2019-2025. La colonna `Post-2018 evidence` e un supporto decisionale, non una regola automatica: se un atleta compare dopo il 2018 con una sola country, cio puo indicare country finale/canonica, cambio reale o correzione probabile da valutare con il contesto 2018. |
| 24 giugno 2026 | Revisione admin originaria completata prima della rettifica name-order: 48 decisioni compilate, 47 `merge_as_same_athlete`, 1 `keep_separate`, 46 `country_correction`, 1 `country_history`. Dopo la rettifica, 47 decisioni restano trasferibili e una nuova review country (`Henji Mboyo`) viene generata dalla normalizzazione automatica. |
| 24 giugno 2026 | A seguito della nota admin su `Takumi Onoshima` / `Onoshima Takumi`, la gestione di nomi/cognomi invertiti o formati equivalenti e stata trasformata da review manuale a regola automatica `merge name order`. La preview 2018 rileva 15 merge automatici, 17 chiavi atleta/country ricondotte a nome canonico e 116 righe risultato normalizzate. |
| 24 giugno 2026 | Rettifica collisioni 2018 dopo `merge name order`: le vecchie review separate `Takumi Onoshima` e `Onoshima Takumi` sono fuse in una sola collisione country `Takumi Onoshima` (`BEL`, `ITA`, `JPN`) con review_id `athlete_identity_collision_e7d998bc5bee3b13`; emerge inoltre una nuova collisione country `Henji Mboyo` (`FRA`, `SUI`) con review_id `athlete_identity_collision_cbd1cb5826150c8e`. |
| 24 giugno 2026 | Decisione admin su `Henji Mboyo`: atleta sempre `SUI`; la variante `FRA` viene trattata come errore di data entry. Decisione tecnica: `merge_as_same_athlete` con `country_correction -cc:SUI`. Tutte le 48 collisioni country della preview 2018 post-name-order risultano ora risolte. |

---

## 4. Tabella revisione collisioni

Nota: `Post-2018 evidence` e ottenuta cercando lo stesso nome e la stessa disciplina nei file `Results 2019.xlsx` - `Results 2025.xlsx`. Serve come evidenza di supporto, non come decisione automatica.

| # | Athlete | Disc. | Countries/counts | Suggested canonical | Risk | 2018 evidence | Post-2018 evidence | Decision | Notes |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | Sol Lucrecia Acosta | WAG | ITA:8, PAR:5 (tot 13) | ITA | MEDIA: verificare | ITA 8: 2nd Italian Serie A; 3rd Italian Serie A / PAR 5: 1st Italian Serie A | 2020: PAR:13 / 2021: PAR:11 / 2022: PAR:25 | merge_as_same_athlete | country_correction -cc:PAR | review_id: `athlete_identity_collision_b81011798c4cc7e5` |
| 2 | Laura Aerts | WAG | BEL:20, NED:8 (tot 28) | BEL | MEDIA: verificare | BEL 20: International GymSport; Leverkusen Cup; Belgian Championships / NED 8: Dutch Championships | not found 2019-2025 | merge_as_same_athlete | country_correction -cc:BEL | review_id: `athlete_identity_collision_e8b44e9eb87cf02f` |
| 3 | Raman Antropau | MAG | BLR:7, ROU:7 (tot 14) | TIE: BLR/ROU | ALTA: pareggio | BLR 7: World Championships / ROU 7: European Championships | 2019: BLR:21 | merge_as_same_athlete | country_correction -cc:BLR| review_id: `athlete_identity_collision_3beab366ad35a51b` |
| 4 | Stella Ashcroft | WAG | AUS:1, NZL:16 (tot 17) | NZL | BASSA/MEDIA: possibile outlier o cambio country | AUS 1: Melbourne World Cup / NZL 16: Commonwealth Games; Melbourne World Cup | not found 2019-2025 | merge_as_same_athlete | country_correction -cc:NZL | review_id: `athlete_identity_collision_25975f56a254df1d` |
| 5 | Giulia Bencini | WAG | GER:5, ITA:35 (tot 40) | ITA | BASSA/MEDIA: possibile outlier o cambio country | GER 5: 4th Bundesliga / ITA 35: Italian Gold Championships; 3rd Italian Serie A; Bundesliga Finals | 2019: ITA:12 / 2020: ITA:23 / 2021: ITA:8 | merge_as_same_athlete | country_correction -cc:ITA | review_id: `athlete_identity_collision_1e21b709d428c6ad` |
| 6 | Bogi Berg | MAG | DEN:8, FAR:4 (tot 12) | DEN | MEDIA: verificare | DEN 8: Danish Championships / FAR 4: Nordic Championships | 2019: DEN:6 | merge_as_same_athlete | country_correction -cc:DEN | review_id: `athlete_identity_collision_8a67a894dad2aa45` |
| 7 | Astrid Breckmann | WAG | DEN:12, FAR:5 (tot 17) | DEN | MEDIA: verificare | DEN 12: Danish Championships / FAR 5: Nordic Championships | 2019: FAR:20 / 2020: DEN:8 / 2021: DEN:5 / 2022: DEN:5 / 2023: DEN:3 | merge_as_same_athlete | country_correction -cc:DEN | review_id: `athlete_identity_collision_d35ef3cc9a1b0474` |
| 8 | Pascal Brendel | MAG | FRA:1, GER:7 (tot 8) | GER | BASSA/MEDIA: possibile outlier o cambio country | FRA 1: RD761 Junior International Cup / GER 7: RD761 Junior International Cup | 2019: GER:34 / 2020: GER:3 / 2021: GER:28 / 2022: GER:53 / 2023: GER:82 / 2024: GER:72 | merge_as_same_athlete | country_correction -cc:GER | review_id: `athlete_identity_collision_a059bc4f4341602f` |
| 9 | Corinne Bunagan | WAG | PHI:10, USA:5 (tot 15) | PHI | MEDIA: verificare | PHI 10: World Championships; Asian Games / USA 5: Orlando Qualifier | not found 2019-2025 | merge_as_same_athlete | country_correction -cc:PHI | review_id: `athlete_identity_collision_dd02abca5bb8c80a` |
| 10 | Georgios Chatziefstathiou | MAG | GRE:37, ITA:5 (tot 42) | GRE | BASSA/MEDIA: possibile outlier o cambio country | GRE 37: Greek Championships; Mediterranean Games; European Championships / ITA 5: 2nd Italian Serie A | 2019: GRE:4 | merge_as_same_athlete | country_correction -cc:GRE | review_id: `athlete_identity_collision_1948eb6f54d4f7fc` |
| 11 | Margaux Daveloose | WAG | BEL:33, FRA:3 (tot 36) | BEL | BASSA/MEDIA: possibile outlier o cambio country | BEL 33: International Gymnix; Elite Gym Massilia; Belgian Championships / FRA 3: Top 12 Series 1 | 2019: BEL:21 / 2020: BEL:6 / 2021: BEL:21 | merge_as_same_athlete | country_correction -cc:BEL | review_id: `athlete_identity_collision_4e13666066e5a1c2` |
| 12 | Sofia Diaz | WAG | ESP:2, PUR:2 (tot 4) | TIE: ESP/PUR | ALTA: pareggio | ESP 2: 3rd Spanish League / PUR 2: International Gymnix | 2021: PUR:2 | merge_as_same_athlete | country_correction -cc:PUR | review_id: `athlete_identity_collision_6ce6d4f95456ca9d` |
| 13 | Daniel Fox | MAG | GBR:12, IRL:10 (tot 22) | GBR | ALTA: distribuzione vicina | GBR 12: English Championships; British Championships / IRL 10: Irish Super Championships; Irish Championships | 2019: IRL:4 / 2021: IRL:9 / 2022: IRL:15 / 2024: IRL:30 | merge_as_same_athlete | country_correction -cc:IRL | review_id: `athlete_identity_collision_91a32b244809173d` |
| 14 | Benjamin Gischard | MAG | FRA:3, SUI:38 (tot 41) | SUI | BASSA/MEDIA: possibile outlier o cambio country | FRA 3: Top 12 Semi-Final 2 / SUI 38: Koper Challenge Cup; Swiss Championships; World Championships | 2019: SUI:41 / 2020: SUI:13 / 2021: SUI:60 / 2022: SUI:14 / 2023: SUI:32 / 2025: SUI:26 | merge_as_same_athlete | country_correction -cc:SUI | review_id: `athlete_identity_collision_595510b25b9d82f8` |
| 15 | Dmitriy Govorov | MAG | GEO:22, RUS:31 (tot 53) | RUS | ALTA: distribuzione vicina | GEO 22: Dityatin Cup; Voronin Cup / RUS 31: Russian Championships | not found 2019-2025 | merge_as_same_athlete | country_correction -cc:GEO | review_id: `athlete_identity_collision_45fa3927b3d55b89` |
| 16 | Eyal Indig | MAG | GBR:7, ISR:14 (tot 21) | ISR | MEDIA: verificare | GBR 7: British Championships / ISR 14: Israeli Championships; European Championships | 2019: ISR:28 / 2020: ISR:8 / 2021: ISR:24 / 2022: ISR:20 / 2023: ISR:4 / 2025: ISR:9 | merge_as_same_athlete | country_correction -cc:ISR | review_id: `athlete_identity_collision_15c46d1aa44f01b4` |
| 17 | Tan Fu Jie | MAG | MAS:9, TPE:3 (tot 12) | MAS | BASSA/MEDIA: possibile outlier o cambio country | MAS 9: Asian Games; Commonwealth Games; Doha World Cup / TPE 3: Singapore Open | 2019: MAS:14 / 2020: MAS:3 / 2022: MAS:4 | merge_as_same_athlete | country_correction -cc:MAS | review_id: `athlete_identity_collision_6adaf0afc5d23ad2` |
| 18 | Yuya Kamoto | MAG | JPN:35, UKR:3 (tot 38) | JPN | BASSA/MEDIA: possibile outlier o cambio country | JPN 35: All-Japan Championships; NHK Trophy; All-Japan Event Championships / UKR 3: Paris Challenge Cup | 2019: JPN:42 / 2020: JPN:24 / 2021: JPN:21 / 2022: JPN:43 / 2023: JPN:25 / 2024: JPN:16 / 2025: JPN:3 | merge_as_same_athlete | country_correction -cc:JPN | review_id: `athlete_identity_collision_023fe0040af9709b` |
| 19 | Noah Kuavita | MAG | BEL:39, FRA:2 (tot 41) | BEL | BASSA/MEDIA: possibile outlier o cambio country | BEL 39: Belgian Championships; Ghent Men's Friendly; Dutch Championships / FRA 2: Top 12 Series 6 | 2019: BEL:48 / 2020: BEL:3 / 2021: BEL:37 / 2022: BEL:29 / 2023: BEL:13 / 2024: BEL:15 / 2025: BEL:10 | merge_as_same_athlete | country_correction -cc:BEL | review_id: `athlete_identity_collision_9cd5b626f59c4803` |
| 20 | Konstantin Kuzovkov | MAG | GEO:59, RUS:17 (tot 76) | GEO | BASSA/MEDIA: possibile outlier o cambio country | GEO 59: European Championships; Dityatin Cup; Voronin Cup / RUS 17: Russian Championships | 2019: GEO:34 / 2020: GEO:9 | merge_as_same_athlete | country_correction -cc:GEO | review_id: `athlete_identity_collision_92011bd6ade6fdba` |
| 21 | Helge Liebrich | MAG | GER:25, ITA:14 (tot 39) | GER | MEDIA: verificare | GER 25: 2nd Bundesliga; 4th Bundesliga; 3rd Bundesliga / ITA 14: 2nd Italian Serie A; 3rd Italian Serie A | 2019: GER:26 / 2020: GER:2 / 2021: GER:1 | merge_as_same_athlete | country_correction -cc:GER | review_id: `athlete_identity_collision_2e6fce9a3a815be4` |
| 22 | Gioia Meli | WAG | ESP:3, ITA:2 (tot 5) | ESP | MEDIA: verificare | ESP 3: 3rd Spanish League / ITA 2: Italian Gold Championships | not found 2019-2025 | merge_as_same_athlete | country_correction -cc:ITA | review_id: `athlete_identity_collision_8272ef602eefccae` |
| 23 | Jon Jang Mi | WAG | CHN:5, PRK:6 (tot 11) | PRK | ALTA: distribuzione vicina | CHN 5: Asian Games / PRK 6: Asian Games; World Championships | 2024: PRK:3 | merge_as_same_athlete | country_correction -cc:PRK | review_id: `athlete_identity_collision_9399b65215ab2b12` |
| 24 | Janna Mouffok | WAG | ALG:10, FRA:13 (tot 23) | FRA | ALTA: distribuzione vicina | ALG 10: Varsenare Friendly; World Championships / FRA 13: French Championships; Top 12 Final; Top 12 Series 3 | not found 2019-2025 | merge_as_same_athlete | country_correction -cc:ALG | review_id: `athlete_identity_collision_3582dd3480be12f6` |
| 25 | Andrei Muntean | MAG | FRA:5, ROU:69 (tot 74) | ROU | BASSA/MEDIA: possibile outlier o cambio country | FRA 5: Top 12 Series 1; Top 12 Series 4; Top 12 Series 2 / ROU 69: World Championships; Romanian Championships; Koper Challenge Cup | 2019: FRA:4, GER:2, ROU:27 / 2020: ROU:12 / 2021: ROU:5 / 2022: FRA:1, ROU:34 / 2023: ROU:39 / 2024: ROU:11 / 2025: ROU:2 | merge_as_same_athlete | country_correction -cc:ROU | review_id: `athlete_identity_collision_336a1ce6b2e19533` |
| 26 | Sofiia Mykytsei | WAG | GER:10, UKR:11 (tot 21) | UKR | ALTA: distribuzione vicina | GER 10: 3rd Bundesliga; 1st Bundesliga / UKR 11: Ukraine Cup | 2019: UKR:5 / 2020: UKR:8 | merge_as_same_athlete | country_correction -cc:UKR | review_id: `athlete_identity_collision_0b1e37828cf14ad4` |
| 27 | Yu Nagayosi | MAG | JPN:7, RSA:2 (tot 9) | JPN | BASSA/MEDIA: possibile outlier o cambio country | JPN 7: Africa Safari International / RSA 2: Africa Safari International | not found 2019-2025 | merge_as_same_athlete | country_correction -cc:JPN | review_id: `athlete_identity_collision_a5604845aadbcb5e` |
| 28 | Sofia Nair | WAG | ALG:12, FRA:5 (tot 17) | ALG | MEDIA: verificare | ALG 12: African Championships; Youth Olympic Games / FRA 5: Elite Gym Massilia | 2019: ALG:19 / 2022: ALG:5 | merge_as_same_athlete | country_correction -cc:ALG | review_id: `athlete_identity_collision_60e0088d12d68679` |
| 29 | Michael O'Neill | MAG | GBR:14, IRL:13 (tot 27) | GBR | ALTA: distribuzione vicina | GBR 14: English Championships; British Championships / IRL 13: Irish Championships; Irish Super Championships | 2019: GBR:14, IRL:12 / 2021: GBR:3, IRL:2 / 2022: GBR:4, IRL:4 / 2023: IRL:7 / 2024: GBR:14, IRL:13 / 2025: GBR:3, IRL:2 | merge_as_same_athlete | country_correction -cc:IRL | review_id: `athlete_identity_collision_83326483e75bd109` |
| 30 | Davide Odomaro | MAG | FRA:6, ITA:14 (tot 20) | ITA | MEDIA: verificare | FRA 6: Top 12 Semi-Final 1; Top 12 Series 4; Top 12 Series 1 / ITA 14: 3rd Italian Serie A; 2nd Italian Serie A; 1st Italian Serie A | 2019: FRA:1, ITA:12 | merge_as_same_athlete | country_correction -cc:ITA | review_id: `athlete_identity_collision_6f1a5dbe55c8df29` |
| 31 | Takumi Onoshima | MAG | BEL:21, ITA:12, JPN:7 (tot 40) | BEL | RETTIFICA NAME-ORDER: vecchie review `Takumi Onoshima` e `Onoshima Takumi` fuse automaticamente | BEL 21: Ghent Men's Friendly; Doha World Cup; Dutch Championships; Belgian Championships / ITA 12: 1st Italian Serie A; 2nd Italian Serie A; 3rd Italian Serie A / JPN 7: DTB Team Challenge | 2019: BEL:38 / 2020: BEL:4 / 2021: BEL:17 / 2022: BEL:35 / 2023: BEL:22 / 2024: BEL:3 / 2025: BEL:31 | merge_as_same_athlete | country_correction -cc:BEL; name_order_auto_merge; review_id: `athlete_identity_collision_e7d998bc5bee3b13` |
| 32 | Ana Palacios | WAG | ESP:8, GUA:25 (tot 33) | GUA | BASSA/MEDIA: possibile outlier o cambio country | ESP 8: Spanish Championships; International GymSport / GUA 25: Central American & Caribbean Games; Pan American Championships; World Championships | 2019: GUA:20 / 2021: GUA:10 / 2022: GUA:5 | merge_as_same_athlete | country_correction -cc:GUA | review_id: `athlete_identity_collision_f853884d4d281fd4` |
| 33 | Justin Pesesse | MAG | BEL:26, FRA:3 (tot 29) | BEL | BASSA/MEDIA: possibile outlier o cambio country | BEL 26: European Championships; Belgian Championships; Dutch Championships / FRA 3: Top 12 Series 2 | 2019: BEL:16 / 2020: BEL:8 / 2021: BEL:4 | merge_as_same_athlete | country_correction -cc:BEL | review_id: `athlete_identity_collision_c85be8f84adb5998` |
| 34 | Freja Petersen | WAG | DEN:16, FAR:5 (tot 21) | DEN | BASSA/MEDIA: possibile outlier o cambio country | DEN 16: Danish Championships; European Championships / FAR 5: Nordic Championships | 2019: DEN:36 / 2021: DEN:30 / 2022: DEN:33 | merge_as_same_athlete | country_correction -cc:DEN | review_id: `athlete_identity_collision_87d99fabcaa70fc3` |
| 35 | Berta Pujadas | WAG | BRA:1, ESP:30 (tot 31) | ESP | BASSA/MEDIA: possibile outlier o cambio country | BRA 1: Gymnasiade / ESP 30: Houston National Invitational; 3rd Spanish League; Gymnasiade | 2019: ESP:54 / 2020: ESP:2 / 2021: ESP:12 / 2022: ESP:1 | merge_as_same_athlete | country_correction -cc:ESP | review_id: `athlete_identity_collision_11ffe28564b3f077` |
| 36 | Rebekka Rein | WAG | DEN:7, FAR:5 (tot 12) | DEN | ALTA: distribuzione vicina | DEN 7: Danish Championships / FAR 5: Nordic Championships | 2019: FAR:15 / 2020: DEN:4 / 2021: DEN:5 / 2022: DEN:5 | merge_as_same_athlete | country_correction -cc:DEN | review_id: `athlete_identity_collision_f78e22a7308fb871` |
| 37 | Sara Ricciardi | WAG | ITA:50, SRB:5 (tot 55) | ITA | BASSA/MEDIA: possibile outlier o cambio country | ITA 50: Italian Championships; Italian Gold Championships; City of Jesolo Trophy / SRB 5: World Championships | 2019: ITA:25 / 2020: ITA:21 / 2021: ITA:10 / 2022: ITA:15 / 2023: ITA:8 / 2024: ITA:13 / 2025: ITA:4 | merge_as_same_athlete | country_correction -cc:ITA | review_id: `athlete_identity_collision_e7667a5cae10cfcb` |
| 38 | Alexey Rostov | MAG | ITA:4, RUS:53 (tot 57) | RUS | BASSA/MEDIA: possibile outlier o cambio country | ITA 4: 2nd Italian Serie A / RUS 53: Russian Championships; 2nd Bundesliga; 5th Bundesliga | 2019: RUS:76 / 2020: RUS:13 / 2021: RUS:40 / 2022: RUS:47 / 2023: RUS:32 / 2024: RUS:35 | merge_as_same_athlete | country_correction -cc:RUS | review_id: `athlete_identity_collision_4c3f9d0cce838c57` |
| 39 | Melek Sak | WAG | RUS:5, TUR:5 (tot 10) | TIE: RUS/TUR | ALTA: pareggio | RUS 5: Russian Junior Championships / TUR 5: Turkish Championships | 2021: RUS:10 | keep_separate | review_id: `athlete_identity_collision_3c8332ac471efa45` |
| 40 | Deborah Salmina | WAG | ITA:15, VEN:11 (tot 26) | ITA | ALTA: distribuzione vicina | ITA 15: City of Jesolo Trophy; 1st Italian Serie A; 2nd Italian Serie A / VEN 11: Central American & Caribbean Games | 2020: VEN:3 / 2021: VEN:5 / 2023: VEN:32 / 2024: VEN:5 | merge_as_same_athlete | country_history -cc:VEN | review_id: `athlete_identity_collision_a45f4d7313b28b44` |
| 41 | Samir Serhani | MAG | FRA:2, SUI:13 (tot 15) | SUI | BASSA/MEDIA: possibile outlier o cambio country | FRA 2: Top 12 Final / SUI 13: Dityatin Cup; Koper Challenge Cup | 2019: SUI:21 / 2021: SUI:2 / 2022: SUI:8 / 2023: SUI:25 / 2024: SUI:26 | merge_as_same_athlete | country_correction -cc:SUI | review_id: `athlete_identity_collision_fa3754f614b25141` |
| 42 | Alexander Shatilov | MAG | ISR:33, RUS:1 (tot 34) | ISR | BASSA/MEDIA: possibile outlier o cambio country | ISR 33: European Championships; Israeli Championships; World Championships / RUS 1: European Championships | 2019: ISR:51 / 2020: ISR:9 / 2021: ISR:4 | merge_as_same_athlete | country_correction -cc:ISR | review_id: `athlete_identity_collision_bb2a6e67bf68555d` |
| 43 | Adam Steele | MAG | GBR:7, IRL:49 (tot 56) | IRL | BASSA/MEDIA: possibile outlier o cambio country | GBR 7: English Championships / IRL 49: British Championships; Mersin Challenge Cup; European Championships | 2019: IRL:41 / 2021: IRL:14 / 2022: IRL:11 / 2023: IRL:20 / 2024: IRL:41 / 2025: IRL:14 | merge_as_same_athlete | country_correction -cc:IRL | review_id: `athlete_identity_collision_fb5696f27500767c` |
| 44 | Henji Mboyo | MAG | FRA:1, SUI:36 (tot 37) | SUI | NUOVA REVIEW DOPO NAME-ORDER: fusione automatica `Henji M'Boyo` / `Henji Mboyo` | FRA 1: Top 12 Semi-Final 1 / SUI 36: Baiersbronn Men's Friendly | 2019: SUI:5 / 2021: SUI:34 / 2023: SUI:24 / 2025: SUI:5 | merge_as_same_athlete | country_correction -cc:SUI; Henji Mboyo sempre SUI; review_id: `athlete_identity_collision_cbd1cb5826150c8e` |
| 45 | Marcus Taylor | MAG | GBR:16, IRL:7 (tot 23) | GBR | MEDIA: verificare | GBR 16: British Championships; English Championships / IRL 7: Irish Championships | not found 2019-2025 | merge_as_same_athlete | country_correction -cc:IRL | review_id: `athlete_identity_collision_51b693a22ac237c4` |
| 46 | Gaius Thompson | MAG | GBR:11, GER:3 (tot 14) | GBR | BASSA/MEDIA: possibile outlier o cambio country | GBR 11: British Championships; English Championships; Osijek Challenge Cup / GER 3: 7th Bundesliga | not found 2019-2025 | merge_as_same_athlete | country_correction -cc:GBR | review_id: `athlete_identity_collision_79632be836714957` |
| 47 | Michael Wilner | MAG | ISR:3, USA:2 (tot 5) | ISR | MEDIA: verificare | ISR 3: Israeli Championships / USA 2: Winter Cup Challenge | 2019: USA:3 | merge_as_same_athlete | country_correction -cc:USA | review_id: `athlete_identity_collision_75b1f7e53190a858` |
| 48 | Kimy Xiong | WAG | FRA:5, SUI:1 (tot 6) | FRA | BASSA/MEDIA: possibile outlier o cambio country | FRA 5: Tournoi International / SUI 1: Tournoi International | 2019: FRA:5 | merge_as_same_athlete | country_correction -cc:FRA | review_id: `athlete_identity_collision_7cf2cfbd83cecedb` |

---

## 5. Audit automatico nome/cognome invertiti o formati equivalenti

Questa sezione registra i casi in cui LEVERAGE normalizza automaticamente varianti dello stesso atleta con ordine nome/cognome invertito o formato equivalente. Dopo la decisione metodologica del 24 giugno 2026 questi casi non generano piu una review autonoma per l'ADMIN.

Regola applicata:

- il tool applica automaticamente `merge name order`;
- il nome canonico viene scelto dando priorita a un atleta gia presente nel database;
- se l'atleta non esiste ancora, viene usata la variante piu ricorrente nel file importato;
- se dopo il merge rimangono country diverse, il sistema crea una normale review country `possible_athlete_identity_collision`;
- l'ADMIN decide quindi solo la questione country, non l'inversione del nome.

Statistiche preview 2018:

- merge automatici name-order: 15;
- chiavi atleta/country ricondotte a nome canonico: 17;
- righe risultato normalizzate: 116;
- review name-order manuali: 0;
- review country derivata dal merge e risolta: `Henji Mboyo` (`FRA`, `SUI`) -> `country_correction -cc:SUI`;
- review country fuse: `Takumi Onoshima` + `Onoshima Takumi` -> `Takumi Onoshima` (`BEL`, `ITA`, `JPN`).

| # | Name variants | Disc. | 2018 counts | Post-2018 evidence | Automatic action | Notes |
|---:|---|---|---|---|---|---|
| 1 | Aeadwong Nattipong / Nattipong Aeadwong | MAG | Aeadwong Nattipong (THA:11; tot 11) / Nattipong Aeadwong (THA:10; tot 10) | Nattipong Aeadwong -> 2019: THA:9 | automatic merge name order | no country review generated |
| 2 | Anawin Phothong / Phothong Anawin | MAG | Anawin Phothong (THA:4; tot 4) / Phothong Anawin (THA:8; tot 8) | not found 2019-2025 | automatic merge name order | no country review generated |
| 3 | Arca Mustafa / Mustafa Arca | MAG | Arca Mustafa (TUR:7; tot 7) / Mustafa Arca (TUR:27; tot 27) | Arca Mustafa -> 2019: TUR:7 / Mustafa Arca -> 2019: TUR:46 / 2020: TUR:19 / 2021: TUR:33 | automatic merge name order | no country review generated |
| 4 | Balazs Kiss / Kiss Balazs | MAG | Balazs Kiss (HUN:18; tot 18) / Kiss Balazs (HUN:13; tot 13) | Balazs Kiss -> 2019: HUN:14 / 2020: HUN:29 / 2021: HUN:4 / 2022: HUN:53 / 2023: HUN:44 / 2024: HUN:50 / 2025: HUN:30 | automatic merge name order | no country review generated |
| 5 | Baobenmad Suphacheep / Suphacheep Baobenmad | MAG | Baobenmad Suphacheep (THA:14; tot 14) / Suphacheep Baobenmad (THA:9; tot 9) | Suphacheep Baobenmad -> 2021: THA:7 / 2022: THA:2 / 2023: THA:30 / 2024: THA:7 / 2025: THA:20 | automatic merge name order | no country review generated |
| 6 | Boonpatham Punyapat / Punyapat Boonpatham | MAG | Boonpatham Punyapat (THA:8; tot 8) / Punyapat Boonpatham (THA:7; tot 7) | Punyapat Boonpatham -> 2023: THA:7 | automatic merge name order | no country review generated |
| 7 | Cong Shi / Shi Cong | MAG | Cong Shi (CHN:10; tot 10) / Shi Cong (CHN:33; tot 33) | Shi Cong -> 2019: CHN:15 / 2020: CHN:18 / 2021: CHN:42 / 2022: CHN:10 / 2023: CHN:41 / 2024: CHN:25 / 2025: CHN:64 | automatic merge name order | no country review generated |
| 8 | Enoc Rodelo / Rodelo Enoc | MAG | Enoc Rodelo (MEX:7; tot 7) / Rodelo Enoc (MEX:7; tot 7) | Enoc Rodelo -> 2022: MEX:3 / 2023: MEX:11 | automatic merge name order | no country review generated |
| 9 | Henji M'Boyo / Henji Mboyo | MAG | Henji M'Boyo (FRA:1; tot 1) / Henji Mboyo (SUI:36; tot 36) | Henji Mboyo -> 2019: SUI:5 / 2021: SUI:34 / 2023: SUI:24 / 2025: SUI:5 | automatic merge name order | genera review country `athlete_identity_collision_cbd1cb5826150c8e`, poi risolta con `country_correction -cc:SUI` |
| 10 | Jamorn Prommanee / Prommanee Jamorn | MAG | Jamorn Prommanee (THA:11; tot 11) / Prommanee Jamorn (THA:8; tot 8) | Jamorn Prommanee -> 2019: THA:20 | automatic merge name order | no country review generated |
| 11 | Kaeson Lim / Lim Kaeson | MAG | Kaeson Lim (SGP:3; tot 3) / Lim Kaeson (SGP:3; tot 3) | Kaeson Lim -> 2019: SGP:14 / 2021: SGP:2 / 2023: SGP:29 / Lim Kaeson -> 2019: SGP:7 / 2022: SGP:7 / 2024: SGP:4 / 2025: SGP:5 | automatic merge name order | no country review generated |
| 12 | Kondo Mamoru / Mamoru Kondo | MAG | Kondo Mamoru (JPN:1; tot 1) / Mamoru Kondo (JPN:3; tot 3) | Kondo Mamoru -> 2019: JPN:7 / Mamoru Kondo -> 2019: JPN:19 / 2020: JPN:14 / 2021: JPN:16 / 2022: JPN:17 / 2023: JPN:33 / 2024: JPN:34 / 2025: JPN:14 | automatic merge name order | no country review generated |
| 13 | Lydia May Collins / Lydia-May Collins | WAG | Lydia May Collins (GBR:10; tot 10) / Lydia-May Collins (GBR:3; tot 3) | Lydia-May Collins -> 2019: GBR:10 | automatic merge name order | no country review generated |
| 14 | Maresca Salvatore / Salvatore Maresca | MAG | Maresca Salvatore (ITA:7; tot 7) / Salvatore Maresca (ITA:8; tot 8) | Salvatore Maresca -> 2019: ITA:23 / 2020: ITA:17 / 2021: ITA:19 / 2022: ITA:19 / 2023: ITA:16 / 2024: ITA:15 | automatic merge name order | no country review generated |
| 15 | Onoshima Takumi / Takumi Onoshima | MAG | Onoshima Takumi (BEL:7, ITA:12; tot 19) / Takumi Onoshima (BEL:14, JPN:7; tot 21) | Takumi Onoshima -> 2019: BEL:38 / 2020: BEL:4 / 2021: BEL:17 / 2022: BEL:35 / 2023: BEL:22 / 2024: BEL:3 / 2025: BEL:31 | automatic merge name order | fuse due vecchie review country in `athlete_identity_collision_e7d998bc5bee3b13` |

---

## 6. Regola di aggiornamento documento

Ogni decisione presa durante la revisione deve aggiornare:

1. la colonna `Decision`;
2. la colonna `Notes`;
3. il `Decision log`, se la decisione introduce una regola generale o una scelta metodologica;
4. il diario del popolamento massivo, quando la decisione modifica lo stato del commit 2018.

Tutte le collisioni country 2018 risultano risolte e sono state applicate nel commit controllato del file 2018. Esito post-import: 7.134 athlete creati, 211 event creati, 89.988 result creati, 0 duplicati semantici result post-import.
