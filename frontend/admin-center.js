import { mountNotificationInbox } from './account-tools.js?v=live-reminders-20260930';
import { athleteFieldOptions } from './athlete-field-options.js?v=20260930';
import { mountResultEditor } from './admin-result-editor.js?v=editor-event-search-20261001';
import { mountWorldGymnasticsScan } from './admin-wg-scan.js?v=20261001';

export function isWorldGymnasticsReviewSuggestion(suggestion) {
  const title = suggestion.entity_type === 'athlete' ? 'World Gymnastics Athlete Profile'
    : suggestion.entity_type === 'event' ? 'World Gymnastics Event Detail' : '';
  if (!title || suggestion.source_title !== title || suggestion.status !== 'pending') return false;
  try {
    const url = new URL(suggestion.source_url);
    return ['http:', 'https:'].includes(url.protocol)
      && (url.hostname === 'gymnastics.sport' || url.hostname.endsWith('.gymnastics.sport'));
  } catch (_) { return false; }
}

// The admin workspace uses the same API contracts and controls as entity profiles.
const COPY = {
  WorldGymnasticsScanControl: ["World Gymnastics scan", "Scansione World Gymnastics", "Escaneo World Gymnastics", "Recherche World Gymnastics"],
  WorldGymnasticsScanJob: ["World Gymnastics match", "Riscontro World Gymnastics", "Coincidencia World Gymnastics", "Correspondance World Gymnastics"],
  center: ["Admin center", "Centro Admin", "Centro Admin", "Centre Admin"],
  superCenter: ["Super Admin center", "Centro Super Admin", "Centro Super Admin", "Centre Super Admin"],
  superIntro: ["Manage access roles, review the audit trail and restore changes.", "Gestisci i ruoli di accesso, verifica lo storico delle operazioni e ripristina le modifiche.", "Gestiona los roles de acceso, revisa el historial y restaura los cambios.", "Gérez les rôles, consultez l’historique et restaurez les modifications."],
  backToAccount: ["Back to Personal Area", "Torna all’Area Personale", "Volver al Área Personal", "Retour à l’Espace personnel"],
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
  activityPeriod: ["Activity period", "Periodo di attività", "Periodo de actividad", "Période d’activité"],
  activity7: ["Last 7 days", "Ultimi 7 giorni", "Últimos 7 días", "7 derniers jours"],
  activity30: ["Last 30 days", "Ultimi 30 giorni", "Últimos 30 días", "30 derniers jours"],
  activity90: ["Last 90 days", "Ultimi 90 giorni", "Últimos 90 días", "90 derniers jours"],
  activityAll: ["Entire audit history", "Intero storico audit", "Todo el historial", "Tout l’historique"],
  activityTotal: ["Logged operations", "Operazioni registrate", "Operaciones registradas", "Opérations enregistrées"],
  activityActions: ["By operation", "Per operazione", "Por operación", "Par opération"],
  activityEntities: ["Data involved", "Dati coinvolti", "Datos afectados", "Données concernées"],
  activityActors: ["Most active authors · up to 10", "Autori più attivi · fino a 10", "Autores más activos · hasta 10", "Auteurs les plus actifs · jusqu’à 10"],
  activityRecent: ["Latest operations · up to 20", "Ultime operazioni · fino a 20", "Últimas operaciones · hasta 20", "Dernières opérations · jusqu’à 20"],
  activityAuthor: ["Author", "Autore", "Autor", "Auteur"],
  activityUnknown: ["Unattributed author", "Autore non attribuito", "Autor no atribuido", "Auteur non attribué"],
  activityDate: ["Date and time", "Data e ora", "Fecha y hora", "Date et heure"],
  activityLast: ["Last activity", "Ultima attività", "Última actividad", "Dernière activité"],
  activityOperation: ["Operation", "Operazione", "Operación", "Opération"],
  activityAudit: ["Open audit and restore", "Apri audit e ripristino", "Abrir auditoría y restauración", "Ouvrir audit et restauration"],
  activityNote: [
    "Audit entries for the selected period, including SUPER ADMIN operations. Counts refer to log entries, not unique modified records. Review status is current; SUPER ADMIN operations are automatically approved. Actions not recorded in the audit are not included.",
    "Voci di audit nel periodo selezionato, incluse le operazioni SUPER ADMIN. I conteggi indicano voci del registro, non record distinti modificati. Lo stato di revisione è quello attuale; le operazioni SUPER ADMIN sono approvate automaticamente. Le azioni non tracciate nell’audit non sono incluse.",
    "Entradas de auditoría del periodo, incluidas las operaciones SUPER ADMIN. Los recuentos son entradas, no registros distintos modificados. El estado de revisión es el actual; SUPER ADMIN se aprueba automáticamente. Las acciones no registradas no se incluyen.",
    "Entrées d’audit de la période, y compris les opérations SUPER ADMIN. Les compteurs portent sur les entrées, non les fiches distinctes modifiées. L’état de révision est actuel ; SUPER ADMIN est approuvé automatiquement. Les actions non tracées sont exclues."
  ],
  approved: ["Approved", "Approvate", "Aprobadas", "Approuvées"],
  reverted: ["Reverted", "Annullate", "Revertidas", "Annulées"],
  create: ["Creation", "Inserimento", "Creación", "Création"],
  update: ["Update", "Aggiornamento", "Actualización", "Mise à jour"],
  soft_delete: ["Deletion", "Eliminazione", "Eliminación", "Suppression"],
  role_update: ["Role change", "Cambio ruolo", "Cambio de rol", "Changement de rôle"],
  revert_update: ["Update reversal", "Annullamento modifica", "Reversión de cambio", "Annulation de modification"],
  update_world_gymnastics: ["World Gymnastics update", "Aggiornamento World Gymnastics", "Actualización World Gymnastics", "Mise à jour World Gymnastics"],
  dataAthletes: ["Athletes", "Atleti", "Atletas", "Athlètes"],
  dataEvents: ["Events", "Eventi", "Eventos", "Événements"],
  dataResults: ["Results and scores", "Risultati e punteggi", "Resultados y puntuaciones", "Résultats et notes"],
  dataTotal: ["Total", "Totali", "Total", "Total"],
  dataVerified: ["World Gymnastics verified", "Verificati World Gymnastics", "Verificados World Gymnastics", "Vérifiés World Gymnastics"],
  dataIncomplete: ["To complete", "Da completare", "Por completar", "À compléter"],
  dataBirthMissing: ["Missing birth year", "Senza anno di nascita", "Sin año de nacimiento", "Sans année de naissance"],
  dataDatesMissing: ["Missing event dates", "Date gara incomplete", "Fechas incompletas", "Dates incomplètes"],
  dataWithResults: ["With results", "Con risultati", "Con resultados", "Avec résultats"],
  dataWithoutResults: ["Without results", "Senza risultati", "Sin resultados", "Sans résultats"],
  dataFinal: ["Final Score recorded", "Final Score registrato", "Final Score registrado", "Final Score enregistré"],
  dataNoFinal: ["Final Score unavailable", "Final Score non disponibile", "Final Score no disponible", "Final Score indisponible"],
  dataD: ["D Score recorded", "D Score registrato", "D Score registrado", "D Score enregistré"],
  dataE: ["E Score recorded", "E Score registrato", "E Score registrado", "E Score enregistré"],
  dataP: ["Penalty recorded", "Penalty registrata", "Penalty registrada", "Penalty enregistrée"],
  dataB: ["Bonus recorded", "Bonus registrato", "Bonus registrado", "Bonus enregistré"],
  dataOverviewNote: [
    "Active records only. To complete includes optional fields, even on verified profiles. Events without results include future events. Score counts include recorded values (including zero), not estimates or derived totals.",
    "Solo record attivi. Da completare include campi facoltativi, anche nei profili verificati. Gli eventi senza risultati comprendono quelli futuri. I conteggi dei punteggi includono valori registrati (anche zero), non stime o totali derivati.",
    "Solo registros activos. Por completar incluye campos opcionales, también en perfiles verificados. Los eventos sin resultados incluyen eventos futuros. Las puntuaciones cuentan valores registrados (incluido cero), no estimaciones ni totales derivados.",
    "Enregistrements actifs uniquement. À compléter inclut les champs facultatifs, même pour les profils vérifiés. Les événements sans résultats incluent ceux à venir. Les notes comptent les valeurs enregistrées (y compris zéro), sans estimations ni totaux calculés."
  ],
  entry: ["New Entity", "Nuova Entità", "Nueva Entidad", "Nouvelle Entité"],
  results: ["Results Editor", "Editor Risultati", "Editor de Resultados", "Éditeur de Résultats"],
  athletes: ["Athletes", "Atleti", "Atletas", "Athlètes"],
  events: ["Events", "Eventi", "Eventos", "Événements"],
  Athlete: ["Athlete", "Atleta", "Atleta", "Athlète"],
  Event: ["Event", "Evento", "Evento", "Événement"],
  Result: ["Result", "Risultato", "Resultado", "Résultat"],
  duplicateResults: ["Possible duplicate results", "Possibili risultati duplicati", "Posibles resultados duplicados", "Résultats potentiellement en double"],
  wgReview: ["World Gymnastics matches", "Riscontri World Gymnastics", "Coincidencias World Gymnastics", "Correspondances World Gymnastics"],
  imports: ["File import", "Importazione file", "Importación de archivos", "Importation de fichiers"],
  calendar: ["Calendar", "Calendario", "Calendario", "Calendrier"],
  review: ["Review", "Revisioni", "Revisión", "Révision"],
  notifications: ["Notifications", "Notifiche", "Notificaciones", "Notifications"],
  statistics: ["Statistics", "Statistiche", "Estadísticas", "Statistiques"],
  importResults: ["Results (The Gymternet)", "Risultati (The Gymternet)", "Resultados (The Gymternet)", "Résultats (The Gymternet)"],
  importCalendar: ["Calendar (The Gymternet)", "Calendario (The Gymternet)", "Calendario (The Gymternet)", "Calendrier (The Gymternet)"],
  chooseFile: ["Choose file", "Scegli file", "Elegir archivo", "Choisir un fichier"],
  noFileSelected: ["No file selected", "Nessun file selezionato", "Ningún archivo seleccionado", "Aucun fichier sélectionné"],
  statsTraffic: ["Traffic", "Traffico", "Tráfico", "Trafic"],
  statsAccounts: ["Accounts", "Account", "Cuentas", "Comptes"],
  visitors: ["Visitors", "Visitatori", "Visitantes", "Visiteurs"],
  sessions: ["Sessions", "Sessioni", "Sesiones", "Sessions"],
  page_views: ["Page views", "Pagine visualizzate", "Vistas de páginas", "Pages vues"],
  searches: ["Searches", "Ricerche", "Búsquedas", "Recherches"],
  athlete_views: ["Athlete profile views", "Schede atleta visualizzate", "Vistas de atletas", "Profils athlètes consultés"],
  event_views: ["Event profile views", "Schede evento visualizzate", "Vistas de eventos", "Fiches événements consultées"],
  dashboard_views: ["Dashboard views", "Dashboard visualizzate", "Vistas del panel", "Tableaux de bord consultés"],
  trackedActions: ["Tracked actions", "Azioni registrate", "Acciones registradas", "Actions enregistrées"],
  average_session_seconds: ["Average session (seconds)", "Sessione media (secondi)", "Sesión media (segundos)", "Session moyenne (secondes)"],
  registered_users: ["Registered", "Registrati", "Registrados", "Inscrits"],
  verified_users: ["Verified", "Verificati", "Verificados", "Vérifiés"],
  unverified_users: ["Unverified", "Non verificati", "Sin verificar", "Non vérifiés"],
  active_users: ["Active", "Attivi", "Activos", "Actifs"],
  inactive_users: ["Inactive", "Inattivi", "Inactivos", "Inactifs"],
  statsWindow: ["Activity in the last {days} days", "Attività negli ultimi {days} giorni", "Actividad en los últimos {days} días", "Activité des {days} derniers jours"],
  top_searches: ["Most frequent searches", "Ricerche più frequenti", "Búsquedas más frecuentes", "Recherches les plus fréquentes"],
  top_athletes: ["Most viewed athletes", "Atleti più visualizzati", "Atletas más vistos", "Athlètes les plus consultés"],
  top_events: ["Most viewed events", "Eventi più visualizzati", "Eventos más vistos", "Événements les plus consultés"],
  users: ["Users and roles", "Utenti e ruoli", "Usuarios y roles", "Utilisateurs et rôles"],
  merge: ["Entity Merge", "Unione Entità", "Unión de Entidades", "Fusion d’Entités"],
  mergeAthlete: ["Merge athlete", "Unione atleta", "Unión de atleta", "Fusion d’athlète"],
  mergeEvent: ["Merge event", "Unione evento", "Unión de evento", "Fusion d’événement"],
  sourceEvent: ["Source event ID", "ID evento da unire", "ID evento de origen", "ID événement source"],
  targetEvent: ["Destination event ID", "ID evento da mantenere", "ID evento de destino", "ID événement à conserver"],
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
let navigationObserver;
export async function renderAdminCenter(host) {
  const { state, escapeHtml: esc } = host;
  const superCenter = /^\/super-admin(?:\/|$)/.test(state.route);
  const baseRoute = superCenter ? "/super-admin" : "/admin";
  const text = (key) => COPY[key] ? adminLabel(state.language, key) : host.t(key) !== key ? host.t(key) : adminLabel(state.language, key);
  if (!["admin", "super_admin"].includes(state.currentUser?.role) || (superCenter && state.currentUser?.role !== "super_admin")) {
    host.authRequiredPage(text("denied"), true);
    return;
  }
  if (session?.user !== state.currentUser.id) session = { user: state.currentUser.id, rows: [], import: null };
  const run = ++generation;
  const active = () => run === generation && (state.route.split('?')[0] === baseRoute || state.route.startsWith(`${baseRoute}/`));
  const superAdmin = state.currentUser.role === "super_admin";
  const tabs = superCenter ? ["overview", "users", "audit", "notifications"] : ["overview", "statistics", "review", "entry", "merge", "results", "imports", "notifications"];
  const requested = state.route.split("?")[0].split("/")[2];
  if (!superCenter && superAdmin && ["users", "audit"].includes(requested)) {
    window.location.replace(`#/super-admin/${requested}`);
    return;
  }
  const tab = tabs.includes(requested) ? requested : "overview";
  const button = (label, attributes = "") => `<button type="button" class="quiet-button outline-command-button" ${attributes}>${esc(text(label))}</button>`;
  const field = (name, label, type = "text", value = "", required = false) => {
    if (["country", "canonical_country", "birth_year", "country_change_year"].includes(name)) return select(name, label, athleteFieldOptions(name.includes("country") && !name.endsWith("year") ? "country" : "birth_year", value), String(value ?? ""));
    return `<label>${esc(text(label))}<input name="${esc(name)}" type="${type}" value="${esc(value ?? "")}" ${required ? "required" : ""} ${type === "number" ? 'step="any"' : ""}></label>`;
  };
  const select = (name, label, options, value = "") => host.renderAdminSelectControl(name, text(label), value,
    options.map((o) => typeof o === "string" ? { value: o, label: text(o) } : o));
  const form = (id, fields, label = "load") => `<form id="${id}" class="admin-form-grid">${fields}<div class="admin-center-actions"><button type="submit" class="quiet-button outline-command-button">${text(label)}</button></div></form>`;
  const toolBlock = (title, content) => `<section class="admin-tool-block"><div class="section-header compact-section-header"><h2>${esc(text(title))}</h2></div>${content}</section>`;
  const emptyState = () => `<div class="empty-state">${esc(text("empty"))}</div>`;
  const nameOf = (a) => [a.last_name, a.first_name].filter(Boolean).join(" ") || a.name || a.athlete_name || a.event_name || "";
  host.setApp(`<div class="detail-topbar"><a class="quiet-button detail-back-button" href="#/account">${esc(text("backToAccount"))}</a></div><section class="admin-center"><div class="section-heading"><h1>${text(superCenter ? "superCenter" : "center")}</h1><p>${text(superCenter ? "superIntro" : "intro")}</p></div>
    <nav class="admin-center-nav" aria-label="${text(superCenter ? "superCenter" : "center")}"><div class="admin-nav-scroll"><div class="segmented-control admin-view-toggle">${tabs.filter((key) => key !== 'notifications').map((key) => `<a class="segmented-option" data-admin-tab="${key}" ${key === tab ? 'aria-current="page"' : ""} href="#${baseRoute}/${key}">${text(key)}</a>`).join("")}<span class="segmented-thumb admin-view-thumb" aria-hidden="true"></span></div></div>
      <button type="button" id="adminNotificationsToggle" class="favorite-button admin-tools-toggle account-tool-button ${tab === 'notifications' ? 'is-open' : ''}" aria-label="${esc(text('notifications'))}" aria-pressed="${tab === 'notifications'}" aria-controls="accountNotifications"><span class="account-tool-icon account-tool-icon-notifications" aria-hidden="true"></span><span id="accountUnreadCount" class="account-unread-count" hidden></span></button></nav>
    <div id="adminFeedback" role="status" aria-live="polite"></div><section id="adminWorkspace" class="panel athlete-admin-panel admin-workspace-panel" aria-label="${text(tab)}" ${tab === 'notifications' ? 'hidden' : ''}><div class="section-header compact-section-header"><h2>${esc(text(tab))}</h2></div></section><div data-account-view-panel ${tab === 'notifications' ? '' : 'hidden'}><section id="accountNotifications"></section></div></section>`);
  document.getElementById('adminNotificationsToggle').onclick = () => { window.location.hash = tab === 'notifications' ? `#${baseRoute}` : `#${baseRoute}/notifications`; };
  const control = document.querySelector('.admin-view-toggle');
  const scroll = document.querySelector('.admin-nav-scroll');
  const thumb = control.querySelector('.admin-view-thumb');
  const positionThumb = (key) => {
    const option = control.querySelector(`[data-admin-tab="${key}"]`);
    thumb.hidden = !option;
    if (!option) return;
    thumb.style.width = `${option.offsetWidth}px`;
    thumb.style.transform = `translateX(${option.offsetLeft}px)`;
  };
  thumb.style.transition = 'none';
  positionThumb(session.navigationCenter === baseRoute ? session.navigationTab || tab : tab);
  scroll.scrollLeft = session.navigationCenter === baseRoute ? session.navigationScroll || 0 : 0;
  // Establish the previous position before animating the newly selected section.
  thumb.getBoundingClientRect();
  thumb.style.transition = '';
  positionThumb(tab);
  session.navigationTab = tab;
  session.navigationCenter = baseRoute;
  const revealSelected = () => {
    positionThumb(tab);
    const option = control.querySelector('[aria-current="page"]');
    if (!option) return;
    if (option.offsetLeft < scroll.scrollLeft) scroll.scrollLeft = option.offsetLeft;
    else if (option.offsetLeft + option.offsetWidth > scroll.scrollLeft + scroll.clientWidth) scroll.scrollLeft = option.offsetLeft + option.offsetWidth - scroll.clientWidth;
  };
  revealSelected();
  scroll.addEventListener('scroll', () => { session.navigationScroll = scroll.scrollLeft; });
  navigationObserver?.disconnect();
  navigationObserver = new ResizeObserver(revealSelected);
  navigationObserver.observe(scroll);
  mountNotificationInbox({ ...host, notificationScope: 'admin' });
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
      error.status = response.status;
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
  const paint = (html) => {
    if (active()) {
      root.innerHTML = `<div class="section-header compact-section-header"><h2>${esc(text(tab))}</h2></div><section class="admin-tool-block admin-workspace-content">${html}</section>`;
      bind();
    }
  };
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
      if (schemaName.startsWith("Athlete") && ["country", "birth_year"].includes(key)) return select(key, caption, athleteFieldOptions(key, values[key]), String(values[key] ?? ""));
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
      if (superCenter) {
        const loadActivity = async () => {
          const data = await api("/admin/activity-overview", { params: { days: session.activityDays ?? 30 } });
          const number = new Intl.NumberFormat(state.language);
          const date = (value) => new Intl.DateTimeFormat(state.language, { dateStyle: "short", timeStyle: "short" }).format(new Date(value.endsWith("Z") ? value : `${value}Z`));
          const author = (row) => `${row.email || text("activityUnknown")}${row.admin_id == null ? "" : ` · #${row.admin_id}`}`;
          const entity = (value) => text(({ Athlete: "athlete", Event: "event", Result: "result", User: "users" })[value] || value);
          const summary = (title, rows) => `<section class="admin-data-group" aria-label="${esc(text(title))}"><h3>${esc(text(title))}</h3><dl><div class="admin-data-total"><dt>${esc(text("dataTotal"))}</dt><dd>${number.format(data.total)}</dd></div>${rows.map(([label, count]) => `<div><dt>${esc(label)}</dt><dd>${number.format(count)}</dd></div>`).join("")}</dl></section>`;
          const activityList = (title, headers, rows) => `<details class="admin-activity-details admin-revision-group"><summary>${esc(text(title))}<span class="admin-revision-count">${number.format(rows.length)}</span></summary><div class="admin-revision-list">${rows.length ? rows.map((cells) => `<article class="account-notification"><div class="account-notification-copy"><p><strong>${esc(cells[0])}</strong></p><dl class="admin-activity-row-details">${cells.slice(1).map((cell, index) => `<div><dt>${esc(text(headers[index + 1]))}</dt><dd>${esc(cell)}</dd></div>`).join("")}</dl></div></article>`).join("") : emptyState()}</div></details>`;
          paint(`<div class="admin-data-overview">
            ${summary("activityTotal", [[text("pending"), data.pending], [text("approved"), data.approved], [text("reverted"), data.reverted]])}
            ${summary("activityActions", data.by_action.map((row) => [text(row.key), row.count]))}
            ${summary("activityEntities", data.by_entity.map((row) => [entity(row.key), row.count]))}
          </div>
          <p class="admin-data-note">${esc(text("activityNote"))}</p>
          ${form("adminActivityPeriod", select("days", "activityPeriod", [
            { value: "7", label: text("activity7") }, { value: "30", label: text("activity30") },
            { value: "90", label: text("activity90") }, { value: "0", label: text("activityAll") },
          ], String(session.activityDays ?? 30)))}
          ${activityList("activityActors", ["activityAuthor", "activityTotal", "pending", "activityLast"], data.actors.map((row) => [author(row), number.format(row.count), number.format(row.pending), date(row.last_activity)]))}
          ${activityList("activityRecent", ["ID", "activityDate", "activityAuthor", "status"], data.recent.map((row) => [`#${row.id} · ${text(row.action)} · ${entity(row.entity_type)}${row.entity_id == null ? "" : ` #${row.entity_id}`}`, date(row.created_at), author(row), text(row.review_status)]))}
          <div class="admin-center-actions"><a class="quiet-button outline-command-button" href="#/super-admin/audit">${esc(text("activityAudit"))}</a></div>`);
          if (!active()) return;
          document.getElementById("adminActivityPeriod").onsubmit = guard(async (event) => {
            session.activityDays = Number(new FormData(event.currentTarget).get("days"));
            await loadActivity();
          });
        };
        await loadActivity();
      } else {
        const data = await api("/admin/data-overview");
        const groups = [
          ["athletes", "dataAthletes", [["verified", "dataVerified"], ["incomplete", "dataIncomplete"], ["missing_birth_year", "dataBirthMissing"], ["mag", "MAG"], ["wag", "WAG"]]],
          ["events", "dataEvents", [["verified", "dataVerified"], ["incomplete", "dataIncomplete"], ["missing_dates", "dataDatesMissing"], ["with_results", "dataWithResults"], ["without_results", "dataWithoutResults"]]],
          ["results", "dataResults", [["with_final_score", "dataFinal"], ["without_final_score", "dataNoFinal"], ["with_d_score", "dataD"], ["with_e_score", "dataE"], ["with_penalty", "dataP"], ["with_bonus", "dataB"]]],
        ];
        const number = new Intl.NumberFormat(state.language);
        paint(`<div class="admin-data-overview">${groups.map(([key, title, rows]) => `<section class="admin-data-group" aria-label="${esc(text(title))}"><h3>${esc(text(title))}</h3><dl><div class="admin-data-total"><dt>${esc(text("dataTotal"))}</dt><dd data-overview-count="${key}.total">${number.format(data[key].total)}</dd></div>${rows.map(([field, label]) => `<div><dt>${esc(text(label))}</dt><dd data-overview-count="${key}.${field}">${number.format(data[key][field])}</dd></div>`).join("")}</dl></section>`).join("")}</div><p class="admin-data-note">${esc(text("dataOverviewNote"))}</p>`);
      }
    }
    if (tab === "entry") {
      paint(`<div class="admin-center-actions"><div class="segmented-control admin-create-toggle" role="group" aria-label="${esc(text("entry"))}" data-active="true" style="--selected-index: 0"><button type="button" class="segmented-option" id="adminNewAthlete" aria-pressed="true">${esc(text("newAthlete"))}</button><button type="button" class="segmented-option" id="adminNewEvent" aria-pressed="false">${esc(text("newEvent"))}</button><span class="segmented-thumb" aria-hidden="true"></span></div></div><div id="adminCreate"></div>`);
      let createRevision = 0;
      const selectCreate = (kind) => {
        document.getElementById("adminNewEvent").setAttribute("aria-pressed", String(kind === "events"));
        document.getElementById("adminNewAthlete").setAttribute("aria-pressed", String(kind === "athletes"));
        const toggle = root.querySelector(".admin-create-toggle");
        toggle.dataset.active = String(Boolean(kind));
        if (kind) toggle.style.setProperty("--selected-index", kind === "athletes" ? "0" : "1");
      };
      const create = async (kind) => {
        const revision = ++createRevision;
        const schema = kind === "events" ? "EventCreate" : "AthleteCreate";
        const fields = await schemaFields(schema);
        if (!active() || revision !== createRevision) return;
        document.getElementById("adminCreate").innerHTML = form("adminCreateForm", fields, "save"); bind();
        selectCreate(kind);
        onSubmit("adminCreateForm", async (values) => {
          const created = await api(`/${kind}/`, { method: "POST", body: typed(schema, values) });
          if (!active() || revision !== createRevision) return;
          document.getElementById("adminCreate").innerHTML = entityLink(kind, created.id);
          selectCreate(null);
          feedback(text("success"));
        });
      };
      document.getElementById("adminNewEvent").onclick = guard(() => create("events"));
      document.getElementById("adminNewAthlete").onclick = guard(() => create("athletes"));
      await create("athletes");
    }
    if (tab === "results") {
      paint('<div id="adminResultEditor"></div>');
      mountResultEditor({ root: root.querySelector('#adminResultEditor'), api, select, field, text, esc, bind, searchUi: host, active, language: state.language, nameOf, feedback,
        initialSelection: new URLSearchParams(state.route.split('?')[1] || ''),
        onSaved: () => { state.globalSearch.payload = null; } });
    }
    if (tab === "imports") await imports();
    if (tab === "review") {
      const [suggestions, duplicates] = await Promise.all([
        api("/data-suggestions/", { params: { status: "pending" } }),
        api("/admin/result-duplicate-groups"),
      ]);
      const groups = new Map();
      for (const suggestion of suggestions.filter(isWorldGymnasticsReviewSuggestion)) {
        const key = `${suggestion.entity_type}:${suggestion.entity_id}`;
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(suggestion);
      }
      const reviewGroups = [];
      for (const items of groups.values()) {
        const first = items[0];
        const kind = first.entity_type === "athlete" ? "athletes" : "events";
        try {
          const entity = await api(`/${kind}/${first.entity_id}`);
          reviewGroups.push({ kind, entity, items });
        } catch (error) { if (error.status !== 404) throw error; }
      }
      const empty = () => `<div class="empty-state">${esc(text("empty"))}</div>`;
      const block = (title, content) => `<section class="admin-tool-block"><div class="section-header compact-section-header"><h2>${esc(title)}</h2></div>${content}</section>`;
      paint(`<div class="admin-revisions">
        ${block(text("duplicateResults"), duplicates.length ? `<details class="admin-revision-group"><summary>${esc(text("details"))}<span class="admin-revision-count">${duplicates.length}</span></summary>${report(duplicates)}</details>` : empty())}
        ${block(text("wgReview"), `<div id="adminWorldGymnasticsScan"></div><div id="adminRevisionSuggestions">${reviewGroups.map(({ kind, entity, items }) => `<details class="admin-revision-group" data-wg-review-group><summary>${esc(nameOf(entity))} · ${esc(text(items[0].entity_type))} #${entity.id}</summary><div class="admin-center-actions">${entityLink(kind, entity.id)}</div>${items.map((s) => `<article class="account-notification"><div class="account-notification-copy"><p><strong>${esc(text(s.field_name))}</strong></p>${s.evidence ? `<p class="admin-revision-meta">${esc(s.evidence)}</p>` : ""}<a class="admin-revision-source" href="${esc(s.source_url)}" target="_blank" rel="noopener noreferrer">${esc(s.source_title)}</a>${s.entity_type === "athlete" && ["country", "birth_year"].includes(s.field_name) ? select(`suggestion_${s.id}`, "value", athleteFieldOptions(s.field_name, s.suggested_value), String(s.suggested_value ?? "")) : field(`suggestion_${s.id}`, "value", "text", s.suggested_value)}</div><div class="account-notification-actions">${button("accept", `data-accept="${s.id}"`)}${button("reject", `data-reject="${s.id}"`)}</div></article>`).join("")}</details>`).join("") || empty()}</div>`)}
        </div>`);
      await mountWorldGymnasticsScan({ root: root.querySelector('#adminWorldGymnasticsScan'), api, esc, language: state.language, active, feedback, route: state.route });
      root.querySelectorAll('[data-accept]').forEach((b) => b.classList.add('admin-accept-button'));
      root.querySelectorAll('[data-reject]').forEach((b) => b.classList.add('filter-clear-button'));
      ["accept", "reject"].forEach((action) => root.querySelectorAll(`[data-${action}]`).forEach((b) => b.onclick = guard(async () => {
        const id = Number(b.dataset[action]); await api(`/data-suggestions/${id}/${action}`, { method: "POST", body: action === "accept" ? { value: root.querySelector(`[name="suggestion_${id}"]`).value } : {} });
        const group = b.closest('[data-wg-review-group]');
        b.closest("article").remove();
        if (!group.querySelector("article")) group.remove();
        const list = document.getElementById("adminRevisionSuggestions");
        if (!list.querySelector("article")) list.innerHTML = empty();
        feedback(text("success"));
      })));
    }
    if (tab === "statistics") {
      paint(form("adminStatsForm", field("start_date", "start_date", "date") + field("end_date", "end_date", "date")) + '<div id="adminStats"></div>');
      const start = root.querySelector('[name="start_date"]');
      const end = root.querySelector('[name="end_date"]');
      start.onchange = () => { end.min = start.value; };
      const number = new Intl.NumberFormat(state.language, { maximumFractionDigits: 1 });
      const block = (title, content) => `<section class="admin-tool-block"><div class="section-header compact-section-header"><h2>${esc(text(title))}</h2></div>${content}</section>`;
      const metrics = (data, keys) => `<dl class="admin-stats-metrics">${keys.map(([key, label = key]) => `<div><dt>${esc(text(label))}</dt><dd>${data[key] == null ? "—" : number.format(data[key])}</dd></div>`).join("")}</dl>`;
      let statsRevision = 0;
      const load = async (params = {}) => {
        const revision = ++statsRevision;
        const data = await api("/site-analytics/admin/summary", { params });
        if (!active() || revision !== statsRevision) return;
        start.value = data.start_date || start.value;
        end.value = data.end_date || end.value;
        end.min = start.value;
        document.getElementById("adminStats").innerHTML =
          block("statsTraffic", metrics(data, ["visitors", "sessions", "page_views", "searches", "athlete_views", "event_views", "dashboard_views", "average_session_seconds"].map((key) => [key]).concat([["total_events", "trackedActions"]]))) +
          block("statsAccounts", metrics(data.users || {}, ["registered_users", "verified_users", "unverified_users", "active_users", "inactive_users"].map((key) => [key])) + `<p class="admin-stats-note">${esc(text("statsWindow").replace("{days}", data.users?.active_window_days ?? 30))}</p>`) +
          ["top_searches", "top_athletes", "top_events"].map((key) => block(key, data[key]?.length ? `<ol class="admin-stats-top">${data[key].map((item) => `<li><span>${esc(item.label)}</span><strong>${number.format(item.count)}</strong></li>`).join("")}</ol>` : `<div class="empty-state">${esc(text("empty"))}</div>`)).join("");
      };
      onSubmit("adminStatsForm", load); await load();
    }
    if (tab === "merge") {
      paint(`<div class="admin-center-actions"><div class="segmented-control admin-create-toggle" role="group" aria-label="${esc(text('merge'))}" data-active="true" style="--selected-index: 0"><button type="button" class="segmented-option" id="adminMergeAthlete" aria-pressed="true">${esc(text('mergeAthlete'))}</button><button type="button" class="segmented-option" id="adminMergeEvent" aria-pressed="false">${esc(text('mergeEvent'))}</button><span class="segmented-thumb" aria-hidden="true"></span></div></div><div id="adminMergeContent"></div>`);
      let mergeRevision = 0;
      const renderMerge = (kind) => {
        ++mergeRevision;
        const isEvent = kind === 'events';
        document.getElementById('adminMergeAthlete').setAttribute('aria-pressed', String(!isEvent));
        document.getElementById('adminMergeEvent').setAttribute('aria-pressed', String(isEvent));
        root.querySelector('.admin-create-toggle').style.setProperty('--selected-index', isEvent ? '1' : '0');
        document.getElementById('adminMergeContent').innerHTML = form('adminMergeForm', field('source', isEvent ? 'sourceEvent' : 'source', 'number', '', true) + field('target', isEvent ? 'targetEvent' : 'target', 'number', '', true) + field('reason', 'reason'), 'preview') + '<div id="adminMergePreview"></div>';
        const output = document.getElementById('adminMergePreview');
        document.getElementById('adminMergeForm').addEventListener('input', () => { ++mergeRevision; output.innerHTML = ''; });
        onSubmit('adminMergeForm', async (v) => {
          const revision = ++mergeRevision;
          const payload = { [isEvent ? 'target_event_id' : 'target_athlete_id']: Number(v.target), reason: v.reason || null };
          const result = await api(`/${kind}/${Number(v.source)}/merge-preview`, {method: 'POST', body: payload});
          if (!active() || revision !== mergeRevision) return;
          const {preview_token, ...visiblePreview} = result;
          output.innerHTML = report(visiblePreview) + (result.can_merge ? button(isEvent ? 'mergeEvent' : 'mergeAthlete', 'id="adminMergeCommit"') : '');
          document.getElementById('adminMergeCommit')?.addEventListener('click', () => confirm(isEvent ? 'mergeEvent' : 'mergeAthlete', async () => {
            if (!active() || revision !== mergeRevision) return;
            const saved = await api(`/${kind}/${Number(v.source)}/merge`, {method: 'POST', body: {...payload, confirm: true, ...(isEvent ? {preview_token: result.preview_token} : {})}});
            if (!active() || revision !== mergeRevision) return;
            ++mergeRevision;
            output.innerHTML = report(saved);
            state.globalSearch.payload = null;
          }));
        });
      };
      document.getElementById('adminMergeAthlete').onclick = () => renderMerge('athletes');
      document.getElementById('adminMergeEvent').onclick = () => renderMerge('events');
      renderMerge('athletes');
    }
    if (tab === "users") {
      paint(form("adminUsersForm", field("search", "email", "email")) + '<div id="adminUsers" class="admin-revision-list"></div>');
      onSubmit("adminUsersForm", async (params) => {
        const users = await api("/admin/users", { params }); if (!active()) return;
        document.getElementById("adminUsers").innerHTML = users.map((u) => `<article class="account-notification"><div class="account-notification-copy"><p><strong>${esc(u.email)}</strong></p><p class="admin-revision-meta">${esc(u.role.replaceAll('_', ' ').toUpperCase())}</p></div><div class="account-notification-actions admin-user-role-actions">${select(`role_${u.id}`, "role", ["user", "admin", "super_admin"], u.role)}${button("save", `data-role="${u.id}"`)}</div></article>`).join("") || emptyState(); bind();
        root.querySelectorAll("[data-role]").forEach((b) => b.onclick = () => confirm("save", async () => { await api(`/admin/users/${b.dataset.role}/role`, { method: "PUT", body: { role: root.querySelector(`[name="role_${b.dataset.role}"]`).value } }); }));
      });
    }
    if (tab === "audit") {
      paint(form("adminAuditForm", select("entity_type", "entity_type", [{ value: "", label: text("all") }, "Athlete", "Event", "Result"]) + field("entity_id", "ID", "number") + select("review_status", "status", [{ value: "", label: text("all") }, "pending", "approved", "reverted"])) + '<div id="adminAudit" class="admin-revision-list"></div>' + toolBlock("restore", form("adminRestoreForm", select("type", "entity_type", ["athletes", "events", "results"]) + field("id", "ID", "number", "", true), "restore")));
      onSubmit("adminAuditForm", async (params) => {
        const logs = await api("/admin/audit-logs", { params }); if (!active()) return;
        document.getElementById("adminAudit").innerHTML = logs.map((log) => `<article class="account-notification"><div class="account-notification-copy"><p><strong>#${log.id} · ${esc(text(log.entity_type))} #${log.entity_id} · ${esc(text(log.action))}</strong></p><p class="admin-revision-meta">${esc(new Date(log.created_at.endsWith('Z') ? log.created_at : `${log.created_at}Z`).toLocaleString(state.language))} · ${esc(text(log.review_status))}</p><details class="admin-revision-group"><summary>${text("details")}</summary>${report({ before: log.before_json ? JSON.parse(log.before_json) : null, after: log.after_json ? JSON.parse(log.after_json) : null })}</details>${field(`note_${log.id}`, "reason")}</div>${log.review_status === "pending" && log.admin_id !== state.currentUser.id ? `<div class="account-notification-actions">${button("approve", `data-audit="${log.id}" data-action="approve"`)}${log.action === "update" && ["Athlete", "Event", "Result"].includes(log.entity_type) ? button("revert", `data-audit="${log.id}" data-action="revert"`) : ""}</div>` : ""}</article>`).join("") || emptyState();
        root.querySelectorAll('[data-action="approve"]').forEach((b) => b.classList.add('admin-accept-button'));
        root.querySelectorAll('[data-action="revert"]').forEach((b) => b.classList.add('filter-clear-button'));
        root.querySelectorAll("[data-audit]").forEach((b) => b.onclick = () => confirm(b.dataset.action, async () => { await api(`/admin/audit-logs/${b.dataset.audit}/${b.dataset.action}`, { method: "POST", body: { note: root.querySelector(`[name="note_${b.dataset.audit}"]`).value || null } }); b.closest("article").remove(); if (!document.querySelector('#adminAudit article')) document.getElementById('adminAudit').innerHTML = emptyState(); }));
      });
      onSubmit("adminRestoreForm", async (v) => confirm("restore", () => api(`/admin/${v.type}/${Number(v.id)}/restore`, { method: "PUT" })));
    }
  } catch (error) { feedback(error.message, true); }

  async function imports() {
    paint(form("adminImportForm", select("kind", "type", [{ value: "gymternet", label: text("importResults") }, { value: "calendar", label: text("importCalendar") }], session.import?.kind || "gymternet") + select("year_hint", "year", [{ value: "", label: "—" }, ...Array.from({ length: new Date().getFullYear() - 1898 }, (_, index) => String(new Date().getFullYear() + 1 - index))], session.import?.params?.year_hint || "") + `<div class="admin-form-field"><span>File</span><div class="admin-file-picker"><input id="adminImportFile" name="file" type="file" accept=".xlsx,.csv" required tabindex="-1" aria-label="${esc(text("chooseFile"))}"><button id="adminChooseFile" type="button" class="quiet-button outline-command-button" aria-controls="adminImportFile" aria-describedby="adminImportFilename">${esc(text("chooseFile"))}</button><span id="adminImportFilename" aria-live="polite">${esc(text("noFileSelected"))}</span></div></div>` + select("csv_discipline", "CSV discipline", [{ value: "", label: "—" }, "MAG", "WAG"]) + select("csv_score_kind", "CSV score", [{ value: "", label: "—" }, "final", "dscore"]) + field("create_missing_from_year", "Create calendar events from year", "number"), "preview") + '<div id="adminImportOutput"></div>');
    onSubmit("adminImportForm", async (v, f) => {
      const file = f.elements.file.files[0];
      const params = v.kind === "calendar" ? { create_missing_from_year: v.create_missing_from_year } : { year_hint: v.year_hint, csv_discipline: v.csv_discipline, csv_score_kind: v.csv_score_kind, orphan_review_limit: 5000, athlete_review_limit: 5000 };
      const body = new FormData(); body.append("file", file);
      const preview = await api(`/imports/${v.kind}/preview`, { method: "POST", body, params });
      session.import = { kind: v.kind, file, params, preview, athlete: {}, orphan: {}, visible: 25 }; showImport();
    });
    const importForm = document.getElementById("adminImportForm");
    const chooseFile = document.getElementById("adminChooseFile");
    chooseFile.onclick = () => importForm.elements.file.click();
    importForm.elements.file.addEventListener("invalid", (event) => {
      event.preventDefault(); chooseFile.focus(); feedback(text("noFileSelected"), true);
    });
    const syncFields = () => {
      document.getElementById("adminImportFilename").textContent = importForm.elements.file.files[0]?.name || text("noFileSelected");
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
