# LEVERAGE Frontend

Minimal dependency-free frontend prototype for the LEVERAGE MVP.

The current machine does not have Node/npm installed, so this first UI layer is plain HTML/CSS/JavaScript. It can be served locally with Python and already talks to the public FastAPI endpoints.

## Local Run

Start the API from the project root:

```bash
uvicorn app.main:app --reload
```

Start the frontend from this folder:

```bash
python3 -m http.server 5173
```

If port 5173 is already busy, use the local fallback port:

```bash
python3 -m http.server 5174
```

Open:

```text
http://localhost:5173
```

or, when using the fallback port:

```text
http://localhost:5174
```

Default API base URL:

```text
http://localhost:8000
```

You can change it from the UI footer during local testing.

## Scope

- Unified Admin center at `#/admin`, accessible from the personal area.
- Manual batches, Gymternet/Calendar review, notifications and data completion.
- Athlete merges, site statistics, super-admin roles, audit and restore.
- First-login MFA enrollment and password change.

See [Admin center](../docs/LEVERAGE_admin_center.md) for permissions and validation.

- Public home screen
- Minimal routing
- Athlete search
- Event calendar browser
- Rankings and official event classifications
- Interactive athlete profile analytics
- Two-athlete MAG/WAG comparison with synchronized radar and trend charts
- Side-by-side and overlaid comparison layouts
- EN/IT/ES/FR language selector
- LEVERAGE brand assets

This folder is intentionally light. It can later be migrated to React/Vite once Node is installed, while preserving the visual direction and API contracts.
