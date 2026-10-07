# LEVERAGE Frontend

Interfaccia del MVP privato in HTML, CSS e JavaScript vanilla, senza build
Node/npm. Include Home, Atleti, Eventi, Rankings, Analytics, Area Personale,
Centro Admin e Centro Super Admin. Lingue: EN, IT, ES, FR.

## Avvio locale

Dalla radice della repository, in due terminali separati:

```bash
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
.venv/bin/python -m http.server 5173 --bind 127.0.0.1 --directory frontend
```

Aprire <http://127.0.0.1:5173/>. In caso di porta frontend occupata, usare
5174. Non avviare un secondo backend sullo stesso database per cambiare
semplicemente la porta della preview. L'API locale predefinita e sulla porta
8000; il vecchio selettore API nel footer non e piu presente.

Gli accessi DEMO e i generatori notifiche nella downbar sono mantenuti
intenzionalmente per la versione privata. Non esporre la configurazione
dimostrativa su Internet.

La [guida di consegna](../docs/LEVERAGE_MVP_privato_consegna.md) descrive
configurazione, backup, ripristino isolato, ambiente verificato e limiti.
