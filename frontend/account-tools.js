const labels = {
  registerLink: ["Sign up", "Registrati", "Regístrate", "S’inscrire"],
  recoverLink: ["Recover password", "Recupera password", "Recuperar contraseña", "Récupérer le mot de passe"],
  forgotHelp: ["Enter the email associated with your account to receive a password reset link.", "Inserisci l’email associata al tuo account per ricevere un link con cui reimpostare la password.", "Introduce el correo asociado a tu cuenta para recibir un enlace para restablecer la contraseña.", "Saisissez l’adresse email associée à votre compte pour recevoir un lien de réinitialisation du mot de passe."],
  notifications: ["Notifications", "Notifiche", "Notificaciones", "Notifications"],
  settings: ["Settings", "Impostazioni", "Ajustes", "Paramètres"],
  unread: ["Unread only", "Solo non lette", "Solo sin leer", "Non lues uniquement"],
  read: ["Mark as read", "Segna come letta", "Marcar como leída", "Marquer comme lue"],
  readAll: ["Mark all as read", "Segna tutte come lette", "Marcar todas como leídas", "Tout marquer comme lu"],
  more: ["Load more notifications", "Carica altre notifiche", "Cargar más notificaciones", "Charger plus de notifications"],
  empty: ["No notifications.", "Nessuna notifica.", "No hay notificaciones.", "Aucune notification."],
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

function context(host) {
  const { state, escapeHtml: esc } = host;
  const t = (key) => accountText(state.language, key);
  const button = (key, attrs = "") => '<button class="quiet-button outline-command-button" type="button" ' + attrs + '>' + esc(t(key)) + '</button>';
  const input = (name, key, type = "password") => '<label><span>' + esc(t(key)) + '</span><input name="' + name + '" type="' + type +
    '" required ' + (type === "password" ? 'maxlength="128" minlength="' + (name === "current_password" ? 1 : 12) + '" autocomplete="' + (name === "current_password" ? "current-password" : "new-password") + '"' : 'autocomplete="email"') + '></label>';
  const feedback = (node, key, error = false) => {
    node.className = "account-feedback " + (error ? "is-error" : "is-success");
    node.textContent = t(key);
  };
  const request = async (path, method = "GET", body, auth = true, params = {}) => {
    const response = await host.fetchApi(path, params, {
      method, headers: auth ? host.authHeaders(Boolean(body)) : { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = response.status === 204 ? null : await response.json();
    if (!response.ok) {
      const error = new Error("Request failed");
      error.status = response.status;
      if (auth && response.status === 401) host.clearAuth();
      throw error;
    }
    return data;
  };
  const errorKey = (e) => e.status === 429 ? "cooldown" : e.status === 503 ? "delivery" : e.status === 401 ? "expired" : "failed";
  return { t, esc, button, input, feedback, request, errorKey };
}

export function mountAccountTools(host) {
  const { state } = host;
  const { t, esc, button, input, feedback, request, errorKey } = context(host);
  const notifications = document.getElementById("accountNotifications");
  const settings = document.getElementById("accountSettings");
  const userId = state.currentUser.id;
  const live = () => notifications.isConnected && state.currentUser?.id === userId;
  settings.innerHTML = '<h2>' + t("settings") + '</h2><div class="account-settings-language">' +
    host.renderAdminSelectControl("account_language", t("language"), state.language, [
      { value: "en", label: "English" }, { value: "it", label: "Italiano" },
      { value: "es", label: "Español" }, { value: "fr", label: "Français" },
    ]) + '</div><h3>' + t("change") + '</h3><form id="accountPasswordForm" class="auth-form">' +
    input("current_password", "current") + input("new_password", "new") + input("repeat_password", "repeat") +
    '<button class="quiet-button outline-command-button" type="submit">' + t("save") + '</button><div role="status" aria-live="polite" id="accountPasswordFeedback"></div></form>';
  host.bindAdminSelectControls(settings);
  settings.querySelector('[name="account_language"]').addEventListener("change", (e) => host.setLanguage(e.target.value));
  settings.querySelector("form").onsubmit = async (e) => {
    e.preventDefault();
    const form = e.currentTarget, submit = form.querySelector("button[type=submit]");
    if (submit.disabled) return;
    const values = Object.fromEntries(new FormData(form)), message = document.getElementById("accountPasswordFeedback");
    if (values.new_password !== values.repeat_password) { feedback(message, "mismatch", true); return; }
    submit.disabled = true; message.textContent = "";
    try {
      await request("/auth/password/change", "POST", { current_password: values.current_password, new_password: values.new_password });
      if (!live()) return;
      host.clearAuth(); form.reset(); form.hidden = true;
      feedback(message, "success"); settings.append(message);
      settings.insertAdjacentHTML("beforeend", '<a class="quiet-button outline-command-button" href="#/login">' + host.t("signIn") + '</a>');
    } catch (error) { feedback(message, error.status === 400 ? "wrongPassword" : errorKey(error), true); }
    finally { submit.disabled = false; }
  };
  notifications.innerHTML = '<h2>' + t("notifications") + '</h2><div class="account-notification-actions"><label><input id="accountUnreadOnly" type="checkbox"> ' + t("unread") +
    '</label>' + button("readAll", 'id="accountReadAll"') + '</div><div id="accountNotificationFeedback" role="status" aria-live="polite"></div><div id="accountNotificationList"></div>' +
    button("more", 'id="accountMoreNotifications" hidden');
  let offset = 0, revision = 0, loaded = false, busy = false;
  const list = notifications.querySelector("#accountNotificationList"), more = notifications.querySelector("#accountMoreNotifications");
  const unreadOnly = notifications.querySelector("#accountUnreadOnly");
  const updateCount = async () => {
    try {
      const data = await request("/notifications/unread-count");
      if (!live()) return;
      const badge = document.getElementById("accountUnreadCount");
      badge.textContent = data.count > 99 ? "99+" : String(data.count || "");
      badge.hidden = !data.count;
      badge.setAttribute("aria-label", String(data.count));
    } catch (_) { /* The notification list reports request failures. */ }
  };
  const load = async (reset = false) => {
    if (busy && !reset) return;
    const current = ++revision;
    if (reset) offset = 0;
    busy = true; more.disabled = true;
    notifications.querySelector("#accountNotificationFeedback").textContent = "";
    try {
      const items = await request("/notifications/", "GET", null, true, { limit: 30, offset, unread_only: unreadOnly.checked });
      if (!live() || current !== revision) return;
      if (reset) list.innerHTML = "";
      for (const item of items) {
        const article = document.createElement("article");
        article.className = "account-notification" + (item.is_read ? "" : " is-unread");
        const links = [["athlete", "athletes"], ["event", "events"]].filter(([key]) => item["related_" + key + "_id"]).map(([key, path]) =>
          '<a class="quiet-button outline-command-button" href="#/' + path + '/' + Number(item["related_" + key + "_id"]) + '">' + esc(host.t(key === "athlete" ? "navAthletes" : "navEvents")) + '</a>').join("");
        article.innerHTML = '<div><p>' + esc(item.message) + '</p><time>' + esc(new Date(item.created_at).toLocaleString(state.language)) +
          '</time></div><div class="account-notification-actions">' + links + (!item.is_read ? button("read", 'data-read') : "") + '</div>';
        const read = article.querySelector("[data-read]");
        if (read) read.onclick = async () => {
          read.disabled = true;
          try {
            await request("/notifications/" + item.id + "/read", "PUT");
            article.classList.remove("is-unread"); read.remove();
            if (unreadOnly.checked) await load(true);
            await updateCount();
          } catch (error) { feedback(notifications.querySelector("#accountNotificationFeedback"), errorKey(error), true); read.disabled = false; }
        };
        list.append(article);
      }
      offset += items.length; more.hidden = items.length < 30; loaded = true;
      if (!list.children.length) list.textContent = t("empty");
    } catch (error) { if (live()) feedback(notifications.querySelector("#accountNotificationFeedback"), errorKey(error), true); }
    finally { if (current === revision) { busy = false; more.disabled = false; } }
  };
  more.onclick = () => load();
  unreadOnly.onchange = () => load(true);
  notifications.querySelector("#accountReadAll").onclick = async (e) => {
    const b = e.currentTarget; b.disabled = true;
    try { await request("/notifications/read-all", "PUT"); await load(true); await updateCount(); }
    catch (error) { feedback(notifications.querySelector("#accountNotificationFeedback"), errorKey(error), true); }
    finally { b.disabled = false; }
  };
  const activate = () => { if (!notifications.closest("[data-account-view-panel]").hidden && !loaded) load(true); };
  document.querySelectorAll("[data-account-view]").forEach((b) => b.addEventListener("click", activate));
  updateCount(); activate();
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
  if (reset && token.length < 20) { form.hidden = true; feedback(message, "invalid", true); return; }
  form.onsubmit = async (e) => {
    e.preventDefault(); const submit = form.querySelector("button");
    if (submit.disabled) return;
    const values = Object.fromEntries(new FormData(form));
    if (reset && values.new_password !== values.repeat_password) { feedback(message, "mismatch", true); return; }
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
    } catch (error) { if (form.isConnected) feedback(message, reset && error.status === 400 ? "invalid" : errorKey(error), true); }
    finally { submit.disabled = false; }
  };
}
