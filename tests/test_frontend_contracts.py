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


def test_entity_cards_keep_verified_profile_data_out_of_list_summaries():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")

    athlete_cards = source.split("function renderAthleteCards", 1)[1].split(
        "function renderAthleteResultsPage",
        1,
    )[0]
    event_cards = source.split("function renderEventList", 1)[1].split(
        "function buildCalendarWeeks",
        1,
    )[0]
    favorite_athletes = source.split("function renderFavoriteAthletes", 1)[1].split(
        "function renderFavoriteEvents",
        1,
    )[0]
    favorite_events = source.split("function renderFavoriteEvents", 1)[1].split(
        "function renderAthleteProfileImage",
        1,
    )[0]

    assert "athleteCardSummaryPills(athlete)" in athlete_cards
    assert "world_gymnastics_status" not in athlete_cards
    assert "birth_year" not in athlete_cards
    assert 'eventCardSummaryPills(event)' in event_cards
    assert "event.location" not in event_cards
    assert "event.venue" not in event_cards
    assert "calendarOnly" not in event_cards
    assert 'athleteCardSummaryPills(athlete, item.athlete_id)' in favorite_athletes
    assert "result_count" not in favorite_athletes
    assert 'eventCardSummaryPills(event)' in favorite_events
    assert "result_count" not in favorite_events


def test_verified_entity_cards_show_badges_and_keep_event_dates_on_a_second_line():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    styles = (PROJECT_ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")

    athlete_title = source.split("function athleteCardTitle", 1)[1].split(
        "function athleteCardSummaryPills",
        1,
    )[0]
    event_title = source.split("function eventCardTitle", 1)[1].split(
        "function currentParams",
        1,
    )[0]

    assert "renderAthleteVerificationBadge(athlete)" in athlete_title
    assert 'class="entity-card-name-line athlete-card-title"' in athlete_title
    assert "renderEventVerificationBadge(event)" in event_title
    assert event_title.index('class="entity-card-name-line"') < event_title.index('class="event-card-date"')
    event_title_styles = styles.split(".event-card-title {", 1)[1].split("}", 1)[0]
    event_date_styles = styles.split(".event-card-date {", 1)[1].split("}", 1)[0]
    assert "display: grid" in event_title_styles
    assert "display: block" in event_date_styles


def test_analytics_favorites_loading_message_is_delayed_to_avoid_flashing():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    render_block = source.split("function renderAnalyticsFavoriteAthletes", 1)[1].split(
        "function renderAnalyticsComparisonSelection",
        1,
    )[0]
    load_block = source.split("async function loadAnalyticsFavoriteAthletes", 1)[1].split(
        "async function selectAnalyticsComparisonAthlete",
        1,
    )[0]

    assert "const ANALYTICS_FAVORITES_LOADING_DELAY_MS = 250" in source
    assert "comparison.favoritesLoading && comparison.favoritesLoadingVisible" in render_block
    assert 'comparison.favoritesLoading && !comparison.favoriteDetails.length) return ""' in render_block
    assert "comparison.favoritesLoadingVisible = false" in load_block
    assert "analyticsFavoritesLoadingTimer = window.setTimeout" in load_block
    assert "ANALYTICS_FAVORITES_LOADING_DELAY_MS" in load_block
    assert "window.clearTimeout(analyticsFavoritesLoadingTimer)" in load_block


def test_saved_ranking_cards_use_the_compact_event_card_title_structure():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    styles = (PROJECT_ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")
    ranking_cards = source.split("function renderSavedRankingViews", 1)[1].split(
        "function accountViewSection",
        1,
    )[0]

    assert 'class="event-card-title saved-ranking-card-title"' in ranking_cards
    assert 'class="event-card-date"' in ranking_cards
    assert 'title,\n      "",' in ranking_cards
    assert ".account-view-panel .account-preference-card-list .entity-card" not in styles


def test_favorite_filter_hover_overrides_the_generic_filter_blue_outline():
    styles = (PROJECT_ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")

    assert '.filter-button.section-favorite-filter:not([aria-pressed="true"]):hover' in styles
    assert '.filter-button.section-favorite-filter:not([aria-pressed="true"]):focus-visible' in styles
    assert '.quiet-button.section-favorite-filter:not([aria-pressed="true"]):hover' in styles
    favorite_hover_block = styles.split(
        '.filter-button.section-favorite-filter:not([aria-pressed="true"]):hover,',
        1,
    )[1].split("}", 1)[0]
    assert "border-color: var(--favorite-yellow)" in favorite_hover_block
    assert "background: #fff" in favorite_hover_block
    assert "color: var(--favorite-yellow)" in favorite_hover_block


def test_saved_ranking_popup_uses_the_leverage_popup_and_control_tokens():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    styles = (PROJECT_ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")
    shell_styles = styles.split(".saved-ranking-form-shell {", 1)[1].split("}", 1)[0]
    input_styles = styles.split(".saved-ranking-form input {", 1)[1].split("}", 1)[0]
    action_styles = styles.split(".saved-ranking-submit {", 1)[1].split("}", 1)[0]
    input_row_styles = styles.split(".saved-ranking-input-row {", 1)[1].split("}", 1)[0]
    input_shell_markup = source.split('class="saved-ranking-input-shell"', 1)[1].split("</span>", 1)[0]

    assert 'class="saved-ranking-filter-summary"' in source
    assert "padding: 13px 14px" in shell_styles
    assert "border-radius: var(--surface-radius)" in shell_styles
    assert "box-shadow: 0 20px 56px rgba(16, 16, 20, 0.12)" in shell_styles
    assert ".saved-ranking-form-shell[hidden]" in styles
    assert "font-size: 14px" in input_styles
    assert "grid-template-columns: minmax(0, 1fr) auto" in input_row_styles
    assert "gap: 7px" in input_row_styles
    assert 'class="saved-ranking-submit"' not in input_shell_markup
    assert "min-height: 36px" in action_styles
    assert "border-radius: var(--control-radius)" in action_styles
    input_shell_styles = styles.split(".saved-ranking-input-shell {", 1)[1].split("}", 1)[0]
    assert "min-height: 36px" in input_shell_styles
    assert "height: 30px" in input_styles
    assert ".saved-ranking-message:empty" in styles
    assert "@keyframes savedRankingPopupIn" in styles


def test_saved_ranking_popup_summarizes_the_number_of_active_filters():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    styles = (PROJECT_ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")
    panel = source.split("function renderRankingSavePanel", 1)[1].split(
        "function renderRankingList",
        1,
    )[0]
    summary_styles = styles.split(".saved-ranking-filter-summary {", 1)[1].split("}", 1)[0]

    assert "savedRankingActiveFilterCount(savedRankingFiltersPayload())" in panel
    assert 'activeFilterCount === 1 ? "activeFilterSingular" : "activeFilterPlural"' in panel
    assert "rankingFilterSummary()" not in panel
    shell_styles = styles.split(".saved-ranking-form-shell {", 1)[1].split("}", 1)[0]
    assert "display: grid" in shell_styles
    assert "gap: 11px" in shell_styles
    assert "padding: 13px 14px" in shell_styles
    assert "font-size: var(--card-meta-size)" in summary_styles
    assert "font-weight: 520" in summary_styles


def test_saved_ranking_empty_name_uses_inline_validation_and_shake_feedback():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    styles = (PROJECT_ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")
    binding = source.split("function bindRankingSaveForm", 1)[1].split(
        "async function hydrateEventsCalendar",
        1,
    )[0]

    assert 'id="rankingSaveForm" novalidate' in source
    assert 'input.setAttribute("aria-invalid", "true")' in binding
    assert 'message.textContent = t("rankingViewNameRequired")' in binding
    assert 'shell.classList.add("is-shaking")' in binding
    assert 'input?.addEventListener("input"' in binding
    assert ".saved-ranking-input-shell.is-invalid" in styles
    assert ".saved-ranking-message.is-error" in styles
    assert "@keyframes savedRankingInvalidShake" in styles
    assert "@media (prefers-reduced-motion: reduce)" in styles


def test_global_search_supports_progressive_loading_without_duplicates():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    global_search = source.split("async function renderGlobalSearch()", 1)[1].split(
        "function featureCard",
        1,
    )[0]

    assert 'renderLoadMoreButton("global-search", t("loadMoreSearchResults"))' in source
    assert "function mergeGlobalSearchResults" in source
    assert "offset: append ? searchOffset : 0" in global_search
    assert "searchOffset + GLOBAL_SEARCH_SECTION_LIMIT" in global_search
    assert 'bindLoadMoreButton("global-search"' in global_search


def test_global_search_detail_links_preserve_home_context_and_return_route():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    global_results = source.split("function searchResultCard", 1)[1].split(
        "async function renderGlobalSearch",
        1,
    )[0]
    athlete_back = source.split("function athleteDetailBackDestination", 1)[1].split(
        "async function renderAthleteDetail",
        1,
    )[0]
    event_back = source.split("function eventDetailBackDestination", 1)[1].split(
        "async function renderAthleteDetail",
        1,
    )[0]

    assert 'params.set("from", "search")' in source
    assert 'params.set("return_to", String(returnRoute || "/search"))' in source
    assert 'globalSearchDetailHref(`#/athletes/${athlete.id}`)' in global_results
    assert 'globalSearchDetailHref(`#/events/${event.id}`)' in global_results
    assert 'globalSearchDetailHref(`#/events/${result.event_id}`)' in global_results
    assert 'source === "search"' in athlete_back
    assert 'params.get("from") === "search"' in event_back
    assert 'label: t("backToGlobalSearch")' in athlete_back
    assert 'label: t("backToGlobalSearch")' in event_back
    assert "routeHasGlobalSearchContext(state.route)" in source


def test_global_search_return_reuses_loaded_results_without_refetching():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    state_block = source.split("const state = {", 1)[1].split("const TODAY", 1)[0]
    global_search = source.split("async function renderGlobalSearch()", 1)[1].split(
        "function featureCard",
        1,
    )[0]

    assert "globalSearch:" in state_block
    assert "state.globalSearch.query === query" in global_search
    assert "renderGlobalSearchResults(cachedSearch.payload)" in global_search
    assert "let searchPayload = cachedSearch?.payload || null" in global_search
    assert "let searchOffset = cachedSearch?.offset || 0" in global_search
    assert "state.globalSearch = {" in global_search
    assert "if (cachedSearch)" in global_search
    cached_branch = global_search.split("if (cachedSearch)", 1)[1].split("trackSiteSearch(query)", 1)[0]
    assert "return;" in cached_branch
    assert 'bindLoadMoreButton("global-search"' in cached_branch
