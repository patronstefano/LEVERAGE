// The admin workspace uses the same API contracts and controls as entity profiles.
const COPY = {
  center: ["Admin center", "Centro Admin", "Centro Admin", "Centre Admin"],
  entities: ["Manage records", "Gestione record", "Gestionar registros", "Gérer les fiches"],
  delete: ["Delete", "Elimina", "Eliminar", "Supprimer"],
  image: ["Upload image", "Carica immagine", "Subir imagen", "Importer une image"],
  mfaSetup: ["Set up two-factor authentication", "Configura l’autenticazione a due fattori", "Configurar autenticación de dos factores", "Configurer l’authentification à deux facteurs"],
  mfaInstructions: ["Add this secret to your authenticator app, then enter its six-digit code.", "Aggiungi questa chiave alla tua app di autenticazione, poi inserisci il codice a sei cifre.", "Añade esta clave a tu app de autenticación e introduce el código de seis dígitos.", "Ajoutez cette clé à votre application d’authentification, puis saisissez son code à six chiffres."],
  recovery: ["Store these recovery codes securely before continuing. Each code can be used once.", "Conserva questi codici di recupero in un luogo sicuro prima di continuare. Ogni codice può essere usato una sola volta.", "Guarda estos códigos de recuperación antes de continuar. Cada código solo puede usarse una vez.", "Conservez ces codes de récupération avant de continuer. Chaque code est à usage unique."],
  continue: ["Continue", "Continua", "Continuar", "Continuer"],
  name: ["Name", "Nome", "Nombre", "Nom"],
  filename: ["File", "File", "Archivo", "Fichier"],
  "CSV discipline": ["CSV discipline", "Disciplina CSV", "Disciplina CSV", "Discipline CSV"],
  "CSV score": ["CSV score type", "Tipo di punteggio CSV", "Tipo de puntuación CSV", "Type de score CSV"],
  "Create calendar events from year": ["Create calendar events from year", "Crea eventi calendario dall’anno", "Crear eventos desde el año", "Créer les événements à partir de l’année"],
  possible_existing_athlete_match: ["Possible existing athlete", "Possibile atleta già presente", "Posible atleta existente", "Athlète existant possible"],
  possible_athlete_identity_collision: ["Identity and country to review", "Identità e nazionalità da verificare", "Identidad y nacionalidad por revisar", "Identité et nationalité à vérifier"],
  issues: ["Issues", "Problemi", "Problemas", "Problèmes"],
  conflicts: ["Conflicts", "Conflitti", "Conflictos", "Conflits"],
  duplicates: ["Duplicates", "Duplicati", "Duplicados", "Doublons"],
  sample_results: ["Sample results", "Campione risultati", "Muestra de resultados", "Exemples de résultats"],
  athlete_match_review: ["Athlete review", "Verifica atleti", "Revisión de atletas", "Vérification des athlètes"],
  orphan_dscore_review: ["Unmatched D Scores", "D Score non associati", "D Scores sin asociar", "D Scores non associés"],
  first_name: ["First name", "Nome", "Nombre", "Prénom"],
  last_name: ["Last name", "Cognome", "Apellido", "Nom"],
  birth_year: ["Birth year", "Anno di nascita", "Año de nacimiento", "Année de naissance"],
  start_date: ["Start date", "Data di inizio", "Fecha de inicio", "Date de début"],
  end_date: ["End date", "Data di fine", "Fecha de fin", "Date de fin"],
  location: ["Location", "Località", "Localidad", "Lieu"],
  venue: ["Venue", "Sede", "Sede", "Site"],
  discipline: ["Discipline", "Disciplina", "Disciplina", "Discipline"],
  category: ["Category", "Categoria", "Categoría", "Catégorie"],
  level: ["Level", "Livello", "Nivel", "Niveau"],
  format: ["Format", "Formato", "Formato", "Format"],
  round: ["Round", "Fase", "Fase", "Phase"],
  apparatus: ["Apparatus", "Attrezzo", "Aparato", "Agrès"],
  day: ["Day", "Giorno", "Día", "Jour"],
  rank: ["Official rank", "Posizione ufficiale", "Posición oficial", "Rang officiel"],
  vt_attempt: ["Vault attempt", "Tentativo al volteggio", "Intento de salto", "Essai au saut"],
  entity_type: ["Entity", "Entità", "Entidad", "Entité"],
  type: ["Type", "Tipo", "Tipo", "Type"],
  value: ["Value", "Valore", "Valor", "Valeur"],
  role: ["Role", "Ruolo", "Rol", "Rôle"],
  image_url: ["Image URL", "URL immagine", "URL de imagen", "URL de l’image"],
  current_password: ["Current password", "Password attuale", "Contraseña actual", "Mot de passe actuel"],
  new_password: ["New password", "Nuova password", "Nueva contraseña", "Nouveau mot de passe"],
  code: ["Verification code", "Codice di verifica", "Código de verificación", "Code de vérification"],
  final: ["Final", "Finale", "Final", "Finale"],
  qualification: ["Qualification", "Qualifica", "Clasificación", "Qualification"],
  individual: ["Individual", "Individuale", "Individual", "Individuel"],
  team: ["Team", "Squadra", "Equipo", "Équipe"],
  mixed_team: ["Mixed team", "Squadra mista", "Equipo mixto", "Équipe mixte"],
  upcoming: ["Upcoming", "In programma", "Próximos", "À venir"],
  ongoing: ["Ongoing", "In corso", "En curso", "En cours"],
  completed_no_results: ["Completed without results", "Conclusi senza risultati", "Finalizados sin resultados", "Terminés sans résultats"],
  completed_with_results: ["Completed with results", "Conclusi con risultati", "Finalizados con resultados", "Terminés avec résultats"],
  matched_rows: ["Matched rows", "Righe associate", "Filas asociadas", "Lignes associées"],
  parsed_rows: ["Source rows", "Righe sorgente", "Filas de origen", "Lignes source"],
  importable_results: ["Importable results", "Risultati importabili", "Resultados importables", "Résultats importables"],
  would_create_athletes: ["New athletes", "Nuovi atleti", "Nuevos atletas", "Nouveaux athlètes"],
  would_create_events: ["New events", "Nuovi eventi", "Nuevos eventos", "Nouveaux événements"],
  total_athletes: ["Athletes", "Atleti", "Atletas", "Athlètes"],
  total_events: ["Events", "Eventi", "Eventos", "Événements"],
  before: ["Before", "Prima", "Antes", "Avant"],
  after: ["After", "Dopo", "Después", "Après"],
  Penalty: ["Penalty", "Penalità", "Penalización", "Pénalité"],
  countryMismatch: ["Select an athlete with the same discipline.", "Seleziona un atleta della stessa disciplina.", "Selecciona un atleta de la misma disciplina.", "Sélectionnez un athlète de la même discipline."],
  overview: ["Overview", "Panoramica", "Resumen", "Vue d’ensemble"],
  entry: ["Data entry", "Inserimento dati", "Entrada de datos", "Saisie des données"],
  imports: ["Imports", "Importazioni", "Importaciones", "Importations"],
  calendar: ["Calendar", "Calendario", "Calendario", "Calendrier"],
  review: ["Review", "Revisioni", "Revisión", "Révision"],
  notifications: ["Notifications", "Notifiche", "Notificaciones", "Notifications"],
  statistics: ["Site statistics", "Statistiche sito", "Estadísticas", "Statistiques"],
  security: ["Security", "Sicurezza", "Seguridad", "Sécurité"],
  users: ["Users and roles", "Utenti e ruoli", "Usuarios y roles", "Utilisateurs et rôles"],
  merge: ["Merge athletes", "Unisci atleti", "Fusionar atletas", "Fusionner les athlètes"],
  audit: ["Audit and restore", "Audit e ripristino", "Auditoría y restauración", "Audit et restauration"],
  intro: ["Manage data, review changes and follow import activity.", "Gestisci i dati, verifica le modifiche e segui le importazioni.", "Gestiona datos, revisa cambios y sigue las importaciones.", "Gérez les données, vérifiez les modifications et suivez les importations."],
  denied: ["Admin access required.", "Accesso ADMIN richiesto.", "Se requiere acceso ADMIN.", "Accès ADMIN requis."],
  load: ["Load", "Carica", "Cargar", "Charger"],
  more: ["Load more", "Carica altri", "Cargar más", "Charger davantage"],
  save: ["Save", "Salva", "Guardar", "Enregistrer"],
  preview: ["Preview", "Anteprima", "Vista previa", "Aperçu"],
  commit: ["Confirm import", "Conferma importazione", "Confirmar importación", "Confirmer l’importation"],
  report: ["Download report", "Scarica report", "Descargar informe", "Télécharger le rapport"],
  empty: ["No items.", "Nessun elemento.", "Sin elementos.", "Aucun élément."],
  success: ["Operation completed.", "Operazione completata.", "Operación completada.", "Opération terminée."],
  pending: ["Awaiting review", "In attesa di verifica", "Pendiente de revisión", "En attente de vérification"],
  confirm: ["Confirm", "Conferma", "Confirmar", "Confirmer"],
  cancel: ["Cancel", "Annulla", "Cancelar", "Annuler"],
  newEvent: ["New event", "Nuovo evento", "Nuevo evento", "Nouvel événement"],
  newAthlete: ["New athlete", "Nuovo atleta", "Nuevo atleta", "Nouvel athlète"],
  event: ["Event", "Evento", "Evento", "Événement"],
  athlete: ["Athlete", "Atleta", "Atleta", "Athlète"],
  result: ["Result", "Risultato", "Resultado", "Résultat"],
  add: ["Add result", "Aggiungi risultato", "Añadir resultado", "Ajouter un résultat"],
  remove: ["Remove", "Rimuovi", "Quitar", "Supprimer"],
  batch: ["Results awaiting submission", "Risultati da inviare", "Resultados pendientes de envío", "Résultats à envoyer"],
  submit: ["Validate and save results", "Verifica e salva risultati", "Validar y guardar resultados", "Valider et enregistrer les résultats"],
  search: ["Search by name or ID", "Cerca per nome o ID", "Buscar por nombre o ID", "Rechercher par nom ou ID"],
  edit: ["Open profile and tools", "Apri scheda e strumenti", "Abrir ficha y herramientas", "Ouvrir la fiche et les outils"],
  complete: ["Data to complete", "Dati da completare", "Datos por completar", "Données à compléter"],
  suggestions: ["Suggestions", "Suggerimenti", "Sugerencias", "Suggestions"],
  accept: ["Accept", "Accetta", "Aceptar", "Accepter"],
  reject: ["Reject", "Rifiuta", "Rechazar", "Refuser"],
  markRead: ["Mark as read", "Segna come letta", "Marcar como leída", "Marquer comme lue"],
  readAll: ["Mark all as read", "Segna tutte come lette", "Marcar todas como leídas", "Tout marquer comme lu"],
  notify: ["Send result reminders", "Invia promemoria risultati", "Enviar recordatorios", "Envoyer les rappels"],
  source: ["Source athlete ID", "ID atleta da unire", "ID atleta de origen", "ID athlète source"],
  target: ["Destination athlete ID", "ID atleta da mantenere", "ID atleta de destino", "ID athlète à conserver"],
  reason: ["Reason", "Motivazione", "Motivo", "Motif"],
  restore: ["Restore", "Ripristina", "Restaurar", "Restaurer"],
  approve: ["Approve", "Approva", "Aprobar", "Approuver"],
  revert: ["Revert change", "Annulla modifica", "Revertir cambio", "Annuler la modification"],
  details: ["Details", "Dettagli", "Detalles", "Détails"],
  year: ["Year", "Anno", "Año", "Année"],
  status: ["Status", "Stato", "Estado", "Statut"],
  all: ["All", "Tutti", "Todos", "Tous"],
  unresolved: ["Leave for review", "Lascia in revisione", "Dejar en revisión", "Laisser en révision"],
  partial: ["Import valid rows only", "Importa solo le righe valide", "Importar solo filas válidas", "Importer uniquement les lignes valides"],
  identity: ["Identity decision", "Decisione identità", "Decisión de identidad", "Décision d’identité"],
  decision: ["Decision", "Decisione", "Decisión", "Décision"],
  country: ["Country", "Nazione", "País", "Pays"],
  countryStrategy: ["Country handling", "Gestione nazionalità", "Gestión de nacionalidad", "Gestion de nationalité"],
  history: ["Preserve country history", "Conserva storico nazionalità", "Conservar historial", "Conserver l’historique"],
  correction: ["Correct all represented countries", "Correggi tutte le nazionalità rappresentate", "Corregir nacionalidades", "Corriger les nationalités"],
  updateCountry: ["Update current country", "Aggiorna nazionalità attuale", "Actualizar nacionalidad actual", "Actualiser la nationalité"],
  keepCountry: ["Keep current country", "Mantieni nazionalità attuale", "Mantener nacionalidad", "Conserver la nationalité"],
  separate: ["Keep separate", "Mantieni separati", "Mantener separados", "Garder séparés"],
  same: ["Same athlete", "Stesso atleta", "Mismo atleta", "Même athlète"],
  discard: ["Discard", "Scarta", "Descartar", "Écarter"],
  manual: ["Manual match", "Associazione manuale", "Asociación manual", "Association manuelle"],
  mutation: ["Confirm this operation on the selected data?", "Confermi questa operazione sui dati selezionati?", "¿Confirmas esta operación?", "Confirmer cette opération sur les données sélectionnées ?"],
};
export function adminLabel(language, key) {
  return COPY[key]?.[["en", "it", "es", "fr"].indexOf(language)] || COPY[key]?.[0] || key.replaceAll("_", " ");
}

export async function renderAdminMfaSetup(host, token) {
  const { escapeHtml: esc, state } = host;
  const t = (key) => adminLabel(state.language, key);
  const request = async (path, body) => {
    const response = await host.fetchApi(path, {}, {
      method: "POST",
      headers: { Authorization: "Bearer " + token, "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    const result = await response.json();
    if (!response.ok) throw new Error(typeof result.detail === "string" ? result.detail : String(response.status));
    return result;
  };
  const setup = await request("/auth/mfa/setup");
  host.setApp('<section class="admin-center auth-panel"><h1>' + t("mfaSetup") + '</h1><p>' + t("mfaInstructions") +
    '</p><code>' + esc(setup.secret) + '</code><form id="adminMfaEnrollment" class="admin-form-grid"><label>' + t("code") +
    '<input name="code" inputmode="numeric" pattern="[0-9]{6}" autocomplete="one-time-code" required></label><button class="quiet-button outline-command-button" type="submit">' +
    t("confirm") + '</button></form><p id="adminMfaError" role="alert"></p><div id="adminMfaRecovery"></div></section>');
  const form = document.getElementById("adminMfaEnrollment");
  form.onsubmit = async (event) => {
    event.preventDefault();
    const button = form.querySelector("button");
    if (button.disabled) return;
    button.disabled = true;
    try {
      const result = await request("/auth/mfa/confirm", { code: form.elements.code.value });
      form.hidden = true;
      document.getElementById("adminMfaRecovery").innerHTML = '<p>' + t("recovery") + '</p><pre>' + esc(result.recovery_codes.join("\n")) +
        '</pre><button type="button" class="quiet-button outline-command-button" id="adminMfaContinue">' + t("continue") + '</button>';
      document.getElementById("adminMfaContinue").onclick = () => host.completeLoginWithToken(result.access_token);
    } catch (error) {
      document.getElementById("adminMfaError").textContent = error.message;
    } finally { button.disabled = false; }
  };
}

let session = null;
let generation = 0;
export async function renderAdminCenter(host) {
  const { state, escapeHtml: esc } = host;
  const text = (key) => COPY[key] ? adminLabel(state.language, key) : host.t(key) !== key ? host.t(key) : adminLabel(state.language, key);
  if (!["admin", "super_admin"].includes(state.currentUser?.role)) {
    host.setApp(`<p role="alert">${text("denied")}</p><a class="quiet-button" href="#/login">${host.t("signIn")}</a>`);
    return;
  }
  if (session?.user !== state.currentUser.id) session = { user: state.currentUser.id, rows: [], import: null };
  const run = ++generation;
  const active = () => run === generation && state.route.startsWith("/admin");
  const superAdmin = state.currentUser.role === "super_admin";
  const tabs = ["overview", "entry", "entities", "imports", "calendar", "review", "merge", "notifications", "statistics", "security", ...(superAdmin ? ["users", "audit"] : [])];
  const requested = state.route.split("?")[0].split("/")[2];
  const tab = tabs.includes(requested) ? requested : "overview";
  const button = (label, attributes = "") => `<button type="button" class="quiet-button outline-command-button" ${attributes}>${esc(text(label))}</button>`;
  const field = (name, label, type = "text", value = "", required = false) => `<label>${esc(text(label))}<input name="${esc(name)}" type="${type}" value="${esc(value ?? "")}" ${required ? "required" : ""} ${type === "number" ? 'step="any"' : ""}></label>`;
  const select = (name, label, options, value = "") => host.renderAdminSelectControl(name, text(label), value,
    options.map((o) => typeof o === "string" ? { value: o, label: text(o) } : o));
  const form = (id, fields, label = "load") => `<form id="${id}" class="admin-form-grid">${fields}<div class="admin-center-actions"><button type="submit" class="quiet-button outline-command-button">${text(label)}</button></div></form>`;
  const nameOf = (a) => [a.last_name, a.first_name].filter(Boolean).join(" ") || a.name || a.athlete_name || a.event_name || "";
  host.setApp(`<section class="admin-center"><div class="section-heading"><h1>${text("center")}</h1><p>${text("intro")}</p></div>
    <nav class="admin-center-nav" aria-label="${text("center")}">${tabs.map((key) => `<a class="quiet-button outline-command-button ${key === tab ? "is-active" : ""}" ${key === tab ? 'aria-current="page"' : ""} href="#/admin/${key}">${text(key)}</a>`).join("")}</nav>
    <div id="adminFeedback" role="status" aria-live="polite"></div><section id="adminWorkspace" aria-label="${text(tab)}"></section></section>`);
  const root = document.getElementById("adminWorkspace");
  const feedback = (message, error = false) => {
    if (!active()) return;
    const node = document.getElementById("adminFeedback");
    node.className = message ? `admin-center-feedback ${error ? "is-error" : "is-success"}` : "";
    node.textContent = message;
  };
  const api = async (path, { method = "GET", body, params = {} } = {}) => {
    if (!active()) throw new Error("Inactive workspace");
    const multipart = body instanceof FormData;
    const response = await host.fetchApi(path, params, {
      method, headers: host.authHeaders(Boolean(body) && !multipart),
      body: body ? (multipart ? body : JSON.stringify(body)) : undefined,
    });
    const data = response.status === 204 ? null : await response.json();
    if (!response.ok) {
      if (response.status === 401) host.clearAuth();
      const detail = data?.detail || data;
      const error = new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
      error.detail = detail;
      throw error;
    }
    return data;
  };
  const guard = (fn) => async (event) => {
    event?.preventDefault();
    const trigger = event?.currentTarget;
    const controls = trigger?.tagName === "FORM" ? [...trigger.querySelectorAll('button[type="submit"]')] : [trigger];
    if (trigger?.dataset.busy) return;
    if (trigger?.dataset) trigger.dataset.busy = "true";
    controls.forEach((c) => { if (c) c.disabled = true; });
    feedback("");
      try { await fn(event); } catch (error) {
        feedback(error.message, true);
        const dialog = trigger?.closest?.("dialog");
        if (dialog) {
          let notice = dialog.querySelector('[role="alert"]');
          if (!notice) { notice = document.createElement("p"); notice.setAttribute("role", "alert"); dialog.append(notice); }
          notice.textContent = error.message;
        }
      }
    finally { controls.forEach((c) => { if (c) c.disabled = false; }); if (trigger?.dataset) delete trigger.dataset.busy; }
  };
  const onSubmit = (id, fn) => document.getElementById(id)?.addEventListener("submit", guard((e) => fn(Object.fromEntries(new FormData(e.currentTarget)), e.currentTarget)));
  const bind = () => host.bindAdminSelectControls(root);
  const paint = (html) => { if (active()) { root.innerHTML = html; bind(); } };
  const report = (value) => {
    if (value === null || value === undefined) return "<span>—</span>";
    if (typeof value !== "object") return esc(String(value));
    if (Array.isArray(value)) return value.length ? `<ol class="admin-report-list">${value.map((v) => `<li>${report(v)}</li>`).join("")}</ol>` : text("empty");
    return `<dl class="admin-report">${Object.entries(value).filter(([,v]) => v !== null).map(([k,v]) => `<div><dt>${esc(text(k))}</dt><dd>${typeof v === "object" ? `<details><summary>${text("details")}${Array.isArray(v) ? ` (${v.length})` : ""}</summary>${report(v)}</details>` : report(v)}</dd></div>`).join("")}</dl>`;
  };
  const download = (data, filename = "leverage-admin-report.json") => {
    const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
    const a = document.createElement("a"); a.href = url; a.download = filename; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  const confirm = (label, operation) => {
    const dialog = document.createElement("dialog"); dialog.className = "admin-confirm";
    dialog.innerHTML = `<h2>${esc(text(label))}</h2><p>${text("mutation")}</p><div class="admin-center-actions">${button("cancel", 'data-cancel')}${button("confirm", 'data-confirm')}</div>`;
    document.body.append(dialog); dialog.showModal();
    dialog.querySelector("[data-cancel]").onclick = () => dialog.close();
    const close = () => dialog.close();
    window.addEventListener("hashchange", close, { once: true });
    dialog.addEventListener("close", () => { window.removeEventListener("hashchange", close); dialog.remove(); });
    dialog.querySelector("[data-confirm]").onclick = guard(async () => { await operation(); dialog.close(); feedback(text("success")); });
  };
  let schemas;
  const getSchemas = async () => schemas ||= (await api("/openapi.json")).components.schemas;
  const resolve = (schema) => schema.$ref ? schemas[schema.$ref.split("/").pop()] : schema.anyOf ? resolve(schema.anyOf.find((s) => s.type !== "null")) : schema;
  const schemaFields = async (schemaName, values = {}, only = null) => {
    await getSchemas();
    const schema = schemas[schemaName];
    const entries = Object.entries(schema.properties).filter(([key]) => !only || only.includes(key));
    const first = entries.findIndex(([key]) => key === "first_name"), last = entries.findIndex(([key]) => key === "last_name");
    if (first >= 0 && last > first) [entries[first], entries[last]] = [entries[last], entries[first]];
    return entries.map(([key, definition]) => {
      const s = resolve(definition), required = schema.required?.includes(key);
      const caption = text(key);
      if (s.enum) return select(key, caption, (required ? [] : [{ value: "", label: "—" }]).concat(s.enum.map((v) => ({ value: v, label: text(v) }))), values[key] ?? definition.default ?? "");
      if (s.type === "boolean") return `<label><input type="checkbox" name="${key}" ${values[key] ? "checked" : ""}>${esc(caption)}</label>`;
      return field(key, caption, s.format === "date" ? "date" : ["integer", "number"].includes(s.type) ? "number" : "text", values[key] ?? definition.default ?? "", required);
    }).join("");
  };
  const typed = (schemaName, values) => Object.fromEntries(Object.entries(values).map(([key, value]) => {
    const definition = schemas[schemaName]?.properties[key];
    const type = definition ? resolve(definition).type : "string";
    return [key, value === "" ? null : ["integer", "number"].includes(type) ? Number(value) : type === "boolean" ? value === "on" : value];
  }));
  const entityLink = (type, id, label) => `<a class="quiet-button outline-command-button" href="#/${type}/${Number(id)}?from=admin&amp;admin_tools=1&amp;return_to=${encodeURIComponent(state.route)}">${esc(label || text("edit"))}</a>`;
  const wireLookup = (input, output, path, params, choose) => {
    let timer, request = 0;
    input.addEventListener("input", () => {
      clearTimeout(timer); const version = ++request;
      const query = input.value.trim();
      if (query.length < 2) { output.innerHTML = ""; return; }
      timer = setTimeout(async () => {
        try {
          const items = path === "/events/" && /^\d+$/.test(query)
            ? [await api("/events/" + Number(query))]
            : await api(path, { params: { ...params, search: query, query, limit: 12 } });
          if (version !== request || !active() || !output.isConnected) return;
          output.innerHTML = items.map((item, index) => `<button type="button" class="admin-lookup-option" data-choice="${index}">${esc(nameOf(item))} <span>${esc(item.country || "")} · ${item.id || item.athlete_id}</span></button>`).join("");
          output.querySelectorAll("[data-choice]").forEach((b) => b.onclick = () => { choose(items[Number(b.dataset.choice)]); output.innerHTML = ""; });
        } catch (error) { if (version === request) feedback(error.message, true); }
      }, 220);
    });
  };
  try {
    if (tab === "overview") {
      paint(`<div class="admin-overview-links">${tabs.filter((v) => v !== "overview").map((v) => `<a class="admin-overview-link" href="#/admin/${v}"><h2>${text(v)}</h2><span aria-hidden="true">›</span></a>`).join("")}</div>`);
    }
    if (tab === "entry") {
      paint(`<h2>${text("entry")}</h2><div class="admin-center-actions">${button("newEvent", 'id="adminNewEvent"')}${button("newAthlete", 'id="adminNewAthlete"')}</div><div id="adminCreate"></div>
        <div class="admin-lookup">${field("event_search", "search")}<div id="adminEventOptions"></div></div><div id="adminEntry"></div>`);
      const create = async (kind) => {
        const schema = kind === "events" ? "EventCreate" : "AthleteCreate";
        document.getElementById("adminCreate").innerHTML = form("adminCreateForm", await schemaFields(schema), "save"); bind();
        onSubmit("adminCreateForm", async (values) => {
          const created = await api(`/${kind}/`, { method: "POST", body: typed(schema, values) });
          document.getElementById("adminCreate").innerHTML = entityLink(kind, created.id);
          feedback(text("success")); if (kind === "events") await loadEvent(created);
        });
      };
      document.getElementById("adminNewEvent").onclick = guard(() => create("events"));
      document.getElementById("adminNewAthlete").onclick = guard(() => create("athletes"));
      const loadEvent = async (event) => {
        if (session.event?.id !== event.id && session.rows.length) { feedback(text("batch"), true); return; }
        session.event = event;
        document.getElementById("adminCreate").innerHTML = "";
        const options = await api(`/events/${event.id}/manual-entry-options`);
        if (!active()) return;
        const area = document.getElementById("adminEntry");
        area.innerHTML = `<h3>${esc(event.name)}</h3>${entityLink("events", event.id)}
          <div class="admin-form-grid" id="adminContext">${select("discipline", "discipline", options.disciplines)}${select("category", "category", options.categories)}${select("format", "format", options.formats, options.current_context?.format)}${select("round", "round", options.rounds, options.current_context?.round)}${field("day", "day", "number")}</div>
          <form id="adminResultForm" class="admin-form-grid"><div class="admin-lookup admin-form-wide">${field("athlete_search", "search")}<div id="adminAthleteOptions"></div><span id="adminSelectedAthlete"></span></div>
          <details class="admin-form-wide"><summary>${text("newAthlete")}</summary><div class="admin-form-grid">${field("last_name", host.t("lastName"))}${field("first_name", host.t("firstName"))}${field("country", "country")}</div></details>
          ${select("apparatus", "apparatus", options.apparatus_by_discipline[options.disciplines[0]])}
          ${["D_score", "E_score", "Penalty", "Bonus", "score", "rank", "vt_attempt"].map((key) => field(key, key === "score" ? "Final Score" : key, "number", "", key === "score" || key === "E_score" && event.year >= 2026)).join("")}
          <div><button type="submit" class="quiet-button outline-command-button">${text("add")}</button></div></form>
          <h3>${text("batch")}</h3><div id="adminBatch"></div>${button("submit", 'id="adminSubmitResults"')}`;
        bind();
        let selected = null;
        const search = area.querySelector('[name="athlete_search"]');
        area.querySelectorAll('#adminResultForm input[name="first_name"], #adminResultForm input[name="last_name"]').forEach((input) => input.addEventListener("input", () => {
          selected = null; search.value = ""; document.getElementById("adminSelectedAthlete").textContent = "";
        }));
        search.addEventListener("input", () => { selected = null; document.getElementById("adminSelectedAthlete").textContent = ""; });
        wireLookup(search, document.getElementById("adminAthleteOptions"), `/events/${event.id}/result-athlete-suggestions`, {}, (a) => { selected = a; search.value = nameOf(a); document.getElementById("adminSelectedAthlete").textContent = `ID ${a.id || a.athlete_id} · ${a.discipline}`; });
        const context = () => Object.fromEntries([...document.querySelectorAll("#adminContext input")].map((i) => [i.name, i.value]));
        area.querySelector('#adminContext [name="discipline"]').addEventListener("change", () => {
          selected = null; search.value = ""; document.getElementById("adminSelectedAthlete").textContent = "";
          const control = area.querySelector('#adminResultForm [name="apparatus"]').closest(".admin-form-field");
          control.outerHTML = select("apparatus", "apparatus", options.apparatus_by_discipline[context().discipline]); bind();
        });
        const batch = () => {
          document.getElementById("adminBatch").innerHTML = session.rows.map((row, i) => `<div class="admin-center-row"><span>${esc(row.label)} · ${esc(row.data.apparatus)} · ${row.data.score}</span>${button("remove", `data-remove="${i}"`)}</div>`).join("") || text("empty");
          document.getElementById("adminSubmitResults").disabled = !session.rows.length;
          area.querySelectorAll("[data-remove]").forEach((b) => b.onclick = () => { session.rows.splice(Number(b.dataset.remove), 1); batch(); });
        };
        batch();
        onSubmit("adminResultForm", async (v, f) => {
          const c = context();
          if (selected && selected.discipline !== c.discipline) throw new Error(text("countryMismatch"));
          if (!selected && (!v.last_name.trim() || !v.first_name.trim())) throw new Error(text("athlete"));
          const data = { ...c, day: c.day ? Number(c.day) : null, apparatus: v.apparatus };
          for (const key of ["D_score", "E_score", "Penalty", "Bonus", "score", "rank", "vt_attempt"]) data[key] = v[key] === "" ? null : Number(v[key]);
          if (selected) data.athlete_id = selected.id || selected.athlete_id;
          else data.athlete = { last_name: v.last_name.trim(), first_name: v.first_name.trim(), country: v.country || null };
          session.rows.push({ data, label: selected ? nameOf(selected) : `${v.last_name} ${v.first_name}` });
          for (const key of ["D_score", "E_score", "Penalty", "Bonus", "score", "rank"]) f.elements[key].value = "";
          batch();
        });
        document.getElementById("adminSubmitResults").onclick = guard(async () => {
          const saved = await api(`/events/${event.id}/results/bulk`, { method: "POST", body: { results: session.rows.map((r) => r.data) } });
          session.rows = []; batch(); feedback(`${text("success")} ${saved.length}`);
        });
      };
      wireLookup(root.querySelector('[name="event_search"]'), document.getElementById("adminEventOptions"), "/events/", {}, (event) => guard(() => loadEvent(event))());
      if (session.event) await loadEvent(session.event);
    }
    if (tab === "entities") {
      paint(form("adminRecordLookup", select("kind", "type", ["athletes", "events", "results"]) + field("id", "Leverage ID", "number", "", true)) + '<div id="adminRecord"></div>');
      onSubmit("adminRecordLookup", async (v) => {
        const id = Number(v.id), kind = v.kind;
        const record = await api("/" + kind + "/" + id);
        const output = document.getElementById("adminRecord");
        if (kind === "results") {
          const fields = ["athlete_id", "event_id", "represented_country", "discipline", "category", "apparatus", "vt_attempt", "day", "format", "round", "D_score", "E_score", "Penalty", "Bonus", "score", "rank"];
          output.innerHTML = form("adminResultEdit", await schemaFields("ResultUpdate", record, fields), "save");
          onSubmit("adminResultEdit", async (values) => {
            await api("/results/" + id, { method: "PUT", body: typed("ResultUpdate", values) }); feedback(text("success"));
          });
        } else {
          output.innerHTML = entityLink(kind, id, nameOf(record)) +
            form("adminImage", '<label>' + text("image") + '<input type="file" name="file" accept="image/png,image/jpeg,image/webp" required></label>', "image");
          onSubmit("adminImage", async (values, f) => {
            const body = new FormData(); body.append("file", f.elements.file.files[0]);
            await api("/" + kind + "/" + id + "/image", { method: "POST", body }); feedback(text("success"));
          });
        }
        output.insertAdjacentHTML("beforeend", button("delete", 'id="adminDeleteRecord"')); bind();
        document.getElementById("adminDeleteRecord").onclick = () => confirm("delete", async () => {
          await api("/" + kind + "/" + id, { method: "DELETE" }); output.innerHTML = "";
        });
        document.getElementById("adminRecordLookup").addEventListener("change", () => { output.innerHTML = ""; }, { once: true });
      });
    }
    if (tab === "imports") await imports();
    if (tab === "calendar") {
      paint(form("adminCalendarForm", field("year", "year", "number", new Date().getFullYear()) + select("status", "status", [{ value: "", label: text("all") }, ...["upcoming", "ongoing", "completed_no_results", "completed_with_results"]])) + button("notify", 'id="adminNotify"') + '<div id="adminCalendarOutput"></div>');
      const load = async (params) => {
        const data = await api("/admin/calendar", { params: { ...params, limit: 2000 } });
        if (!active()) return;
        document.getElementById("adminCalendarOutput").innerHTML = report(data.summary) + data.events.map((e) => `<div class="admin-center-row"><div><strong>${esc(e.name)}</strong><p>${esc(e.start_date || e.year)} – ${esc(e.end_date || "")} · ${esc(e.status || e.calendar_status || "")} · ${e.result_count ?? 0}</p></div>${entityLink("events", e.id)}</div>`).join("");
      };
      onSubmit("adminCalendarForm", load);
      const grid = document.createElement("div");
      grid.id = "adminCalendarGrid";
      document.getElementById("adminCalendarOutput").before(grid);
      const drawCalendar = async () => {
        const params = Object.fromEntries(new FormData(document.getElementById("adminCalendarForm")));
        const data = await api("/admin/calendar", { params: { ...params, limit: 2000 } });
        if (!active()) return;
        let month = new Date(Number(params.year), 0, 1);
        const draw = () => {
          host.renderHomeCalendar("#adminCalendarGrid", data.events, month, { navScope: "admin" });
          root.querySelectorAll('[data-calendar-nav-scope="admin"]').forEach((b) => b.onclick = () => {
            month = new Date(month.getFullYear(), month.getMonth() + Number(b.dataset.calendarNav), 1); draw();
          });
          root.querySelector('[data-calendar-today-scope="admin"]').onclick = () => { month = new Date(); draw(); };
        };
        draw();
      };
      document.getElementById("adminCalendarForm").addEventListener("submit", guard(drawCalendar));
      await drawCalendar();
      document.getElementById("adminNotify").onclick = () => confirm("notify", () => api("/admin/event-result-reminders/notify", { method: "POST" }));
      await load({ year: new Date().getFullYear() });
    }
    if (tab === "review") {
      const [incomplete, suggestions, duplicates] = await Promise.all([api("/admin/entities-to-complete", { params: { limit: 500 } }), api("/data-suggestions/", { params: { status: "pending" } }), api("/admin/result-duplicate-groups")]);
      paint(`<h2>${text("complete")}</h2>${report({ total_athletes: incomplete.total_athletes, total_events: incomplete.total_events })}${["athletes", "events"].map((kind) => `<details><summary>${host.t(kind === "athletes" ? "navAthletes" : "navEvents")} (${incomplete[kind].length})</summary>${incomplete[kind].map((e) => `<div class="admin-center-row"><span>${esc(nameOf(e))} · ${esc((e.missing_fields || []).join(", "))}</span>${entityLink(kind, e.id)}</div>`).join("")}</details>`).join("")}
        <h2>${text("suggestions")}</h2>${suggestions.map((s) => `<article class="admin-review-row"><div><strong>${esc(s.entity_type)} #${s.entity_id} · ${esc(s.field_name)}</strong><p>${esc(s.evidence || "")}</p>${s.source_url && /^https?:\/\//.test(s.source_url) ? `<a href="${esc(s.source_url)}" target="_blank" rel="noopener noreferrer">${esc(s.source_title || s.source_url)}</a>` : ""}${field(`suggestion_${s.id}`, "value", "text", s.suggested_value)}</div><div class="admin-center-actions">${button("accept", `data-accept="${s.id}"`)}${button("reject", `data-reject="${s.id}"`)}</div></article>`).join("") || text("empty")}<details><summary>${text("result")} · ${text("review")}</summary>${report(duplicates)}</details>`);
      ["accept", "reject"].forEach((action) => root.querySelectorAll(`[data-${action}]`).forEach((b) => b.onclick = guard(async () => {
        const id = Number(b.dataset[action]); await api(`/data-suggestions/${id}/${action}`, { method: "POST", body: action === "accept" ? { value: root.querySelector(`[name="suggestion_${id}"]`).value } : {} });
        b.closest("article").remove(); feedback(text("success"));
      })));
    }
    if (tab === "notifications") {
      paint(button("readAll", 'id="adminReadAll"') + '<div id="adminNotices"></div>' + button("more", 'id="adminMoreNotices"'));
      let offset = 0;
      const load = async () => {
        const items = await api("/notifications/", { params: { limit: 50, offset } }); if (!active()) return;
        const area = document.getElementById("adminNotices");
        area.insertAdjacentHTML("beforeend", items.map((n) => `<article class="admin-center-row"><div><p>${esc(n.message)}</p><small>${esc(n.created_at)}</small>${n.related_event_id ? entityLink("events", n.related_event_id) : ""}${n.related_athlete_id ? entityLink("athletes", n.related_athlete_id) : ""}</div>${!n.is_read ? button("markRead", `data-read="${n.id}"`) : ""}</article>`).join(""));
        offset += items.length; document.getElementById("adminMoreNotices").hidden = items.length < 50;
        area.querySelectorAll("[data-read]").forEach((b) => b.onclick = guard(async () => { await api(`/notifications/${b.dataset.read}/read`, { method: "PUT" }); b.remove(); }));
      };
      document.getElementById("adminReadAll").onclick = guard(async () => { await api("/notifications/read-all", { method: "PUT" }); root.querySelectorAll("[data-read]").forEach((b) => b.remove()); });
      document.getElementById("adminMoreNotices").onclick = guard(load); await load();
    }
    if (tab === "statistics") {
      paint(form("adminStatsForm", field("start_date", host.t("startDate"), "date") + field("end_date", host.t("endDate"), "date")) + '<div id="adminStats"></div>');
      const load = async (params = {}) => { const data = await api("/site-analytics/admin/summary", { params }); if (active()) document.getElementById("adminStats").innerHTML = report(data); };
      onSubmit("adminStatsForm", load); await load();
    }
    if (tab === "merge") {
      paint(form("adminMergeForm", field("source", "source", "number", "", true) + field("target", "target", "number", "", true) + field("reason", "reason"), "preview") + '<div id="adminMergePreview"></div>');
      onSubmit("adminMergeForm", async (v) => {
        const payload = { target_athlete_id: Number(v.target), reason: v.reason || null };
        const result = await api(`/athletes/${Number(v.source)}/merge-preview`, { method: "POST", body: payload });
        const output = document.getElementById("adminMergePreview"); output.innerHTML = report(result) + (result.can_merge ? button("merge", 'id="adminMergeCommit"') : "");
        document.getElementById("adminMergeCommit")?.addEventListener("click", () => confirm("merge", async () => {
          const saved = await api(`/athletes/${Number(v.source)}/merge`, { method: "POST", body: { ...payload, confirm: true } }); output.innerHTML = report(saved);
        }));
        document.getElementById("adminMergeForm").addEventListener("input", () => { output.innerHTML = ""; }, { once: true });
      });
    }
    if (tab === "users") {
      paint(form("adminUsersForm", field("search", "email", "email")) + '<div id="adminUsers"></div>');
      onSubmit("adminUsersForm", async (params) => {
        const users = await api("/admin/users", { params }); if (!active()) return;
        document.getElementById("adminUsers").innerHTML = users.map((u) => `<div class="admin-center-row"><span>${esc(u.email)} · ${esc(u.role)}</span>${select(`role_${u.id}`, "role", ["user", "admin", "super_admin"], u.role)}${button("save", `data-role="${u.id}"`)}</div>`).join("") || text("empty"); bind();
        root.querySelectorAll("[data-role]").forEach((b) => b.onclick = () => confirm("save", async () => { await api(`/admin/users/${b.dataset.role}/role`, { method: "PUT", body: { role: root.querySelector(`[name="role_${b.dataset.role}"]`).value } }); }));
      });
    }
    if (tab === "audit") {
      paint(form("adminAuditForm", select("entity_type", "entity_type", [{ value: "", label: text("all") }, "Athlete", "Event", "Result"]) + field("entity_id", "ID", "number") + select("review_status", "status", [{ value: "", label: text("all") }, "pending", "approved", "reverted"])) + '<div id="adminAudit"></div>' + `<h2>${text("restore")}</h2>` + form("adminRestoreForm", select("type", "entity_type", ["athletes", "events", "results"]) + field("id", "ID", "number", "", true), "restore"));
      onSubmit("adminAuditForm", async (params) => {
        const logs = await api("/admin/audit-logs", { params }); if (!active()) return;
        document.getElementById("adminAudit").innerHTML = logs.map((log) => `<article class="admin-center-row"><div><strong>#${log.id} · ${esc(log.entity_type)} #${log.entity_id} · ${esc(log.action)}</strong><p>${esc(log.created_at)} · ${esc(log.review_status)}</p><details><summary>${text("details")}</summary>${report({ before: log.before_json ? JSON.parse(log.before_json) : null, after: log.after_json ? JSON.parse(log.after_json) : null })}</details>${field(`note_${log.id}`, "reason")}</div>${log.review_status === "pending" && log.admin_id !== state.currentUser.id ? `<div class="admin-center-actions">${button("approve", `data-audit="${log.id}" data-action="approve"`)}${log.action === "update" ? button("revert", `data-audit="${log.id}" data-action="revert"`) : ""}</div>` : ""}</article>`).join("") || text("empty");
        root.querySelectorAll("[data-audit]").forEach((b) => b.onclick = () => confirm(b.dataset.action, async () => { await api(`/admin/audit-logs/${b.dataset.audit}/${b.dataset.action}`, { method: "POST", body: { note: root.querySelector(`[name="note_${b.dataset.audit}"]`).value || null } }); b.closest("article").remove(); }));
      });
      onSubmit("adminRestoreForm", async (v) => confirm("restore", () => api(`/admin/${v.type}/${Number(v.id)}/restore`, { method: "PUT" })));
    }
    if (tab === "security") {
      paint(`<h2>${text("security")}</h2><div id="adminSecurityForms"></div>`);
      const target = document.getElementById("adminSecurityForms");
      const openapi = await api("/openapi.json"); schemas = openapi.components.schemas;
      for (const path of ["/auth/password/change"]) {
        const ref = openapi.paths[path].post.requestBody.content["application/json"].schema.$ref.split("/").pop();
        const id = path.endsWith("confirm") ? "adminMfaConfirm" : "adminPasswordChange";
        target.insertAdjacentHTML("beforeend", `<h3>${path.endsWith("confirm") ? "MFA" : "Password"}</h3>${form(id, await schemaFields(ref), "save")}`);
        target.querySelectorAll('input[name*="password"]').forEach((i) => { i.type = "password"; i.autocomplete = "new-password"; });
        onSubmit(id, async (v, f) => {
          const result = await api(path, { method: "POST", body: typed(ref, v) }); f.reset();
          if (result.access_token) await host.setToken(result.access_token);
          if (path === "/auth/password/change") {
            host.clearAuth(); window.location.hash = "#/login"; return;
          }
          if (result.recovery_codes) document.getElementById("adminMfaOutput").innerHTML = report({ recovery_codes: result.recovery_codes });
          feedback(result.message || text("success"));
        });
      }
      target.insertAdjacentHTML("beforeend", report({ MFA: Boolean(state.currentUser.mfa_enabled) })); bind();
    }
  } catch (error) { feedback(error.message, true); }

  async function imports() {
    paint(form("adminImportForm", select("kind", "type", ["gymternet", "calendar"], session.import?.kind || "gymternet") + '<label>File<input name="file" type="file" accept=".xlsx,.csv" required></label>' + field("year_hint", "year", "number") + select("csv_discipline", "CSV discipline", [{ value: "", label: "—" }, "MAG", "WAG"]) + select("csv_score_kind", "CSV score", [{ value: "", label: "—" }, "final", "dscore"]) + field("create_missing_from_year", "Create calendar events from year", "number"), "preview") + '<div id="adminImportOutput"></div>');
    onSubmit("adminImportForm", async (v, f) => {
      const file = f.elements.file.files[0];
      const params = v.kind === "calendar" ? { create_missing_from_year: v.create_missing_from_year } : { year_hint: v.year_hint, csv_discipline: v.csv_discipline, csv_score_kind: v.csv_score_kind, orphan_review_limit: 5000, athlete_review_limit: 5000 };
      const body = new FormData(); body.append("file", file);
      const preview = await api(`/imports/${v.kind}/preview`, { method: "POST", body, params });
      session.import = { kind: v.kind, file, params, preview, athlete: {}, orphan: {}, visible: 25 }; showImport();
    });
    const importForm = document.getElementById("adminImportForm");
    const syncFields = () => {
      const calendar = importForm.elements.kind.value === "calendar";
      const csv = importForm.elements.file.files[0]?.name.toLowerCase().endsWith(".csv");
      for (const key of ["csv_discipline", "csv_score_kind", "year_hint", "create_missing_from_year"]) {
        importForm.elements[key].closest("label, .admin-form-field").hidden =
          key === "create_missing_from_year" ? !calendar : key === "year_hint" ? calendar : calendar || !csv;
      }
    };
    importForm.addEventListener("change", () => {
      session.import = null;
      document.getElementById("adminImportOutput").innerHTML = "";
      syncFields();
    });
    syncFields();
    if (session.import) showImport();
  }
  function showImport() {
    if (!active()) return;
    const draft = session.import, output = document.getElementById("adminImportOutput"), p = draft.preview;
    const reviewRows = (items, type) => items.slice(0, draft.visible || 25).map((item, index) => {
      const identity = item.problem_type === "possible_athlete_identity_collision";
      const choices = [{ value: "", label: text("unresolved") }, ...(item.suggestions || []).map((s) => ({ value: `suggestion:${s.suggestion_id}`, label: `${text("accept")} · ${s.label || nameOf(s.target_athlete || s.target_result || {})} · ${s.confidence ?? ""}` })),
        ...(type === "orphan" ? [{ value: "discard", label: text("discard") }] : identity ? [{ value: "keep_separate", label: text("separate") }, { value: "merge_as_same_athlete", label: text("same") }] : [{ value: "create_new", label: text("newAthlete") }]), { value: "manual_target", label: text("manual") }];
      return `<article class="admin-import-review" data-review-type="${type}" data-review-index="${index}"><details><summary>${esc(nameOf(item.imported_athlete || item.orphan_dscore || {}))} · ${esc(item.problem_type || item.review_id)}</summary>${report(item)}</details><div class="admin-form-grid">${select("action", "decision", choices, draft[type][item.review_id]?.selection || "")}${type === "athlete" ? field("athlete_id", "target", "number") + select("country_action", "countryStrategy", [{ value: "", label: "—" }, { value: "update_country", label: text("updateCountry") }, { value: "keep_existing_country", label: text("keepCountry") }]) + field("canonical_country", "country") + select("country_strategy", "countryStrategy", [{ value: "preserve_represented_country", label: text("history") }, { value: "correct_all_to_canonical", label: text("correction") }]) : field("target_id", "Target result")}</div></article>`;
    }).join("");
    output.innerHTML = `<h3>${esc(p.filename)}</h3>${report(Object.fromEntries(Object.entries(p).filter(([,v]) => typeof v !== "object")))}
      <details><summary>${text("details")}</summary>${report({ issues: p.issues, conflicts: p.conflicts, duplicates: p.duplicates, rows: p.rows || p.sample_results, duplicate_source_rows: p.duplicate_source_rows, matched_event_source_conflicts: p.matched_event_source_conflicts })}</details>
      ${reviewRows(p.athlete_match_review || [], "athlete")}${reviewRows(p.orphan_dscore_review || [], "orphan")}
      <div class="admin-center-actions">${button("report", 'id="adminExportImport"')}${!p.committed ? button("commit", 'id="adminCommitImport"') : ""}</div>
      ${draft.kind === "gymternet" && !p.committed ? `<label><input id="adminPartialImport" type="checkbox">${text("partial")}</label>` : ""}`;
    if (!p.committed) {
      output.insertAdjacentHTML("beforeend", button("preview", 'id="adminReviewPreview"') + button("more", 'id="adminMoreReviews"') + '<div id="adminReviewedReport"></div>');
      const more = document.getElementById("adminMoreReviews");
      more.hidden = Math.max(p.athlete_match_review?.length || 0, p.orphan_dscore_review?.length || 0) <= (draft.visible || 25);
      more.onclick = () => { draft.visible = (draft.visible || 25) + 25; showImport(); };
      document.getElementById("adminReviewPreview").onclick = guard(async () => {
        const body = new FormData(); body.append("file", draft.file);
        body.append("athlete_match_decisions", JSON.stringify(Object.values(draft.athlete).filter((d) => d.action)));
        body.append("orphan_dscore_decisions", JSON.stringify(Object.values(draft.orphan).filter((d) => d.action)));
        const result = await api(`/imports/${draft.kind}/preview`, { method: "POST", body, params: draft.params });
        draft.reviewed = result;
        document.getElementById("adminReviewedReport").innerHTML = report(result);
      });
    }
    bind();
    output.querySelectorAll("[data-review-type]").forEach((row) => {
      const type = row.dataset.reviewType, items = type === "athlete" ? p.athlete_match_review : p.orphan_dscore_review, item = items[Number(row.dataset.reviewIndex)];
      const lookup = document.createElement("div");
      lookup.className = "admin-lookup";
      lookup.innerHTML = field("target_search", "search") + '<div class="admin-target-options"></div>';
      row.append(lookup);
      if (type === "athlete") {
        wireLookup(lookup.querySelector("input"), lookup.querySelector("div"), "/athletes/", {}, (athlete) => {
          row.querySelector('[name="athlete_id"]').value = athlete.id || athlete.athlete_id;
          const action = row.querySelector('[name="action"]');
          action.value = "manual_target";
          action.closest("[data-admin-select]").querySelector("[data-admin-select-label]").textContent = text("manual");
          action.dispatchEvent(new Event("change", { bubbles: true }));
        });
      } else {
        let timer, version = 0;
        lookup.querySelector("input").oninput = () => {
          clearTimeout(timer); const request = ++version;
          timer = setTimeout(async () => {
            try {
              const body = new FormData(); body.append("file", draft.file);
              const found = await api("/imports/gymternet/review-target-suggestions", { method: "POST", body, params: { ...draft.params, review_id: item.review_id, query: lookup.querySelector("input").value } });
              if (request !== version || !lookup.isConnected) return;
              const list = lookup.querySelector("div");
              list.innerHTML = found.suggestions.map((s, i) => '<button type="button" class="admin-lookup-option" data-target="' + i + '">' + esc(s.label) + '</button>').join("");
              list.querySelectorAll("[data-target]").forEach((b) => b.onclick = () => {
                row.querySelector('[name="target_id"]').value = found.suggestions[Number(b.dataset.target)].target_id;
                const action = row.querySelector('[name="action"]'); action.value = "manual_target";
                action.closest("[data-admin-select]").querySelector("[data-admin-select-label]").textContent = text("manual");
                action.dispatchEvent(new Event("change", { bubbles: true })); list.innerHTML = "";
              });
            } catch (error) { feedback(error.message, true); }
          }, 300);
        };
      }
      const previous = draft[type][item.review_id] || {};
      row.querySelectorAll("input[name]").forEach((input) => {
        if (previous[input.name] !== undefined && input.name !== "action") {
          input.value = previous[input.name];
          const selectLabel = input.closest("[data-admin-select]")?.querySelector("[data-admin-select-label]");
          if (selectLabel) {
            const choice = [...input.closest("[data-admin-select]").querySelectorAll("[data-admin-select-value]")].find((c) => c.dataset.adminSelectValue === input.value);
            if (choice) selectLabel.textContent = choice.textContent.trim();
          }
        }
      });
      row.addEventListener("change", () => {
        draft.reviewed = null;
        const values = Object.fromEntries([...row.querySelectorAll("input[name]")].map((i) => [i.name, i.value]));
        const selection = values.action; let decision = { review_id: item.review_id, selection, ...values };
        if (selection.startsWith("suggestion:")) { decision.action = "accept_suggestion"; decision.suggestion_id = selection.slice(11); }
        if (values.athlete_id) decision.target = { athlete_id: Number(values.athlete_id) };
        draft[type][item.review_id] = decision;
      });
    });
    document.getElementById("adminExportImport").onclick = () => download({ preview: p, athlete_match_decisions: Object.values(draft.athlete), orphan_dscore_decisions: Object.values(draft.orphan) }, `leverage-${draft.kind}-report.json`);
    document.getElementById("adminCommitImport")?.addEventListener("click", () => confirm("commit", async () => {
      const body = new FormData(); body.append("file", draft.file);
      for (const [type, key] of [["athlete", "athlete_match_decisions"], ["orphan", "orphan_dscore_decisions"]]) body.append(key, JSON.stringify(Object.values(draft[type]).filter((d) => d.action)));
      try {
        const result = await api(`/imports/${draft.kind}/commit`, { method: "POST", body, params: { ...draft.params, ...(draft.kind === "gymternet" ? { allow_partial: document.getElementById("adminPartialImport").checked } : {}) } });
        draft.preview = result; showImport();
      } catch (error) {
        if (error.detail && typeof error.detail === "object") { draft.lastError = error.detail; download({ ...draft.preview, commit_error: error.detail }, "leverage-import-conflicts.json"); }
        throw error;
      }
    }));
  }
}
