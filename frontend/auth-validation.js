const messages = {
  required: ["Complete the required fields.", "Completa i campi obbligatori.", "Completa los campos obligatorios.", "Remplissez les champs obligatoires."],
  email: ["Enter a valid email address.", "Inserisci un indirizzo email valido.", "Introduce un correo electrónico válido.", "Saisissez une adresse email valide."],
  password: ["The password must contain 6 to 128 characters.", "La password deve contenere da 6 a 128 caratteri.", "La contraseña debe contener entre 6 y 128 caracteres.", "Le mot de passe doit contenir entre 6 et 128 caractères."],
  mismatch: ["The passwords do not match.", "Le password non coincidono.", "Las contraseñas no coinciden.", "Les mots de passe ne correspondent pas."],
  code: ["Enter a valid authentication or recovery code.", "Inserisci un Codice di Autenticazione o di recupero valido.", "Introduce un código de autenticación o recuperación válido.", "Saisissez un code d’authentification ou de récupération valide."],
  credentials: ["Incorrect email or password.", "Email o password errate.", "Correo o contraseña incorrectos.", "Email ou mot de passe incorrect."],
  wrongCode: ["Incorrect authentication code. Try again.", "Codice di Autenticazione errato. Riprova.", "Código de autenticación incorrecto. Inténtalo de nuevo.", "Code d’authentification incorrect. Réessayez."],
  verification: ["Verify your email before signing in.", "Verifica la tua email prima di accedere.", "Verifica tu correo antes de iniciar sesión.", "Vérifiez votre email avant de vous connecter."],
  rate: ["Too many attempts. Wait before trying again.", "Troppi tentativi. Attendi prima di riprovare.", "Demasiados intentos. Espera antes de reintentar.", "Trop de tentatives. Patientez avant de réessayer."],
  delivery: ["Email delivery is unavailable. Try again later.", "Invio email non disponibile. Riprova più tardi.", "El envío de correo no está disponible. Inténtalo más tarde.", "Envoi d’email indisponible. Réessayez plus tard."],
  network: ["Unable to connect. Check your connection and try again.", "Connessione non riuscita. Controlla la connessione e riprova.", "No se pudo conectar. Comprueba la conexión y reintenta.", "Connexion impossible. Vérifiez votre connexion et réessayez."],
  invalid: ["Some values are invalid. Check the highlighted fields.", "Alcuni dati non sono validi. Controlla i campi evidenziati.", "Algunos datos no son válidos. Revisa los campos resaltados.", "Certaines données sont invalides. Vérifiez les champs indiqués."],
  expired: ["This link is invalid or expired. Request a new one.", "Il link non è valido o è scaduto. Richiedine uno nuovo.", "El enlace no es válido o ha caducado. Solicita otro.", "Lien invalide ou expiré. Demandez-en un nouveau."],
  current: ["The current password is incorrect.", "La password attuale è errata.", "La contraseña actual es incorrecta.", "Le mot de passe actuel est incorrect."],
  session: ["Your session expired. Sign in again.", "Sessione scaduta. Accedi nuovamente.", "Sesión caducada. Inicia sesión de nuevo.", "Session expirée. Reconnectez-vous."],
  failed: ["Unable to complete the operation. Try again later.", "Impossibile completare l’operazione. Riprova più tardi.", "No se pudo completar la operación. Inténtalo más tarde.", "Impossible de terminer l’opération. Réessayez plus tard."],
};

export function bindAuthValidation(form, message, getLanguage) {
  form.noValidate = true;
  const shell = form.closest('.auth-panel') || form;
  const main = shell.closest('.auth-main-view');
  if (main) {
    main.style.setProperty('--auth-feedback-growth', '0px');
  }
  const anchorLayout = () => {
    const main = shell.closest('.auth-main-view');
    if (!main || shell.hasAttribute('data-auth-anchored')) return;
    // Preserve the initially centered position while feedback expands below it.
    const top = shell.getBoundingClientRect().top;
    const padding = parseFloat(getComputedStyle(main).paddingTop);
    main.style.setProperty('--auth-bottom-space', getComputedStyle(main).paddingBottom);
    const links = main.querySelector('.auth-login-links');
    main.style.setProperty('--auth-links-space', links ? getComputedStyle(links).marginTop : '0px');
    main.style.setProperty('--auth-content-top', `${padding}px`);
    shell.setAttribute('data-auth-anchored', '');
    const shift = top - shell.getBoundingClientRect().top;
    main.style.setProperty('--auth-content-top', `${Math.max(padding, padding + shift)}px`);
  };
  const inputs = () => [...form.querySelectorAll('input')].filter((input) => !input.disabled && input.type !== 'hidden' && !input.closest('[hidden]'));
  const text = (key) => messages[key][Math.max(0, ['en', 'it', 'es', 'fr'].indexOf(getLanguage()))];
  const clear = () => {
    form.querySelectorAll('[aria-invalid]').forEach((input) => {
      input.removeAttribute('aria-invalid');
      input.classList.remove('is-invalid');
      if (input.getAttribute('aria-describedby') === message.id) input.removeAttribute('aria-describedby');
    });
    shell.classList.remove('is-shaking');
    if (message.dataset.authError) {
      message.textContent = '';
      message.classList.remove('auth-validation-message', 'is-error');
      delete message.dataset.authError;
    }
    main?.style.setProperty('--auth-feedback-growth', '0px');
  };
  const show = (issues) => {
    anchorLayout();
    clear();
    const initialHeight = shell.offsetHeight;
    message.classList.remove('is-success', 'account-feedback');
    message.classList.add('auth-validation-message', 'is-error');
    message.dataset.authError = 'true';
    message.textContent = [...new Set(issues.map((issue) => text(issue.key)))].join(' ');
    main?.style.setProperty('--auth-feedback-growth', `${Math.max(0, shell.offsetHeight - initialHeight)}px`);
    const fields = [...new Set(issues.flatMap((issue) => issue.fields || []))];
    fields.forEach((input) => {
      input.setAttribute('aria-invalid', 'true');
      input.setAttribute('aria-describedby', message.id);
      input.classList.add('is-invalid');
    });
    void shell.offsetWidth;
    shell.classList.add('is-shaking');
    fields[0]?.focus({ preventScroll: true });
  };
  form.addEventListener('input', clear);
  const validate = () => {
    anchorLayout();
    clear();
    const fields = inputs(), issues = [];
    for (const input of fields) {
      if (input.type !== 'password') input.value = input.value.trim();
      const value = input.value;
      if (input.required && !value) { issues.push({ key: 'required', fields: [input] }); continue; }
      if (!value) continue;
      if (input.type === 'email' && !input.validity.valid) issues.push({ key: 'email', fields: [input] });
      else if (input.type === 'password' && (value.length < (input.minLength > 0 ? input.minLength : 6) || value.length > 128)) issues.push({ key: 'password', fields: [input] });
      else if (input.id === 'loginMfaCode' && (value.length < 6 || value.length > 64)) issues.push({ key: 'code', fields: [input] });
    }
    const confirmation = form.querySelector('#registerPasswordConfirm, [name="repeat_password"]');
    const password = form.querySelector('#registerPassword, [name="new_password"]');
    if (confirmation?.value && password?.value && confirmation.value !== password.value) issues.push({ key: 'mismatch', fields: [confirmation] });
    if (issues.length) show(issues);
    return !issues.length;
  };
  const serverError = (error, mode) => {
    const status = error.status, detail = error.detail;
    const fields = inputs();
    let key = 'failed', affected = [];
    if (status === 429) key = 'rate';
    else if (status === 503) key = 'delivery';
    else if (!status) key = 'network';
    else if (status === 403 && detail === 'Email verification required') key = 'verification';
    else if (status === 401 && mode === 'login') {
      key = detail === 'Invalid authentication credentials' ? 'wrongCode' : 'credentials';
      affected = fields.filter((f) => key === 'wrongCode' ? f.id === 'loginMfaCode' : f.type === 'email' || f.type === 'password');
    } else if (status === 401) key = 'session';
    else if (status === 400 && mode === 'reset') key = 'expired';
    else if (status === 400 && mode === 'change') { key = 'current'; affected = fields.filter((f) => f.name === 'current_password'); }
    else if (status === 422) {
      key = 'invalid';
      const names = Array.isArray(detail) ? detail.map((item) => item.loc?.at(-1)) : [];
      affected = fields.filter((f) => names.includes(f.name) || (names.includes('email') && f.type === 'email') || (names.includes('password') && f.type === 'password') || (names.includes('mfa_code') && f.id === 'loginMfaCode'));
      if (!affected.length) affected = fields;
    }
    show([{ key, fields: affected }]);
  };
  return { validate, serverError };
}
