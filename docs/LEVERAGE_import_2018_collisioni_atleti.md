# LEVERAGE - Revisione collisioni atleta import 2018

Data creazione: 24 giugno 2026  
File sorgente: `import_files/Results 2018.xlsx`  
Stato: revisione manuale aperta, nessun commit 2018 eseguito

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

Ogni riga deve essere verificata e aggiornata con una decisione admin esplicita.

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
| 24 giugno 2026 | Le 48 collisioni 2018 saranno verificate manualmente una per una prima del commit definitivo del file 2018. Nessuna regola generale di merge automatico viene applicata senza validazione admin. |
| 24 giugno 2026 | Il flusso tecnico distingue tra `country_history` e `country_correction`. In caso di cambio reale i Result preservano la country sorgente; in caso di errore data entry i Result vengono importati con `represented_country` corretto senza modificare il file Excel sorgente. |

---

## 4. Tabella revisione collisioni

| # | Athlete | Disc. | Countries/counts | Suggested canonical | Risk | Evidence | Decision | Notes |
|---:|---|---|---|---|---|---|---|---|
| 1 | Sol Lucrecia Acosta | WAG | ITA:8, PAR:5 (tot 13) | ITA | MEDIA: verificare | ITA 8: 2nd Italian Serie A; 3rd Italian Serie A / PAR 5: 1st Italian Serie A | TODO | review_id: `athlete_identity_collision_b81011798c4cc7e5` |
| 2 | Laura Aerts | WAG | BEL:20, NED:8 (tot 28) | BEL | MEDIA: verificare | BEL 20: International GymSport; Leverkusen Cup; Belgian Championships / NED 8: Dutch Championships | TODO | review_id: `athlete_identity_collision_e8b44e9eb87cf02f` |
| 3 | Raman Antropau | MAG | BLR:7, ROU:7 (tot 14) | TIE: BLR/ROU | ALTA: pareggio | BLR 7: World Championships / ROU 7: European Championships | TODO | review_id: `athlete_identity_collision_3beab366ad35a51b` |
| 4 | Stella Ashcroft | WAG | AUS:1, NZL:16 (tot 17) | NZL | BASSA/MEDIA: possibile outlier o cambio country | AUS 1: Melbourne World Cup / NZL 16: Commonwealth Games; Melbourne World Cup | TODO | review_id: `athlete_identity_collision_25975f56a254df1d` |
| 5 | Giulia Bencini | WAG | GER:5, ITA:35 (tot 40) | ITA | BASSA/MEDIA: possibile outlier o cambio country | GER 5: 4th Bundesliga / ITA 35: Italian Gold Championships; 3rd Italian Serie A; Bundesliga Finals | TODO | review_id: `athlete_identity_collision_1e21b709d428c6ad` |
| 6 | Bogi Berg | MAG | DEN:8, FAR:4 (tot 12) | DEN | MEDIA: verificare | DEN 8: Danish Championships / FAR 4: Nordic Championships | TODO | review_id: `athlete_identity_collision_8a67a894dad2aa45` |
| 7 | Astrid Breckmann | WAG | DEN:12, FAR:5 (tot 17) | DEN | MEDIA: verificare | DEN 12: Danish Championships / FAR 5: Nordic Championships | TODO | review_id: `athlete_identity_collision_d35ef3cc9a1b0474` |
| 8 | Pascal Brendel | MAG | FRA:1, GER:7 (tot 8) | GER | BASSA/MEDIA: possibile outlier o cambio country | FRA 1: RD761 Junior International Cup / GER 7: RD761 Junior International Cup | TODO | review_id: `athlete_identity_collision_a059bc4f4341602f` |
| 9 | Corinne Bunagan | WAG | PHI:10, USA:5 (tot 15) | PHI | MEDIA: verificare | PHI 10: World Championships; Asian Games / USA 5: Orlando Qualifier | TODO | review_id: `athlete_identity_collision_dd02abca5bb8c80a` |
| 10 | Georgios Chatziefstathiou | MAG | GRE:37, ITA:5 (tot 42) | GRE | BASSA/MEDIA: possibile outlier o cambio country | GRE 37: Greek Championships; Mediterranean Games; European Championships / ITA 5: 2nd Italian Serie A | TODO | review_id: `athlete_identity_collision_1948eb6f54d4f7fc` |
| 11 | Margaux Daveloose | WAG | BEL:33, FRA:3 (tot 36) | BEL | BASSA/MEDIA: possibile outlier o cambio country | BEL 33: International Gymnix; Elite Gym Massilia; Belgian Championships / FRA 3: Top 12 Series 1 | TODO | review_id: `athlete_identity_collision_4e13666066e5a1c2` |
| 12 | Sofia Diaz | WAG | ESP:2, PUR:2 (tot 4) | TIE: ESP/PUR | ALTA: pareggio | ESP 2: 3rd Spanish League / PUR 2: International Gymnix | TODO | review_id: `athlete_identity_collision_6ce6d4f95456ca9d` |
| 13 | Daniel Fox | MAG | GBR:12, IRL:10 (tot 22) | GBR | ALTA: distribuzione vicina | GBR 12: English Championships; British Championships / IRL 10: Irish Super Championships; Irish Championships | TODO | review_id: `athlete_identity_collision_91a32b244809173d` |
| 14 | Benjamin Gischard | MAG | FRA:3, SUI:38 (tot 41) | SUI | BASSA/MEDIA: possibile outlier o cambio country | FRA 3: Top 12 Semi-Final 2 / SUI 38: Koper Challenge Cup; Swiss Championships; World Championships | TODO | review_id: `athlete_identity_collision_595510b25b9d82f8` |
| 15 | Dmitriy Govorov | MAG | GEO:22, RUS:31 (tot 53) | RUS | ALTA: distribuzione vicina | GEO 22: Dityatin Cup; Voronin Cup / RUS 31: Russian Championships | TODO | review_id: `athlete_identity_collision_45fa3927b3d55b89` |
| 16 | Eyal Indig | MAG | GBR:7, ISR:14 (tot 21) | ISR | MEDIA: verificare | GBR 7: British Championships / ISR 14: Israeli Championships; European Championships | TODO | review_id: `athlete_identity_collision_15c46d1aa44f01b4` |
| 17 | Tan Fu Jie | MAG | MAS:9, TPE:3 (tot 12) | MAS | BASSA/MEDIA: possibile outlier o cambio country | MAS 9: Asian Games; Commonwealth Games; Doha World Cup / TPE 3: Singapore Open | TODO | review_id: `athlete_identity_collision_6adaf0afc5d23ad2` |
| 18 | Yuya Kamoto | MAG | JPN:35, UKR:3 (tot 38) | JPN | BASSA/MEDIA: possibile outlier o cambio country | JPN 35: All-Japan Championships; NHK Trophy; All-Japan Event Championships / UKR 3: Paris Challenge Cup | TODO | review_id: `athlete_identity_collision_023fe0040af9709b` |
| 19 | Noah Kuavita | MAG | BEL:39, FRA:2 (tot 41) | BEL | BASSA/MEDIA: possibile outlier o cambio country | BEL 39: Belgian Championships; Ghent Men's Friendly; Dutch Championships / FRA 2: Top 12 Series 6 | TODO | review_id: `athlete_identity_collision_9cd5b626f59c4803` |
| 20 | Konstantin Kuzovkov | MAG | GEO:59, RUS:17 (tot 76) | GEO | BASSA/MEDIA: possibile outlier o cambio country | GEO 59: European Championships; Dityatin Cup; Voronin Cup / RUS 17: Russian Championships | TODO | review_id: `athlete_identity_collision_92011bd6ade6fdba` |
| 21 | Helge Liebrich | MAG | GER:25, ITA:14 (tot 39) | GER | MEDIA: verificare | GER 25: 2nd Bundesliga; 4th Bundesliga; 3rd Bundesliga / ITA 14: 2nd Italian Serie A; 3rd Italian Serie A | TODO | review_id: `athlete_identity_collision_2e6fce9a3a815be4` |
| 22 | Gioia Meli | WAG | ESP:3, ITA:2 (tot 5) | ESP | MEDIA: verificare | ESP 3: 3rd Spanish League / ITA 2: Italian Gold Championships | TODO | review_id: `athlete_identity_collision_8272ef602eefccae` |
| 23 | Jon Jang Mi | WAG | CHN:5, PRK:6 (tot 11) | PRK | ALTA: distribuzione vicina | CHN 5: Asian Games / PRK 6: Asian Games; World Championships | TODO | review_id: `athlete_identity_collision_9399b65215ab2b12` |
| 24 | Janna Mouffok | WAG | ALG:10, FRA:13 (tot 23) | FRA | ALTA: distribuzione vicina | ALG 10: Varsenare Friendly; World Championships / FRA 13: French Championships; Top 12 Final; Top 12 Series 3 | TODO | review_id: `athlete_identity_collision_3582dd3480be12f6` |
| 25 | Andrei Muntean | MAG | FRA:5, ROU:69 (tot 74) | ROU | BASSA/MEDIA: possibile outlier o cambio country | FRA 5: Top 12 Series 1; Top 12 Series 4; Top 12 Series 2 / ROU 69: World Championships; Romanian Championships; Koper Challenge Cup | TODO | review_id: `athlete_identity_collision_336a1ce6b2e19533` |
| 26 | Sofiia Mykytsei | WAG | GER:10, UKR:11 (tot 21) | UKR | ALTA: distribuzione vicina | GER 10: 3rd Bundesliga; 1st Bundesliga / UKR 11: Ukraine Cup | TODO | review_id: `athlete_identity_collision_0b1e37828cf14ad4` |
| 27 | Yu Nagayosi | MAG | JPN:7, RSA:2 (tot 9) | JPN | BASSA/MEDIA: possibile outlier o cambio country | JPN 7: Africa Safari International / RSA 2: Africa Safari International | TODO | review_id: `athlete_identity_collision_a5604845aadbcb5e` |
| 28 | Sofia Nair | WAG | ALG:12, FRA:5 (tot 17) | ALG | MEDIA: verificare | ALG 12: African Championships; Youth Olympic Games / FRA 5: Elite Gym Massilia | TODO | review_id: `athlete_identity_collision_60e0088d12d68679` |
| 29 | Michael O'Neill | MAG | GBR:14, IRL:13 (tot 27) | GBR | ALTA: distribuzione vicina | GBR 14: English Championships; British Championships / IRL 13: Irish Championships; Irish Super Championships | TODO | review_id: `athlete_identity_collision_83326483e75bd109` |
| 30 | Davide Odomaro | MAG | FRA:6, ITA:14 (tot 20) | ITA | MEDIA: verificare | FRA 6: Top 12 Semi-Final 1; Top 12 Series 4; Top 12 Series 1 / ITA 14: 3rd Italian Serie A; 2nd Italian Serie A; 1st Italian Serie A | TODO | review_id: `athlete_identity_collision_6f1a5dbe55c8df29` |
| 31 | Takumi Onoshima | MAG | BEL:14, JPN:7 (tot 21) | BEL | MEDIA: verificare | BEL 14: Ghent Men's Friendly; Doha World Cup; Dutch Championships / JPN 7: DTB Team Challenge | TODO | review_id: `athlete_identity_collision_b6a14a5addced044` |
| 32 | Ana Palacios | WAG | ESP:8, GUA:25 (tot 33) | GUA | BASSA/MEDIA: possibile outlier o cambio country | ESP 8: Spanish Championships; International GymSport / GUA 25: Central American & Caribbean Games; Pan American Championships; World Championships | TODO | review_id: `athlete_identity_collision_f853884d4d281fd4` |
| 33 | Justin Pesesse | MAG | BEL:26, FRA:3 (tot 29) | BEL | BASSA/MEDIA: possibile outlier o cambio country | BEL 26: European Championships; Belgian Championships; Dutch Championships / FRA 3: Top 12 Series 2 | TODO | review_id: `athlete_identity_collision_c85be8f84adb5998` |
| 34 | Freja Petersen | WAG | DEN:16, FAR:5 (tot 21) | DEN | BASSA/MEDIA: possibile outlier o cambio country | DEN 16: Danish Championships; European Championships / FAR 5: Nordic Championships | TODO | review_id: `athlete_identity_collision_87d99fabcaa70fc3` |
| 35 | Berta Pujadas | WAG | BRA:1, ESP:30 (tot 31) | ESP | BASSA/MEDIA: possibile outlier o cambio country | BRA 1: Gymnasiade / ESP 30: Houston National Invitational; 3rd Spanish League; Gymnasiade | TODO | review_id: `athlete_identity_collision_11ffe28564b3f077` |
| 36 | Rebekka Rein | WAG | DEN:7, FAR:5 (tot 12) | DEN | ALTA: distribuzione vicina | DEN 7: Danish Championships / FAR 5: Nordic Championships | TODO | review_id: `athlete_identity_collision_f78e22a7308fb871` |
| 37 | Sara Ricciardi | WAG | ITA:50, SRB:5 (tot 55) | ITA | BASSA/MEDIA: possibile outlier o cambio country | ITA 50: Italian Championships; Italian Gold Championships; City of Jesolo Trophy / SRB 5: World Championships | TODO | review_id: `athlete_identity_collision_e7667a5cae10cfcb` |
| 38 | Alexey Rostov | MAG | ITA:4, RUS:53 (tot 57) | RUS | BASSA/MEDIA: possibile outlier o cambio country | ITA 4: 2nd Italian Serie A / RUS 53: Russian Championships; 2nd Bundesliga; 5th Bundesliga | TODO | review_id: `athlete_identity_collision_4c3f9d0cce838c57` |
| 39 | Melek Sak | WAG | RUS:5, TUR:5 (tot 10) | TIE: RUS/TUR | ALTA: pareggio | RUS 5: Russian Junior Championships / TUR 5: Turkish Championships | TODO | review_id: `athlete_identity_collision_3c8332ac471efa45` |
| 40 | Deborah Salmina | WAG | ITA:15, VEN:11 (tot 26) | ITA | ALTA: distribuzione vicina | ITA 15: City of Jesolo Trophy; 1st Italian Serie A; 2nd Italian Serie A / VEN 11: Central American & Caribbean Games | TODO | review_id: `athlete_identity_collision_a45f4d7313b28b44` |
| 41 | Samir Serhani | MAG | FRA:2, SUI:13 (tot 15) | SUI | BASSA/MEDIA: possibile outlier o cambio country | FRA 2: Top 12 Final / SUI 13: Dityatin Cup; Koper Challenge Cup | TODO | review_id: `athlete_identity_collision_fa3754f614b25141` |
| 42 | Alexander Shatilov | MAG | ISR:33, RUS:1 (tot 34) | ISR | BASSA/MEDIA: possibile outlier o cambio country | ISR 33: European Championships; Israeli Championships; World Championships / RUS 1: European Championships | TODO | review_id: `athlete_identity_collision_bb2a6e67bf68555d` |
| 43 | Adam Steele | MAG | GBR:7, IRL:49 (tot 56) | IRL | BASSA/MEDIA: possibile outlier o cambio country | GBR 7: English Championships / IRL 49: British Championships; Mersin Challenge Cup; European Championships | TODO | review_id: `athlete_identity_collision_fb5696f27500767c` |
| 44 | Onoshima Takumi | MAG | BEL:7, ITA:12 (tot 19) | ITA | MEDIA: verificare | BEL 7: Belgian Championships / ITA 12: 2nd Italian Serie A; 3rd Italian Serie A; 1st Italian Serie A | TODO | review_id: `athlete_identity_collision_5e68c98718a950c4` |
| 45 | Marcus Taylor | MAG | GBR:16, IRL:7 (tot 23) | GBR | MEDIA: verificare | GBR 16: British Championships; English Championships / IRL 7: Irish Championships | TODO | review_id: `athlete_identity_collision_51b693a22ac237c4` |
| 46 | Gaius Thompson | MAG | GBR:11, GER:3 (tot 14) | GBR | BASSA/MEDIA: possibile outlier o cambio country | GBR 11: British Championships; English Championships; Osijek Challenge Cup / GER 3: 7th Bundesliga | TODO | review_id: `athlete_identity_collision_79632be836714957` |
| 47 | Michael Wilner | MAG | ISR:3, USA:2 (tot 5) | ISR | MEDIA: verificare | ISR 3: Israeli Championships / USA 2: Winter Cup Challenge | TODO | review_id: `athlete_identity_collision_75b1f7e53190a858` |
| 48 | Kimy Xiong | WAG | FRA:5, SUI:1 (tot 6) | FRA | BASSA/MEDIA: possibile outlier o cambio country | FRA 5: Tournoi International / SUI 1: Tournoi International | TODO | review_id: `athlete_identity_collision_7cf2cfbd83cecedb` |

---

## 5. Regola di aggiornamento documento

Ogni decisione presa durante la revisione deve aggiornare:

1. la colonna `Decision`;
2. la colonna `Notes`;
3. il `Decision log`, se la decisione introduce una regola generale o una scelta metodologica;
4. il diario del popolamento massivo, quando la decisione modifica lo stato del commit 2018.

Solo quando tutte le righe saranno risolte si procedera al commit definitivo del file 2018.
