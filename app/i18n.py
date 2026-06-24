from typing import Any, Optional

from app import models


SUPPORTED_LANGUAGE_OPTIONS = (
    {"code": models.LanguageEnum.EN, "label": "English"},
    {"code": models.LanguageEnum.IT, "label": "Italiano"},
    {"code": models.LanguageEnum.ES, "label": "Español"},
    {"code": models.LanguageEnum.FR, "label": "Français"},
)


def normalize_language(language: Any, default: models.LanguageEnum = models.LanguageEnum.EN) -> models.LanguageEnum:
    value = language.value if hasattr(language, "value") else language
    try:
        return models.LanguageEnum(value)
    except ValueError:
        return default


def language_from_accept_language(accept_language: Optional[str]) -> Optional[models.LanguageEnum]:
    if not accept_language:
        return None

    weighted_languages = []
    for raw_part in accept_language.split(","):
        part = raw_part.strip()
        if not part:
            continue

        language_tag, _, quality_part = part.partition(";")
        quality = 1.0
        if quality_part.strip().startswith("q="):
            try:
                quality = float(quality_part.strip()[2:])
            except ValueError:
                quality = 0.0

        language_code = language_tag.split("-")[0].lower()
        weighted_languages.append((quality, language_code))

    for _, language_code in sorted(weighted_languages, reverse=True):
        try:
            return models.LanguageEnum(language_code)
        except ValueError:
            continue

    return None


def resolve_public_language(
    selected_language: Any = None,
    accept_language: Optional[str] = None,
) -> tuple[models.LanguageEnum, str]:
    if selected_language is not None:
        return normalize_language(selected_language), "selected"

    header_language = language_from_accept_language(accept_language)
    if header_language is not None:
        return header_language, "accept_language"

    return models.LanguageEnum.EN, "default"


RESULT_CONTEXT_LABELS = {
    models.LanguageEnum.EN: {
        (models.RoundEnum.QUALIFICATION, models.FormatEnum.INDIVIDUAL): "individual qualification",
        (models.RoundEnum.QUALIFICATION, models.FormatEnum.TEAM): "team qualification",
        (models.RoundEnum.QUALIFICATION, models.FormatEnum.APPARATUS): "apparatus qualification",
        (models.RoundEnum.FINAL, models.FormatEnum.INDIVIDUAL): "individual final",
        (models.RoundEnum.FINAL, models.FormatEnum.TEAM): "team final",
        (models.RoundEnum.FINAL, models.FormatEnum.APPARATUS): "apparatus final",
    },
    models.LanguageEnum.IT: {
        (models.RoundEnum.QUALIFICATION, models.FormatEnum.INDIVIDUAL): "qualifica individuale",
        (models.RoundEnum.QUALIFICATION, models.FormatEnum.TEAM): "qualifica team",
        (models.RoundEnum.QUALIFICATION, models.FormatEnum.APPARATUS): "qualifica ad attrezzo",
        (models.RoundEnum.FINAL, models.FormatEnum.INDIVIDUAL): "finale individuale",
        (models.RoundEnum.FINAL, models.FormatEnum.TEAM): "finale team",
        (models.RoundEnum.FINAL, models.FormatEnum.APPARATUS): "finale ad attrezzo",
    },
    models.LanguageEnum.ES: {
        (models.RoundEnum.QUALIFICATION, models.FormatEnum.INDIVIDUAL): "clasificacion individual",
        (models.RoundEnum.QUALIFICATION, models.FormatEnum.TEAM): "clasificacion por equipos",
        (models.RoundEnum.QUALIFICATION, models.FormatEnum.APPARATUS): "clasificacion por aparato",
        (models.RoundEnum.FINAL, models.FormatEnum.INDIVIDUAL): "final individual",
        (models.RoundEnum.FINAL, models.FormatEnum.TEAM): "final por equipos",
        (models.RoundEnum.FINAL, models.FormatEnum.APPARATUS): "final por aparato",
    },
    models.LanguageEnum.FR: {
        (models.RoundEnum.QUALIFICATION, models.FormatEnum.INDIVIDUAL): "qualification individuelle",
        (models.RoundEnum.QUALIFICATION, models.FormatEnum.TEAM): "qualification par equipes",
        (models.RoundEnum.QUALIFICATION, models.FormatEnum.APPARATUS): "qualification par agrès",
        (models.RoundEnum.FINAL, models.FormatEnum.INDIVIDUAL): "finale individuelle",
        (models.RoundEnum.FINAL, models.FormatEnum.TEAM): "finale par equipes",
        (models.RoundEnum.FINAL, models.FormatEnum.APPARATUS): "finale par agrès",
    },
}


TRANSLATIONS = {
    "notification.new_result.single": {
        models.LanguageEnum.EN: "New score for {athlete_name} during the {context_label} at {event_name}.",
        models.LanguageEnum.IT: "Nuovo punteggio di {athlete_name} durante la {context_label} alla {event_name}.",
        models.LanguageEnum.ES: "Nueva puntuacion de {athlete_name} durante la {context_label} en {event_name}.",
        models.LanguageEnum.FR: "Nouvelle note de {athlete_name} pendant la {context_label} à {event_name}.",
    },
    "notification.new_result.plural": {
        models.LanguageEnum.EN: "New scores for {athlete_name} during the {context_label} at {event_name}: {result_count} results available.",
        models.LanguageEnum.IT: "Nuovi punteggi di {athlete_name} durante la {context_label} alla {event_name}: {result_count} risultati disponibili.",
        models.LanguageEnum.ES: "Nuevas puntuaciones de {athlete_name} durante la {context_label} en {event_name}: {result_count} resultados disponibles.",
        models.LanguageEnum.FR: "Nouvelles notes de {athlete_name} pendant la {context_label} à {event_name} : {result_count} resultats disponibles.",
    },
    "notification.new_event": {
        models.LanguageEnum.EN: "New event '{event_name}' at {level} level has been added.",
        models.LanguageEnum.IT: "Nuovo evento '{event_name}' di livello {level} aggiunto.",
        models.LanguageEnum.ES: "Nuevo evento '{event_name}' de nivel {level} anadido.",
        models.LanguageEnum.FR: "Nouvel evenement '{event_name}' de niveau {level} ajoute.",
    },
    "notification.admin_promotion": {
        models.LanguageEnum.EN: "You have been promoted to ADMIN. On your next login, you must configure two-factor authentication to use LEVERAGE admin tools.",
        models.LanguageEnum.IT: "Hai ottenuto la promozione ad ADMIN. Al prossimo accesso dovrai configurare l'autenticazione a due fattori per usare gli strumenti di amministrazione di LEVERAGE.",
        models.LanguageEnum.ES: "Has sido promovido a ADMIN. En tu proximo acceso deberas configurar la autenticacion de dos factores para usar las herramientas de administracion de LEVERAGE.",
        models.LanguageEnum.FR: "Vous avez ete promu ADMIN. A votre prochaine connexion, vous devrez configurer l'authentification a deux facteurs pour utiliser les outils d'administration de LEVERAGE.",
    },
    "notification.super_admin_promotion": {
        models.LanguageEnum.EN: "You have been promoted to SUPER ADMIN. On your next login, you must configure two-factor authentication to manage roles, restore data and critical operations.",
        models.LanguageEnum.IT: "Hai ottenuto la promozione a SUPER ADMIN. Al prossimo accesso dovrai configurare l'autenticazione a due fattori per gestire ruoli, restore e operazioni critiche.",
        models.LanguageEnum.ES: "Has sido promovido a SUPER ADMIN. En tu proximo acceso deberas configurar la autenticacion de dos factores para gestionar roles, restauraciones y operaciones criticas.",
        models.LanguageEnum.FR: "Vous avez ete promu SUPER ADMIN. A votre prochaine connexion, vous devrez configurer l'authentification a deux facteurs pour gerer les roles, les restaurations et les operations critiques.",
    },
    "notification.admin_demotion": {
        models.LanguageEnum.EN: "Your ADMIN role has been removed. Your account now has standard USER permissions.",
        models.LanguageEnum.IT: "Il tuo ruolo ADMIN e stato rimosso. Ora il tuo account ha i permessi USER standard.",
        models.LanguageEnum.ES: "Tu rol ADMIN ha sido eliminado. Tu cuenta ahora tiene permisos USER estandar.",
        models.LanguageEnum.FR: "Votre role ADMIN a ete retire. Votre compte dispose maintenant des autorisations USER standard.",
    },
    "notification.data_entry_formula_blocked": {
        models.LanguageEnum.EN: "Manual import blocked for {event_name}: {count} result(s) do not match Final Score = D + E - P + B. Check and correct: {preview}{suffix}.",
        models.LanguageEnum.IT: "Import manuale bloccato per {event_name}: {count} result non tornano con la formula Final Score = D + E - P + B. Controlla e correggi: {preview}{suffix}.",
        models.LanguageEnum.ES: "Importacion manual bloqueada para {event_name}: {count} result(s) no coinciden con Final Score = D + E - P + B. Revisa y corrige: {preview}{suffix}.",
        models.LanguageEnum.FR: "Import manuel bloque pour {event_name} : {count} result(s) ne correspondent pas a Final Score = D + E - P + B. Verifiez et corrigez : {preview}{suffix}.",
    },
    "notification.data_entry_created_athletes": {
        models.LanguageEnum.EN: "Manual data entry report for {event_name}: {count} new athlete(s) created ({athlete_names}). Complete the athlete profile as soon as possible.",
        models.LanguageEnum.IT: "Report data entry manuale per {event_name}: {count} nuovo/i atleta/i creato/i ({athlete_names}). Completa la scheda atleta appena possibile.",
        models.LanguageEnum.ES: "Reporte de entrada manual para {event_name}: {count} nuevo(s) atleta(s) creado(s) ({athlete_names}). Completa la ficha del atleta lo antes posible.",
        models.LanguageEnum.FR: "Rapport de saisie manuelle pour {event_name} : {count} nouvel/nouveaux athlete(s) cree(s) ({athlete_names}). Completez la fiche athlete des que possible.",
    },
    "notification.event_results_reminder": {
        models.LanguageEnum.EN: "Result reminder: event {event_name} ended {days_since_end} day(s) ago and still has no Result entries.",
        models.LanguageEnum.IT: "Reminder risultati: l'evento {event_name} risulta concluso da {days_since_end} giorni e non ha ancora Result inseriti.",
        models.LanguageEnum.ES: "Recordatorio de resultados: el evento {event_name} termino hace {days_since_end} dia(s) y aun no tiene Result cargados.",
        models.LanguageEnum.FR: "Rappel resultats : l'evenement {event_name} est termine depuis {days_since_end} jour(s) et n'a encore aucun Result saisi.",
    },
    "notification.import_summary": {
        models.LanguageEnum.EN: (
            "Gymternet import report: {created_athletes} new athlete(s); {created_events} new event(s); "
            "{created_results} new score(s); {created_complete_results} complete score(s); "
            "{created_partial_results} score(s) with not available data; {athletes_with_new_results} athlete(s) with new results; "
            "{events_with_new_results} event(s) with new results; {updated_events} updated event(s); "
            "{updated_athlete_countries} athlete country change(s); {corrected_represented_countries} represented country correction(s); "
            "{orphan_dscore_review_uncommitted} orphan D-score(s) left in review; "
            "{skipped_duplicates} duplicate(s) skipped."
        ),
        models.LanguageEnum.IT: (
            "Report import Gymternet: {created_athletes} nuovo/i atleta/i; {created_events} nuovo/i evento/i; "
            "{created_results} nuovo/i punteggio/i; {created_complete_results} punteggio/i completo/i; "
            "{created_partial_results} punteggio/i con dati not available; {athletes_with_new_results} atleta/i con nuovi risultati; "
            "{events_with_new_results} evento/i con nuovi risultati; {updated_events} evento/i aggiornato/i; "
            "{updated_athlete_countries} cambio/i country atleta; {corrected_represented_countries} correzione/i represented country; "
            "{orphan_dscore_review_uncommitted} D-score orfano/i rimasto/i in review; "
            "{skipped_duplicates} duplicato/i saltato/i."
        ),
        models.LanguageEnum.ES: (
            "Reporte de importacion Gymternet: {created_athletes} nuevo(s) atleta(s); {created_events} nuevo(s) evento(s); "
            "{created_results} nueva(s) puntuacion(es); {created_complete_results} puntuacion(es) completa(s); "
            "{created_partial_results} puntuacion(es) con datos not available; {athletes_with_new_results} atleta(s) con nuevos resultados; "
            "{events_with_new_results} evento(s) con nuevos resultados; {updated_events} evento(s) actualizado(s); "
            "{updated_athlete_countries} cambio(s) de country de atleta; {corrected_represented_countries} correccion(es) de represented country; "
            "{orphan_dscore_review_uncommitted} D-score huerfano(s) pendiente(s) de revision; "
            "{skipped_duplicates} duplicado(s) omitido(s)."
        ),
        models.LanguageEnum.FR: (
            "Rapport d'import Gymternet : {created_athletes} nouvel/nouveaux athlete(s) ; {created_events} nouvel/nouveaux evenement(s) ; "
            "{created_results} nouvelle(s) note(s) ; {created_complete_results} note(s) complete(s) ; "
            "{created_partial_results} note(s) avec donnees not available ; {athletes_with_new_results} athlete(s) avec nouveaux resultats ; "
            "{events_with_new_results} evenement(s) avec nouveaux resultats ; {updated_events} evenement(s) mis a jour ; "
            "{updated_athlete_countries} changement(s) de country athlete ; {corrected_represented_countries} correction(s) represented country ; "
            "{orphan_dscore_review_uncommitted} D-score orphelin(s) restant en review ; "
            "{skipped_duplicates} doublon(s) ignore(s)."
        ),
    },
}


def result_context_label(
    round_value: models.RoundEnum,
    format_value: models.FormatEnum,
    language: Any = models.LanguageEnum.EN,
) -> str:
    resolved_language = normalize_language(language)
    labels = RESULT_CONTEXT_LABELS.get(resolved_language, RESULT_CONTEXT_LABELS[models.LanguageEnum.EN])
    return labels.get((round_value, format_value), RESULT_CONTEXT_LABELS[models.LanguageEnum.EN][(round_value, format_value)])


def translate(key: str, language: Any = models.LanguageEnum.EN, **params) -> str:
    resolved_language = normalize_language(language)
    translations = TRANSLATIONS[key]
    template = translations.get(resolved_language, translations[models.LanguageEnum.EN])
    return template.format(**params)
