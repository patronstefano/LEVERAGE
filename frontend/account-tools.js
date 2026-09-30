import { bindAuthValidation } from "./auth-validation.js?v=password-min-copy-20260930";

const labels = {
  registerLink: ["Sign up", "Registrati", "Regístrate", "S’inscrire"],
  recoverLink: ["Recover password", "Recupera password", "Recuperar contraseña", "Récupérer le mot de passe"],
  forgotHelp: ["Enter the email associated with your account to receive a password reset link.", "Inserisci l’email associata al tuo account per ricevere un link con cui reimpostare la password.", "Introduce el correo asociado a tu cuenta para recibir un enlace para restablecer la contraseña.", "Saisissez l’adresse email associée à votre compte pour recevoir un lien de réinitialisation du mot de passe."],
  notifications: ["Notifications", "Notifiche", "Notificaciones", "Notifications"],
  settings: ["Settings", "Impostazioni", "Ajustes", "Paramètres"],
  goToAthlete: ["Go to Athlete", "Vai all’Atleta", "Ir al Atleta", "Voir l’Athlète"],
  goToEvent: ["Go to Event", "Vai all’Evento", "Ir al Evento", "Voir l’Événement"],
  demoGenerator: ["Generate USER notifications (DEMO)", "Generatore notifiche USER (DEMO)", "Generar notificaciones USER (DEMO)", "Générer des notifications USER (DEMO)"],
  demoAdminGenerator: ["Admin Center notifications (DEMO)", "Notifiche Centro Admin (DEMO)", "Notificaciones Centro Admin (DEMO)", "Notifications Centre Admin (DEMO)"],
  demoAdminPersonalGenerator: ["Personal Area notifications (DEMO)", "Notifiche Area Personale (DEMO)", "Notificaciones Área Personal (DEMO)", "Notifications Espace Personnel (DEMO)"],
  demoSuperAdminGenerator: ["Generate SUPER ADMIN notifications (DEMO)", "Generatore notifiche SUPER ADMIN (DEMO)", "Generar notificaciones SUPER ADMIN (DEMO)", "Générer des notifications SUPER ADMIN (DEMO)"],
  demoImport: ["Import completed: 3 new athletes, 2 new events, 24 results; 2 duplicates skipped. Check the new entities’ details.", "Importazione completata: 3 nuovi atleti, 2 nuovi eventi, 24 risultati; 2 duplicati ignorati. Verifica i dati delle nuove entità.", "Importación completada: 3 nuevos atletas, 2 nuevos eventos, 24 resultados; 2 duplicados omitidos. Revisa los datos de las nuevas entidades.", "Import terminé : 3 nouveaux athlètes, 2 nouveaux événements, 24 résultats ; 2 doublons ignorés. Vérifiez les données des nouvelles entités."],
  demoDataEntry: ["Manual entry completed: 12 results and 2 new athletes. Complete the new athletes’ profiles.", "Inserimento manuale completato: 12 risultati e 2 nuovi atleti. Completa le schede dei nuovi atleti.", "Entrada manual completada: 12 resultados y 2 nuevos atletas. Completa los perfiles de los nuevos atletas.", "Saisie manuelle terminée : 12 résultats et 2 nouveaux athlètes. Complétez les profils des nouveaux athlètes."],
  demoReminder: ["2 completed events without results: Example Event A, Example Event B.", "2 Eventi conclusi e senza risultati: Gara di esempio A, Gara di esempio B.", "2 eventos finalizados sin resultados: Evento de ejemplo A, Evento de ejemplo B.", "2 événements terminés sans résultats : Événement exemple A, Événement exemple B."],
  demoSecurity: ["Security alert: another administrator deleted a result. Review the operation in the audit log.", "Avviso di sicurezza: un altro amministratore ha eliminato un risultato. Verifica l’operazione nel registro di audit.", "Alerta de seguridad: otro administrador ha eliminado un resultado. Revisa la operación en el registro de auditoría.", "Alerte de sécurité : un autre administrateur a supprimé un résultat. Vérifiez l’opération dans le journal d’audit."],
  demoResult: ["New results in {count} competitions: {events}.", "Nuovi risultati in {count} gare: {events}.", "Nuevos resultados en {count} competiciones: {events}.", "Nouveaux résultats dans {count} compétitions : {events}."],
  demoResultSingle: ["New results in 1 competition: {events}.", "Nuovi risultati in 1 gara: {events}.", "Nuevos resultados en 1 competición: {events}.", "Nouveaux résultats dans 1 compétition : {events}."],
  demoCompetition: ["Example competition", "Gara di esempio", "Competición de ejemplo", "Compétition fictive"],
  demoEvent: ["New event at {level} level.", "Nuovo evento di livello {level}.", "Nuevo evento de nivel {level}.", "Nouvel événement de niveau {level}."],
  demoRecommendedEvent: ["New event recommended based on your favorites.", "Nuovo evento consigliato in base ai preferiti.", "Nuevo evento recomendado según tus favoritos.", "Nouvel événement recommandé selon vos favoris."],
  demoPromotion: ["You have been promoted to ADMIN. Administration tools are now available.", "Hai ottenuto la promozione ad ADMIN. Gli strumenti di amministrazione sono ora disponibili.", "Has obtenido la promoción a ADMIN. Las herramientas de administración ya están disponibles.", "Vous avez été promu ADMIN. Les outils d’administration sont maintenant disponibles."],
  demoDemotion: ["Your role has changed to USER. Administration tools are no longer available.", "Il tuo ruolo è stato modificato in USER. Gli strumenti di amministrazione non sono più disponibili.", "Tu rol ha cambiado a USER. Las herramientas de administración ya no están disponibles.", "Votre rôle est devenu USER. Les outils d’administration ne sont plus disponibles."],
  role: ["Role", "Ruolo", "Rol", "Rôle"],
  accountData: ["Account details", "Dati account", "Datos de la cuenta", "Informations du compte"],
  unread: ["Unread only", "Solo non lette", "Solo sin leer", "Non lues uniquement"],
  read: ["Mark as read", "Segna come letta", "Marcar como leída", "Marquer comme lue"],
  readAll: ["Mark all as read", "Segna tutte come lette", "Marcar todas como leídas", "Tout marquer comme lu"],
  more: ["Load more notifications", "Carica altre notifiche", "Cargar más notificaciones", "Charger plus de notifications"],
  empty: ["No notifications.", "Nessuna notifica.", "No hay notificaciones.", "Aucune notification."],
  emptyUnread: ["No unread notifications.", "Nessuna notifica da leggere.", "No hay notificaciones sin leer.", "Aucune notification non lue."],
  retry: ["Try again", "Riprova", "Reintentar", "Réessayer"],
  language: ["Preferred language", "Lingua preferita", "Idioma preferido", "Langue préférée"],
  change: ["Change password", "Cambia password", "Cambiar contraseña", "Changer le mot de passe"],
  current: ["Current password", "Password attuale", "Contraseña actual", "Mot de passe actuel"],
  new: ["New password", "Nuova password", "Nueva contraseña", "Nouveau mot de passe"],
  repeat: ["Confirm new password", "Conferma nuova password", "Confirmar contraseña", "Confirmer le nouveau mot de passe"],
  save: ["Save", "Salva", "Guardar", "Enregistrer"],
  forgot: ["Forgot password?", "Recupera password", "¿Olvidaste tu contraseña?", "Mot de passe oublié ?"],
  reset: ["Reset password", "Reimposta password", "Restablecer contraseña", "Réinitialiser le mot de passe"],
  resend: ["Resend verification email", "Reinvia email di verifica", "Reenviar correo de verificación", "Renvoyer l’email de vérification"],
  request: ["Send link", "Invia link", "Enviar enlace", "Envoyer le lien"],
  sent: ["If the address is eligible, you will receive an email with the next steps.", "Se l’indirizzo soddisfa i requisiti, riceverai un’email con le istruzioni.", "Si la dirección cumple los requisitos, recibirás un correo con las instrucciones.", "Si l’adresse est éligible, vous recevrez un email avec les instructions."],
  mismatch: ["The passwords do not match.", "Le password non coincidono.", "Las contraseñas no coinciden.", "Les mots de passe ne correspondent pas."],
  success: ["Password updated. Sign in again.", "Password aggiornata. Accedi nuovamente.", "Contraseña actualizada. Vuelve a iniciar sesión.", "Mot de passe modifié. Reconnectez-vous."],
  invalid: ["This link is invalid or expired. Request a new one.", "Questo link non è valido o è scaduto. Richiedine uno nuovo.", "Este enlace no es válido o ha caducado. Solicita otro.", "Ce lien est invalide ou expiré. Demandez-en un nouveau."],
  failed: ["Unable to complete the operation. Try again.", "Impossibile completare l’operazione. Riprova.", "No se pudo completar la operación. Inténtalo de nuevo.", "Impossible de terminer l’opération. Réessayez."],
  cooldown: ["Too many requests. Please wait before trying again.", "Troppe richieste. Attendi prima di riprovare.", "Demasiadas solicitudes. Espera antes de reintentar.", "Trop de demandes. Patientez avant de réessayer."],
  delivery: ["Email delivery is currently unavailable. Please try again later.", "L’invio email non è al momento disponibile. Riprova più tardi.", "El envío de correo no está disponible. Inténtalo más tarde.", "L’envoi d’email est indisponible. Réessayez plus tard."],
  wrongPassword: ["The current password is incorrect.", "La password attuale non è corretta.", "La contraseña actual es incorrecta.", "Le mot de passe actuel est incorrect."],
  expired: ["Your session expired. Sign in again.", "La sessione è scaduta. Accedi nuovamente.", "La sesión ha caducado. Inicia sesión de nuevo.", "La session a expiré. Reconnectez-vous."],
  languageFailed: ["Your preferred language could not be saved. Please try again.", "Non è stato possibile salvare la lingua preferita. Riprova.", "No se pudo guardar el idioma preferido. Inténtalo de nuevo.", "Impossible d’enregistrer la langue préférée. Réessayez."],
};
export const accountText = (language, key) => labels[key]?.[["en", "it", "es", "fr"].indexOf(language)] || labels[key]?.[0] || key;

// Development-only, in-memory inbox: never writes simulated data to the API.
const demoInboxes = new Map();
const adminNotificationTypes = new Set(['import_summary', 'data_entry_summary', 'event_results_reminder', 'security_alert']);
const demoEmails = { user: 'demo.user@leverage-demo.com', admin: 'demo.admin@leverage-demo.com', super_admin: 'demo.superadmin@leverage-demo.com' };
export const canGenerateDemoNotifications = (user) => ['localhost', '127.0.0.1', '[::1]'].includes(location.hostname)
  && Boolean(user && demoEmails[user.role] && user.email === demoEmails[user.role]);
export function generateDemoNotifications(user, athletes = [], events = [], resultEvents = [], scope = 'all') {
  if (!canGenerateDemoNotifications(user)) return;
  const athlete = athletes.find((detail) => detail.athlete?.id)?.athlete;
  const event = events.find((detail) => detail.event?.id)?.event;
  const examples = [
    { type: 'new_result', key: resultEvents.length > 1 ? 'demoResult' : 'demoResultSingle', events: resultEvents, name: [athlete?.last_name, athlete?.first_name].filter(Boolean).join(' '), related_athlete_id: athlete?.id },
    { type: 'new_event', key: ['National Event', 'International Event'].includes(event?.level) ? 'demoRecommendedEvent' : 'demoEvent', name: event ? (event.name.includes(String(event.year)) ? event.name : `${event.name} ${event.year}`) : 'World Cup Paris 2026', level: event?.level || 'World Cup', related_event_id: event?.id },
    { type: 'admin_promotion', key: 'demoPromotion' },
    { type: 'admin_demotion', key: 'demoDemotion' },
  ];
  if (['admin', 'super_admin'].includes(user.role)) {
    examples.push(
      { type: 'import_summary', key: 'demoImport' },
      { type: 'data_entry_summary', key: 'demoDataEntry' },
      { type: 'event_results_reminder', key: 'demoReminder' },
    );
  }
  if (user.role === 'super_admin') examples.push({ type: 'security_alert', key: 'demoSecurity' });
  const generated = examples.map((example, index) => ({
    ...example, id: index + 1, is_read: false,
    created_at: new Date(Date.now() - index * 3600000).toISOString(),
  }));
  for (const target of ['personal', 'admin']) {
    if (scope !== 'all' && scope !== target) continue;
    demoInboxes.set(`${user.id}:${target}`, generated.filter((item) => adminNotificationTypes.has(item.type) === (target === 'admin')));
  }
}

function context(host) {
  const { state, escapeHtml: esc } = host;
  const t = (key) => accountText(state.language, key);
  const button = (key, attrs = "") => '<button class="quiet-button outline-command-button" type="button" ' + attrs + '>' + esc(t(key)) + '</button>';
  const input = (name, key, type = "password") => '<label><span>' + esc(t(key)) + '</span><input name="' + name + '" type="' + type +
    '" required ' + (type === "password" ? 'maxlength="128" minlength="' + (name === "current_password" ? 1 : 6) + '" autocomplete="' + (name === "current_password" ? "current-password" : "new-password") + '"' : 'autocomplete="email" inputmode="email" autocapitalize="none" spellcheck="false" placeholder="name@example.com" pattern="[^\\s@]+@[^\\s@]+\\.[^\\s@]+"') + '></label>';
  const feedback = (node, key, error = false) => {
    node.className = "account-feedback " + (error ? "is-error" : "is-success");
    node.textContent = t(key);
  };
  const request = async (path, method = "GET", body, auth = true, params = {}) => {
    const scope = host.notificationScope || 'personal';
    if (path.startsWith('/notifications/')) params = { ...params, scope };
    const generated = canGenerateDemoNotifications(state.currentUser) && demoInboxes.get(`${state.currentUser.id}:${scope}`);
    const inbox = generated && generated.filter((item) => adminNotificationTypes.has(item.type) === (scope === 'admin'));
    if (inbox && path.startsWith('/notifications/')) {
      if (path === '/notifications/unread-count') return { count: inbox.filter((item) => !item.is_read).length };
      if (path === '/notifications/read-all' && method === 'PUT') inbox.forEach((item) => { item.is_read = true; });
      else if (method === 'PUT') {
        const item = inbox.find((entry) => entry.id === Number(path.split('/')[2]));
        if (item) item.is_read = true;
      } else return inbox.filter((item) => !params.unread_only || !item.is_read)
        .sort((a, b) => Number(a.is_read) - Number(b.is_read) || new Date(b.created_at) - new Date(a.created_at) || b.id - a.id)
        .slice(params.offset || 0, (params.offset || 0) + (params.limit || 30))
        .map((item) => ({ ...item, message: [item.name,
          t(item.key).replace('{level}', item.level || '').replace('{count}', item.events?.length || 1).replace('{events}', item.events?.length
            ? item.events.map((event) => event.name.includes(String(event.year)) ? event.name : `${event.name} (${event.year})`).join('; ')
            : t('demoCompetition'))].filter(Boolean).join(' · ') }));
      return { message: 'OK' };
    }
    const response = await host.fetchApi(path, params, {
      method, headers: auth ? host.authHeaders(Boolean(body)) : { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = response.status === 204 ? null : await response.json().catch(() => null);
    if (!response.ok) {
      const error = new Error("Request failed");
      error.status = response.status;
      error.detail = data?.detail;
      if (auth && response.status === 401) host.clearAuth();
      throw error;
    }
    return data;
  };
  const errorKey = (e) => e.status === 429 ? "cooldown" : e.status === 401 ? "expired" : "failed";
  return { t, esc, button, input, feedback, request, errorKey };
}

export function mountAccountTools(host) {
  const { state } = host;
  const { t, esc, button, input, feedback, request, errorKey } = context(host);
  const notifications = document.getElementById("accountNotifications");
  const settings = document.getElementById("accountSettings");
  const userId = state.currentUser.id;
  const live = () => notifications.isConnected && state.currentUser?.id === userId;
  const adminBadge = document.getElementById('accountAdminUnreadCount');
  if (adminBadge && ['admin', 'super_admin'].includes(state.currentUser.role)) {
    const adminRequest = context({ ...host, notificationScope: 'admin' }).request;
    const refreshAdminBadge = () => adminRequest('/notifications/unread-count').then((data) => {
      if (!live() || !adminBadge.isConnected) return;
      const count = Math.max(0, Number(data.count) || 0);
      adminBadge.textContent = count > 99 ? '99+' : String(count);
      adminBadge.hidden = count === 0;
      adminBadge.setAttribute('aria-label', `${t('unread')}: ${count}`);
    }).catch(() => { /* Do not display an unverified count when loading fails. */ });
    refreshAdminBadge();
    const pollAdminBadge = async () => {
      if (!live()) return;
      if (!document.hidden) await refreshAdminBadge();
      if (live()) setTimeout(pollAdminBadge, 30000);
    };
    setTimeout(pollAdminBadge, 30000);
  }
  settings.className = 'panel athlete-admin-panel account-settings-panel';
  settings.innerHTML = '<div class="section-header compact-section-header"><h2>' + t("settings") + '</h2></div>' +
    '<section class="admin-tool-block"><div class="section-header compact-section-header"><h2>' + t("accountData") + '</h2></div><div class="admin-form-grid account-settings-details">' +
    '<dl class="account-settings-identity"><div><dt>Email</dt><dd>' + esc(state.currentUser.email) + '</dd></div>' +
    '<div><dt>' + esc(t("role")) + '</dt><dd>' + esc(String(state.currentUser.role || '').replaceAll('_', ' ').toUpperCase()) + '</dd></div></dl>' +
    host.renderAdminSelectControl("account_language", t("language"), state.language, [
      { value: "en", label: "English" }, { value: "it", label: "Italiano" },
      { value: "es", label: "Español" }, { value: "fr", label: "Français" },
    ]) + '</div></section><form id="accountPasswordForm" class="auth-form admin-edit-form">' +
    '<div class="section-header compact-section-header"><h2>' + t("change") + '</h2><button class="quiet-button outline-command-button" type="submit">' + t("save") + '</button></div><div class="admin-form-grid">' +
    input("current_password", "current") + input("new_password", "new") + input("repeat_password", "repeat") +
    '</div><div role="status" aria-live="polite" id="accountPasswordFeedback"></div></form>';
  host.bindAdminSelectControls(settings);
  settings.querySelector('[name="account_language"]').addEventListener("change", (e) => host.setLanguage(e.target.value));
  const passwordValidation = bindAuthValidation(settings.querySelector("form"), settings.querySelector("#accountPasswordFeedback"), () => state.language);
  settings.querySelector("form").onsubmit = async (e) => {
    e.preventDefault();
    const form = e.currentTarget, submit = form.querySelector("button[type=submit]");
    if (submit.disabled || !passwordValidation.validate()) return;
    const values = Object.fromEntries(new FormData(form)), message = document.getElementById("accountPasswordFeedback");
    submit.disabled = true; message.textContent = "";
    try {
      await request("/auth/password/change", "POST", { current_password: values.current_password, new_password: values.new_password });
      if (!live()) return;
      host.clearAuth(); form.reset(); form.hidden = true;
      feedback(message, "success"); form.parentElement.append(message);
      form.parentElement.insertAdjacentHTML("beforeend", '<a class="quiet-button outline-command-button" href="#/login">' + host.t("signIn") + '</a>');
    } catch (error) { if (form.isConnected) passwordValidation.serverError(error, "change"); }
    finally { submit.disabled = false; }
  };
  mountNotificationInbox(host);
}

export function mountNotificationInbox(host) {
  const { state } = host;
  const { t, esc, button, feedback, request, errorKey } = context(host);
  const notifications = document.getElementById('accountNotifications');
  const userId = state.currentUser.id;
  const live = () => notifications.isConnected && state.currentUser?.id === userId;
  notifications.className = 'panel athlete-admin-panel account-notifications-panel';
  notifications.innerHTML = '<div class="section-header compact-section-header"><h2>' + t("notifications") + '</h2><div class="account-notification-toolbar">' +
    '<button class="quiet-button account-unread-filter" type="button" id="accountUnreadOnly" aria-pressed="false">' + esc(t("unread")) + '</button>' +
    '<button class="quiet-button filter-clear-button" type="button" id="accountReadAll">' + esc(t("readAll")) + '</button>' +
    '</div></div><section class="admin-tool-block"><div id="accountNotificationFeedback" role="status" aria-live="polite"></div>' + button("retry", 'id="accountNotificationRetry" hidden') + '<div id="accountNotificationList" aria-live="polite" aria-busy="false"></div>' +
    button("more", 'id="accountMoreNotifications" hidden') + '</section>';
  let offset = 0, revision = 0, loaded = false, busy = false;
  const list = notifications.querySelector("#accountNotificationList"), more = notifications.querySelector("#accountMoreNotifications");
  const unreadOnly = notifications.querySelector("#accountUnreadOnly");
  const isUnreadOnly = () => unreadOnly.getAttribute('aria-pressed') === 'true';
  const retry = notifications.querySelector("#accountNotificationRetry");
  const readAll = notifications.querySelector("#accountReadAll");
  let unreadCount = 0, failedReset = true;
  const updateCount = async () => {
    try {
      const data = await request("/notifications/unread-count");
      if (!live()) return;
      const badge = document.getElementById("accountUnreadCount");
      unreadCount = data.count || 0;
      readAll.disabled = !unreadCount;
      badge.textContent = data.count > 99 ? "99+" : String(data.count || "");
      badge.hidden = !data.count;
      badge.setAttribute("aria-label", String(data.count));
    } catch (_) { /* The notification list reports request failures. */ }
  };
  const load = async (reset = false, requestedLimit = 30) => {
    if (busy && !reset) return;
    const current = ++revision;
    if (reset) offset = 0;
    busy = true; more.disabled = true;
    list.setAttribute('aria-busy', 'true');
    retry.hidden = true;
    notifications.querySelector("#accountNotificationFeedback").textContent = "";
    try {
      const items = [];
      while (items.length < requestedLimit) {
        const limit = Math.min(500, requestedLimit - items.length);
        const chunk = await request("/notifications/", "GET", null, true, { limit, offset: offset + items.length, unread_only: isUnreadOnly() });
        items.push(...chunk);
        if (chunk.length < limit) break;
      }
      if (!live() || current !== revision) return;
      if (reset) list.innerHTML = "";
      const existingIds = new Set([...list.querySelectorAll('[data-notification-id]')].map((item) => item.dataset.notificationId));
      for (const item of items) {
        if (existingIds.has(String(item.id))) continue;
        existingIds.add(String(item.id));
        const article = document.createElement("article");
        article.dataset.notificationId = String(item.id);
        article.dataset.notificationType = item.type || '';
        article.className = "account-notification" + (item.is_read ? "" : " is-unread");
        const links = [["athlete", "athletes"], ["event", "events"]].filter(([key]) => item["related_" + key + "_id"]).map(([key, path]) =>
          '<a class="quiet-button outline-command-button" href="#/' + path + '/' + Number(item["related_" + key + "_id"]) + '">' + esc(t(key === "athlete" ? "goToAthlete" : "goToEvent")) + '</a>').join("");
        article.innerHTML = '<div class="account-notification-copy"><p>' + esc(item.message) + '</p><time datetime="' + esc(item.created_at) + '">' + esc(new Date(item.created_at).toLocaleString(state.language)) +
          '</time></div><div class="account-notification-actions">' + links + (!item.is_read ? '<button class="quiet-button filter-clear-button" type="button" data-read>' + esc(t("read")) + '</button>' : "") + '</div>';
        const read = article.querySelector("[data-read]");
        if (read) read.onclick = async () => {
          read.disabled = true;
          try {
            await request("/notifications/" + item.id + "/read", "PUT");
            if (!live()) return;
            article.classList.remove("is-unread"); read.remove();
            await load(true);
            await updateCount();
          } catch (error) { if (live()) feedback(notifications.querySelector("#accountNotificationFeedback"), errorKey(error), true); read.disabled = false; }
        };
        list.append(article);
      }
      offset += items.length; more.hidden = items.length < requestedLimit; loaded = true;
      if (!list.children.length) list.innerHTML = '<div class="empty-state">' + esc(t(isUnreadOnly() ? "emptyUnread" : "empty")) + '</div>';
    } catch (error) {
      if (live() && current === revision) {
        feedback(notifications.querySelector("#accountNotificationFeedback"), errorKey(error), true);
        failedReset = reset; retry.hidden = false;
      }
    } finally { if (current === revision) { busy = false; more.disabled = false; list.setAttribute('aria-busy', 'false'); } }
  };
  retry.onclick = () => load(failedReset);
  more.onclick = () => load();
  unreadOnly.onclick = () => {
    unreadOnly.setAttribute('aria-pressed', String(!isUnreadOnly()));
    load(true);
  };
  notifications.querySelector("#accountReadAll").onclick = async (e) => {
    const b = e.currentTarget; b.disabled = true;
    try { await request("/notifications/read-all", "PUT"); if (!live()) return; await load(true); await updateCount(); }
    catch (error) { if (live()) feedback(notifications.querySelector("#accountNotificationFeedback"), errorKey(error), true); }
    finally { b.disabled = !unreadCount; }
  };
  const activate = () => { if (!notifications.closest("[data-account-view-panel]").hidden && !loaded) load(true); };
  document.querySelectorAll("[data-account-view]").forEach((b) => b.addEventListener("click", activate));
  updateCount(); activate();
  const poll = async () => {
    if (!live()) return;
    if (!document.hidden) {
      await updateCount();
      if (loaded && !busy && !notifications.closest('[data-account-view-panel]').hidden) {
        await load(true, Math.max(30, offset));
      }
    }
    if (live()) setTimeout(poll, 30000);
  };
  setTimeout(poll, 30000);
}

export function renderAccountRecovery(host, mode) {
  const { t, esc, input, feedback, request, errorKey } = context(host);
  const reset = mode === "reset", resend = mode === "resend";
  const title = reset ? "reset" : resend ? "resend" : "forgot";
  const token = new URLSearchParams(host.state.route.split("?")[1] || "").get("token") || "";
  host.setApp('<div class="auth-brand auth-brand-form"><img class="auth-brand-logo" src="./assets/leverage-logo.png" alt="LEVERAGE" width="28" height="28"><h1>' + t(title) + '</h1>' +
    (!reset && !resend ? '<p class="home-body account-recovery-intro">' + esc(t("forgotHelp")) + '</p>' : '') + '</div><section class="panel auth-panel account-recovery"><form class="auth-form" id="accountRecoveryForm">' +
    (reset ? input("new_password", "new") + input("repeat_password", "repeat") : input("email", "Email", "email")) +
    '<button type="submit" class="quiet-button outline-command-button">' + t(reset ? "save" : "request") +
    '</button></form><div id="accountRecoveryFeedback" role="status" aria-live="polite"></div></section><div class="auth-login-links"><div class="auth-switch-row"><a href="#/login">' +
    esc(host.t("backToLogin")) + '</a>' + (reset || resend ? '<a href="#/forgot-password">' + t("forgot") + '</a>' : '') + '</div></div>');
  const form = document.getElementById("accountRecoveryForm"), message = document.getElementById("accountRecoveryFeedback");
  const validation = bindAuthValidation(form, message, () => host.state.language);
  if (reset && token.length < 20) { form.hidden = true; feedback(message, "invalid", true); return; }
  form.onsubmit = async (e) => {
    e.preventDefault(); const submit = form.querySelector("button[type=submit]");
    if (submit.disabled || !validation.validate()) return;
    const values = Object.fromEntries(new FormData(form));
    submit.disabled = true; message.textContent = "";
    try {
      await request(reset ? "/auth/password/reset" : resend ? "/auth/resend-verification" : "/auth/password/forgot", "POST",
        reset ? { token, new_password: values.new_password } : { email: values.email.trim() }, false);
      if (!form.isConnected) return;
      form.reset();
      if (reset) {
        host.clearAuth(); form.hidden = true;
        window.history.replaceState(null, "", "#/reset-password");
        host.state.route = "/reset-password";
      }
      feedback(message, reset ? "success" : "sent");
    } catch (error) { if (form.isConnected) validation.serverError(error, mode); }
    finally { submit.disabled = false; }
  };
}
