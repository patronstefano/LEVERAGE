import { athleteFieldOptions as localizedAthleteFieldOptions } from './athlete-field-options.js?v=country-names-20261001';
import { mountResultEditor } from './admin-result-editor.js?v=export-search-row-20261006';
import { mountWorldGymnasticsScan } from './admin-wg-scan.js?v=centered-review-load-20261006';
import { bindAuthValidation } from './auth-validation.js?v=admin-validation-20261001';
import { mountEntityReviews } from './admin-entity-reviews.js?v=deferred-reviews-20261006';
import { createAdminReport } from './admin-reports.js?v=incremental-import-20261006';
import { mountImportResolution } from './admin-import-resolution.js?v=independent-review-scopes-20261007';
import { mountImportProgress, mountImportProgressDialog } from './admin-import-progress.js?v=import-dialog-below-actions-20261006';
import { renderAthleteImportComparison, renderImportIdentityComparison, IMPORT_COPY, pendingImportReviews, importIssueScope, sourceReviewCoversIssue, renderAutomaticImportIssues, mountImportReport, renderImportMetrics, renderImportIssues, mountImportAthletes, mountCalendarImportRows, mountCalendarConflicts } from './admin-import-report.js?v=independent-review-scopes-20261007';

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
  ...IMPORT_COPY,
  loadedDuplicateGroups: ['Loaded groups', 'Gruppi caricati', 'Grupos cargados', 'Groupes chargés'],
  involvedResults: ['Results in loaded groups', 'Punteggi nei gruppi caricati', 'Resultados en grupos cargados', 'Résultats des groupes chargés'],
  lastSuperAdmin: ['Last active SUPER ADMIN: role cannot be changed.', 'Ultimo SUPER ADMIN attivo: ruolo non modificabile.', 'Último SUPER ADMIN activo: rol no modificable.', 'Dernier SUPER ADMIN actif : rôle non modifiable.'],
  deleteUser: ['Delete user', 'Elimina utente', 'Eliminar usuario', 'Supprimer l’utilisateur'],
  deleteUserWarning: ['The account will be disabled and its sessions revoked. Audit history and linked data will be retained.', 'L’account sarà disabilitato e le sessioni revocate. Lo storico audit e i dati collegati saranno conservati.', 'La cuenta se desactivará y sus sesiones se revocarán. Se conservarán el historial y los datos vinculados.', 'Le compte sera désactivé et ses sessions révoquées. L’historique et les données liées seront conservés.'],
  userDeleted: ['User deleted', 'Utente eliminato', 'Usuario eliminado', 'Utilisateur supprimé'],
  deactivate: ['Account deactivated', 'Account disabilitato', 'Cuenta desactivada', 'Compte désactivé'],
  auditAuthor: ['Author', 'Autore', 'Autor', 'Auteur'],
  auditCurrentRole: ['Current role', 'Ruolo attuale', 'Rol actual', 'Rôle actuel'],
  auditUnknownAuthor: ['Author unavailable', 'Autore non disponibile', 'Autor no disponible', 'Auteur indisponible'],
  reviewResults: ['Results', 'Risultati', 'Resultados', 'Résultats'],
  swapMergeIds: ['Swap IDs', 'Inverti gli ID', 'Intercambiar los ID', 'Inverser les ID'],
  'junior and senior': ['Junior and Senior', 'Junior e Senior', 'Junior y Senior', 'Junior et Senior'],
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
  activityAll: ["Complete history", "Storico completo", "Historial completo", "Historique complet"],
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
    "Audit entries created in the selected period, including actions by SUPER ADMIN. Each entry is counted once, even when several entries concern the same record. Review statuses reflect their current state; the author's SUPER ADMIN role does not automatically approve an entry. Actions without an audit entry are not counted.",
    "Voci di audit create nel periodo selezionato, incluse le azioni dei SUPER ADMIN. Ogni voce è conteggiata una volta, anche se più voci riguardano la stessa entità. Gli stati di revisione sono quelli attuali; il ruolo SUPER ADMIN dell'autore non approva automaticamente una voce. Le azioni senza voce di audit non sono conteggiate.",
    "Entradas de auditoría creadas en el período seleccionado, incluidas las acciones de SUPER ADMIN. Cada entrada se cuenta una vez, aunque varias correspondan a la misma entidad. Los estados de revisión son los actuales; el rol SUPER ADMIN del autor no aprueba una entrada automáticamente. Las acciones sin entrada de auditoría no se cuentan.",
    "Entrées d'audit créées pendant la période sélectionnée, y compris les actions des SUPER ADMIN. Chaque entrée est comptée une fois, même si plusieurs concernent la même entité. Les états de révision sont ceux en vigueur ; le rôle SUPER ADMIN de l'auteur n'approuve pas automatiquement une entrée. Les actions sans entrée d'audit ne sont pas comptées."
  ],
  approved: ["Approved", "Approvate", "Aprobadas", "Approuvées"],
  reverted: ["Reverted", "Annullate", "Revertidas", "Annulées"],
  create: ["Creation", "Inserimento", "Creación", "Création"],
  update: ["Update", "Aggiornamento", "Actualización", "Mise à jour"],
  soft_delete: ["Deletion", "Eliminazione", "Eliminación", "Suppression"],
  role_update: ["Role change", "Cambio ruolo", "Cambio de rol", "Changement de rôle"],
  revert_update: ["Update reversal", "Annullamento modifica", "Reversión de cambio", "Annulation de modification"],
  revert_create: ["Insertion reversal", "Annullamento inserimento", "Anulación de inserción", "Annulation de création"],
  undoCreate: ["Undo insertion", "Annulla inserimento", "Anular inserción", "Annuler la création"],
  undoMerge: ["Undo merge", "Annulla unione", "Anular unión", "Annuler la fusion"],
  revert_merge: ["Merge reversal", "Annullamento unione", "Anulación de unión", "Annulation de fusion"],
  update_world_gymnastics: ["World Gymnastics update", "Aggiornamento World Gymnastics", "Actualización World Gymnastics", "Mise à jour World Gymnastics"],
  dataAthletes: ["Athletes", "Atleti", "Atletas", "Athlètes"],
  dataEvents: ["Events", "Eventi", "Eventos", "Événements"],
  dataResults: ["Results and scores", "Risultati e punteggi", "Resultados y puntuaciones", "Résultats et notes"],
  dataTotal: ["Total", "Totali", "Total", "Total"],
  dataVerified: ["World Gymnastics verified", "Verificati World Gymnastics", "Verificados World Gymnastics", "Vérifiés World Gymnastics"],
  dataScanned: ["World Gymnastics scanned", "Scansionati World Gymnastics", "Escaneados World Gymnastics", "Analysés World Gymnastics"],
  dataPossibleDuplicates: ["Possible duplicate pairs", "Possibili duplicati", "Posibles duplicados", "Doublons possibles"],
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
    "Active records only. Possible duplicates counts pairs awaiting review, not unique entities. Scanned counts completed World Gymnastics checks, not verified profiles. Events without results include future events. Score counts include recorded values (including zero), not estimates or derived totals.",
    "Solo record attivi. Possibili duplicati conta le coppie da revisionare, non le entità distinte. Scansionati indica i controlli World Gymnastics conclusi, non i profili verificati. Gli eventi senza risultati comprendono quelli futuri. I punteggi contano valori registrati (anche zero), non stime o totali derivati.",
    "Solo registros activos. Posibles duplicados cuenta los pares pendientes de revisión, no las entidades distintas. Escaneados indica comprobaciones World Gymnastics concluidas, no perfiles verificados. Los eventos sin resultados incluyen los futuros. Las puntuaciones cuentan valores registrados (incluido cero), no estimaciones ni totales derivados.",
    "Enregistrements actifs uniquement. Doublons possibles compte les paires à vérifier, pas les entités distinctes. Analysés indique les contrôles World Gymnastics terminés, pas les profils vérifiés. Les événements sans résultats incluent ceux à venir. Les notes comptent les valeurs enregistrées (y compris zéro), sans estimations ni totaux calculés."
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
  review: ["Duplicate Review", "Revisione Duplicati", "Revisión de Duplicados", "Révision des Doublons"],
  'world-gymnastics': ['World Gymnastics', 'World Gymnastics', 'World Gymnastics', 'World Gymnastics'],
  notifications: ["Notifications", "Notifiche", "Notificaciones", "Notifications"],
  statistics: ["Site Statistics", "Statistiche Sito", "Estadísticas del sitio", "Statistiques du site"],
  importResults: ["Results (The Gymternet)", "Risultati (The Gymternet)", "Resultados (The Gymternet)", "Résultats (The Gymternet)"],
  importCalendar: ["Calendar (The Gymternet)", "Calendario (The Gymternet)", "Calendario (The Gymternet)", "Calendrier (The Gymternet)"],
  importLoading: ["Analyzing the file...", "Analisi del file in corso...", "Analizando el archivo...", "Analyse du fichier en cours..."],
  importAnalysisComplete: ["Analysis complete", "Analisi completata", "Análisis completado", "Analyse terminée"],
  importUploading: ["Uploading file", "Caricamento file", "Subiendo archivo", "Envoi du fichier"],
  importNoRows: ["No Gymternet results found. Check the file format, sheet names and year.", "Nessun risultato Gymternet trovato. Controlla formato, nomi dei fogli e anno.", "No se encontraron resultados Gymternet. Revisa el formato, los nombres de las hojas y el año.", "Aucun résultat Gymternet trouvé. Vérifiez le format, les noms des feuilles et l'année."],
  importOnlyDuplicates: ["No new results to import: the file contains results already in LEVERAGE.", "Nessun nuovo risultato da importare: il file contiene risultati già presenti in LEVERAGE.", "No hay resultados nuevos para importar: el archivo contiene resultados ya presentes en LEVERAGE.", "Aucun nouveau résultat à importer : le fichier contient des résultats déjà présents dans LEVERAGE."],
  chooseFile: ["Choose file", "Scegli file", "Elegir archivo", "Choisir un fichier"],
  noFileSelected: ["No file selected", "Nessun file selezionato", "Ningún archivo seleccionado", "Aucun fichier sélectionné"],
  statsTraffic: ["Traffic", "Traffico", "Tráfico", "Trafic"],
  statsOtherZero: ["Other activity", "Altre attività", "Otras actividades", "Autres activités"],
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
  users: ["Users and Roles", "Utenti e Ruoli", "Usuarios y Roles", "Utilisateurs et Rôles"],
  merge: ["Entity Merge", "Unione Entità", "Unión de Entidades", "Fusion d’Entités"],
  mergeAthlete: ["Merge athlete", "Unione atleta", "Unión de atleta", "Fusion d’athlète"],
  mergeEvent: ["Merge event", "Unione evento", "Unión de evento", "Fusion d’événement"],
  sourceEvent: ["Source event ID", "ID evento da unire", "ID evento de origen", "ID événement source"],
  targetEvent: ["Destination event ID", "ID evento da mantenere", "ID evento de destino", "ID événement à conserver"],
  audit: ["Audit and Restore", "Audit e Ripristino", "Auditoría y Restauración", "Audit et Restauration"],
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
  athleteSaved: ["New athlete saved", "Nuovo atleta salvato", "Nuevo atleta guardado", "Nouvel athlète enregistré"],
  eventSaved: ["New event saved", "Nuovo evento salvato", "Nuevo evento guardado", "Nouvel événement enregistré"],
  athleteMerged: ["Athletes merged", "Atleti uniti", "Atletas unidos", "Athlètes fusionnés"],
  eventMerged: ["Events merged", "Eventi uniti", "Eventos unidos", "Événements fusionnés"],
  goToAthlete: ["Go to athlete", "Vai all’atleta", "Ir al atleta", "Voir l’athlète"],
  goToEvent: ["Go to event", "Vai all’evento", "Ir al evento", "Voir l’événement"],
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
  undoDelete: ["Undo deletion", "Annulla eliminazione", "Deshacer eliminación", "Annuler la suppression"],
  revert_delete: ["Deletion reversal", "Annullamento eliminazione", "Anulación de eliminación", "Annulation de suppression"],
  details: ["Details", "Dettagli", "Detalles", "Détails"],
  compareChanges: ["Compare details", "Confronta dettagli", "Comparar detalles", "Comparer les détails"],
  insertedData: ["View inserted data", "Visualizza i dati inseriti", "Ver datos insertados", "Voir les données créées"],
  importDetails: ["Issues and source rows", "Anomalie e righe sorgente", "Problemas y filas de origen", "Anomalies et lignes source"],
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
  const athleteFieldOptions = (field, current) => localizedAthleteFieldOptions(field, current, state.language);
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
  const tabs = superCenter ? ["overview", "statistics", "users", "audit"] : ["overview", "world-gymnastics", "review", "merge", "entry", "results", "imports"];
  const requested = state.route.split("?")[0].split("/")[2];
  if (requested === 'notifications') {
    window.location.replace('#/account?section=notifications');
    return;
  }
  if (!superCenter && superAdmin && ["users", "audit", "statistics"].includes(requested)) {
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
  const emptyState = () => `<div class="empty-state">${esc(text("empty"))}</div>`;
  const nameOf = (a) => [a.last_name, a.first_name].filter(Boolean).join(" ") || a.name || a.athlete_name || a.event_name || "";
  host.setApp(`<div class="detail-topbar"><a class="quiet-button detail-back-button" href="#/account">${esc(text("backToAccount"))}</a></div><section class="admin-center"><div class="section-heading"><h1>${text(superCenter ? "superCenter" : "center")}</h1><p>${text(superCenter ? "superIntro" : "intro")}</p></div>
    <nav class="admin-center-nav" aria-label="${text(superCenter ? "superCenter" : "center")}"><div class="admin-nav-scroll"><div class="segmented-control admin-view-toggle">${tabs.map((key) => `<a class="segmented-option" data-admin-tab="${key}" ${key === tab ? 'aria-current="page"' : ""} href="#${baseRoute}/${key}">${text(key)}</a>`).join("")}<span class="segmented-thumb admin-view-thumb" aria-hidden="true"></span></div></div></nav>
    <div id="adminFeedback" role="status" aria-live="polite"></div><section id="adminWorkspace" class="panel athlete-admin-panel admin-workspace-panel" aria-label="${text(tab)}"><div class="section-header compact-section-header"><h2>${esc(text(tab))}</h2></div></section></section>`);
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
  const root = document.getElementById("adminWorkspace");
  const feedback = (message, error = false) => {
    if (!active()) return;
    const node = document.getElementById("adminFeedback");
    node.className = message ? `admin-center-feedback ${error ? "is-error" : "is-success"}` : "";
    node.textContent = message;
  };
  const api = async (path, { method = "GET", body, params = {}, onUploadProgress, onUploaded, responseType } = {}) => {
    if (!active()) throw new Error("Inactive workspace");
    const multipart = body instanceof FormData;
    const response = multipart && onUploadProgress
      ? await host.uploadApi(path, params, body, onUploadProgress, onUploaded)
      : await host.fetchApi(path, params, {
        method, headers: host.authHeaders(Boolean(body) && !multipart),
        body: body ? (multipart ? body : JSON.stringify(body)) : undefined,
      });
    if (response.ok && responseType === 'blob') return response.blob();
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
  const onSubmit = (id, fn) => {
    const target = document.getElementById(id);
    if (!target) return;
    const message = document.createElement('p');
    message.id = `${id}Validation`;
    message.className = 'admin-form-validation';
    message.setAttribute('role', 'alert');
    target.append(message);
    const validation = bindAuthValidation(target, message, () => state.language, {generic: true});
    target.addEventListener('submit', guard(async (e) => {
      if (!validation.validate()) return;
      try { await fn(Object.fromEntries(new FormData(e.currentTarget)), e.currentTarget); }
      catch (error) {
        if (error.status === 422) validation.serverError(error, 'admin');
        else { validation.showError(error.message); }
      }
    }));
  };
  const bind = () => host.bindAdminSelectControls(root);
  const paint = (html) => {
    if (active()) {
      root.innerHTML = `<div class="section-header compact-section-header"><h2>${esc(text(tab))}</h2></div><section class="admin-tool-block admin-workspace-content">${html}</section>`;
      bind();
    }
  };
  const report = createAdminReport({text, esc, language: state.language});
  const confirm = (label, operation, showSuccess = true, explanation = '') => {
    const dialog = document.createElement("dialog"); dialog.className = "admin-confirm";
    dialog.innerHTML = `<h2>${esc(text(label))}</h2><p>${text("mutation")}</p><div class="admin-center-actions">${button("cancel", 'data-cancel')}${button("confirm", 'data-confirm')}</div>`;
    document.body.append(dialog); dialog.showModal();
    if (explanation) dialog.querySelector('p').textContent = explanation;
    dialog.querySelector("[data-cancel]").onclick = () => dialog.close();
    const close = () => dialog.close();
    window.addEventListener("hashchange", close, { once: true });
    dialog.addEventListener("close", () => { window.removeEventListener("hashchange", close); dialog.remove(); });
    dialog.querySelector("[data-confirm]").onclick = guard(async () => { await operation(dialog); dialog.close(); if (showSuccess) feedback(text("success")); });
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
        let activityRevision = 0;
        const loadActivity = async () => {
          const revision = ++activityRevision;
          const data = await api("/admin/activity-overview", { params: { days: session.activityDays ?? 30 } });
          if (!active() || revision !== activityRevision) return;
          const number = new Intl.NumberFormat(state.language);
          const entity = (value) => text(({ Athlete: "athlete", Event: "event", Result: "result", User: "users" })[value] || value);
          const summary = (title, rows, showTotal = false) => `<section class="admin-data-group" aria-label="${esc(text(title))}"><h3>${esc(text(title))}</h3><dl>${showTotal ? `<div class="admin-data-total"><dt class="sr-only">${esc(text(title))}</dt><dd>${number.format(data.total)}</dd></div>` : ""}${rows.map(([label, count]) => `<div><dt>${esc(label)}</dt><dd>${number.format(count)}</dd></div>`).join("")}</dl></section>`;
          paint(`<div id="adminActivityPeriod" class="admin-form-grid">${select("days", "activityPeriod", [
            { value: "7", label: text("activity7") }, { value: "30", label: text("activity30") },
            { value: "90", label: text("activity90") }, { value: "0", label: text("activityAll") },
          ], String(session.activityDays ?? 30))}</div><div class="admin-data-overview admin-activity-overview">
            ${summary("activityTotal", [[text("pending"), data.pending], [text("approved"), data.approved], [text("reverted"), data.reverted]], true)}
            ${summary("activityActions", data.by_action.map((row) => [text(row.key), row.count]))}
            ${summary("activityEntities", data.by_entity.map((row) => [entity(row.key), row.count]))}
          </div>
          <p class="admin-data-note">${esc(text("activityNote"))}</p>`);
          if (!active()) return;
          root.querySelector('#adminActivityPeriod [name=days]').onchange = async (event) => {
            session.activityDays = Number(event.target.value);
            try { await loadActivity(); } catch (error) { if (active()) feedback(error.message, true); }
          };
        };
        await loadActivity();
      } else {
        const data = await api("/admin/data-overview");
        const groups = [
          ["athletes", "dataAthletes", [["verified", "dataVerified"], ["scanned_world_gymnastics", "dataScanned"], ["possible_duplicates", "dataPossibleDuplicates"], ["missing_birth_year", "dataBirthMissing"], ["mag", "MAG"], ["wag", "WAG"]]],
          ["events", "dataEvents", [["verified", "dataVerified"], ["scanned_world_gymnastics", "dataScanned"], ["possible_duplicates", "dataPossibleDuplicates"], ["missing_dates", "dataDatesMissing"], ["with_results", "dataWithResults"], ["without_results", "dataWithoutResults"]]],
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
          const isAthlete = kind === "athletes";
          document.getElementById("adminCreate").innerHTML = `<div class="admin-center-feedback is-success" role="status">${esc(text(isAthlete ? "athleteSaved" : "eventSaved"))}</div><div class="admin-center-actions">${entityLink(kind, created.id, text(isAthlete ? "goToAthlete" : "goToEvent"))}</div>`;
          selectCreate(null);
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
    if (tab === "review" || tab === 'world-gymnastics') {
      const wgOnly = tab === 'world-gymnastics';
      const [suggestions, duplicates] = await Promise.all([
        wgOnly ? api("/data-suggestions/", { params: { status: "pending" } }) : [],
        wgOnly ? [] : api("/admin/result-duplicate-groups"),
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
      const block = (title, content, id = '') => `<section class="admin-tool-block"${id ? ` id="${id}" hidden` : ''}>${title ? `<div class="section-header compact-section-header"><h2>${esc(title)}</h2></div>` : ''}${content}</section>`;
      paint(`<div class="admin-center-actions"><div class="segmented-control admin-create-toggle admin-review-toggle" role="group" aria-label="${esc(text('review'))}" data-active="true" style="--selected-index: 0"><button type="button" class="segmented-option" data-review-entity="athlete" aria-pressed="true">${esc(text('athletes'))}</button><button type="button" class="segmented-option" data-review-entity="event" aria-pressed="false">${esc(text('events'))}</button><button type="button" class="segmented-option" data-review-entity="result" aria-pressed="false">${esc(text('reviewResults'))}</button><span class="segmented-thumb" aria-hidden="true"></span></div></div><div class="admin-revisions">
        <section id="adminEntityReviews" class="admin-tool-block"></section>
        ${block('', duplicates.length ? `<details class="admin-revision-group"><summary>${esc(text("details"))}<span class="admin-revision-count">${duplicates.length}</span></summary>${report(duplicates)}</details>` : empty(), 'adminResultReviews')}
        ${block('', `<div id="adminWorldGymnasticsScan"></div><div id="adminRevisionSuggestions">${reviewGroups.map(({ kind, entity, items }) => `<details class="admin-revision-group" data-wg-review-group data-review-kind="${items[0].entity_type}"><summary>${esc(nameOf(entity))} · ${esc(text(items[0].entity_type))} #${entity.id}</summary><div class="admin-center-actions">${entityLink(kind, entity.id)}</div>${items.map((s) => `<article class="account-notification"><div class="account-notification-copy"><p><strong>${esc(text(s.field_name))}</strong></p>${s.evidence ? `<p class="admin-revision-meta">${esc(s.evidence)}</p>` : ""}<a class="admin-revision-source" href="${esc(s.source_url)}" target="_blank" rel="noopener noreferrer">${esc(s.source_title)}</a>${s.entity_type === "athlete" && ["country", "birth_year"].includes(s.field_name) ? select(`suggestion_${s.id}`, "value", athleteFieldOptions(s.field_name, s.suggested_value), String(s.suggested_value ?? "")) : field(`suggestion_${s.id}`, "value", "text", s.suggested_value)}</div><div class="account-notification-actions">${button("accept", `data-accept="${s.id}"`)}${button("reject", `data-reject="${s.id}"`)}</div></article>`).join("")}</details>`).join("") || empty()}</div>`)}
        </div>`);
      let reviewEntity = new URLSearchParams(state.route.split('?')[1] || '').get('entity_type') === 'event' ? 'event' : 'athlete';
      const reviewToggle = root.querySelector('.admin-review-toggle');
      reviewToggle.setAttribute('aria-label', text(tab));
      if (wgOnly) {
        root.querySelector('#adminEntityReviews').remove();
        root.querySelector('#adminResultReviews').remove();
        root.querySelector('[data-review-entity="result"]').remove();
        reviewToggle.classList.remove('admin-review-toggle');
      } else {
        root.querySelector('#adminWorldGymnasticsScan').closest('.admin-tool-block').remove();
        const count = new Intl.NumberFormat(state.language);
        root.querySelector('#adminResultReviews').insertAdjacentHTML('afterbegin', `<dl class="admin-stats-metrics admin-duplicate-recap" data-result-recap><div><dt>${esc(text('loadedDuplicateGroups'))}</dt><dd>${count.format(duplicates.length)}</dd></div><div><dt>${esc(text('involvedResults'))}</dt><dd>${count.format(duplicates.reduce((sum, group) => sum + (group.count || 0), 0))}</dd></div></dl>`);
      }
      const updateReviewVisibility = () => {
        const list = root.querySelector('#adminRevisionSuggestions');
        if (!list) return;
        const groups = [...list.querySelectorAll('[data-wg-review-group]')];
        groups.forEach((group) => { group.hidden = group.dataset.reviewKind !== reviewEntity; });
        list.querySelector('.empty-state')?.remove();
        list.hidden = !groups.some((group) => !group.hidden);
      };
      const selectReviewEntity = async (kind) => {
        reviewEntity = kind;
        root.querySelectorAll('[data-review-entity]').forEach((button) => {
          button.setAttribute('aria-pressed', String(button.dataset.reviewEntity === kind));
          button.parentElement.style.setProperty('--selected-index', String(['athlete', 'event', 'result'].indexOf(kind)));
        });
        const resultsSelected = kind === 'result';
        if (!wgOnly) {
          root.querySelector('#adminResultReviews').hidden = !resultsSelected;
          root.querySelector('#adminEntityReviews').hidden = resultsSelected;
        }
        updateReviewVisibility();
        if (resultsSelected) return;
        const reviewActive = () => active() && reviewEntity === kind;
        if (!wgOnly) {
          const pairRoot = document.createElement('section');
          pairRoot.id = 'adminEntityReviews';
          pairRoot.className = 'admin-tool-block';
          root.querySelector('#adminEntityReviews').replaceWith(pairRoot);
          mountEntityReviews({root: pairRoot, kind, api, esc, language: state.language, active: reviewActive, route: state.route});
          return;
        }
        const scanRoot = document.createElement('div');
        scanRoot.id = 'adminWorldGymnasticsScan';
        root.querySelector('#adminWorldGymnasticsScan').replaceWith(scanRoot);
        await mountWorldGymnasticsScan({ root: scanRoot, api, esc, language: state.language, active: reviewActive, feedback, route: state.route, entityType: kind, noteHost: scanRoot.parentElement, controlsHost: reviewToggle.parentElement });
      };
      root.querySelectorAll('[data-review-entity]').forEach((button) => {
        button.onclick = () => { if (reviewEntity !== button.dataset.reviewEntity) selectReviewEntity(button.dataset.reviewEntity); };
      });
      await selectReviewEntity(reviewEntity);
      root.querySelectorAll('[data-accept]').forEach((b) => b.classList.add('admin-accept-button'));
      root.querySelectorAll('[data-reject]').forEach((b) => b.classList.add('filter-clear-button'));
      ["accept", "reject"].forEach((action) => root.querySelectorAll(`[data-${action}]`).forEach((b) => b.onclick = guard(async () => {
        const id = Number(b.dataset[action]); await api(`/data-suggestions/${id}/${action}`, { method: "POST", body: action === "accept" ? { value: root.querySelector(`[name="suggestion_${id}"]`).value } : {} });
        const group = b.closest('[data-wg-review-group]');
        b.closest("article").remove();
        if (!group.querySelector("article")) group.remove();
        updateReviewVisibility();
        feedback(text("success"));
      })));
    }
    if (tab === "statistics") {
      paint(`<div id="adminStatsForm" class="admin-form-grid">${select("days", "activityPeriod", [
        { value: "7", label: text("activity7") }, { value: "30", label: text("activity30") },
        { value: "90", label: text("activity90") }, { value: "0", label: text("activityAll") },
      ], String(session.statisticsDays ?? 30))}</div><div id="adminStats"></div>`);
      const number = new Intl.NumberFormat(state.language, { maximumFractionDigits: 1 });
      const metrics = (data, keys) => `<dl>${keys.map(([key, label = key], index) => `<div${index === 0 ? ' class="admin-data-total"' : ''}><dt>${esc(text(label))}</dt><dd>${data[key] == null ? "—" : number.format(data[key])}</dd></div>`).join("")}</dl>`;
      const trafficMetrics = (data) => {
        const keys = ["visitors", "sessions", "page_views", "searches", "athlete_views", "event_views", "dashboard_views", "average_session_seconds"];
        const shown = keys.filter((key) => data[key] !== 0);
        const zeroCount = keys.length - shown.length;
        return `<dl><div class="admin-data-total"><dt>${esc(text("trackedActions"))}</dt><dd>${number.format(data.total_events)}</dd></div>${shown.map((key) => `<div><dt>${esc(text(key))}</dt><dd>${data[key] == null ? "—" : number.format(data[key])}</dd></div>`).join("")}${zeroCount ? `<div><dt>${esc(text("statsOtherZero"))}</dt><dd>0</dd></div>` : ""}</dl>`;
      };
      const block = (title, content) => `<section class="admin-data-group" aria-label="${esc(text(title))}"><h3>${esc(text(title))}</h3>${content}</section>`;
      let statsRevision = 0;
      const load = async () => {
        const revision = ++statsRevision;
        const data = await api("/site-analytics/admin/summary", { params: { days: session.statisticsDays ?? 30 } });
        if (!active() || revision !== statsRevision) return;
        document.getElementById("adminStats").innerHTML =
          '<div class="admin-data-overview admin-site-statistics">' +
          block("statsTraffic", trafficMetrics(data)) +
          block("statsAccounts", metrics(data.users || {}, ["registered_users", "verified_users", "unverified_users", "active_users", "inactive_users"].map((key) => [key]))) + '</div>';
      };
      root.querySelector('#adminStatsForm [name=days]').onchange = async (event) => {
        session.statisticsDays = Number(event.target.value);
        try { await load(); } catch (error) { if (active()) feedback(error.message, true); }
      };
      await load();
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
        const reviewParams = new URLSearchParams(state.route.split('?')[1] || '');
        const fromReview = reviewParams.get('entity_type') === (isEvent ? 'event' : 'athlete');
        const reviewId = (key) => fromReview && /^[1-9][0-9]*$/.test(reviewParams.get(key) || '') ? reviewParams.get(key) : '';
        const swap = `<button type="button" id="adminMergeSwap" class="quiet-button outline-command-button admin-merge-swap" aria-label="${esc(text('swapMergeIds'))}" title="${esc(text('swapMergeIds'))}"><span aria-hidden="true"></span></button>`;
        document.getElementById('adminMergeContent').innerHTML = form('adminMergeForm', '<div class="admin-merge-ids">' + field('source', isEvent ? 'sourceEvent' : 'source', 'number', reviewId('source'), true) + swap + field('target', isEvent ? 'targetEvent' : 'target', 'number', reviewId('target'), true) + '</div>' + field('reason', 'reason'), 'preview') + '<div id="adminMergePreview"></div>';
        const output = document.getElementById('adminMergePreview');
        const mergeForm = document.getElementById('adminMergeForm');
        const actions = mergeForm.querySelector('.admin-center-actions');
        const clearCommit = () => actions.querySelector('#adminMergeCommit')?.remove();
        mergeForm.addEventListener('input', () => { ++mergeRevision; output.innerHTML = ''; clearCommit(); });
        document.getElementById('adminMergeSwap').addEventListener('click', () => {
          const source = mergeForm.elements.namedItem('source');
          const target = mergeForm.elements.namedItem('target');
          [source.value, target.value] = [target.value, source.value];
          source.dispatchEvent(new Event('input', {bubbles: true}));
          target.dispatchEvent(new Event('input', {bubbles: true}));
        });
        onSubmit('adminMergeForm', async (v) => {
          const revision = ++mergeRevision;
          clearCommit();
          const payload = { [isEvent ? 'target_event_id' : 'target_athlete_id']: Number(v.target), reason: v.reason || null };
          const result = await api(`/${kind}/${Number(v.source)}/merge-preview`, {method: 'POST', body: payload});
          if (!active() || revision !== mergeRevision) return;
          const {preview_token, ...visiblePreview} = result;
          output.innerHTML = report(visiblePreview);
          if (result.can_merge) actions.insertAdjacentHTML('beforeend', button(isEvent ? 'mergeEvent' : 'mergeAthlete', 'id="adminMergeCommit"'));
          document.getElementById('adminMergeCommit')?.addEventListener('click', () => confirm(isEvent ? 'mergeEvent' : 'mergeAthlete', async () => {
            if (!active() || revision !== mergeRevision) return;
            const saved = await api(`/${kind}/${Number(v.source)}/merge`, {method: 'POST', body: {...payload, confirm: true, ...(isEvent ? {preview_token: result.preview_token} : {})}});
            if (!active() || revision !== mergeRevision) return;
            ++mergeRevision;
            const target = isEvent ? saved.target_event : saved.target_athlete;
            document.getElementById('adminMergeContent').innerHTML = `<div class="admin-center-feedback is-success" role="status">${esc(text(isEvent ? 'eventMerged' : 'athleteMerged'))}</div><div class="admin-center-actions">${entityLink(kind, target.id, text(isEvent ? 'goToEvent' : 'goToAthlete'))}</div>`;
            state.globalSearch.payload = null;
          }, false));
        });
      };
      document.getElementById('adminMergeAthlete').onclick = () => renderMerge('athletes');
      document.getElementById('adminMergeEvent').onclick = () => renderMerge('events');
      renderMerge(new URLSearchParams(state.route.split('?')[1] || '').get('entity_type') === 'event' ? 'events' : 'athletes');
    }
    if (tab === "users") {
      paint(`<form id="adminUsersForm" class="admin-form-grid">${field("search", "email", "search")}</form><div id="adminUsers" class="admin-revision-list"></div>`);
      let userSearchRevision = 0, userSearchTimer;
      const searchInput = root.querySelector('#adminUsersForm [name=search]');
      const loadUsers = async () => {
        const revision = ++userSearchRevision;
        const users = await api("/admin/users", { params: {search: searchInput.value.trim()} });
        if (!active() || revision !== userSearchRevision) return;
        document.getElementById("adminUsers").innerHTML = users.map((u) => `<article class="account-notification"><div class="account-notification-copy"><p><strong>${esc(u.email)}</strong></p><p class="admin-revision-meta">${esc(u.role.replaceAll('_', ' ').toUpperCase())}</p></div><div class="account-notification-actions admin-user-role-actions">${select(`role_${u.id}`, "role", ["user", "admin", "super_admin"], u.role)}${button("save", `data-role="${u.id}"`)}</div></article>`).join("") || emptyState(); bind();
        root.querySelectorAll("[data-role]").forEach((b) => b.onclick = () => confirm("save", async () => { await api(`/admin/users/${b.dataset.role}/role`, { method: "PUT", body: { role: root.querySelector(`[name="role_${b.dataset.role}"]`).value } }); }));
        for (const user of users) {
          const actions = root.querySelector(`[data-role="${user.id}"]`).parentElement;
          if (user.is_active === false) {
            actions.innerHTML = `<span class="admin-revision-meta">${esc(text('userDeleted'))}</span>`;
            continue;
          }
          if (user.is_last_active_super_admin) {
            actions.innerHTML = `<span class="admin-revision-meta">${esc(text('lastSuperAdmin'))}</span>`;
            continue;
          }
          if (user.id === state.currentUser.id) continue;
          actions.insertAdjacentHTML('beforeend', button('deleteUser', `data-delete-user="${user.id}"`));
          const remove = actions.querySelector('[data-delete-user]');
          remove.classList.add('filter-clear-button');
          remove.onclick = () => confirm('deleteUser', async () => {
            await api(`/admin/users/${user.id}`, {method: 'DELETE'});
            if (!active()) return;
            actions.innerHTML = `<div class="admin-center-feedback is-success admin-audit-success" role="status">${esc(text('userDeleted'))}</div>`;
          }, false, `${user.email} · ${text('deleteUserWarning')}`);
        }
      };
      onSubmit('adminUsersForm', async () => { clearTimeout(userSearchTimer); await loadUsers(); });
      searchInput.addEventListener('input', () => {
        ++userSearchRevision;
        clearTimeout(userSearchTimer);
        userSearchTimer = setTimeout(async () => {
          if (!active()) return;
          const revision = userSearchRevision;
          try { await loadUsers(); }
          catch (error) { if (active() && userSearchRevision === revision + 1) feedback(error.message, true); }
        }, 180);
      });
      await loadUsers();
    }
    if (tab === "audit") {
      paint(`<form id="adminAuditForm" class="admin-form-grid">${select("entity_type", "entity_type", [{ value: "", label: text("all") }, "Athlete", "Event", "Result"]) + field("entity_id", "Leverage ID", "number") + select("review_status", "status", [{ value: "", label: text("all") }, "pending", "approved", "reverted"])}</form><div id="adminAudit" class="admin-revision-list"></div>`);
      const auditForm = root.querySelector('#adminAuditForm');
      let auditRevision = 0, auditTimer;
      const loadAudit = async () => {
        const revision = ++auditRevision;
        const params = Object.fromEntries(new FormData(auditForm));
        const logs = await api("/admin/audit-logs", { params });
        if (!active() || revision !== auditRevision) return;
        document.getElementById("adminAudit").innerHTML = logs.map((log) => `<article class="account-notification admin-audit-record"><div class="account-notification-copy"><p><strong>#${log.id} · ${esc(text(log.entity_type))} #${log.entity_id} · ${esc(text(log.action))}</strong></p><p class="admin-revision-meta admin-audit-meta">${esc(new Date(log.created_at.endsWith('Z') ? log.created_at : `${log.created_at}Z`).toLocaleString(state.language))} · ${esc(text(log.review_status))}</p></div><div class="admin-center-actions admin-audit-commands">${button('compareChanges', `data-audit-compare="${log.id}" aria-expanded="false" aria-controls="auditDetails_${log.id}"`)}<div class="account-notification-actions">${["pending", "approved"].includes(log.review_status) && log.action === "update" && ["Athlete", "Event", "Result", "EventCalendarEntry"].includes(log.entity_type) ? button("revert", `data-audit="${log.id}" data-action="revert"`) : ""}</div></div><div class="admin-audit-details" id="auditDetails_${log.id}" hidden>${report({ before: log.before_json ? JSON.parse(log.before_json) : null, after: log.after_json ? JSON.parse(log.after_json) : null })}${field(`note_${log.id}`, "reason")}</div></article>`).join("") || emptyState();
        for (const [index, log] of logs.entries()) {
          const article = root.querySelectorAll('#adminAudit > article')[index];
          const author = document.createElement('p');
          author.className = 'admin-revision-meta';
          author.dataset.auditAuthor = '';
          const identity = [log.admin_email, log.admin_id != null ? `ID ${log.admin_id}` : null].filter(Boolean).join(' · ');
          const role = log.admin_current_role ? `${text('auditCurrentRole')}: ${String(log.admin_current_role).replaceAll('_', ' ').toUpperCase()}` : '';
          author.textContent = [identity ? `${text('auditAuthor')}: ${identity}` : text('auditUnknownAuthor'), role].filter(Boolean).join(' · ');
          article.querySelector('.admin-audit-meta').after(author);
          if (!['create', 'merge', 'soft_delete'].includes(log.action) || !['Athlete', 'Event'].includes(log.entity_type)) continue;
          const actions = article.querySelector('.account-notification-actions');
          const undoLabel = log.action === 'soft_delete' ? 'undoDelete' : log.action === 'merge' ? 'undoMerge' : 'undoCreate';
          if (['pending', 'approved'].includes(log.review_status)) actions.insertAdjacentHTML('beforeend', button(undoLabel, `data-audit="${log.id}" data-action="revert" data-confirm-label="${undoLabel}"`));
        }
        root.querySelectorAll('[data-action="revert"]').forEach((b) => b.classList.add('filter-clear-button'));
        root.querySelectorAll("[data-audit]").forEach((b) => b.onclick = () => confirm(b.dataset.confirmLabel || b.dataset.action, async () => {
          const note = root.querySelector(`[name="note_${b.dataset.audit}"]`);
          await api(`/admin/audit-logs/${b.dataset.audit}/${b.dataset.action}`, { method: "POST", body: { note: note.value || null } });
          if (!active()) return;
          const article = b.closest('article');
          const log = logs.find((item) => String(item.id) === b.dataset.audit);
          log.review_status = 'reverted';
          article.querySelector('.admin-audit-meta').textContent = `${new Date(log.created_at.endsWith('Z') ? log.created_at : `${log.created_at}Z`).toLocaleString(state.language)} · ${text(log.review_status)}`;
          note.disabled = true;
          article.querySelector('.account-notification-actions').innerHTML = `<div class="admin-center-feedback is-success admin-audit-success" role="status">${esc(text('success'))}</div>`;
        }, false));
        root.querySelectorAll('[data-audit-compare]').forEach((button) => {
          button.onclick = () => {
            const details = root.querySelector(`#auditDetails_${button.dataset.auditCompare}`);
            details.hidden = !details.hidden;
            button.setAttribute('aria-expanded', String(!details.hidden));
          };
        });
      };
      onSubmit('adminAuditForm', async () => { clearTimeout(auditTimer); await loadAudit(); });
      const scheduleAudit = (delay) => {
        const revision = ++auditRevision;
        clearTimeout(auditTimer);
        auditTimer = setTimeout(async () => {
          if (!active() || !auditForm.checkValidity()) return;
          try { await loadAudit(); }
          catch (error) { if (active() && auditRevision === revision + 1) feedback(error.message, true); }
        }, delay);
      };
      auditForm.addEventListener('change', () => scheduleAudit(0));
      auditForm.querySelector('[name=entity_id]').addEventListener('input', () => scheduleAudit(180));
      await loadAudit();
    }
  } catch (error) { feedback(error.message, true); }

  async function imports() {
    let importRevision = 0;
    paint(form("adminImportForm", select("kind", "type", [{ value: "gymternet", label: text("importResults") }, { value: "calendar", label: text("importCalendar") }], session.import?.kind || "gymternet") + select("year_hint", "year", [{ value: "", label: "—" }, ...Array.from({ length: new Date().getFullYear() - 1898 }, (_, index) => String(new Date().getFullYear() + 1 - index))], session.import?.params?.year_hint || session.import?.params?.year || "") + `<div class="admin-form-field"><span>File</span><div class="admin-file-picker"><input id="adminImportFile" name="file" type="file" accept=".xlsx,.csv" required tabindex="-1" aria-label="${esc(text("chooseFile"))}"><button id="adminChooseFile" type="button" class="quiet-button outline-command-button" aria-controls="adminImportFile" aria-describedby="adminImportFilename">${esc(text("chooseFile"))}</button><span id="adminImportFilename" aria-live="polite">${esc(text("noFileSelected"))}</span></div></div>` + select("csv_discipline", "CSV discipline", [{ value: "", label: "—" }, "MAG", "WAG"]) + select("csv_score_kind", "CSV score", [{ value: "", label: "—" }, "final", "dscore"]), "preview") + '<div id="adminImportOutput"></div>');
    onSubmit("adminImportForm", async (v, f) => {
      const revision = ++importRevision;
      const file = f.elements.file.files[0];
      const params = v.kind === "calendar" ? { year: v.year_hint } : { year_hint: v.year_hint, csv_discipline: v.csv_discipline, csv_score_kind: v.csv_score_kind, orphan_review_limit: 5000, athlete_review_limit: 5000, skip_existing_events: false };
      const body = new FormData(); body.append("file", file);
      const output = document.getElementById("adminImportOutput");
      output.innerHTML = '<div id="adminImportInitialProgress"></div>';
      const progress = mountImportProgress({root: output.firstElementChild, text, esc, uploading: true});
      const {onUploadProgress, onUploaded} = progress;
      try {
        const preview = await api(`/imports/${v.kind}/preview`, { method: "POST", body, params, onUploadProgress, onUploaded });
        if (!active() || !output.isConnected || revision !== importRevision) return;
        await progress.complete();
        if (!active() || !output.isConnected || revision !== importRevision) return;
        session.import = { kind: v.kind, file, params, preview, athlete: {}, orphan: {}, event: {} }; showImport();
      } catch (error) {
        if (revision !== importRevision || !output.isConnected) return;
        output.textContent = "";
        throw error;
      } finally {
        progress.dispose();
      }
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
      for (const key of ["csv_discipline", "csv_score_kind", "year_hint"]) {
        importForm.elements[key].closest("label, .admin-form-field").hidden =
          key === "year_hint" ? false : calendar || !csv;
      }
    };
    importForm.addEventListener("change", () => {
      importRevision++;
      session.import = null;
      document.getElementById("adminImportOutput").innerHTML = "";
      syncFields();
    });
    if (session.import?.file) {
      const transfer = new DataTransfer();
      transfer.items.add(session.import.file);
      importForm.elements.file.files = transfer.files;
      for (const name of ['csv_discipline', 'csv_score_kind']) {
        const input = importForm.elements[name];
        input.value = session.import.params[name] ?? '';
        const select = input.closest('[data-admin-select]');
        if (select) {
          const option = [...select.querySelectorAll('[data-admin-select-value]')].find(item => item.dataset.adminSelectValue === input.value);
          if (option) select.querySelector('[data-admin-select-label]').textContent = option.textContent.trim();
        }
      }
    }
    syncFields();
    if (session.import) showImport();
  }
  function showImport() {
    if (!active()) return;
    const draft = session.import, output = document.getElementById("adminImportOutput"), p = draft.preview;
    const selectedParams = {...draft.params, ...draft.pendingParams};
    output.dataset.importKind = draft.kind;
    draft.event ||= {};
    draft.source ||= {};
    let refreshPreview;
    draft.reviewPages ||= {};
    draft.reviewOpen ||= {};
    const pageSize = 6;
    const countryReview = item => ['possible_athlete_country_change', 'possible_athlete_identity_collision'].includes(item.problem_type);
    const athleteCountryReviews = (p.athlete_match_review || []).filter(countryReview);
    const athleteIdentityReviews = (p.athlete_match_review || []).filter(item => !countryReview(item));
    for (const [type, items] of [['athlete', athleteIdentityReviews], ['athleteCountry', athleteCountryReviews], ['event', p.event_match_review], ['orphan', p.orphan_dscore_review]]) {
      draft.reviewPages[type] = Math.min(draft.reviewPages[type] || 0, Math.max(0, Math.ceil((items?.length || 0) / pageSize) - 1));
    }
    const start = type => (draft.reviewPages[type] || 0) * pageSize;
    const isDeferred = type => Boolean(selectedParams[`defer_${type}_reviews`] ?? selectedParams.defer_duplicate_reviews);
    const reviewGroup = (type, title, count, rows) => `<details class="admin-revision-group" data-import-group="${type}" ${draft.reviewOpen[type] ? 'open' : ''}><summary>${esc(text(title))}<span class="admin-revision-count">${count}</span></summary>${rows}${count > pageSize ? `<div class="admin-import-pagination">${button('importPreviousPage', `data-review-page="${type}" data-direction="-1" ${start(type) === 0 ? 'disabled' : ''}`)}<span>${start(type) + 1}–${Math.min(start(type) + pageSize, count)} / ${count}</span>${button('importNextPage', `data-review-page="${type}" data-direction="1" ${start(type) + pageSize >= count ? 'disabled' : ''}`)}</div>` : ''}</details>`;
    const issueErrors = (p.issues || []).filter((issue) => issue.severity === 'error');
    const standaloneIssues = draft.kind === 'gymternet' && !p.committed
      ? issueErrors.filter(issue => !sourceReviewCoversIssue(issue, p.source_review || [])) : issueErrors;
    const issuesByScope = Object.fromEntries(['events', 'athletes', 'results'].map(scope => [scope, standaloneIssues.filter(issue => importIssueScope(issue) === scope)]));
    const scoreConflicts = (p.conflicts || []).filter(conflict => importIssueScope(conflict) === 'results');
    const countryConflicts = (p.conflicts || []).filter(conflict => importIssueScope(conflict) === 'athletes');
    const calendarAlreadyImported = draft.kind === 'calendar' && !p.committed && p.parsed_rows > 0
      && p.would_create_events === 0 && p.would_update_events === 0
      && !p.unmatched_historical_rows && !p.duplicate_source_rows?.length && !p.matched_event_source_conflicts?.length;
    const importStatus = issueErrors.length ? '' : calendarAlreadyImported ? text('importHistoricalOnly') : draft.kind !== 'gymternet' ? '' :
      p.skipped_existing_events?.length && p.importable_results === 0 && !p.conflicts?.length && !p.athlete_match_review?.length && !p.event_match_review?.length ? text('importHistoricalOnly') :
      p.parsed_rows === 0 ? text('importNoRows') :
      p.importable_results === 0 && p.duplicates?.length && !p.conflicts?.length ? text('importOnlyDuplicates') : '';
    const reviewRows = (items, type, pageType = type) => items.slice(start(pageType), start(pageType) + pageSize).map((item, pageIndex) => {
      const index = type === 'athlete' ? p.athlete_match_review.indexOf(item) : start(type) + pageIndex;
      const identity = item.problem_type === "possible_athlete_identity_collision";
      const countryChange = item.problem_type === "possible_athlete_country_change";
      const choices = [{ value: "", label: text("unresolved") }, ...(item.suggestions || []).map((s) => ({ value: `suggestion:${s.suggestion_id}`, label: `${text("accept")} · ${s.label || nameOf(s.target_athlete || s.target_result || {})} · ${s.confidence ?? ""}` })),
        ...(countryChange ? [{value: "update_country", label: text("updateCountry")}, {value: "keep_existing_country", label: text("keepCountry")}] : []),
        ...(type === "orphan" ? [{ value: "discard", label: text("discard") }] : identity ? [{ value: "keep_separate", label: text("separate") }, { value: "merge_as_same_athlete", label: text("same") }] : [{ value: "create_new", label: text("newAthlete") }]), { value: "manual_target", label: text("manual") }];
      const source = item.imported_athlete || item.orphan_dscore || {};
      const countryOnly = type === 'athlete' && countryReview(item);
      const countryOptions = [...new Set([source.country, item.existing_athlete?.country, ...(item.saved_result_countries || []), ...(item.country_variants || []).map(v => v.country), ...(item.suggestions || []).map(v => v.target_athlete?.country)].filter(Boolean))].map(value => ({value, label: value}));
      const previousCountry = draft.athlete[item.review_id] || {};
      const ambiguousCountry = new Set((item.suggestions || []).map(s => s.target_athlete?.athlete_id).filter(Boolean)).size > 1;
      const countryControls = `${ambiguousCountry ? `<p class="admin-stats-note">${esc(text('importCountryAmbiguous'))}</p>` : ''}<div class="admin-form-grid admin-country-review-controls">${!ambiguousCountry ? select('country_history_choice', 'importCountryHistoryAction', [{value: '', label: '—'}, ...countryOptions], previousCountry.action === 'country_history' ? previousCountry.canonical_country : '') + select('country_correction_choice', 'importCountryCorrectionAction', [{value: '', label: '—'}, ...countryOptions], previousCountry.action === 'country_correction' ? previousCountry.canonical_country : '') : ''}<div class="admin-center-actions">${button('importCountryDeferAction', `data-country-defer aria-pressed="${previousCountry.action === 'defer'}"`)}</div></div>`;
      const best = item.suggestions?.[0];
      const target = item.existing_athlete || best?.target_athlete || best?.target_result || {};
      const identityDecision = draft.athlete[item.review_id] || {};
      const identityTargets = [...new Map((item.suggestions || []).filter(s => s.target_athlete?.athlete_id).map(s => [s.target_athlete.athlete_id, s])).values()];
      const identityControls = `<div class="admin-center-actions">${[['accept_suggestion', 'importIdentityMerge'], ['create_new', 'importIdentityCreate'], ['defer', 'importIdentityDefer']].map(([action, label]) => button(label, `data-identity-action="${action}" aria-pressed="${(identityDecision.selection || identityDecision.action) === action}" ${action === 'accept_suggestion' && !identityTargets.length ? 'disabled' : ''}`)).join('')}</div>${identityTargets.length > 1 ? `<div data-identity-target ${(identityDecision.selection || identityDecision.action) === 'accept_suggestion' ? '' : 'hidden'}>${select('identity_target', 'target', [{value: '', label: '—'}, ...identityTargets.map(s => ({value: s.suggestion_id, label: `${nameOf(s.target_athlete)} · ${s.target_athlete.country || '—'} · ID ${s.target_athlete.athlete_id}`}))], identityDecision.suggestion_id || '')}</div>` : ''}`;
      return `<article class="admin-identity-pair admin-import-review" data-review-type="${type}" data-review-index="${index}"><div class="admin-identity-pair-grid"><div class="admin-identity-entity"><strong>${esc(nameOf(source))}</strong><p class="admin-revision-meta">${esc([text('importFile'), source.discipline, source.country, source.year].filter(Boolean).join(' · '))}</p></div><div class="admin-identity-entity"><strong>${esc(nameOf(target))}</strong><p class="admin-revision-meta">${esc([target.athlete_id ? `ID ${target.athlete_id}` : '', target.discipline, target.country].filter(Boolean).join(' · '))}</p></div></div><div class="admin-center-actions">${best?.confidence != null ? `<span class="admin-review-compatibility">${esc(text('compatibility'))}: ${Math.round(best.confidence * 100)}%</span>` : ''}${button('importCompare', 'data-import-review-toggle aria-expanded="false"')}</div><div data-pair-details hidden>${type === 'athlete' ? renderAthleteImportComparison({item, name: nameOf(source), text, esc}) : report(source) + report(item.suggestions || [])}${type === 'athlete' ? '<div class="admin-athlete-review-actions">' : ''}${countryOnly ? countryControls : type === 'athlete' ? identityControls : `<div class="admin-form-grid">${select("action", "decision", choices, draft[type][item.review_id]?.selection || "")}${type === "athlete" ? field("athlete_id", "target", "number") + (countryChange ? '' : select("country_action", "countryStrategy", [{ value: "", label: "—" }, { value: "update_country", label: text("updateCountry") }, { value: "keep_existing_country", label: text("keepCountry") }])) + field("canonical_country", "country") + select("country_strategy", "countryStrategy", [{ value: "preserve_represented_country", label: text("history") }, { value: "correct_all_to_canonical", label: text("correction") }]) : field("target_id", "Target result")}</div>`}${type === 'athlete' ? '</div>' : ''}</div></article>`;
    }).join("");
    const eventComparison = (item, target) => `<div class="admin-import-athlete-comparison"><dl class="admin-activity-row-details"><div><dt>${esc(text('importFile'))}</dt><dd>${esc(item.event_name)}<p class="admin-revision-meta">${esc([item.year, ...(item.disciplines || [])].filter(Boolean).join(' · '))}</p></dd></div><div><dt>${esc(text('importDatabase'))}</dt><dd>${esc(target?.name || '—')}<p class="admin-revision-meta">${esc([target?.year, target?.discipline].filter(Boolean).join(' · '))}</p></dd></div></dl></div>`;
    const eventReviewRows = (p.event_match_review || []).slice(start('event'), start('event') + pageSize).map((item, i) => {
      const candidates = item.suggestions || [];
      const decision = draft.event[item.review_id] || {};
      const selected = decision.selection || decision.action || '';
      const target = candidates.find(candidate => candidate.event_id === decision.event_id) || candidates[0];
      return `<article class="admin-identity-pair admin-import-review" data-event-review="${start('event') + i}">
        <div class="admin-identity-pair-grid">
          <div class="admin-identity-entity"><strong>${esc(item.event_name)}</strong><p class="admin-revision-meta">${esc([text('importFile'), item.year, ...(item.disciplines || [])].filter(Boolean).join(' · '))}</p></div>
          <div class="admin-identity-entity"><strong data-event-target-name>${esc(target?.name || '—')}</strong><p class="admin-revision-meta" data-event-target-meta>${esc([target?.event_id ? `ID ${target.event_id}` : '', target?.year, target?.discipline].filter(Boolean).join(' · '))}</p></div>
        </div>
        <div class="admin-center-actions"><span class="admin-review-compatibility" data-event-compatibility ${target?.compatibility == null ? 'hidden' : ''}>${esc(text('compatibility'))}: ${target?.compatibility ?? ''}%</span>${button('importCompare', 'data-import-review-toggle aria-expanded="false"')}</div>
        <div data-pair-details hidden><div data-event-comparison>${eventComparison(item, target)}</div>
          <div class="admin-athlete-review-actions"><div class="admin-center-actions">${[['match_existing', 'importEventIdentityMatch'], ['keep_separate', 'importEventIdentityCreate'], ['defer', 'importIdentityDefer']].map(([action, label]) => button(label, `data-event-identity-action="${action}" aria-pressed="${selected === action}" ${action === 'match_existing' && !candidates.length ? 'disabled' : ''}`)).join('')}</div>
          ${candidates.length > 1 ? `<div data-identity-target ${selected === 'match_existing' ? '' : 'hidden'}>${select('event_target', 'importEventIdentityTarget', [{value: '', label: '—'}, ...candidates.map(candidate => ({value: String(candidate.event_id), label: `${candidate.name} · ${candidate.year} · ${candidate.discipline} · ID ${candidate.event_id}`}))], decision.event_id ? String(decision.event_id) : '')}</div>` : ''}</div>
        </div></article>`;
    }).join('');
    const importForm = document.getElementById('adminImportForm');
    importForm.hidden = !draft.fileFormOpen;
    const calendarConflicts = (p.duplicate_source_rows?.length || 0) + (p.matched_event_source_conflicts?.length || 0);
    const metrics = items => renderImportMetrics({items, text, esc, language: state.language});
    const completedMetrics = draft.kind === 'gymternet'
      ? [['importCreatedResults', p.created_results], ['importCreatedAthletes', p.created_athletes], ['importCreatedEvents', p.created_events], ['importUpdatedEvents', p.updated_events], ['importSkippedDuplicates', p.skipped_duplicates], ['importSkippedConflicts', p.skipped_conflicts]]
      : [['importUpdatedEvents', p.updated_events], ['importCreatedEvents', p.created_events], ['importCalendarUnmatched', p.skipped_unmatched_historical_rows]];
    const calendarMetrics = [['importCalendarRows', p.parsed_rows], ['importCalendarMatched', p.matched_events], ['importCalendarUpdate', p.would_update_events], ['importNewEvents', p.would_create_events], ['importCalendarUnmatched', p.unmatched_historical_rows], ['importCalendarConflicts', calendarConflicts]];
    if (draft.kind === 'calendar' && p.skip_existing_events) {
      (p.committed ? completedMetrics : calendarMetrics).push(['importCalendarExcluded', p.skipped_existing_events_count]);
    }
    output.innerHTML = `
      <div class="admin-import-heading ${p.committed ? 'is-complete' : ''}">
        <div><h3>${esc(text(p.committed ? 'importCompleted' : 'preview'))}</h3><p class="admin-revision-meta">${esc(p.filename)}</p></div>
        <div class="admin-import-header-actions">
          ${importStatus === text('importHistoricalOnly') ? `<p class="admin-center-feedback" data-import-status role="status">${esc(importStatus)}</p>` : ''}
          ${!p.committed ? `<div class="admin-import-scope-choice">${select('existing_event_scope', draft.kind === 'calendar' ? 'importCalendarExistingScope' : 'importExistingScope', [{value: 'include', label: text('importScopeInclude')}, {value: 'skip', label: text('importScopeSkip')}], selectedParams.skip_existing_events ? 'skip' : 'include')}</div>` : ''}
          ${button(draft.fileFormOpen ? 'importHideFile' : 'importChangeFile', `id="adminImportChangeFile" aria-controls="adminImportForm" aria-expanded="${Boolean(draft.fileFormOpen)}"`)}
        </div>
      </div>
      <div id="adminImportScopeStatus" hidden></div>
      ${p.committed && p.deferred_duplicate_pairs ? `<p class="admin-stats-note">${esc(text('importDeferredCount').replace('{n}', p.deferred_duplicate_pairs))} <a href="#/admin/review">${esc(text('importDuplicateLater'))}</a></p>` : ''}
      ${p.committed ? metrics(completedMetrics) : draft.kind === 'gymternet' ? '<div id="adminImportOverview"></div>' : metrics(calendarMetrics)}
      ${draft.kind === 'gymternet' && !p.committed ? '<div id="adminImportResolution"></div>' : ''}
      ${!p.committed && (athleteIdentityReviews.length || isDeferred('athlete')) ? reviewGroup('athlete', 'importAthleteReview', athleteIdentityReviews.length, isDeferred('athlete') ? '' : reviewRows(athleteIdentityReviews, "athlete")) : ''}
      ${!p.committed && athleteCountryReviews.length ? reviewGroup('athleteCountry', 'importAthleteCountryReview', athleteCountryReviews.length, reviewRows(athleteCountryReviews, 'athlete', 'athleteCountry')) : ''}
      ${!p.committed && (p.event_match_review?.length || isDeferred('event')) ? reviewGroup('event', 'importEventReview', p.event_match_review?.length || 0, isDeferred('event') ? '' : eventReviewRows) : ''}
      ${issueErrors.length && (draft.kind !== 'gymternet' || p.committed) ? `<div data-import-issues>${renderImportIssues({issues: issueErrors, text, esc, language: state.language, sourceRows: p.committed ? [] : p.source_review, page: draft.issuePage || 0})}</div>` : ''}
      ${draft.kind === 'calendar' ? '<div id="adminCalendarRows"></div><div id="adminCalendarConflicts"></div>' : ''}
      <p class="admin-stats-note" id="adminImportDecisionsNotice" ${draft.needsPreview ? '' : 'hidden'}>${esc(text('importNeedsPreview'))}</p>
      ${!p.committed ? `<div class="admin-center-actions admin-import-actions">${button('importRecalculate', 'id="adminReviewPreview"')}${button('commit', 'id="adminCommitImport"')}</div>` : ''}
      ${importStatus && importStatus !== text('importHistoricalOnly') ? `<p class="admin-center-feedback ${p.parsed_rows === 0 ? 'is-error' : ''}" data-import-status role="status">${esc(importStatus)}</p>` : ''}
      ${!p.committed ? `<footer class="admin-import-notes admin-stats-note">${draft.kind === 'gymternet' ? `<p>${esc(text('importReviewScope'))} ${esc(text('importCandidatesNote'))}</p>` : p.skip_existing_events ? `<p>${esc(text('importCalendarSkipNote'))}</p>` : ''}</footer>` : ''}
    `;
    if (draft.kind === 'gymternet' && !p.committed) {
      const reviewParts = [
        ['events', 'importReviewEvents', (p.event_match_decision_stats?.unresolved ?? (p.event_match_review?.length || 0)) + issuesByScope.events.filter(issue => issue.severity === 'error').length],
        ['athletes', 'importReviewAthletes', (p.athlete_match_decision_stats?.unresolved ?? (p.athlete_match_review?.length || 0)) + countryConflicts.length + issuesByScope.athletes.filter(issue => issue.severity === 'error').length],
        ['results', 'importReviewResults', scoreConflicts.length + issuesByScope.results.filter(issue => issue.severity === 'error').length],
      ];
      const nav = document.createElement('div');
      nav.className = 'admin-center-actions admin-import-review-tabs';
      nav.setAttribute('role', 'tablist');
      nav.innerHTML = reviewParts.map(([key, label, pending]) => `<button type="button" class="filter-button" role="tab" id="importTab_${key}" aria-controls="importPart_${key}" data-import-part="${key}">${esc(text(label))}${pending ? ` <span class="admin-revision-count">(${pending})</span>` : ''}</button>`).join('');
      output.querySelector('#adminImportOverview').before(nav);
      const sections = {};
      for (const [key] of reviewParts) {
        const section = document.createElement('section');
        section.id = `importPart_${key}`;
        section.className = 'admin-import-review-part';
        section.setAttribute('role', 'tabpanel');
        section.setAttribute('aria-labelledby', `importTab_${key}`);
        sections[key] = section;
        nav.after(section);
      }
      sections.events.append(output.querySelector('#adminImportOverview'));
      const athleteOverview = document.createElement('div');
      athleteOverview.id = 'adminImportAthletes';
      sections.athletes.append(athleteOverview);
      for (const [key, kind] of [['events', 'event'], ['athletes', 'athlete']]) {
        const group = output.querySelector(`[data-import-group=${kind}]`);
        if (group) {
          sections[key].append(group);
          group.querySelector('summary').insertAdjacentHTML('afterend', `<div class="admin-center-actions">${button(isDeferred(kind) ? 'importResumeDuplicates' : 'importDeferDuplicates', `data-defer-duplicates="${kind}"`)}</div>`);
          if (kind === 'athlete') group.querySelector('.admin-center-actions').insertAdjacentHTML('afterend', `<p class="admin-stats-note" data-identity-review-note>${esc(text('importDuplicateNote'))}</p>`);
          if (isDeferred(kind)) group.querySelector('.admin-import-pagination')?.remove();
        }
      }
      let countryReviewGroup = output.querySelector('[data-import-group=athleteCountry]');
      if (!countryReviewGroup && countryConflicts.length) {
        sections.athletes.insertAdjacentHTML('beforeend', reviewGroup('athleteCountry', 'importAthleteCountryReview', 0, ''));
        countryReviewGroup = sections.athletes.querySelector('[data-import-group=athleteCountry]');
      }
      if (countryReviewGroup) {
        sections.athletes.append(countryReviewGroup);
        countryReviewGroup.querySelector('.admin-revision-count').textContent = athleteCountryReviews.length + countryConflicts.length;
        countryReviewGroup.querySelector('summary').insertAdjacentHTML('afterend', `<p class="admin-stats-note" data-country-review-note>${esc(text('importCountryIdentityNote'))}</p>`);
        countryReviewGroup.querySelector('summary').insertAdjacentHTML('afterend', `<div class="admin-center-actions">${button('importDeferAllCountries', 'data-defer-all-countries')}</div>`);
      }
      const existingResults = (p.duplicates || []).filter(row => row.reason === 'duplicate_existing').length;
      sections.results.innerHTML = metrics([['importExisting', existingResults], ['importNew', p.importable_results], ['importConflicts', scoreConflicts.length]]);
      if (countryConflicts.length) {
        const countryPage = draft.countryConflictPage = Math.min(draft.countryConflictPage || 0, Math.max(0, Math.ceil(countryConflicts.length / 6) - 1));
        countryReviewGroup.insertAdjacentHTML('beforeend', `<div data-country-conflicts>${countryConflicts.slice(countryPage * 6, (countryPage + 1) * 6).map((c, index) => `<article class="admin-identity-pair"><div><strong>${esc(nameOf(c))}</strong><p class="admin-revision-meta">${esc(c.event_name)} · ${esc(c.year)}</p></div><div class="admin-center-actions">${button('importCompare', 'data-import-review-toggle aria-expanded="false"')}${button('importUseStoredCountry', `data-country-fix="${countryPage * 6 + index}" ${!c.existing_country ? 'disabled' : ''}`)}${button('importExcludeCountryRow', `data-country-exclude="${countryPage * 6 + index}"`)}</div><p class="admin-stats-note">${esc(text('importCountryCorrectionNote'))}</p><div data-pair-details hidden>${renderImportIdentityComparison({leftName: nameOf(c), rightName: nameOf(c), rightLabel: text(c.existing_result_id ? 'importDatabase' : 'previous'), fields: [['country', c.country, c.existing_country]], text, esc})}</div></article>`).join('')}${countryConflicts.length > 6 ? `<div class="admin-import-pagination">${button('importPreviousPage', `data-country-page="-1" ${countryPage === 0 ? 'disabled' : ''}`)}<span>${countryPage * 6 + 1}–${Math.min((countryPage + 1) * 6, countryConflicts.length)} / ${countryConflicts.length}</span>${button('importNextPage', `data-country-page="1" ${(countryPage + 1) * 6 >= countryConflicts.length ? 'disabled' : ''}`)}</div>` : ''}</div>`);
        const group = sections.athletes.querySelector('[data-country-conflicts]');
        group.querySelectorAll('[data-country-page]').forEach(control => control.onclick = () => { draft.countryConflictPage += Number(control.dataset.countryPage); showImport(); });
      }
      for (const selector of ['#adminImportResolution', '[data-import-group=orphan]', '[data-import-issues]']) {
        const node = output.querySelector(selector);
        if (node) sections.results.append(node);
      }
      draft.scopedIssuePages ||= {};
      sections.results.insertAdjacentHTML('beforeend', renderAutomaticImportIssues({issues: p.issues || [], text, esc, language: state.language}));
      for (const [scope, issues] of Object.entries(issuesByScope)) {
        if (!issues.length) continue;
        sections[scope].insertAdjacentHTML('beforeend', `<div data-import-issues data-issue-scope="${scope}">${renderImportIssues({issues, text, esc, language: state.language, sourceRows: scope === 'results' ? p.source_review : [], page: draft.scopedIssuePages[scope] || 0})}</div>`);
      }
      const notes = output.querySelector('.admin-import-notes');
      for (const [key, label] of [['events', 'importNoEventReviews'], ['athletes', 'importNoAthleteReviews']]) {
        if (!sections[key].querySelector('[data-import-group], [data-import-issues], [data-country-conflicts]')) {
          sections[key].insertAdjacentHTML('beforeend', `<div class="admin-center-feedback" data-import-empty="${key}" role="status">${esc(text(label))}</div>`);
        }
      }
      if (isDeferred('event') || isDeferred('athlete')) notes.insertAdjacentHTML('beforeend', `<p>${esc(text('importDeferredNote'))}</p>`);
      output.querySelectorAll('[data-import-group] > .admin-stats-note:not([data-country-review-note]):not([data-identity-review-note]), .admin-import-duplicate-link > .admin-stats-note').forEach(note => note.remove());
      const choosePart = key => {
        draft.reviewPart = key;
        for (const [name, section] of Object.entries(sections)) section.hidden = name !== key;
        nav.querySelectorAll('[data-import-part]').forEach(control => {
          const selected = control.dataset.importPart === key;
          control.setAttribute('aria-selected', String(selected));
          control.setAttribute('aria-pressed', String(selected));
          control.tabIndex = selected ? 0 : -1;
        });
      };
      nav.querySelectorAll('[data-import-part]').forEach((control, index) => {
        control.onclick = () => choosePart(control.dataset.importPart);
        control.onkeydown = event => {
          if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
          event.preventDefault();
          const next = event.key === 'Home' ? 0 : event.key === 'End' ? 2 : (index + (event.key === 'ArrowRight' ? 1 : 2)) % 3;
          const key = reviewParts[next][0];
          choosePart(key);
          nav.querySelector(`[data-import-part=${key}]`).focus();
        };
      });
      choosePart(draft.reviewPart || 'events');
      mountImportAthletes({root: athleteOverview, preview: p, text, esc, report, language: state.language, route: state.route, viewState: draft.athleteView ||= {}});
    }
    output.querySelector('#adminImportChangeFile').onclick = event => {
      draft.fileFormOpen = !draft.fileFormOpen;
      importForm.hidden = !draft.fileFormOpen;
      event.currentTarget.setAttribute('aria-expanded', String(draft.fileFormOpen));
      event.currentTarget.textContent = text(draft.fileFormOpen ? 'importHideFile' : 'importChangeFile');
    };
    output.querySelectorAll('[data-issue-page]').forEach(control => control.onclick = () => {
      const scope = control.closest('[data-issue-scope]')?.dataset.issueScope;
      if (scope) draft.scopedIssuePages[scope] = Number(control.dataset.issuePage);
      else draft.issuePage = Number(control.dataset.issuePage);
      showImport();
    });
    if (!p.committed) {
      const bodyWithDecisions = (preview, includeIdentities = true, includeEvents = true) => {
        const body = new FormData(); body.append("file", draft.file);
        body.append("source_row_decisions", JSON.stringify(Object.values(draft.source)));
        for (const [type, key, items] of [
          ['athlete', 'athlete_match_decisions', preview.athlete_match_review],
          ['orphan', 'orphan_dscore_decisions', preview.orphan_dscore_review],
          ['event', 'event_match_decisions', preview.event_match_review],
        ]) {
          const ids = new Set((items || []).map(item => item.review_id));
          body.append(key, JSON.stringify(Object.values(draft[type]).filter(d => d.action && ids.has(d.review_id) && (type === 'event' ? includeEvents : includeIdentities))));
        }
        return body;
      };
      refreshPreview = async (scope = draft.pendingParams?.skip_existing_events ?? draft.params.skip_existing_events, dialog = null) => {
        if (draft.scopeBusy) return;
        const changingScope = scope !== draft.params.skip_existing_events;
        const changingSource = Boolean(draft.sourceDirty);
        const pending = {...draft.params, ...draft.pendingParams};
        const params = {...draft.params, skip_existing_events: Boolean(scope), ...(draft.kind === 'gymternet' ? {
          defer_duplicate_reviews: false,
          defer_event_reviews: Boolean(pending.defer_event_reviews ?? pending.defer_duplicate_reviews),
          defer_athlete_reviews: Boolean(pending.defer_athlete_reviews ?? pending.defer_duplicate_reviews),
        } : {})};
        const revision = draft.decisionRevision || 0;
        draft.scopeBusy = true;
        output.inert = true;
        output.setAttribute('aria-busy', 'true');
        output.querySelector('#adminCommitImport')?.setAttribute('disabled', '');
        const progress = mountImportProgressDialog({dialog, text, esc});
        try {
          let result = await api(`/imports/${draft.kind}/preview`, { method: "POST", body: bodyWithDecisions(draft.preview, !changingScope && !changingSource, !changingSource), params });
          if (session.import !== draft || revision !== (draft.decisionRevision || 0)) return;
          if (changingSource && (result.event_match_review || []).some(item => draft.event[item.review_id]?.action)) {
            result = await api(`/imports/${draft.kind}/preview`, { method: "POST", body: bodyWithDecisions(result, false), params });
          }
          // Reapply only decisions that belong to the newly selected scope.
          if ((changingScope || changingSource) && [['athlete', result.athlete_match_review], ['orphan', result.orphan_dscore_review]]
              .some(([type, items]) => (items || []).some(item => draft[type][item.review_id]?.action))) {
            result = await api(`/imports/${draft.kind}/preview`, { method: "POST", body: bodyWithDecisions(result), params });
          }
          if (session.import !== draft || revision !== (draft.decisionRevision || 0)) return;
          if (!active() || !output.isConnected) return;
          await progress.complete();
          if (!active() || !output.isConnected || session.import !== draft || revision !== (draft.decisionRevision || 0)) return;
          draft.params = params;
          draft.pendingParams = {};
          draft.preview = result;
          draft.needsPreview = false;
          draft.sourceDirty = false;
        } finally {
          progress.dispose();
          draft.scopeBusy = false;
          if (output.isConnected) {
            output.inert = false;
            output.removeAttribute('aria-busy');
          }
          if (active() && session.import === draft) showImport();
          else draft.onRefreshSettled?.();
        }
      };
      document.getElementById("adminReviewPreview").onclick = guard(() => refreshPreview());
      output.querySelectorAll('[data-defer-duplicates]').forEach(control => control.addEventListener('click', guard(async () => {
        const kind = control.dataset.deferDuplicates;
        const stage = () => {
          draft.pendingParams = {...draft.pendingParams, [`defer_${kind}_reviews`]: !isDeferred(kind)};
          markChanged(); showImport();
        };
        if (isDeferred(kind)) stage();
        else confirm('importDeferDuplicates', stage, false, text(kind === 'event' ? 'importDeferEventsConfirm' : 'importDeferAthletesConfirm'));
      })));
      output.querySelector('[name=existing_event_scope]')?.addEventListener('change', guard(async event => {
        draft.pendingParams = {...draft.pendingParams, skip_existing_events: event.target.value === 'skip'};
        markChanged();
        await refreshPreview();
      }));
    }
    output.inert = Boolean(draft.scopeBusy);
    output.setAttribute('aria-busy', String(Boolean(draft.scopeBusy)));
    if (draft.scopeBusy) {
      mountImportProgress({root: output.querySelector('#adminImportScopeStatus'), text, esc});
      draft.onRefreshSettled = () => {
        if (active() && session.import === draft) showImport();
      };
    } else {
      delete draft.onRefreshSettled;
    }
    bind();
    if (draft.kind === 'calendar') {
      const issuesGroup = output.querySelector('[data-import-issues]');
      mountCalendarImportRows({root: output.querySelector('#adminCalendarRows'), preview: p,
        text, esc, language: state.language, route: state.route, viewState: draft.calendarView ||= {}});
      mountCalendarConflicts({root: output.querySelector('#adminCalendarConflicts'), preview: p,
        text, esc, language: state.language, route: state.route, viewState: draft.calendarConflictView ||= {}});
      if (issuesGroup) output.querySelector('#adminCalendarConflicts').after(issuesGroup);
    }

    const updateCommit = () => {
      const control = output.querySelector('#adminCommitImport');
      if (control) control.disabled = Boolean(draft.scopeBusy || issueErrors.length || p.parsed_rows === 0 || (p.skipped_existing_events?.length && !p.importable_results) || draft.needsPreview ||
        (draft.kind === 'calendar' && p.skip_existing_events && !p.rows?.length) ||
        p.athlete_match_decision_stats?.unresolved || p.event_match_decision_stats?.unresolved ||
        (draft.kind === 'gymternet' && p.athlete_match_decision_stats?.invalid_decisions) || p.conflicts?.length || calendarConflicts);
    };
    const markChanged = () => {
      draft.decisionRevision = (draft.decisionRevision || 0) + 1;
      draft.needsPreview = true;
      output.querySelector('#adminImportDecisionsNotice').hidden = false;
      updateCommit();
      updateReviewCompletion();
    };
    const updateReviewCompletion = () => {
      if (draft.kind !== 'gymternet' || p.committed) return;
      const pending = pendingImportReviews(p, draft);
      for (const [scope, label] of [['events', 'importNoEventReviews'], ['athletes', 'importNoAthleteReviews']]) {
        const section = output.querySelector(`#importPart_${scope}`);
        const message = section?.querySelector(`[data-import-empty=${scope}]`);
        if (pending[scope]) message?.remove();
        else if (section && !message) section.insertAdjacentHTML('beforeend', `<div class="admin-center-feedback" data-import-empty="${scope}" role="status">${esc(text(label))}</div>`);
      }
      clearTimeout(draft.autoPreviewTimer);
      const revision = draft.decisionRevision || 0;
      if (draft.needsPreview && !draft.scopeBusy && !Object.values(pending).some(Boolean)
          && draft.autoPreviewRevision !== revision) {
        draft.autoPreviewTimer = setTimeout(guard(async () => {
          if (!active() || !output.isConnected || session.import !== draft || draft.scopeBusy || !draft.needsPreview
              || revision !== (draft.decisionRevision || 0)) return;
          draft.autoPreviewRevision = revision;
          await refreshPreview();
        }), 500);
      }
    };
    output.querySelector('[data-defer-all-countries]')?.addEventListener('click', () => confirm('importDeferAllCountries', () => {
      const exclusions = new Map();
      for (const conflict of countryConflicts) {
        const source = (p.source_review || []).find(row => row.sheet === conflict.source_sheet && row.row === conflict.source_row);
        if (!source) throw new Error(text('importCountrySourceMissing'));
        for (const ref of [source, ...(source.related_rows || [])]) {
          const row = (p.source_review || []).find(item => item.sheet === ref.sheet && item.row === ref.row);
          if (!row) throw new Error(text('importCountrySourceMissing'));
          exclusions.set(`${row.sheet}:${row.row}`, {sheet: row.sheet, row: row.row, fingerprint: row.fingerprint, action: 'exclude'});
        }
      }
      for (const item of athleteCountryReviews) draft.athlete[item.review_id] = {review_id: item.review_id, action: 'defer'};
      for (const [key, decision] of exclusions) draft.source[key] = decision;
      if (exclusions.size) draft.sourceDirty = true;
      draft.reviewOpen.athleteCountry = true;
      markChanged();
      showImport();
    }, false, text('importDeferAllCountriesConfirm')));
    output.querySelectorAll('[data-country-fix], [data-country-exclude]').forEach(control => {
      control.onclick = guard(() => {
        const exclude = control.hasAttribute('data-country-exclude');
        const conflict = countryConflicts[Number(exclude ? control.dataset.countryExclude : control.dataset.countryFix)];
        const source = (p.source_review || []).find(row => row.sheet === conflict.source_sheet && row.row === conflict.source_row);
        if (!source) return;
        const rows = [source, ...(source.related_rows || []).map(ref => (p.source_review || []).find(row => row.sheet === ref.sheet && row.row === ref.row)).filter(Boolean)];
        for (const row of rows) {
          const key = `${row.sheet}:${row.row}`;
          if (!exclude && !row.country_field) continue;
          draft.source[key] = {sheet: row.sheet, row: row.row, fingerprint: row.fingerprint, action: exclude ? 'exclude' : 'edit',
            ...(!exclude ? {values: {...draft.source[key]?.values, [row.country_field]: conflict.existing_country}} : {})};
        }
        draft.sourceDirty = true;
        markChanged();
        control.disabled = true;
      });
    });
    if (draft.kind === 'gymternet' && !p.committed) {
      const resolution = !p.committed ? mountImportResolution({
        root: output.querySelector('#adminImportResolution'), preview: {...p, conflicts: scoreConflicts}, draft, text, esc, button, field, report,
        markChanged: () => { draft.sourceDirty = true; markChanged(); }, confirm, guard, language: state.language,
      }) : null;
      mountImportReport({root: output.querySelector('#adminImportOverview'), preview: p, text, esc, report,
        language: state.language, route: state.route, viewState: draft.reportView ||= {}, onCorrect: resolution ? (sheet, row) => resolution.focus(sheet, row) : null});
      output.querySelectorAll('[data-correct-issue-sheet]').forEach(control => control.onclick = () => resolution?.focus(control.dataset.correctIssueSheet, Number(control.dataset.correctIssueRow)));
    }
    output.querySelectorAll('[data-import-group]').forEach(group => group.ontoggle = () => {
      if (group.isConnected) draft.reviewOpen[group.dataset.importGroup] = group.open;
    });
    output.querySelectorAll('[data-review-page]').forEach(control => control.onclick = () => {
      const type = control.dataset.reviewPage;
      draft.reviewPages[type] = Math.max(0, (draft.reviewPages[type] || 0) + Number(control.dataset.direction));
      showImport();
    });
    updateCommit();

    output.querySelectorAll('[data-import-review-toggle]').forEach(control => control.onclick = () => {
      const details = control.closest('article').querySelector('[data-pair-details]');
      details.hidden = !details.hidden;
      control.setAttribute('aria-expanded', String(!details.hidden));
    });
    output.querySelectorAll('[data-event-review]').forEach(row => {
      const item = p.event_match_review[Number(row.dataset.eventReview)];
      const candidates = item.suggestions || [];
      const stageEvent = (action, targetId) => {
        const target = candidates.find(candidate => candidate.event_id === Number(targetId));
        draft.event[item.review_id] = {review_id: item.review_id, selection: action,
          action: action === 'match_existing' && !target ? '' : action,
          ...(action === 'match_existing' && target ? {event_id: target.event_id} : {})};
        draft.reviewOpen.event = true;
        row.querySelectorAll('[data-event-identity-action]').forEach(control => control.setAttribute('aria-pressed', String(control.dataset.eventIdentityAction === action)));
        const picker = row.querySelector('[data-identity-target]');
        if (picker) picker.hidden = action !== 'match_existing';
        if (target) {
          row.querySelector('[data-event-comparison]').innerHTML = eventComparison(item, target);
          row.querySelector('[data-event-target-name]').textContent = target.name;
          row.querySelector('[data-event-target-meta]').textContent = [`ID ${target.event_id}`, target.year, target.discipline].filter(Boolean).join(' · ');
          const compatibility = row.querySelector('[data-event-compatibility]');
          compatibility.hidden = target.compatibility == null;
          compatibility.textContent = `${text('compatibility')}: ${target.compatibility ?? ''}%`;
        }
        markChanged();
      };
      row.querySelectorAll('[data-event-identity-action]').forEach(control => control.onclick = () => {
        const action = control.dataset.eventIdentityAction;
        const targetId = candidates.length === 1 ? candidates[0].event_id : row.querySelector('[name=event_target]')?.value;
        stageEvent(action, action === 'match_existing' ? targetId : null);
      });
      row.addEventListener('change', event => {
        if (event.target.name === 'event_target') stageEvent('match_existing', event.target.value);
      });
    });
    output.querySelectorAll("[data-review-type]").forEach((row) => {
      const type = row.dataset.reviewType, items = type === "athlete" ? p.athlete_match_review : p.orphan_dscore_review, item = items[Number(row.dataset.reviewIndex)];
      if (type === 'athlete' && countryReview(item)) {
        const stageCountry = (action, country) => {
          draft.athlete[item.review_id] = {review_id: item.review_id, action, ...(country ? {canonical_country: country} : {})};
          draft.reviewOpen.athleteCountry = true;
          markChanged();
          for (const input of row.querySelectorAll('[name=country_history_choice], [name=country_correction_choice]')) {
            const active = input.name === (action === 'country_history' ? 'country_history_choice' : 'country_correction_choice') && country;
            input.value = active ? country : '';
            input.closest('[data-admin-select]').querySelector('[data-admin-select-label]').textContent = active ? country : '—';
            input.closest('[data-admin-select]').querySelectorAll('[role=option]').forEach(option => option.setAttribute('aria-selected', String(option.dataset.adminSelectValue === input.value)));
          }
          row.querySelector('[data-country-defer]').setAttribute('aria-pressed', String(action === 'defer'));
        };
        row.querySelector('[data-country-defer]').onclick = () => stageCountry('defer');
        row.addEventListener('change', event => {
          if (!['country_history_choice', 'country_correction_choice'].includes(event.target.name)) return;
          stageCountry(event.target.value ? (event.target.name === 'country_history_choice' ? 'country_history' : 'country_correction') : '', event.target.value);
        });
        return;
      }
      if (type === 'athlete') {
        const candidates = [...new Map((item.suggestions || []).filter(s => s.target_athlete?.athlete_id).map(s => [s.target_athlete.athlete_id, s])).values()];
        const stageIdentity = (action, suggestionId) => {
          draft.athlete[item.review_id] = {review_id: item.review_id, selection: action, action: action === 'accept_suggestion' && !suggestionId ? '' : action, ...(suggestionId ? {suggestion_id: suggestionId} : {})};
          draft.reviewOpen.athlete = true;
          row.querySelectorAll('[data-identity-action]').forEach(control => control.setAttribute('aria-pressed', String(control.dataset.identityAction === action)));
          const targetPicker = row.querySelector('[data-identity-target]');
          if (targetPicker) targetPicker.hidden = action !== 'accept_suggestion';
          markChanged();
        };
        row.querySelectorAll('[data-identity-action]').forEach(control => control.onclick = () => {
          const action = control.dataset.identityAction;
          const suggestionId = candidates.length === 1 ? candidates[0].suggestion_id : row.querySelector('[name=identity_target]')?.value;
          stageIdentity(action, action === 'accept_suggestion' ? suggestionId : null);
        });
        row.addEventListener('change', event => {
          if (event.target.name === 'identity_target') stageIdentity('accept_suggestion', event.target.value);
        });
        return;
      }
      const lookup = document.createElement("div");
      lookup.className = "admin-lookup";
      lookup.innerHTML = field("target_search", "search") + '<div class="admin-target-options"></div>';
      row.querySelector('[data-pair-details]').append(lookup);
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
              body.append('source_row_decisions', JSON.stringify(Object.values(draft.source)));
              body.append('event_match_decisions', JSON.stringify(Object.values(draft.event).filter(d => d.action && p.event_match_review?.some(item => item.review_id === d.review_id))));
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
        markChanged();
      });
    });

    updateReviewCompletion();
    document.getElementById("adminCommitImport")?.addEventListener("click", () => confirm("commit", async () => {
      const body = new FormData(); body.append("file", draft.file);
      body.append("source_row_decisions", JSON.stringify(Object.values(draft.source)));
      for (const [type, key, items] of [["athlete", "athlete_match_decisions", p.athlete_match_review], ["orphan", "orphan_dscore_decisions", p.orphan_dscore_review], ["event", "event_match_decisions", p.event_match_review]]) {
        const ids = new Set((items || []).map(item => item.review_id));
        body.append(key, JSON.stringify(Object.values(draft[type]).filter(d => d.action && ids.has(d.review_id))));
      }
      try {
        const result = await api(`/imports/${draft.kind}/commit`, { method: "POST", body, params: { ...draft.params, ...(draft.kind === "gymternet" ? { allow_partial: false, require_resolved_reviews: true } : {}) } });
        draft.preview = result; showImport();
      } catch (error) {
        if (error.detail && typeof error.detail === "object" && Array.isArray(error.detail.issues)) { draft.preview = error.detail; draft.needsPreview = false; showImport(); }
        throw error;
      }
    }));
  }
}
