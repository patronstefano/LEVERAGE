from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_local_preview_uses_only_the_canonical_backend_port():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    fallback_block = source.split("const API_FALLBACK_BASES = [", 1)[1].split("];", 1)[0]

    assert '"http://127.0.0.1:8000"' in fallback_block
    assert '"http://localhost:8000"' in fallback_block
    assert ":8001" not in fallback_block
    assert ":8002" not in fallback_block
    assert "800[0-2]" in source


def test_verified_athlete_badge_is_rendered_in_the_profile_metadata():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    styles = (PROJECT_ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")

    assert "function renderAthleteProfileMeta(athlete)" in source
    assert "renderAthleteVerificationBadge(athlete)" in source
    assert 'aria-hidden="true">✓</span>' in source
    assert ".athlete-profile-meta" in styles
    assert ".athlete-verification-badge" in styles
    badge_styles = styles.split(".athlete-verification-badge {", 1)[1].split("}", 1)[0]
    assert "width: 16px" in badge_styles
    assert "margin-left: 3px" in badge_styles
    assert "clip-path: polygon(" in badge_styles


def test_verified_event_uses_the_same_badge_and_identity_layout_as_athlete():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")

    assert "function renderEventVerificationBadge(event)" in source
    assert "if (!event?.world_gymnastics_verified_at) return \"\";" in source
    assert 'renderEventVerificationBadge(event)' in source
    assert 'class="athlete-verification-badge event-verification-badge"' in source
    event_items_block = source.split("const eventWorldGymnasticsItems = [", 1)[1].split(
        "].filter((item)",
        1,
    )[0]
    expected_labels = [
        't("worldGymnasticsId")',
        't("worldGymnasticsStatus")',
        't("worldGymnasticsProfile")',
        't("worldGymnasticsVerified")',
        't("verifiedByAdminId")',
    ]
    positions = [event_items_block.index(label) for label in expected_labels]
    assert positions == sorted(positions)
    assert 'class="timeline-list"' in source
    assert "displayEnumValue(event.world_gymnastics_status)" in event_items_block


def test_verification_badge_removal_uses_neutral_danger_feedback():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    styles = (PROJECT_ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")

    assert 'setAdminSuggestionFeedback(message, t("badgeRemoved"), "danger")' in source
    danger_styles = styles.split(
        ".athlete-admin-panel .auth-message.is-danger:not(:empty) {",
        1,
    )[1].split("}", 1)[0]
    assert "background: transparent" in danger_styles
    assert "color: var(--danger)" in danger_styles


def test_world_gymnastics_identity_fields_have_stable_order_and_status_casing():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    items_block = source.split("const worldGymnasticsItems = [", 1)[1].split(
        "].filter((item)",
        1,
    )[0]

    expected_labels = [
        't("worldGymnasticsId")',
        't("worldGymnasticsStatus")',
        't("worldGymnasticsProfile")',
        't("worldGymnasticsVerified")',
        't("verifiedByAdminId")',
    ]
    positions = [items_block.index(label) for label in expected_labels]
    assert positions == sorted(positions)
    assert "displayEnumValue(athlete.world_gymnastics_status)" in items_block


def test_event_admin_tools_follow_the_controlled_world_gymnastics_flow():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")

    assert "function renderWorldGymnasticsMatchedEventProfile(response)" in source
    assert 'body: { ...payload, create_suggestions: false }' in source
    assert 'data-event-world-gymnastics-fields' in source
    assert 'removeEventWorldGymnasticsVerification' in source
    assert 'method: "PATCH"' in source
    assert 'remove_world_gymnastics_verification: true' in source
    assert 'isAdminUser()\n      ? [t("verifiedByAdminId"), event.world_gymnastics_verified_by_admin_id]' in source


def test_event_search_keeps_the_incomplete_final_card_row():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    split_block = source.split("function splitEventListFullRows", 1)[1].split(
        "function renderEventList",
        1,
    )[0]
    render_block = source.split("function renderEventList", 1)[1].split(
        "function buildCalendarWeeks",
        1,
    )[0]

    assert "if (!hasMore || !remainder" in split_block
    assert "pending: events.slice(visibleCount)" in split_block
    assert "splitEventListFullRows(displayEvents, true)" not in render_block


def test_athlete_search_keeps_every_card_in_the_final_page():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    card_block = source.split("function renderAthleteCards", 1)[1].split(
        "function renderAthleteResultsPage",
        1,
    )[0]
    load_block = source.split("const loadAthletes = async", 1)[1].split(
        "const refreshAthleteResults",
        1,
    )[0]

    assert "athletes.map((athlete)" in card_block
    assert "slice(" not in card_block
    assert "splitEventListFullRows" not in card_block
    assert "slice(0, ATHLETE_SECTION_LIMIT)" in load_block
    assert "athleteHasMore = athletes.length > ATHLETE_SECTION_LIMIT" in load_block


def test_result_warnings_share_relevance_and_rendering_rules_across_views():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    styles = (PROJECT_ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")

    helper = source.split("function relevantResultDataWarnings", 1)[1].split(
        "function localizedWorldGymnasticsWarning",
        1,
    )[0]
    event_block = source.split("function eventResultWarningMessages", 1)[1].split(
        "function renderEventResultWarnings",
        1,
    )[0]

    assert 'selectedMetric === "execution_estimate"' in helper
    assert 'selectedApparatuses.has("VT") || selectedApparatuses.has("VT AVG")' in helper
    assert "return localizedBackendWarnings(warnings)" in helper
    assert 't("analyticsEEstimateNotice")' in event_block
    assert "relevantResultDataWarnings(results, selectedMetric, [selectedApparatus])" in event_block
    assert 'renderDataWarningStack(eventResultWarningMessages(results, payload), "event-result-warning-stack")' in source
    warning_styles = styles.split(".data-warning-box {", 1)[1].split("}", 1)[0]
    assert "background: transparent" in warning_styles
    assert "border-radius: var(--surface-radius)" in warning_styles
