const API_BASE_KEY = "leverage.apiBase";
const LANGUAGE_KEY = "leverage.language";
const AUTH_TOKEN_KEY = "leverage.authToken";
const SECTION_ROUTE_MEMORY_KEY = "leverage.sectionRoutes";
const API_FALLBACK_BASES = [
  "http://127.0.0.1:8002",
  "http://localhost:8002",
  "http://127.0.0.1:8001",
  "http://localhost:8001",
  "http://127.0.0.1:8000",
  "http://localhost:8000",
];

function initialApiBase() {
  const storedApiBase = localStorage.getItem(API_BASE_KEY) || "";
  const isLocalPreview = ["127.0.0.1", "localhost"].includes(window.location.hostname)
    && window.location.port.startsWith("517");
  if (isLocalPreview && (!storedApiBase || /:800[01]\/?$/.test(storedApiBase))) {
    localStorage.setItem(API_BASE_KEY, API_FALLBACK_BASES[0]);
    return API_FALLBACK_BASES[0];
  }
  return storedApiBase || API_FALLBACK_BASES[0];
}

const SECTION_BASE_ROUTES = {
  athletes: "/athletes",
  events: "/events",
  rankings: "/rankings",
  analytics: "/analytics",
};

function routeSection(route) {
  const routePath = String(route || "/").split("?")[0];
  if (routePath === "/athletes" || routePath.startsWith("/athletes/")) return "athletes";
  if (routePath === "/events" || routePath.startsWith("/events/")) return "events";
  if (routePath === "/rankings" || routePath.startsWith("/rankings/")) return "rankings";
  if (routePath === "/analytics" || routePath.startsWith("/analytics/")) return "analytics";
  return "";
}

function contextualAthleteSourceSection(route) {
  const [routePath, query = ""] = String(route || "/").split("?");
  if (!/^\/athletes\/\d+$/.test(routePath)) return "";
  const source = new URLSearchParams(query).get("from") || "";
  if (source === "athletes") return "athletes";
  if (source === "ranking") return "rankings";
  if (source === "classification") return "events";
  return "";
}

function activeRouteSection(route) {
  return contextualAthleteSourceSection(route) || routeSection(route);
}

function isAthleteSectionDetailRoute(route) {
  const routePath = String(route || "/").split("?")[0];
  return /^\/athletes\/\d+$/.test(routePath) && activeRouteSection(route) === "athletes";
}

function routeBelongsToSection(route, section) {
  return activeRouteSection(route) === section;
}

function initialSectionRoutes() {
  let storedRoutes = {};
  try {
    storedRoutes = JSON.parse(sessionStorage.getItem(SECTION_ROUTE_MEMORY_KEY) || "{}");
  } catch (_error) {
    storedRoutes = {};
  }
  return Object.fromEntries(Object.entries(SECTION_BASE_ROUTES).map(([section, fallbackRoute]) => {
    const storedRoute = storedRoutes[section];
    return [section, routeBelongsToSection(storedRoute, section) ? storedRoute : fallbackRoute];
  }));
}

const state = {
  route: "/",
  language: localStorage.getItem(LANGUAGE_KEY) || "en",
  apiBase: initialApiBase(),
  authToken: localStorage.getItem(AUTH_TOKEN_KEY) || "",
  currentUser: null,
  emailVerification: {
    token: "",
    status: "idle",
  },
  favoriteAthleteIds: new Set(),
  favoriteEventIds: new Set(),
  favoritesLoaded: false,
  eventsCalendarMonthOffset: 0,
  eventsCalendarNavigationKey: "",
  eventsViewMode: "list",
  athleteSortMode: "name",
  eventsFavoriteCalendarAutoFocus: false,
  openEventTimeFilter: false,
  openRankingTimeFilter: false,
  openEventDateWheel: "",
  openRankingDateWheel: "",
  sectionRoutes: initialSectionRoutes(),
  athleteAnalytics: {
    metric: "score",
    mode: "period",
    apparatuses: ["AA"],
    startIndex: -1,
    endIndex: -1,
    snapshotIndex: -1,
    payload: null,
  },
  analyticsComparison: {
    athletes: [null, null],
    payloads: [null, null],
    favoriteDetails: [],
    favoritesOpen: false,
    favoritesLoading: false,
    favoritesError: "",
    metric: "score",
    mode: "period",
    apparatuses: ["AA"],
    layout: "side-by-side",
    startIndex: -1,
    endIndex: -1,
    snapshotIndex: -1,
  },
  eventDetail: {
    eventId: null,
    profile: null,
    selectedClassificationKey: "",
    sortBy: "score",
  },
  filters: {
    athletes: {
      discipline: [],
      category: [],
      favoritesOnly: "",
    },
    events: {
      discipline: [],
      category: [],
      level: [],
      favoritesOnly: "",
      startDate: "",
      endDate: "",
      startPeriod: "",
      endPeriod: "",
    },
    rankings: {
      discipline: [],
      category: [],
      level: [],
      sortBy: "score",
      apparatus: ["AA"],
      scoringCycle: [],
      startYear: "",
      endYear: "",
      startDate: "",
      endDate: "",
      startPeriod: "",
      endPeriod: "",
    },
  },
};
const TODAY = new Date();
const DATE_PICKER_START_YEAR = 2018;
const DATE_PICKER_END_YEAR = TODAY.getFullYear();
const ATHLETE_SECTION_LIMIT = 96;
const EVENT_CARD_COLUMN_COUNT = 3;
const EVENT_SECTION_LIMIT = 60;
const RANKING_SECTION_LIMIT = 60;
const RANKING_APPARATUS_BY_DISCIPLINE = {
  MAG: ["AA", "FX", "PH", "SR", "VT", "PB", "HB", "VT AVG"],
  WAG: ["AA", "VT", "UB", "BB", "FX", "VT AVG"],
};
const SCORING_CYCLE_FILTERS = ["2017-2021", "2022-2024", "2025-2028"];
const EVENT_LEVEL_FILTERS = [
  { label: "Olympic Games", value: "Olympic Games", abbreviation: "OG" },
  { label: "World Championships", value: "World Championships", abbreviation: "WCh" },
  { label: "Continental Championships", value: "Continental Championships", abbreviation: "CCh" },
  { label: "World Cup", value: "World Cup", abbreviation: "WC" },
  { label: "World Challenge Cup", value: "World Challenge Cup", abbreviation: "WCC" },
  { label: "International Events", value: "International Event", abbreviation: "INT" },
  { label: "National Events", value: "National Event", abbreviation: "NAT" },
];
const RANKING_METRIC_FILTERS = [
  { label: "Final Score", value: "score" },
  { label: "D Score", value: "D_score" },
  { label: "E Score", value: "execution_estimate" },
  { label: "Penalty", value: "Penalty" },
  { label: "Bonus", value: "Bonus" },
];
const ATHLETE_ANALYTICS_APPARATUS_ORDER = {
  MAG: ["FX", "PH", "SR", "VT", "PB", "HB"],
  WAG: ["VT", "UB", "BB", "FX"],
};
const EVENT_CLASSIFICATION_FIXED_OPTIONS = {
  discipline: ["MAG", "WAG"],
  category: ["senior", "junior"],
  round: ["final", "qualification"],
  format: ["individual", "apparatus", "team", "mixed team"],
};
const ATHLETE_ANALYTICS_METRICS = RANKING_METRIC_FILTERS;
const ATHLETE_TREND_SVG_WIDTH = 900;
const ATHLETE_TREND_SVG_HEIGHT = 300;
const ATHLETE_TREND_SVG_PADDING = { top: 22, right: 24, bottom: 42, left: 48 };
const ATHLETE_TREND_COMPONENT_COLORS = {
  score: "#6f7480",
  D_score: "#4f8fd8",
  E_score: "#45a874",
  execution_estimate: "#45a874",
  Penalty: "#c79a35",
  Bonus: "#d8649c",
  FX: "#4f8fd8",
  PH: "#c79a35",
  SR: "#45a874",
  VT: "#d8649c",
  PB: "#7876d8",
  HB: "#28a5a0",
  UB: "#9a70d6",
  BB: "#d08b45",
  VT1: "#d8649c",
  VT2: "#52a9c8",
};
const ANALYTICS_COMPARISON_COLORS = ["#191747", "#9f3047"];
let searchAutocompleteRequestId = 0;
let athleteSearchRequestId = 0;
let eventSearchRequestId = 0;
let eventDetailRankingRequestId = 0;
let eventDetailRankingAbortController = null;
let eventDetailRankingRefreshTimer = null;
const sectionFilterRefreshers = {
  athletes: null,
  events: null,
  rankings: null,
};
let stickySummaryCleanups = [];

const translations = {
  en: {
    navHome: "Home",
    navAthletes: "Athletes",
    navEvents: "Events",
    navRankings: "Rankings",
    navAnalytics: "Analytics",
    athletesMenuSearch: "Search athletes",
    athletesMenuSearchText: "Find gymnasts by name, country or discipline.",
    athletesMenuProfiles: "Athlete profiles",
    athletesMenuProfilesText: "Open clean athlete cards with official details.",
    athletesMenuCompare: "Compare athletes",
    athletesMenuCompareText: "Prepare trends and side-by-side analysis.",
    eventsMenuCalendar: "Calendar",
    eventsMenuCalendarText: "Browse past and upcoming competitions.",
    eventsMenuResults: "Event results",
    eventsMenuResultsText: "Filter rankings by discipline, category and round.",
    eventsMenuRankings: "Competition rankings",
    eventsMenuRankingsText: "Move from an event to its score tables.",
    rankingsMenuScores: "Score rankings",
    rankingsMenuScoresText: "Sort by final score and available components.",
    rankingsMenuFilters: "Smart filters",
    rankingsMenuFiltersText: "Use only values that exist in the data.",
    rankingsMenuQuality: "Data quality",
    rankingsMenuQualityText: "Spot estimated or not available values.",
    analyticsMenuTrends: "Performance trends",
    analyticsMenuTrendsText: "Follow scores across selected periods.",
    analyticsMenuAge: "Age and country",
    analyticsMenuAgeText: "Study age distributions by country and event.",
    analyticsMenuApparatus: "Apparatus profiles",
    analyticsMenuApparatusText: "Prepare MAG and WAG apparatus diagrams.",
    signIn: "Sign in",
    account: "Personal Area",
    signOut: "Sign out",
    email: "Email",
    password: "Password",
    mfaCode: "MFA code",
    loginAction: "Sign in",
    loginHelp: "Access your private area to save athletes and events.",
    loginError: "Unable to sign in. Check your credentials and email verification.",
    registerPrompt: "New to LEVERAGE?",
    registerLink: "Create an account",
    registerHeading: "Create your account",
    registerIntro: "Join LEVERAGE to save athletes, events and your personal Ranking configurations.",
    registerHelp: "Use a valid email address and choose a password with at least 12 characters.",
    confirmPassword: "Confirm password",
    registerAction: "Create account",
    alreadyRegistered: "Already registered?",
    backToLogin: "Sign in",
    passwordMismatch: "The passwords do not match.",
    registrationSuccess: "Check your inbox. If the address can be registered, you will receive a verification link shortly.",
    registrationError: "Unable to complete registration. Please check the data and try again.",
    verifyEmailHeading: "Verify your email",
    verifyEmailIntro: "Complete verification to activate your LEVERAGE account.",
    verificationChecking: "Verifying your email address...",
    verificationSuccess: "Email verified. You can now sign in.",
    verificationError: "This verification link is invalid or has expired.",
    mfaRequired: "Enter your MFA code to complete sign in.",
    mfaSetupRequired: "Admin MFA setup is required before this account can sign in here.",
    demoLoginNote: "Temporary frontend development shortcuts.",
    demoUser: "DEMO USER",
    demoAdmin: "DEMO ADMIN",
    demoSuperAdmin: "DEMO SUPER ADMIN",
    accountHeading: "Personal Area",
    accountIntro: "Your private area for favorite athletes, favorite events and personal shortcuts.",
    accountContentNavigation: "Choose your saved content",
    favoriteAthletes: "Favorite athletes",
    favoriteEvents: "Favorite events",
    myFavoriteAthletes: "My favorite athletes",
    myFavoriteEvents: "My favorite events",
    favoritesFilter: "Favorites",
    levelFilter: "Level",
    athleteSortName: "Name",
    athleteSortCountry: "Country",
    addFavoriteAthlete: "Save athlete",
    removeFavoriteAthlete: "Remove athlete",
    addFavoriteEvent: "Save event",
    removeFavoriteEvent: "Remove event",
    loginRequiredFavorites: "Sign in to save favorites.",
    noFavoriteAthletes: "No favorite athletes yet.",
    noFavoriteEvents: "No favorite events yet.",
    latestResult: "Latest result",
    savedOn: "Saved on",
    savedRankingViews: "Saved Rankings",
    savedRankingsShortcut: "Saved",
    noSavedRankingViews: "No saved Ranking configurations yet.",
    saveRankingView: "Save this Ranking",
    rankingViewName: "Ranking name",
    rankingViewNamePlaceholder: "Example: MAG FX 2025 cycle",
    rankingViewSaved: "Ranking configuration saved.",
    rankingViewError: "Unable to save this Ranking configuration.",
    openSavedRanking: "Open saved Ranking",
    deleteSavedRanking: "Delete saved Ranking",
    clearRankingFilters: "Clear filters",
    clearSearch: "Clear search",
    filters: "Filters",
    activeFilterSingular: "active filter",
    activeFilterPlural: "active filters",
    backToFilters: "Back to filters",
    loadMoreAthletes: "Load more Athletes",
    loadMoreEvents: "Load more Events",
    loadMoreScores: "Load more Scores",
    language: "Language",
    save: "Save",
    footerTagline: "Artistic Gymnastics Analytics",
    heroEyebrow: "Elite gymnastics, structured.",
    heroTitle: "LEVERAGE",
    heroSubtitle: "Artistic Gymnastics Analytics",
    heroBody: "Search athletes, events and results in a structured gymnastics database designed for analysis, comparison and context.",
    searchPlaceholder: "Search athletes, events and results...",
    athleteSearchPlaceholder: "Search athletes by name, Leverage ID or country...",
    search: "Search",
    globalSearchHeading: "Global search",
    globalSearchIntro: "Search athletes, events and results in a structured gymnastics database designed for analysis, comparison and context.",
    matchingAthletes: "Athletes",
    matchingEvents: "Events",
    matchingResults: "Results",
    filteredResults: "Filtered results",
    relatedResults: "Related results",
    noGlobalSearchResults: "No global results found.",
    noStructuredSearchResults: "No results match all the search filters together. Related matches are shown below.",
    dataLoadError: "Unable to load live data. Please try again in a moment.",
    exploreTitle: "Start with the data",
    exploreSubtitle: "Four clear paths into the platform.",
    athletesTitle: "Explore Athletes",
    athletesText: "Find gymnasts by name, country or discipline.",
    eventsTitle: "Browse Events",
    eventsText: "Use the calendar to move through seasons and competitions.",
    rankingsTitle: "Create Rankings",
    rankingsText: "Sort results by final score, D score or available metrics.",
    compareTitle: "Compare Performance",
    compareText: "Prepare athlete comparisons and long-term trends.",
    open: "Open",
    recentEvents: "Calendar",
    calendarMonth: "Calendar month",
    currentMonth: "Current month",
    previousMonth: "Previous month",
    nextMonth: "Next month",
    favoriteEventNavigation: "Favorite event navigation",
    previousFavoriteEvent: "Previous favorite event",
    nextFavoriteEvent: "Next favorite event",
    eventNavigation: "Event navigation",
    previousEvent: "Previous event",
    nextEvent: "Next event",
    today: "Today",
    resultsAvailable: "Results available",
    resultsMissing: "Results missing",
    ongoing: "Ongoing",
    upcoming: "Upcoming",
    completedWithResults: "With results",
    completedNoResults: "Missing results",
    calendarOnly: "Calendar only",
    rankingPreview: "Ranking",
    viewAll: "View all",
    athletesHeading: "Athletes",
    athletesIntro: "Search gymnasts by name, country, discipline or category. Open profiles, review results and manage favorites when signed in.",
    eventsHeading: "Events",
    eventsIntro: "Find competitions in list or calendar view, filter by level, period, discipline and category, then open event records.",
    eventSearchPlaceholder: "Search events by competition, year or place...",
    eventViewList: "List",
    eventViewCalendar: "Calendar",
    eventProfile: "Event profile",
    eventDetails: "Information",
    eventResultsHeading: "Event classifications",
    eventResultsIntro: "Official classifications loaded for this event. Choose one to view the results ordered by Final Score.",
    eventClassification: "Classification",
    eventAvailableClassifications: "Loaded classifications",
    classificationSection: "Section",
    eventNoResults: "No classifications are available for this event yet.",
    eventResultWarnings: "Result warnings",
    eventUpdateSaved: "Event updated.",
    eventUpdateError: "Unable to update event.",
    adminEventTools: "Admin tools",
    adminToolsButton: "Open admin tools",
    editEvent: "Edit event",
    findEvent: "Automatic search",
    useEvent: "Import data",
    figEventIdOrUrl: "FIG event ID or event URL",
    officialRank: "Official rank",
    format: "Format",
    round: "Round",
    day: "Day",
    location: "Location",
    venue: "Venue",
    rankingsHeading: "Rankings",
    rankingsIntro: "Build score Rankings from the results database. Filter by apparatus, level, period and Olympic cycle, then sort by Final Score or score components.",
    analyticsHeading: "Analytics",
    analyticsIntro: "Compare two athletes through synchronized apparatus profiles and performance trends. Search and add an athlete to start the analysis.",
    analyticsCompareAthleteA: "First athlete",
    analyticsCompareAthleteB: "Second athlete",
    analyticsCompareSearchFull: "Remove an athlete to add another one.",
    analyticsCompareSameDiscipline: "Choose an athlete from the same discipline.",
    analyticsCompareSameAthlete: "Choose two different athletes.",
    analyticsCompareSideBySide: "Side by side",
    analyticsCompareOverlay: "Overlay",
    analyticsCompareRemove: "Remove athlete",
    analyticsCompareNoSuggestions: "No compatible athletes found.",
    analyticsCompareFavoriteEmpty: "No compatible favorite athletes available.",
    analyticsCompareFavoriteError: "Unable to load favorite athletes.",
    loginHeading: "Sign in",
    loginIntro: "User and admin areas will use the authentication system already implemented in the backend.",
    noResults: "No results found.",
    loading: "Loading...",
    discipline: "Discipline",
    category: "Category",
    apparatus: "Apparatus",
    all: "All",
    senior: "Senior",
    junior: "Junior",
    results: "results",
    result: "result",
    score: "Score",
    rankingMetric: "Ranking metric",
    estimatedEScoreRankingNotice: "E Score is estimated from Final Score and D Score. It may include unavailable Penalty or Bonus data.",
    penaltyDataUnavailable: "Penalty data are not available for the current filters. Try Final Score, D Score or E Score, or change the filters.",
    bonusDataUnavailable: "Bonus data are not available for the current filters. Try Final Score, D Score or E Score, or change the filters.",
    vaultAverageComponentDataUnavailable: "VT AVG component data are not available for the selected metric. Try Final Score or change apparatus.",
    scoringCycle: "Olympic cycle",
    allCycles: "All cycles",
    timeInterval: "Period",
    fromDate: "From date",
    toDate: "To date",
    datePlaceholder: "dd/mm/yyyy",
    dateYear: "Year",
    dateMonth: "Month",
    dateDay: "Day",
    eventYear: "Event year",
    country: "Country",
    date: "Date",
    status: "Status",
    event: "Event",
    athlete: "Athlete",
    athleteProfile: "Athlete profile",
    athleteIdentity: "Identity",
    officialData: "Official data",
    firstName: "First name",
    lastName: "Last name",
    birthYear: "Birth year",
    leverageId: "Leverage ID",
    athleteId: "Leverage ID",
    image: "Image",
    imageUrl: "Image URL",
    worldGymnasticsProfile: "World Gymnastics profile",
    worldGymnasticsData: "World Gymnastics",
    worldGymnasticsEvent: "World Gymnastics event",
    worldGymnasticsId: "World Gymnastics ID",
    worldGymnasticsStatus: "World Gymnastics status",
    worldGymnasticsVerified: "World Gymnastics verified",
    verifiedByAdminId: "Verified by admin ID",
    openWorldGymnastics: "Open World Gymnastics",
    notLinked: "Not linked",
    notAvailable: "Not available",
    countryHistory: "Country history",
    noCountryHistory: "No country changes recorded.",
    adminAthleteTools: "Admin tools",
    editAthlete: "Edit athlete",
    saveChanges: "Save changes",
    updateSaved: "Athlete updated.",
    updateError: "Unable to update athlete.",
    verifiedAthleteBadge: "Verified athlete",
    assignVerificationBadge: "Assign verification badge",
    removeVerificationBadge: "Remove verification badge",
    verificationBadgeAssigned: "Verification badge assigned.",
    verificationBadgeRemoved: "Verification badge removed.",
    verificationBadgeError: "Unable to update the verification badge.",
    countryChangeYear: "Country change year",
    adminSuggestions: "Data awaiting approval",
    adminSuggestionSingular: "item awaiting approval",
    adminSuggestionPlural: "items awaiting approval",
    noPendingSuggestions: "No data awaiting approval.",
    suggestedValue: "Suggested value",
    evidence: "Evidence",
    accept: "Accept",
    reject: "Reject",
    suggestionAccepted: "Suggestion accepted.",
    suggestionRejected: "Suggestion rejected.",
    suggestionError: "Unable to review suggestion.",
    worldGymnasticsAssistant: "World Gymnastics assistant",
    findProfile: "Automatic search",
    figIdOrUrl: "FIG ID or profile URL",
    generateFromProfile: "Manual search",
    useProfile: "Import data",
    noWorldGymnasticsCandidates: "No World Gymnastics candidates found.",
    profileSearchError: "Unable to search World Gymnastics.",
    profileSuggestionsCreated: "World Gymnastics data imported for review.",
    wgWarningTypeNoCandidates: "No candidates",
    wgWarningTypeNameMismatch: "Name check",
    wgWarningTypeCountryMismatch: "Country check",
    wgWarningTypeDisciplineMismatch: "Discipline check",
    wgWarningTypeEventMismatch: "Event check",
    wgWarningNoAthleteCandidates: "No World Gymnastics athlete profile candidates were found.",
    wgWarningNoEventCandidates: "No World Gymnastics event candidates were found.",
    wgWarningNameMismatch: "LEVERAGE athlete name differs from the selected World Gymnastics profile.",
    wgWarningCountryMismatch: "LEVERAGE athlete country differs from the selected World Gymnastics profile.",
    wgWarningDisciplineMismatch: "LEVERAGE discipline is not listed on the selected World Gymnastics profile.",
    athleteAnalyticsHeading: "Performance analytics",
    athleteAnalyticsIntro: "Interactive apparatus profile, score trends and summary statistics built from this athlete's results.",
    analyticsMetric: "Metric",
    analyticsMode: "Time view",
    analyticsModePeriod: "Period",
    analyticsModeSnapshot: "Snapshot",
    analyticsTimeline: "Timeline",
    analyticsUpTo: "Up to",
    analyticsAt: "At",
    analyticsAverage: "Average",
    analyticsBest: "Best",
    analyticsLatest: "Latest",
    analyticsEvents: "Events",
    analyticsTotalResults: "Total results",
    analyticsNoData: "No analytics data available for this metric.",
    analyticsMetricUnavailable: "This metric is not available for this athlete in the selected data.",
    analyticsEEstimateNotice: "E Score may be estimated from Final Score and D Score and can include unavailable Penalty or Bonus data.",
    analyticsEventPeriod: "Event period",
    analyticsMultipleEventPeriods: "Multiple event periods",
    analyticsEventPeriodNotice: "Some results come from multi-day events. When Gymternet does not provide the exact session date, Leverage shows the event period from the calendar and anchors the point to the event start only for chronological positioning.",
    analyticsDateSource: "Date source",
    analyticsDateSourceDefaultSummary: "Statistics use the event dates or event periods available in Leverage. Multi-day events without an exact session date are shown as event periods, not as results from the first day.",
    analyticsDateSourcePeriodSummary: "These statistics include results associated with the event period, not with a single event-start day.",
    analyticsRoundFormats: "Rounds / formats",
    analyticsMoreEventSingular: "more event",
    analyticsMoreEvents: "more events",
    analyticsShapeTitle: "Apparatus profile",
    analyticsTrendTitle: "Trend performance",
    analyticsYearTitle: "Year averages",
    analyticsPointCount: "points",
    analyticsPointSingular: "point",
    analyticsPointPlural: "points",
    analyticsResultCount: "results",
    analyticsResultSingular: "result",
    analyticsResultPlural: "results",
    analyticsNoApparatusData: "No apparatus data",
    analyticsScoringCycles: "Olympic cycles",
    analyticsScoringCycleSingular: "Olympic cycle",
    analyticsScoringCyclePlural: "Olympic cycles",
    analyticsMultipleScoringCyclesNotice: "This selection includes multiple gymnastics scoring cycles. Scores may reflect different Codes of Points.",
    warningVaultAttemptOrder: "Vault attempt order may be uncertain: Vault 1 can refer to Vault 2 and vice versa.",
    warningExecutionEstimate: "Estimated execution from D Score and Final Score.",
    warningExecutionEstimatePenalty: "Estimated execution from D Score and Final Score, including possible unavailable Penalty data.",
    warningExecutionEstimateBonus: "Estimated execution from D Score and Final Score, including a possible unrecorded Bonus.",
    warningExecutionEstimatePenaltyBonus: "Estimated execution from D Score and Final Score, including possible unavailable Penalty data and a possible unrecorded Bonus.",
    rankingWarningMixedDisciplines: "This Ranking intentionally mixes MAG and WAG results. Apparatus rules and score scales may not be directly comparable.",
    rankingWarningMixedDisciplineMode: "Mixed-discipline mode was enabled. Results remain comparable only when the selected context is semantically coherent.",
    rankingWarningMultipleScoringCycles: "This Ranking includes multiple gymnastics scoring cycles ({cycles}). Scores may reflect different Codes of Points.",
    notApplicable: "Not applicable",
    apparatusScoresUnavailable: "Apparatus scores not available",
    backToAthletes: "Back to Athletes",
    backToRanking: "Back to Ranking",
    backToClassification: "Back to Standings",
    backToEvents: "Back to Events",
    backToHome: "Back to Home",
    comingSoon: "Coming soon",
  },
  it: {
    navHome: "Home",
    navAthletes: "Atleti",
    navEvents: "Eventi",
    navRankings: "Rankings",
    navAnalytics: "Analytics",
    athletesMenuSearch: "Cerca atleti",
    athletesMenuSearchText: "Trova ginnasti per nome, nazione o disciplina.",
    athletesMenuProfiles: "Schede atleta",
    athletesMenuProfilesText: "Apri schede pulite con dati ufficiali.",
    athletesMenuCompare: "Confronta atleti",
    athletesMenuCompareText: "Prepara trend e analisi affiancate.",
    eventsMenuCalendar: "Calendario",
    eventsMenuCalendarText: "Sfoglia gare passate e future.",
    eventsMenuResults: "Risultati evento",
    eventsMenuResultsText: "Filtra classifiche per disciplina, categoria e round.",
    eventsMenuRankings: "Classifiche gara",
    eventsMenuRankingsText: "Passa da un evento alle sue tabelle punteggio.",
    rankingsMenuScores: "Score rankings",
    rankingsMenuScoresText: "Ordina per final score e componenti disponibili.",
    rankingsMenuFilters: "Filtri smart",
    rankingsMenuFiltersText: "Usa solo valori realmente presenti nei dati.",
    rankingsMenuQuality: "Qualità dati",
    rankingsMenuQualityText: "Riconosci valori stimati o non disponibili.",
    analyticsMenuTrends: "Trend performance",
    analyticsMenuTrendsText: "Segui i punteggi in periodi selezionati.",
    analyticsMenuAge: "Età e nazione",
    analyticsMenuAgeText: "Studia distribuzioni età per nazione ed evento.",
    analyticsMenuApparatus: "Profili attrezzo",
    analyticsMenuApparatusText: "Prepara diagrammi MAG e WAG per attrezzo.",
    signIn: "Accedi",
    account: "Area personale",
    signOut: "Esci",
    email: "Email",
    password: "Password",
    mfaCode: "Codice MFA",
    loginAction: "Accedi",
    loginHelp: "Accedi alla tua area privata per salvare atleti ed eventi.",
    loginError: "Accesso non riuscito. Controlla credenziali e verifica email.",
    registerPrompt: "Non sei ancora registrato?",
    registerLink: "Crea un account",
    registerHeading: "Crea il tuo account",
    registerIntro: "Iscriviti a LEVERAGE per salvare atleti, eventi e le tue configurazioni personali di Ranking.",
    registerHelp: "Usa un indirizzo email valido e scegli una password di almeno 12 caratteri.",
    confirmPassword: "Conferma password",
    registerAction: "Crea account",
    alreadyRegistered: "Sei già registrato?",
    backToLogin: "Accedi",
    passwordMismatch: "Le password non coincidono.",
    registrationSuccess: "Controlla la posta. Se l'indirizzo può essere registrato, riceverai a breve un link di verifica.",
    registrationError: "Impossibile completare la registrazione. Controlla i dati e riprova.",
    verifyEmailHeading: "Verifica la tua email",
    verifyEmailIntro: "Completa la verifica per attivare il tuo account LEVERAGE.",
    verificationChecking: "Verifica dell'indirizzo email in corso...",
    verificationSuccess: "Email verificata. Ora puoi accedere.",
    verificationError: "Il link di verifica non è valido oppure è scaduto.",
    mfaRequired: "Inserisci il codice MFA per completare l'accesso.",
    mfaSetupRequired: "Prima di accedere qui, questo account admin deve completare la configurazione MFA.",
    demoLoginNote: "Scorciatoie temporanee per lo sviluppo frontend.",
    demoUser: "DEMO USER",
    demoAdmin: "DEMO ADMIN",
    demoSuperAdmin: "DEMO SUPER ADMIN",
    accountHeading: "Area personale",
    accountIntro: "La tua area privata per atleti preferiti, eventi preferiti e scorciatoie personali.",
    accountContentNavigation: "Scegli i contenuti salvati",
    favoriteAthletes: "Atleti preferiti",
    favoriteEvents: "Eventi preferiti",
    myFavoriteAthletes: "I miei atleti preferiti",
    myFavoriteEvents: "I miei eventi preferiti",
    favoritesFilter: "Preferiti",
    levelFilter: "Level",
    athleteSortName: "Nome",
    athleteSortCountry: "Nazione",
    addFavoriteAthlete: "Salva atleta",
    removeFavoriteAthlete: "Rimuovi atleta",
    addFavoriteEvent: "Salva evento",
    removeFavoriteEvent: "Rimuovi evento",
    loginRequiredFavorites: "Accedi per salvare preferiti.",
    noFavoriteAthletes: "Nessun atleta preferito.",
    noFavoriteEvents: "Nessun evento preferito.",
    latestResult: "Ultimo risultato",
    savedOn: "Salvato il",
    savedRankingViews: "Rankings salvati",
    savedRankingsShortcut: "Salvati",
    noSavedRankingViews: "Nessuna configurazione Ranking salvata.",
    saveRankingView: "Salva questo Ranking",
    rankingViewName: "Nome Ranking",
    rankingViewNamePlaceholder: "Esempio: MAG FX ciclo 2025",
    rankingViewSaved: "Configurazione Ranking salvata.",
    rankingViewError: "Impossibile salvare questa configurazione Ranking.",
    openSavedRanking: "Apri Ranking salvato",
    deleteSavedRanking: "Elimina Ranking salvato",
    clearRankingFilters: "Pulisci filtri",
    clearSearch: "Cancella ricerca",
    filters: "Filtri",
    activeFilterSingular: "filtro attivo",
    activeFilterPlural: "filtri attivi",
    backToFilters: "Torna ai filtri",
    loadMoreAthletes: "Carica altri Atleti",
    loadMoreEvents: "Carica altri Eventi",
    loadMoreScores: "Carica altri Scores",
    language: "Lingua",
    save: "Salva",
    footerTagline: "Artistic Gymnastics Analytics",
    heroEyebrow: "Ginnastica elite, strutturata.",
    heroTitle: "LEVERAGE",
    heroSubtitle: "Artistic Gymnastics Analytics",
    heroBody: "Cerca atleti, eventi e risultati in un database di ginnastica strutturato per analisi, confronto e contesto.",
    searchPlaceholder: "Cerca atleti, eventi e risultati...",
    athleteSearchPlaceholder: "Cerca atleti per nome, Leverage ID o nazione...",
    search: "Cerca",
    globalSearchHeading: "Ricerca globale",
    globalSearchIntro: "Cerca atleti, eventi e risultati in un database di ginnastica strutturato per analisi, confronto e contesto.",
    matchingAthletes: "Atleti",
    matchingEvents: "Eventi",
    matchingResults: "Risultati",
    filteredResults: "Risultati filtrati",
    relatedResults: "Risultati collegati",
    noGlobalSearchResults: "Nessun risultato globale trovato.",
    noStructuredSearchResults: "Nessun risultato corrisponde a tutti i filtri della ricerca. Sotto trovi i match collegati.",
    dataLoadError: "Impossibile caricare i dati live. Riprova tra poco.",
    exploreTitle: "Parti dai dati",
    exploreSubtitle: "Quattro percorsi chiari nella piattaforma.",
    athletesTitle: "Esplora Atleti",
    athletesText: "Trova ginnasti per nome, nazione o disciplina.",
    eventsTitle: "Sfoglia Eventi",
    eventsText: "Usa il calendario per navigare stagioni e competizioni.",
    rankingsTitle: "Crea Rankings",
    rankingsText: "Ordina i risultati per score, D score o metriche disponibili.",
    compareTitle: "Confronta Performance",
    compareText: "Prepara confronti atleta e trend nel tempo.",
    open: "Apri",
    recentEvents: "Calendario",
    calendarMonth: "Mese calendario",
    currentMonth: "Mese corrente",
    previousMonth: "Mese precedente",
    nextMonth: "Mese successivo",
    favoriteEventNavigation: "Navigazione eventi preferiti",
    previousFavoriteEvent: "Evento preferito precedente",
    nextFavoriteEvent: "Evento preferito successivo",
    eventNavigation: "Navigazione eventi",
    previousEvent: "Evento precedente",
    nextEvent: "Evento successivo",
    today: "Oggi",
    resultsAvailable: "Risultati disponibili",
    resultsMissing: "Risultati mancanti",
    ongoing: "In corso",
    upcoming: "In programma",
    completedWithResults: "Con risultati",
    completedNoResults: "Risultati mancanti",
    calendarOnly: "Solo calendario",
    rankingPreview: "Ranking",
    viewAll: "Vedi tutto",
    athletesHeading: "Atleti",
    athletesIntro: "Cerca ginnasti per nome, nazione, disciplina o categoria. Apri la scheda atleta, consulta i risultati e gestisci i preferiti quando sei loggato.",
    eventsHeading: "Eventi",
    eventsIntro: "Trova gare in lista o calendario, filtra per level, periodo, disciplina e categoria, poi apri la scheda evento.",
    eventSearchPlaceholder: "Cerca eventi per competizione, anno o luogo...",
    eventViewList: "Lista",
    eventViewCalendar: "Calendario",
    eventProfile: "Scheda evento",
    eventDetails: "Informazioni",
    eventResultsHeading: "Classifiche evento",
    eventResultsIntro: "Classifiche ufficiali caricate per questo evento. Scegline una per visualizzare i risultati ordinati per Final Score.",
    eventClassification: "Classifica",
    eventAvailableClassifications: "Classifiche caricate",
    classificationSection: "Sezione",
    eventNoResults: "Non sono ancora disponibili classifiche per questo evento.",
    eventResultWarnings: "Avvisi risultati",
    eventUpdateSaved: "Evento aggiornato.",
    eventUpdateError: "Impossibile aggiornare l'evento.",
    adminEventTools: "Strumenti admin",
    adminToolsButton: "Apri strumenti admin",
    editEvent: "Modifica evento",
    findEvent: "Ricerca automatica",
    useEvent: "Importa dati",
    figEventIdOrUrl: "FIG event ID o URL evento",
    officialRank: "Rank ufficiale",
    format: "Format",
    round: "Round",
    day: "Giorno",
    location: "Luogo",
    venue: "Sede",
    rankingsHeading: "Rankings",
    rankingsIntro: "Costruisci Rankings dai risultati: filtra per attrezzo, level, periodo e ciclo olimpico, poi ordina per Final Score o componenti del punteggio.",
    analyticsHeading: "Analytics",
    analyticsIntro: "Confronta due atleti attraverso profili attrezzo e Trend performance sincronizzati. Cerca e aggiungi un atleta per iniziare l'analisi.",
    analyticsCompareAthleteA: "Primo atleta",
    analyticsCompareAthleteB: "Secondo atleta",
    analyticsCompareSearchFull: "Rimuovi un atleta per aggiungerne un altro.",
    analyticsCompareSameDiscipline: "Scegli un atleta della stessa disciplina.",
    analyticsCompareSameAthlete: "Scegli due atleti differenti.",
    analyticsCompareSideBySide: "Affiancati",
    analyticsCompareOverlay: "Sovrapposti",
    analyticsCompareRemove: "Rimuovi atleta",
    analyticsCompareNoSuggestions: "Nessun atleta compatibile trovato.",
    analyticsCompareFavoriteEmpty: "Nessun atleta preferito compatibile disponibile.",
    analyticsCompareFavoriteError: "Impossibile caricare gli atleti preferiti.",
    loginHeading: "Accedi",
    loginIntro: "Le aree utente e admin useranno il sistema di autenticazione già implementato.",
    noResults: "Nessun risultato trovato.",
    loading: "Caricamento...",
    discipline: "Disciplina",
    category: "Categoria",
    apparatus: "Attrezzo",
    all: "Tutto",
    senior: "Senior",
    junior: "Junior",
    results: "risultati",
    result: "risultato",
    score: "Score",
    rankingMetric: "Metrica Ranking",
    estimatedEScoreRankingNotice: "E Score è stimato da Final Score e D Score. Può includere dati Penalty o Bonus non disponibili.",
    penaltyDataUnavailable: "I dati Penalty non sono disponibili per i filtri selezionati. Usa Final Score, D Score o E Score, oppure modifica i filtri.",
    bonusDataUnavailable: "I dati Bonus non sono disponibili per i filtri selezionati. Usa Final Score, D Score o E Score, oppure modifica i filtri.",
    vaultAverageComponentDataUnavailable: "I dati componenti di VT AVG non sono disponibili per la metrica selezionata. Usa Final Score oppure modifica attrezzo.",
    scoringCycle: "Ciclo olimpico",
    allCycles: "Tutti i cicli",
    timeInterval: "Periodo",
    fromDate: "Da data",
    toDate: "A data",
    datePlaceholder: "gg/mm/aaaa",
    dateYear: "Anno",
    dateMonth: "Mese",
    dateDay: "Giorno",
    eventYear: "Anno gara",
    country: "Nazione",
    date: "Data",
    status: "Stato",
    event: "Evento",
    athlete: "Atleta",
    athleteProfile: "Scheda atleta",
    athleteIdentity: "Identità",
    officialData: "Dati ufficiali",
    firstName: "Nome",
    lastName: "Cognome",
    birthYear: "Anno di nascita",
    leverageId: "Leverage ID",
    athleteId: "Leverage ID",
    image: "Immagine",
    imageUrl: "URL immagine",
    worldGymnasticsProfile: "Profilo World Gymnastics",
    worldGymnasticsData: "World Gymnastics",
    worldGymnasticsEvent: "Evento World Gymnastics",
    worldGymnasticsId: "ID World Gymnastics",
    worldGymnasticsStatus: "Status World Gymnastics",
    worldGymnasticsVerified: "World Gymnastics verificato",
    verifiedByAdminId: "Verificato da admin ID",
    openWorldGymnastics: "Apri World Gymnastics",
    notLinked: "Non collegato",
    notAvailable: "Non disponibile",
    countryHistory: "Storico nazionalità",
    noCountryHistory: "Nessun cambio nazionalità registrato.",
    adminAthleteTools: "Strumenti admin",
    editAthlete: "Modifica atleta",
    saveChanges: "Salva modifiche",
    updateSaved: "Atleta aggiornato.",
    updateError: "Impossibile aggiornare l'atleta.",
    verifiedAthleteBadge: "Atleta verificato",
    assignVerificationBadge: "Assegna badge di verifica",
    removeVerificationBadge: "Rimuovi badge di verifica",
    verificationBadgeAssigned: "Badge di verifica assegnato.",
    verificationBadgeRemoved: "Badge di verifica rimosso.",
    verificationBadgeError: "Impossibile aggiornare il badge di verifica.",
    countryChangeYear: "Anno cambio nazionalità",
    adminSuggestions: "Dati in attesa di approvazione",
    adminSuggestionSingular: "dato in attesa di approvazione",
    adminSuggestionPlural: "dati in attesa di approvazione",
    noPendingSuggestions: "Nessun dato in attesa di approvazione.",
    suggestedValue: "Valore suggerito",
    evidence: "Evidenza",
    accept: "Accetta",
    reject: "Rifiuta",
    suggestionAccepted: "Suggerimento accettato.",
    suggestionRejected: "Suggerimento rifiutato.",
    suggestionError: "Impossibile revisionare il suggerimento.",
    worldGymnasticsAssistant: "Assistente World Gymnastics",
    findProfile: "Ricerca automatica",
    figIdOrUrl: "FIG ID o URL profilo",
    generateFromProfile: "Ricerca manuale",
    useProfile: "Importa dati",
    noWorldGymnasticsCandidates: "Nessun candidato World Gymnastics trovato.",
    profileSearchError: "Impossibile cercare su World Gymnastics.",
    profileSuggestionsCreated: "Dati World Gymnastics importati per la revisione.",
    wgWarningTypeNoCandidates: "Nessun candidato",
    wgWarningTypeNameMismatch: "Controllo nome",
    wgWarningTypeCountryMismatch: "Controllo nazione",
    wgWarningTypeDisciplineMismatch: "Controllo disciplina",
    wgWarningTypeEventMismatch: "Controllo evento",
    wgWarningNoAthleteCandidates: "Nessun candidato profilo atleta World Gymnastics trovato.",
    wgWarningNoEventCandidates: "Nessun candidato evento World Gymnastics trovato.",
    wgWarningNameMismatch: "Il nome atleta in LEVERAGE è diverso dal profilo World Gymnastics selezionato.",
    wgWarningCountryMismatch: "La nazione atleta in LEVERAGE è diversa dal profilo World Gymnastics selezionato.",
    wgWarningDisciplineMismatch: "La disciplina LEVERAGE non è presente nel profilo World Gymnastics selezionato.",
    athleteAnalyticsHeading: "Analytics performance",
    athleteAnalyticsIntro: "Profilo attrezzi interattivo, trend dei punteggi e statistiche riepilogative costruite sui risultati dell'atleta.",
    analyticsMetric: "Metrica",
    analyticsMode: "Vista temporale",
    analyticsModePeriod: "Periodo",
    analyticsModeSnapshot: "Istante",
    analyticsTimeline: "Timeline",
    analyticsUpTo: "Fino a",
    analyticsAt: "Al",
    analyticsAverage: "Media",
    analyticsBest: "Migliore",
    analyticsLatest: "Ultimo",
    analyticsEvents: "Eventi",
    analyticsTotalResults: "Risultati totali",
    analyticsNoData: "Nessun dato analytics disponibile per questa metrica.",
    analyticsMetricUnavailable: "Questa metrica non è disponibile per questo atleta nei dati selezionati.",
    analyticsEEstimateNotice: "E Score può essere stimato da Final Score e D Score e può includere dati Penalty o Bonus non disponibili.",
    analyticsEventPeriod: "Periodo evento",
    analyticsMultipleEventPeriods: "Più periodi evento",
    analyticsEventPeriodNotice: "Alcuni risultati provengono da eventi su più giorni. Quando Gymternet non fornisce la data esatta della sessione, Leverage mostra il periodo evento del calendario e usa l'inizio evento solo come riferimento cronologico.",
    analyticsDateSource: "Fonte temporale",
    analyticsDateSourceDefaultSummary: "Le statistiche usano le date o i periodi evento disponibili in Leverage. Gli eventi multigiorno senza data esatta della sessione vengono mostrati come periodi evento, non come risultati del primo giorno.",
    analyticsDateSourcePeriodSummary: "Queste statistiche includono risultati associati al periodo dell'evento, non a un singolo giorno di inizio gara.",
    analyticsRoundFormats: "Round / format",
    analyticsMoreEventSingular: "altro evento",
    analyticsMoreEvents: "altri eventi",
    analyticsShapeTitle: "Profilo attrezzi",
    analyticsTrendTitle: "Trend performance",
    analyticsYearTitle: "Medie per anno",
    analyticsPointCount: "punti",
    analyticsPointSingular: "punto",
    analyticsPointPlural: "punti",
    analyticsResultCount: "risultati",
    analyticsResultSingular: "risultato",
    analyticsResultPlural: "risultati",
    analyticsNoApparatusData: "Nessun dato attrezzo",
    analyticsScoringCycles: "Cicli olimpici",
    analyticsScoringCycleSingular: "Ciclo olimpico",
    analyticsScoringCyclePlural: "Cicli olimpici",
    analyticsMultipleScoringCyclesNotice: "Questa selezione include più cicli olimpici. I punteggi possono riflettere Codici dei Punteggi diversi.",
    warningVaultAttemptOrder: "Ordine dei salti al volteggio potenzialmente incerto: Vault 1 può riferirsi a Vault 2 e viceversa.",
    warningExecutionEstimate: "Esecuzione stimata da D Score e Final Score.",
    warningExecutionEstimatePenalty: "Esecuzione stimata da D Score e Final Score, con possibili dati Penalty non disponibili.",
    warningExecutionEstimateBonus: "Esecuzione stimata da D Score e Final Score, con un possibile Bonus non registrato.",
    warningExecutionEstimatePenaltyBonus: "Esecuzione stimata da D Score e Final Score, con possibili dati Penalty non disponibili e un possibile Bonus non registrato.",
    rankingWarningMixedDisciplines: "Questo Ranking combina intenzionalmente risultati MAG e WAG. Le regole degli attrezzi e le scale dei punteggi potrebbero non essere direttamente confrontabili.",
    rankingWarningMixedDisciplineMode: "La modalità multi-disciplina è attiva. I risultati restano confrontabili solo quando il contesto selezionato è semanticamente coerente.",
    rankingWarningMultipleScoringCycles: "Questo Ranking include più cicli olimpici ({cycles}). I punteggi possono riflettere Codici dei Punteggi diversi.",
    notApplicable: "Non applicabile",
    apparatusScoresUnavailable: "Punteggi attrezzi non disponibili",
    backToAthletes: "Torna agli Atleti",
    backToRanking: "Torna al Ranking",
    backToClassification: "Torna alla Classifica",
    backToEvents: "Torna agli Eventi",
    backToHome: "Torna alla Home",
    comingSoon: "In arrivo",
  },
  es: {
    navHome: "Home",
    navAthletes: "Atletas",
    navEvents: "Eventos",
    navRankings: "Rankings",
    navAnalytics: "Analitica",
    athletesMenuSearch: "Buscar atletas",
    athletesMenuSearchText: "Encuentra gimnastas por nombre, pais o disciplina.",
    athletesMenuProfiles: "Perfiles de atleta",
    athletesMenuProfilesText: "Abre fichas limpias con datos oficiales.",
    athletesMenuCompare: "Comparar atletas",
    athletesMenuCompareText: "Prepara tendencias y analisis lado a lado.",
    eventsMenuCalendar: "Calendario",
    eventsMenuCalendarText: "Explora competiciones pasadas y futuras.",
    eventsMenuResults: "Resultados de evento",
    eventsMenuResultsText: "Filtra rankings por disciplina, categoria y ronda.",
    eventsMenuRankings: "Rankings de competicion",
    eventsMenuRankingsText: "Pasa de un evento a sus tablas de score.",
    rankingsMenuScores: "Rankings de score",
    rankingsMenuScoresText: "Ordena por final score y componentes disponibles.",
    rankingsMenuFilters: "Filtros inteligentes",
    rankingsMenuFiltersText: "Usa solo valores existentes en los datos.",
    rankingsMenuQuality: "Calidad de datos",
    rankingsMenuQualityText: "Detecta valores estimados o no disponibles.",
    analyticsMenuTrends: "Tendencias",
    analyticsMenuTrendsText: "Sigue scores en periodos seleccionados.",
    analyticsMenuAge: "Edad y pais",
    analyticsMenuAgeText: "Estudia edades por pais y evento.",
    analyticsMenuApparatus: "Perfiles por aparato",
    analyticsMenuApparatusText: "Prepara diagramas MAG y WAG por aparato.",
    signIn: "Entrar",
    account: "Área personal",
    signOut: "Salir",
    email: "Email",
    password: "Password",
    mfaCode: "Codigo MFA",
    loginAction: "Entrar",
    loginHelp: "Accede a tu area privada para guardar atletas y eventos.",
    loginError: "No se pudo iniciar sesion. Revisa credenciales y verificacion email.",
    registerPrompt: "Todavia no tienes una cuenta?",
    registerLink: "Crear una cuenta",
    registerHeading: "Crea tu cuenta",
    registerIntro: "Unete a LEVERAGE para guardar atletas, eventos y tus configuraciones personales de Ranking.",
    registerHelp: "Utiliza un email valido y elige una contrasena de al menos 12 caracteres.",
    confirmPassword: "Confirmar contrasena",
    registerAction: "Crear cuenta",
    alreadyRegistered: "Ya tienes una cuenta?",
    backToLogin: "Entrar",
    passwordMismatch: "Las contrasenas no coinciden.",
    registrationSuccess: "Revisa tu correo. Si la direccion puede registrarse, recibiras pronto un enlace de verificacion.",
    registrationError: "No se pudo completar el registro. Revisa los datos e intentalo de nuevo.",
    verifyEmailHeading: "Verifica tu email",
    verifyEmailIntro: "Completa la verificacion para activar tu cuenta LEVERAGE.",
    verificationChecking: "Verificando tu direccion de email...",
    verificationSuccess: "Email verificado. Ya puedes iniciar sesion.",
    verificationError: "El enlace de verificacion no es valido o ha caducado.",
    mfaRequired: "Introduce el codigo MFA para completar el acceso.",
    mfaSetupRequired: "Esta cuenta admin debe configurar MFA antes de acceder aqui.",
    demoLoginNote: "Accesos temporales para desarrollo frontend.",
    demoUser: "DEMO USER",
    demoAdmin: "DEMO ADMIN",
    demoSuperAdmin: "DEMO SUPER ADMIN",
    accountHeading: "Área personal",
    accountIntro: "Tu area privada para atletas favoritos, eventos favoritos y accesos personales.",
    accountContentNavigation: "Elige tus contenidos guardados",
    favoriteAthletes: "Atletas favoritos",
    favoriteEvents: "Eventos favoritos",
    myFavoriteAthletes: "Mis atletas favoritos",
    myFavoriteEvents: "Mis eventos favoritos",
    favoritesFilter: "Favoritos",
    levelFilter: "Level",
    athleteSortName: "Nombre",
    athleteSortCountry: "Pais",
    addFavoriteAthlete: "Guardar atleta",
    removeFavoriteAthlete: "Quitar atleta",
    addFavoriteEvent: "Guardar evento",
    removeFavoriteEvent: "Quitar evento",
    loginRequiredFavorites: "Inicia sesion para guardar favoritos.",
    noFavoriteAthletes: "Aun no hay atletas favoritos.",
    noFavoriteEvents: "Aun no hay eventos favoritos.",
    latestResult: "Ultimo resultado",
    savedOn: "Guardado el",
    savedRankingViews: "Rankings guardados",
    savedRankingsShortcut: "Guardados",
    noSavedRankingViews: "Aun no hay configuraciones Ranking guardadas.",
    saveRankingView: "Guardar este Ranking",
    rankingViewName: "Nombre Ranking",
    rankingViewNamePlaceholder: "Ejemplo: MAG FX ciclo 2025",
    rankingViewSaved: "Configuracion Ranking guardada.",
    rankingViewError: "No se pudo guardar esta configuracion Ranking.",
    openSavedRanking: "Abrir Ranking guardado",
    deleteSavedRanking: "Eliminar Ranking guardado",
    clearRankingFilters: "Limpiar filtros",
    clearSearch: "Borrar busqueda",
    filters: "Filtros",
    activeFilterSingular: "filtro activo",
    activeFilterPlural: "filtros activos",
    backToFilters: "Volver a los filtros",
    loadMoreAthletes: "Cargar mas Atletas",
    loadMoreEvents: "Cargar mas Eventos",
    loadMoreScores: "Cargar mas Scores",
    language: "Idioma",
    save: "Guardar",
    footerTagline: "Artistic Gymnastics Analytics",
    heroEyebrow: "Gimnasia elite, estructurada.",
    heroTitle: "LEVERAGE",
    heroSubtitle: "Artistic Gymnastics Analytics",
    heroBody: "Busca atletas, eventos y resultados en una base de datos de gimnasia estructurada para analisis, comparacion y contexto.",
    searchPlaceholder: "Buscar atletas, eventos y resultados...",
    athleteSearchPlaceholder: "Buscar atletas por nombre, Leverage ID o pais...",
    search: "Buscar",
    globalSearchHeading: "Busqueda global",
    globalSearchIntro: "Busca atletas, eventos y resultados en una base de datos de gimnasia estructurada para analisis, comparacion y contexto.",
    matchingAthletes: "Atletas",
    matchingEvents: "Eventos",
    matchingResults: "Resultados",
    filteredResults: "Resultados filtrados",
    relatedResults: "Resultados relacionados",
    noGlobalSearchResults: "No se encontraron resultados globales.",
    noStructuredSearchResults: "Ningun resultado coincide con todos los filtros de busqueda. Abajo se muestran coincidencias relacionadas.",
    dataLoadError: "No se pueden cargar los datos en vivo. Intentalo de nuevo en un momento.",
    exploreTitle: "Empieza por los datos",
    exploreSubtitle: "Cuatro caminos claros dentro de la plataforma.",
    athletesTitle: "Explorar Atletas",
    athletesText: "Encuentra gimnastas por nombre, pais o disciplina.",
    eventsTitle: "Ver Eventos",
    eventsText: "Usa el calendario para navegar temporadas y competiciones.",
    rankingsTitle: "Crear Rankings",
    rankingsText: "Ordena resultados por score, D score o metricas disponibles.",
    compareTitle: "Comparar Rendimiento",
    compareText: "Prepara comparaciones y tendencias a largo plazo.",
    open: "Abrir",
    recentEvents: "Calendario",
    calendarMonth: "Mes calendario",
    currentMonth: "Mes actual",
    previousMonth: "Mes anterior",
    nextMonth: "Mes siguiente",
    favoriteEventNavigation: "Navegacion de eventos favoritos",
    previousFavoriteEvent: "Evento favorito anterior",
    nextFavoriteEvent: "Evento favorito siguiente",
    eventNavigation: "Navegacion de eventos",
    previousEvent: "Evento anterior",
    nextEvent: "Evento siguiente",
    today: "Hoy",
    resultsAvailable: "Resultados disponibles",
    resultsMissing: "Resultados pendientes",
    ongoing: "En curso",
    upcoming: "Programado",
    completedWithResults: "Con resultados",
    completedNoResults: "Resultados pendientes",
    calendarOnly: "Solo calendario",
    rankingPreview: "Ranking",
    viewAll: "Ver todo",
    athletesHeading: "Atletas",
    athletesIntro: "Busca gimnastas por nombre, pais, disciplina o categoria. Abre perfiles, revisa resultados y gestiona favoritos al iniciar sesion.",
    eventsHeading: "Eventos",
    eventsIntro: "Encuentra competiciones en lista o calendario, filtra por level, periodo, disciplina y categoria, y abre la ficha del evento.",
    eventSearchPlaceholder: "Buscar eventos por competicion, ano o lugar...",
    eventViewList: "Lista",
    eventViewCalendar: "Calendario",
    eventProfile: "Ficha de evento",
    eventDetails: "Informacion",
    eventResultsHeading: "Clasificaciones del evento",
    eventResultsIntro: "Clasificaciones oficiales cargadas para este evento. Elige una para ver los resultados ordenados por Final Score.",
    eventClassification: "Clasificacion",
    eventAvailableClassifications: "Clasificaciones cargadas",
    classificationSection: "Seccion",
    eventNoResults: "Todavia no hay clasificaciones disponibles para este evento.",
    eventResultWarnings: "Avisos de resultados",
    eventUpdateSaved: "Evento actualizado.",
    eventUpdateError: "No se pudo actualizar el evento.",
    adminEventTools: "Herramientas admin",
    adminToolsButton: "Abrir herramientas admin",
    editEvent: "Editar evento",
    findEvent: "Búsqueda automática",
    useEvent: "Importar datos",
    figEventIdOrUrl: "FIG event ID o URL evento",
    officialRank: "Rank oficial",
    format: "Format",
    round: "Ronda",
    day: "Dia",
    location: "Lugar",
    venue: "Sede",
    rankingsHeading: "Rankings",
    rankingsIntro: "Construye Rankings desde los resultados: filtra por aparato, level, periodo y ciclo olimpico, y ordena por Final Score o componentes.",
    analyticsHeading: "Analitica",
    analyticsIntro: "Compara dos atletas mediante perfiles por aparato y tendencias de rendimiento sincronizadas. Busca y anade un atleta para iniciar el analisis.",
    analyticsCompareAthleteA: "Primer atleta",
    analyticsCompareAthleteB: "Segundo atleta",
    analyticsCompareSearchFull: "Elimina un atleta para anadir otro.",
    analyticsCompareSameDiscipline: "Elige un atleta de la misma disciplina.",
    analyticsCompareSameAthlete: "Elige dos atletas diferentes.",
    analyticsCompareSideBySide: "En paralelo",
    analyticsCompareOverlay: "Superpuestos",
    analyticsCompareRemove: "Eliminar atleta",
    analyticsCompareNoSuggestions: "No se encontraron atletas compatibles.",
    analyticsCompareFavoriteEmpty: "No hay atletas favoritos compatibles disponibles.",
    analyticsCompareFavoriteError: "No se pudieron cargar los atletas favoritos.",
    loginHeading: "Entrar",
    loginIntro: "Las areas de usuario y admin usaran el sistema de autenticacion ya implementado.",
    noResults: "No se encontraron resultados.",
    loading: "Cargando...",
    discipline: "Disciplina",
    category: "Categoria",
    apparatus: "Aparato",
    all: "Todo",
    senior: "Senior",
    junior: "Junior",
    results: "resultados",
    result: "resultado",
    score: "Score",
    rankingMetric: "Metrica Ranking",
    estimatedEScoreRankingNotice: "E Score se estima a partir de Final Score y D Score. Puede incluir datos Penalty o Bonus no disponibles.",
    penaltyDataUnavailable: "Los datos Penalty no están disponibles para los filtros seleccionados. Usa Final Score, D Score o E Score, o cambia los filtros.",
    bonusDataUnavailable: "Los datos Bonus no están disponibles para los filtros seleccionados. Usa Final Score, D Score o E Score, o cambia los filtros.",
    vaultAverageComponentDataUnavailable: "Los datos de componentes de VT AVG no están disponibles para la métrica seleccionada. Usa Final Score o cambia el aparato.",
    scoringCycle: "Ciclo olimpico",
    allCycles: "Todos los ciclos",
    timeInterval: "Periodo",
    fromDate: "Desde fecha",
    toDate: "Hasta fecha",
    datePlaceholder: "dd/mm/aaaa",
    dateYear: "Ano",
    dateMonth: "Mes",
    dateDay: "Dia",
    eventYear: "Ano del evento",
    country: "Pais",
    date: "Fecha",
    status: "Estado",
    event: "Evento",
    athlete: "Atleta",
    athleteProfile: "Perfil de atleta",
    athleteIdentity: "Identidad",
    officialData: "Datos oficiales",
    firstName: "Nombre",
    lastName: "Apellido",
    birthYear: "Ano de nacimiento",
    leverageId: "Leverage ID",
    athleteId: "Leverage ID",
    image: "Imagen",
    imageUrl: "URL imagen",
    worldGymnasticsProfile: "Perfil World Gymnastics",
    worldGymnasticsData: "World Gymnastics",
    worldGymnasticsEvent: "Evento World Gymnastics",
    worldGymnasticsId: "ID World Gymnastics",
    worldGymnasticsStatus: "Estado World Gymnastics",
    worldGymnasticsVerified: "World Gymnastics verificado",
    verifiedByAdminId: "Verificado por admin ID",
    openWorldGymnastics: "Abrir World Gymnastics",
    notLinked: "No vinculado",
    notAvailable: "No disponible",
    countryHistory: "Historial de nacionalidad",
    noCountryHistory: "No hay cambios de nacionalidad registrados.",
    adminAthleteTools: "Herramientas admin",
    editAthlete: "Editar atleta",
    saveChanges: "Guardar cambios",
    updateSaved: "Atleta actualizado.",
    updateError: "No se pudo actualizar el atleta.",
    verifiedAthleteBadge: "Atleta verificado",
    assignVerificationBadge: "Asignar insignia de verificación",
    removeVerificationBadge: "Eliminar insignia de verificación",
    verificationBadgeAssigned: "Insignia de verificación asignada.",
    verificationBadgeRemoved: "Insignia de verificación eliminada.",
    verificationBadgeError: "No se pudo actualizar la insignia de verificación.",
    countryChangeYear: "Ano de cambio de nacionalidad",
    adminSuggestions: "Datos pendientes de aprobación",
    adminSuggestionSingular: "dato pendiente de aprobación",
    adminSuggestionPlural: "datos pendientes de aprobación",
    noPendingSuggestions: "No hay datos pendientes de aprobación.",
    suggestedValue: "Valor sugerido",
    evidence: "Evidencia",
    accept: "Aceptar",
    reject: "Rechazar",
    suggestionAccepted: "Sugerencia aceptada.",
    suggestionRejected: "Sugerencia rechazada.",
    suggestionError: "No se pudo revisar la sugerencia.",
    worldGymnasticsAssistant: "Asistente World Gymnastics",
    findProfile: "Búsqueda automática",
    figIdOrUrl: "FIG ID o URL perfil",
    generateFromProfile: "Búsqueda manual",
    useProfile: "Importar datos",
    noWorldGymnasticsCandidates: "No se encontraron candidatos World Gymnastics.",
    profileSearchError: "No se pudo buscar en World Gymnastics.",
    profileSuggestionsCreated: "Datos de World Gymnastics importados para revisión.",
    wgWarningTypeNoCandidates: "Sin candidatos",
    wgWarningTypeNameMismatch: "Control de nombre",
    wgWarningTypeCountryMismatch: "Control de país",
    wgWarningTypeDisciplineMismatch: "Control de disciplina",
    wgWarningTypeEventMismatch: "Control de evento",
    wgWarningNoAthleteCandidates: "No se encontraron candidatos de perfil de atleta World Gymnastics.",
    wgWarningNoEventCandidates: "No se encontraron candidatos de evento World Gymnastics.",
    wgWarningNameMismatch: "El nombre del atleta en LEVERAGE difiere del perfil World Gymnastics seleccionado.",
    wgWarningCountryMismatch: "El país del atleta en LEVERAGE difiere del perfil World Gymnastics seleccionado.",
    wgWarningDisciplineMismatch: "La disciplina LEVERAGE no aparece en el perfil World Gymnastics seleccionado.",
    athleteAnalyticsHeading: "Analitica de rendimiento",
    athleteAnalyticsIntro: "Perfil interactivo por aparato, tendencias de score y estadisticas resumen construidas desde los resultados del atleta.",
    analyticsMetric: "Metrica",
    analyticsMode: "Vista temporal",
    analyticsModePeriod: "Periodo",
    analyticsModeSnapshot: "Instante",
    analyticsTimeline: "Timeline",
    analyticsUpTo: "Hasta",
    analyticsAt: "En",
    analyticsAverage: "Media",
    analyticsBest: "Mejor",
    analyticsLatest: "Ultimo",
    analyticsEvents: "Eventos",
    analyticsTotalResults: "Resultados totales",
    analyticsNoData: "No hay datos de analitica para esta metrica.",
    analyticsMetricUnavailable: "Esta métrica no está disponible para este atleta en los datos seleccionados.",
    analyticsEEstimateNotice: "E Score puede estimarse desde Final Score y D Score y puede incluir datos Penalty o Bonus no disponibles.",
    analyticsEventPeriod: "Periodo del evento",
    analyticsMultipleEventPeriods: "Varios periodos de evento",
    analyticsEventPeriodNotice: "Algunos resultados proceden de eventos de varios días. Cuando Gymternet no proporciona la fecha exacta de la sesión, Leverage muestra el periodo del evento del calendario y usa el inicio del evento solo como referencia cronológica.",
    analyticsDateSource: "Fuente temporal",
    analyticsDateSourceDefaultSummary: "Las estadísticas usan las fechas o periodos de evento disponibles en Leverage. Los eventos de varios días sin fecha exacta de sesión se muestran como periodos de evento, no como resultados del primer día.",
    analyticsDateSourcePeriodSummary: "Estas estadísticas incluyen resultados asociados al periodo del evento, no a un único día de inicio de la competición.",
    analyticsRoundFormats: "Rondas / formatos",
    analyticsMoreEventSingular: "evento más",
    analyticsMoreEvents: "eventos más",
    analyticsShapeTitle: "Perfil por aparato",
    analyticsTrendTitle: "Trend performance",
    analyticsYearTitle: "Medias por ano",
    analyticsPointCount: "puntos",
    analyticsPointSingular: "punto",
    analyticsPointPlural: "puntos",
    analyticsResultCount: "resultados",
    analyticsResultSingular: "resultado",
    analyticsResultPlural: "resultados",
    analyticsNoApparatusData: "Sin datos por aparato",
    analyticsScoringCycles: "Ciclos olímpicos",
    analyticsScoringCycleSingular: "Ciclo olímpico",
    analyticsScoringCyclePlural: "Ciclos olímpicos",
    analyticsMultipleScoringCyclesNotice: "Esta selección incluye varios ciclos olímpicos. Los scores pueden reflejar Códigos de Puntuación diferentes.",
    warningVaultAttemptOrder: "El orden de los saltos puede ser incierto: Vault 1 puede referirse a Vault 2 y viceversa.",
    warningExecutionEstimate: "Ejecución estimada a partir de D Score y Final Score.",
    warningExecutionEstimatePenalty: "Ejecución estimada a partir de D Score y Final Score, con posibles datos Penalty no disponibles.",
    warningExecutionEstimateBonus: "Ejecución estimada a partir de D Score y Final Score, con un posible Bonus no registrado.",
    warningExecutionEstimatePenaltyBonus: "Ejecución estimada a partir de D Score y Final Score, con posibles datos Penalty no disponibles y un posible Bonus no registrado.",
    rankingWarningMixedDisciplines: "Este Ranking combina intencionadamente resultados MAG y WAG. Las reglas de los aparatos y las escalas de score pueden no ser directamente comparables.",
    rankingWarningMixedDisciplineMode: "El modo multi-disciplina está activo. Los resultados siguen siendo comparables solo cuando el contexto seleccionado es semánticamente coherente.",
    rankingWarningMultipleScoringCycles: "Este Ranking incluye varios ciclos olímpicos ({cycles}). Los scores pueden reflejar Códigos de Puntuación diferentes.",
    notApplicable: "No aplicable",
    apparatusScoresUnavailable: "Scores por aparato no disponibles",
    backToAthletes: "Volver a Atletas",
    backToRanking: "Volver al Ranking",
    backToClassification: "Volver a la clasificación",
    backToEvents: "Volver a Eventos",
    backToHome: "Volver a Home",
    comingSoon: "Proximamente",
  },
  fr: {
    navHome: "Accueil",
    navAthletes: "Athletes",
    navEvents: "Evenements",
    navRankings: "Rankings",
    navAnalytics: "Analytique",
    athletesMenuSearch: "Rechercher athletes",
    athletesMenuSearchText: "Trouvez les gymnastes par nom, pays ou discipline.",
    athletesMenuProfiles: "Fiches athlete",
    athletesMenuProfilesText: "Ouvrez des fiches claires avec donnees officielles.",
    athletesMenuCompare: "Comparer athletes",
    athletesMenuCompareText: "Preparez tendances et analyses cote a cote.",
    eventsMenuCalendar: "Calendrier",
    eventsMenuCalendarText: "Parcourez competitions passees et futures.",
    eventsMenuResults: "Resultats evenement",
    eventsMenuResultsText: "Filtrez par discipline, categorie et tour.",
    eventsMenuRankings: "Classements competition",
    eventsMenuRankingsText: "Passez d'un evenement a ses tableaux de score.",
    rankingsMenuScores: "Score rankings",
    rankingsMenuScoresText: "Triez par final score et composants disponibles.",
    rankingsMenuFilters: "Filtres intelligents",
    rankingsMenuFiltersText: "Utilisez seulement les valeurs presentes.",
    rankingsMenuQuality: "Qualite des donnees",
    rankingsMenuQualityText: "Reperez valeurs estimees ou non disponibles.",
    analyticsMenuTrends: "Tendances performance",
    analyticsMenuTrendsText: "Suivez les scores sur des periodes choisies.",
    analyticsMenuAge: "Age et pays",
    analyticsMenuAgeText: "Etudiez les ages par pays et evenement.",
    analyticsMenuApparatus: "Profils par appareil",
    analyticsMenuApparatusText: "Preparez des diagrammes MAG et WAG.",
    signIn: "Connexion",
    account: "Espace personnel",
    signOut: "Deconnexion",
    email: "Email",
    password: "Password",
    mfaCode: "Code MFA",
    loginAction: "Connexion",
    loginHelp: "Accedez a votre espace prive pour enregistrer athletes et evenements.",
    loginError: "Connexion impossible. Verifiez identifiants et verification email.",
    registerPrompt: "Vous n'avez pas encore de compte ?",
    registerLink: "Creer un compte",
    registerHeading: "Creez votre compte",
    registerIntro: "Rejoignez LEVERAGE pour enregistrer athletes, evenements et configurations personnelles de Ranking.",
    registerHelp: "Utilisez une adresse email valide et choisissez un mot de passe d'au moins 12 caracteres.",
    confirmPassword: "Confirmer le mot de passe",
    registerAction: "Creer le compte",
    alreadyRegistered: "Vous avez deja un compte ?",
    backToLogin: "Connexion",
    passwordMismatch: "Les mots de passe ne correspondent pas.",
    registrationSuccess: "Consultez votre messagerie. Si l'adresse peut etre enregistree, vous recevrez bientot un lien de verification.",
    registrationError: "Impossible de terminer l'inscription. Verifiez les donnees et reessayez.",
    verifyEmailHeading: "Verifiez votre email",
    verifyEmailIntro: "Terminez la verification pour activer votre compte LEVERAGE.",
    verificationChecking: "Verification de votre adresse email...",
    verificationSuccess: "Email verifie. Vous pouvez maintenant vous connecter.",
    verificationError: "Ce lien de verification est invalide ou a expire.",
    mfaRequired: "Saisissez le code MFA pour terminer la connexion.",
    mfaSetupRequired: "Ce compte admin doit configurer MFA avant de se connecter ici.",
    demoLoginNote: "Raccourcis temporaires pour le developpement frontend.",
    demoUser: "DEMO USER",
    demoAdmin: "DEMO ADMIN",
    demoSuperAdmin: "DEMO SUPER ADMIN",
    accountHeading: "Espace personnel",
    accountIntro: "Votre espace prive pour athletes favoris, evenements favoris et raccourcis personnels.",
    accountContentNavigation: "Choisissez vos contenus enregistres",
    favoriteAthletes: "Athletes favoris",
    favoriteEvents: "Evenements favoris",
    myFavoriteAthletes: "Mes athletes favoris",
    myFavoriteEvents: "Mes evenements favoris",
    favoritesFilter: "Favoris",
    levelFilter: "Level",
    athleteSortName: "Nom",
    athleteSortCountry: "Pays",
    addFavoriteAthlete: "Enregistrer athlete",
    removeFavoriteAthlete: "Retirer athlete",
    addFavoriteEvent: "Enregistrer evenement",
    removeFavoriteEvent: "Retirer evenement",
    loginRequiredFavorites: "Connectez-vous pour enregistrer des favoris.",
    noFavoriteAthletes: "Aucun athlete favori.",
    noFavoriteEvents: "Aucun evenement favori.",
    latestResult: "Dernier resultat",
    savedOn: "Enregistre le",
    savedRankingViews: "Rankings enregistres",
    savedRankingsShortcut: "Enregistres",
    noSavedRankingViews: "Aucune configuration Ranking enregistree.",
    saveRankingView: "Enregistrer ce Ranking",
    rankingViewName: "Nom Ranking",
    rankingViewNamePlaceholder: "Exemple : MAG FX cycle 2025",
    rankingViewSaved: "Configuration Ranking enregistree.",
    rankingViewError: "Impossible d'enregistrer cette configuration Ranking.",
    openSavedRanking: "Ouvrir Ranking enregistre",
    deleteSavedRanking: "Supprimer Ranking enregistre",
    clearRankingFilters: "Effacer filtres",
    clearSearch: "Effacer recherche",
    filters: "Filtres",
    activeFilterSingular: "filtre actif",
    activeFilterPlural: "filtres actifs",
    backToFilters: "Retour aux filtres",
    loadMoreAthletes: "Charger plus d'Athletes",
    loadMoreEvents: "Charger plus d'Evenements",
    loadMoreScores: "Charger plus de Scores",
    language: "Langue",
    save: "Enregistrer",
    footerTagline: "Artistic Gymnastics Analytics",
    heroEyebrow: "Gymnastique elite, structuree.",
    heroTitle: "LEVERAGE",
    heroSubtitle: "Artistic Gymnastics Analytics",
    heroBody: "Recherchez athletes, evenements et resultats dans une base de donnees de gymnastique structuree pour analyse, comparaison et contexte.",
    searchPlaceholder: "Rechercher athletes, evenements et resultats...",
    athleteSearchPlaceholder: "Rechercher athletes par nom, Leverage ID ou pays...",
    search: "Rechercher",
    globalSearchHeading: "Recherche globale",
    globalSearchIntro: "Recherchez athletes, evenements et resultats dans une base de donnees de gymnastique structuree pour analyse, comparaison et contexte.",
    matchingAthletes: "Athletes",
    matchingEvents: "Evenements",
    matchingResults: "Resultats",
    filteredResults: "Resultats filtres",
    relatedResults: "Resultats lies",
    noGlobalSearchResults: "Aucun resultat global trouve.",
    noStructuredSearchResults: "Aucun resultat ne correspond a tous les filtres de recherche. Les correspondances liees sont affichees ci-dessous.",
    dataLoadError: "Impossible de charger les donnees en direct. Reessayez dans un instant.",
    exploreTitle: "Commencer par les donnees",
    exploreSubtitle: "Quatre entrees simples dans la plateforme.",
    athletesTitle: "Explorer les Athletes",
    athletesText: "Trouvez les gymnastes par nom, pays ou discipline.",
    eventsTitle: "Voir les Evenements",
    eventsText: "Utilisez le calendrier pour parcourir les saisons.",
    rankingsTitle: "Creer des Rankings",
    rankingsText: "Triez les resultats par score, D score ou metriques disponibles.",
    compareTitle: "Comparer les Performances",
    compareText: "Preparez comparaisons et tendances dans le temps.",
    open: "Ouvrir",
    recentEvents: "Calendrier",
    calendarMonth: "Mois calendrier",
    currentMonth: "Mois courant",
    previousMonth: "Mois precedent",
    nextMonth: "Mois suivant",
    favoriteEventNavigation: "Navigation evenements favoris",
    previousFavoriteEvent: "Evenement favori precedent",
    nextFavoriteEvent: "Evenement favori suivant",
    eventNavigation: "Navigation evenements",
    previousEvent: "Evenement precedent",
    nextEvent: "Evenement suivant",
    today: "Aujourd'hui",
    resultsAvailable: "Resultats disponibles",
    resultsMissing: "Resultats manquants",
    ongoing: "En cours",
    upcoming: "A venir",
    completedWithResults: "Avec resultats",
    completedNoResults: "Resultats manquants",
    calendarOnly: "Calendrier seul",
    rankingPreview: "Ranking",
    viewAll: "Tout voir",
    athletesHeading: "Athletes",
    athletesIntro: "Recherchez les gymnastes par nom, pays, discipline ou categorie. Ouvrez les fiches, consultez les resultats et gerez les favoris en connexion.",
    eventsHeading: "Evenements",
    eventsIntro: "Trouvez les competitions en liste ou calendrier, filtrez par level, periode, discipline et categorie, puis ouvrez la fiche evenement.",
    eventSearchPlaceholder: "Rechercher evenements par competition, annee ou lieu...",
    eventViewList: "Liste",
    eventViewCalendar: "Calendrier",
    eventProfile: "Fiche evenement",
    eventDetails: "Informations",
    eventResultsHeading: "Classements evenement",
    eventResultsIntro: "Classements officiels charges pour cet evenement. Choisissez-en un pour afficher les resultats tries par Final Score.",
    eventClassification: "Classement",
    eventAvailableClassifications: "Classements charges",
    classificationSection: "Section",
    eventNoResults: "Aucun classement n'est encore disponible pour cet evenement.",
    eventResultWarnings: "Alertes resultats",
    eventUpdateSaved: "Evenement mis a jour.",
    eventUpdateError: "Impossible de mettre a jour l'evenement.",
    adminEventTools: "Outils admin",
    adminToolsButton: "Ouvrir les outils admin",
    editEvent: "Modifier evenement",
    findEvent: "Recherche automatique",
    useEvent: "Importer les donnees",
    figEventIdOrUrl: "FIG event ID ou URL evenement",
    officialRank: "Rang officiel",
    format: "Format",
    round: "Tour",
    day: "Jour",
    location: "Lieu",
    venue: "Site",
    rankingsHeading: "Rankings",
    rankingsIntro: "Construisez des Rankings depuis les resultats: filtrez par appareil, level, periode et cycle olympique, puis triez par Final Score ou composants.",
    analyticsHeading: "Analytique",
    analyticsIntro: "Comparez deux athletes avec des profils par appareil et des tendances de performance synchronises. Recherchez et ajoutez un athlete pour commencer l'analyse.",
    analyticsCompareAthleteA: "Premier athlete",
    analyticsCompareAthleteB: "Deuxieme athlete",
    analyticsCompareSearchFull: "Retirez un athlete pour en ajouter un autre.",
    analyticsCompareSameDiscipline: "Choisissez un athlete de la meme discipline.",
    analyticsCompareSameAthlete: "Choisissez deux athletes differents.",
    analyticsCompareSideBySide: "Cote a cote",
    analyticsCompareOverlay: "Superposes",
    analyticsCompareRemove: "Retirer l'athlete",
    analyticsCompareNoSuggestions: "Aucun athlete compatible trouve.",
    analyticsCompareFavoriteEmpty: "Aucun athlete favori compatible disponible.",
    analyticsCompareFavoriteError: "Impossible de charger les athletes favoris.",
    loginHeading: "Connexion",
    loginIntro: "Les espaces utilisateur et admin utiliseront l'authentification deja implementee.",
    noResults: "Aucun resultat.",
    loading: "Chargement...",
    discipline: "Discipline",
    category: "Categorie",
    apparatus: "Appareil",
    all: "Tout",
    senior: "Senior",
    junior: "Junior",
    results: "resultats",
    result: "resultat",
    score: "Score",
    rankingMetric: "Metrique Ranking",
    estimatedEScoreRankingNotice: "E Score est estimé à partir du Final Score et du D Score. Il peut inclure des données Penalty ou Bonus indisponibles.",
    penaltyDataUnavailable: "Les données Penalty ne sont pas disponibles pour les filtres sélectionnés. Utilisez Final Score, D Score ou E Score, ou modifiez les filtres.",
    bonusDataUnavailable: "Les données Bonus ne sont pas disponibles pour les filtres sélectionnés. Utilisez Final Score, D Score ou E Score, ou modifiez les filtres.",
    vaultAverageComponentDataUnavailable: "Les données composantes de VT AVG ne sont pas disponibles pour la métrique sélectionnée. Utilisez Final Score ou changez d'appareil.",
    scoringCycle: "Cycle olympique",
    allCycles: "Tous les cycles",
    timeInterval: "Periode",
    fromDate: "Depuis date",
    toDate: "Jusqu'a date",
    datePlaceholder: "jj/mm/aaaa",
    dateYear: "Annee",
    dateMonth: "Mois",
    dateDay: "Jour",
    eventYear: "Annee competition",
    country: "Pays",
    date: "Date",
    status: "Statut",
    event: "Evenement",
    athlete: "Athlete",
    athleteProfile: "Fiche athlete",
    athleteIdentity: "Identite",
    officialData: "Donnees officielles",
    firstName: "Prenom",
    lastName: "Nom",
    birthYear: "Annee de naissance",
    leverageId: "Leverage ID",
    athleteId: "Leverage ID",
    image: "Image",
    imageUrl: "URL image",
    worldGymnasticsProfile: "Profil World Gymnastics",
    worldGymnasticsData: "World Gymnastics",
    worldGymnasticsEvent: "Evenement World Gymnastics",
    worldGymnasticsId: "ID World Gymnastics",
    worldGymnasticsStatus: "Statut World Gymnastics",
    worldGymnasticsVerified: "World Gymnastics verifie",
    verifiedByAdminId: "Verifie par admin ID",
    openWorldGymnastics: "Ouvrir World Gymnastics",
    notLinked: "Non lie",
    notAvailable: "Non disponible",
    countryHistory: "Historique nationalite",
    noCountryHistory: "Aucun changement de nationalite enregistre.",
    adminAthleteTools: "Outils admin",
    editAthlete: "Modifier athlete",
    saveChanges: "Enregistrer modifications",
    updateSaved: "Athlete mis a jour.",
    updateError: "Impossible de mettre a jour l'athlete.",
    verifiedAthleteBadge: "Athlete verifie",
    assignVerificationBadge: "Attribuer le badge de verification",
    removeVerificationBadge: "Retirer le badge de verification",
    verificationBadgeAssigned: "Badge de verification attribue.",
    verificationBadgeRemoved: "Badge de verification retire.",
    verificationBadgeError: "Impossible de mettre a jour le badge de verification.",
    countryChangeYear: "Annee changement nationalite",
    adminSuggestions: "Données en attente d’approbation",
    adminSuggestionSingular: "donnée en attente d’approbation",
    adminSuggestionPlural: "données en attente d’approbation",
    noPendingSuggestions: "Aucune donnée en attente d’approbation.",
    suggestedValue: "Valeur suggeree",
    evidence: "Preuve",
    accept: "Accepter",
    reject: "Refuser",
    suggestionAccepted: "Suggestion acceptee.",
    suggestionRejected: "Suggestion refusee.",
    suggestionError: "Impossible de reviser la suggestion.",
    worldGymnasticsAssistant: "Assistant World Gymnastics",
    findProfile: "Recherche automatique",
    figIdOrUrl: "FIG ID ou URL profil",
    generateFromProfile: "Recherche manuelle",
    useProfile: "Importer les donnees",
    noWorldGymnasticsCandidates: "Aucun candidat World Gymnastics trouve.",
    profileSearchError: "Recherche World Gymnastics impossible.",
    profileSuggestionsCreated: "Données World Gymnastics importées pour révision.",
    wgWarningTypeNoCandidates: "Aucun candidat",
    wgWarningTypeNameMismatch: "Controle du nom",
    wgWarningTypeCountryMismatch: "Controle du pays",
    wgWarningTypeDisciplineMismatch: "Controle discipline",
    wgWarningTypeEventMismatch: "Controle evenement",
    wgWarningNoAthleteCandidates: "Aucun candidat de profil athlete World Gymnastics trouve.",
    wgWarningNoEventCandidates: "Aucun candidat evenement World Gymnastics trouve.",
    wgWarningNameMismatch: "Le nom de l'athlete dans LEVERAGE differe du profil World Gymnastics selectionne.",
    wgWarningCountryMismatch: "Le pays de l'athlete dans LEVERAGE differe du profil World Gymnastics selectionne.",
    wgWarningDisciplineMismatch: "La discipline LEVERAGE n'apparait pas sur le profil World Gymnastics selectionne.",
    athleteAnalyticsHeading: "Analytique performance",
    athleteAnalyticsIntro: "Profil interactif par appareil, tendances de score et statistiques de synthese construites depuis les resultats de l'athlete.",
    analyticsMetric: "Metrique",
    analyticsMode: "Vue temporelle",
    analyticsModePeriod: "Periode",
    analyticsModeSnapshot: "Instant",
    analyticsTimeline: "Timeline",
    analyticsUpTo: "Jusqu'a",
    analyticsAt: "Au",
    analyticsAverage: "Moyenne",
    analyticsBest: "Meilleur",
    analyticsLatest: "Dernier",
    analyticsEvents: "Evenements",
    analyticsTotalResults: "Resultats totaux",
    analyticsNoData: "Aucune donnee analytique disponible pour cette metrique.",
    analyticsMetricUnavailable: "Cette métrique n'est pas disponible pour cet athlète dans les données sélectionnées.",
    analyticsEEstimateNotice: "E Score peut être estimé depuis Final Score et D Score et peut inclure des données Penalty ou Bonus indisponibles.",
    analyticsEventPeriod: "Periode evenement",
    analyticsMultipleEventPeriods: "Plusieurs periodes evenement",
    analyticsEventPeriodNotice: "Certains résultats proviennent d'événements sur plusieurs jours. Quand Gymternet ne fournit pas la date exacte de la session, Leverage affiche la période événement du calendrier et utilise le début de l'événement seulement comme repère chronologique.",
    analyticsDateSource: "Source temporelle",
    analyticsDateSourceDefaultSummary: "Les statistiques utilisent les dates ou périodes événement disponibles dans Leverage. Les événements sur plusieurs jours sans date exacte de session sont affichés comme périodes événement, pas comme résultats du premier jour.",
    analyticsDateSourcePeriodSummary: "Ces statistiques incluent des résultats associés à la période de l'événement, pas à un seul jour de début de compétition.",
    analyticsRoundFormats: "Rounds / formats",
    analyticsMoreEventSingular: "autre événement",
    analyticsMoreEvents: "autres événements",
    analyticsShapeTitle: "Profil par appareil",
    analyticsTrendTitle: "Trend performance",
    analyticsYearTitle: "Moyennes par annee",
    analyticsPointCount: "points",
    analyticsPointSingular: "point",
    analyticsPointPlural: "points",
    analyticsResultCount: "resultats",
    analyticsResultSingular: "résultat",
    analyticsResultPlural: "résultats",
    analyticsNoApparatusData: "Aucune donnee appareil",
    analyticsScoringCycles: "Cycles olympiques",
    analyticsScoringCycleSingular: "Cycle olympique",
    analyticsScoringCyclePlural: "Cycles olympiques",
    analyticsMultipleScoringCyclesNotice: "Cette sélection inclut plusieurs cycles olympiques. Les scores peuvent refléter différents Codes de pointage.",
    warningVaultAttemptOrder: "L'ordre des sauts peut être incertain: Vault 1 peut correspondre à Vault 2 et inversement.",
    warningExecutionEstimate: "Exécution estimée à partir du D Score et du Final Score.",
    warningExecutionEstimatePenalty: "Exécution estimée à partir du D Score et du Final Score, avec de possibles données Penalty indisponibles.",
    warningExecutionEstimateBonus: "Exécution estimée à partir du D Score et du Final Score, avec un possible Bonus non enregistré.",
    warningExecutionEstimatePenaltyBonus: "Exécution estimée à partir du D Score et du Final Score, avec de possibles données Penalty indisponibles et un possible Bonus non enregistré.",
    rankingWarningMixedDisciplines: "Ce Ranking combine intentionnellement des résultats MAG et WAG. Les règles des appareils et les échelles de score peuvent ne pas être directement comparables.",
    rankingWarningMixedDisciplineMode: "Le mode multi-discipline est actif. Les résultats restent comparables uniquement lorsque le contexte sélectionné est sémantiquement cohérent.",
    rankingWarningMultipleScoringCycles: "Ce Ranking inclut plusieurs cycles olympiques ({cycles}). Les scores peuvent refléter différents Codes de pointage.",
    notApplicable: "Non applicable",
    apparatusScoresUnavailable: "Scores par appareil non disponibles",
    backToAthletes: "Retour aux Athletes",
    backToRanking: "Retour au Ranking",
    backToClassification: "Retour au classement",
    backToEvents: "Retour aux Evenements",
    backToHome: "Retour a l'accueil",
    comingSoon: "Bientot",
  },
};

const $ = (selector) => document.querySelector(selector);
const t = (key) => translations[state.language]?.[key] || translations.en[key] || key;
function tx(key, replacements = {}) {
  return t(key).replace(/\{([a-zA-Z0-9_]+)\}/g, (_, token) => (
    Object.prototype.hasOwnProperty.call(replacements, token) ? String(replacements[token]) : ""
  ));
}

function localizedCount(count, singularKey, pluralKey) {
  const number = Number(count) || 0;
  const label = t(Math.abs(number) === 1 ? singularKey : pluralKey);
  return `${number.toLocaleString()} ${label}`;
}

function localizedBackendWarning(message) {
  const text = String(message || "").trim();
  if (!text) return "";
  const normalized = text.toLowerCase();
  if (normalized.includes("vault 1") && normalized.includes("vault 2")) {
    return t("warningVaultAttemptOrder");
  }
  if (
    normalized.includes("estimated execution from d score and final score") &&
    normalized.includes("penalty") &&
    normalized.includes("bonus")
  ) {
    return t("warningExecutionEstimatePenaltyBonus");
  }
  if (
    normalized.includes("estimated execution from d score and final score") &&
    normalized.includes("penalty")
  ) {
    return t("warningExecutionEstimatePenalty");
  }
  if (
    normalized.includes("estimated execution from d score and final score") &&
    normalized.includes("bonus")
  ) {
    return t("warningExecutionEstimateBonus");
  }
  if (normalized.includes("estimated execution from d score and final score")) {
    return t("warningExecutionEstimate");
  }
  if (normalized.includes("mixes mag and wag results")) {
    return t("rankingWarningMixedDisciplines");
  }
  if (normalized.includes("mixed-discipline mode was enabled")) {
    return t("rankingWarningMixedDisciplineMode");
  }
  if (normalized.includes("multiple gymnastics scoring cycles")) {
    const cycleLabels = text.match(/\(([^)]+)\)/)?.[1] || "";
    return tx("rankingWarningMultipleScoringCycles", { cycles: cycleLabels });
  }
  return text;
}

function normalizedWarningSearchText(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/\s+/g, " ")
    .trim();
}

function executionEstimateWarningFlags(message) {
  const normalized = normalizedWarningSearchText(message);
  const isGenericEScoreEstimate = normalized.includes("e score") &&
    normalized.includes("final score") &&
    normalized.includes("d score") &&
    ["estimated", "stimato", "stimata", "estimato", "estimata", "estima", "estimarse", "estime"].some((term) => normalized.includes(term));
  const isExecutionEstimate = [
    "estimated execution from d score and final score",
    "esecuzione stimata da d score e final score",
    "ejecucion estimada a partir de d score y final score",
    "execution estimee a partir du d score et du final score",
  ].some((fragment) => normalized.includes(fragment));
  if (!isExecutionEstimate && !isGenericEScoreEstimate) {
    return null;
  }
  return {
    generic: true,
    frontendGeneric: isGenericEScoreEstimate,
    penalty: isExecutionEstimate && normalized.includes("penalty"),
    bonus: isExecutionEstimate && normalized.includes("bonus"),
  };
}

function localizedExecutionEstimateWarning(flags) {
  if (!flags?.generic) return "";
  if (flags.penalty && flags.bonus) return t("warningExecutionEstimatePenaltyBonus");
  if (flags.penalty) return t("warningExecutionEstimatePenalty");
  if (flags.bonus) return t("warningExecutionEstimateBonus");
  return t("warningExecutionEstimate");
}

function localizedBackendWarnings(messages = []) {
  const warnings = [];
  const seen = new Set();
  const executionFlags = { generic: false, penalty: false, bonus: false };
  let executionInsertIndex = null;
  messages.forEach((message) => {
    const estimateFlags = executionEstimateWarningFlags(message);
    if (estimateFlags) {
      executionFlags.generic = true;
      executionFlags.penalty = executionFlags.penalty || estimateFlags.penalty;
      executionFlags.bonus = executionFlags.bonus || estimateFlags.bonus;
      if (executionInsertIndex === null) executionInsertIndex = warnings.length;
      return;
    }
    const warning = localizedBackendWarning(message);
    if (!warning || seen.has(warning)) return;
    seen.add(warning);
    warnings.push(warning);
  });
  const executionWarning = localizedExecutionEstimateWarning(executionFlags);
  if (executionWarning && !seen.has(executionWarning)) {
    warnings.splice(executionInsertIndex ?? warnings.length, 0, executionWarning);
  }
  return warnings;
}

function uniqueTextItems(values = []) {
  const seen = new Set();
  return values
    .map((value) => String(value || "").trim())
    .filter((value) => {
      if (!value || seen.has(value)) return false;
      seen.add(value);
      return true;
    });
}

function consolidatedDataWarnings(values = []) {
  const warnings = [];
  const seen = new Set();
  const executionFlags = { generic: false, penalty: false, bonus: false };
  let executionInsertIndex = null;
  let frontendExecutionNotice = "";
  uniqueTextItems(values).forEach((message) => {
    const estimateFlags = executionEstimateWarningFlags(message);
    if (estimateFlags) {
      executionFlags.generic = true;
      executionFlags.penalty = executionFlags.penalty || estimateFlags.penalty;
      executionFlags.bonus = executionFlags.bonus || estimateFlags.bonus;
      if (estimateFlags.frontendGeneric && !frontendExecutionNotice) {
        frontendExecutionNotice = message;
      }
      if (executionInsertIndex === null) executionInsertIndex = warnings.length;
      return;
    }
    const key = normalizedWarningSearchText(message);
    if (!key || seen.has(key)) return;
    seen.add(key);
    warnings.push(message);
  });
  const executionWarning = executionFlags.penalty || executionFlags.bonus || !frontendExecutionNotice
    ? localizedExecutionEstimateWarning(executionFlags)
    : frontendExecutionNotice;
  if (executionWarning && !seen.has(normalizedWarningSearchText(executionWarning))) {
    warnings.splice(executionInsertIndex ?? warnings.length, 0, executionWarning);
  }
  return warnings;
}

function renderDataWarningStack(messages = [], extraClass = "") {
  const warnings = consolidatedDataWarnings(messages);
  if (!warnings.length) return "";
  const className = ["data-warning-stack", extraClass].filter(Boolean).join(" ");
  return `
    <div class="${className}">
      <div class="data-warning-box warning-notice">
        ${warnings.map((warning) => `<span>${escapeHtml(warning)}</span>`).join("")}
      </div>
    </div>
  `;
}

function warningIsVaultAttemptOrder(message) {
  const normalized = normalizedWarningSearchText(message);
  return normalized.includes("vault 1") && normalized.includes("vault 2");
}

function warningIsMultipleScoringCycles(message) {
  const normalized = normalizedWarningSearchText(message);
  return normalized.includes("multiple gymnastics scoring cycles") ||
    normalized.includes("piu cicli olimpici") ||
    normalized.includes("varios ciclos olimpicos") ||
    normalized.includes("plusieurs cycles olympiques");
}

function localizedWorldGymnasticsWarning(warning = {}) {
  const typeKeyByType = {
    no_candidates: "wgWarningTypeNoCandidates",
    name_mismatch: "wgWarningTypeNameMismatch",
    country_mismatch: "wgWarningTypeCountryMismatch",
    discipline_mismatch: "wgWarningTypeDisciplineMismatch",
    title_mismatch: "wgWarningTypeEventMismatch",
    start_date_mismatch: "wgWarningTypeEventMismatch",
    end_date_mismatch: "wgWarningTypeEventMismatch",
    category_mismatch: "wgWarningTypeEventMismatch",
    level_mismatch: "wgWarningTypeEventMismatch",
    location_mismatch: "wgWarningTypeEventMismatch",
    venue_mismatch: "wgWarningTypeEventMismatch",
  };
  const message = String(warning.message || "").trim();
  const normalized = message.toLowerCase();
  let messageText = message;
  if (normalized.includes("no world gymnastics athlete profile candidates")) {
    messageText = t("wgWarningNoAthleteCandidates");
  } else if (normalized.includes("no world gymnastics event candidates")) {
    messageText = t("wgWarningNoEventCandidates");
  } else if (normalized.includes("athlete name differs")) {
    messageText = t("wgWarningNameMismatch");
  } else if (normalized.includes("athlete country differs")) {
    messageText = t("wgWarningCountryMismatch");
  } else if (normalized.includes("discipline is not listed")) {
    messageText = t("wgWarningDisciplineMismatch");
  }
  return {
    type: t(typeKeyByType[warning.type] || "") || warning.type || t("status"),
    message: messageText,
  };
}

const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
}[character]));

function setLanguage(language) {
  state.language = language;
  localStorage.setItem(LANGUAGE_KEY, language);
  document.documentElement.lang = language;
  applyTranslations();
  syncLanguageControl();
  render();
}

function applyTranslations() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  updateAuthUi();
}

function syncTopbarHeight() {
  const topbar = document.querySelector(".topbar");
  if (!topbar) return;
  document.documentElement.style.setProperty("--topbar-height", `${Math.ceil(topbar.getBoundingClientRect().height)}px`);
}

function syncLanguageControl() {
  const label = $("#languageLabel");
  if (label) {
    label.textContent = state.language.toUpperCase();
  }
  document.querySelectorAll("[data-language-option]").forEach((button) => {
    const isSelected = button.dataset.languageOption === state.language;
    button.hidden = isSelected;
    button.setAttribute("aria-selected", String(isSelected));
  });
}

function updateAuthUi() {
  const authLink = $("#authLink");
  if (!authLink) return;
  if (state.currentUser) {
    authLink.href = "#/account";
    authLink.textContent = t("account");
    authLink.removeAttribute("data-i18n");
  } else {
    authLink.href = "#/login";
    authLink.dataset.i18n = "signIn";
    authLink.textContent = t("signIn");
  }
}

function closeLanguageMenu() {
  const control = $("#languageControl");
  const button = $("#languageButton");
  if (!control || !button) return;
  control.classList.remove("is-open");
  button.setAttribute("aria-expanded", "false");
}

function closeSearchSuggestions() {
  searchAutocompleteRequestId += 1;
  analyticsComparisonSearchRequestId += 1;
  document.querySelectorAll(".search-suggestions").forEach((node) => {
    node.hidden = true;
    node.innerHTML = "";
    setSearchSuggestionsOpen(node, false);
    setSearchSuggestionsBusy(node, false);
  });
}

function setSearchSuggestionsOpen(suggestions, isOpen, itemCount = 4) {
  const form = suggestions.closest(".search-form");
  if (!form) return;
  form.classList.toggle("search-suggestions-open", isOpen);
  form.closest(".section-search-row")?.classList.toggle("search-suggestions-layer-open", isOpen);
  if (!isOpen) {
    form.style.removeProperty("--search-suggestions-visible-height");
    return;
  }
  const visibleRows = Math.min(Math.max(itemCount, 1), 4);
  const rowHeight = 66;
  const rowGap = 3;
  const panelPadding = 16;
  const height = panelPadding + (visibleRows * rowHeight) + (Math.max(0, visibleRows - 1) * rowGap);
  form.style.setProperty("--search-suggestions-visible-height", `${height}px`);
}

function setSearchSuggestionsBusy(suggestions, isBusy) {
  if (isBusy) {
    suggestions.setAttribute("aria-busy", "true");
  } else {
    suggestions.removeAttribute("aria-busy");
  }
}

function setupIntroSplash() {
  const splash = $("#introSplash");
  if (!splash) return;
  const initialRoute = window.location.hash.replace(/^#/, "") || "/";
  if (initialRoute !== "/") {
    document.body.classList.remove("intro-active");
    splash.remove();
    return;
  }
  let splashFinished = false;
  const finishSplash = () => {
    if (splashFinished) return;
    splashFinished = true;
    splash.remove();
  };
  const finishIntro = () => {
    finishSplash();
    document.body.classList.remove("intro-active");
  };
  splash.addEventListener("animationend", (event) => {
    if (event.target === splash) finishSplash();
  });
  window.setTimeout(finishSplash, 1900);
  window.setTimeout(finishIntro, 2350);
}

function normalizedApiBase(value) {
  return String(value || "").trim().replace(/\/$/, "");
}

function apiBaseCandidates() {
  return [
    normalizedApiBase(state.apiBase),
    ...API_FALLBACK_BASES.map(normalizedApiBase),
  ].filter((base, index, bases) => base && bases.indexOf(base) === index);
}

function syncApiBase(base) {
  const normalizedBase = normalizedApiBase(base);
  if (!normalizedBase || state.apiBase === normalizedBase) return;
  state.apiBase = normalizedBase;
  localStorage.setItem(API_BASE_KEY, normalizedBase);
}

function apiUrl(path, params = {}, base = state.apiBase) {
  const url = new URL(path, normalizedApiBase(base));
  Object.entries(params).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.filter((item) => item !== undefined && item !== null && item !== "").forEach((item) => {
        url.searchParams.append(key, item);
      });
    } else if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, value);
    }
  });
  return url.toString();
}

async function fetchApi(path, params = {}, options = {}) {
  let lastError = null;
  for (const base of apiBaseCandidates()) {
    try {
      const response = await fetch(apiUrl(path, params, base), options);
      syncApiBase(base);
      return response;
    } catch (error) {
      if (error?.name === "AbortError" || options.signal?.aborted) {
        throw error;
      }
      lastError = error;
    }
  }
  throw lastError || new Error("API unavailable");
}

function authHeaders(includeJson = false) {
  const headers = { Accept: "application/json" };
  if (includeJson) headers["Content-Type"] = "application/json";
  if (state.authToken) headers.Authorization = `Bearer ${state.authToken}`;
  return headers;
}

function clearAuth() {
  state.authToken = "";
  state.currentUser = null;
  state.favoriteAthleteIds = new Set();
  state.favoriteEventIds = new Set();
  state.favoritesLoaded = false;
  state.filters.athletes.favoritesOnly = "";
  state.filters.events.favoritesOnly = "";
  state.analyticsComparison.favoriteDetails = [];
  state.analyticsComparison.favoritesOpen = false;
  state.analyticsComparison.favoritesLoading = false;
  state.analyticsComparison.favoritesError = "";
  localStorage.removeItem(AUTH_TOKEN_KEY);
  updateAuthUi();
}

async function getJson(path, params = {}, options = {}) {
  const response = await fetchApi(path, params, {
    headers: options.auth ? authHeaders() : { Accept: "application/json" },
    signal: options.signal,
  });
  if (!response.ok) {
    if (options.auth && response.status === 401) clearAuth();
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

async function sendJson(path, { method = "POST", body = null, auth = true } = {}) {
  const response = await fetchApi(path, {}, {
    method,
    headers: auth ? authHeaders(Boolean(body)) : {
      Accept: "application/json",
      ...(body ? { "Content-Type": "application/json" } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    if (auth && response.status === 401) clearAuth();
    throw new Error(`${response.status} ${response.statusText}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

async function hydrateCurrentUser() {
  if (!state.authToken) {
    clearAuth();
    return null;
  }
  try {
    state.currentUser = await getJson("/auth/me", {}, { auth: true });
    updateAuthUi();
    return state.currentUser;
  } catch (_error) {
    clearAuth();
    return null;
  }
}

async function completeLoginWithToken(accessToken) {
  state.authToken = accessToken;
  localStorage.setItem(AUTH_TOKEN_KEY, state.authToken);
  state.favoritesLoaded = false;
  await hydrateCurrentUser();
  await ensureFavoritesLoaded({ force: true }).catch(() => {});
  window.location.hash = "#/account";
}

async function ensureFavoritesLoaded({ force = false } = {}) {
  if (!state.currentUser) return;
  if (state.favoritesLoaded && !force) return;
  const [athletes, events] = await Promise.all([
    getJson("/preferences/athletes/followed", {}, { auth: true }),
    getJson("/preferences/events/saved", {}, { auth: true }),
  ]);
  state.favoriteAthleteIds = new Set(athletes.map((item) => Number(item.athlete_id)));
  state.favoriteEventIds = new Set(events.map((item) => Number(item.event_id)));
  state.favoritesLoaded = true;
}

async function trackSiteSearch(query) {
  try {
    await fetch(apiUrl("/site-analytics/events"), {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        event_type: "search",
        path: state.route,
        search_query: query,
      }),
    });
  } catch (_error) {
    // Analytics must never block public search.
  }
}

function formatDateRange(item) {
  const start = item.start_date || "";
  const end = item.end_date || "";
  if (!start && !end) return "";
  if (start === end || !end) return start;
  return `${start} - ${end}`;
}

function formatReadableDate(value, includeYear = true) {
  const date = parseLocalDate(value);
  if (!date) return "";
  return new Intl.DateTimeFormat(state.language, {
    month: "short",
    day: "numeric",
    ...(includeYear ? { year: "numeric" } : {}),
  }).format(date);
}

function formatReadableDateRange(item) {
  const start = parseLocalDate(item.start_date);
  const end = parseLocalDate(item.end_date);
  if (!start && !end) return String(item.year || "");
  if (!start) return formatReadableDate(item.end_date);
  if (!end || sameDay(start, end)) return formatReadableDate(item.start_date || item.end_date);
  const sameYearValue = start.getFullYear() === end.getFullYear();
  const sameMonthValue = sameYearValue && start.getMonth() === end.getMonth();
  if (sameMonthValue) {
    const month = new Intl.DateTimeFormat(state.language, { month: "short" }).format(start);
    return `${month} ${start.getDate()}-${end.getDate()}, ${start.getFullYear()}`;
  }
  if (sameYearValue) {
    return `${formatReadableDate(item.start_date, false)}-${formatReadableDate(item.end_date, false)}, ${start.getFullYear()}`;
  }
  return `${formatReadableDate(item.start_date)}-${formatReadableDate(item.end_date)}`;
}

function parseLocalDate(value) {
  if (!value) return null;
  const [year, month, day] = String(value).split("-").map(Number);
  if (!year || !month || !day) return null;
  return new Date(year, month - 1, day);
}

function formatLocalIso(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function clampNumber(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function daysInMonth(year, month) {
  return new Date(year, month, 0).getDate();
}

function defaultDatePickerDate() {
  return new Date(clampNumber(TODAY.getFullYear(), DATE_PICKER_START_YEAR, DATE_PICKER_END_YEAR), 0, 1);
}

function defaultDatePickerIso() {
  return formatLocalIso(defaultDatePickerDate());
}

function datePickerParts(value) {
  const parsed = parseLocalDate(value) || defaultDatePickerDate();
  const year = clampNumber(parsed.getFullYear(), DATE_PICKER_START_YEAR, DATE_PICKER_END_YEAR);
  const month = parsed.getMonth() + 1;
  const day = clampNumber(parsed.getDate(), 1, daysInMonth(year, month));
  return { year, month, day };
}

function isoFromDateParts(parts) {
  const year = clampNumber(Number(parts.year) || TODAY.getFullYear(), DATE_PICKER_START_YEAR, DATE_PICKER_END_YEAR);
  const month = clampNumber(Number(parts.month) || 1, 1, 12);
  const day = clampNumber(Number(parts.day) || 1, 1, daysInMonth(year, month));
  return `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

function isoDateIsBefore(leftDate, rightDate) {
  return Boolean(leftDate && rightDate && String(leftDate) < String(rightDate));
}

function validIsoDate(year, month, day) {
  if (year < DATE_PICKER_START_YEAR || year > DATE_PICKER_END_YEAR) return "";
  if (month < 1 || month > 12 || day < 1 || day > daysInMonth(year, month)) return "";
  return `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

function validPeriodMonth(year, month) {
  if (year < DATE_PICKER_START_YEAR || year > DATE_PICKER_END_YEAR) return null;
  if (month < 1 || month > 12) return null;
  const monthValue = String(month).padStart(2, "0");
  return {
    startDate: `${year}-${monthValue}-01`,
    endDate: `${year}-${monthValue}-${String(daysInMonth(year, month)).padStart(2, "0")}`,
    display: `${monthValue}/${year}`,
  };
}

function validPeriodYear(year) {
  if (year < DATE_PICKER_START_YEAR || year > DATE_PICKER_END_YEAR) return null;
  return {
    startDate: `${year}-01-01`,
    endDate: `${year}-12-31`,
    display: String(year),
  };
}

function periodFromFullDate(isoDate) {
  if (!isoDate) return null;
  return {
    startDate: isoDate,
    endDate: isoDate,
    display: formatDateInputValue(isoDate),
  };
}

function normalizeTypedDate(value) {
  const text = String(value || "").trim();
  if (!text) return "";
  let match = text.match(/^(\d{4})[-/.](\d{2})[-/.](\d{2})$/);
  if (match) {
    return validIsoDate(Number(match[1]), Number(match[2]), Number(match[3])) || null;
  }
  match = text.match(/^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})$/);
  if (match) {
    return validIsoDate(Number(match[3]), Number(match[2]), Number(match[1])) || null;
  }
  match = text.match(/^(\d{8})$/);
  if (match) {
    const raw = match[1];
    const leadingYear = Number(raw.slice(0, 4));
    if (leadingYear >= DATE_PICKER_START_YEAR && leadingYear <= DATE_PICKER_END_YEAR) {
      return validIsoDate(leadingYear, Number(raw.slice(4, 6)), Number(raw.slice(6, 8))) || null;
    }
    return validIsoDate(Number(raw.slice(4, 8)), Number(raw.slice(2, 4)), Number(raw.slice(0, 2))) || null;
  }
  return null;
}

function normalizeTypedPeriod(value) {
  const text = String(value || "").trim();
  if (!text) return { startDate: "", endDate: "", display: "" };

  let match = text.match(/^(\d{4})$/);
  if (match) return validPeriodYear(Number(match[1]));

  match = text.match(/^(\d{4})[-/.](\d{1,2})$/);
  if (match) return validPeriodMonth(Number(match[1]), Number(match[2]));

  match = text.match(/^(\d{1,2})[-/.](\d{4})$/);
  if (match) return validPeriodMonth(Number(match[2]), Number(match[1]));

  match = text.match(/^(\d{6})$/);
  if (match) {
    const raw = match[1];
    return validPeriodMonth(Number(raw.slice(2, 6)), Number(raw.slice(0, 2)));
  }

  const isoDate = normalizeTypedDate(text);
  if (isoDate === "") return { startDate: "", endDate: "", display: "" };
  return periodFromFullDate(isoDate);
}

function periodDateForField(period, field) {
  if (!period) return "";
  return field === "endDate" ? period.endDate : period.startDate;
}

function periodInputShouldValidate(value) {
  const digits = String(value || "").replace(/\D/g, "");
  if (digits.length >= 8) return true;
  if (digits.length === 6) return true;
  if (digits.length === 4 && Number(digits) >= 1900) return true;
  return /^\d{4}[-/.]\d{1,2}$/.test(String(value || "").trim());
}

function formatDateInputValue(value) {
  const date = parseLocalDate(value);
  if (!date) return "";
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const year = String(date.getFullYear());
  return `${day}/${month}/${year}`;
}

function formatTypedDateInput(value) {
  const text = String(value || "");
  if (/^\d{4}[-/.]/.test(text)) return text.slice(0, 10);
  if (/[a-z]/i.test(text)) return text;
  const digits = text.replace(/\D/g, "").slice(0, 8);
  if (digits.length <= 2) return digits;

  if (digits.length < 4 && /^(19|20)/.test(digits)) {
    return digits;
  }

  if (digits.length === 4) {
    const possibleYear = Number(digits);
    if (possibleYear >= DATE_PICKER_START_YEAR && possibleYear <= DATE_PICKER_END_YEAR) return digits;
  }

  if (digits.length > 4 && digits.length <= 6) {
    const possibleMonth = Number(digits.slice(0, 2));
    const possibleYearPrefix = digits.slice(2);
    if (possibleMonth >= 1 && possibleMonth <= 12 && /^20\d{0,2}$/.test(possibleYearPrefix)) {
      return `${digits.slice(0, 2)}/${possibleYearPrefix}`;
    }
  }

  if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`;
  if (digits.length <= 6) return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4, 8)}`;
}

function monthShortLabel(month) {
  return new Intl.DateTimeFormat(state.language, { month: "short" }).format(new Date(2020, month - 1, 1));
}

function addDays(date, days) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

function startOfWeekMonday(date) {
  const start = new Date(date);
  const offset = (start.getDay() + 6) % 7;
  start.setDate(start.getDate() - offset);
  return start;
}

function sameDay(left, right) {
  return left.getFullYear() === right.getFullYear() &&
    left.getMonth() === right.getMonth() &&
    left.getDate() === right.getDate();
}

function sameMonth(left, right) {
  return left.getFullYear() === right.getFullYear() && left.getMonth() === right.getMonth();
}

function monthLabel(date) {
  return new Intl.DateTimeFormat(state.language, { month: "long", year: "numeric" }).format(date);
}

function monthTitleParts(date) {
  return {
    month: new Intl.DateTimeFormat(state.language, { month: "long" }).format(date),
    year: new Intl.DateTimeFormat(state.language, { year: "numeric" }).format(date),
  };
}

function weekdayLabels() {
  const monday = new Date(2026, 0, 5);
  return Array.from({ length: 7 }, (_, index) => (
    new Intl.DateTimeFormat(state.language, { weekday: "short" }).format(addDays(monday, index))
  ));
}

function sortCalendarItems(items) {
  return [...items].sort((left, right) => {
    const leftDate = left.start_date || "9999-12-31";
    const rightDate = right.start_date || "9999-12-31";
    return leftDate.localeCompare(rightDate) || left.name.localeCompare(right.name);
  });
}

function resultLabel(count) {
  const value = Number(count || 0).toLocaleString();
  return `${value} ${count === 1 ? t("result") : t("results")}`;
}

function normalizeRoute() {
  const raw = window.location.hash.replace(/^#/, "") || "/";
  state.route = raw.startsWith("/") ? raw : `/${raw}`;
}

function persistSectionRoutes() {
  try {
    sessionStorage.setItem(SECTION_ROUTE_MEMORY_KEY, JSON.stringify(state.sectionRoutes));
  } catch (_error) {
    // Section route memory is a convenience feature; ignore storage failures.
  }
}

function rememberCurrentSectionRoute() {
  const section = activeRouteSection(state.route);
  if (!section) return;
  if (
    section === "athletes" &&
    !isAthleteSectionDetailRoute(state.route) &&
    isAthleteSectionDetailRoute(state.sectionRoutes.athletes)
  ) {
    return;
  }
  state.sectionRoutes[section] = state.route;
  persistSectionRoutes();
}

function rememberAthleteListRoute() {
  if (!routeIsListSection("athletes")) return;
  state.sectionRoutes.athletes = state.route;
  persistSectionRoutes();
  syncSectionNavLinks();
}

function sectionNavigationRoute(section) {
  if (!section || !SECTION_BASE_ROUTES[section]) return "/";
  const contextualSource = contextualAthleteSourceSection(state.route);
  if (contextualSource && contextualSource !== "athletes" && section === "athletes") {
    return SECTION_BASE_ROUTES.athletes;
  }
  return routeBelongsToSection(state.sectionRoutes[section], section)
    ? state.sectionRoutes[section]
    : SECTION_BASE_ROUTES[section];
}

function syncSectionNavLinks() {
  document.querySelectorAll(".nav-trigger[data-section-nav]").forEach((link) => {
    const section = link.dataset.sectionNav;
    if (!section || !SECTION_BASE_ROUTES[section]) return;
    link.setAttribute("href", `#${sectionNavigationRoute(section)}`);
  });
}

function bindSectionNavLinks() {
  document.querySelectorAll(".nav-trigger[data-section-nav]").forEach((link) => {
    link.addEventListener("click", (event) => {
      const section = link.dataset.sectionNav;
      if (!section || !SECTION_BASE_ROUTES[section]) return;
      // Capture the exact open view before resolving another section's remembered route.
      normalizeRoute();
      rememberCurrentSectionRoute();
      const route = sectionNavigationRoute(section);
      link.setAttribute("href", `#${route}`);
      if (window.location.hash === `#${route}`) return;
      event.preventDefault();
      window.location.hash = `#${route}`;
    });
  });
}

function syncNavIndicator() {
  const nav = document.querySelector(".nav-links");
  const indicator = nav?.querySelector(".nav-indicator");
  const activeLink = nav?.querySelector(".nav-trigger[aria-current='page']");
  if (!nav || !indicator || !activeLink) {
    nav?.classList.remove("has-active-indicator");
    return;
  }
  const navRect = nav.getBoundingClientRect();
  const activeRect = activeLink.getBoundingClientRect();
  const left = activeRect.left - navRect.left + nav.scrollLeft + 12;
  const width = Math.max(0, activeRect.width - 24);
  indicator.style.width = `${width}px`;
  indicator.style.transform = `translateX(${Math.round(left)}px)`;
  nav.classList.add("has-active-indicator");
}

function setActiveNav() {
  rememberCurrentSectionRoute();
  syncSectionNavLinks();
  const currentSection = activeRouteSection(state.route);
  document.querySelectorAll(".nav-trigger").forEach((link) => {
    const section = link.dataset.sectionNav || "";
    const route = link.getAttribute("href")?.replace("#", "") || "/";
    let active = false;
    if (section) {
      active = currentSection === section;
    } else if (route === "/") {
      active = state.route === "/" || state.route.startsWith("/search");
    } else {
      active = state.route === route || state.route.startsWith(`${route}/`) || state.route.startsWith(`${route}?`);
    }
    if (active) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  });
  requestAnimationFrame(syncNavIndicator);
}

function setApp(html) {
  cleanupStickySummaries();
  const app = $("#app");
  const routePath = state.route.split("?")[0];
  const isPrimarySection = ["/athletes", "/events", "/rankings", "/analytics"].includes(routePath);
  app.classList.toggle("home-main-view", state.route === "/");
  app.classList.toggle("primary-section-main-view", isPrimarySection);
  app.classList.toggle("auth-main-view", ["/login", "/register", "/verify-email"].includes(routePath));
  app.innerHTML = html;
  app.focus({ preventScroll: true });
}

function cleanupStickySummaries() {
  stickySummaryCleanups.forEach((cleanup) => cleanup());
  stickySummaryCleanups = [];
}

function stickySummaryTargetSelector(scope) {
  if (scope === "rankings") return ".ranking-filter-stack";
  if (scope === "event-detail") return ".event-classification-sticky-menu";
  return "";
}

function scrollStickySummaryToControls(scope) {
  const selector = stickySummaryTargetSelector(scope);
  const target = selector ? document.querySelector(selector) : null;
  if (!target) {
    scrollToPageTopSmooth();
    return;
  }
  const top = Math.max(0, target.getBoundingClientRect().top + window.scrollY - topbarScrollOffset() - 12);
  window.scrollTo({ top, behavior: "smooth" });
}

function bindStickySummaryControls(root = document) {
  const rootNode = root && typeof root.querySelectorAll === "function" ? root : document;
  const buttons = [...rootNode.querySelectorAll("[data-sticky-summary-scroll]")];
  buttons.forEach((button) => {
    const onClick = () => scrollStickySummaryToControls(button.dataset.stickySummaryScroll || "");
    button.addEventListener("click", onClick);
    stickySummaryCleanups.push(() => button.removeEventListener("click", onClick));
  });
}

function renderStickyContextScrollButton(scope) {
  return `
    <button
      class="context-scroll-button"
      type="button"
      data-sticky-summary-scroll="${escapeHtml(scope)}"
      aria-label="${escapeHtml(t("backToFilters"))}"
    >
      <span aria-hidden="true"></span>
    </button>
  `;
}

function renderContextInStickyHost(hostId, html) {
  const host = $(`#${hostId}`);
  if (!host) return false;
  host.innerHTML = html;
  bindStickySummaryControls(host);
  return true;
}

function pageHeading(titleKey, introKey) {
  return `
    <section class="page-heading">
      <div>
        <p class="eyebrow">LEVERAGE</p>
        <h1>${t(titleKey)}</h1>
        <p>${t(introKey)}</p>
      </div>
    </section>
  `;
}

function disciplinePillClass(label) {
  const value = String(label || "").replace(/\s+/g, " ").trim().toUpperCase();
  if (value === "MAG") return "discipline-mag";
  if (value === "WAG") return "discipline-wag";
  if (["MAG AND WAG", "MAG E WAG", "MAG Y WAG", "MAG ET WAG", "MAG & WAG", "MAG/WAG"].includes(value)) return "discipline-mixed";
  return "";
}

function pillClassName(pill = {}) {
  return ["pill", pill.variant || "", disciplinePillClass(pill.label)].filter(Boolean).join(" ");
}

function renderPill(pill, options = {}) {
  const label = options.escape ? escapeHtml(pill.label) : pill.label;
  return `<span class="${pillClassName(pill)}">${label}</span>`;
}

function isAdminUser() {
  return ["admin", "super_admin"].includes(String(state.currentUser?.role || ""));
}

function displayValue(value) {
  if (value === null || value === undefined || value === "") return t("notAvailable");
  return String(value);
}

function hasDisplayValue(value) {
  return !(value === null || value === undefined || value === "");
}

function mediaUrl(value) {
  if (!value) return "";
  const url = String(value);
  if (/^https?:\/\//i.test(url)) return url;
  try {
    return new URL(url, state.apiBase).toString();
  } catch (_error) {
    return url;
  }
}

function formatDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat(state.language, {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(date);
}

function athleteProfileDisplayName(athlete = {}) {
  const firstName = String(athlete.first_name || "").trim();
  const lastName = String(athlete.last_name || "").trim();
  return [lastName, firstName].filter(Boolean).join(" ") ||
    athleteCardDisplayName(athlete, `${t("athlete")} ${athlete.id}`);
}

function athleteInitials(athlete = {}) {
  const parts = [athlete.last_name, athlete.first_name]
    .map((part) => String(part || "").trim())
    .filter(Boolean);
  return parts.map((part) => part[0]).join("").slice(0, 2).toUpperCase() || "L";
}

function renderDetailField(label, value, options = {}) {
  const isMissing = value === null || value === undefined || value === "";
  const valueHtml = options.html || escapeHtml(displayValue(value));
  return `
    <div class="detail-field ${isMissing ? "is-empty" : ""}">
      <span>${escapeHtml(label)}</span>
      <strong>${valueHtml}</strong>
    </div>
  `;
}

function renderDetailFieldIfPresent(label, value, options = {}) {
  if (!hasDisplayValue(value)) return "";
  return renderDetailField(label, value, options);
}

function entityCard(title, meta, pills = [], href = "", actionHtml = "") {
  const titleContent = href && actionHtml
    ? `<a class="entity-title-link" href="${href}">${title}</a>`
    : title;
  const cardClasses = ["entity-card", href ? "entity-card-clickable" : ""].filter(Boolean).join(" ");
  const content = `
    <article class="${cardClasses}">
      <div class="entity-row">
        <h3>${titleContent}</h3>
        ${actionHtml}
      </div>
      <p class="meta">${meta}</p>
      <div class="pill-row">
        ${pills.map((pill) => renderPill(pill)).join("")}
      </div>
    </article>
  `;
  return href && !actionHtml ? `<a href="${href}">${content}</a>` : content;
}

function favoriteButton(kind, id, isActive) {
  if (!state.currentUser || !id) return "";
  const active = Boolean(isActive);
  const labelKey = kind === "athlete"
    ? (active ? "removeFavoriteAthlete" : "addFavoriteAthlete")
    : (active ? "removeFavoriteEvent" : "addFavoriteEvent");
  return `
    <button
      class="favorite-button ${active ? "is-active" : ""}"
      type="button"
      data-favorite-kind="${kind}"
      data-favorite-id="${Number(id)}"
      aria-pressed="${active}"
      aria-label="${t(labelKey)}"
    >
      <span aria-hidden="true">${active ? "★" : "☆"}</span>
    </button>
  `;
}

function adminToolsIcon() {
  return `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M14.7 6.3a4.2 4.2 0 0 0-5.1 5.1l-5.5 5.5 3 3 5.5-5.5a4.2 4.2 0 0 0 5.1-5.1l-3 3-2.9-2.9 2.9-3.1Z"></path>
    </svg>
  `;
}

function adminToolsButton(kind) {
  if (!isAdminUser()) return "";
  const panelId = kind === "event" ? "eventAdminPanel" : "athleteAdminPanel";
  return `
    <button
      class="favorite-button admin-tools-toggle"
      type="button"
      data-admin-tools-toggle="${panelId}"
      aria-controls="${panelId}"
      aria-expanded="false"
      aria-label="${escapeHtml(t("adminToolsButton"))}"
    >
      ${adminToolsIcon()}
      <span class="sr-only">${escapeHtml(t("adminToolsButton"))}</span>
    </button>
  `;
}

function detailProfileActions(kind, id, isFavorite) {
  const actions = [
    favoriteButton(kind, id, isFavorite),
    adminToolsButton(kind),
  ].filter(Boolean).join("");
  return actions ? `<div class="detail-profile-actions">${actions}</div>` : "";
}

function setFavoriteButtonState(button, isActive) {
  const kind = button.dataset.favoriteKind;
  const labelKey = kind === "athlete"
    ? (isActive ? "removeFavoriteAthlete" : "addFavoriteAthlete")
    : (isActive ? "removeFavoriteEvent" : "addFavoriteEvent");
  button.classList.toggle("is-active", isActive);
  button.setAttribute("aria-pressed", String(isActive));
  button.setAttribute("aria-label", t(labelKey));
  const icon = button.querySelector("span");
  if (icon) icon.textContent = isActive ? "★" : "☆";
}

async function toggleFavorite(kind, id, button) {
  if (!state.currentUser) {
    window.location.hash = "#/login";
    return;
  }
  const numericId = Number(id);
  const idSet = kind === "athlete" ? state.favoriteAthleteIds : state.favoriteEventIds;
  const isActive = idSet.has(numericId) || button.getAttribute("aria-pressed") === "true";
  button.disabled = true;
  try {
    if (kind === "athlete") {
      if (isActive) {
        await sendJson(`/preferences/athletes/follow/${numericId}`, { method: "DELETE" });
        idSet.delete(numericId);
      } else {
        await sendJson("/preferences/athletes/follow", { body: { athlete_id: numericId } });
        idSet.add(numericId);
      }
    } else if (isActive) {
      await sendJson(`/preferences/events/save/${numericId}`, { method: "DELETE" });
      idSet.delete(numericId);
    } else {
      await sendJson("/preferences/events/save", { body: { event_id: numericId } });
      idSet.add(numericId);
    }
    setFavoriteButtonState(button, !isActive);
    if (
      isActive &&
      ((kind === "athlete" && favoritesOnly("athletes") && routeIsListSection("athletes")) ||
        (kind === "event" && favoritesOnly("events") && routeIsListSection("events")))
    ) {
      renderAfterFilterChange();
    }
  } catch (_error) {
    await ensureFavoritesLoaded({ force: true }).catch(() => {});
    setFavoriteButtonState(button, kind === "athlete"
      ? state.favoriteAthleteIds.has(numericId)
      : state.favoriteEventIds.has(numericId));
  } finally {
    button.disabled = false;
  }
}

function bindFavoriteButtons() {
  document.querySelectorAll("[data-favorite-kind]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      toggleFavorite(button.dataset.favoriteKind, button.dataset.favoriteId, button);
    });
  });
}

function bindAdminToolsToggles() {
  document.querySelectorAll("[data-admin-tools-toggle]").forEach((button) => {
    if (button.dataset.adminToolsBound === "true") return;
    button.dataset.adminToolsBound = "true";
    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      const panel = document.getElementById(button.dataset.adminToolsToggle || "");
      if (!panel) return;
      const willOpen = panel.hidden;
      button.setAttribute("aria-expanded", String(willOpen));
      button.classList.toggle("is-open", willOpen);
      if (willOpen) {
        window.clearTimeout(Number(panel.dataset.closeTimer || 0));
        panel.hidden = false;
        panel.classList.remove("is-closing");
        requestAnimationFrame(() => {
          panel.classList.add("is-visible");
          panel.scrollIntoView({ behavior: "smooth", block: "start" });
        });
        return;
      }

      panel.classList.remove("is-visible");
      panel.classList.add("is-closing");
      const closeTimer = window.setTimeout(() => {
        panel.hidden = true;
        panel.classList.remove("is-closing");
        delete panel.dataset.closeTimer;
      }, 220);
      panel.dataset.closeTimer = String(closeTimer);
    });
  });
}

function deleteSavedRankingButton(viewId) {
  return `
    <button
      class="favorite-button delete-button"
      type="button"
      data-delete-ranking-view-id="${Number(viewId)}"
      aria-label="${t("deleteSavedRanking")}"
    >
      <svg class="trash-icon" aria-hidden="true" viewBox="0 0 24 24" focusable="false">
        <path d="M4 7h16"></path>
        <path d="M10 11v6"></path>
        <path d="M14 11v6"></path>
        <path d="M9 7V5h6v2"></path>
        <path d="M6 7l1 14h10l1-14"></path>
      </svg>
    </button>
  `;
}

async function deleteSavedRankingView(viewId, button) {
  button.disabled = true;
  try {
    await sendJson(`/preferences/dashboard-views/${Number(viewId)}`, { method: "DELETE" });
    await renderAccount();
  } catch (_error) {
    button.disabled = false;
  }
}

function bindSavedRankingDeleteButtons() {
  document.querySelectorAll("[data-delete-ranking-view-id]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      deleteSavedRankingView(button.dataset.deleteRankingViewId, button);
    });
  });
}

function errorState() {
  return `<div class="error-state">${t("dataLoadError")}</div>`;
}

function loadingState() {
  return `<div class="empty-state loading">${t("loading")}</div>`;
}

function emptyState() {
  return `<div class="empty-state">${t("noResults")}</div>`;
}

function emptyMessage(message) {
  return `<div class="empty-state">${message}</div>`;
}

function renderLoadMoreButton(scope, label) {
  return `
    <div class="load-more-row">
      <button class="quiet-button load-more-button" type="button" data-load-more="${escapeHtml(scope)}">
        ${escapeHtml(label)}
      </button>
    </div>
  `;
}

function bindLoadMoreButton(scope, onClick) {
  const button = document.querySelector(`[data-load-more="${scope}"]`);
  if (!button || typeof onClick !== "function") return;
  button.addEventListener("click", async () => {
    if (button.disabled) return;
    button.disabled = true;
    button.textContent = t("loading");
    try {
      await onClick();
    } finally {
      if (button.isConnected) {
        button.disabled = false;
      }
    }
  });
}

function mergeUniqueBy(items, nextItems, keyForItem) {
  const merged = [...items];
  const seen = new Set(items.map(keyForItem));
  nextItems.forEach((item) => {
    const key = keyForItem(item);
    if (seen.has(key)) return;
    seen.add(key);
    merged.push(item);
  });
  return merged;
}

function rankingUnavailableMetricEmptyState(metric, selectedApparatuses = []) {
  const normalizedMetric = normalizeRankingMetricValue(metric);
  if (
    selectedApparatuses.includes("VT AVG") &&
    (normalizedMetric === "D_score" || normalizedMetric === "execution_estimate")
  ) {
    return emptyMessage(t("vaultAverageComponentDataUnavailable"));
  }
  if (normalizedMetric === "Penalty") return emptyMessage(t("penaltyDataUnavailable"));
  if (normalizedMetric === "Bonus") return emptyMessage(t("bonusDataUnavailable"));
  return "";
}

function messageState(message) {
  return `<div class="empty-state">${message}</div>`;
}

function searchInputControl(id, value, placeholder) {
  return `
    <div class="search-input-shell">
      <input class="search-input" id="${id}" type="search" autocomplete="off" value="${escapeHtml(value || "")}" placeholder="${escapeHtml(placeholder)}">
      <button class="search-clear-button" type="button" data-search-clear-for="${id}" aria-label="${t("clearSearch")}" ${value ? "" : "hidden"}><span aria-hidden="true">&times;</span></button>
    </div>
  `;
}

function bindSearchClearButtons() {
  document.querySelectorAll("[data-search-clear-for]").forEach((button) => {
    const input = document.getElementById(button.dataset.searchClearFor);
    if (!input) return;
    const syncVisibility = () => {
      button.hidden = !input.value;
    };
    button.addEventListener("click", () => {
      input.value = "";
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.focus();
      syncVisibility();
    });
    input.addEventListener("input", syncVisibility);
    syncVisibility();
  });
}

async function renderHome() {
  setApp(`
    <section class="hero home-hero">
      <div class="hero-copy home-hero-copy">
        <h1 class="home-title" aria-label="${t("heroTitle")}">
          <img class="home-wordmark" src="./assets/leverage-wordmark.png" alt="">
        </h1>
        <p class="home-subtitle">${t("heroSubtitle")}</p>
        <p class="home-body">${t("heroBody")}</p>
        <div class="search-panel">
          <form class="search-form" id="globalSearchForm">
            ${searchInputControl("globalSearchInput", "", t("searchPlaceholder"))}
            <button class="primary-button outline-command-button" type="submit">${t("search")}</button>
            <div class="search-suggestions" id="globalSearchSuggestions" role="listbox" hidden></div>
          </form>
        </div>
      </div>
    </section>

    <section class="section home-data-section" aria-label="${escapeHtml(t("exploreTitle"))}">
      <div class="grid-4 home-data-grid">
        ${featureCard(t("athletesTitle"), t("athletesText"), "#/athletes", { compact: true, showLink: false })}
        ${featureCard(t("eventsTitle"), t("eventsText"), "#/events", { compact: true, showLink: false })}
        ${featureCard(t("rankingsTitle"), t("rankingsText"), "#/rankings", { compact: true, showLink: false })}
        ${featureCard(t("compareTitle"), t("compareText"), "#/analytics", { compact: true, showLink: false })}
      </div>
    </section>

  `);

  $("#globalSearchForm").addEventListener("submit", (event) => {
    event.preventDefault();
    closeSearchSuggestions();
    const query = $("#globalSearchInput").value.trim();
    window.location.hash = query ? `#/search?q=${encodeURIComponent(query)}` : "#/search";
  });
  bindSearchClearButtons();
  setupSearchAutocomplete("#globalSearchInput", "#globalSearchSuggestions");
}

function suggestionMeta(parts) {
  return parts.filter(Boolean).join(" · ");
}

function athleteSuggestion(athlete) {
  return {
    label: athlete.name,
    meta: suggestionMeta([t("athlete"), athlete.country, athlete.discipline]),
    href: `#/athletes/${athlete.id}`,
  };
}

function eventSuggestion(event) {
  return {
    label: event.name,
    meta: suggestionMeta([t("event"), event.location, String(event.year)]),
    href: `#/events/${event.id}`,
  };
}

function resultSuggestion(result) {
  return {
    label: result.athlete_name,
    meta: suggestionMeta([t("matchingResults"), result.event_name, result.apparatus, scoreLabel(result.score)]),
    href: `#/events/${result.event_id}`,
  };
}

function appendUniqueSuggestions(target, source, key) {
  const existing = new Set(target.map(key));
  source.forEach((item) => {
    const value = key(item);
    if (existing.has(value)) return;
    existing.add(value);
    target.push(item);
  });
}

function buildSuggestionItems(data) {
  const athletes = data.athletes || [];
  const events = data.events || [];
  const results = data.results || [];
  const items = [];

  const athleteIds = new Set(athletes.map((athlete) => athlete.id));
  const eventIds = new Set(events.map((event) => event.id));
  const athleteResults = results.filter((result) => athleteIds.has(result.athlete_id));
  const eventResults = results.filter((result) => eventIds.has(result.event_id));
  const otherResults = results.filter((result) => (
    !athleteIds.has(result.athlete_id) && !eventIds.has(result.event_id)
  ));

  if (athletes.length) {
    appendUniqueSuggestions(items, athletes.slice(0, 3).map(athleteSuggestion), (item) => item.href || item.query || item.label);
    appendUniqueSuggestions(items, athleteResults.slice(0, 4).map(resultSuggestion), (item) => `${item.href}-${item.label}-${item.meta}`);
    appendUniqueSuggestions(items, events.slice(0, 2).map(eventSuggestion), (item) => item.href || item.query || item.label);
  } else if (events.length) {
    appendUniqueSuggestions(items, events.slice(0, 3).map(eventSuggestion), (item) => item.href || item.query || item.label);
    appendUniqueSuggestions(items, eventResults.slice(0, 4).map(resultSuggestion), (item) => `${item.href}-${item.label}-${item.meta}`);
    appendUniqueSuggestions(items, athletes.slice(0, 2).map(athleteSuggestion), (item) => item.href || item.query || item.label);
  }

  appendUniqueSuggestions(items, otherResults.slice(0, 3).map(resultSuggestion), (item) => `${item.href}-${item.label}-${item.meta}`);

  if (!items.length) {
    appendUniqueSuggestions(items, results.slice(0, 5).map(resultSuggestion), (item) => `${item.href}-${item.label}-${item.meta}`);
  }
  if (!items.length) {
    appendUniqueSuggestions(items, athletes.slice(0, 3).map(athleteSuggestion), (item) => item.href || item.query || item.label);
    appendUniqueSuggestions(items, events.slice(0, 3).map(eventSuggestion), (item) => item.href || item.query || item.label);
  }

  return items.slice(0, 7);
}

function renderSearchSuggestions(container, items) {
  if (!items.length) {
    container.innerHTML = `<div class="search-suggestion search-suggestion-status">${escapeHtml(t("noResults"))}</div>`;
    container.hidden = false;
    setSearchSuggestionsOpen(container, true, 1);
    setSearchSuggestionsBusy(container, false);
    return;
  }
  container.innerHTML = items.map((item) => `
    <button class="search-suggestion" type="button" role="option" data-suggestion-query="${escapeHtml(item.query || item.label)}" ${item.href ? `data-suggestion-href="${escapeHtml(item.href)}"` : ""}>
      <strong>${escapeHtml(item.label)}</strong>
      <span>${escapeHtml(item.meta)}</span>
    </button>
  `).join("");
  container.hidden = false;
  setSearchSuggestionsOpen(container, true, items.length);
  setSearchSuggestionsBusy(container, false);
  container.querySelectorAll(".search-suggestion").forEach((button) => {
    button.addEventListener("click", () => {
      closeSearchSuggestions();
      if (button.dataset.suggestionHref) {
        window.location.hash = button.dataset.suggestionHref;
        return;
      }
      window.location.hash = `#/search?q=${encodeURIComponent(button.dataset.suggestionQuery || "")}`;
    });
  });
}

function setupSearchAutocomplete(inputSelector, suggestionsSelector) {
  const input = $(inputSelector);
  const suggestions = $(suggestionsSelector);
  if (!input || !suggestions) return;
  input.closest(".search-form")?.addEventListener("click", (event) => {
    event.stopPropagation();
  });
  let debounceTimer;
  const updateSuggestions = () => {
    window.clearTimeout(debounceTimer);
    const query = input.value.trim();
    const requestId = ++searchAutocompleteRequestId;
    if (query.length < 2) {
      suggestions.hidden = true;
      suggestions.innerHTML = "";
      setSearchSuggestionsOpen(suggestions, false);
      setSearchSuggestionsBusy(suggestions, false);
      return;
    }
    const hadStableSuggestions = !suggestions.hidden && Boolean(suggestions.querySelector("button.search-suggestion"));
    setSearchSuggestionsBusy(suggestions, true);
    debounceTimer = window.setTimeout(async () => {
      try {
        const data = await getJson("/search/", { q: query, limit: 5 });
        if (requestId !== searchAutocompleteRequestId) return;
        renderSearchSuggestions(suggestions, buildSuggestionItems(data));
      } catch (_error) {
        if (requestId !== searchAutocompleteRequestId) return;
        setSearchSuggestionsBusy(suggestions, false);
        if (!hadStableSuggestions) {
          suggestions.innerHTML = `<div class="search-suggestion search-suggestion-status">${escapeHtml(t("loadFailed"))}</div>`;
          suggestions.hidden = false;
          setSearchSuggestionsOpen(suggestions, true, 1);
        }
      }
    }, 170);
  };
  input.addEventListener("input", updateSuggestions);
  input.addEventListener("focus", updateSuggestions);
  input.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeSearchSuggestions();
      input.blur();
    }
  });
}

function searchSection(title, items) {
  if (!items.length) return "";
  return `
    <section class="panel search-result-section">
      <div class="section-header">
        <h2>${title}</h2>
      </div>
      <div class="entity-list">${items.join("")}</div>
    </section>
  `;
}

function scoreLabel(value) {
  return value === null || value === undefined ? t("notAvailable") : Number(value).toFixed(3);
}

function timeFiltersForScope(scope) {
  return scope === "events" ? eventTimeFilters() : rankingTimeFilters();
}

function dateWheelOptionIsDisabled(scope, field, unit, optionValue, currentValue) {
  if (field !== "endDate") return false;
  const filters = timeFiltersForScope(scope);
  const startDate = parseLocalDate(filters.startDate);
  if (!startDate) return false;
  const parts = datePickerParts(currentValue);
  const value = Number(optionValue);
  const startYear = startDate.getFullYear();
  const startMonth = startDate.getMonth() + 1;
  const startDay = startDate.getDate();

  if (unit === "year") return value < startYear;
  if (parts.year < startYear) return true;
  if (parts.year > startYear) return false;
  if (unit === "month") return value < startMonth;
  if (parts.month < startMonth) return true;
  if (parts.month > startMonth) return false;
  if (unit === "day") return value < startDay;
  return false;
}

function dateWheelTodayOptionIsDisabled(scope, field) {
  if (field !== "endDate") return false;
  const filters = timeFiltersForScope(scope);
  return isoDateIsBefore(formatLocalIso(TODAY), filters.startDate);
}

function renderDateWheelColumn(scope, field, unit, label, options, selectedValue, currentValue, extraOptions = "") {
  return `
    <div class="ranking-date-wheel-column" aria-label="${escapeHtml(label)}">
      <span class="ranking-date-wheel-label">${escapeHtml(label)}</span>
      <div class="ranking-date-wheel-options">
        ${options.map((option) => {
          const disabled = dateWheelOptionIsDisabled(scope, field, unit, option.value, currentValue);
          return `
            <button
              class="ranking-date-wheel-option"
              type="button"
              data-date-wheel-scope="${scope}"
              data-date-wheel-field="${field}"
              data-date-wheel-unit="${unit}"
              data-date-wheel-value="${option.value}"
              aria-pressed="${String(option.value === selectedValue)}"
              ${disabled ? "disabled" : ""}
            >${escapeHtml(option.label)}</button>
          `;
        }).join("")}
        ${extraOptions}
      </div>
    </div>
  `;
}

function renderDateWheelTodayOption(scope, field) {
  const disabled = dateWheelTodayOptionIsDisabled(scope, field);
  return `
    <button
      class="ranking-date-wheel-option ranking-date-wheel-today-option"
      type="button"
      data-date-wheel-today-scope="${scope}"
      data-date-wheel-today-field="${field}"
      aria-pressed="false"
      ${disabled ? "disabled" : ""}
    >${escapeHtml(t("today"))}</button>
  `;
}

function scrollDateWheelColumnToActive(column) {
  const activeOption = column.querySelector("[aria-pressed='true']");
  if (!activeOption) return;
  column.scrollTop = activeOption.offsetTop - (column.clientHeight / 2) + (activeOption.clientHeight / 2);
}

function scrollDateWheelToActive(details) {
  if (!details) return;
  window.requestAnimationFrame(() => {
    details.querySelectorAll(".ranking-date-wheel-options").forEach(scrollDateWheelColumnToActive);
  });
}

function activeDateWheel(scope) {
  return scope === "events" ? state.openEventDateWheel : state.openRankingDateWheel;
}

function setActiveDateWheel(scope, field) {
  if (scope === "events") {
    state.openEventDateWheel = field;
  } else {
    state.openRankingDateWheel = field;
  }
}

function timeFilterIsOpen(scope) {
  return scope === "events" ? state.openEventTimeFilter : state.openRankingTimeFilter;
}

function setTimeFilterOpen(scope, isOpen) {
  if (scope === "events") {
    state.openEventTimeFilter = isOpen;
    if (!isOpen) {
      state.openEventDateWheel = "";
    }
  } else {
    state.openRankingTimeFilter = isOpen;
    if (!isOpen) {
      state.openRankingDateWheel = "";
    }
  }
}

function renderDateWheel(scope, field, label, value, displayValue = "") {
  const parts = datePickerParts(value);
  const inputValue = displayValue || formatDateInputValue(value);
  const defaultInputValue = formatDateInputValue(defaultDatePickerIso());
  const placeholder = inputValue ? t("datePlaceholder") : defaultInputValue;
  const years = Array.from(
    { length: DATE_PICKER_END_YEAR - DATE_PICKER_START_YEAR + 1 },
    (_, index) => {
      const year = DATE_PICKER_START_YEAR + index;
      return { value: year, label: String(year) };
    },
  );
  const months = Array.from({ length: 12 }, (_, index) => {
    const month = index + 1;
    return { value: month, label: monthShortLabel(month) };
  });
  const days = Array.from({ length: daysInMonth(parts.year, parts.month) }, (_, index) => {
    const day = index + 1;
    return { value: day, label: String(day) };
  });
  return `
    <details class="ranking-date-wheel" data-date-wheel-scope="${scope}" data-date-wheel="${field}" ${activeDateWheel(scope) === field ? "open" : ""}>
      <summary class="ranking-date-wheel-summary">
        <span>${escapeHtml(label)}</span>
        <input
          class="ranking-date-wheel-input"
          type="text"
          inputmode="numeric"
          autocomplete="off"
          maxlength="10"
          placeholder="${escapeHtml(placeholder)}"
          value="${escapeHtml(inputValue)}"
          aria-label="${escapeHtml(label)}"
          data-date-wheel-default-value="${String(!inputValue)}"
          data-date-wheel-text-scope="${scope}"
          data-date-wheel-text-field="${field}"
        >
      </summary>
      <div class="ranking-date-wheel-panel">
        ${renderDateWheelColumn(scope, field, "day", t("dateDay"), days, parts.day, value || defaultDatePickerIso())}
        ${renderDateWheelColumn(scope, field, "month", t("dateMonth"), months, parts.month, value || defaultDatePickerIso())}
        ${renderDateWheelColumn(scope, field, "year", t("dateYear"), years, parts.year, value || defaultDatePickerIso(), renderDateWheelTodayOption(scope, field))}
      </div>
    </details>
  `;
}

function renderRankingDateWheel(field, label, value, displayValue = "") {
  return renderDateWheel("rankings", field, label, value, displayValue);
}

function renderEventDateWheel(field, label, value, displayValue = "") {
  return renderDateWheel("events", field, label, value, displayValue);
}

function componentValueLabel(value, status) {
  if (value !== null && value !== undefined) return Number(value).toFixed(3);
  if (status === "not_applicable") return t("notApplicable");
  return t("notAvailable");
}

function dScoreLabel(value, status) {
  if (value !== null && value !== undefined) return Number(value).toFixed(1);
  if (status === "not_applicable") return t("notApplicable");
  return t("notAvailable");
}

function rankingMetricValueLabel(entry, metric = rankingSortBy()) {
  if (metric === "D_score") return dScoreLabel(entry.D_score);
  if (metric === "execution_estimate") return scoreLabel(entry.execution_estimate);
  if (metric === "Penalty") return componentValueLabel(entry.Penalty, entry.penalty_status);
  if (metric === "Bonus") return componentValueLabel(entry.Bonus, entry.bonus_status);
  return scoreLabel(entry.score);
}

function rankingIsAaEntry(entry) {
  return (entry.apparatus || "AA") === "AA";
}

function leaderboardPrimaryValue(entry, selectedMetric = rankingSortBy()) {
  if (rankingIsAaEntry(entry) && selectedMetric === "score") return scoreLabel(entry.score);
  return rankingMetricValueLabel(entry, selectedMetric);
}

function vaultAwareApparatusLabel(apparatus, vtAttempt, showVaultAttempts = false) {
  const value = apparatus || "AA";
  if (value !== "VT") return value;
  if (!showVaultAttempts) return "VT";
  if (Number(vtAttempt) === 1) return "VT 1";
  if (Number(vtAttempt) === 2) return "VT 2";
  return "VT";
}

function aaScoreComponentLabel(component) {
  if (component.apparatus === "VT") {
    return Number(component.vt_attempt) === 2 ? "VT 2" : "VT";
  }
  return component.apparatus || t("notAvailable");
}

function vaultScoreComponentLabel(component) {
  if (Number(component.vt_attempt) === 1) return "VT 1";
  if (Number(component.vt_attempt) === 2) return "VT 2";
  return "VT";
}

function scoreCompositionMetricIsExcluded(metric, excludedMetric = "") {
  if (!excludedMetric || excludedMetric === "score") return false;
  if (metric === "execution_estimate") {
    return excludedMetric === "execution_estimate" || excludedMetric === "E_score";
  }
  return metric === excludedMetric;
}

function scoreCompositionValues(item, excludedMetric = "") {
  const eLabel = item.execution_estimate === null || item.execution_estimate === undefined
    ? componentValueLabel(item.E_score, item.e_score_status)
    : scoreLabel(item.execution_estimate);
  const values = [
    { metric: "D_score", label: "D", value: dScoreLabel(item.D_score) },
    { metric: "execution_estimate", label: "E est.", value: eLabel },
    { metric: "Penalty", label: "P", value: componentValueLabel(item.Penalty, item.penalty_status) },
    { metric: "Bonus", label: "B", value: componentValueLabel(item.Bonus, item.bonus_status) },
  ].filter((component) => !scoreCompositionMetricIsExcluded(component.metric, excludedMetric));
  if (excludedMetric && excludedMetric !== "score") {
    return [
      { metric: "score", label: "Final Score", value: scoreLabel(item.score) },
      ...values,
    ];
  }
  return values;
}

function leaderboardPrimaryLabel(entry, selectedMetric = rankingSortBy()) {
  if (rankingIsAaEntry(entry) && selectedMetric === "score") return "Final Score";
  return rankingMetricLabel(selectedMetric);
}

function leaderboardScoreChip(label, value, options = {}) {
  const text = value === null || value === undefined ? t("notAvailable") : String(value);
  const unavailable = text === t("notAvailable") || text === t("notApplicable");
  return `
    <span class="leaderboard-score-chip${options.primary ? " is-primary" : ""}${unavailable ? " is-muted" : ""}">
      <strong>${escapeHtml(label)}</strong>
      <span>${escapeHtml(text)}</span>
    </span>
  `;
}

function leaderboardScoreChipList(chips = []) {
  return chips
    .filter((chip) => chip && hasDisplayValue(chip.label))
    .map((chip) => leaderboardScoreChip(chip.label, chip.value, chip))
    .join("");
}

function leaderboardValueIsUnavailable(value) {
  const text = value === null || value === undefined ? t("notAvailable") : String(value);
  return text === t("notAvailable") || text === t("notApplicable");
}

function leaderboardPrimarySecondaryChips() {
  return "";
}

function leaderboardPrimaryDetailRows(entry, selectedMetric = rankingSortBy()) {
  if (!rankingIsAaEntry(entry)) return [];
  if (selectedMetric === "score") {
    if (entry.D_score === null || entry.D_score === undefined) return [];
    return [{ label: "D Score AA", value: dScoreLabel(entry.D_score) }];
  }
  const finalScore = scoreLabel(entry.score);
  if (leaderboardValueIsUnavailable(finalScore)) return [];
  return [{ label: "Final Score", value: finalScore }];
}

function componentScoreDataIsVisible(value, status) {
  return value !== null && value !== undefined || status === "not_available";
}

function combineUnavailablePenaltyBonus(rows = []) {
  const unavailableValue = t("notAvailable");
  const penaltyIndex = rows.findIndex((row) => row.metric === "Penalty" && row.value === unavailableValue);
  const bonusIndex = rows.findIndex((row) => row.metric === "Bonus" && row.value === unavailableValue);
  if (penaltyIndex < 0 || bonusIndex < 0) return rows;
  const insertionIndex = Math.min(penaltyIndex, bonusIndex);
  const compactRows = rows.filter((row) => row.metric !== "Penalty" && row.metric !== "Bonus");
  compactRows.splice(insertionIndex, 0, {
    metric: "PenaltyBonus",
    label: "P / B",
    value: unavailableValue,
  });
  return compactRows;
}

function aaLeaderboardComponentValue(component, selectedMetric = rankingSortBy()) {
  if (!component) return t("notAvailable");
  if (selectedMetric === "D_score") return dScoreLabel(component.D_score);
  if (selectedMetric === "execution_estimate") {
    return component.execution_estimate === null || component.execution_estimate === undefined
      ? componentValueLabel(component.E_score, component.e_score_status)
      : scoreLabel(component.execution_estimate);
  }
  if (selectedMetric === "Penalty") return componentValueLabel(component.Penalty, component.penalty_status);
  if (selectedMetric === "Bonus") return componentValueLabel(component.Bonus, component.bonus_status);
  return scoreLabel(component.score);
}

function aaLeaderboardComponentDetails(component, selectedMetric = rankingSortBy()) {
  if (!component) return [];
  const eValue = component.execution_estimate === null || component.execution_estimate === undefined
    ? componentValueLabel(component.E_score, component.e_score_status)
    : scoreLabel(component.execution_estimate);
  const rows = [
    { metric: "score", label: "Final Score", value: scoreLabel(component.score) },
    { metric: "D_score", label: "D Score", value: dScoreLabel(component.D_score) },
    { metric: "execution_estimate", label: "E Score", value: eValue },
  ];
  if (componentScoreDataIsVisible(component.Penalty, component.penalty_status)) {
    rows.push({ metric: "Penalty", label: "P", value: componentValueLabel(component.Penalty, component.penalty_status) });
  }
  if (componentScoreDataIsVisible(component.Bonus, component.bonus_status)) {
    rows.push({ metric: "Bonus", label: "B", value: componentValueLabel(component.Bonus, component.bonus_status) });
  }
  const visibleRows = rows.filter((row) => {
    if (selectedMetric === "score") return row.metric !== "score";
    return !scoreCompositionMetricIsExcluded(row.metric, selectedMetric);
  });
  return combineUnavailablePenaltyBonus(visibleRows);
}

function aaLeaderboardScoreCells(entry, selectedMetric = rankingSortBy()) {
  const apparatusOrder = ATHLETE_ANALYTICS_APPARATUS_ORDER[entry.discipline] || ATHLETE_ANALYTICS_APPARATUS_ORDER.MAG;
  const componentsByApparatus = new Map();
  (entry.apparatus_scores || []).forEach((component) => {
    componentsByApparatus.set(aaScoreComponentLabel(component), component);
  });
  return apparatusOrder.map((apparatus) => {
    const component = componentsByApparatus.get(apparatus);
    return {
      label: apparatus,
      value: aaLeaderboardComponentValue(component, selectedMetric),
      muted: !component || leaderboardValueIsUnavailable(aaLeaderboardComponentValue(component, selectedMetric)),
      detailRows: aaLeaderboardComponentDetails(component, selectedMetric),
    };
  });
}

function vaultAverageLeaderboardScoreCells(entry) {
  const componentsByAttempt = new Map();
  (entry.apparatus_scores || []).forEach((component) => {
    componentsByAttempt.set(Number(component.vt_attempt || 0), component);
  });
  return [1, 2].map((attempt) => {
    const component = componentsByAttempt.get(attempt);
    return {
      label: `VT ${attempt}`,
      value: component ? scoreLabel(component.score) : t("notAvailable"),
      muted: !component || component.score === null || component.score === undefined,
      detailRows: component ? aaLeaderboardComponentDetails(component, "score") : [],
    };
  });
}

function standardLeaderboardScoreCells(entry, selectedMetric = rankingSortBy()) {
  return scoreCompositionValues(entry, selectedMetric).map(({ label, value }) => ({
    label,
    value,
    muted: leaderboardValueIsUnavailable(value),
  }));
}

function leaderboardScoreCells(entry, selectedMetric = rankingSortBy()) {
  if (rankingIsAaEntry(entry)) {
    return aaLeaderboardScoreCells(entry, selectedMetric);
  }
  if (entry.apparatus === "VT AVG") {
    return vaultAverageLeaderboardScoreCells(entry);
  }
  return standardLeaderboardScoreCells(entry, selectedMetric);
}

function renderLeaderboardExpandedDetails(rows = [], className = "") {
  const visibleRows = rows.filter((item) => item && hasDisplayValue(item.label));
  if (!visibleRows.length) return "";
  return `
    <span class="leaderboard-score-details ${className}" aria-hidden="true">
      ${visibleRows.map((item) => `
        <span class="leaderboard-score-detail-row">
          <strong>${escapeHtml(item.label)}</strong>
          <span>${escapeHtml(item.value)}</span>
        </span>
      `).join("")}
    </span>
  `;
}

function renderLeaderboardScoreTable(cells = []) {
  const visibleCells = cells.filter((cell) => cell && hasDisplayValue(cell.label));
  if (!visibleCells.length) {
    return `<span class="leaderboard-data-muted">${escapeHtml(t("apparatusScoresUnavailable"))}</span>`;
  }
  return `
    <span class="leaderboard-score-table" style="--score-column-count: ${visibleCells.length};">
      ${visibleCells.map((cell) => {
        const value = cell.value === null || cell.value === undefined ? t("notAvailable") : String(cell.value);
        const muted = cell.muted || leaderboardValueIsUnavailable(value);
        const subValues = (cell.subValues || []).filter((item) => item && hasDisplayValue(item.label));
        const detailRows = (cell.detailRows || []).filter((item) => item && hasDisplayValue(item.label));
        return `
          <span class="leaderboard-score-cell${muted ? " is-muted" : ""}${detailRows.length ? " has-details" : ""}">
            <strong>${escapeHtml(cell.label)}</strong>
            <span class="leaderboard-score-value">${escapeHtml(value)}</span>
            ${subValues.length ? `
              <small>${subValues.map((item) => `${escapeHtml(item.label)} ${escapeHtml(item.value)}`).join(" · ")}</small>
            ` : ""}
            ${renderLeaderboardExpandedDetails(detailRows)}
          </span>
        `;
      }).join("")}
    </span>
  `;
}

function rankingLeaderboardTags(entry, options = {}) {
  if (options.showTags === false) return "";
  const tags = [
    ...(options.showApparatus === false ? [] : [vaultAwareApparatusLabel(entry.apparatus, entry.vt_attempt, options.showVaultAttempts)]),
    ...(entry.discipline ? [displayEnumValue(entry.discipline)] : []),
    ...(entry.category ? [eventClassificationCategoryLabel(entry.category)] : []),
    ...(entry.format ? [displayEnumValue(entry.format)] : []),
    ...(entry.round ? [displayEnumValue(entry.round)] : []),
    ...(entry.day ? [`${t("day")} ${entry.day}`] : []),
    ...(options.showYear && entry.year ? [String(entry.year)] : []),
  ].filter(Boolean);
  return tags.length
    ? `<span class="leaderboard-tags">${tags.map((label) => renderPill({ label }, { escape: true })).join("")}</span>`
    : "";
}

function leaderboardAthleteHref(href, options = {}) {
  const returnContext = options.returnContext || "";
  if (!returnContext) return href;
  const [path, query = ""] = String(href).split("?");
  const params = new URLSearchParams(query);
  params.set("from", returnContext);
  const expectedReturnSection = returnContext === "ranking" ? "rankings" : "events";
  if (routeSection(state.route) === expectedReturnSection) {
    params.set("return_to", state.route);
  }
  if (returnContext === "classification" && options.returnEventId) {
    params.set("event_id", String(options.returnEventId));
  }
  return `${path}?${params.toString()}`;
}

function renderLeaderboardList(entries = [], options = {}) {
  const selectedMetric = options.selectedMetric || rankingSortBy();
  return `
    <div class="leaderboard-list ${options.className || ""}">
      ${entries.map((entry) => {
        const rank = options.rankForEntry ? options.rankForEntry(entry) : entry.computed_rank;
        const primaryValue = leaderboardPrimaryValue(entry, selectedMetric);
        const meta = (options.metaForEntry ? options.metaForEntry(entry) : [])
          .filter(Boolean)
          .join(" · ");
        const baseHref = options.hrefForEntry ? options.hrefForEntry(entry) : `#/athletes/${entry.athlete_id}`;
        const href = leaderboardAthleteHref(baseHref, options);
        const secondaryScores = leaderboardPrimarySecondaryChips(entry, selectedMetric);
        const primaryDetailRows = leaderboardPrimaryDetailRows(entry, selectedMetric);
        const scoreCells = leaderboardScoreCells(entry, selectedMetric);
        const scoreTable = renderLeaderboardScoreTable(scoreCells);
        const expandable = (rankingIsAaEntry(entry) || entry.apparatus === "VT AVG") && (
          primaryDetailRows.length || scoreCells.some((cell) => (cell.detailRows || []).length)
        );
        const rowContent = `
            <span class="leaderboard-rank">#${escapeHtml(String(rank || ""))}</span>
            <span class="leaderboard-athlete">
              ${expandable
                ? `<a class="leaderboard-athlete-link" href="${escapeHtml(href)}">${escapeHtml(entry.athlete_name || t("athlete"))}</a>`
                : `<strong>${escapeHtml(entry.athlete_name || t("athlete"))}</strong>`}
              ${meta ? `<span>${escapeHtml(meta)}</span>` : ""}
            </span>
            <span class="leaderboard-primary-score${primaryDetailRows.length ? " has-details" : ""}">
              <strong>${escapeHtml(primaryValue)}</strong>
              <span class="leaderboard-primary-label">${escapeHtml(leaderboardPrimaryLabel(entry, selectedMetric))}</span>
              ${secondaryScores}
              ${renderLeaderboardExpandedDetails(primaryDetailRows, "leaderboard-primary-details")}
            </span>
            <span class="leaderboard-detail-row">
              ${rankingLeaderboardTags(entry, options)}
              ${scoreTable}
            </span>
        `;
        if (expandable) {
          return `
            <div
              class="leaderboard-row is-expandable"
              role="button"
              tabindex="0"
              aria-expanded="false"
              data-leaderboard-expandable-row
            >${rowContent}</div>
          `;
        }
        return `<a class="leaderboard-row" href="${escapeHtml(href)}">${rowContent}</a>`;
      }).join("")}
    </div>
  `;
}

function setLeaderboardRowExpanded(row, expanded) {
  row.classList.toggle("is-expanded", expanded);
  row.setAttribute("aria-expanded", String(expanded));
  row.querySelectorAll(".leaderboard-score-details").forEach((details) => {
    details.setAttribute("aria-hidden", String(!expanded));
  });
}

function toggleLeaderboardRow(row) {
  setLeaderboardRowExpanded(row, row.getAttribute("aria-expanded") !== "true");
}

function bindLeaderboardExpansionEvents() {
  document.addEventListener("click", (event) => {
    const row = event.target.closest?.("[data-leaderboard-expandable-row]");
    if (!row || event.target.closest("a, button, input, select, textarea")) return;
    toggleLeaderboardRow(row);
  });
  document.addEventListener("keydown", (event) => {
    const row = event.target.closest?.("[data-leaderboard-expandable-row]");
    if (!row || event.target !== row || !["Enter", " "].includes(event.key)) return;
    event.preventDefault();
    toggleLeaderboardRow(row);
  });
}

function searchResultCard(result) {
  const pills = [
    { label: `${t("score")} ${scoreLabel(result.score)}`, variant: "brand" },
    ...(result.apparatus ? [{ label: result.apparatus }] : []),
    { label: result.discipline },
    ...(result.country ? [{ label: result.country }] : []),
  ];
  const meta = [result.event_name, result.date || String(result.year)].filter(Boolean).join(" · ");
  return entityCard(result.athlete_name, meta, pills, `#/events/${result.event_id}`);
}

function renderGlobalSearchResults(data) {
  const structuredResultSearch = Boolean(data.structured_result_search);
  if (!data.total_count) {
    return messageState(t("noGlobalSearchResults"));
  }
  const athleteItems = data.athletes.map((athlete) => {
    const pills = [
      { label: athlete.discipline, variant: "brand" },
      ...(athlete.country ? [{ label: athlete.country }] : []),
      { label: resultLabel(athlete.result_count) },
    ];
    return entityCard(athlete.name, athlete.country || t("country"), pills, `#/athletes/${athlete.id}`);
  });
  const eventItems = data.events.map((event) => {
    const pills = [
      { label: displayEnumValue(event.discipline), variant: "brand" },
      { label: displayEnumValue(event.category) },
      { label: resultLabel(event.result_count) },
    ];
    const meta = [event.location, formatDateRange(event) || String(event.year)].filter(Boolean).join(" · ");
    return entityCard(event.name, meta, pills, `#/events/${event.id}`);
  });
  const resultItems = data.results.map(searchResultCard);
  const relatedResultItems = (data.related_results || []).map(searchResultCard);
  if (structuredResultSearch) {
    if (!data.results.length) {
      return `
        <div class="search-results">
          ${messageState(t("noStructuredSearchResults"))}
          ${searchSection(t("relatedResults"), relatedResultItems)}
          ${searchSection(t("matchingAthletes"), athleteItems)}
          ${searchSection(t("matchingEvents"), eventItems)}
        </div>
      `;
    }
    return `
      <div class="search-results">
        ${searchSection(t("filteredResults"), resultItems)}
      </div>
    `;
  }
  return `
    <div class="search-results">
      ${searchSection(t("matchingAthletes"), athleteItems)}
      ${searchSection(t("matchingEvents"), eventItems)}
      ${searchSection(t("matchingResults"), resultItems)}
    </div>
  `;
}

async function renderGlobalSearch() {
  const params = currentParams();
  const query = params.get("q") || "";
  setApp(`
    <div class="detail-topbar">
      <a class="quiet-button detail-back-button" href="#/">${escapeHtml(t("backToHome"))}</a>
    </div>
    ${pageHeading("globalSearchHeading", "globalSearchIntro")}
    <form class="search-form search-page-form" id="globalSearchPageForm">
      ${searchInputControl("globalSearchPageInput", query, t("searchPlaceholder"))}
      <button class="primary-button outline-command-button" type="submit">${t("search")}</button>
      <div class="search-suggestions" id="globalSearchPageSuggestions" role="listbox" hidden></div>
    </form>
    ${query ? `<div id="globalSearchResults">${loadingState()}</div>` : ""}
  `);
  $("#globalSearchPageForm").addEventListener("submit", (event) => {
    event.preventDefault();
    closeSearchSuggestions();
    const nextQuery = $("#globalSearchPageInput").value.trim();
    window.location.hash = nextQuery ? `#/search?q=${encodeURIComponent(nextQuery)}` : "#/search";
  });
  bindSearchClearButtons();
  setupSearchAutocomplete("#globalSearchPageInput", "#globalSearchPageSuggestions");
  if (!query) return;
  try {
    trackSiteSearch(query);
    const results = await getJson("/search/", { q: query, limit: 8 });
    $("#globalSearchResults").innerHTML = renderGlobalSearchResults(results);
  } catch (error) {
    $("#globalSearchResults").innerHTML = errorState(error);
  }
}

function featureCard(title, text, href, options = {}) {
  const classes = ["feature-card", options.compact ? "feature-card-compact" : ""].filter(Boolean).join(" ");
  const showLink = options.showLink !== false;
  return `
    <a class="${classes}" href="${href}">
      <div>
        <h3>${title}</h3>
        <p>${text}</p>
      </div>
      ${showLink ? `<span class="feature-link">${t("open")}</span>` : ""}
    </a>
  `;
}

function currentFilterScope() {
  if (state.route.startsWith("/athletes")) return "athletes";
  if (state.route.startsWith("/events")) return "events";
  if (state.route.startsWith("/rankings")) return "rankings";
  return "global";
}

function scopedFilters(scope = currentFilterScope()) {
  if (!state.filters[scope]) {
    state.filters[scope] = {};
  }
  return state.filters[scope];
}

function filterValues(type, scope = currentFilterScope()) {
  const value = scopedFilters(scope)[type];
  if (Array.isArray(value)) return value;
  return value ? [value] : [];
}

function rankingScoringCycleValues(values = filterValues("scoringCycle", "rankings")) {
  const rawValues = Array.isArray(values) ? values : (values ? [values] : []);
  if (rawValues.includes("all")) return [...SCORING_CYCLE_FILTERS];
  return [...new Set(rawValues.filter((value) => SCORING_CYCLE_FILTERS.includes(value)))];
}

const EXCLUSIVE_APPARATUS_FILTERS = new Set(["AA", "VT AVG"]);

function normalizeExclusiveApparatusSelection(values = []) {
  const uniqueValues = [...new Set(values.filter(Boolean))];
  const exclusiveValue = uniqueValues.find((value) => EXCLUSIVE_APPARATUS_FILTERS.has(value));
  if (!uniqueValues.length) return ["AA"];
  if (!exclusiveValue) return uniqueValues;
  return [exclusiveValue];
}

function toggleExclusiveApparatusSelection(values = [], value) {
  const uniqueValues = [...new Set(values.filter(Boolean))];
  if (uniqueValues.includes(value)) {
    return normalizeExclusiveApparatusSelection(uniqueValues.filter((item) => item !== value));
  }
  if (EXCLUSIVE_APPARATUS_FILTERS.has(value)) return [value];
  return normalizeExclusiveApparatusSelection([...uniqueValues.filter((item) => !EXCLUSIVE_APPARATUS_FILTERS.has(item)), value]);
}

function multiFilterParam(type, scope = currentFilterScope()) {
  return filterValues(type, scope).join(",");
}

function singleFilterParam(type, scope = currentFilterScope()) {
  const values = filterValues(type, scope);
  return values.length === 1 ? values[0] : "";
}

function filterIsActive(type, value, scope = currentFilterScope(), activeValue = scopedFilters(scope)[type]) {
  if (scope === "rankings" && type === "scoringCycle") {
    const values = rankingScoringCycleValues(activeValue);
    return values.includes(value);
  }
  return Array.isArray(activeValue) ? activeValue.includes(value) : activeValue === value;
}

function rankingDiscipline() {
  return singleFilterParam("discipline", "rankings") || "MAG";
}

function normalizeRankingMetricValue(value) {
  return value === "E_score" ? "execution_estimate" : (value || "score");
}

function rankingSortBy() {
  const selectedMetric = normalizeRankingMetricValue(singleFilterParam("sortBy", "rankings"));
  return RANKING_METRIC_FILTERS.some((metric) => metric.value === selectedMetric) ? selectedMetric : "score";
}

function rankingMetricLabel(value = rankingSortBy()) {
  return RANKING_METRIC_FILTERS.find((metric) => metric.value === value)?.label || "Final Score";
}

function rankingApparatusFilters() {
  return RANKING_APPARATUS_BY_DISCIPLINE[rankingDiscipline()] || [];
}

function rankingApparatusValues() {
  const allowedApparatuses = rankingApparatusFilters();
  const normalized = normalizeExclusiveApparatusSelection(
    filterValues("apparatus", "rankings").filter((value) => allowedApparatuses.includes(value)),
  );
  scopedFilters("rankings").apparatus = normalized;
  return normalized;
}

function favoritesOnly(scope) {
  return Boolean(state.currentUser && singleFilterParam("favoritesOnly", scope) === "true");
}

function eventTimeFilters() {
  const filters = scopedFilters("events");
  return {
    startDate: filters.startDate || "",
    endDate: filters.endDate || "",
    startPeriod: filters.startPeriod || "",
    endPeriod: filters.endPeriod || "",
  };
}

function eventHasTimeFilter() {
  const filters = eventTimeFilters();
  return Boolean(filters.startDate || filters.endDate);
}

function eventMatchesTimeFilter(event) {
  const filters = eventTimeFilters();
  if (!filters.startDate && !filters.endDate) return true;
  const eventStart = parseLocalDate(event.start_date || event.end_date);
  const eventEnd = parseLocalDate(event.end_date || event.start_date);
  if (!eventStart && !eventEnd) return false;
  const filterStart = parseLocalDate(filters.startDate);
  const filterEnd = parseLocalDate(filters.endDate);
  if (filterStart && eventEnd && eventEnd < filterStart) return false;
  if (filterEnd && eventStart && eventStart > filterEnd) return false;
  return true;
}

function routeIsListSection(scope) {
  if (scope === "athletes") return state.route === "/athletes" || state.route.startsWith("/athletes?");
  if (scope === "events") return state.route === "/events" || state.route.startsWith("/events?");
  return false;
}

function filterFavoriteAthletes(athletes) {
  if (!favoritesOnly("athletes")) return athletes;
  return athletes.filter((athlete) => state.favoriteAthleteIds.has(Number(athlete.id)));
}

function filterFavoriteEvents(events) {
  if (!favoritesOnly("events")) return events;
  return events.filter((event) => event.id && state.favoriteEventIds.has(Number(event.id)));
}

function normalizedText(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function textMatchesQuery(value, query) {
  const terms = normalizedText(query).split(/\s+/).filter(Boolean);
  if (!terms.length) return true;
  const haystack = normalizedText(value);
  return terms.every((term) => haystack.includes(term));
}

function eventValueIncludesFilter(value, filters) {
  if (!filters.length) return true;
  const text = String(value || "");
  return filters.some((filter) => text === filter || text.includes(filter));
}

function favoriteAthleteDetailMatches(detail, query) {
  const athlete = detail.athlete || {};
  const disciplineFilters = filterValues("discipline", "athletes");
  if (disciplineFilters.length && !disciplineFilters.includes(athlete.discipline)) {
    return false;
  }
  return textMatchesQuery([
    athlete.first_name,
    athlete.last_name,
    `${athlete.first_name || ""} ${athlete.last_name || ""}`,
    `${athlete.last_name || ""} ${athlete.first_name || ""}`,
    athlete.country,
    athlete.discipline,
    detail.athlete_id,
  ].join(" "), query);
}

function athleteSortText(value) {
  return normalizedText(value).trim();
}

function athleteLastNameSortPriority(athlete = {}) {
  const lastName = athleteSortText(athlete.last_name);
  if (!lastName) return 2;
  if (lastName.startsWith("(")) return 1;
  return 0;
}

function compareAthletesByName(leftAthlete = {}, rightAthlete = {}) {
  const priorityCompare = athleteLastNameSortPriority(leftAthlete) - athleteLastNameSortPriority(rightAthlete);
  if (priorityCompare) {
    return priorityCompare;
  }
  const leftName = `${leftAthlete.last_name || ""} ${leftAthlete.first_name || ""}`.trim();
  const rightName = `${rightAthlete.last_name || ""} ${rightAthlete.first_name || ""}`.trim();
  return athleteSortText(leftName).localeCompare(athleteSortText(rightName));
}

function compareAthletesForCurrentSort(leftAthlete = {}, rightAthlete = {}) {
  const nameCompare = compareAthletesByName(leftAthlete, rightAthlete);
  if (state.athleteSortMode !== "country") {
    return nameCompare || Number(leftAthlete.id || 0) - Number(rightAthlete.id || 0);
  }
  const leftCountry = athleteSortText(leftAthlete.country);
  const rightCountry = athleteSortText(rightAthlete.country);
  if (!leftCountry && rightCountry) return 1;
  if (leftCountry && !rightCountry) return -1;
  const countryCompare = leftCountry.localeCompare(rightCountry);
  return countryCompare || nameCompare || Number(leftAthlete.id || 0) - Number(rightAthlete.id || 0);
}

function sortFavoriteAthleteDetails(details) {
  return [...details].sort((left, right) => (
    compareAthletesForCurrentSort(left.athlete || {}, right.athlete || {})
  ));
}

function favoriteEventDetailMatches(detail, query) {
  const event = detail.event || {};
  if (!eventValueIncludesFilter(event.discipline, filterValues("discipline", "events"))) return false;
  if (!eventValueIncludesFilter(event.category, filterValues("category", "events"))) return false;
  if (filterValues("level", "events").length && !filterValues("level", "events").includes(event.level)) return false;
  if (!eventMatchesTimeFilter(event)) return false;
  return textMatchesQuery([
    event.name,
    event.year,
    event.location,
    event.venue,
    event.discipline,
    event.category,
    event.level,
    detail.event_id,
  ].join(" "), query);
}

async function getFavoriteAthleteDetailsForSection(query = "") {
  const details = await getJson("/preferences/athletes/followed/details", {}, { auth: true });
  state.favoriteAthleteIds = new Set(details.map((item) => Number(item.athlete_id)));
  state.favoritesLoaded = true;
  return sortFavoriteAthleteDetails(details.filter((detail) => favoriteAthleteDetailMatches(detail, query)));
}

async function getFavoriteEventDetailsForSection(query = "") {
  const details = await getJson("/preferences/events/saved/details", {}, { auth: true });
  state.favoriteEventIds = new Set(details.map((item) => Number(item.event_id)));
  state.favoritesLoaded = true;
  return details.filter((detail) => favoriteEventDetailMatches(detail, query));
}

function rankingCategory() {
  return singleFilterParam("category", "rankings");
}

function rankingTimeFilters() {
  const filters = scopedFilters("rankings");
  return {
    startYear: filters.startYear || "",
    endYear: filters.endYear || "",
    startDate: filters.startDate || "",
    endDate: filters.endDate || "",
    startPeriod: filters.startPeriod || "",
    endPeriod: filters.endPeriod || "",
  };
}

function rankingHasTimeFilter() {
  const filters = rankingTimeFilters();
  return Boolean(filters.startYear || filters.endYear || filters.startDate || filters.endDate);
}

function savedRankingHasTimeFilter(filters = {}) {
  return Boolean(
    filters.startYear
    || filters.endYear
    || filters.startDate
    || filters.endDate
    || filters.startPeriod
    || filters.endPeriod,
  );
}

function normalizeRankingTemporalFilterState() {
  if (!rankingHasTimeFilter() || !rankingScoringCycleValues().length) return;
  scopedFilters("rankings").scoringCycle = [];
}

function rankingQueryParams(limit, offset = 0) {
  normalizeRankingTemporalFilterState();
  const scoringCycles = rankingScoringCycleValues();
  const timeFilters = rankingTimeFilters();
  const params = {
    limit,
    offset,
    discipline: rankingDiscipline(),
    category: rankingCategory(),
    level: filterValues("level", "rankings"),
    sort_by: rankingSortBy(),
    apparatus: rankingApparatusValues(),
  };
  if (timeFilters.startYear) params.start_year = timeFilters.startYear;
  if (timeFilters.endYear) params.end_year = timeFilters.endYear;
  if (timeFilters.startDate) params.start_date = timeFilters.startDate;
  if (timeFilters.endDate) params.end_date = timeFilters.endDate;
  if (rankingHasTimeFilter()) {
    return params;
  }
  if (SCORING_CYCLE_FILTERS.every((cycle) => scoringCycles.includes(cycle))) {
    params.include_all_scoring_cycles = true;
  } else if (scoringCycles.length) {
    params.scoring_cycle = scoringCycles;
  }
  return params;
}

function savedRankingFiltersPayload() {
  const timeFilters = rankingTimeFilters();
  const hasTimeFilter = rankingHasTimeFilter();
  return {
    discipline: [rankingDiscipline()],
    category: filterValues("category", "rankings"),
    level: filterValues("level", "rankings"),
    sortBy: rankingSortBy(),
    apparatus: rankingApparatusValues(),
    scoringCycle: hasTimeFilter ? [] : rankingScoringCycleValues(),
    startYear: timeFilters.startYear,
    endYear: timeFilters.endYear,
    startDate: timeFilters.startDate,
    endDate: timeFilters.endDate,
    startPeriod: timeFilters.startPeriod,
    endPeriod: timeFilters.endPeriod,
  };
}

function normalizeSavedFilterArray(value) {
  if (Array.isArray(value)) return value.filter((item) => item !== undefined && item !== null && item !== "");
  return value ? [value] : [];
}

function applySavedRankingFilters(filters = {}) {
  const discipline = normalizeSavedFilterArray(filters.discipline);
  const selectedDiscipline = discipline.includes("WAG") ? "WAG" : "MAG";
  const allowedApparatuses = RANKING_APPARATUS_BY_DISCIPLINE[selectedDiscipline] || [];
  const legacyStartYear = filters.startYear ? String(filters.startYear).trim() : "";
  const legacyEndYear = filters.endYear ? String(filters.endYear).trim() : "";
  const resolvedStartDate = filters.startDate || (legacyStartYear ? `${legacyStartYear}-01-01` : "");
  const resolvedEndDate = filters.endDate || (legacyEndYear ? `${legacyEndYear}-12-31` : "");
  const selectedLevels = normalizeSavedFilterArray(filters.level).filter((value) => (
    EVENT_LEVEL_FILTERS.some((level) => level.value === value)
  ));
  const selectedMetric = normalizeRankingMetricValue(normalizeSavedFilterArray(filters.sortBy || filters.sort_by)[0]);
  const hasTimeFilter = savedRankingHasTimeFilter({
    ...filters,
    startYear: legacyStartYear,
    endYear: legacyEndYear,
    startDate: resolvedStartDate,
    endDate: resolvedEndDate,
  });
  Object.assign(scopedFilters("rankings"), {
    discipline: [selectedDiscipline],
    category: normalizeSavedFilterArray(filters.category).filter((value) => ["junior", "senior"].includes(value)),
    level: selectedLevels,
    sortBy: RANKING_METRIC_FILTERS.some((metric) => metric.value === selectedMetric) ? selectedMetric : "score",
    apparatus: normalizeExclusiveApparatusSelection(normalizeSavedFilterArray(filters.apparatus).filter((value) => allowedApparatuses.includes(value))),
    scoringCycle: hasTimeFilter ? [] : rankingScoringCycleValues(normalizeSavedFilterArray(filters.scoringCycle)),
    startYear: "",
    endYear: "",
    startDate: resolvedStartDate,
    endDate: resolvedEndDate,
    startPeriod: filters.startPeriod || legacyStartYear || formatDateInputValue(resolvedStartDate),
    endPeriod: filters.endPeriod || legacyEndYear || formatDateInputValue(resolvedEndDate),
  });
}

function rankingFilterSummary(filters = savedRankingFiltersPayload()) {
  const parts = [];
  const discipline = normalizeSavedFilterArray(filters.discipline);
  parts.push(discipline[0] || "MAG");
  parts.push(...normalizeSavedFilterArray(filters.category).map((value) => (
    value === "junior" ? t("junior") : t("senior")
  )));
  const selectedLevels = normalizeSavedFilterArray(filters.level).filter((value) => (
    EVENT_LEVEL_FILTERS.some((level) => level.value === value)
  ));
  if (selectedLevels.length) parts.push(selectedLevels.map(eventLevelAbbreviation).join(", "));
  parts.push(rankingMetricLabel(normalizeRankingMetricValue(normalizeSavedFilterArray(filters.sortBy || filters.sort_by)[0])));
  parts.push(...normalizeSavedFilterArray(filters.apparatus));
  const scoringCycles = rankingScoringCycleValues(normalizeSavedFilterArray(filters.scoringCycle));
  if (filters.startDate || filters.endDate || filters.startPeriod || filters.endPeriod) {
    parts.push([
      filters.startPeriod || formatDateInputValue(filters.startDate),
      filters.endPeriod || formatDateInputValue(filters.endDate),
    ].filter(Boolean).join(" - "));
  } else if (filters.startYear || filters.endYear) {
    parts.push([filters.startYear, filters.endYear].filter(Boolean).join(" - "));
  } else if (SCORING_CYCLE_FILTERS.every((cycle) => scoringCycles.includes(cycle))) {
    parts.push(t("allCycles"));
  } else {
    parts.push(...scoringCycles);
  }
  return parts.filter(Boolean).join(" · ");
}

async function applySavedRankingViewFromRoute(viewId) {
  if (!state.currentUser || !viewId) return;
  try {
    const view = await getJson(`/preferences/dashboard-views/${viewId}`, {}, { auth: true });
    if (view.view_type === "ranking") {
      applySavedRankingFilters(view.filters || {});
    }
  } catch (_error) {
    // If a saved view cannot be loaded, keep the current Ranking filters.
  } finally {
    window.history.replaceState(null, "", "#/rankings");
    state.route = "/rankings";
    setActiveNav();
  }
}

function calendarDateFromOffset(offset) {
  return new Date(TODAY.getFullYear(), TODAY.getMonth() + offset, 1);
}

function eventsCalendarDate() {
  return calendarDateFromOffset(state.eventsCalendarMonthOffset);
}

function calendarMonthOffsetForDate(date) {
  return ((date.getFullYear() - TODAY.getFullYear()) * 12) + (date.getMonth() - TODAY.getMonth());
}

function eventCalendarNavigationDate(event) {
  return parseLocalDate(event?.start_date || event?.end_date);
}

function eventCalendarNavigationKey(event = {}) {
  return [
    event.calendar_entry_id || "",
    event.id || "",
    event.name || "",
    event.start_date || "",
    event.end_date || "",
    event.discipline || "",
    event.category || "",
  ].join("|");
}

function calendarNavigationItemSort(left, right) {
  return left.date - right.date ||
    String(left.event.name || "").localeCompare(String(right.event.name || "")) ||
    Number(left.event.calendar_entry_id || 0) - Number(right.event.calendar_entry_id || 0) ||
    Number(left.event.id || 0) - Number(right.event.id || 0) ||
    left.originalIndex - right.originalIndex;
}

function eventCalendarNavigationItems(events = []) {
  return [...events]
    .map((event, originalIndex) => ({
      event,
      date: eventCalendarNavigationDate(event),
      key: eventCalendarNavigationKey(event),
      originalIndex,
    }))
    .filter((item) => item.date)
    .sort(calendarNavigationItemSort);
}

function favoriteEventNavigationItems(details) {
  return [...details]
    .map((detail, originalIndex) => {
      const event = detail.event || {};
      return {
        detail,
        event,
        date: eventCalendarNavigationDate(event),
        key: eventCalendarNavigationKey(event),
        originalIndex,
      };
    })
    .filter((item) => item.date)
    .sort((left, right) => (
      calendarNavigationItemSort(left, right) ||
      Number(left.detail.event_id || 0) - Number(right.detail.event_id || 0)
    ));
}

function sortFavoriteEventDetails(details) {
  const datedItems = favoriteEventNavigationItems(details);
  const datedIds = new Set(datedItems.map((item) => item.detail));
  const undatedDetails = details.filter((detail) => !datedIds.has(detail));
  return [
    ...datedItems.map((item) => item.detail),
    ...undatedDetails,
  ];
}

function eventCalendarNavigationIndex(items, monthDate) {
  if (!items.length) return -1;
  const selectedIndex = items.findIndex((item) => item.key && item.key === state.eventsCalendarNavigationKey);
  if (selectedIndex >= 0) return selectedIndex;
  const sameMonthIndex = items.findIndex((item) => sameMonth(item.date, monthDate));
  if (sameMonthIndex >= 0) return sameMonthIndex;
  const monthStart = new Date(monthDate.getFullYear(), monthDate.getMonth(), 1);
  const nextIndex = items.findIndex((item) => item.date >= monthStart);
  return nextIndex >= 0 ? nextIndex : items.length - 1;
}

function syncEventCalendarNavigationSelection(items, monthDate) {
  const index = eventCalendarNavigationIndex(items, monthDate);
  state.eventsCalendarNavigationKey = index >= 0 ? items[index].key : "";
  return index;
}

function focusEventsCalendarOnFirstFavorite(details) {
  const [firstItem] = favoriteEventNavigationItems(details);
  if (!firstItem) return false;
  state.eventsCalendarNavigationKey = firstItem.key;
  state.eventsCalendarMonthOffset = calendarMonthOffsetForDate(firstItem.date);
  return true;
}

function eventCalendarHasNavigationScope(query = "") {
  return Boolean(
    query.trim() ||
    filterValues("discipline", "events").length ||
    filterValues("category", "events").length ||
    filterValues("level", "events").length ||
    eventHasTimeFilter() ||
    favoritesOnly("events"),
  );
}

function eventCalendarQueryParams(query = "", options = {}) {
  return {
    search: query,
    start_date: options.startDate || "",
    end_date: options.endDate || "",
    as_of: formatLocalIso(TODAY),
    limit: options.limit || 1000,
    offset: options.offset || 0,
    discipline: multiFilterParam("discipline", "events"),
    category: multiFilterParam("category", "events"),
    level: filterValues("level", "events"),
  };
}

async function fetchFilteredEventCalendarNavigationItems(query = "") {
  if (!eventCalendarHasNavigationScope(query)) return [];
  const timeFilters = eventTimeFilters();
  const events = await getJson("/events/calendar", eventCalendarQueryParams(query, {
    startDate: timeFilters.startDate,
    endDate: timeFilters.endDate,
  }));
  return eventCalendarNavigationItems(filterFavoriteEvents(events));
}

function filterButton(label, type, value, scope = currentFilterScope(), className = "") {
  return `<button class="filter-button ${className}" type="button" data-filter-scope="${scope}" data-filter-type="${type}" data-filter-value="${value}" aria-pressed="${filterIsActive(type, value, scope)}">${label}</button>`;
}

function eventLevelAbbreviation(value) {
  return EVENT_LEVEL_FILTERS.find((level) => level.value === value)?.abbreviation || value;
}

function renderEventLevelFilter() {
  const selectedLevels = filterValues("level", "events");
  const label = selectedLevels.length
    ? `${t("levelFilter")}: ${selectedLevels.map(eventLevelAbbreviation).join(", ")}`
    : t("levelFilter");
  return `
    <details class="filter-menu event-level-filter">
      <summary class="filter-button filter-menu-summary" aria-pressed="${Boolean(selectedLevels.length)}">${escapeHtml(label)}</summary>
      <div class="filter-menu-panel">
        ${EVENT_LEVEL_FILTERS.map((level) => filterButton(level.label, "level", level.value, "events", "filter-menu-option")).join("")}
      </div>
    </details>
  `;
}

function renderRankingScoringCycleFilter() {
  const selectedCycles = rankingScoringCycleValues();
  const allCyclesSelected = SCORING_CYCLE_FILTERS.every((cycle) => selectedCycles.includes(cycle));
  const label = allCyclesSelected
    ? `${t("scoringCycle")}: ${t("allCycles")}`
    : selectedCycles.length
      ? `${t("scoringCycle")}: ${selectedCycles.join(", ")}`
      : t("scoringCycle");
  return `
    <details class="filter-menu ranking-cycle-filter">
      <summary class="filter-button filter-menu-summary" aria-pressed="${Boolean(selectedCycles.length)}">${escapeHtml(label)}</summary>
      <div class="filter-menu-panel">
        ${SCORING_CYCLE_FILTERS.map((cycle) => filterButton(cycle, "scoringCycle", cycle, "rankings", "filter-menu-option")).join("")}
      </div>
    </details>
  `;
}

function renderRankingLevelFilter() {
  const selectedLevels = filterValues("level", "rankings");
  const label = selectedLevels.length
    ? `${t("levelFilter")}: ${selectedLevels.map(eventLevelAbbreviation).join(", ")}`
    : t("levelFilter");
  return `
    <details class="filter-menu ranking-level-filter">
      <summary class="filter-button filter-menu-summary" aria-pressed="${Boolean(selectedLevels.length)}">${escapeHtml(label)}</summary>
      <div class="filter-menu-panel">
        ${EVENT_LEVEL_FILTERS.map((level) => filterButton(level.label, "level", level.value, "rankings", "filter-menu-option")).join("")}
      </div>
    </details>
  `;
}

function renderRankingMetricFilters() {
  const selectedMetric = rankingSortBy();
  const selectedIndex = Math.max(0, RANKING_METRIC_FILTERS.findIndex((metric) => metric.value === selectedMetric));
  return `
    <div
      class="segmented-control ranking-metric-control"
      role="radiogroup"
      aria-label="${escapeHtml(t("rankingMetric"))}"
      style="--segment-count: ${RANKING_METRIC_FILTERS.length}; --selected-index: ${selectedIndex};"
    >
      ${RANKING_METRIC_FILTERS.map((metric) => `
        <button
          class="segmented-option ranking-metric-option"
          type="button"
          role="radio"
          data-ranking-metric="${escapeHtml(metric.value)}"
          aria-checked="${String(selectedMetric === metric.value)}"
        >${escapeHtml(metric.label)}</button>
      `).join("")}
      <span class="segmented-thumb ranking-metric-thumb" aria-hidden="true"></span>
    </div>
  `;
}

function disciplineSegmentedControl() {
  const selected = rankingDiscipline();
  return `
    <div class="segmented-control" role="radiogroup" aria-label="${t("discipline")}">
      ${["MAG", "WAG"].map((value) => `
        <button
          class="segmented-option"
          type="button"
          role="radio"
          aria-checked="${selected === value}"
          data-ranking-discipline="${value}"
        >${value}</button>
      `).join("")}
      <span class="segmented-thumb" data-selected="${selected}"></span>
    </div>
  `;
}

function eventViewModeControl() {
  const selected = state.eventsViewMode === "calendar" ? "calendar" : "list";
  const options = [
    { value: "list", label: t("eventViewList") },
    { value: "calendar", label: t("eventViewCalendar") },
  ];
  return `
    <div class="segmented-control event-view-toggle" role="radiogroup" aria-label="${t("navEvents")}">
      ${options.map((option) => `
        <button
          class="segmented-option"
          type="button"
          role="radio"
          aria-checked="${selected === option.value}"
          data-event-view-mode="${option.value}"
        >${escapeHtml(option.label)}</button>
      `).join("")}
      <span class="segmented-thumb" data-selected="${selected}"></span>
    </div>
  `;
}

function athleteSortModeControl() {
  const selected = state.athleteSortMode === "country" ? "country" : "name";
  const options = [
    { value: "name", label: t("athleteSortName") },
    { value: "country", label: t("athleteSortCountry") },
  ];
  return `
    <div class="segmented-control athlete-sort-toggle" role="radiogroup" aria-label="${t("athlete")}">
      ${options.map((option) => `
        <button
          class="segmented-option"
          type="button"
          role="radio"
          aria-checked="${selected === option.value}"
          data-athlete-sort-mode="${option.value}"
        >${escapeHtml(option.label)}</button>
      `).join("")}
      <span class="segmented-thumb" data-selected="${selected}"></span>
    </div>
  `;
}

function closeFilterPopups(except = null) {
  document.querySelectorAll(".filter-menu[open], .ranking-time-filter[open]").forEach((details) => {
    if (details === except) return;
    details.open = false;
    const timeScope = details.dataset.timeFilterScope;
    if (timeScope) setTimeFilterOpen(timeScope, false);
  });
}

function closeRankingSavePopup() {
  const shell = $("#rankingSaveFormShell");
  const revealButton = $("#showRankingSaveFormButton");
  if (!shell || shell.hidden) return;
  shell.hidden = true;
  revealButton?.setAttribute("aria-expanded", "false");
}

function eventStartedInsideFilterPopup(event) {
  const path = typeof event.composedPath === "function" ? event.composedPath() : [];
  if (path.some((node) => node instanceof Element && node.matches(".filter-menu, .ranking-time-filter"))) {
    return true;
  }
  const target = event.target instanceof Element ? event.target : event.target?.parentElement;
  return Boolean(target?.closest(".filter-menu, .ranking-time-filter"));
}

function eventStartedInsideRankingSavePopup(event) {
  const path = typeof event.composedPath === "function" ? event.composedPath() : [];
  if (path.some((node) => node instanceof Element && node.matches(".saved-ranking-panel"))) {
    return true;
  }
  const target = event.target instanceof Element ? event.target : event.target?.parentElement;
  return Boolean(target?.closest(".saved-ranking-panel"));
}

function closeFilterPopupsOnOutsidePointerDown(event) {
  if (!eventStartedInsideFilterPopup(event)) closeFilterPopups();
  if (!eventStartedInsideRankingSavePopup(event)) closeRankingSavePopup();
}

function bindFilterMenuPopups() {
  document.querySelectorAll(".filter-menu").forEach((details) => {
    details.addEventListener("toggle", () => {
      if (details.open) closeFilterPopups(details);
    });
  });
}

function handleSectionFilterChange(change) {
  if (!["athletes", "events", "rankings"].includes(change.scope)) {
    renderAfterFilterChange();
    return;
  }
  syncFilterButtonState(change.button);
  if (change.scope === "events") {
    syncEventLevelFilterMenu();
    if (change.type === "favoritesOnly") {
      state.eventsFavoriteCalendarAutoFocus = favoritesOnly("events");
    }
  }
  if (change.scope === "rankings") {
    syncRankingLevelFilterMenu();
    syncRankingScoringCycleFilterMenu();
    syncTimeFilterUi("rankings");
    if (change.type === "apparatus") syncRankingApparatusFilterRow();
  }
  if (change.scope === "rankings") {
    refreshSectionFilters(change.scope, { scroll: false, showLoading: false });
    return;
  }
  refreshSectionFiltersAtRecordsTop(change.scope);
}

function applyFilterButtonChange(button, onChange = null) {
  const notifyChange = (change) => {
    if (typeof onChange === "function") {
      onChange(change);
      return;
    }
    renderAfterFilterChange();
  };
  const scope = button.dataset.filterScope || currentFilterScope();
  const type = button.dataset.filterType;
  const value = button.dataset.filterValue;
  const filters = scopedFilters(scope);
  if (scope === "rankings" && type === "scoringCycle") {
    clearRankingTimeFilters();
    const cycleValues = rankingScoringCycleValues(filterValues(type, scope));
    filters[type] = cycleValues.includes(value)
      ? cycleValues.filter((item) => item !== value)
      : [...cycleValues, value];
    notifyChange({ scope, type, value, button });
    return;
  }
  if (scope === "rankings" && type === "apparatus") {
    filters[type] = toggleExclusiveApparatusSelection(filterValues(type, scope), value);
    notifyChange({ scope, type, value, button });
    return;
  }
  if (Array.isArray(filters[type])) {
    const values = filterValues(type, scope);
    filters[type] = values.includes(value)
      ? values.filter((item) => item !== value)
      : [...values, value];
  } else {
    filters[type] = filters[type] === value ? "" : value;
  }
  notifyChange({ scope, type, value, button });
}

function bindFilterButtonsIn(root, onChange = null) {
  root.querySelectorAll("[data-filter-type]").forEach((button) => {
    button.addEventListener("click", () => applyFilterButtonChange(button, onChange));
  });
}

function bindFilterButtons(onChange = null) {
  bindFilterButtonsIn(document, onChange);
  bindFilterMenuPopups();
}

function syncRankingApparatusFilterRow(onChange = handleSectionFilterChange) {
  const row = $("#rankingApparatusFilterRow");
  if (!row) return;
  rankingApparatusValues();
  row.innerHTML = rankingApparatusFilters()
    .map((apparatus) => filterButton(apparatus, "apparatus", apparatus, "rankings"))
    .join("");
  bindFilterButtonsIn(row, onChange);
}

function bindRankingDisciplineControl(onChange = null) {
  document.querySelectorAll("[data-ranking-discipline]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextDiscipline = button.dataset.rankingDiscipline === "WAG" ? "WAG" : "MAG";
      if (rankingDiscipline() === nextDiscipline) return;
      scopedFilters("rankings").discipline = [nextDiscipline];
      const allowedApparatuses = RANKING_APPARATUS_BY_DISCIPLINE[nextDiscipline] || [];
      scopedFilters("rankings").apparatus = normalizeExclusiveApparatusSelection(filterValues("apparatus", "rankings").filter((value) => (
        allowedApparatuses.includes(value)
      )));
      syncRankingDisciplineControl();
      syncRankingApparatusFilterRow();
      window.setTimeout(() => {
        if (typeof onChange === "function") {
          onChange();
        } else {
          renderAfterFilterChange();
        }
      }, 220);
    });
  });
}

function bindRankingMetricControl(onChange) {
  document.querySelectorAll("[data-ranking-metric]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextMetric = normalizeRankingMetricValue(button.dataset.rankingMetric);
      if (rankingSortBy() === nextMetric) return;
      scopedFilters("rankings").sortBy = nextMetric;
      syncRankingMetricControl();
      if (typeof onChange === "function") {
        onChange();
        return;
      }
      renderAfterFilterChange();
    });
  });
}

function syncRankingDisciplineControl() {
  const selected = rankingDiscipline();
  document.querySelectorAll("[data-ranking-discipline]").forEach((button) => {
    button.setAttribute("aria-checked", String(button.dataset.rankingDiscipline === selected));
  });
  const control = document.querySelector("[data-ranking-discipline]")?.closest(".segmented-control");
  const thumb = control?.querySelector(".segmented-thumb");
  if (thumb) thumb.dataset.selected = selected;
}

function syncRankingMetricControl() {
  const selected = rankingSortBy();
  const selectedIndex = Math.max(0, RANKING_METRIC_FILTERS.findIndex((metric) => metric.value === selected));
  document.querySelectorAll("[data-ranking-metric]").forEach((button) => {
    button.setAttribute("aria-checked", String(button.dataset.rankingMetric === selected));
  });
  document.querySelectorAll(".ranking-metric-control").forEach((control) => {
    control.style.setProperty("--selected-index", selectedIndex);
  });
}

function syncEventDetailMetricControl(options = {}) {
  const selected = eventDetailSortBy();
  const selectedIndex = Math.max(0, RANKING_METRIC_FILTERS.findIndex((metric) => metric.value === selected));
  document.querySelectorAll("[data-event-detail-metric]").forEach((button) => {
    button.setAttribute("aria-checked", String(button.dataset.eventDetailMetric === selected));
  });
  document.querySelectorAll(".event-detail-metric-control").forEach((control) => {
    control.style.setProperty("--selected-index", selectedIndex);
    syncMeasuredSegmentedThumb(control, options);
  });
}

function syncMeasuredSegmentedThumb(control, options = {}) {
  if (!control) return;
  const selectedOption = control.querySelector(".segmented-option[aria-checked=\"true\"]");
  const thumb = control.querySelector(".segmented-thumb");
  if (!selectedOption || !thumb) return;
  const animate = options.animate !== false;
  if (!animate) control.classList.add("is-syncing-thumb");
  control.style.setProperty("--thumb-left", `${selectedOption.offsetLeft}px`);
  control.style.setProperty("--thumb-width", `${selectedOption.offsetWidth}px`);
  control.classList.add("is-measured-thumb");
  if (!animate) {
    window.requestAnimationFrame(() => {
      control.classList.remove("is-syncing-thumb");
    });
  }
}

function syncEventDetailSegmentedThumbs(root = document, options = {}) {
  const rootNode = root && typeof root.querySelectorAll === "function" ? root : document;
  window.requestAnimationFrame(() => {
    rootNode
      .querySelectorAll(".event-classification-segment, .event-detail-metric-control")
      .forEach((control) => syncMeasuredSegmentedThumb(control, options));
  });
}

function eventClassificationFieldShouldRender(field, options) {
  if (!options.length) return false;
  return !(field === "day" && !options.some((value) => hasDisplayValue(value)));
}

function eventClassificationControlCanPatch(field, selected, groups) {
  const options = eventClassificationDisplayOptionsForField(field, selected, groups);
  const control = document.querySelector(`[data-event-classification-control="${field}"]`);
  const shouldRender = eventClassificationFieldShouldRender(field, options);
  if (!shouldRender) return !control;
  if (!control) return false;
  const buttons = [...control.querySelectorAll("[data-event-classification-value]")];
  return buttons.length === options.length
    && buttons.every((button, index) => (
      button.dataset.eventClassificationValue === eventClassificationValueKey(options[index])
    ));
}

function replaceEventClassificationControl(field, selected, groups) {
  const html = eventClassificationSegment(field, selected, groups);
  const control = document.querySelector(`[data-event-classification-control="${field}"]`);
  const fieldNode = control?.closest(".event-classification-segment-field");
  if (!fieldNode) return !html;
  if (!html) {
    fieldNode.remove();
    return true;
  }
  fieldNode.outerHTML = html;
  const nextControl = document.querySelector(`[data-event-classification-control="${field}"]`);
  syncMeasuredSegmentedThumb(nextControl, { animate: false });
  return true;
}

function syncEventClassificationControl(field, selected, groups, syncOptions = {}) {
  const control = document.querySelector(`[data-event-classification-control="${field}"]`);
  if (!control) return;
  const selectedValue = eventClassificationValueKey(selected?.[field]);
  const fieldOptions = eventClassificationDisplayOptionsForField(field, selected, groups);
  const selectedIndex = Math.max(0, fieldOptions.findIndex((value) => eventClassificationValueKey(value) === selectedValue));
  control.style.setProperty("--selected-index", selectedIndex);
  control.querySelectorAll("[data-event-classification-value]").forEach((button) => {
    const active = button.dataset.eventClassificationValue === selectedValue;
    const available = eventClassificationOptionIsAvailable(field, button.dataset.eventClassificationValue, selected, groups);
    button.setAttribute("aria-checked", String(active));
    button.setAttribute("aria-disabled", available ? "false" : "true");
    button.disabled = !available;
  });
  syncMeasuredSegmentedThumb(control, syncOptions);
}

function syncEventDetailClassificationControls() {
  const groups = officialEventClassificationGroups();
  const selected = selectedEventClassification();
  const fields = eventClassificationFields();
  if (!selected) return false;
  let replacedControl = false;
  for (const field of fields) {
    if (eventClassificationControlCanPatch(field, selected, groups)) {
      syncEventClassificationControl(field, selected, groups);
    } else if (replaceEventClassificationControl(field, selected, groups)) {
      replacedControl = true;
    } else {
      return false;
    }
  }
  syncEventDetailMetricControl({ animate: false });
  if (replacedControl) {
    bindEventClassificationControls(document.querySelector(".event-classification-sticky-menu"), { syncThumbs: false });
  }
  return true;
}

function syncEventViewModeControl() {
  const selected = state.eventsViewMode === "calendar" ? "calendar" : "list";
  document.querySelectorAll("[data-event-view-mode]").forEach((button) => {
    button.setAttribute("aria-checked", String(button.dataset.eventViewMode === selected));
  });
  document.querySelectorAll(".event-view-toggle .segmented-thumb").forEach((thumb) => {
    thumb.dataset.selected = selected;
  });
}

function bindEventViewModeControl(onChange) {
  document.querySelectorAll("[data-event-view-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextMode = button.dataset.eventViewMode === "calendar" ? "calendar" : "list";
      if (state.eventsViewMode === nextMode) return;
      state.eventsViewMode = nextMode;
      if (nextMode === "calendar" && favoritesOnly("events")) {
        state.eventsFavoriteCalendarAutoFocus = true;
      }
      syncEventViewModeControl();
      if (typeof onChange === "function") onChange();
    });
  });
}

function syncAthleteSortModeControl() {
  const selected = state.athleteSortMode === "country" ? "country" : "name";
  document.querySelectorAll("[data-athlete-sort-mode]").forEach((button) => {
    button.setAttribute("aria-checked", String(button.dataset.athleteSortMode === selected));
  });
  document.querySelectorAll(".athlete-sort-toggle .segmented-thumb").forEach((thumb) => {
    thumb.dataset.selected = selected;
  });
}

function bindAthleteSortModeControl(onChange) {
  document.querySelectorAll("[data-athlete-sort-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextMode = button.dataset.athleteSortMode === "country" ? "country" : "name";
      if (state.athleteSortMode === nextMode) return;
      state.athleteSortMode = nextMode;
      syncAthleteSortModeControl();
      if (typeof onChange === "function") onChange();
    });
  });
}

function clearRankingTimeFilters() {
  Object.assign(scopedFilters("rankings"), {
    startYear: "",
    endYear: "",
    startDate: "",
    endDate: "",
    startPeriod: "",
    endPeriod: "",
  });
  setTimeFilterOpen("rankings", false);
}

function clearEventTimeFilters() {
  Object.assign(scopedFilters("events"), {
    startDate: "",
    endDate: "",
    startPeriod: "",
    endPeriod: "",
  });
  setTimeFilterOpen("events", false);
}

function clearSectionSearch(section) {
  const config = {
    athletes: { inputId: "athleteSearchInput", syncRoute: syncAthleteSearchRoute },
    events: { inputId: "eventSearchInput", syncRoute: syncEventSearchRoute },
  }[section];
  if (!config) return;
  const input = document.getElementById(config.inputId);
  if (input) input.value = "";
  const clearButton = document.querySelector(`[data-search-clear-for="${config.inputId}"]`);
  if (clearButton) clearButton.hidden = true;
  config.syncRoute("");
  closeSearchSuggestions();
}

function clearEventFilters() {
  Object.assign(scopedFilters("events"), {
    discipline: [],
    category: [],
    level: [],
    favoritesOnly: "",
    startDate: "",
    endDate: "",
    startPeriod: "",
    endPeriod: "",
  });
  setTimeFilterOpen("events", false);
  state.eventsCalendarMonthOffset = 0;
  state.eventsFavoriteCalendarAutoFocus = false;
  clearSectionSearch("events");
  syncSectionFilterButtons("events");
  syncEventLevelFilterMenu();
  syncTimeFilterUi("events");
  refreshSectionFiltersAtRecordsTop("events");
}

function clearAthleteFilters() {
  Object.assign(scopedFilters("athletes"), {
    discipline: [],
    category: [],
    favoritesOnly: "",
  });
  clearSectionSearch("athletes");
  syncSectionFilterButtons("athletes");
  refreshSectionFiltersAtRecordsTop("athletes");
}

function clearRankingFilters() {
  Object.assign(scopedFilters("rankings"), {
    discipline: [],
    category: [],
    level: [],
    sortBy: "score",
    apparatus: ["AA"],
    scoringCycle: [],
    startYear: "",
    endYear: "",
    startDate: "",
    endDate: "",
    startPeriod: "",
    endPeriod: "",
  });
  setTimeFilterOpen("rankings", false);
  syncSectionFilterButtons("rankings");
  syncRankingDisciplineControl();
  syncRankingMetricControl();
  syncRankingApparatusFilterRow();
  syncRankingLevelFilterMenu();
  syncRankingScoringCycleFilterMenu();
  syncTimeFilterUi("rankings");
  refreshSectionFilters("rankings", { scroll: false, showLoading: false });
}

function normalizeDateRangeChange(field, startDate, endDate, startPeriod = "", endPeriod = "") {
  if (field === "endDate" && isoDateIsBefore(endDate, startDate)) {
    return null;
  }
  if (field === "startDate" && isoDateIsBefore(endDate, startDate)) {
    return {
      startDate,
      endDate: "",
      startPeriod,
      endPeriod: "",
    };
  }
  return {
    startDate,
    endDate,
    startPeriod,
    endPeriod,
  };
}

function setRankingDateRange(startDate, endDate, startPeriod = "", endPeriod = "", field = "") {
  const nextRange = normalizeDateRangeChange(field, startDate, endDate, startPeriod, endPeriod);
  if (!nextRange) return false;
  setTimeFilterOpen("rankings", true);
  Object.assign(scopedFilters("rankings"), {
    startYear: "",
    endYear: "",
    startDate: nextRange.startDate,
    endDate: nextRange.endDate,
    startPeriod: nextRange.startPeriod,
    endPeriod: nextRange.endPeriod,
    scoringCycle: [],
  });
  syncTimeFilterUi("rankings");
  syncRankingScoringCycleFilterMenu();
  refreshSectionFilters("rankings", { scroll: false, showLoading: false });
  return true;
}

function monthOffsetForDate(value) {
  const date = parseLocalDate(value);
  if (!date) return 0;
  return ((date.getFullYear() - TODAY.getFullYear()) * 12) + (date.getMonth() - TODAY.getMonth());
}

function setEventDateRange(startDate, endDate, startPeriod = "", endPeriod = "", field = "") {
  const nextRange = normalizeDateRangeChange(field, startDate, endDate, startPeriod, endPeriod);
  if (!nextRange) return false;
  setTimeFilterOpen("events", true);
  Object.assign(scopedFilters("events"), {
    startDate: nextRange.startDate,
    endDate: nextRange.endDate,
    startPeriod: nextRange.startPeriod,
    endPeriod: nextRange.endPeriod,
  });
  if (nextRange.startDate || nextRange.endDate) {
    state.eventsCalendarMonthOffset = monthOffsetForDate(nextRange.startDate || nextRange.endDate);
  }
  syncTimeFilterUi("events");
  refreshSectionFiltersAtRecordsTop("events");
  return true;
}

function bindTimeFilterToggle(scope) {
  const details = document.querySelector(`[data-time-filter-scope="${scope}"]`);
  const summary = details?.querySelector("[data-time-filter-summary]");
  if (!details || !summary) return;
  details.open = timeFilterIsOpen(scope);
  details.addEventListener("toggle", () => {
    setTimeFilterOpen(scope, details.open);
  });
  summary.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (!details.open) closeFilterPopups(details);
    setTimeFilterOpen(scope, !details.open);
    details.open = timeFilterIsOpen(scope);
  });
}

function bindDateWheelFilters(scope, getFilters, setDateRange) {
  const openStateKey = scope === "events" ? "openEventDateWheel" : "openRankingDateWheel";
  document.querySelectorAll(`[data-date-wheel-scope="${scope}"][data-date-wheel]`).forEach((details) => {
    details.addEventListener("toggle", () => {
      if (details.open) {
        state[openStateKey] = details.dataset.dateWheel || "";
        document.querySelectorAll(`[data-date-wheel-scope="${scope}"][data-date-wheel]`).forEach((otherDetails) => {
          if (otherDetails !== details) otherDetails.removeAttribute("open");
        });
        scrollDateWheelToActive(details);
      } else if (state[openStateKey] === details.dataset.dateWheel) {
        state[openStateKey] = "";
      }
    });
  });

  document.querySelectorAll(`[data-date-wheel-text-scope="${scope}"]`).forEach((input) => {
    const details = input.closest("[data-date-wheel]");
    const field = input.dataset.dateWheelTextField;
    const openWheel = () => {
      if (!details || !field) return;
      state[openStateKey] = field;
      details.open = true;
      document.querySelectorAll(`[data-date-wheel-scope="${scope}"][data-date-wheel]`).forEach((otherDetails) => {
        if (otherDetails !== details) otherDetails.removeAttribute("open");
      });
      scrollDateWheelToActive(details);
    };
    input.addEventListener("click", (event) => {
      event.stopPropagation();
      openWheel();
    });
    input.addEventListener("focus", openWheel);
    input.addEventListener("keydown", (event) => {
      event.stopPropagation();
    });
    input.addEventListener("input", () => {
      const formattedValue = formatTypedDateInput(input.value);
      if (formattedValue !== input.value) {
        input.value = formattedValue;
      }
      const parsedPeriod = normalizeTypedPeriod(input.value);
      const filters = getFilters();
      const nextStartDate = field === "startDate" ? periodDateForField(parsedPeriod, field) : filters.startDate;
      const nextEndDate = field === "endDate" ? periodDateForField(parsedPeriod, field) : filters.endDate;
      const rangeInvalid = field === "endDate" && isoDateIsBefore(nextEndDate, nextStartDate);
      input.classList.toggle(
        "is-invalid",
        (parsedPeriod === null && periodInputShouldValidate(input.value)) || rangeInvalid,
      );
      if (parsedPeriod === null) return;
      if (rangeInvalid) return;
      state[openStateKey] = field;
      setDateRange(
        nextStartDate,
        nextEndDate,
        field === "startDate" ? parsedPeriod.display : filters.startPeriod,
        field === "endDate" ? parsedPeriod.display : filters.endPeriod,
        field,
      );
    });
  });

  document.querySelectorAll(`[data-date-wheel-scope="${scope}"][data-date-wheel-field]`).forEach((button) => {
    button.addEventListener("click", () => {
      const field = button.dataset.dateWheelField;
      const unit = button.dataset.dateWheelUnit;
      const value = Number(button.dataset.dateWheelValue);
      const filters = getFilters();
      const parts = datePickerParts(filters[field]);
      parts[unit] = value;
      const nextDate = isoFromDateParts(parts);
      state[openStateKey] = field;
      const displayValue = formatDateInputValue(nextDate);
      setDateRange(
        field === "startDate" ? nextDate : filters.startDate,
        field === "endDate" ? nextDate : filters.endDate,
        field === "startDate" ? displayValue : filters.startPeriod,
        field === "endDate" ? displayValue : filters.endPeriod,
        field,
      );
    });
  });

  document.querySelectorAll(`[data-date-wheel-today-scope="${scope}"]`).forEach((button) => {
    button.addEventListener("click", () => {
      const field = button.dataset.dateWheelTodayField;
      if (!field) return;
      const filters = getFilters();
      const todayDate = formatLocalIso(TODAY);
      const displayValue = formatDateInputValue(todayDate);
      state[openStateKey] = field;
      setDateRange(
        field === "startDate" ? todayDate : filters.startDate,
        field === "endDate" ? todayDate : filters.endDate,
        field === "startDate" ? displayValue : filters.startPeriod,
        field === "endDate" ? displayValue : filters.endPeriod,
        field,
      );
    });
  });

  document.querySelectorAll(`[data-date-wheel-scope="${scope}"] .ranking-date-wheel-options`).forEach((column) => {
    scrollDateWheelColumnToActive(column);
  });
}

function bindRankingTimeFilters() {
  bindTimeFilterToggle("rankings");
  bindDateWheelFilters("rankings", rankingTimeFilters, setRankingDateRange);
}

function bindEventTimeFilters() {
  bindTimeFilterToggle("events");
  bindDateWheelFilters("events", eventTimeFilters, setEventDateRange);
}

function bindEventClearFilters() {
  $("#clearEventFiltersButton")?.addEventListener("click", clearEventFilters);
}

function bindAthleteClearFilters() {
  $("#clearAthleteFiltersButton")?.addEventListener("click", clearAthleteFilters);
}

function bindRankingClearFilters() {
  $("#clearRankingFiltersButton")?.addEventListener("click", clearRankingFilters);
}

function bindRankingSaveForm() {
  const revealButton = $("#showRankingSaveFormButton");
  const shell = $("#rankingSaveFormShell");
  revealButton?.addEventListener("click", () => {
    if (!shell) return;
    const shouldShow = shell.hidden;
    shell.hidden = !shouldShow;
    revealButton.setAttribute("aria-expanded", String(shouldShow));
    if (shouldShow) {
      $("#rankingViewNameInput")?.focus();
    }
  });

  const form = $("#rankingSaveForm");
  if (!form || !state.currentUser) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const input = $("#rankingViewNameInput");
    const message = $("#rankingSaveMessage");
    const submit = form.querySelector("button[type='submit']");
    const name = input.value.trim();
    if (!name) return;
    message.textContent = "";
    submit.disabled = true;
    try {
      await sendJson("/preferences/dashboard-views", {
        body: {
          name,
          view_type: "ranking",
          chart_type: "ranking_table",
          filters: savedRankingFiltersPayload(),
          is_default: false,
          position: 0,
        },
      });
      input.value = "";
      message.textContent = t("rankingViewSaved");
    } catch (_error) {
      message.textContent = t("rankingViewError");
    } finally {
      submit.disabled = false;
    }
  });
}

async function hydrateEventsCalendar(query = "", selector = "#eventViewResults", shouldRender = () => true) {
  const node = $(selector);
  if (!node) return;
  let calendarDate = eventsCalendarDate();
  const favoriteFilterActive = favoritesOnly("events");
  if (favoriteFilterActive) {
    const favoriteDetails = await getFavoriteEventDetailsForSection(query);
    if (state.eventsFavoriteCalendarAutoFocus) {
      focusEventsCalendarOnFirstFavorite(favoriteDetails);
      state.eventsFavoriteCalendarAutoFocus = false;
      calendarDate = eventsCalendarDate();
    }
    if (!shouldRender()) return;
    const sortedFavoriteEvents = sortFavoriteEventDetails(favoriteDetails).map((detail) => detail.event).filter(Boolean);
    const navigationItems = favoriteEventNavigationItems(favoriteDetails);
    syncEventCalendarNavigationSelection(navigationItems, calendarDate);
    renderHomeCalendar(selector, sortedFavoriteEvents, calendarDate, {
      navScope: "events",
      wrapperClass: "home-calendar full-calendar",
      maxVisibleLanes: 6,
      extraControls: renderEventCalendarNavigation(navigationItems, calendarDate, { favorite: true }),
      focusedEventKey: state.eventsCalendarNavigationKey,
    });
    return;
  }
  const monthStart = new Date(calendarDate.getFullYear(), calendarDate.getMonth(), 1);
  const monthEnd = new Date(calendarDate.getFullYear(), calendarDate.getMonth() + 1, 0);
  const timeFilters = eventTimeFilters();
  const filterStart = parseLocalDate(timeFilters.startDate);
  const filterEnd = parseLocalDate(timeFilters.endDate);
  const requestStart = filterStart && filterStart > monthStart ? filterStart : monthStart;
  const requestEnd = filterEnd && filterEnd < monthEnd ? filterEnd : monthEnd;
  if (requestStart > requestEnd) {
    const navigationItems = await fetchFilteredEventCalendarNavigationItems(query);
    if (!shouldRender()) return;
    syncEventCalendarNavigationSelection(navigationItems, calendarDate);
    renderHomeCalendar(selector, [], calendarDate, {
      navScope: "events",
      wrapperClass: "home-calendar full-calendar",
      maxVisibleLanes: 6,
      extraControls: renderEventCalendarNavigation(navigationItems, calendarDate),
      focusedEventKey: state.eventsCalendarNavigationKey,
    });
    return;
  }
  const [events, navigationItems] = await Promise.all([
    getJson("/events/calendar", eventCalendarQueryParams(query, {
      startDate: formatLocalIso(requestStart),
      endDate: formatLocalIso(requestEnd),
    })),
    fetchFilteredEventCalendarNavigationItems(query),
  ]);
  if (!shouldRender()) return;
  syncEventCalendarNavigationSelection(navigationItems, calendarDate);
  renderHomeCalendar(selector, filterFavoriteEvents(events), calendarDate, {
    navScope: "events",
    wrapperClass: "home-calendar full-calendar",
    maxVisibleLanes: 6,
    extraControls: renderEventCalendarNavigation(navigationItems, calendarDate),
    focusedEventKey: state.eventsCalendarNavigationKey,
  });
}

async function changeEventsCalendarMonth(delta) {
  state.eventsCalendarMonthOffset += delta;
  try {
    await hydrateEventsCalendar($("#eventSearchInput")?.value.trim() || "");
  } catch (error) {
    const node = $("#eventViewResults");
    if (node) node.innerHTML = errorState(error);
  }
}

async function resetEventsCalendarMonth() {
  state.eventsCalendarMonthOffset = 0;
  try {
    await hydrateEventsCalendar($("#eventSearchInput")?.value.trim() || "");
  } catch (error) {
    const node = $("#eventViewResults");
    if (node) node.innerHTML = errorState(error);
  }
}

function renderEventCalendarNavigation(items, monthDate, options = {}) {
  if (!items.length) return "";
  const currentIndex = syncEventCalendarNavigationSelection(items, monthDate);
  const currentItem = items[currentIndex] || items[0];
  const currentTitle = [
    currentItem.event.name,
    formatReadableDateRange(currentItem.event),
  ].filter(Boolean).join(" · ");
  const countLabel = `${currentIndex + 1}/${items.length}`;
  const disabled = items.length < 2 ? "disabled" : "";
  const ariaLabel = options.favorite ? t("favoriteEventNavigation") : t("eventNavigation");
  const previousLabel = options.favorite ? t("previousFavoriteEvent") : t("previousEvent");
  const nextLabel = options.favorite ? t("nextFavoriteEvent") : t("nextEvent");
  return `
    <div class="calendar-favorite-nav calendar-event-nav" aria-label="${escapeHtml(ariaLabel)}">
      <button
        class="calendar-nav-button calendar-favorite-nav-button"
        type="button"
        data-event-calendar-nav="-1"
        aria-label="${escapeHtml(previousLabel)}"
        ${disabled}
      >&#8249;</button>
      <span class="calendar-favorite-nav-label" aria-label="${escapeHtml(currentTitle)}">${escapeHtml(countLabel)}</span>
      <button
        class="calendar-nav-button calendar-favorite-nav-button"
        type="button"
        data-event-calendar-nav="1"
        aria-label="${escapeHtml(nextLabel)}"
        ${disabled}
      >&#8250;</button>
    </div>
  `;
}

async function moveEventsCalendarToNavigationEvent(delta) {
  const resultsNode = $("#eventViewResults");
  const query = $("#eventSearchInput")?.value.trim() || "";
  const requestId = ++eventSearchRequestId;
  if (resultsNode) {
    resultsNode.classList.add("is-updating");
    resultsNode.setAttribute("aria-busy", "true");
  }
  try {
    const items = favoritesOnly("events")
      ? favoriteEventNavigationItems(await getFavoriteEventDetailsForSection(query))
      : await fetchFilteredEventCalendarNavigationItems(query);
    if (items.length) {
      const currentIndex = eventCalendarNavigationIndex(items, eventsCalendarDate());
      const nextIndex = (currentIndex + delta + items.length) % items.length;
      state.eventsCalendarNavigationKey = items[nextIndex].key;
      state.eventsCalendarMonthOffset = calendarMonthOffsetForDate(items[nextIndex].date);
    }
    await hydrateEventsCalendar(query, "#eventViewResults", () => requestId === eventSearchRequestId);
  } catch (error) {
    if (resultsNode) resultsNode.innerHTML = errorState(error);
  } finally {
    if (requestId === eventSearchRequestId && resultsNode) {
      resultsNode.classList.remove("is-updating");
      resultsNode.setAttribute("aria-busy", "false");
    }
  }
}

function eventListItemKey(event = {}) {
  return [
    event.calendar_entry_id ? `calendar-${event.calendar_entry_id}` : `event-${event.id || "none"}`,
    event.name || "",
    event.start_date || "",
    event.end_date || "",
  ].join("|");
}

function eventListDisplayItems(events = []) {
  return events.filter((event) => (
    !event.id ||
    event.calendar_entry_id ||
    !events.some((other) => (
      other !== event &&
      other.id === event.id &&
      other.calendar_entry_id &&
      other.start_date === event.start_date &&
      other.end_date === event.end_date
    ))
  ));
}

function splitEventListFullRows(events = [], hasMore = false) {
  const remainder = events.length % EVENT_CARD_COLUMN_COUNT;
  if (!remainder || events.length <= EVENT_CARD_COLUMN_COUNT) return { visible: events, pending: [] };
  const visibleCount = events.length - remainder;
  return {
    visible: events.slice(0, visibleCount),
    pending: hasMore ? events.slice(visibleCount) : [],
  };
}

function renderEventList(selector, events, options = {}) {
  const node = $(selector);
  if (!node) return;
  const displayEvents = eventListDisplayItems(events);
  const rowSplit = splitEventListFullRows(displayEvents, true);
  const visibleEvents = rowSplit.visible.length ? rowSplit.visible : displayEvents;
  if (!visibleEvents.length) {
    node.innerHTML = emptyState();
    return;
  }
  node.innerHTML = `<div class="grid-3 event-results-list">${visibleEvents.map((event) => {
    const period = formatReadableDateRange(event);
    const meta = [
      event.location,
      event.venue,
    ].filter(Boolean).join(" · ");
    const pills = [
      { label: displayEnumValue(event.discipline) },
      { label: displayEnumValue(event.category) },
      { label: event.level },
    ];
    if (event.is_calendar_only) {
      pills.push({ label: t("calendarOnly") });
    }
    return entityCard(
      eventCardTitle(event, period),
      meta,
      pills,
      event.id ? `#/events/${event.id}` : "",
      favoriteButton("event", event.id, state.favoriteEventIds.has(Number(event.id))),
    );
  }).join("")}</div>${options.hasMore ? renderLoadMoreButton("events", t("loadMoreEvents")) : ""}`;
  bindFavoriteButtons();
}

function buildCalendarWeeks(monthDate) {
  const firstOfMonth = new Date(monthDate.getFullYear(), monthDate.getMonth(), 1);
  const lastOfMonth = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0);
  let cursor = startOfWeekMonday(firstOfMonth);
  const weeks = [];
  while (cursor <= lastOfMonth || weeks.length < 5) {
    const days = Array.from({ length: 7 }, (_, index) => addDays(cursor, index));
    weeks.push({
      start: days[0],
      end: days[6],
      days,
    });
    cursor = addDays(cursor, 7);
  }
  return weeks;
}

function calendarStatusClass(event) {
  if (event.calendar_status === "completed_with_results") return "has-results";
  if (event.calendar_status === "completed_no_results") return "missing-results";
  if (event.calendar_status === "ongoing") return "ongoing";
  return "upcoming";
}

function buildWeekEventSegments(events, week) {
  const segments = [];
  events.forEach((event) => {
    const eventStart = parseLocalDate(event.start_date) || new Date(event.year, 0, 1);
    const eventEnd = parseLocalDate(event.end_date) || eventStart;
    if (eventEnd < week.start || eventStart > week.end) return;

    const segmentStart = eventStart < week.start ? week.start : eventStart;
    const segmentEnd = eventEnd > week.end ? week.end : eventEnd;
    segments.push({
      event,
      startColumn: ((segmentStart.getDay() + 6) % 7) + 1,
      endColumn: ((segmentEnd.getDay() + 6) % 7) + 1,
    });
  });

  segments.sort((left, right) => (
    left.startColumn - right.startColumn ||
    right.endColumn - left.endColumn ||
    left.event.name.localeCompare(right.event.name)
  ));

  const lanes = [];
  segments.forEach((segment) => {
    let lane = lanes.findIndex((laneEnd) => segment.startColumn > laneEnd);
    if (lane === -1) {
      lane = lanes.length;
      lanes.push(0);
    }
    lanes[lane] = segment.endColumn;
    segment.lane = lane;
  });
  return segments;
}

function renderHomeCalendar(selector, events, monthDate = TODAY, options = {}) {
  const node = $(selector);
  const weeks = buildCalendarWeeks(monthDate);
  const labels = weekdayLabels();
  const sortedEvents = sortCalendarItems(events).filter((event) => event.start_date || event.end_date);
  const monthName = monthLabel(monthDate);
  const monthTitle = monthTitleParts(monthDate);
  const navScope = options.navScope || "home";
  const wrapperClass = options.wrapperClass || "home-calendar";
  const maxVisibleLanes = options.maxVisibleLanes || 4;
  const extraControls = options.extraControls || "";
  const focusedEventKey = options.focusedEventKey || "";

  node.innerHTML = `
    <div class="${wrapperClass}" aria-label="${escapeHtml(`${t("calendarMonth")} ${monthName}`)}">
      <div class="calendar-toolbar">
        <div class="calendar-title-row">
          <button class="calendar-nav-button" type="button" data-calendar-nav="-1" data-calendar-nav-scope="${navScope}" aria-label="${t("previousMonth")}">&#8249;</button>
          <div class="calendar-title-label">
            <span class="calendar-kicker">${t("calendarMonth")}</span>
            <strong>${escapeHtml(monthTitle.month)}</strong>
            <span class="calendar-year">${escapeHtml(monthTitle.year)}</span>
          </div>
          <button class="calendar-nav-button" type="button" data-calendar-nav="1" data-calendar-nav-scope="${navScope}" aria-label="${t("nextMonth")}">&#8250;</button>
          <button class="calendar-today-button" type="button" data-calendar-today-scope="${navScope}" aria-label="${t("today")}">${t("today")}</button>
          ${extraControls}
        </div>
        <div class="calendar-legend" aria-label="${t("status")}">
          <span><i class="legend-dot has-results"></i>${t("resultsAvailable")}</span>
          <span><i class="legend-dot missing-results"></i>${t("resultsMissing")}</span>
          <span><i class="legend-dot ongoing"></i>${t("ongoing")}</span>
          <span><i class="legend-dot upcoming"></i>${t("upcoming")}</span>
        </div>
      </div>
      <div class="calendar-weekdays">
        ${labels.map((label) => `<span>${escapeHtml(label)}</span>`).join("")}
      </div>
      <div class="calendar-month-grid">
        ${weeks.map((week) => {
          const segments = buildWeekEventSegments(sortedEvents, week);
          const visibleSegments = segments.filter((segment) => segment.lane < maxVisibleLanes);
          const hiddenCount = segments.length - visibleSegments.length;
          const lanes = Math.max(1, Math.min(maxVisibleLanes, segments.length));
          return `
            <div class="calendar-week" style="--calendar-lanes: ${lanes};">
              <div class="calendar-days">
                ${week.days.map((day) => {
                  const isCurrentMonth = sameMonth(day, monthDate);
                  const isToday = sameDay(day, TODAY);
                  const todayAttributes = isToday
                    ? `data-today-label="${escapeHtml(t("today"))}" tabindex="0"`
                    : "";
                  return `
                    <div class="calendar-day ${isCurrentMonth ? "" : "outside"} ${isToday ? "today" : ""}" ${todayAttributes}>
                      <span class="calendar-day-number">${day.getDate()}</span>
                      ${isToday ? `<span class="sr-only">${t("today")}</span>` : ""}
                    </div>
                  `;
                }).join("")}
              </div>
              <div class="calendar-bars">
                ${visibleSegments.map((segment) => {
                  const event = segment.event;
                  const href = event.id ? `#/events/${event.id}` : "";
                  const accessibilityLabel = [
                    event.name,
                    formatDateRange(event),
                    event.calendar_status,
                    event.is_calendar_only ? t("calendarOnly") : "",
                  ].filter(Boolean).join(" · ");
                  const element = `
                    <span class="calendar-event-label">${escapeHtml(event.name)}</span>
                  `;
                  const style = `grid-column: ${segment.startColumn} / ${segment.endColumn + 1}; grid-row: ${segment.lane + 1};`;
                  const isFocused = focusedEventKey && eventCalendarNavigationKey(event) === focusedEventKey;
                  const className = `calendar-event-bar ${calendarStatusClass(event)}${isFocused ? " is-calendar-focus" : ""}`;
                  return href
                    ? `<a class="${className}" href="${href}" style="${style}" aria-label="${escapeHtml(accessibilityLabel)}">${element}</a>`
                    : `<span class="${className}" style="${style}" aria-label="${escapeHtml(accessibilityLabel)}">${element}</span>`;
                }).join("")}
                ${hiddenCount > 0 ? `<span class="calendar-more" style="grid-column: 1 / 8; grid-row: ${maxVisibleLanes + 1};">+${hiddenCount}</span>` : ""}
              </div>
            </div>
          `;
        }).join("")}
      </div>
    </div>
  `;
  node.querySelectorAll("[data-calendar-nav]").forEach((button) => {
    button.addEventListener("click", () => {
      if (button.dataset.calendarNavScope === "events") {
        const delta = Number(button.dataset.calendarNav || 0);
        changeEventsCalendarMonth(delta);
      }
    });
  });
  node.querySelectorAll("[data-calendar-today-scope]").forEach((button) => {
    button.addEventListener("click", () => {
      if (button.dataset.calendarTodayScope === "events") {
        resetEventsCalendarMonth();
      }
    });
  });
  node.querySelectorAll("[data-event-calendar-nav]").forEach((button) => {
    button.addEventListener("click", () => {
      moveEventsCalendarToNavigationEvent(Number(button.dataset.eventCalendarNav || 0));
    });
  });
}

function renderRankingContext(payload) {
  const timePreview = timeFilterPreview(rankingTimeFilters());
  const selectedLevels = filterValues("level", "rankings");
  const scoringCycles = rankingScoringCycleValues();
  const hasMultipleScoringCycles = rankingHasMultipleScoringCycles(payload);
  const parts = [
    "Ranking",
    rankingDiscipline(),
    ...filterValues("category", "rankings").map((value) => (value === "junior" ? t("junior") : t("senior"))),
    ...(selectedLevels.length ? [`${t("levelFilter")}: ${selectedLevels.map(eventLevelAbbreviation).join(", ")}`] : []),
    ...rankingApparatusValues(),
    rankingMetricLabel(rankingSortBy()),
  ];
  if (timePreview) {
    parts.push(`${t("timeInterval")}: ${timePreview}`);
  } else if (scoringCycles.length) {
    parts.push(`${t("scoringCycle")}: ${scoringCycles.join(", ")}`);
  } else if (payload?.scoring_cycle?.label) {
    parts.push(`${t("scoringCycle")} ${payload.scoring_cycle.label}`);
  } else if (payload?.available_scoring_cycles?.length) {
    parts.push(`${t("scoringCycle")} ${payload.available_scoring_cycles.map((cycle) => cycle.label).join(", ")}`);
  }
  if (!parts.length) return "";
  const rankingDetails = parts.slice(1).join(" · ");
  return `
    <div class="context-note sticky-context-note">
      <div class="context-note-copy">
        <span><strong class="context-note-lead">RANKING</strong>${rankingDetails ? ` · ${escapeHtml(rankingDetails)}` : ""}</span>
        ${hasMultipleScoringCycles ? `<span>${escapeHtml(t("analyticsMultipleScoringCyclesNotice"))}</span>` : ""}
      </div>
      ${renderStickyContextScrollButton("rankings")}
    </div>
  `;
}

function rankingHasMultipleScoringCycles(payload = {}) {
  const explicitCycles = rankingScoringCycleValues();
  if (explicitCycles.length > 1) return true;
  if ((payload?.available_scoring_cycles || []).length > 1) return true;
  return (payload?.warnings || []).some(warningIsMultipleScoringCycles);
}

function rankingWarningMessages(payload = {}) {
  const selectedMetric = rankingSortBy();
  const selectedApparatuses = filterValues("apparatus", "rankings");
  const payloadWarnings = (payload?.warnings || []).filter((warning) => !warningIsMultipleScoringCycles(warning));
  const rankingWarnings = (payload.ranking || [])
    .flatMap((entry) => entry.data_warnings || [])
    .filter((warning) => {
      if (executionEstimateWarningFlags(warning)) {
        return selectedMetric === "execution_estimate";
      }
      if (warningIsVaultAttemptOrder(warning)) {
        return selectedApparatuses.includes("VT") || selectedApparatuses.includes("VT AVG");
      }
      return true;
    });
  return [
    ...(selectedMetric === "execution_estimate" ? [t("estimatedEScoreRankingNotice")] : []),
    ...localizedBackendWarnings([
      ...payloadWarnings,
      ...rankingWarnings,
    ]),
  ];
}

function renderRankingWarningStack(payload = {}) {
  return renderDataWarningStack(rankingWarningMessages(payload), "ranking-warning-stack");
}

function timeFilterPreview(filters) {
  const startValue = filters.startPeriod || formatDateInputValue(filters.startDate);
  const endValue = filters.endPeriod || formatDateInputValue(filters.endDate);
  if (startValue && endValue) return `${startValue} - ${endValue}`;
  if (startValue) return `${t("fromDate")}: ${startValue}`;
  if (endValue) return `${t("toDate")}: ${endValue}`;
  return "";
}

function timeFilterButtonLabel(filters) {
  const preview = timeFilterPreview(filters);
  return preview ? `${t("timeInterval")}: ${preview}` : t("timeInterval");
}

function renderRankingTimeFilter() {
  const filters = rankingTimeFilters();
  const label = timeFilterButtonLabel(filters);
  return `
    <details class="ranking-time-filter" data-time-filter-scope="rankings" ${timeFilterIsOpen("rankings") ? "open" : ""}>
      <summary
        class="filter-button ranking-time-summary"
        aria-pressed="${rankingHasTimeFilter()}"
        data-time-filter-summary
      ><span class="filter-summary-label">${escapeHtml(label)}</span></summary>
      <div class="ranking-time-panel">
        <div class="ranking-time-inputs">
          ${renderRankingDateWheel("startDate", t("fromDate"), filters.startDate, filters.startPeriod)}
          ${renderRankingDateWheel("endDate", t("toDate"), filters.endDate, filters.endPeriod)}
        </div>
      </div>
    </details>
  `;
}

function renderEventTimeFilter() {
  const filters = eventTimeFilters();
  const label = timeFilterButtonLabel(filters);
  return `
    <details class="ranking-time-filter event-time-filter" data-time-filter-scope="events" ${timeFilterIsOpen("events") ? "open" : ""}>
      <summary
        class="filter-button ranking-time-summary"
        aria-pressed="${eventHasTimeFilter()}"
        data-time-filter-summary
      ><span class="filter-summary-label">${escapeHtml(label)}</span></summary>
      <div class="ranking-time-panel">
        <div class="ranking-time-inputs">
          ${renderEventDateWheel("startDate", t("fromDate"), filters.startDate, filters.startPeriod)}
          ${renderEventDateWheel("endDate", t("toDate"), filters.endDate, filters.endPeriod)}
        </div>
      </div>
    </details>
  `;
}

function renderRankingSavePanel() {
  if (!state.currentUser) {
    return "";
  }
  return `
    <div class="saved-ranking-panel">
      <button class="quiet-button ranking-outline-action ranking-save-toggle" type="button" id="showRankingSaveFormButton" aria-controls="rankingSaveFormShell" aria-expanded="false">${t("saveRankingView")}</button>
      <section class="panel saved-ranking-form-shell" id="rankingSaveFormShell" hidden>
        <form class="saved-ranking-form" id="rankingSaveForm">
          <label>
            <span>${t("rankingViewName")}</span>
            <span class="saved-ranking-input-shell">
              <input id="rankingViewNameInput" type="text" maxlength="120" required placeholder="${t("rankingViewNamePlaceholder")}">
              <button class="saved-ranking-submit" type="submit">${t("save")}</button>
            </span>
          </label>
          <span class="saved-ranking-message" id="rankingSaveMessage" role="status" aria-live="polite"></span>
        </form>
        <p>${t("filters")}: ${escapeHtml(rankingFilterSummary())}</p>
      </section>
    </div>
  `;
}

function renderRankingList(selector, payloadOrRankings) {
  const node = $(selector);
  if (!node) return;
  const payload = Array.isArray(payloadOrRankings) ? { ranking: payloadOrRankings } : (payloadOrRankings || {});
  const rankings = payload.ranking || [];
  const pagination = payload.pagination || {};
  const context = renderRankingContext(payload);
  const contextInStickyHost = renderContextInStickyHost("rankingContextHost", context);
  const inlineContext = contextInStickyHost ? "" : context;
  const warningStack = renderRankingWarningStack(payload);
  const selectedMetric = rankingSortBy();
  const selectedApparatuses = filterValues("apparatus", "rankings");
  const showVaultAttempts = selector === "#rankingResults" &&
    selectedApparatuses.length === 1 &&
    selectedApparatuses[0] === "VT";
  if (!rankings.length) {
    const unavailableMetricEmpty = rankingUnavailableMetricEmptyState(selectedMetric, selectedApparatuses);
    node.innerHTML = `${inlineContext}${unavailableMetricEmpty || emptyState()}${warningStack}`;
    return;
  }
  node.innerHTML = `
    ${inlineContext}
    ${renderLeaderboardList(rankings, {
      className: "ranking-results-list",
      selectedMetric,
      returnContext: "ranking",
      showVaultAttempts,
      showTags: false,
      metaForEntry: (entry) => {
        const eventDate = entry.date ? formatReadableDate(entry.date) : "";
        const eventYear = entry.year ? `${t("eventYear")} ${entry.year}` : "";
        return [entry.country, entry.event_name, eventDate || eventYear];
      },
    })}
    ${pagination.hasMore ? renderLoadMoreButton("rankings", t("loadMoreScores")) : ""}
    ${warningStack}
  `;
}

function athleteSearchRoute(query) {
  return query ? `/athletes?search=${encodeURIComponent(query)}` : "/athletes";
}

function syncAthleteSearchRoute(query) {
  if (!routeIsListSection("athletes")) return;
  const route = athleteSearchRoute(query);
  state.route = route;
  window.history.replaceState(null, "", `#${route}`);
  setActiveNav();
}

function athleteCardDisplayName(athlete = {}, fallback = "") {
  const firstName = String(athlete.first_name || "").trim();
  const lastName = String(athlete.last_name || "").trim();
  return [lastName, firstName].filter(Boolean).join(" ") || fallback;
}

function athleteSectionProfileHref(athleteId) {
  const params = new URLSearchParams({ from: "athletes" });
  const returnRoute = routeSection(state.route) === "athletes"
    ? state.route
    : SECTION_BASE_ROUTES.athletes;
  params.set("return_to", returnRoute);
  return `#/athletes/${athleteId}?${params.toString()}`;
}

function leverageIdLabel(id) {
  return `${t("leverageId")} ${id}`;
}

function compactIdLabel(id) {
  return `ID ${id}`;
}

function renderAthleteCards(athletes) {
  if (!athletes.length) return emptyState();
  return `<div class="grid-3 athlete-results-list">${athletes.map((athlete) => {
    const pills = [
      { label: athlete.discipline, variant: "brand" },
      { label: athlete.country || t("country") },
      { label: compactIdLabel(athlete.id) },
      ...(athlete.birth_year ? [{ label: String(athlete.birth_year) }] : []),
    ];
    return entityCard(
      escapeHtml(athleteCardDisplayName(athlete, `${t("athlete")} ${athlete.id}`)),
      athlete.world_gymnastics_status || "",
      pills,
      athleteSectionProfileHref(athlete.id),
      favoriteButton("athlete", athlete.id, state.favoriteAthleteIds.has(Number(athlete.id))),
    );
  }).join("")}</div>`;
}

function renderAthleteResultsPage(athletes, hasMore = false) {
  return `
    ${renderAthleteCards(athletes)}
    ${hasMore ? renderLoadMoreButton("athletes", t("loadMoreAthletes")) : ""}
  `;
}

function eventSearchRoute(query) {
  return query ? `/events?search=${encodeURIComponent(query)}` : "/events";
}

function syncEventSearchRoute(query) {
  const route = eventSearchRoute(query);
  state.route = route;
  window.history.replaceState(null, "", `#${route}`);
  setActiveNav();
}

function eventCardTitle(event = {}, period = "") {
  const fallbackName = `${t("event")} ${event.id || ""}`.trim();
  const name = event.name || fallbackName;
  return `
    <span class="event-card-title">
      <span class="event-card-name">${escapeHtml(name)}</span>
      ${period ? `<span class="event-card-date">${escapeHtml(period)}</span>` : ""}
    </span>
  `;
}

function currentParams() {
  const [, query = ""] = state.route.split("?");
  return new URLSearchParams(query);
}

function syncFilterButtonState(button) {
  if (!button) return;
  const scope = button.dataset.filterScope || currentFilterScope();
  button.setAttribute("aria-pressed", String(filterIsActive(
    button.dataset.filterType,
    button.dataset.filterValue,
    scope,
  )));
}

function syncSectionFilterButtons(scope) {
  document.querySelectorAll(`[data-filter-scope="${scope}"]`).forEach(syncFilterButtonState);
}

function syncEventLevelFilterMenu() {
  const summary = document.querySelector(".event-level-filter .filter-menu-summary");
  if (!summary) return;
  const selectedLevels = filterValues("level", "events");
  const label = selectedLevels.length
    ? `${t("levelFilter")}: ${selectedLevels.map(eventLevelAbbreviation).join(", ")}`
    : t("levelFilter");
  summary.textContent = label;
  summary.setAttribute("aria-pressed", String(Boolean(selectedLevels.length)));
}

function syncRankingLevelFilterMenu() {
  const summary = document.querySelector(".ranking-level-filter .filter-menu-summary");
  if (!summary) return;
  const selectedLevels = filterValues("level", "rankings");
  const label = selectedLevels.length
    ? `${t("levelFilter")}: ${selectedLevels.map(eventLevelAbbreviation).join(", ")}`
    : t("levelFilter");
  summary.textContent = label;
  summary.setAttribute("aria-pressed", String(Boolean(selectedLevels.length)));
}

function syncRankingScoringCycleFilterMenu() {
  const summary = document.querySelector(".ranking-cycle-filter .filter-menu-summary");
  const selectedCycles = rankingScoringCycleValues();
  document.querySelectorAll(".ranking-cycle-filter [data-filter-type=\"scoringCycle\"]").forEach(syncFilterButtonState);
  if (!summary) return;
  const allCyclesSelected = SCORING_CYCLE_FILTERS.every((cycle) => selectedCycles.includes(cycle));
  const label = allCyclesSelected
    ? `${t("scoringCycle")}: ${t("allCycles")}`
    : selectedCycles.length
      ? `${t("scoringCycle")}: ${selectedCycles.join(", ")}`
      : t("scoringCycle");
  summary.textContent = label;
  summary.setAttribute("aria-pressed", String(Boolean(selectedCycles.length)));
}

function syncTimeFilterUi(scope) {
  const filters = timeFiltersForScope(scope);
  const details = document.querySelector(`[data-time-filter-scope="${scope}"]`);
  const summary = details?.querySelector("[data-time-filter-summary]");
  if (summary) {
    const label = timeFilterButtonLabel(filters);
    const hasFilter = scope === "events" ? eventHasTimeFilter() : rankingHasTimeFilter();
    summary.setAttribute("aria-pressed", String(hasFilter));
    const labelNode = summary.querySelector(".filter-summary-label");
    if (labelNode) labelNode.textContent = label;
  }
  document.querySelectorAll(`[data-date-wheel-text-scope="${scope}"]`).forEach((input) => {
    const field = input.dataset.dateWheelTextField;
    if (!field) return;
    input.value = filters[field === "startDate" ? "startPeriod" : "endPeriod"] || formatDateInputValue(filters[field]);
    input.classList.remove("is-invalid");
  });
}

async function renderAthletes() {
  rememberAthleteListRoute();
  const params = currentParams();
  const search = params.get("search") || "";
  await ensureFavoritesLoaded().catch(() => {});
  setApp(`
    ${pageHeading("athletesHeading", "athletesIntro")}
    <div class="section-search-row athlete-search-row">
      <form class="search-form section-search-form" id="athleteSearchForm">
        ${searchInputControl("athleteSearchInput", search, t("athleteSearchPlaceholder"))}
      </form>
      <div class="section-filter-stack">
        <div class="toolbar section-filter-row athlete-filter-row">
          ${filterButton("MAG", "discipline", "MAG", "athletes")}
          ${filterButton("WAG", "discipline", "WAG", "athletes")}
          ${filterButton(t("senior"), "category", "senior", "athletes")}
          ${filterButton(t("junior"), "category", "junior", "athletes")}
        </div>
        <div class="toolbar section-filter-row athlete-sort-row">
          ${athleteSortModeControl()}
          <div class="filter-action-group">
            ${state.currentUser ? filterButton(t("favoritesFilter"), "favoritesOnly", "true", "athletes", "section-favorite-filter") : ""}
            <button class="quiet-button filter-clear-button filters-reset-button" type="button" id="clearAthleteFiltersButton">${t("clearRankingFilters")}</button>
          </div>
        </div>
      </div>
    </div>
    <div class="athlete-results" id="athleteResults" aria-live="polite">${loadingState()}</div>
  `);
  const form = $("#athleteSearchForm");
  const input = $("#athleteSearchInput");
  const resultsNode = $("#athleteResults");
  let searchTimer;
  let athletePageItems = [];
  let athleteHasMore = false;
  let athletePageOffset = 0;
  const loadAthletes = async (query, options = {}) => {
    const { showLoading = false, updateRoute = false, append = false } = options;
    const requestId = ++athleteSearchRequestId;
    const favoriteFilterActive = favoritesOnly("athletes");
    if (updateRoute) syncAthleteSearchRoute(query);
    if (showLoading && !append) resultsNode.innerHTML = loadingState();
    resultsNode.classList.add("is-updating");
    resultsNode.setAttribute("aria-busy", "true");
    try {
      if (favoriteFilterActive) {
        const favoriteDetails = await getFavoriteAthleteDetailsForSection(query);
        if (requestId !== athleteSearchRequestId) return;
        athletePageItems = [];
        athleteHasMore = false;
        athletePageOffset = 0;
        resultsNode.innerHTML = renderFavoriteAthletes(favoriteDetails);
        bindFavoriteButtons();
        return;
      }
      const offset = append ? athletePageOffset : 0;
      const athletes = await getJson("/athletes/", {
        search: query,
        discipline: singleFilterParam("discipline", "athletes"),
        category: filterValues("category", "athletes"),
        sort_by: state.athleteSortMode,
        limit: ATHLETE_SECTION_LIMIT + 1,
        offset,
      });
      if (requestId !== athleteSearchRequestId) return;
      const pageItems = filterFavoriteAthletes(athletes).slice(0, ATHLETE_SECTION_LIMIT);
      athleteHasMore = athletes.length > ATHLETE_SECTION_LIMIT;
      athletePageOffset = offset + pageItems.length;
      athletePageItems = append
        ? mergeUniqueBy(athletePageItems, pageItems, (athlete) => athlete.id)
        : pageItems;
      resultsNode.innerHTML = renderAthleteResultsPage(athletePageItems, athleteHasMore);
      bindFavoriteButtons();
      bindLoadMoreButton("athletes", () => loadAthletes(input.value.trim(), { append: true }));
    } catch (error) {
      if (requestId !== athleteSearchRequestId) return;
      resultsNode.innerHTML = errorState(error);
    } finally {
      if (requestId === athleteSearchRequestId) {
        resultsNode.classList.remove("is-updating");
        resultsNode.setAttribute("aria-busy", "false");
      }
    }
  };
  const refreshAthleteResults = ({ showLoading = true, scroll = "records" } = {}) => {
    window.clearTimeout(searchTimer);
    return refreshListFromFilter(loadAthletes(input.value.trim(), { showLoading }), "athletes", { scroll });
  };
  setSectionFilterRefresher("athletes", refreshAthleteResults);
  bindFilterButtons(handleSectionFilterChange);
  bindAthleteClearFilters();
  bindAthleteSortModeControl(() => {
    refreshSectionFiltersAtRecordsTop("athletes");
  });
  bindSearchClearButtons();

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const query = input.value.trim();
    window.clearTimeout(searchTimer);
    refreshListFromFilter(loadAthletes(query, { showLoading: true, updateRoute: true }), "athletes");
  });
  input.addEventListener("input", () => {
    const query = input.value.trim();
    syncAthleteSearchRoute(query);
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => {
      refreshListFromFilter(loadAthletes(query), "athletes");
    }, 140);
  });
  await loadAthletes(search, { showLoading: true });
}

async function renderEvents() {
  const params = currentParams();
  const search = params.get("search") || "";
  await ensureFavoritesLoaded().catch(() => {});
  setApp(`
    ${pageHeading("eventsHeading", "eventsIntro")}
    <div class="section-search-row">
      <form class="search-form section-search-form" id="eventSearchForm">
        ${searchInputControl("eventSearchInput", search, t("eventSearchPlaceholder"))}
      </form>
      <div class="section-filter-stack">
        <div class="toolbar section-filter-row event-filter-row">
          ${filterButton("MAG", "discipline", "MAG", "events")}
          ${filterButton("WAG", "discipline", "WAG", "events")}
          ${filterButton(t("senior"), "category", "senior", "events")}
          ${filterButton(t("junior"), "category", "junior", "events")}
          ${renderEventLevelFilter()}
          ${renderEventTimeFilter()}
        </div>
        <div class="toolbar section-filter-row event-view-row">
          ${eventViewModeControl()}
          <div class="filter-action-group">
            ${state.currentUser ? filterButton(t("favoritesFilter"), "favoritesOnly", "true", "events", "section-favorite-filter") : ""}
            <button class="quiet-button filter-clear-button filters-reset-button" type="button" id="clearEventFiltersButton">${t("clearRankingFilters")}</button>
          </div>
        </div>
      </div>
    </div>
    <section class="event-list-panel event-view-panel">
      <div class="event-live-results" id="eventViewResults" aria-live="polite">${loadingState()}</div>
    </section>
  `);
  const form = $("#eventSearchForm");
  const input = $("#eventSearchInput");
  const resultsNode = $("#eventViewResults");
  let searchTimer;
  let eventPageItems = [];
  let eventHasMore = false;
  let eventPageOffset = 0;
  let eventPendingItems = [];
  let eventRawExhausted = false;
  const resetEventPagination = () => {
    eventPageItems = [];
    eventHasMore = false;
    eventPageOffset = 0;
    eventPendingItems = [];
    eventRawExhausted = false;
  };
  const fetchNextEventDisplayBatch = async (query) => {
    const timeFilters = eventTimeFilters();
    const events = await getJson("/events/calendar", {
      search: query,
      discipline: filterValues("discipline", "events"),
      category: filterValues("category", "events"),
      level: filterValues("level", "events"),
      start_date: timeFilters.startDate,
      end_date: timeFilters.endDate,
      as_of: formatLocalIso(TODAY),
      limit: EVENT_SECTION_LIMIT,
      offset: eventPageOffset,
    });
    eventPageOffset += events.length;
    if (events.length < EVENT_SECTION_LIMIT) {
      eventRawExhausted = true;
    }
    return eventListDisplayItems(filterFavoriteEvents(events));
  };
  const nextEventDisplayPage = async (query) => {
    let availableItems = eventListDisplayItems(eventPendingItems);
    while (availableItems.length < EVENT_SECTION_LIMIT && !eventRawExhausted) {
      const displayBatch = await fetchNextEventDisplayBatch(query);
      availableItems = eventListDisplayItems(mergeUniqueBy(availableItems, displayBatch, eventListItemKey));
    }
    let takeCount = Math.min(EVENT_SECTION_LIMIT, availableItems.length);
    if (takeCount > EVENT_CARD_COLUMN_COUNT) {
      takeCount -= takeCount % EVENT_CARD_COLUMN_COUNT;
    }
    const pageItems = availableItems.slice(0, takeCount);
    const leftoverItems = availableItems.slice(takeCount);
    eventPendingItems = eventRawExhausted && leftoverItems.length < EVENT_CARD_COLUMN_COUNT
      ? []
      : leftoverItems;
    eventHasMore = eventPendingItems.length > 0 || !eventRawExhausted;
    return pageItems;
  };
  const loadEvents = async (query, options = {}) => {
    const { showLoading = false, updateRoute = false, append = false } = options;
    const requestId = ++eventSearchRequestId;
    const favoriteFilterActive = favoritesOnly("events");
    if (updateRoute) syncEventSearchRoute(query);
    if (showLoading && !append) resultsNode.innerHTML = loadingState();
    resultsNode.classList.add("is-updating");
    resultsNode.setAttribute("aria-busy", "true");
    try {
      if (favoriteFilterActive) {
        const favoriteDetails = await getFavoriteEventDetailsForSection(query);
        if (requestId !== eventSearchRequestId) return;
        if (state.eventsFavoriteCalendarAutoFocus) {
          focusEventsCalendarOnFirstFavorite(favoriteDetails);
          state.eventsFavoriteCalendarAutoFocus = false;
        }
        resetEventPagination();
        resultsNode.innerHTML = renderFavoriteEvents(favoriteDetails);
        bindFavoriteButtons();
        return;
      }
      if (!append) resetEventPagination();
      const pageItems = await nextEventDisplayPage(query);
      if (requestId !== eventSearchRequestId) return;
      const nextPageItems = append
        ? eventListDisplayItems(mergeUniqueBy(eventPageItems, pageItems, eventListItemKey))
        : pageItems;
      const rowSplit = splitEventListFullRows(nextPageItems, eventHasMore);
      eventPageItems = rowSplit.visible;
      eventPendingItems = mergeUniqueBy(rowSplit.pending, eventPendingItems, eventListItemKey);
      renderEventList("#eventViewResults", eventPageItems, { hasMore: eventHasMore });
      bindLoadMoreButton("events", () => loadEvents(input.value.trim(), { append: true }));
    } catch (error) {
      if (requestId !== eventSearchRequestId) return;
      resultsNode.innerHTML = errorState(error);
    } finally {
      if (requestId === eventSearchRequestId) {
        resultsNode.classList.remove("is-updating");
        resultsNode.setAttribute("aria-busy", "false");
      }
    }
  };
  const loadEventView = async (query, options = {}) => {
    const { showLoading = false, updateRoute = false } = options;
    if (updateRoute) syncEventSearchRoute(query);
    if (state.eventsViewMode !== "calendar") {
      await loadEvents(query, { showLoading, updateRoute: false });
      return;
    }
    const requestId = ++eventSearchRequestId;
    if (showLoading) resultsNode.innerHTML = loadingState();
    resultsNode.classList.add("is-updating");
    resultsNode.setAttribute("aria-busy", "true");
    try {
      await hydrateEventsCalendar(query, "#eventViewResults", () => requestId === eventSearchRequestId);
    } catch (error) {
      if (requestId !== eventSearchRequestId) return;
      resultsNode.innerHTML = errorState(error);
    } finally {
      if (requestId === eventSearchRequestId) {
        resultsNode.classList.remove("is-updating");
        resultsNode.setAttribute("aria-busy", "false");
      }
    }
  };
  const refreshEventResults = ({ showLoading = true, scroll = "records" } = {}) => {
    window.clearTimeout(searchTimer);
    return refreshListFromFilter(loadEventView(input.value.trim(), { showLoading }).catch((error) => {
      resultsNode.innerHTML = errorState(error);
    }), "events", { scroll });
  };
  setSectionFilterRefresher("events", refreshEventResults);
  bindFilterButtons(handleSectionFilterChange);
  bindEventViewModeControl(() => {
    refreshSectionFiltersAtRecordsTop("events");
  });
  bindEventTimeFilters();
  bindEventClearFilters();
  bindSearchClearButtons();

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const query = input.value.trim();
    window.clearTimeout(searchTimer);
    refreshListFromFilter(loadEventView(query, { showLoading: true, updateRoute: true }), "events");
  });
  input.addEventListener("input", () => {
    const query = input.value.trim();
    syncEventSearchRoute(query);
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => {
      refreshListFromFilter(loadEventView(query), "events");
    }, 140);
  });
  try {
    await loadEventView(search, { showLoading: true });
  } catch (error) {
    resultsNode.innerHTML = errorState(error);
  }
}

async function renderRankings() {
  const savedViewId = currentParams().get("savedView");
  if (savedViewId) {
    await applySavedRankingViewFromRoute(savedViewId);
  }
  normalizeRankingTemporalFilterState();
  rankingApparatusValues();
  const apparatusFilters = rankingApparatusFilters();
  setApp(`
    ${pageHeading("rankingsHeading", "rankingsIntro")}
    <div class="ranking-filter-stack">
        <div class="ranking-filter-layout">
          <div class="ranking-filter-rows">
            <div class="toolbar ranking-filter-row">
              ${disciplineSegmentedControl()}
              ${filterButton(t("senior"), "category", "senior", "rankings")}
              ${filterButton(t("junior"), "category", "junior", "rankings")}
              ${renderRankingLevelFilter()}
              ${renderRankingTimeFilter()}
              ${renderRankingScoringCycleFilter()}
            </div>
            <div class="toolbar secondary-toolbar ranking-filter-row" id="rankingApparatusFilterRow" aria-label="${t("apparatus")}">
              ${apparatusFilters.map((apparatus) => filterButton(apparatus, "apparatus", apparatus, "rankings")).join("")}
            </div>
            <div class="toolbar secondary-toolbar ranking-filter-row ranking-metric-row" aria-label="${t("rankingMetric")}">
              ${renderRankingMetricFilters()}
            </div>
          </div>
          <div class="ranking-filter-actions">
            ${renderRankingSavePanel()}
            <div class="ranking-filter-bottom-actions">
              ${state.currentUser ? `<a class="quiet-button ranking-outline-action ranking-saved-shortcut" href="#/account?section=saved-rankings">${t("savedRankingsShortcut")}</a>` : ""}
              <button class="quiet-button filter-clear-button filters-reset-button" type="button" id="clearRankingFiltersButton">${t("clearRankingFilters")}</button>
            </div>
          </div>
        </div>
    </div>
    <div id="rankingContextHost" class="sticky-summary-host ranking-summary-sticky" data-sticky-summary="rankings"></div>
    <div id="rankingResults">${loadingState()}</div>
  `);
  let rankingPageEntries = [];
  let rankingPayloadWarnings = [];
  let rankingHasMore = false;
  let rankingPageOffset = 0;
  let rankingRequestId = 0;
  const loadRankingResults = async ({ showLoading = false } = {}) => {
    const requestId = ++rankingRequestId;
    const resultsNode = $("#rankingResults");
    if (showLoading) resultsNode.innerHTML = loadingState();
    try {
      const rankings = await getJson("/analytics/rankings", {
        ...rankingQueryParams(RANKING_SECTION_LIMIT + 1, 0),
      });
      if (requestId !== rankingRequestId) return;
      const pageEntries = rankings.ranking || [];
      rankingPayloadWarnings = uniqueTextItems(rankings.warnings || []);
      rankingHasMore = pageEntries.length > RANKING_SECTION_LIMIT;
      rankingPageEntries = pageEntries.slice(0, RANKING_SECTION_LIMIT);
      rankingPageOffset = rankingPageEntries.length;
      renderRankingList("#rankingResults", {
        ...rankings,
        ranking: rankingPageEntries,
        warnings: rankingPayloadWarnings,
        pagination: { hasMore: rankingHasMore },
      });
      bindLoadMoreButton("rankings", loadMoreRankingResults);
    } catch (error) {
      if (requestId !== rankingRequestId) return;
      resultsNode.innerHTML = errorState(error);
    }
  };
  const loadMoreRankingResults = async () => {
    const requestId = ++rankingRequestId;
    const rankings = await getJson("/analytics/rankings", {
      ...rankingQueryParams(RANKING_SECTION_LIMIT + 1, rankingPageOffset),
    });
    if (requestId !== rankingRequestId) return;
    const pageEntries = (rankings.ranking || []).slice(0, RANKING_SECTION_LIMIT);
    rankingPayloadWarnings = uniqueTextItems([
      ...rankingPayloadWarnings,
      ...(rankings.warnings || []),
    ]);
    rankingHasMore = (rankings.ranking || []).length > RANKING_SECTION_LIMIT;
    rankingPageOffset += pageEntries.length;
    rankingPageEntries = mergeUniqueBy(rankingPageEntries, pageEntries, (entry) => entry.result_id);
    renderRankingList("#rankingResults", {
      ...rankings,
      ranking: rankingPageEntries,
      warnings: rankingPayloadWarnings,
      pagination: { hasMore: rankingHasMore },
    });
    bindLoadMoreButton("rankings", loadMoreRankingResults);
  };
  const refreshRankingResults = ({ showLoading = true, scroll = false } = {}) => (
    refreshListFromFilter(loadRankingResults({ showLoading }), "rankings", { scroll })
  );
  setSectionFilterRefresher("rankings", refreshRankingResults);
  bindFilterButtons(handleSectionFilterChange);
  bindRankingDisciplineControl(() => refreshSectionFilters("rankings", { scroll: false, showLoading: false }));
  bindRankingMetricControl(() => refreshSectionFilters("rankings", { scroll: false, showLoading: false }));
  bindRankingTimeFilters();
  bindRankingClearFilters();
  bindRankingSaveForm();
  await loadRankingResults();
}

function authRequiredPage() {
  setApp(`
    ${pageHeading("loginHeading", "loginIntro")}
    <section class="panel auth-panel">
      <p>${t("loginRequiredFavorites")}</p>
      <a class="primary-button auth-primary-link" href="#/login">${t("signIn")}</a>
    </section>
  `);
}

function renderLogin() {
  if (state.currentUser) {
    renderAccount();
    return;
  }
  setApp(`
    ${pageHeading("loginHeading", "loginIntro")}
    <section class="panel auth-panel">
      <form class="auth-form" id="loginForm">
        <p>${t("loginHelp")}</p>
        <label>
          <span>${t("email")}</span>
          <input id="loginEmail" type="email" autocomplete="email" required>
        </label>
        <label>
          <span>${t("password")}</span>
          <input id="loginPassword" type="password" autocomplete="current-password" required>
        </label>
        <label class="auth-mfa-field" id="mfaField" hidden>
          <span>${t("mfaCode")}</span>
          <input id="loginMfaCode" type="text" inputmode="numeric" autocomplete="one-time-code">
        </label>
        <button class="primary-button" type="submit">${t("loginAction")}</button>
        <div class="auth-message" id="loginMessage" role="status" aria-live="polite"></div>
      </form>
      <div class="auth-switch-row">
        <span>${t("registerPrompt")}</span>
        <a href="#/register">${t("registerLink")}</a>
      </div>
      <div class="demo-login-block">
        <p>${t("demoLoginNote")}</p>
        <div class="demo-login-actions">
          <button class="quiet-button demo-login-button" type="button" data-demo-role="user">${t("demoUser")}</button>
          <button class="quiet-button demo-login-button" type="button" data-demo-role="admin">${t("demoAdmin")}</button>
          <button class="quiet-button demo-login-button" type="button" data-demo-role="super_admin">${t("demoSuperAdmin")}</button>
        </div>
      </div>
    </section>
  `);

  $("#loginForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = $("#loginMessage");
    const submit = event.currentTarget.querySelector("button[type='submit']");
    message.textContent = "";
    submit.disabled = true;
    try {
      const payload = await sendJson("/auth/login", {
        auth: false,
        body: {
          email: $("#loginEmail").value.trim(),
          password: $("#loginPassword").value,
          mfa_code: $("#loginMfaCode")?.value.trim() || undefined,
        },
      });
      if (payload.mfa_required) {
        $("#mfaField").hidden = false;
        $("#loginMfaCode").required = true;
        $("#loginMfaCode").focus();
        message.textContent = t("mfaRequired");
        return;
      }
      if (payload.mfa_setup_required) {
        message.textContent = t("mfaSetupRequired");
        return;
      }
      if (!payload.access_token) {
        message.textContent = t("loginError");
        return;
      }
      await completeLoginWithToken(payload.access_token);
    } catch (_error) {
      message.textContent = t("loginError");
    } finally {
      submit.disabled = false;
    }
  });

  document.querySelectorAll("[data-demo-role]").forEach((button) => {
    button.addEventListener("click", async () => {
      const message = $("#loginMessage");
      message.textContent = "";
      button.disabled = true;
      try {
        const payload = await sendJson("/auth/demo-login", {
          auth: false,
          body: { role: button.dataset.demoRole },
        });
        if (!payload.access_token) {
          message.textContent = t("loginError");
          return;
        }
        await completeLoginWithToken(payload.access_token);
      } catch (_error) {
        message.textContent = t("loginError");
      } finally {
        button.disabled = false;
      }
    });
  });
}

function renderRegister() {
  if (state.currentUser) {
    renderAccount();
    return;
  }
  setApp(`
    ${pageHeading("registerHeading", "registerIntro")}
    <section class="panel auth-panel">
      <form class="auth-form" id="registerForm">
        <p>${t("registerHelp")}</p>
        <label>
          <span>${t("email")}</span>
          <input id="registerEmail" type="email" autocomplete="email" required>
        </label>
        <label>
          <span>${t("password")}</span>
          <input id="registerPassword" type="password" autocomplete="new-password" minlength="12" maxlength="128" required>
        </label>
        <label>
          <span>${t("confirmPassword")}</span>
          <input id="registerPasswordConfirm" type="password" autocomplete="new-password" minlength="12" maxlength="128" required>
        </label>
        <button class="primary-button" type="submit">${t("registerAction")}</button>
        <div class="auth-message" id="registerMessage" role="status" aria-live="polite"></div>
      </form>
      <div class="auth-switch-row">
        <span>${t("alreadyRegistered")}</span>
        <a href="#/login">${t("backToLogin")}</a>
      </div>
    </section>
  `);

  $("#registerForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const message = $("#registerMessage");
    const submit = form.querySelector("button[type='submit']");
    const password = $("#registerPassword").value;
    const passwordConfirm = $("#registerPasswordConfirm").value;
    message.classList.remove("is-success");
    message.textContent = "";
    if (password !== passwordConfirm) {
      message.textContent = t("passwordMismatch");
      $("#registerPasswordConfirm").focus();
      return;
    }
    submit.disabled = true;
    try {
      await sendJson("/auth/register", {
        auth: false,
        body: {
          email: $("#registerEmail").value.trim(),
          password,
          preferred_language: state.language,
        },
      });
      form.querySelectorAll("input, button").forEach((control) => {
        control.disabled = true;
      });
      message.classList.add("is-success");
      message.textContent = t("registrationSuccess");
    } catch (_error) {
      message.textContent = t("registrationError");
      submit.disabled = false;
    }
  });
}

async function renderVerifyEmail() {
  const token = currentParams().get("token") || "";
  const cachedStatus = state.emailVerification.token === token
    ? state.emailVerification.status
    : "idle";
  const initialMessageKey = cachedStatus === "success"
    ? "verificationSuccess"
    : (cachedStatus === "error" ? "verificationError" : "verificationChecking");
  setApp(`
    ${pageHeading("verifyEmailHeading", "verifyEmailIntro")}
    <section class="panel auth-panel auth-verification-panel">
      <div class="auth-message ${cachedStatus === "success" ? "is-success" : ""}" id="verificationMessage" role="status" aria-live="polite">${t(initialMessageKey)}</div>
      <a class="primary-button auth-primary-link" id="verificationLoginLink" href="#/login" ${["success", "error"].includes(cachedStatus) ? "" : "hidden"}>${t("backToLogin")}</a>
    </section>
  `);
  const message = $("#verificationMessage");
  const loginLink = $("#verificationLoginLink");
  if (["success", "error"].includes(cachedStatus)) return;
  if (!token) {
    state.emailVerification = { token: "", status: "error" };
    message.textContent = t("verificationError");
    loginLink.hidden = false;
    return;
  }
  state.emailVerification = { token, status: "checking" };
  try {
    await sendJson("/auth/verify-email", { auth: false, body: { token } });
    state.emailVerification = { token, status: "success" };
    message.classList.add("is-success");
    message.textContent = t("verificationSuccess");
  } catch (_error) {
    state.emailVerification = { token, status: "error" };
    message.textContent = t("verificationError");
  }
  loginLink.hidden = false;
}

function renderFavoriteAthletes(details) {
  if (!details.length) return emptyMessage(t("noFavoriteAthletes"));
  return `<div class="grid-3 athlete-results-list account-preference-card-list">${details.map((item) => {
    const athlete = item.athlete || {};
    const name = athleteCardDisplayName(athlete, `${t("athlete")} ${item.athlete_id}`);
    const meta = [
      athlete.world_gymnastics_status,
      `${Number(item.result_count || 0).toLocaleString()} ${t("results")}`,
      `${t("savedOn")} ${formatReadableDate(String(item.created_at || "").slice(0, 10))}`,
    ].filter(Boolean).join(" · ");
    const pills = [
      { label: athlete.discipline || t("discipline"), variant: "brand" },
      { label: athlete.country || t("country") },
      { label: compactIdLabel(item.athlete_id) },
    ];
    return entityCard(
      escapeHtml(name),
      escapeHtml(meta),
      pills.map((pill) => ({ ...pill, label: escapeHtml(pill.label) })),
      `#/athletes/${item.athlete_id}`,
      favoriteButton("athlete", item.athlete_id, true),
    );
  }).join("")}</div>`;
}

function renderFavoriteEvents(details) {
  if (!details.length) return emptyMessage(t("noFavoriteEvents"));
  const displayDetails = sortFavoriteEventDetails(details);
  const visibleDetails = splitEventListFullRows(displayDetails, false).visible;
  return `<div class="grid-3 event-results-list account-preference-card-list">${visibleDetails.map((item) => {
    const event = item.event || {};
    const period = formatReadableDateRange(event);
    const meta = [
      event.location,
      event.venue,
      `${Number(event.result_count || 0).toLocaleString()} ${t("results")}`,
      `${t("savedOn")} ${formatReadableDate(String(item.created_at || "").slice(0, 10))}`,
    ].filter(Boolean).join(" · ");
    const pills = [
      { label: event.discipline ? displayEnumValue(event.discipline) : t("discipline") },
      { label: event.category ? displayEnumValue(event.category) : t("category") },
      { label: event.level || t("event") },
    ];
    return entityCard(
      eventCardTitle({ ...event, id: item.event_id }, period),
      escapeHtml(meta),
      pills.filter((pill) => pill.label).map((pill) => ({ ...pill, label: escapeHtml(pill.label) })),
      item.event_id ? `#/events/${item.event_id}` : "",
      favoriteButton("event", item.event_id, true),
    );
  }).join("")}</div>`;
}

function renderAthleteProfileImage(athlete) {
  const image = mediaUrl(athlete.image_url);
  const name = athleteProfileDisplayName(athlete);
  if (image) {
    return `
      <div class="athlete-profile-image">
        <img src="${escapeHtml(image)}" alt="${escapeHtml(name)}">
      </div>
    `;
  }
  return `<div class="athlete-profile-image athlete-profile-initials" aria-hidden="true">${escapeHtml(athleteInitials(athlete))}</div>`;
}

function renderAthleteVerificationBadge(athlete) {
  if (!athlete?.is_profile_verified) return "";
  return `
    <span class="athlete-verification-badge" role="img" aria-label="${escapeHtml(t("verifiedAthleteBadge"))}">
      <span aria-hidden="true"></span>
    </span>
  `;
}

function renderCountryHistory(athlete) {
  const changes = athlete.country_changes || [];
  if (!changes.length) return emptyMessage(t("noCountryHistory"));
  return `
    <div class="timeline-list">
      ${changes.map((change) => `
        <div class="timeline-item">
          <span>${escapeHtml(String(change.change_year))}</span>
          <strong>${escapeHtml(displayValue(change.from_country))} -> ${escapeHtml(displayValue(change.to_country))}</strong>
        </div>
      `).join("")}
    </div>
  `;
}

function renderAthleteIdentityPanel(athlete, options = {}) {
  const embedded = Boolean(options.embedded);
  const showHeader = options.showHeader !== false;
  const profileLink = athlete.world_gymnastics_profile_url
    ? `<a class="feature-link identity-profile-link" href="${escapeHtml(athlete.world_gymnastics_profile_url)}" target="_blank" rel="noreferrer">${escapeHtml(t("openWorldGymnastics"))}</a>`
    : "";
  const verifiedAt = formatDateTime(athlete.world_gymnastics_verified_at);
  const fields = [
    renderDetailFieldIfPresent(t("leverageId"), athlete.id),
    renderDetailFieldIfPresent(t("country"), athlete.country),
    renderDetailFieldIfPresent(t("discipline"), athlete.discipline),
    renderDetailFieldIfPresent(t("birthYear"), athlete.birth_year),
  ].filter(Boolean).join("");
  const worldGymnasticsItems = [
    [t("worldGymnasticsStatus"), athlete.world_gymnastics_status],
    [t("worldGymnasticsId"), athlete.world_gymnastics_athlete_id],
    [t("worldGymnasticsProfile"), athlete.world_gymnastics_profile_url, profileLink],
    [t("worldGymnasticsVerified"), verifiedAt],
    isAdminUser()
      ? [t("verifiedByAdminId"), athlete.world_gymnastics_verified_by_admin_id]
      : null,
  ].filter((item) => item && hasDisplayValue(item[1]));
  const worldGymnasticsData = worldGymnasticsItems.length
    ? `
      <div class="athlete-identity-history athlete-identity-world-gymnastics">
        <span>${escapeHtml(t("worldGymnasticsData"))}</span>
        <div class="timeline-list">
          ${worldGymnasticsItems.map(([label, value, html]) => `
            <div class="timeline-item">
              <span>${escapeHtml(label)}</span>
              <strong>${html || escapeHtml(displayValue(value))}</strong>
            </div>
          `).join("")}
        </div>
      </div>
    `
    : "";
  const countryChanges = athlete.country_changes || [];
  const countryHistory = countryChanges.length
    ? `
      <div class="athlete-identity-history">
        <span>${escapeHtml(t("countryHistory"))}</span>
        ${renderCountryHistory(athlete)}
      </div>
    `
    : "";
  const tag = embedded ? "div" : "section";
  const classes = [
    embedded ? "" : "panel athlete-detail-section",
    "athlete-identity-panel",
    embedded ? "athlete-identity-panel-embedded" : "",
  ].filter(Boolean).join(" ");
  return `
    <${tag} class="${classes}">
      ${showHeader ? `<div class="section-header compact-section-header">
        <div>
          <h2>${t("athleteIdentity")}</h2>
        </div>
      </div>` : ""}
      <div class="detail-grid athlete-identity-grid">
        ${fields}
      </div>
      ${worldGymnasticsData}
      ${countryHistory}
    </${tag}>
  `;
}

function athleteAnalyticsMetricLabel(metric) {
  return ATHLETE_ANALYTICS_METRICS.find((item) => item.value === metric)?.label || "Final Score";
}

function athleteAnalyticsOrder(discipline) {
  return ATHLETE_ANALYTICS_APPARATUS_ORDER[discipline] || ATHLETE_ANALYTICS_APPARATUS_ORDER.MAG;
}

function athleteAnalyticsApparatusOptions(discipline) {
  return RANKING_APPARATUS_BY_DISCIPLINE[discipline] || RANKING_APPARATUS_BY_DISCIPLINE.MAG;
}

function athleteAnalyticsSelectedApparatuses(discipline) {
  const options = athleteAnalyticsApparatusOptions(discipline);
  const rawSelection = Array.isArray(state.athleteAnalytics.apparatuses)
    ? state.athleteAnalytics.apparatuses
    : Array.isArray(state.athleteAnalytics.apparatus)
      ? state.athleteAnalytics.apparatus
      : state.athleteAnalytics.apparatus && state.athleteAnalytics.apparatus !== "all"
        ? [state.athleteAnalytics.apparatus]
        : [];
  const uniqueSelection = normalizeExclusiveApparatusSelection([...new Set(rawSelection)].filter((apparatus) => options.includes(apparatus)));
  return options.filter((apparatus) => uniqueSelection.includes(apparatus));
}

function athleteAnalyticsApparatusLabel(apparatus) {
  return apparatus === "all" ? t("all") : apparatus;
}

function athleteAnalyticsApparatusSelectionLabel(selectedApparatuses) {
  if (!selectedApparatuses.length) return t("all");
  return selectedApparatuses.map(athleteAnalyticsApparatusLabel).join(" + ");
}

function athleteAnalyticsPrimaryVertexApparatus(apparatus) {
  return apparatus === "VT AVG" ? "VT" : apparatus;
}

function athleteAnalyticsApparatusMatches(point, selectedApparatuses) {
  if (!selectedApparatuses.length) return point.apparatus !== "AA";
  return selectedApparatuses.includes(point.apparatus);
}

function athleteAnalyticsPointsForSelection(points, selectedApparatuses) {
  return points.filter((point) => athleteAnalyticsApparatusMatches(point, selectedApparatuses));
}

function athleteAnalyticsVertexIsActive(vertexApparatus, selectedApparatuses, discipline) {
  if (!selectedApparatuses.length || selectedApparatuses.includes("AA")) return true;
  const apparatusOrder = athleteAnalyticsOrder(discipline);
  return selectedApparatuses.some((apparatus) => {
    const selectedVertex = athleteAnalyticsPrimaryVertexApparatus(apparatus);
    return apparatusOrder.includes(selectedVertex) && vertexApparatus === selectedVertex;
  });
}

function athleteAnalyticsNumber(value) {
  if (value === null || value === undefined || value === "") return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function athleteAnalyticsPointMetricValue(point, metric) {
  if (metric === "score") return athleteAnalyticsNumber(point.score ?? point.value);
  if (metric === "D_score") return athleteAnalyticsNumber(point.D_score);
  if (metric === "E_score" || metric === "execution_estimate") {
    return athleteAnalyticsNumber(point.E_score) ?? athleteAnalyticsNumber(point.execution_estimate);
  }
  if (metric === "Penalty") return athleteAnalyticsNumber(point.Penalty);
  if (metric === "Bonus") return athleteAnalyticsNumber(point.Bonus);
  return athleteAnalyticsNumber(point.value);
}

function athleteAnalyticsAaContextComponents(points, sourcePoint, discipline) {
  const apparatusOrder = athleteAnalyticsOrder(discipline || sourcePoint.discipline);
  const contextKey = athleteAnalyticsPointContextKey(sourcePoint);
  const byApparatus = new Map();
  points
    .filter((point) => athleteAnalyticsPointContextKey(point) === contextKey)
    .filter((point) => apparatusOrder.includes(point.apparatus))
    .sort((a, b) => athleteAnalyticsSortKey(a).localeCompare(athleteAnalyticsSortKey(b)))
    .forEach((point) => {
      if (point.apparatus === "VT" && Number(point.vt_attempt) === 2) return;
      const current = byApparatus.get(point.apparatus);
      if (!current || athleteAnalyticsPointMetricValue(current, "score") === null) {
        byApparatus.set(point.apparatus, point);
      }
    });
  return apparatusOrder.map((apparatus) => byApparatus.get(apparatus)).filter(Boolean);
}

function athleteAnalyticsSumComponentMetric(points, metric, expectedCount = null) {
  const values = points
    .map((point) => athleteAnalyticsPointMetricValue(point, metric))
    .filter((value) => value !== null);
  if (expectedCount !== null && values.length < expectedCount) return null;
  if (!values.length) return null;
  return values.reduce((sum, value) => sum + value, 0);
}

function athleteAnalyticsAaDScoreTotal(point, allPoints, discipline) {
  const directValue = athleteAnalyticsPointMetricValue(point, "D_score");
  if (directValue !== null) return directValue;
  const apparatusOrder = athleteAnalyticsOrder(discipline || point.discipline);
  const components = athleteAnalyticsAaContextComponents(allPoints, point, discipline);
  return athleteAnalyticsSumComponentMetric(components, "D_score", apparatusOrder.length);
}

function athleteAnalyticsAaComponentValue(point, metric, allPoints, discipline) {
  if (metric === "D_score") return athleteAnalyticsAaDScoreTotal(point, allPoints, discipline);
  if (metric === "execution_estimate" || metric === "E_score") {
    const directValue = athleteAnalyticsPointMetricValue(point, "E_score");
    if (directValue !== null) return directValue;
    const score = athleteAnalyticsPointMetricValue(point, "score");
    const dScore = athleteAnalyticsAaDScoreTotal(point, allPoints, discipline);
    if (score === null || dScore === null) return null;
    const estimate = score - dScore;
    return Number.isFinite(estimate) && estimate >= 0 ? estimate : null;
  }
  if (metric === "Penalty" || metric === "Bonus") {
    const directValue = athleteAnalyticsPointMetricValue(point, metric);
    if (directValue !== null) return directValue;
    return athleteAnalyticsSumComponentMetric(
      athleteAnalyticsAaContextComponents(allPoints, point, discipline),
      metric,
    );
  }
  return athleteAnalyticsPointMetricValue(point, metric);
}

function athleteAnalyticsPointValueForMetric(point, metric, allPoints, discipline) {
  if (point.apparatus === "AA") {
    return athleteAnalyticsAaComponentValue(point, metric, allPoints, discipline);
  }
  return athleteAnalyticsPointMetricValue(point, metric);
}

function athleteAnalyticsPointsForMetric(points, metric, discipline) {
  return points.map((point) => ({
    ...point,
    value: athleteAnalyticsPointValueForMetric(point, metric, points, discipline),
  }));
}

function athleteAnalyticsComponentMetricKey(metric) {
  return metric === "E_score" ? "execution_estimate" : metric;
}

function athleteAnalyticsScoreComponentDefinitions(selectedApparatuses, discipline, primaryMetric = "score") {
  if (selectedApparatuses.length !== 1) return [];
  const selectedApparatus = selectedApparatuses[0];
  const sourceFilter = (point) => point.apparatus === selectedApparatus;
  const componentValueForMetric = (metric) => (
    selectedApparatus === "AA"
      ? (point, allPoints) => athleteAnalyticsAaComponentValue(point, metric, allPoints, discipline)
      : (point) => athleteAnalyticsPointMetricValue(point, metric)
  );
  const primaryMetricKey = athleteAnalyticsComponentMetricKey(primaryMetric);
  return [
    {
      key: "score",
      label: "Final Score",
      metric: "score",
      filter: sourceFilter,
      valueForPoint: componentValueForMetric("score"),
    },
    {
      key: "D_score",
      label: "D Score",
      metric: "D_score",
      filter: sourceFilter,
      valueForPoint: componentValueForMetric("D_score"),
    },
    {
      key: "execution_estimate",
      label: "E Score / E est.",
      metric: "execution_estimate",
      filter: sourceFilter,
      valueForPoint: componentValueForMetric("execution_estimate"),
    },
    {
      key: "Penalty",
      label: "Penalty",
      metric: "Penalty",
      hideWhenAllZero: true,
      filter: sourceFilter,
      valueForPoint: componentValueForMetric("Penalty"),
    },
    {
      key: "Bonus",
      label: "Bonus",
      metric: "Bonus",
      hideWhenAllZero: true,
      filter: sourceFilter,
      valueForPoint: componentValueForMetric("Bonus"),
    },
  ].filter((definition) => athleteAnalyticsComponentMetricKey(definition.metric) !== primaryMetricKey);
}

function athleteAnalyticsComponentDefinitions(selectedApparatuses, discipline, metric) {
  if (["score", "D_score", "execution_estimate", "E_score"].includes(metric)) {
    const scoreComponentDefinitions = athleteAnalyticsScoreComponentDefinitions(selectedApparatuses, discipline, metric);
    if (scoreComponentDefinitions.length) return scoreComponentDefinitions;
  }
  if (selectedApparatuses.length > 1 && !selectedApparatuses.includes("AA") && !selectedApparatuses.includes("VT AVG")) {
    const apparatusOrder = athleteAnalyticsOrder(discipline);
    return selectedApparatuses
      .filter((apparatus) => apparatusOrder.includes(apparatus))
      .map((apparatus) => ({
        key: `selected-${apparatus}`,
        label: apparatus,
        metric,
        filter: (point) => point.apparatus === apparatus,
      }));
  }
  return [];
}

function athleteAnalyticsComponentColor(series) {
  const key = String(series?.key || "").replace(/^selected-/, "");
  const label = String(series?.label || "").replace(/\s+/g, "");
  return ATHLETE_TREND_COMPONENT_COLORS[key]
    || ATHLETE_TREND_COMPONENT_COLORS[label]
    || "rgba(25, 23, 71, 0.42)";
}

function athleteAnalyticsPointContextKey(point) {
  return [
    point.event_id || "",
    point.format || "",
    point.round || "",
    point.discipline || "",
    point.category || "",
    point.day || "",
  ].join("|");
}

function athleteAnalyticsPointDate(point) {
  return point.date || (point.year ? `${point.year}-01-01` : "");
}

function athleteAnalyticsPointEventPeriodLabel(point) {
  return formatReadableDateRange({
    start_date: point.event_start_date || point.date,
    end_date: point.event_end_date || point.event_start_date || point.date,
    year: point.year,
  });
}

function athleteAnalyticsPointIsMultiDayEvent(point) {
  const start = point.event_start_date || point.date;
  const end = point.event_end_date || start;
  return Boolean(start && end && start !== end);
}

function athleteAnalyticsPointUsesEventPeriod(point) {
  if (point.date_precision === "event_period") return true;
  const start = point.event_start_date || point.date;
  const end = point.event_end_date || start;
  return Boolean(start && end && start !== end && !point.day);
}

function athleteAnalyticsPointDisplayDateLabel(point) {
  return athleteAnalyticsPointUsesEventPeriod(point)
    ? athleteAnalyticsPointEventPeriodLabel(point)
    : formatReadableDate(athleteAnalyticsPointDate(point));
}

function athleteAnalyticsContextLabel(point) {
  const eventName = point.event_name || "";
  const roundFormat = [point.round, point.format].filter(Boolean).join(" · ");
  const apparatus = point.apparatus ? athleteAnalyticsApparatusLabel(point.apparatus) : "";
  const parts = [
    eventName,
    roundFormat,
    point.discipline,
    apparatus,
    point.day ? `day ${point.day}` : "",
  ].filter(Boolean);
  return parts.join(" · ");
}

function athleteAnalyticsRoundFormatLabel(point) {
  const parts = [point.round, point.format].filter(Boolean);
  return parts.join(" / ");
}

function athleteAnalyticsEventSummaryKey(point) {
  return [
    point.event_id || point.event_name || "",
    point.event_start_date || point.date || "",
    point.event_end_date || "",
  ].join("|");
}

function athleteAnalyticsEventSummaries(points) {
  const summaries = new Map();
  points.forEach((point) => {
    const key = athleteAnalyticsEventSummaryKey(point);
    if (!key.trim()) return;
    if (!summaries.has(key)) {
      summaries.set(key, {
        eventName: point.event_name || t("event"),
        period: athleteAnalyticsPointEventPeriodLabel(point),
        isMultiDay: athleteAnalyticsPointIsMultiDayEvent(point),
        roundFormats: new Set(),
        apparatuses: new Set(),
      });
    }
    const summary = summaries.get(key);
    const roundFormat = athleteAnalyticsRoundFormatLabel(point);
    if (roundFormat) summary.roundFormats.add(roundFormat);
    if (point.apparatus) summary.apparatuses.add(athleteAnalyticsApparatusLabel(point.apparatus));
  });
  return [...summaries.values()]
    .map((summary) => ({
      ...summary,
      roundFormats: [...summary.roundFormats].sort(),
      apparatuses: [...summary.apparatuses].sort(),
    }))
    .sort((left, right) => `${left.period} ${left.eventName}`.localeCompare(`${right.period} ${right.eventName}`));
}

function athleteAnalyticsEventSummaryInline(summaries, limit = 2) {
  if (!summaries.length) return "";
  const visible = summaries.slice(0, limit).map((summary) => {
    const roundFormats = summary.roundFormats.length ? ` (${summary.roundFormats.join(", ")})` : "";
    return `${summary.eventName}: ${summary.period}${roundFormats}`;
  });
  const remaining = summaries.length - visible.length;
  return `${visible.join(" | ")}${remaining > 0 ? ` +${localizedCount(remaining, "analyticsMoreEventSingular", "analyticsMoreEvents")}` : ""}`;
}

function athleteAnalyticsUniqueLimitedLabels(labels, limit = 3) {
  const uniqueLabels = [...new Set(labels.filter(Boolean))];
  if (uniqueLabels.length <= limit) return uniqueLabels.join(" | ");
  return `${uniqueLabels.slice(0, limit).join(" | ")} +${uniqueLabels.length - limit}`;
}

function athleteAnalyticsTrendPointTooltipAttrs(point, metric) {
  const periodLabel = athleteAnalyticsUniqueLimitedLabels(point.periods || []);
  const eventLabel = athleteAnalyticsUniqueLimitedLabels(point.event_names || []);
  return [
    `data-athlete-trend-point="true"`,
    `data-trend-value="${escapeHtml(athleteAnalyticsFormatValue(point.value, metric))}"`,
    `data-trend-date="${escapeHtml(periodLabel || formatReadableDate(point.date))}"`,
    `data-trend-event="${escapeHtml(eventLabel)}"`,
    `tabindex="0"`,
  ].join(" ");
}

function renderAthleteTrendDot(point, metric, className, radius, extraAttrs = "") {
  return `
    <circle
      class="${className}"
      cx="${point.x.toFixed(1)}"
      cy="${point.y.toFixed(1)}"
      r="${radius}"
      ${extraAttrs}
      ${athleteAnalyticsTrendPointTooltipAttrs(point, metric)}
    ></circle>
  `;
}

function athleteAnalyticsSnapshotDateLabel(points, fallbackDate) {
  const labels = [...new Set(points.map(athleteAnalyticsPointDisplayDateLabel).filter(Boolean))];
  if (labels.length === 1) return labels[0];
  if (labels.length > 1) {
    return athleteAnalyticsUniqueLimitedLabels(labels, 3);
  }
  return fallbackDate ? formatReadableDate(fallbackDate) : t("notAvailable");
}

function athleteAnalyticsTimelineDateLabel(points, dateKey) {
  if (!dateKey) return t("notAvailable");
  const datePoints = points.filter((point) => athleteAnalyticsPointDate(point) === dateKey);
  if (!datePoints.length) return formatReadableDate(dateKey);
  const labels = datePoints.map(athleteAnalyticsPointDisplayDateLabel);
  return athleteAnalyticsUniqueLimitedLabels(labels, 3) || formatReadableDate(dateKey);
}

function athleteAnalyticsSnapshotContextPoints(points, selectedPoints, snapshotDate) {
  if (!snapshotDate) return [];
  const sameDateSelectedPoints = selectedPoints.filter((point) => athleteAnalyticsPointDate(point) === snapshotDate);
  if (sameDateSelectedPoints.length) return sameDateSelectedPoints;
  return points.filter((point) => athleteAnalyticsPointDate(point) === snapshotDate);
}

function athleteAnalyticsSortKey(point) {
  return `${athleteAnalyticsPointDate(point)}-${String(point.result_id || 0).padStart(12, "0")}`;
}

function athleteAnalyticsTimeline(points) {
  return [...new Set(points.map(athleteAnalyticsPointDate).filter(Boolean))].sort();
}

function athleteAnalyticsDefaultCycleRange(timeline) {
  const maxIndex = timeline.length - 1;
  const latestYear = Math.max(...timeline.map((dateKey) => Number(dateKey.slice(0, 4))).filter(Number.isFinite));
  const cycle = scoringCycleForYear(latestYear);
  if (!cycle) return { startIndex: 0, endIndex: maxIndex };
  const cycleStart = `${cycle.startYear}-01-01`;
  const cycleEnd = `${cycle.endYear}-12-31`;
  const cycleIndexes = timeline
    .map((dateKey, index) => ({ dateKey, index }))
    .filter(({ dateKey }) => dateKey >= cycleStart && dateKey <= cycleEnd)
    .map(({ index }) => index);
  if (!cycleIndexes.length) return { startIndex: 0, endIndex: maxIndex };
  return {
    startIndex: cycleIndexes[0],
    endIndex: cycleIndexes[cycleIndexes.length - 1],
  };
}

function athleteAnalyticsCurrentRange(timeline, mode = state.athleteAnalytics.mode) {
  if (!timeline.length) {
    state.athleteAnalytics.startIndex = -1;
    state.athleteAnalytics.endIndex = -1;
    state.athleteAnalytics.snapshotIndex = -1;
    return { startIndex: -1, endIndex: -1, startDate: "", endDate: "" };
  }
  const maxIndex = timeline.length - 1;
  if (mode === "snapshot") {
    let snapshotIndex = Number(state.athleteAnalytics.snapshotIndex);
    if (!Number.isInteger(snapshotIndex) || snapshotIndex < 0 || snapshotIndex > maxIndex) snapshotIndex = maxIndex;
    state.athleteAnalytics.snapshotIndex = snapshotIndex;
    return {
      startIndex: snapshotIndex,
      endIndex: snapshotIndex,
      startDate: timeline[snapshotIndex] || "",
      endDate: timeline[snapshotIndex] || "",
    };
  }
  let startIndex = Number(state.athleteAnalytics.startIndex);
  let endIndex = Number(state.athleteAnalytics.endIndex);
  if (
    !Number.isInteger(startIndex) ||
    startIndex < 0 ||
    startIndex > maxIndex ||
    !Number.isInteger(endIndex) ||
    endIndex < 0 ||
    endIndex > maxIndex
  ) {
    ({ startIndex, endIndex } = athleteAnalyticsDefaultCycleRange(timeline));
  }
  if (startIndex > endIndex) startIndex = endIndex;
  state.athleteAnalytics.startIndex = startIndex;
  state.athleteAnalytics.endIndex = endIndex;
  return {
    startIndex,
    endIndex,
    startDate: timeline[startIndex] || "",
    endDate: timeline[endIndex] || "",
  };
}

function athleteAnalyticsValue(point) {
  const value = Number(point.value);
  return Number.isFinite(value) ? value : null;
}

function athleteAnalyticsScaleMax(metric, values) {
  const maxObserved = Math.max(0, ...values.filter((value) => value !== null && value !== undefined));
  if (metric === "execution_estimate" || metric === "E_score") return Math.max(10, maxObserved);
  if (metric === "D_score") return Math.max(10, maxObserved);
  if (metric === "Penalty" || metric === "Bonus") return Math.max(1, maxObserved);
  return Math.max(20, maxObserved);
}

function athleteAnalyticsPointYear(point) {
  const pointDate = athleteAnalyticsPointDate(point);
  if (pointDate) return Number(pointDate.slice(0, 4));
  return Number(point.year);
}

function scoringCycleForYear(year) {
  if (!Number.isFinite(year)) return null;
  if (year <= 2021) return { label: "2017-2021", startYear: 2017, endYear: 2021 };
  if (year <= 2024) return { label: "2022-2024", startYear: 2022, endYear: 2024 };
  const startYear = 2025 + (Math.floor((year - 2025) / 4) * 4);
  return { label: `${startYear}-${startYear + 3}`, startYear, endYear: startYear + 3 };
}

function athleteAnalyticsScoringCycles(points) {
  const cyclesByLabel = new Map();
  points.forEach((point) => {
    const cycle = scoringCycleForYear(athleteAnalyticsPointYear(point));
    if (cycle) cyclesByLabel.set(cycle.label, cycle);
  });
  return [...cyclesByLabel.values()].sort((left, right) => left.startYear - right.startYear);
}

function athleteAnalyticsLowerIsBetter(metric) {
  return metric === "Penalty";
}

function athleteAnalyticsFormatValue(value, metric = state.athleteAnalytics.metric) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return t("notAvailable");
  if (metric === "D_score") return dScoreLabel(value);
  if (metric === "Penalty" || metric === "Bonus") return componentValueLabel(value);
  return scoreLabel(value);
}

function athleteAnalyticsIncludedPoints(points, startDate, endDate, mode = state.athleteAnalytics.mode) {
  if (!endDate) return [];
  const isSnapshot = mode === "snapshot";
  return points
    .filter((point) => athleteAnalyticsValue(point) !== null)
    .filter((point) => {
      const pointDate = athleteAnalyticsPointDate(point);
      if (!pointDate) return false;
      if (isSnapshot) return pointDate === endDate;
      return (!startDate || pointDate >= startDate) && pointDate <= endDate;
    })
    .sort((a, b) => athleteAnalyticsSortKey(a).localeCompare(athleteAnalyticsSortKey(b)));
}

function athleteAnalyticsSummary(points, metric) {
  const values = points.map(athleteAnalyticsValue).filter((value) => value !== null);
  if (!values.length) {
    return { average: null, best: null, latest: null, eventCount: 0, resultCount: 0 };
  }
  const latestPoint = [...points].sort((a, b) => athleteAnalyticsSortKey(a).localeCompare(athleteAnalyticsSortKey(b))).at(-1);
  return {
    average: values.reduce((sum, value) => sum + value, 0) / values.length,
    best: athleteAnalyticsLowerIsBetter(metric) ? Math.min(...values) : Math.max(...values),
    latest: athleteAnalyticsValue(latestPoint),
    eventCount: new Set(points.map((point) => point.event_id).filter(Boolean)).size,
    resultCount: points.length,
  };
}

function athleteAnalyticsBuildVertices(points, discipline, metric, mode, startDate, endDate) {
  const order = athleteAnalyticsOrder(discipline);
  return order.map((apparatus) => {
    const apparatusPoints = athleteAnalyticsIncludedPoints(
      points.filter((point) => point.apparatus === apparatus),
      startDate,
      endDate,
      mode,
    );
    if (!apparatusPoints.length) {
      return { apparatus, value: null, resultCount: 0, sourcePoint: null };
    }
    if (mode === "snapshot") {
      const sourcePoint = apparatusPoints.at(-1);
      return {
        apparatus,
        value: athleteAnalyticsValue(sourcePoint),
        resultCount: 1,
        sourcePoint,
      };
    }
    const values = apparatusPoints.map(athleteAnalyticsValue).filter((value) => value !== null);
    return {
      apparatus,
      value: values.reduce((sum, value) => sum + value, 0) / values.length,
      resultCount: apparatusPoints.length,
      sourcePoint: apparatusPoints.at(-1),
    };
  });
}

function athleteAnalyticsPolarPoint(index, total, radius, center = 150) {
  const angle = -Math.PI / 2 + ((Math.PI * 2) / total) * index;
  return {
    x: center + Math.cos(angle) * radius,
    y: center + Math.sin(angle) * radius,
  };
}

function athleteAnalyticsSvgPolygon(points) {
  return points.map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(" ");
}

function athleteAnalyticsRadarScaleLabel(value) {
  if (!Number.isFinite(value)) return "";
  const rounded = Math.round(value * 10) / 10;
  return Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(1);
}

function renderAthleteAnalyticsShape(vertices, metric, selectedApparatuses, discipline, options = {}) {
  const values = vertices.map((vertex) => vertex.value).filter((value) => value !== null && value !== undefined);
  const maxValue = options.maxValue || athleteAnalyticsScaleMax(metric, values);
  const radius = 106;
  const center = 150;
  const total = vertices.length;
  const hasApparatusFocus = selectedApparatuses.length > 0 && !selectedApparatuses.includes("AA");
  const scaleRatios = [0.25, 0.5, 0.75, 1];
  const rings = scaleRatios.map((ratio) => {
    const ringPoints = vertices.map((_, index) => athleteAnalyticsPolarPoint(index, total, radius * ratio, center));
    return `<polygon class="athlete-radar-ring" points="${athleteAnalyticsSvgPolygon(ringPoints)}"></polygon>`;
  }).join("");
  const scale = scaleRatios.map((ratio) => {
    const y = center - (radius * ratio);
    const rawValue = athleteAnalyticsLowerIsBetter(metric)
      ? maxValue * (1 - ratio)
      : maxValue * ratio;
    return `
      <line class="athlete-radar-scale-tick" x1="${center - 4}" y1="${y.toFixed(1)}" x2="${center + 4}" y2="${y.toFixed(1)}"></line>
      <text class="athlete-radar-scale-label" x="${center + 10}" y="${(y + 3).toFixed(1)}">${escapeHtml(athleteAnalyticsRadarScaleLabel(rawValue))}</text>
    `;
  }).join("");
  const centerScaleValue = athleteAnalyticsLowerIsBetter(metric) ? maxValue : 0;
  const centerScaleLabel = `
    <text class="athlete-radar-scale-label is-center" x="${center + 9}" y="${center + 3}">${escapeHtml(athleteAnalyticsRadarScaleLabel(centerScaleValue))}</text>
  `;
  const axes = vertices.map((vertex, index) => {
    const end = athleteAnalyticsPolarPoint(index, total, radius, center);
    const label = athleteAnalyticsPolarPoint(index, total, radius + 24, center);
    const active = athleteAnalyticsVertexIsActive(vertex.apparatus, selectedApparatuses, discipline);
    return `
      <line class="athlete-radar-axis ${active ? "is-active" : "is-muted"}" x1="${center}" y1="${center}" x2="${end.x.toFixed(1)}" y2="${end.y.toFixed(1)}"></line>
      <text class="athlete-radar-label ${active ? "is-active" : "is-muted"}" x="${label.x.toFixed(1)}" y="${label.y.toFixed(1)}">${escapeHtml(vertex.apparatus)}</text>
    `;
  }).join("");
  const valuePoints = vertices.map((vertex, index) => {
    const rawValue = vertex.value === null || vertex.value === undefined ? null : Number(vertex.value);
    const normalized = rawValue === null || Number.isNaN(rawValue)
      ? 0
      : athleteAnalyticsLowerIsBetter(metric)
        ? Math.max(0, Math.min(1, maxValue === 0 ? 1 : 1 - (rawValue / maxValue)))
        : Math.max(0, Math.min(1, rawValue / maxValue));
    return athleteAnalyticsPolarPoint(index, total, radius * normalized, center);
  });
  const dots = valuePoints.map((point, index) => {
    const vertex = vertices[index];
    const active = athleteAnalyticsVertexIsActive(vertex.apparatus, selectedApparatuses, discipline);
    const valueLabel = athleteAnalyticsFormatValue(vertex.value, metric);
    const apparatusLabel = athleteAnalyticsApparatusLabel(vertex.apparatus);
    return `
      <circle
        class="athlete-radar-dot ${active ? "is-active" : "is-muted"}"
        cx="${point.x.toFixed(1)}"
        cy="${point.y.toFixed(1)}"
        r="${active ? 4.6 : 3.5}"
        data-athlete-radar-point="true"
        data-radar-apparatus="${escapeHtml([options.labelPrefix, apparatusLabel].filter(Boolean).join(" · "))}"
        data-radar-value="${escapeHtml(valueLabel)}"
        tabindex="0"
        aria-label="${escapeHtml(`${apparatusLabel}: ${valueLabel}`)}"
      ></circle>
    `;
  }).join("");
  const activeLines = hasApparatusFocus ? valuePoints.map((point, index) => {
    const vertex = vertices[index];
    if (!athleteAnalyticsVertexIsActive(vertex.apparatus, selectedApparatuses, discipline)) return "";
    return `<line class="athlete-radar-focus-line" x1="${center}" y1="${center}" x2="${point.x.toFixed(1)}" y2="${point.y.toFixed(1)}"></line>`;
  }).join("") : "";
  return `
    <div class="athlete-radar-figure">
      <svg class="athlete-radar-svg" viewBox="0 0 300 300" role="img" aria-label="${escapeHtml(t("analyticsShapeTitle"))}">
        ${rings}
        ${axes}
        <polygon class="athlete-radar-area ${options.seriesColor ? "is-comparison" : ""} ${hasApparatusFocus ? "is-muted" : ""}" ${options.seriesColor ? `style="--comparison-color: ${options.seriesColor};"` : ""} points="${athleteAnalyticsSvgPolygon(valuePoints)}"></polygon>
        ${activeLines}
        <g class="athlete-radar-scale" aria-hidden="true">
          ${centerScaleLabel}
          ${scale}
        </g>
        ${dots}
      </svg>
      <div class="athlete-radar-tooltip" role="status" hidden></div>
    </div>
  `;
}

function athleteAnalyticsShapeLegendItems(data) {
  const selectedApparatuses = data.selectedApparatuses || [];
  if (!selectedApparatuses.length) return [];
  if (selectedApparatuses.length === 1 && EXCLUSIVE_APPARATUS_FILTERS.has(selectedApparatuses[0])) {
    const apparatus = selectedApparatuses[0];
    return [{
      label: athleteAnalyticsApparatusLabel(apparatus),
      value: athleteAnalyticsFormatValue(data.summary.average, data.metric),
      color: ATHLETE_TREND_COMPONENT_COLORS[apparatus] || ATHLETE_TREND_COMPONENT_COLORS.score,
      primary: true,
    }];
  }
  const verticesByApparatus = new Map((data.vertices || []).map((vertex) => [vertex.apparatus, vertex]));
  const seen = new Set();
  return selectedApparatuses
    .map((apparatus) => {
      const vertexApparatus = athleteAnalyticsPrimaryVertexApparatus(apparatus);
      if (seen.has(vertexApparatus)) return null;
      seen.add(vertexApparatus);
      const vertex = verticesByApparatus.get(vertexApparatus);
      return {
        label: athleteAnalyticsApparatusLabel(apparatus),
        value: athleteAnalyticsFormatValue(vertex?.value, data.metric),
        color: ATHLETE_TREND_COMPONENT_COLORS[vertexApparatus] || ATHLETE_TREND_COMPONENT_COLORS.score,
        primary: selectedApparatuses.length === 1,
      };
    })
    .filter(Boolean);
}

function renderAthleteAnalyticsShapeLegend(data) {
  const items = athleteAnalyticsShapeLegendItems(data);
  if (!items.length) return "";
  return `
    <div class="athlete-trend-legend athlete-radar-legend" aria-label="${escapeHtml(t("analyticsShapeTitle"))}">
      ${items.map((item) => `
        <span
          class="${item.primary ? "is-primary" : ""}"
          style="--series-color: ${item.color};"
        >${escapeHtml(`${item.label} ${item.value}`)}</span>
      `).join("")}
    </div>
  `;
}

function athleteAnalyticsTrendPoints(points, startDate, endDate, mode) {
  const grouped = new Map();
  athleteAnalyticsIncludedPoints(points, startDate, endDate, mode).forEach((point) => {
    const key = athleteAnalyticsPointDate(point);
    if (!key) return;
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(point);
  });
  return [...grouped.entries()].map(([dateKey, group]) => {
    const values = group.map(athleteAnalyticsValue).filter((value) => value !== null);
    return {
      date: dateKey,
      value: values.reduce((sum, value) => sum + value, 0) / values.length,
      periods: group.map(athleteAnalyticsPointEventPeriodLabel),
      contexts: group.map(athleteAnalyticsContextLabel),
      event_names: group.map((point) => point.event_name).filter(Boolean),
      has_event_period: group.some(athleteAnalyticsPointUsesEventPeriod),
      result_count: group.length,
    };
  });
}

function athleteAnalyticsDateTime(dateKey) {
  const date = parseLocalDate(dateKey);
  return date ? date.getTime() : null;
}

function athleteAnalyticsTrendDateDomain(allDates) {
  const times = allDates.map(athleteAnalyticsDateTime).filter((time) => time !== null);
  if (!times.length) return { minTime: 0, maxTime: 0 };
  return { minTime: Math.min(...times), maxTime: Math.max(...times) };
}

function athleteAnalyticsTrendX(dateKey, domain, padding, width) {
  const time = athleteAnalyticsDateTime(dateKey);
  const left = padding.left;
  const right = width - padding.right;
  if (time === null || domain.maxTime <= domain.minTime) return (left + right) / 2;
  return left + ((right - left) * (time - domain.minTime)) / (domain.maxTime - domain.minTime);
}

function athleteAnalyticsTrendY(value, padding, height, minValue, valueRange) {
  const top = padding.top;
  const bottom = height - padding.bottom;
  return bottom - ((value - minValue) / valueRange) * (bottom - top);
}

function athleteAnalyticsSvgCoordinates(seriesPoints, allDates, padding, width, height, minValue, valueRange, dateDomain = athleteAnalyticsTrendDateDomain(allDates)) {
  return seriesPoints.map((point) => {
    const x = athleteAnalyticsTrendX(point.date, dateDomain, padding, width);
    const y = athleteAnalyticsTrendY(point.value, padding, height, minValue, valueRange);
    return { ...point, x, y };
  });
}

function athleteAnalyticsSvgPath(coordinates) {
  return coordinates.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
}

function athleteAnalyticsSvgPathSegments(coordinates, referenceDates = []) {
  if (!coordinates.length) return [];
  const referenceIndexes = new Map(referenceDates.map((date, index) => [date, index]));
  const segments = [];
  let currentSegment = [];
  let previousIndex = null;
  coordinates.forEach((point) => {
    const currentIndex = referenceIndexes.get(point.date);
    const continuesSeries = currentSegment.length > 0 && (
      previousIndex === null || currentIndex === undefined || currentIndex === previousIndex + 1
    );
    if (!continuesSeries && currentSegment.length) {
      segments.push(currentSegment);
      currentSegment = [];
    }
    currentSegment.push(point);
    previousIndex = currentIndex ?? null;
  });
  if (currentSegment.length) segments.push(currentSegment);
  return segments;
}

function renderAthleteTrendPaths(coordinates, referenceDates, className, extraAttrs = "") {
  return athleteAnalyticsSvgPathSegments(coordinates, referenceDates)
    .filter((segment) => segment.length >= 2)
    .map((segment) => `<path class="${className}" ${extraAttrs} d="${athleteAnalyticsSvgPath(segment)}"></path>`)
    .join("");
}

function athleteAnalyticsAxisValueLabel(value, metric) {
  if (metric === "Penalty" || metric === "Bonus") return Number(value).toFixed(1);
  return Number(value).toFixed(1);
}

function athleteAnalyticsYAxisTicks(metric, minValue, maxValue) {
  const tickCount = 5;
  const valueRange = Math.max(1, maxValue - minValue);
  return Array.from({ length: tickCount + 1 }, (_, index) => {
    const value = minValue + (valueRange * index) / tickCount;
    return {
      value,
      label: athleteAnalyticsAxisValueLabel(value, metric),
    };
  });
}

function athleteAnalyticsTrendValueDomain(metric, values) {
  const numericValues = values
    .map((value) => Number(value))
    .filter((value) => Number.isFinite(value));
  if (!numericValues.length) {
    return { minValue: 0, maxValue: 1, valueRange: 1 };
  }
  const observedMin = Math.min(...numericValues);
  const observedMax = Math.max(...numericValues);
  if (metric === "Penalty" || metric === "Bonus") {
    const upperPadding = Math.max(0.05, observedMax * 0.18);
    const maxValue = Math.max(0.25, observedMax + upperPadding);
    return { minValue: 0, maxValue, valueRange: Math.max(0.25, maxValue) };
  }
  const observedRange = observedMax - observedMin;
  const padding = observedRange > 0
    ? Math.max(observedRange * 0.16, observedMax * 0.012, 0.05)
    : Math.max(0.45, observedMax * 0.035);
  let minValue = Math.max(0, observedMin - padding);
  let maxValue = observedMax + padding;
  if (maxValue - minValue < 1) {
    const midpoint = (observedMin + observedMax) / 2;
    minValue = Math.max(0, midpoint - 0.5);
    maxValue = midpoint + 0.5;
  }
  return { minValue, maxValue, valueRange: Math.max(1, maxValue - minValue) };
}

function athleteAnalyticsMonthsBetween(startDate, endDate) {
  return ((endDate.getFullYear() - startDate.getFullYear()) * 12) + (endDate.getMonth() - startDate.getMonth());
}

function athleteAnalyticsTrendXTicks(dateDomain) {
  if (!dateDomain.maxTime || dateDomain.maxTime < dateDomain.minTime) return [];
  const startDate = new Date(dateDomain.minTime);
  const endDate = new Date(dateDomain.maxTime);
  const startKey = formatLocalIso(startDate);
  const endKey = formatLocalIso(endDate);
  const spanDays = Math.max(0, Math.round((dateDomain.maxTime - dateDomain.minTime) / 86400000));
  const ticks = [];
  const addTick = (date, label) => {
    if (!date || ticks.some((tick) => tick.date === date)) return;
    ticks.push({ date, label });
  };
  if (spanDays > 730) {
    const startYear = startDate.getFullYear();
    const endYear = endDate.getFullYear();
    addTick(startKey, String(startYear));
    for (let year = startYear + 1; year <= endYear; year += 1) {
      addTick(`${year}-01-01`, String(year));
    }
    if (endYear !== startYear) addTick(endKey, String(endYear));
    return ticks;
  }
  if (spanDays > 75) {
    const monthCount = Math.max(1, athleteAnalyticsMonthsBetween(startDate, endDate) + 1);
    const step = Math.max(1, Math.ceil(monthCount / 6));
    addTick(startKey, `${monthShortLabel(startDate.getMonth() + 1)} ${startDate.getFullYear()}`);
    for (let date = new Date(startDate.getFullYear(), startDate.getMonth() + step, 1); date <= endDate; date = new Date(date.getFullYear(), date.getMonth() + step, 1)) {
      addTick(formatLocalIso(date), `${monthShortLabel(date.getMonth() + 1)} ${date.getFullYear()}`);
    }
    addTick(endKey, `${monthShortLabel(endDate.getMonth() + 1)} ${endDate.getFullYear()}`);
    return ticks;
  }
  const step = Math.max(1, Math.ceil(Math.max(1, spanDays) / 5));
  for (let date = new Date(startDate); date <= endDate; date = addDays(date, step)) {
    const dateKey = formatLocalIso(date);
    addTick(dateKey, formatReadableDate(dateKey, spanDays > 31));
  }
  addTick(endKey, formatReadableDate(endKey, spanDays > 31));
  return ticks;
}

function athleteAnalyticsCycleBoundaries(dateDomain) {
  if (!dateDomain.maxTime || dateDomain.maxTime <= dateDomain.minTime) return [];
  const minYear = new Date(dateDomain.minTime).getFullYear();
  const maxYear = new Date(dateDomain.maxTime).getFullYear();
  const boundaries = [];
  let nextStartYear = (scoringCycleForYear(minYear)?.endYear || minYear) + 1;
  while (nextStartYear <= maxYear) {
    const dateKey = `${nextStartYear}-01-01`;
    const time = athleteAnalyticsDateTime(dateKey);
    if (time !== null && time > dateDomain.minTime && time < dateDomain.maxTime) {
      const cycle = scoringCycleForYear(nextStartYear);
      boundaries.push({ date: dateKey, label: cycle?.label || String(nextStartYear), year: nextStartYear });
    }
    nextStartYear = (scoringCycleForYear(nextStartYear)?.endYear || nextStartYear) + 1;
  }
  return boundaries;
}

function athleteAnalyticsTimelinePercentForDate(timeline, dateKey) {
  const maxIndex = timeline.length - 1;
  if (!dateKey || maxIndex <= 0) return null;
  const targetTime = athleteAnalyticsDateTime(dateKey);
  if (targetTime === null) return null;
  const entries = timeline
    .map((item, index) => ({ index, time: athleteAnalyticsDateTime(item) }))
    .filter((entry) => entry.time !== null);
  if (entries.length < 2) return null;
  const first = entries[0];
  const last = entries[entries.length - 1];
  if (targetTime < first.time || targetTime > last.time) return null;
  const exact = entries.find((entry) => entry.time === targetTime);
  if (exact) return (exact.index / maxIndex) * 100;
  for (let index = 1; index < entries.length; index += 1) {
    const previous = entries[index - 1];
    const next = entries[index];
    if (targetTime < next.time) {
      const timeSpan = Math.max(1, next.time - previous.time);
      const fraction = Math.max(0, Math.min(1, (targetTime - previous.time) / timeSpan));
      const indexPosition = previous.index + ((next.index - previous.index) * fraction);
      return (indexPosition / maxIndex) * 100;
    }
  }
  return null;
}

function renderAthleteAnalyticsTimelineCycleMarkers(timeline) {
  const dateDomain = athleteAnalyticsTrendDateDomain(timeline);
  if (!dateDomain.maxTime || dateDomain.maxTime <= dateDomain.minTime) return "";
  return athleteAnalyticsCycleBoundaries(dateDomain).map((boundary) => {
    const percent = athleteAnalyticsTimelinePercentForDate(timeline, boundary.date);
    if (percent === null) return "";
    return `
      <span
        class="athlete-analytics-cycle-marker"
        style="left: ${percent.toFixed(2)}%;"
        aria-hidden="true"
      >
        <span class="athlete-analytics-cycle-marker-label">${escapeHtml(String(boundary.year || boundary.date.slice(0, 4)))}</span>
      </span>
    `;
  }).join("");
}

function athleteAnalyticsTrendPointerRatio(figure, clientX) {
  const svg = figure?.querySelector(".athlete-trend-svg");
  const rect = svg?.getBoundingClientRect();
  if (!rect || !rect.width || typeof clientX !== "number") return 0.5;
  const leftPadding = (ATHLETE_TREND_SVG_PADDING.left / ATHLETE_TREND_SVG_WIDTH) * rect.width;
  const rightPadding = (ATHLETE_TREND_SVG_PADDING.right / ATHLETE_TREND_SVG_WIDTH) * rect.width;
  const plotLeft = rect.left + leftPadding;
  const plotRight = rect.right - rightPadding;
  const plotWidth = Math.max(1, plotRight - plotLeft);
  return clampNumber((clientX - plotLeft) / plotWidth, 0, 1);
}

function athleteAnalyticsWheelDelta(event) {
  const unit = event.deltaMode === 1
    ? 16
    : event.deltaMode === 2
      ? 240
      : 1;
  const horizontal = Number(event.deltaX) || 0;
  const vertical = Number(event.deltaY) || 0;
  const dominant = Math.abs(horizontal) > Math.abs(vertical) ? horizontal : vertical;
  return dominant * unit;
}

function athleteAnalyticsSnapshotSelectableIndexes(data) {
  const selectableDates = new Set(
    (data.selectedPoints || [])
      .map(athleteAnalyticsPointDate)
      .filter(Boolean),
  );
  return data.timeline
    .map((dateKey, index) => (selectableDates.has(dateKey) ? index : null))
    .filter((index) => index !== null);
}

function nearestSelectableIndexPosition(indexes, currentIndex) {
  const exactPosition = indexes.indexOf(currentIndex);
  if (exactPosition !== -1) return exactPosition;
  let nearestPosition = 0;
  let nearestDistance = Infinity;
  indexes.forEach((index, position) => {
    const distance = Math.abs(index - currentIndex);
    if (distance < nearestDistance) {
      nearestPosition = position;
      nearestDistance = distance;
    }
  });
  return nearestPosition;
}

function athleteAnalyticsZoomRangeFromBase(figure, clientX, factor, baseRange = null) {
  const payload = state.athleteAnalytics.payload;
  if (!payload) return false;
  const data = athleteAnalyticsPreparedData(payload);
  if (data.mode === "snapshot" || data.timeline.length < 2) return false;
  const maxIndex = data.timeline.length - 1;
  const currentStart = clampNumber(
    Number(baseRange?.startIndex ?? data.range.startIndex),
    0,
    maxIndex,
  );
  const currentEnd = clampNumber(
    Number(baseRange?.endIndex ?? data.range.endIndex),
    currentStart,
    maxIndex,
  );
  const currentSpan = Math.max(1, currentEnd - currentStart + 1);
  const minSpan = 2;
  let nextSpan = Math.round(currentSpan * factor);
  nextSpan = clampNumber(nextSpan, minSpan, maxIndex + 1);
  if (nextSpan === currentSpan) {
    if (factor < 1 && currentSpan > minSpan) nextSpan = currentSpan - 1;
    if (factor > 1 && currentSpan < maxIndex + 1) nextSpan = currentSpan + 1;
  }
  if (nextSpan === currentSpan) return false;

  const ratio = athleteAnalyticsTrendPointerRatio(figure, clientX);
  const anchorIndex = currentStart + (ratio * Math.max(0, currentSpan - 1));
  let nextStart = Math.round(anchorIndex - (ratio * Math.max(0, nextSpan - 1)));
  let nextEnd = nextStart + nextSpan - 1;
  if (nextStart < 0) {
    nextEnd -= nextStart;
    nextStart = 0;
  }
  if (nextEnd > maxIndex) {
    nextStart -= nextEnd - maxIndex;
    nextEnd = maxIndex;
  }
  nextStart = clampNumber(nextStart, 0, maxIndex);
  nextEnd = clampNumber(nextEnd, nextStart, maxIndex);
  state.athleteAnalytics.startIndex = nextStart;
  state.athleteAnalytics.endIndex = nextEnd;
  updateAthleteAnalyticsDynamicContent();
  return true;
}

let athleteTrendGestureZoomBase = null;
let athleteTrendSnapshotWheelAccumulator = 0;
let athleteAnalyticsDynamicTransitionTimer = null;
let athleteTrendInteractionCursorTimer = null;

function setAthleteTrendInteractionCursor(figure, active = true) {
  document.querySelectorAll(".athlete-trend-figure.is-interacting").forEach((element) => {
    if (!active || element !== figure) element.classList.remove("is-interacting");
  });
  if (!figure) return;
  figure.classList.toggle("is-interacting", active);
}

function flashAthleteTrendInteractionCursor(figure) {
  setAthleteTrendInteractionCursor(figure, true);
  window.clearTimeout(athleteTrendInteractionCursorTimer);
  athleteTrendInteractionCursorTimer = window.setTimeout(() => {
    setAthleteTrendInteractionCursor(figure, false);
  }, 420);
}

function moveAthleteAnalyticsSnapshotFromWheel(event, preparedData = null) {
  const payload = state.athleteAnalytics.payload;
  if (!payload && !preparedData) return false;
  const data = preparedData || athleteAnalyticsPreparedData(payload);
  if (data.mode !== "snapshot" || data.timeline.length < 2) return false;
  const selectableIndexes = athleteAnalyticsSnapshotSelectableIndexes(data);
  if (selectableIndexes.length < 2) return false;
  const delta = athleteAnalyticsWheelDelta(event);
  if (!Number.isFinite(delta) || delta === 0) return false;

  athleteTrendSnapshotWheelAccumulator += delta;
  const threshold = 34;
  let steps = Math.trunc(athleteTrendSnapshotWheelAccumulator / threshold);
  if (!steps) return true;
  steps = clampNumber(steps, -5, 5);
  athleteTrendSnapshotWheelAccumulator -= steps * threshold;

  const currentPosition = nearestSelectableIndexPosition(selectableIndexes, data.range.endIndex);
  const nextPosition = clampNumber(currentPosition + steps, 0, selectableIndexes.length - 1);
  const nextIndex = selectableIndexes[nextPosition];
  if (nextIndex === data.range.endIndex) return true;
  state.athleteAnalytics.snapshotIndex = nextIndex;
  updateAthleteAnalyticsDynamicContent();
  return true;
}

function bindAthleteTrendZoomEvents() {
  document.addEventListener("wheel", (event) => {
    const figure = event.target.closest?.(".athlete-trend-figure");
    if (!figure || figure.dataset.comparisonTrend === "true") return;
    const payload = state.athleteAnalytics.payload;
    const data = payload ? athleteAnalyticsPreparedData(payload) : null;
    if (data?.mode === "snapshot") {
      const previousSnapshotIndex = state.athleteAnalytics.snapshotIndex;
      const moved = moveAthleteAnalyticsSnapshotFromWheel(event, data);
      if (moved) {
        event.preventDefault();
        event.stopPropagation();
        if (state.athleteAnalytics.snapshotIndex !== previousSnapshotIndex) {
          flashAthleteTrendInteractionCursor(figure);
        }
      }
      return;
    }
    if (Math.abs(event.deltaY) < Math.abs(event.deltaX) && !event.ctrlKey) return;
    const factor = clampNumber(Math.exp(event.deltaY * 0.0025), 0.55, 1.85);
    const zoomed = athleteAnalyticsZoomRangeFromBase(figure, event.clientX, factor);
    if (zoomed) {
      event.preventDefault();
      event.stopPropagation();
      flashAthleteTrendInteractionCursor(figure);
    }
  }, { passive: false });

  document.addEventListener("gesturestart", (event) => {
    const figure = event.target.closest?.(".athlete-trend-figure");
    if (!figure || figure.dataset.comparisonTrend === "true" || !state.athleteAnalytics.payload) return;
    const data = athleteAnalyticsPreparedData(state.athleteAnalytics.payload);
    if (data.mode === "snapshot" || data.timeline.length < 2) return;
    athleteTrendGestureZoomBase = {
      startIndex: data.range.startIndex,
      endIndex: data.range.endIndex,
    };
    setAthleteTrendInteractionCursor(figure, true);
    event.preventDefault();
  }, { passive: false });

  document.addEventListener("gesturechange", (event) => {
    const figure = event.target.closest?.(".athlete-trend-figure");
    if (!figure || figure.dataset.comparisonTrend === "true" || !athleteTrendGestureZoomBase) return;
    const scale = Number(event.scale);
    if (!Number.isFinite(scale) || scale <= 0) return;
    const zoomed = athleteAnalyticsZoomRangeFromBase(
      figure,
      event.clientX,
      clampNumber(1 / scale, 0.2, 4),
      athleteTrendGestureZoomBase,
    );
    if (zoomed) {
      setAthleteTrendInteractionCursor(figure, true);
      event.preventDefault();
    }
  }, { passive: false });

  ["gestureend", "gesturecancel"].forEach((eventName) => {
    document.addEventListener(eventName, () => {
      athleteTrendGestureZoomBase = null;
      window.clearTimeout(athleteTrendInteractionCursorTimer);
      setAthleteTrendInteractionCursor(document.querySelector(".athlete-trend-figure.is-interacting"), false);
    });
  });
}

function renderAthleteTrendAxes(dateDomain, padding, width, height, minValue, maxValue, metric) {
  const left = padding.left;
  const right = width - padding.right;
  const top = padding.top;
  const bottom = height - padding.bottom;
  const valueRange = Math.max(1, maxValue - minValue);
  const yTicks = athleteAnalyticsYAxisTicks(metric, minValue, maxValue);
  const xTicks = athleteAnalyticsTrendXTicks(dateDomain).filter((tick) => {
    const time = athleteAnalyticsDateTime(tick.date);
    return time !== null && time >= dateDomain.minTime && time <= dateDomain.maxTime;
  });
  const cycleBoundaries = athleteAnalyticsCycleBoundaries(dateDomain);
  return `
    <line class="athlete-trend-axis" x1="${left}" y1="${bottom}" x2="${right}" y2="${bottom}"></line>
    <line class="athlete-trend-axis" x1="${left}" y1="${top}" x2="${left}" y2="${bottom}"></line>
    ${yTicks.map((tick) => {
      const y = athleteAnalyticsTrendY(tick.value, padding, height, minValue, valueRange);
      return `
        <line class="athlete-trend-gridline is-y" x1="${left}" y1="${y.toFixed(1)}" x2="${right}" y2="${y.toFixed(1)}"></line>
        <text class="athlete-trend-axis-label is-y" x="${left - 8}" y="${(y + 4).toFixed(1)}">${escapeHtml(tick.label)}</text>
      `;
    }).join("")}
    ${xTicks.map((tick) => {
      const x = athleteAnalyticsTrendX(tick.date, dateDomain, padding, width);
      return `
        <line class="athlete-trend-tick" x1="${x.toFixed(1)}" y1="${bottom}" x2="${x.toFixed(1)}" y2="${bottom + 4}"></line>
        <text class="athlete-trend-axis-label is-x" x="${x.toFixed(1)}" y="${bottom + 18}">${escapeHtml(tick.label)}</text>
      `;
    }).join("")}
    ${cycleBoundaries.map((boundary) => {
      const x = athleteAnalyticsTrendX(boundary.date, dateDomain, padding, width);
      return `
        <line class="athlete-trend-cycle-line" x1="${x.toFixed(1)}" y1="${top}" x2="${x.toFixed(1)}" y2="${bottom}"></line>
        <text class="athlete-trend-cycle-label" x="${(x + 4).toFixed(1)}" y="${top + 10}">${escapeHtml(boundary.label)}</text>
      `;
    }).join("")}
  `;
}

function athleteAnalyticsTrendScope(points, startDate, endDate, mode, forceFullPeriod = false) {
  if (!forceFullPeriod) return { startDate, endDate, mode };
  const timeline = athleteAnalyticsTimeline(points);
  return {
    startDate: "",
    endDate: timeline.at(-1) || endDate,
    mode: "period",
  };
}

function athleteAnalyticsTrendReferenceDates(points, startDate, endDate, mode) {
  const dates = athleteAnalyticsTimeline(points);
  if (mode === "snapshot") return dates;
  return dates.filter((date) => (!startDate || date >= startDate) && (!endDate || date <= endDate));
}

function athleteAnalyticsTrendDomainDates(referenceDates, startDate, endDate, mode) {
  if (mode === "snapshot") return referenceDates;
  return [...new Set([startDate, ...referenceDates, endDate].filter(Boolean))].sort();
}

function athleteAnalyticsDerivedSeriesPoints(points, definition) {
  return points
    .filter(definition.filter)
    .map((point) => {
      const value = definition.valueForPoint
        ? athleteAnalyticsNumber(definition.valueForPoint(point, points))
        : athleteAnalyticsValue(point);
      if (value === null) return null;
      return { ...point, value };
    })
    .filter(Boolean);
}

function athleteAnalyticsBackgroundSeries(points, selectedApparatuses, discipline, metric, startDate, endDate, mode) {
  const isSnapshot = mode === "snapshot";
  return athleteAnalyticsComponentDefinitions(selectedApparatuses, discipline, metric)
    .map((definition) => {
      const sourcePoints = points.filter(definition.filter);
      const componentPoints = athleteAnalyticsDerivedSeriesPoints(points, definition);
      const componentScope = athleteAnalyticsTrendScope(componentPoints, startDate, endDate, mode, isSnapshot);
      return {
        ...definition,
        referenceDates: athleteAnalyticsTrendReferenceDates(
          sourcePoints,
          componentScope.startDate,
          componentScope.endDate,
          componentScope.mode,
        ),
        trend: athleteAnalyticsTrendPoints(
          componentPoints,
          componentScope.startDate,
          componentScope.endDate,
          componentScope.mode,
        ),
      };
    })
    .filter((series) => series.trend.length >= 1)
    .filter((series) => !series.hideWhenAllZero || series.trend.some((point) => Math.abs(Number(point.value)) > 0));
}

function renderAthleteTrendSvg(points, metric, startDate, endDate, mode, selectedApparatuses, discipline) {
  const isSnapshot = mode === "snapshot";
  const mainPoints = athleteAnalyticsPointsForSelection(points, selectedApparatuses);
  const mainReferenceDates = athleteAnalyticsTrendReferenceDates(mainPoints, startDate, endDate, mode);
  const trend = athleteAnalyticsTrendPoints(mainPoints, startDate, endDate, mode);
  const contextScope = athleteAnalyticsTrendScope(mainPoints, startDate, endDate, mode, isSnapshot);
  const contextTrend = isSnapshot
    ? athleteAnalyticsTrendPoints(mainPoints, contextScope.startDate, contextScope.endDate, contextScope.mode)
    : [];
  const backgroundSeries = athleteAnalyticsBackgroundSeries(
    points,
    selectedApparatuses,
    discipline,
    metric,
    startDate,
    endDate,
    mode,
  );
  if (!trend.length) {
    return `<div class="empty-state compact-empty">${t("analyticsNoData")}</div>`;
  }
  const width = ATHLETE_TREND_SVG_WIDTH;
  const height = ATHLETE_TREND_SVG_HEIGHT;
  const padding = ATHLETE_TREND_SVG_PADDING;
  const allSeries = [trend, contextTrend, ...backgroundSeries.map((series) => series.trend)].filter((series) => series.length);
  const domainDates = athleteAnalyticsTrendDomainDates(mainReferenceDates, startDate, endDate, mode);
  const values = allSeries.flatMap((series) => series.map((point) => point.value));
  const { minValue, maxValue, valueRange } = athleteAnalyticsTrendValueDomain(metric, values);
  const dateDomain = athleteAnalyticsTrendDateDomain(domainDates);
  const contextCoordinates = athleteAnalyticsSvgCoordinates(contextTrend, domainDates, padding, width, height, minValue, valueRange, dateDomain);
  const coordinates = athleteAnalyticsSvgCoordinates(trend, domainDates, padding, width, height, minValue, valueRange, dateDomain);
  return `
    <div class="athlete-trend-figure ${isSnapshot ? "is-snapshot" : ""}">
      <svg class="athlete-trend-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(t("analyticsTrendTitle"))}">
        ${renderAthleteTrendAxes(dateDomain, padding, width, height, minValue, maxValue, metric)}
        ${isSnapshot ? renderAthleteTrendPaths(contextCoordinates, mainReferenceDates, "athlete-trend-line is-context") : ""}
        ${backgroundSeries.map((series) => {
          const seriesCoordinates = athleteAnalyticsSvgCoordinates(series.trend, domainDates, padding, width, height, minValue, valueRange, dateDomain);
          const seriesStyle = `style="--series-color: ${athleteAnalyticsComponentColor(series)};"`;
          const backgroundDots = seriesCoordinates
            .map((point) => renderAthleteTrendDot(point, series.metric || metric, "athlete-trend-dot is-background", 3.1, seriesStyle))
            .join("");
          return `
            ${renderAthleteTrendPaths(seriesCoordinates, series.referenceDates, "athlete-trend-line is-background", seriesStyle)}
            ${backgroundDots}
          `;
        }).join("")}
        ${isSnapshot ? "" : renderAthleteTrendPaths(coordinates, mainReferenceDates, "athlete-trend-line")}
        ${coordinates.map((point) => renderAthleteTrendDot(point, metric, `athlete-trend-dot ${isSnapshot ? "is-snapshot-focus" : ""}`, isSnapshot ? 5.4 : 4)).join("")}
      </svg>
      <div class="athlete-trend-tooltip" role="status" hidden></div>
      ${backgroundSeries.length ? `
        <div class="athlete-trend-legend">
          <span class="is-primary">${escapeHtml(`${athleteAnalyticsApparatusSelectionLabel(selectedApparatuses)} · ${athleteAnalyticsMetricLabel(metric)}`)}</span>
          ${backgroundSeries.map((series) => `<span style="--series-color: ${athleteAnalyticsComponentColor(series)};">${escapeHtml(series.label)}</span>`).join("")}
        </div>
      ` : ""}
    </div>
  `;
}

function athleteTrendTooltipHtml(pointNode) {
  const value = pointNode.dataset.trendValue || t("notAvailable");
  const dateLabel = pointNode.dataset.trendDate || "";
  const eventLabel = pointNode.dataset.trendEvent || "";
  return `
    <strong>${escapeHtml(value)}</strong>
    ${dateLabel ? `<span>${escapeHtml(dateLabel)}</span>` : ""}
    ${eventLabel ? `<span>${escapeHtml(eventLabel)}</span>` : ""}
  `;
}

function positionAthleteTrendTooltip(tooltip, figure, eventOrPoint) {
  const figureRect = figure.getBoundingClientRect();
  const sourceRect = typeof eventOrPoint.clientX === "number"
    ? { left: eventOrPoint.clientX, top: eventOrPoint.clientY, width: 0, height: 0 }
    : eventOrPoint.getBoundingClientRect();
  const sourceX = sourceRect.left - figureRect.left + (sourceRect.width / 2);
  const sourceY = sourceRect.top - figureRect.top + (sourceRect.height / 2);
  const tooltipWidth = tooltip.offsetWidth || 220;
  const tooltipHeight = tooltip.offsetHeight || 88;
  const x = Math.min(Math.max(12, sourceX + 12), Math.max(12, figureRect.width - tooltipWidth - 12));
  let y = sourceY - tooltipHeight - 14;
  if (y < 12) y = sourceY + 16;
  tooltip.style.left = `${Math.round(x)}px`;
  tooltip.style.top = `${Math.round(y)}px`;
}

function showAthleteTrendTooltip(pointNode, eventOrPoint = pointNode) {
  const figure = pointNode.closest(".athlete-trend-figure");
  const tooltip = figure?.querySelector(".athlete-trend-tooltip");
  if (!figure || !tooltip) return;
  tooltip.innerHTML = athleteTrendTooltipHtml(pointNode);
  tooltip.hidden = false;
  tooltip.classList.add("is-visible");
  positionAthleteTrendTooltip(tooltip, figure, eventOrPoint);
}

function hideAthleteTrendTooltip(pointNode) {
  const figure = pointNode?.closest(".athlete-trend-figure") || document.querySelector(".athlete-trend-figure");
  const tooltip = figure?.querySelector(".athlete-trend-tooltip");
  if (!tooltip) return;
  tooltip.classList.remove("is-visible");
  tooltip.hidden = true;
}

function athleteRadarTooltipHtml(pointNode) {
  const value = pointNode.dataset.radarValue || t("notAvailable");
  const apparatus = pointNode.dataset.radarApparatus || "";
  return `
    <strong>${escapeHtml(value)}</strong>
    ${apparatus ? `<span>${escapeHtml(apparatus)}</span>` : ""}
  `;
}

function positionAthleteRadarTooltip(tooltip, figure, eventOrPoint) {
  const figureRect = figure.getBoundingClientRect();
  const sourceRect = typeof eventOrPoint.clientX === "number"
    ? { left: eventOrPoint.clientX, top: eventOrPoint.clientY, width: 0, height: 0 }
    : eventOrPoint.getBoundingClientRect();
  const sourceX = sourceRect.left - figureRect.left + (sourceRect.width / 2);
  const sourceY = sourceRect.top - figureRect.top + (sourceRect.height / 2);
  const tooltipWidth = tooltip.offsetWidth || 112;
  const tooltipHeight = tooltip.offsetHeight || 46;
  const x = Math.min(Math.max(10, sourceX + 10), Math.max(10, figureRect.width - tooltipWidth - 10));
  let y = sourceY - tooltipHeight - 12;
  if (y < 10) y = sourceY + 14;
  tooltip.style.left = `${Math.round(x)}px`;
  tooltip.style.top = `${Math.round(y)}px`;
}

function showAthleteRadarTooltip(pointNode, eventOrPoint = pointNode) {
  const figure = pointNode.closest(".athlete-radar-figure");
  const tooltip = figure?.querySelector(".athlete-radar-tooltip");
  if (!figure || !tooltip) return;
  tooltip.innerHTML = athleteRadarTooltipHtml(pointNode);
  tooltip.hidden = false;
  tooltip.classList.add("is-visible");
  positionAthleteRadarTooltip(tooltip, figure, eventOrPoint);
}

function hideAthleteRadarTooltip(pointNode) {
  const figure = pointNode?.closest(".athlete-radar-figure") || document.querySelector(".athlete-radar-figure");
  const tooltip = figure?.querySelector(".athlete-radar-tooltip");
  if (!tooltip) return;
  tooltip.classList.remove("is-visible");
  tooltip.hidden = true;
}

function bindAthleteTrendTooltipEvents() {
  document.addEventListener("pointerover", (event) => {
    const point = event.target.closest?.("[data-athlete-trend-point]");
    if (point) showAthleteTrendTooltip(point, event);
  });
  document.addEventListener("pointermove", (event) => {
    const point = event.target.closest?.("[data-athlete-trend-point]");
    if (point) showAthleteTrendTooltip(point, event);
  });
  document.addEventListener("pointerout", (event) => {
    const point = event.target.closest?.("[data-athlete-trend-point]");
    const nextPoint = event.relatedTarget?.closest?.("[data-athlete-trend-point]");
    if (point && point !== nextPoint) hideAthleteTrendTooltip(point);
  });
  document.addEventListener("focusin", (event) => {
    const point = event.target.closest?.("[data-athlete-trend-point]");
    if (point) showAthleteTrendTooltip(point);
  });
  document.addEventListener("focusout", (event) => {
    const point = event.target.closest?.("[data-athlete-trend-point]");
    if (point) hideAthleteTrendTooltip(point);
  });
}

function bindAthleteRadarTooltipEvents() {
  document.addEventListener("pointerover", (event) => {
    const point = event.target.closest?.("[data-athlete-radar-point]");
    if (point) showAthleteRadarTooltip(point, event);
  });
  document.addEventListener("pointermove", (event) => {
    const point = event.target.closest?.("[data-athlete-radar-point]");
    if (point) showAthleteRadarTooltip(point, event);
  });
  document.addEventListener("pointerout", (event) => {
    const point = event.target.closest?.("[data-athlete-radar-point]");
    const nextPoint = event.relatedTarget?.closest?.("[data-athlete-radar-point]");
    if (point && point !== nextPoint) hideAthleteRadarTooltip(point);
  });
  document.addEventListener("focusin", (event) => {
    const point = event.target.closest?.("[data-athlete-radar-point]");
    if (point) showAthleteRadarTooltip(point);
  });
  document.addEventListener("focusout", (event) => {
    const point = event.target.closest?.("[data-athlete-radar-point]");
    if (point) hideAthleteRadarTooltip(point);
  });
}

function athleteAnalyticsYearBreakdown(points) {
  const grouped = new Map();
  points.forEach((point) => {
    const year = point.year || (athleteAnalyticsPointDate(point) || "").slice(0, 4);
    const value = athleteAnalyticsValue(point);
    if (!year || value === null) return;
    if (!grouped.has(String(year))) grouped.set(String(year), []);
    grouped.get(String(year)).push(value);
  });
  return [...grouped.entries()].sort(([yearA], [yearB]) => yearA.localeCompare(yearB)).map(([year, values]) => ({
    year,
    value: values.reduce((sum, value) => sum + value, 0) / values.length,
    count: values.length,
  }));
}

function renderAthleteYearBars(points, metric) {
  const years = athleteAnalyticsYearBreakdown(points);
  if (!years.length) {
    return `<div class="empty-state compact-empty">${t("analyticsNoData")}</div>`;
  }
  const maxValue = athleteAnalyticsScaleMax(metric, years.map((item) => item.value));
  return `
    <div class="athlete-year-bars">
      ${years.map((item) => {
        const width = Math.max(2, Math.min(100, (item.value / maxValue) * 100));
        return `
          <div class="athlete-year-bar-row">
            <span>${escapeHtml(item.year)}</span>
            <div class="athlete-year-bar-track">
              <div class="athlete-year-bar-fill" style="width: ${width.toFixed(1)}%;"></div>
            </div>
            <strong>${escapeHtml(athleteAnalyticsFormatValue(item.value, metric))}</strong>
            <small>${escapeHtml(localizedCount(item.count, "analyticsResultSingular", "analyticsResultPlural"))}</small>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

function renderAthleteAnalyticsRangeValues(mode, startDate, endDate, points = []) {
  const snapshotMode = mode === "snapshot";
  const startValue = startDate ? athleteAnalyticsTimelineDateLabel(points, startDate) : t("notAvailable");
  const endValue = snapshotMode
    ? athleteAnalyticsSnapshotDateLabel(points, endDate)
    : (endDate ? athleteAnalyticsTimelineDateLabel(points, endDate) : t("notAvailable"));
  if (snapshotMode) {
    return `<span><em>${escapeHtml(t("date"))}</em><strong id="athleteAnalyticsEndLabel">${escapeHtml(endValue)}</strong></span>`;
  }
  return `
    <span><em>${escapeHtml(t("fromDate"))}</em><strong id="athleteAnalyticsStartLabel">${escapeHtml(startValue)}</strong></span>
    <span><em>${escapeHtml(t("toDate"))}</em><strong id="athleteAnalyticsEndLabel">${escapeHtml(endValue)}</strong></span>
  `;
}

function renderAthleteAnalyticsStat(label, value) {
  return `
    <div class="athlete-analytics-stat">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
    </div>
  `;
}

function renderAthleteAnalyticsControls(timeline, range, metric, mode, selectedApparatuses, discipline, timelineLabelPoints = []) {
  const selectedMetricIndex = Math.max(0, ATHLETE_ANALYTICS_METRICS.findIndex((item) => item.value === metric));
  const selectedModeIndex = mode === "snapshot" ? 1 : 0;
  const apparatusOptions = athleteAnalyticsApparatusOptions(discipline);
  const maxIndex = Math.max(0, timeline.length - 1);
  const startIndex = Math.max(0, range.startIndex);
  const endIndex = Math.max(0, range.endIndex);
  const startPercent = maxIndex ? (startIndex / maxIndex) * 100 : 0;
  const endPercent = maxIndex ? (endIndex / maxIndex) * 100 : 100;
  const startDate = timeline[startIndex] || "";
  const endDate = timeline[endIndex] || "";
  const snapshotMode = mode === "snapshot";
  const visualStartPercent = snapshotMode ? endPercent : startPercent;
  return `
    <div class="athlete-analytics-controls">
      <div class="athlete-analytics-filter-cluster">
        <div class="athlete-analytics-control-group athlete-analytics-apparatus-group">
          <div class="athlete-analytics-apparatus-buttons" role="group" aria-label="${escapeHtml(t("apparatus"))}">
            ${apparatusOptions.map((apparatus) => `
              <button
                class="quiet-button athlete-analytics-apparatus-button ${selectedApparatuses.includes(apparatus) ? "is-active" : ""}"
                type="button"
                data-athlete-analytics-apparatus="${escapeHtml(apparatus)}"
                aria-pressed="${String(selectedApparatuses.includes(apparatus))}"
              >${escapeHtml(athleteAnalyticsApparatusLabel(apparatus))}</button>
            `).join("")}
          </div>
        </div>
        <div class="athlete-analytics-control-group athlete-analytics-score-group">
          <div
            class="segmented-control athlete-analytics-metric-control"
            role="radiogroup"
            aria-label="${escapeHtml(t("analyticsMetric"))}"
            style="--segment-count: ${ATHLETE_ANALYTICS_METRICS.length}; --selected-index: ${selectedMetricIndex};"
          >
            ${ATHLETE_ANALYTICS_METRICS.map((item) => `
              <button
                class="segmented-option athlete-analytics-metric-option"
                type="button"
                role="radio"
                data-athlete-analytics-metric="${escapeHtml(item.value)}"
                aria-checked="${String(metric === item.value)}"
              >${escapeHtml(item.label)}</button>
            `).join("")}
            <span class="segmented-thumb athlete-analytics-metric-thumb" aria-hidden="true"></span>
          </div>
        </div>
        <div class="athlete-analytics-time-cluster">
          <div class="athlete-analytics-control-group athlete-analytics-mode-group">
            <div
              class="segmented-control athlete-analytics-mode-control"
              role="radiogroup"
              aria-label="${escapeHtml(t("analyticsMode"))}"
              style="--segment-count: 2; --selected-index: ${selectedModeIndex};"
            >
              <button class="segmented-option" type="button" role="radio" data-athlete-analytics-mode="period" aria-checked="${String(mode === "period")}">${escapeHtml(t("analyticsModePeriod"))}</button>
              <button class="segmented-option" type="button" role="radio" data-athlete-analytics-mode="snapshot" aria-checked="${String(mode === "snapshot")}">${escapeHtml(t("analyticsModeSnapshot"))}</button>
              <span class="segmented-thumb athlete-analytics-mode-thumb" aria-hidden="true"></span>
            </div>
          </div>
          <div class="athlete-analytics-timeline" role="group" aria-label="${escapeHtml(t("analyticsTimeline"))}">
            <div
              class="athlete-analytics-range-shell ${snapshotMode ? "is-snapshot" : ""}"
              style="--range-start: ${visualStartPercent.toFixed(2)}%; --range-end: ${endPercent.toFixed(2)}%;"
            >
              <div class="athlete-analytics-range-track" aria-hidden="true">
                <span class="athlete-analytics-range-selected"></span>
              </div>
              <div class="athlete-analytics-cycle-markers" aria-hidden="true">
                ${renderAthleteAnalyticsTimelineCycleMarkers(timeline)}
              </div>
              <input
                id="athleteAnalyticsStartTimeline"
                class="athlete-analytics-range-input athlete-analytics-range-start"
                type="range"
                min="0"
                max="${maxIndex}"
                step="1"
                value="${startIndex}"
                aria-label="${escapeHtml(t("fromDate"))}"
                ${timeline.length && !snapshotMode ? "" : "disabled"}
              >
              <input
                id="athleteAnalyticsEndTimeline"
                class="athlete-analytics-range-input athlete-analytics-range-end"
                type="range"
                min="0"
                max="${maxIndex}"
                step="1"
                value="${endIndex}"
                aria-label="${escapeHtml(snapshotMode ? t("date") : t("toDate"))}"
                ${timeline.length ? "" : "disabled"}
              >
            </div>
            <div class="athlete-analytics-range-values ${snapshotMode ? "is-snapshot" : ""}">
              ${renderAthleteAnalyticsRangeValues(mode, startDate, endDate, timelineLabelPoints)}
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function athleteAnalyticsPreparedData(payload) {
  const metric = state.athleteAnalytics.metric;
  const mode = state.athleteAnalytics.mode === "snapshot" ? "snapshot" : "period";
  const discipline = payload.athlete?.discipline || "MAG";
  const basePoints = [...(payload.dashboard?.trend || [])].sort((a, b) => athleteAnalyticsSortKey(a).localeCompare(athleteAnalyticsSortKey(b)));
  const points = athleteAnalyticsPointsForMetric(basePoints, metric, discipline)
    .sort((a, b) => athleteAnalyticsSortKey(a).localeCompare(athleteAnalyticsSortKey(b)));
  const timeline = athleteAnalyticsTimeline(basePoints);
  const range = athleteAnalyticsCurrentRange(timeline, mode);
  const selectedApparatuses = athleteAnalyticsSelectedApparatuses(discipline);
  state.athleteAnalytics.apparatuses = selectedApparatuses;
  const selectedPoints = athleteAnalyticsPointsForSelection(points, selectedApparatuses);
  const includedPoints = athleteAnalyticsIncludedPoints(selectedPoints, range.startDate, range.endDate, mode);
  const timelineLabelPoints = mode === "snapshot"
    ? athleteAnalyticsSnapshotContextPoints(points, selectedPoints, range.endDate)
    : includedPoints;
  const summary = athleteAnalyticsSummary(includedPoints, metric);
  const vertices = athleteAnalyticsBuildVertices(points, discipline, metric, mode, range.startDate, range.endDate);
  const availableValues = vertices.some((vertex) => vertex.value !== null && vertex.value !== undefined);
  const uniqueWarnings = localizedBackendWarnings(includedPoints.flatMap((point) => point.data_warnings || []));
  const scoringCycles = athleteAnalyticsScoringCycles(includedPoints);
  const eventPeriodPoints = includedPoints.filter(athleteAnalyticsPointUsesEventPeriod);
  const multiDayPoints = includedPoints.filter(athleteAnalyticsPointIsMultiDayEvent);
  return {
    metric,
    mode,
    discipline,
    selectedApparatuses,
    points,
    selectedPoints,
    timeline,
    range,
    includedPoints,
    timelineLabelPoints,
    summary,
    vertices,
    availableValues,
    uniqueWarnings,
    scoringCycles,
    eventPeriodPoints,
    multiDayPoints,
  };
}

function renderAthleteAnalyticsScoringCycleContext(cycles, discipline = "") {
  if (!cycles.length) return "";
  const labels = cycles.map((cycle) => cycle.label).join(", ");
  const contextDetails = [
    discipline,
    `${t("scoringCycle")} ${labels}`,
  ].filter(Boolean);
  const warnings = cycles.length > 1 ? [t("analyticsMultipleScoringCyclesNotice")] : [];
  return `
    <div class="context-note athlete-analytics-cycle-context">
      <span><strong class="context-note-lead">ANALYTICS</strong>${contextDetails.length ? ` · ${escapeHtml(contextDetails.join(" · "))}` : ""}</span>
      ${warnings.map((warning) => `<span>${escapeHtml(warning)}</span>`).join("")}
    </div>
  `;
}

function renderAthleteAnalyticsDateSourceContext(data) {
  const includedPoints = data.includedPoints || [];
  if (!includedPoints.length) return "";
  const eventPeriodPoints = data.eventPeriodPoints || [];
  const multiDayPoints = data.multiDayPoints || [];
  const summaries = athleteAnalyticsEventSummaries(includedPoints);
  const periodLabel = athleteAnalyticsUniqueLimitedLabels(
    (multiDayPoints.length ? multiDayPoints : includedPoints).map(athleteAnalyticsPointEventPeriodLabel),
    4,
  );
  const contextLabel = athleteAnalyticsUniqueLimitedLabels(
    (eventPeriodPoints.length ? eventPeriodPoints : multiDayPoints).map(athleteAnalyticsContextLabel),
    2,
  );
  const summary = multiDayPoints.length
    ? t("analyticsDateSourcePeriodSummary")
    : t("analyticsDateSourceDefaultSummary");
  return `
    <div class="context-note athlete-analytics-date-context">
      <span>${escapeHtml(t("analyticsDateSource"))}: ${escapeHtml(periodLabel || t("analyticsEventPeriod"))}</span>
      <span>${escapeHtml(summary)}</span>
      ${summaries.length ? `
        <div class="athlete-analytics-date-event-list">
          ${summaries.slice(0, 5).map((item) => `
            <div class="athlete-analytics-date-event">
              <strong>${escapeHtml(item.eventName)}</strong>
              <span>${escapeHtml(item.period)}</span>
              ${item.roundFormats.length ? `<small>${escapeHtml(t("analyticsRoundFormats"))}: ${escapeHtml(item.roundFormats.join(", "))}</small>` : ""}
            </div>
          `).join("")}
          ${summaries.length > 5 ? `<small class="athlete-analytics-date-more">+${escapeHtml(localizedCount(summaries.length - 5, "analyticsMoreEventSingular", "analyticsMoreEvents"))}</small>` : ""}
        </div>
      ` : ""}
      ${contextLabel ? `<span>${escapeHtml(contextLabel)}</span>` : ""}
    </div>
  `;
}

function renderAthleteAnalyticsShapeBlock(data) {
  return `
    <div class="athlete-analytics-chart-block athlete-shape-chart-block">
      <div class="section-header compact-section-header">
        <div>
          <h2>${escapeHtml(t("analyticsShapeTitle"))}</h2>
          <p>${escapeHtml(athleteAnalyticsMetricLabel(data.metric))}</p>
        </div>
      </div>
      ${data.availableValues ? renderAthleteAnalyticsShape(data.vertices, data.metric, data.selectedApparatuses, data.discipline) : `<div class="empty-state compact-empty">${escapeHtml(t("analyticsNoApparatusData"))}</div>`}
      ${data.availableValues ? renderAthleteAnalyticsShapeLegend(data) : ""}
    </div>
  `;
}

function renderAthleteAnalyticsTrendBlock(data) {
  return `
    <div class="athlete-analytics-chart-block athlete-trend-chart-block">
      <div class="section-header compact-section-header">
        <div>
          <h2>${escapeHtml(t("analyticsTrendTitle"))}</h2>
          <p>${escapeHtml(localizedCount(data.includedPoints.length, "analyticsPointSingular", "analyticsPointPlural"))}</p>
        </div>
      </div>
      ${renderAthleteTrendSvg(data.points, data.metric, data.range.startDate, data.range.endDate, data.mode, data.selectedApparatuses, data.discipline)}
    </div>
  `;
}

function renderAthleteAnalyticsYearBlock(data) {
  return `
    <div class="athlete-analytics-chart-block athlete-year-chart-block">
      <div class="section-header compact-section-header">
        <div>
          <h2>${escapeHtml(t("analyticsYearTitle"))}</h2>
          <p>${escapeHtml(athleteAnalyticsMetricLabel(data.metric))}</p>
        </div>
      </div>
      ${renderAthleteYearBars(data.includedPoints, data.metric)}
    </div>
  `;
}

function renderAthleteAnalyticsSummaryGrid(data) {
  return `
    <div class="athlete-analytics-summary-grid">
      ${renderAthleteAnalyticsStat(t("analyticsAverage"), athleteAnalyticsFormatValue(data.summary.average, data.metric))}
      ${renderAthleteAnalyticsStat(t("analyticsBest"), athleteAnalyticsFormatValue(data.summary.best, data.metric))}
      ${renderAthleteAnalyticsStat(t("analyticsLatest"), athleteAnalyticsFormatValue(data.summary.latest, data.metric))}
      ${renderAthleteAnalyticsStat(t("analyticsEvents"), String(data.summary.eventCount))}
      ${renderAthleteAnalyticsStat(t("analyticsTotalResults"), String(data.summary.resultCount))}
    </div>
  `;
}

function renderAthleteAnalyticsNoticeStack(data) {
  const warningStack = renderDataWarningStack([
    data.metric === "execution_estimate" ? t("analyticsEEstimateNotice") : "",
    !data.points.length ? t("analyticsMetricUnavailable") : "",
    ...data.uniqueWarnings,
  ], "athlete-analytics-warning-stack");
  const notices = [
    warningStack,
  ].filter(Boolean);
  if (!notices.length) return "";
  return `
    <div class="athlete-analytics-notice-stack">
      ${notices.join("")}
    </div>
  `;
}

function renderAthleteAnalyticsDynamicContent(data) {
  return `
    <div class="athlete-analytics-primary-stack">
      ${renderAthleteAnalyticsScoringCycleContext(data.scoringCycles, data.discipline)}
      <div class="athlete-analytics-visual-grid">
        <div id="athleteAnalyticsShapeContainer" class="athlete-analytics-shape-container">
          ${renderAthleteAnalyticsShapeBlock(data)}
        </div>
        <div class="athlete-analytics-trend-container">
          ${renderAthleteAnalyticsTrendBlock(data)}
        </div>
      </div>
    </div>
    <div class="athlete-analytics-secondary-grid">
      ${renderAthleteAnalyticsYearBlock(data)}
    </div>
    ${renderAthleteAnalyticsSummaryGrid(data)}
    ${renderAthleteAnalyticsNoticeStack(data)}
  `;
}

function renderAthleteAnalyticsControlsContent(data) {
  return `
    ${renderAthleteAnalyticsControls(
      data.timeline,
      data.range,
      data.metric,
      data.mode,
      data.selectedApparatuses,
      data.discipline,
      data.timelineLabelPoints,
    )}
  `;
}

function renderAthleteAnalyticsContent(data) {
  return `
    <div id="athleteAnalyticsDynamicContent" class="athlete-analytics-dynamic-content">
      ${renderAthleteAnalyticsDynamicContent(data)}
    </div>
  `;
}

function updateAthleteAnalyticsDynamicContent({ animate = false } = {}) {
  if (!state.athleteAnalytics.payload) return;
  const dynamicContainer = $("#athleteAnalyticsDynamicContent");
  const applyUpdate = () => {
    const data = athleteAnalyticsPreparedData(state.athleteAnalytics.payload);
    syncAthleteAnalyticsTimelineControl(data);
    if (!dynamicContainer) return;
    dynamicContainer.innerHTML = renderAthleteAnalyticsDynamicContent(data);
  };
  const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
  applyUpdate();
  if (animate && dynamicContainer && !reduceMotion) {
    window.clearTimeout(athleteAnalyticsDynamicTransitionTimer);
    dynamicContainer.classList.remove("is-metric-transition");
    void dynamicContainer.offsetWidth;
    dynamicContainer.classList.add("is-metric-transition");
    athleteAnalyticsDynamicTransitionTimer = window.setTimeout(() => {
      dynamicContainer.classList.remove("is-metric-transition");
    }, 180);
  }
}

function syncAthleteAnalyticsMetricControl(metric) {
  const selectedIndex = Math.max(0, ATHLETE_ANALYTICS_METRICS.findIndex((item) => item.value === metric));
  document.querySelectorAll("[data-athlete-analytics-metric]").forEach((option) => {
    const isSelected = option.dataset.athleteAnalyticsMetric === metric;
    option.setAttribute("aria-checked", String(isSelected));
  });
  document.querySelector(".athlete-analytics-metric-control")?.style.setProperty("--selected-index", selectedIndex);
}

function syncAthleteAnalyticsApparatusControl(selectedApparatuses) {
  const selectedSet = new Set(selectedApparatuses);
  document.querySelectorAll("[data-athlete-analytics-apparatus]").forEach((button) => {
    const isSelected = selectedSet.has(button.dataset.athleteAnalyticsApparatus);
    button.classList.toggle("is-active", isSelected);
    button.setAttribute("aria-pressed", String(isSelected));
  });
}

function syncAthleteAnalyticsTimelineControl(data) {
  const maxIndex = Math.max(0, data.timeline.length - 1);
  const startTimeline = $("#athleteAnalyticsStartTimeline");
  const endTimeline = $("#athleteAnalyticsEndTimeline");
  const snapshotMode = data.mode === "snapshot";
  if (startTimeline) {
    startTimeline.max = String(maxIndex);
    startTimeline.value = String(Math.max(0, data.range.startIndex));
    startTimeline.disabled = !data.timeline.length || snapshotMode;
  }
  if (endTimeline) {
    endTimeline.max = String(maxIndex);
    endTimeline.value = String(Math.max(0, data.range.endIndex));
    endTimeline.disabled = !data.timeline.length;
  }
  const shell = document.querySelector(".athlete-analytics-range-shell");
  if (shell) {
    const startPercent = maxIndex ? (Math.max(0, data.range.startIndex) / maxIndex) * 100 : 0;
    const endPercent = maxIndex ? (Math.max(0, data.range.endIndex) / maxIndex) * 100 : 100;
    const visualStartPercent = snapshotMode ? endPercent : startPercent;
    shell.style.setProperty("--range-start", `${visualStartPercent.toFixed(2)}%`);
    shell.style.setProperty("--range-end", `${endPercent.toFixed(2)}%`);
    shell.classList.toggle("is-snapshot", snapshotMode);
  }
  const cycleMarkers = shell?.querySelector(".athlete-analytics-cycle-markers");
  if (cycleMarkers) cycleMarkers.innerHTML = renderAthleteAnalyticsTimelineCycleMarkers(data.timeline);
  const valuesContainer = document.querySelector(".athlete-analytics-range-values");
  if (valuesContainer) {
    valuesContainer.classList.toggle("is-snapshot", snapshotMode);
    valuesContainer.innerHTML = renderAthleteAnalyticsRangeValues(data.mode, data.range.startDate, data.range.endDate, data.timelineLabelPoints);
  }
  const startLabel = $("#athleteAnalyticsStartLabel");
  if (startLabel) {
    startLabel.textContent = data.range.startDate
      ? athleteAnalyticsTimelineDateLabel(data.timelineLabelPoints, data.range.startDate)
      : t("notAvailable");
  }
  const endLabel = $("#athleteAnalyticsEndLabel");
  if (endLabel) {
    endLabel.textContent = snapshotMode
      ? athleteAnalyticsSnapshotDateLabel(data.timelineLabelPoints, data.range.endDate)
      : (data.range.endDate ? athleteAnalyticsTimelineDateLabel(data.timelineLabelPoints, data.range.endDate) : t("notAvailable"));
  }
}

function renderAthleteAnalyticsShell() {
  return `
    <section class="athlete-analytics-panel">
      <div class="athlete-analytics-sticky-menu">
        <div id="athleteAnalyticsControlsHost" class="athlete-analytics-controls-host">${loadingState()}</div>
      </div>
      <div id="athleteAnalyticsContent">${loadingState()}</div>
    </section>
  `;
}

function bindAthleteAnalyticsControls(athleteId) {
  document.querySelectorAll("[data-athlete-analytics-metric]").forEach((button) => {
    button.addEventListener("click", () => {
      const metric = button.dataset.athleteAnalyticsMetric || "score";
      if (state.athleteAnalytics.metric === metric) return;
      state.athleteAnalytics.metric = metric;
      athleteTrendSnapshotWheelAccumulator = 0;
      syncAthleteAnalyticsMetricControl(metric);
      updateAthleteAnalyticsDynamicContent({ animate: true });
    });
  });
  document.querySelectorAll("[data-athlete-analytics-apparatus]").forEach((button) => {
    button.addEventListener("click", () => {
      const apparatus = button.dataset.athleteAnalyticsApparatus || "all";
      const payload = state.athleteAnalytics.payload;
      const discipline = payload?.athlete?.discipline || "MAG";
      const currentApparatuses = athleteAnalyticsSelectedApparatuses(discipline);
      const nextApparatuses = toggleExclusiveApparatusSelection(currentApparatuses, apparatus);
      state.athleteAnalytics.apparatuses = nextApparatuses;
      athleteTrendSnapshotWheelAccumulator = 0;
      syncAthleteAnalyticsApparatusControl(nextApparatuses);
      updateAthleteAnalyticsDynamicContent();
    });
  });
  document.querySelectorAll("[data-athlete-analytics-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      const mode = button.dataset.athleteAnalyticsMode === "snapshot" ? "snapshot" : "period";
      if (state.athleteAnalytics.mode === mode) return;
      state.athleteAnalytics.mode = mode;
      athleteTrendSnapshotWheelAccumulator = 0;
      updateAthleteAnalyticsDynamicContent();
      document.querySelectorAll("[data-athlete-analytics-mode]").forEach((option) => {
        const isSelected = option.dataset.athleteAnalyticsMode === mode;
        option.setAttribute("aria-checked", String(isSelected));
      });
      const control = document.querySelector(".athlete-analytics-mode-control");
      if (control) control.style.setProperty("--selected-index", mode === "snapshot" ? 1 : 0);
    });
  });
  const setTimelineHandle = (field, value) => {
    const payload = state.athleteAnalytics.payload;
    const data = payload ? athleteAnalyticsPreparedData(payload) : null;
    const maxIndex = Math.max(0, (data?.timeline.length || 1) - 1);
    let nextValue = Math.max(0, Math.min(maxIndex, Number(value)));
    if (state.athleteAnalytics.mode === "snapshot") {
      state.athleteAnalytics.snapshotIndex = nextValue;
      updateAthleteAnalyticsDynamicContent();
      return;
    }
    const currentStart = Math.max(0, Number(state.athleteAnalytics.startIndex));
    const currentEnd = Math.max(0, Number(state.athleteAnalytics.endIndex));
    if (field === "start") {
      nextValue = Math.min(nextValue, currentEnd);
      state.athleteAnalytics.startIndex = nextValue;
    } else {
      nextValue = Math.max(nextValue, currentStart);
      state.athleteAnalytics.endIndex = nextValue;
    }
    updateAthleteAnalyticsDynamicContent();
  };
  const bindTimelineInput = (input, field) => {
    input?.addEventListener("input", (event) => {
      setTimelineHandle(field, event.currentTarget.value);
    });
    input?.addEventListener("pointerdown", () => {
      input.classList.add("is-dragging");
    });
    ["pointerup", "pointercancel", "blur", "change"].forEach((eventName) => {
      input?.addEventListener(eventName, () => {
        input.classList.remove("is-dragging");
      });
    });
  };
  bindTimelineInput($("#athleteAnalyticsStartTimeline"), "start");
  bindTimelineInput($("#athleteAnalyticsEndTimeline"), "end");
}

let athleteAnalyticsRequestId = 0;

async function loadAthleteAnalytics(athleteId, { preserveControls = false } = {}) {
  const container = $("#athleteAnalyticsContent");
  if (!container) return;
  const controlsHost = $("#athleteAnalyticsControlsHost");
  const requestId = ++athleteAnalyticsRequestId;
  const dynamicContainer = $("#athleteAnalyticsDynamicContent");
  if (preserveControls && dynamicContainer) {
    dynamicContainer.classList.add("is-loading");
    dynamicContainer.innerHTML = `<div class="athlete-analytics-soft-loading">${loadingState()}</div>`;
  } else {
    if (controlsHost) controlsHost.innerHTML = loadingState();
    container.innerHTML = loadingState();
  }
  try {
    const payload = await getJson(`/analytics/athletes/${athleteId}/profile-view`, {
      metric: state.athleteAnalytics.metric,
      criterion: state.athleteAnalytics.mode === "snapshot" ? "latest" : "average",
    });
    if (requestId !== athleteAnalyticsRequestId) return;
    state.athleteAnalytics.payload = payload;
    const data = athleteAnalyticsPreparedData(payload);
    if (preserveControls && dynamicContainer) {
      syncAthleteAnalyticsMetricControl(data.metric);
      syncAthleteAnalyticsApparatusControl(data.selectedApparatuses);
      syncAthleteAnalyticsTimelineControl(data);
      dynamicContainer.classList.remove("is-loading");
      dynamicContainer.innerHTML = renderAthleteAnalyticsDynamicContent(data);
    } else {
      if (controlsHost) controlsHost.innerHTML = renderAthleteAnalyticsControlsContent(data);
      container.innerHTML = renderAthleteAnalyticsContent(data);
      bindAthleteAnalyticsControls(athleteId);
    }
  } catch (error) {
    if (requestId !== athleteAnalyticsRequestId) return;
    if (preserveControls && dynamicContainer) {
      dynamicContainer.classList.remove("is-loading");
      dynamicContainer.innerHTML = errorState(error);
    } else {
      if (controlsHost) controlsHost.innerHTML = "";
      container.innerHTML = errorState(error);
    }
  }
}

let analyticsComparisonSearchRequestId = 0;
let analyticsComparisonProfileRequestId = 0;

function analyticsComparisonDiscipline() {
  return state.analyticsComparison.athletes.find(Boolean)?.discipline || "MAG";
}

function analyticsComparisonSelectedApparatuses() {
  const options = athleteAnalyticsApparatusOptions(analyticsComparisonDiscipline());
  const selected = normalizeExclusiveApparatusSelection(
    [...new Set(state.analyticsComparison.apparatuses || [])].filter((apparatus) => options.includes(apparatus)),
  );
  const resolved = selected.length ? selected : ["AA"];
  state.analyticsComparison.apparatuses = resolved;
  return options.filter((apparatus) => resolved.includes(apparatus));
}

function analyticsComparisonTimeline() {
  return [...new Set(state.analyticsComparison.payloads
    .filter(Boolean)
    .flatMap((payload) => (payload.dashboard?.trend || []).map(athleteAnalyticsPointDate))
    .filter(Boolean))]
    .sort();
}

function analyticsComparisonCurrentRange(timeline) {
  const comparison = state.analyticsComparison;
  if (!timeline.length) {
    comparison.startIndex = -1;
    comparison.endIndex = -1;
    comparison.snapshotIndex = -1;
    return { startIndex: -1, endIndex: -1, startDate: "", endDate: "" };
  }
  const maxIndex = timeline.length - 1;
  if (comparison.mode === "snapshot") {
    let snapshotIndex = Number(comparison.snapshotIndex);
    if (!Number.isInteger(snapshotIndex) || snapshotIndex < 0 || snapshotIndex > maxIndex) snapshotIndex = maxIndex;
    comparison.snapshotIndex = snapshotIndex;
    return {
      startIndex: snapshotIndex,
      endIndex: snapshotIndex,
      startDate: timeline[snapshotIndex],
      endDate: timeline[snapshotIndex],
    };
  }
  let startIndex = Number(comparison.startIndex);
  let endIndex = Number(comparison.endIndex);
  if (
    !Number.isInteger(startIndex) || startIndex < 0 || startIndex > maxIndex ||
    !Number.isInteger(endIndex) || endIndex < 0 || endIndex > maxIndex
  ) {
    ({ startIndex, endIndex } = athleteAnalyticsDefaultCycleRange(timeline));
  }
  startIndex = Math.min(startIndex, endIndex);
  comparison.startIndex = startIndex;
  comparison.endIndex = endIndex;
  return {
    startIndex,
    endIndex,
    startDate: timeline[startIndex],
    endDate: timeline[endIndex],
  };
}

function analyticsComparisonPreparedData() {
  const comparison = state.analyticsComparison;
  const discipline = analyticsComparisonDiscipline();
  const selectedApparatuses = analyticsComparisonSelectedApparatuses();
  const timeline = analyticsComparisonTimeline();
  const range = analyticsComparisonCurrentRange(timeline);
  const athleteData = comparison.payloads.filter(Boolean).map((payload, index) => {
    const basePoints = [...(payload.dashboard?.trend || [])]
      .sort((left, right) => athleteAnalyticsSortKey(left).localeCompare(athleteAnalyticsSortKey(right)));
    const points = athleteAnalyticsPointsForMetric(basePoints, comparison.metric, discipline)
      .sort((left, right) => athleteAnalyticsSortKey(left).localeCompare(athleteAnalyticsSortKey(right)));
    const selectedPoints = athleteAnalyticsPointsForSelection(points, selectedApparatuses);
    const includedPoints = athleteAnalyticsIncludedPoints(
      selectedPoints,
      range.startDate,
      range.endDate,
      comparison.mode,
    );
    const vertices = athleteAnalyticsBuildVertices(
      points,
      discipline,
      comparison.metric,
      comparison.mode,
      range.startDate,
      range.endDate,
    );
    const trendScope = comparison.mode === "snapshot"
      ? { startDate: "", endDate: timeline.at(-1) || range.endDate, mode: "period" }
      : { startDate: range.startDate, endDate: range.endDate, mode: "period" };
    const contextTrend = athleteAnalyticsTrendPoints(
      selectedPoints,
      trendScope.startDate,
      trendScope.endDate,
      trendScope.mode,
    );
    const trend = athleteAnalyticsTrendPoints(
      selectedPoints,
      range.startDate,
      range.endDate,
      comparison.mode,
    );
    return {
      athlete: payload.athlete,
      color: ANALYTICS_COMPARISON_COLORS[index],
      points,
      selectedPoints,
      includedPoints,
      vertices,
      trend,
      contextTrend,
      summary: athleteAnalyticsSummary(includedPoints, comparison.metric),
      warnings: localizedBackendWarnings(includedPoints.flatMap((point) => point.data_warnings || [])),
    };
  });
  const radarValues = athleteData.flatMap((item) => item.vertices.map((vertex) => vertex.value));
  const radarMax = athleteAnalyticsScaleMax(comparison.metric, radarValues);
  const domainDates = comparison.mode === "snapshot"
    ? timeline
    : timeline.filter((date) => date >= range.startDate && date <= range.endDate);
  const trendValues = athleteData.flatMap((item) => (
    comparison.mode === "snapshot" ? item.contextTrend : item.trend
  ).map((point) => point.value));
  const trendValueDomain = athleteAnalyticsTrendValueDomain(comparison.metric, trendValues);
  return {
    discipline,
    selectedApparatuses,
    timeline,
    range,
    athleteData,
    radarMax,
    dateDomain: athleteAnalyticsTrendDateDomain(domainDates),
    trendValueDomain,
    cycles: athleteAnalyticsScoringCycles(athleteData.flatMap((item) => item.includedPoints)),
  };
}

function renderAnalyticsComparisonSelectedAthlete(athlete, slot) {
  const label = t(slot === 0 ? "analyticsCompareAthleteA" : "analyticsCompareAthleteB");
  const name = athleteCardDisplayName(athlete, `${t("athlete")} ${athlete.id}`);
  return `
    <article class="analytics-comparison-picker is-selected" style="--athlete-color: ${ANALYTICS_COMPARISON_COLORS[slot]};">
      <span class="analytics-comparison-picker-label">${escapeHtml(label)}</span>
      <div class="analytics-comparison-selected-athlete">
        <span class="analytics-comparison-color-dot" aria-hidden="true"></span>
        <div>
          <strong>${escapeHtml(name)}</strong>
          <span>${escapeHtml([athlete.country, athlete.discipline, `ID ${athlete.id}`].filter(Boolean).join(" · "))}</span>
        </div>
        <button class="icon-button analytics-comparison-remove" type="button" data-analytics-remove-athlete="${slot}" aria-label="${escapeHtml(t("analyticsCompareRemove"))}" title="${escapeHtml(t("analyticsCompareRemove"))}"><span aria-hidden="true">&times;</span></button>
      </div>
    </article>
  `;
}

function analyticsCompatibleFavoriteDetails() {
  const comparison = state.analyticsComparison;
  const selectedAthletes = comparison.athletes.filter(Boolean);
  if (selectedAthletes.length >= 2) return [];
  const selectedIds = new Set(selectedAthletes.map((athlete) => Number(athlete.id)));
  const discipline = selectedAthletes[0]?.discipline || "";
  return sortFavoriteAthleteDetails(comparison.favoriteDetails.filter((detail) => {
    const athlete = detail.athlete || {};
    return athlete.id &&
      !selectedIds.has(Number(athlete.id)) &&
      (!discipline || athlete.discipline === discipline);
  }));
}

function renderAnalyticsFavoriteAthletes() {
  const comparison = state.analyticsComparison;
  if (comparison.favoritesLoading) {
    return `<div class="analytics-favorite-picker-status">${escapeHtml(t("loading"))}</div>`;
  }
  if (comparison.favoritesError) {
    return `<div class="analytics-favorite-picker-status">${escapeHtml(t("analyticsCompareFavoriteError"))}</div>`;
  }
  const details = analyticsCompatibleFavoriteDetails();
  if (!details.length) {
    return `<div class="analytics-favorite-picker-status">${escapeHtml(t("analyticsCompareFavoriteEmpty"))}</div>`;
  }
  return `
    <div class="grid-3 athlete-results-list account-preference-card-list analytics-favorite-athlete-grid">
      ${details.map((detail) => {
        const athlete = detail.athlete || {};
        const name = athleteCardDisplayName(athlete, `${t("athlete")} ${detail.athlete_id}`);
        const meta = [
          athlete.world_gymnastics_status,
          `${Number(detail.result_count || 0).toLocaleString()} ${t("results")}`,
          `${t("savedOn")} ${formatReadableDate(String(detail.created_at || "").slice(0, 10))}`,
        ].filter(Boolean).join(" · ");
        return `
          <article class="entity-card entity-card-clickable analytics-favorite-athlete-card" role="button" tabindex="0" data-analytics-favorite-athlete-id="${Number(detail.athlete_id)}">
            <div class="entity-row">
              <h3>${escapeHtml(name)}</h3>
              <span class="favorite-button is-active analytics-favorite-static" aria-hidden="true"><span>&#9733;</span></span>
            </div>
            <p class="meta">${escapeHtml(meta)}</p>
            <div class="pill-row">
              ${renderPill({ label: escapeHtml(athlete.discipline || t("discipline")), variant: "brand" })}
              ${renderPill({ label: escapeHtml(athlete.country || t("country")) })}
              ${renderPill({ label: escapeHtml(compactIdLabel(detail.athlete_id)) })}
            </div>
          </article>
        `;
      }).join("")}
    </div>
  `;
}

function renderAnalyticsComparisonSelection() {
  const athletes = state.analyticsComparison.athletes.filter(Boolean);
  const selectionFull = athletes.length >= 2;
  const favoritesOpen = Boolean(state.currentUser && state.analyticsComparison.favoritesOpen);
  return `
    <div class="section-search-row analytics-comparison-search-row">
      <div class="analytics-comparison-search-primary">
        <form class="search-form section-search-form analytics-comparison-search-form" id="analyticsAthleteForm">
          <div class="search-input-shell">
            <input class="search-input" id="analyticsAthleteSearch" type="search" data-analytics-athlete-search autocomplete="off" placeholder="${escapeHtml(t("athleteSearchPlaceholder"))}" aria-label="${escapeHtml(t("athleteSearchPlaceholder"))}" ${selectionFull ? `disabled title="${escapeHtml(t("analyticsCompareSearchFull"))}"` : ""}>
            <button class="search-clear-button" type="button" data-search-clear-for="analyticsAthleteSearch" aria-label="${escapeHtml(t("clearSearch"))}" hidden><span aria-hidden="true">&times;</span></button>
          </div>
          <div class="search-suggestions analytics-comparison-suggestions" id="analyticsAthleteSuggestions" role="listbox" hidden></div>
        </form>
        ${state.currentUser ? `<button class="quiet-button section-favorite-filter analytics-favorites-toggle" type="button" data-analytics-favorites-toggle aria-pressed="${String(favoritesOpen)}" aria-expanded="${String(favoritesOpen)}">${escapeHtml(t("favoritesFilter"))}</button>` : ""}
      </div>
      ${state.currentUser ? `<div class="analytics-favorite-picker" id="analyticsFavoritePicker" ${favoritesOpen ? "" : "hidden"}>${favoritesOpen ? renderAnalyticsFavoriteAthletes() : ""}</div>` : ""}
    </div>
    ${athletes.length ? `<section class="analytics-comparison-selection"><div class="analytics-comparison-selected-list">${athletes.map(renderAnalyticsComparisonSelectedAthlete).join("")}</div></section>` : ""}
    <div id="analyticsComparisonMessage" class="auth-message analytics-comparison-message" role="status" aria-live="polite"></div>
  `;
}

function renderAnalyticsComparisonLayoutControl() {
  const overlay = state.analyticsComparison.layout === "overlay";
  return `
    <div class="athlete-analytics-control-group analytics-comparison-layout-group">
      <div class="segmented-control analytics-comparison-layout-control" role="radiogroup" aria-label="Analytics view" style="--segment-count: 2; --selected-index: ${overlay ? 1 : 0};">
        <button class="segmented-option" type="button" role="radio" data-analytics-comparison-layout="side-by-side" aria-checked="${String(!overlay)}">${escapeHtml(t("analyticsCompareSideBySide"))}</button>
        <button class="segmented-option" type="button" role="radio" data-analytics-comparison-layout="overlay" aria-checked="${String(overlay)}">${escapeHtml(t("analyticsCompareOverlay"))}</button>
        <span class="segmented-thumb analytics-comparison-layout-thumb" aria-hidden="true"></span>
      </div>
    </div>
  `;
}

function renderAnalyticsComparisonControls(data) {
  const comparison = state.analyticsComparison;
  const metricIndex = Math.max(0, ATHLETE_ANALYTICS_METRICS.findIndex((item) => item.value === comparison.metric));
  const modeIndex = comparison.mode === "snapshot" ? 1 : 0;
  const maxIndex = Math.max(0, data.timeline.length - 1);
  const startPercent = maxIndex ? (Math.max(0, data.range.startIndex) / maxIndex) * 100 : 0;
  const endPercent = maxIndex ? (Math.max(0, data.range.endIndex) / maxIndex) * 100 : 100;
  return `
    <div class="athlete-analytics-controls analytics-comparison-controls">
      <div class="athlete-analytics-filter-cluster analytics-comparison-filter-cluster ${data.athleteData.length > 1 ? "has-layout-control" : ""}">
        <div class="athlete-analytics-control-group athlete-analytics-apparatus-group">
          <div class="athlete-analytics-apparatus-buttons" role="group" aria-label="${escapeHtml(t("apparatus"))}">
            ${athleteAnalyticsApparatusOptions(data.discipline).map((apparatus) => `
              <button class="quiet-button athlete-analytics-apparatus-button ${data.selectedApparatuses.includes(apparatus) ? "is-active" : ""}" type="button" data-analytics-comparison-apparatus="${escapeHtml(apparatus)}" aria-pressed="${String(data.selectedApparatuses.includes(apparatus))}">${escapeHtml(apparatus)}</button>
            `).join("")}
          </div>
        </div>
        <div class="athlete-analytics-control-group athlete-analytics-score-group analytics-comparison-score-row">
          <div class="segmented-control athlete-analytics-metric-control" role="radiogroup" aria-label="${escapeHtml(t("analyticsMetric"))}" style="--segment-count: ${ATHLETE_ANALYTICS_METRICS.length}; --selected-index: ${metricIndex};">
            ${ATHLETE_ANALYTICS_METRICS.map((item) => `<button class="segmented-option athlete-analytics-metric-option" type="button" role="radio" data-analytics-comparison-metric="${escapeHtml(item.value)}" aria-checked="${String(comparison.metric === item.value)}">${escapeHtml(item.label)}</button>`).join("")}
            <span class="segmented-thumb athlete-analytics-metric-thumb" aria-hidden="true"></span>
          </div>
        </div>
        <div class="athlete-analytics-time-cluster analytics-comparison-time-cluster ${data.athleteData.length > 1 ? "has-layout-control" : ""}">
          ${data.athleteData.length > 1 ? renderAnalyticsComparisonLayoutControl() : ""}
          <div class="athlete-analytics-control-group athlete-analytics-mode-group">
            <div class="segmented-control athlete-analytics-mode-control" role="radiogroup" aria-label="${escapeHtml(t("analyticsMode"))}" style="--segment-count: 2; --selected-index: ${modeIndex};">
              <button class="segmented-option" type="button" role="radio" data-analytics-comparison-mode="period" aria-checked="${String(comparison.mode === "period")}">${escapeHtml(t("analyticsModePeriod"))}</button>
              <button class="segmented-option" type="button" role="radio" data-analytics-comparison-mode="snapshot" aria-checked="${String(comparison.mode === "snapshot")}">${escapeHtml(t("analyticsModeSnapshot"))}</button>
              <span class="segmented-thumb athlete-analytics-mode-thumb" aria-hidden="true"></span>
            </div>
          </div>
          <div class="athlete-analytics-timeline">
            <div class="athlete-analytics-range-shell ${comparison.mode === "snapshot" ? "is-snapshot" : ""}" style="--range-start: ${(comparison.mode === "snapshot" ? endPercent : startPercent).toFixed(2)}%; --range-end: ${endPercent.toFixed(2)}%;">
              <div class="athlete-analytics-range-track" aria-hidden="true"><span class="athlete-analytics-range-selected"></span></div>
              <div class="athlete-analytics-cycle-markers" aria-hidden="true">${renderAthleteAnalyticsTimelineCycleMarkers(data.timeline)}</div>
              <input id="analyticsComparisonStartTimeline" class="athlete-analytics-range-input athlete-analytics-range-start" type="range" min="0" max="${maxIndex}" step="1" value="${Math.max(0, data.range.startIndex)}" ${comparison.mode === "snapshot" || !data.timeline.length ? "disabled" : ""} aria-label="${escapeHtml(t("fromDate"))}">
              <input id="analyticsComparisonEndTimeline" class="athlete-analytics-range-input athlete-analytics-range-end" type="range" min="0" max="${maxIndex}" step="1" value="${Math.max(0, data.range.endIndex)}" ${!data.timeline.length ? "disabled" : ""} aria-label="${escapeHtml(comparison.mode === "snapshot" ? t("date") : t("toDate"))}">
            </div>
            <div class="athlete-analytics-range-values ${comparison.mode === "snapshot" ? "is-snapshot" : ""}" id="analyticsComparisonRangeValues">
              ${renderAthleteAnalyticsRangeValues(comparison.mode, data.range.startDate, data.range.endDate, data.athleteData.flatMap((item) => item.includedPoints))}
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function analyticsComparisonSeriesPoint(point, athleteName) {
  const events = (point.event_names || []).map((eventName) => `${athleteName} · ${eventName}`);
  return { ...point, event_names: events.length ? events : [athleteName] };
}

function renderAnalyticsComparisonTrendFigure(series, data) {
  const width = ATHLETE_TREND_SVG_WIDTH;
  const height = ATHLETE_TREND_SVG_HEIGHT;
  const padding = ATHLETE_TREND_SVG_PADDING;
  const { minValue, maxValue, valueRange } = data.trendValueDomain;
  const hasTrendData = series.some((item) => (
    state.analyticsComparison.mode === "snapshot" ? item.contextTrend : item.trend
  ).length);
  if (!hasTrendData || !data.dateDomain.maxTime) {
    return `<div class="empty-state compact-empty">${escapeHtml(t("analyticsNoData"))}</div>`;
  }
  return `
    <div class="athlete-trend-figure analytics-comparison-trend-figure ${state.analyticsComparison.mode === "snapshot" ? "is-snapshot" : ""}" data-comparison-trend="true">
      <svg class="athlete-trend-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(t("analyticsTrendTitle"))}">
        ${renderAthleteTrendAxes(data.dateDomain, padding, width, height, minValue, maxValue, state.analyticsComparison.metric)}
        ${series.map((item) => {
          const sourceTrend = state.analyticsComparison.mode === "snapshot" ? item.contextTrend : item.trend;
          const referenceDates = sourceTrend.map((point) => point.date);
          const coordinates = athleteAnalyticsSvgCoordinates(sourceTrend, referenceDates, padding, width, height, minValue, valueRange, data.dateDomain);
          const style = `style="--series-color: ${item.color};"`;
          const lineClass = `athlete-trend-line analytics-comparison-line ${state.analyticsComparison.mode === "snapshot" ? "is-context" : ""}`;
          const focusCoordinates = state.analyticsComparison.mode === "snapshot"
            ? athleteAnalyticsSvgCoordinates(item.trend, item.trend.map((point) => point.date), padding, width, height, minValue, valueRange, data.dateDomain)
            : coordinates;
          return `
            ${renderAthleteTrendPaths(coordinates, referenceDates, lineClass, style)}
            ${focusCoordinates.map((point) => renderAthleteTrendDot(
              analyticsComparisonSeriesPoint(point, athleteCardDisplayName(item.athlete)),
              state.analyticsComparison.metric,
              "athlete-trend-dot analytics-comparison-dot",
              state.analyticsComparison.mode === "snapshot" ? 5.2 : 4,
              style,
            )).join("")}
          `;
        }).join("")}
      </svg>
      <div class="athlete-trend-tooltip" role="status" hidden></div>
      <div class="athlete-trend-legend analytics-comparison-legend">
        ${series.map((item) => `<span class="is-primary" style="--series-color: ${item.color};">${escapeHtml(`${athleteCardDisplayName(item.athlete)} · ${athleteAnalyticsApparatusSelectionLabel(data.selectedApparatuses)} · ${athleteAnalyticsMetricLabel(state.analyticsComparison.metric)}`)}</span>`).join("")}
      </div>
    </div>
  `;
}

function renderAnalyticsComparisonRadarFigure(series, data) {
  const first = series[0];
  if (!first) return emptyState();
  const vertices = first.vertices;
  const radius = 106;
  const center = 150;
  const total = vertices.length;
  const hasApparatusFocus = data.selectedApparatuses.length > 0 && !data.selectedApparatuses.includes("AA");
  const scaleRatios = [0.25, 0.5, 0.75, 1];
  const rings = scaleRatios.map((ratio) => `<polygon class="athlete-radar-ring" points="${athleteAnalyticsSvgPolygon(vertices.map((_, index) => athleteAnalyticsPolarPoint(index, total, radius * ratio, center)))}"></polygon>`).join("");
  const axes = vertices.map((vertex, index) => {
    const end = athleteAnalyticsPolarPoint(index, total, radius, center);
    const label = athleteAnalyticsPolarPoint(index, total, radius + 24, center);
    const active = athleteAnalyticsVertexIsActive(vertex.apparatus, data.selectedApparatuses, data.discipline);
    return `<line class="athlete-radar-axis ${active ? "is-active" : "is-muted"}" x1="${center}" y1="${center}" x2="${end.x.toFixed(1)}" y2="${end.y.toFixed(1)}"></line><text class="athlete-radar-label ${active ? "is-active" : "is-muted"}" x="${label.x.toFixed(1)}" y="${label.y.toFixed(1)}">${escapeHtml(vertex.apparatus)}</text>`;
  }).join("");
  const scale = scaleRatios.map((ratio) => {
    const value = athleteAnalyticsLowerIsBetter(state.analyticsComparison.metric) ? data.radarMax * (1 - ratio) : data.radarMax * ratio;
    const y = center - (radius * ratio);
    return `<text class="athlete-radar-scale-label" x="${center + 10}" y="${(y + 3).toFixed(1)}">${escapeHtml(athleteAnalyticsRadarScaleLabel(value))}</text>`;
  }).join("");
  return `
    <div class="athlete-radar-figure analytics-comparison-radar-figure">
      <svg class="athlete-radar-svg" viewBox="0 0 300 300" role="img" aria-label="${escapeHtml(t("analyticsShapeTitle"))}">
        ${rings}${axes}<text class="athlete-radar-scale-label is-center" x="${center + 9}" y="${center + 3}">${escapeHtml(athleteAnalyticsRadarScaleLabel(athleteAnalyticsLowerIsBetter(state.analyticsComparison.metric) ? data.radarMax : 0))}</text>${scale}
        ${series.map((item) => {
          const points = item.vertices.map((vertex, index) => {
            const value = athleteAnalyticsNumber(vertex.value) || 0;
            const normalized = data.radarMax
              ? athleteAnalyticsLowerIsBetter(state.analyticsComparison.metric)
                ? Math.max(0, Math.min(1, 1 - (value / data.radarMax)))
                : Math.max(0, Math.min(1, value / data.radarMax))
              : 0;
            return athleteAnalyticsPolarPoint(index, total, radius * normalized, center);
          });
          const focusLines = hasApparatusFocus ? points.map((point, index) => {
            const vertex = item.vertices[index];
            if (!athleteAnalyticsVertexIsActive(vertex.apparatus, data.selectedApparatuses, data.discipline)) return "";
            return `<line class="athlete-radar-focus-line" style="--series-color: ${item.color};" x1="${center}" y1="${center}" x2="${point.x.toFixed(1)}" y2="${point.y.toFixed(1)}"></line>`;
          }).join("") : "";
          return `<polygon class="athlete-radar-area is-comparison ${hasApparatusFocus ? "is-muted" : ""}" style="--comparison-color: ${item.color};" points="${athleteAnalyticsSvgPolygon(points)}"></polygon>${focusLines}${points.map((point, index) => {
            const vertex = item.vertices[index];
            const active = athleteAnalyticsVertexIsActive(vertex.apparatus, data.selectedApparatuses, data.discipline);
            return `<circle class="athlete-radar-dot analytics-comparison-radar-dot ${active ? "is-active" : "is-muted"}" style="--series-color: ${item.color};" cx="${point.x.toFixed(1)}" cy="${point.y.toFixed(1)}" r="${active ? 4.6 : 3.5}" data-athlete-radar-point="true" data-radar-apparatus="${escapeHtml(`${athleteCardDisplayName(item.athlete)} · ${vertex.apparatus}`)}" data-radar-value="${escapeHtml(athleteAnalyticsFormatValue(vertex.value, state.analyticsComparison.metric))}" tabindex="0"></circle>`;
          }).join("")}`;
        }).join("")}
      </svg>
      <div class="athlete-radar-tooltip" role="status" hidden></div>
      <div class="athlete-trend-legend analytics-comparison-legend">${series.map((item) => `<span class="is-primary" style="--series-color: ${item.color};">${escapeHtml(`${athleteCardDisplayName(item.athlete)} · ${athleteAnalyticsApparatusSelectionLabel(data.selectedApparatuses)} ${athleteAnalyticsFormatValue(item.summary.average, state.analyticsComparison.metric)}`)}</span>`).join("")}</div>
    </div>
  `;
}

function renderAnalyticsComparisonSummary(item) {
  return `
    <div class="analytics-comparison-summary" style="--athlete-color: ${item.color};">
      <strong>${escapeHtml(athleteCardDisplayName(item.athlete))}</strong>
      <span>${escapeHtml(item.athlete.country || t("notAvailable"))}</span>
      ${renderAthleteAnalyticsSummaryGrid({ metric: state.analyticsComparison.metric, summary: item.summary })}
    </div>
  `;
}

function renderAnalyticsComparisonChartHeader(titleKey, athlete = null) {
  return `
    <div class="section-header compact-section-header">
      <div>
        <h2>${escapeHtml(t(titleKey))}</h2>
        ${athlete ? `<p>${escapeHtml(athleteCardDisplayName(athlete))}</p>` : ""}
      </div>
    </div>
  `;
}

function renderAnalyticsComparisonContent(data) {
  const overlay = state.analyticsComparison.layout === "overlay";
  const cycleContext = renderAthleteAnalyticsScoringCycleContext(data.cycles, data.discipline);
  const warningMessages = [
    state.analyticsComparison.metric === "execution_estimate" ? t("analyticsEEstimateNotice") : "",
    ...data.athleteData.flatMap((item) => item.warnings),
  ];
  const warningStack = renderDataWarningStack(warningMessages, "athlete-analytics-warning-stack");
  if (data.athleteData.length === 1) {
    const item = data.athleteData[0];
    return `
      ${cycleContext}
      <div class="athlete-analytics-visual-grid analytics-comparison-single-grid">
        <div class="athlete-analytics-chart-block athlete-shape-chart-block analytics-comparison-athlete-chart" style="--athlete-color: ${item.color};">${renderAnalyticsComparisonChartHeader("analyticsShapeTitle", item.athlete)}${renderAnalyticsComparisonRadarFigure([item], data)}</div>
        <div class="athlete-analytics-chart-block athlete-trend-chart-block analytics-comparison-athlete-chart" style="--athlete-color: ${item.color};">${renderAnalyticsComparisonChartHeader("analyticsTrendTitle", item.athlete)}${renderAnalyticsComparisonTrendFigure([item], data)}</div>
      </div>
      ${renderAthleteAnalyticsSummaryGrid({ metric: state.analyticsComparison.metric, summary: item.summary })}
      ${warningStack}
    `;
  }
  if (overlay) {
    return `
      ${cycleContext}
      <div class="athlete-analytics-visual-grid analytics-comparison-overlay-grid">
        <div class="athlete-analytics-chart-block athlete-shape-chart-block">${renderAnalyticsComparisonChartHeader("analyticsShapeTitle")}${renderAnalyticsComparisonRadarFigure(data.athleteData, data)}</div>
        <div class="athlete-analytics-chart-block athlete-trend-chart-block">${renderAnalyticsComparisonChartHeader("analyticsTrendTitle")}${renderAnalyticsComparisonTrendFigure(data.athleteData, data)}</div>
      </div>
      <div class="analytics-comparison-summary-grid">${data.athleteData.map(renderAnalyticsComparisonSummary).join("")}</div>
      ${warningStack}
    `;
  }
  return `
    ${cycleContext}
    <div class="analytics-comparison-chart-row">
      ${data.athleteData.map((item) => `<div class="athlete-analytics-chart-block athlete-shape-chart-block analytics-comparison-athlete-chart" style="--athlete-color: ${item.color};">${renderAnalyticsComparisonChartHeader("analyticsShapeTitle", item.athlete)}${renderAnalyticsComparisonRadarFigure([item], data)}</div>`).join("")}
    </div>
    <div class="analytics-comparison-chart-row">
      ${data.athleteData.map((item) => `<div class="athlete-analytics-chart-block athlete-trend-chart-block analytics-comparison-athlete-chart" style="--athlete-color: ${item.color};">${renderAnalyticsComparisonChartHeader("analyticsTrendTitle", item.athlete)}${renderAnalyticsComparisonTrendFigure([item], data)}</div>`).join("")}
    </div>
    <div class="analytics-comparison-summary-grid">${data.athleteData.map(renderAnalyticsComparisonSummary).join("")}</div>
    ${warningStack}
  `;
}

function updateAnalyticsComparisonContent({ animate = false } = {}) {
  const content = $("#analyticsComparisonContent");
  if (!content || !state.analyticsComparison.payloads.some(Boolean)) return;
  const data = analyticsComparisonPreparedData();
  content.innerHTML = renderAnalyticsComparisonContent(data);
  if (animate && !window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches) {
    content.classList.remove("is-metric-transition");
    void content.offsetWidth;
    content.classList.add("is-metric-transition");
  }
}

function syncAnalyticsComparisonTimeline({ animate = false } = {}) {
  const data = analyticsComparisonPreparedData();
  const maxIndex = Math.max(0, data.timeline.length - 1);
  const startInput = $("#analyticsComparisonStartTimeline");
  const endInput = $("#analyticsComparisonEndTimeline");
  const shell = document.querySelector(".analytics-comparison-controls .athlete-analytics-range-shell");
  const snapshotMode = state.analyticsComparison.mode === "snapshot";
  if (startInput) {
    startInput.max = String(maxIndex);
    startInput.value = String(Math.max(0, data.range.startIndex));
    startInput.disabled = snapshotMode || !data.timeline.length;
  }
  if (endInput) {
    endInput.max = String(maxIndex);
    endInput.value = String(Math.max(0, data.range.endIndex));
    endInput.disabled = !data.timeline.length;
  }
  if (shell) {
    const startPercent = maxIndex ? (Math.max(0, data.range.startIndex) / maxIndex) * 100 : 0;
    const endPercent = maxIndex ? (Math.max(0, data.range.endIndex) / maxIndex) * 100 : 100;
    shell.style.setProperty("--range-start", `${(snapshotMode ? endPercent : startPercent).toFixed(2)}%`);
    shell.style.setProperty("--range-end", `${endPercent.toFixed(2)}%`);
    shell.classList.toggle("is-snapshot", snapshotMode);
  }
  const rangeValues = $("#analyticsComparisonRangeValues");
  if (rangeValues) {
    rangeValues.classList.toggle("is-snapshot", snapshotMode);
    rangeValues.innerHTML = renderAthleteAnalyticsRangeValues(state.analyticsComparison.mode, data.range.startDate, data.range.endDate, data.athleteData.flatMap((item) => item.includedPoints));
  }
  updateAnalyticsComparisonContent({ animate });
}

function syncAnalyticsComparisonApparatusControl() {
  const selected = new Set(analyticsComparisonSelectedApparatuses());
  document.querySelectorAll("[data-analytics-comparison-apparatus]").forEach((button) => {
    const active = selected.has(button.dataset.analyticsComparisonApparatus);
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  });
}

function syncAnalyticsComparisonMetricControl() {
  const metric = state.analyticsComparison.metric;
  const selectedIndex = Math.max(0, ATHLETE_ANALYTICS_METRICS.findIndex((item) => item.value === metric));
  document.querySelectorAll("[data-analytics-comparison-metric]").forEach((button) => {
    button.setAttribute("aria-checked", String(button.dataset.analyticsComparisonMetric === metric));
  });
  document.querySelector(".analytics-comparison-controls .athlete-analytics-metric-control")
    ?.style.setProperty("--selected-index", selectedIndex);
}

function syncAnalyticsComparisonModeControl() {
  const mode = state.analyticsComparison.mode;
  document.querySelectorAll("[data-analytics-comparison-mode]").forEach((button) => {
    button.setAttribute("aria-checked", String(button.dataset.analyticsComparisonMode === mode));
  });
  document.querySelector(".analytics-comparison-controls .athlete-analytics-mode-control")
    ?.style.setProperty("--selected-index", mode === "snapshot" ? 1 : 0);
}

function syncAnalyticsComparisonLayoutControl() {
  const layout = state.analyticsComparison.layout;
  document.querySelectorAll("[data-analytics-comparison-layout]").forEach((button) => {
    button.setAttribute("aria-checked", String(button.dataset.analyticsComparisonLayout === layout));
  });
  document.querySelector(".analytics-comparison-layout-control")
    ?.style.setProperty("--selected-index", layout === "overlay" ? 1 : 0);
}

function bindAnalyticsComparisonControls() {
  document.querySelectorAll("[data-analytics-comparison-apparatus]").forEach((button) => {
    button.addEventListener("click", () => {
      state.analyticsComparison.apparatuses = toggleExclusiveApparatusSelection(
        analyticsComparisonSelectedApparatuses(),
        button.dataset.analyticsComparisonApparatus,
      );
      syncAnalyticsComparisonApparatusControl();
      updateAnalyticsComparisonContent({ animate: true });
    });
  });
  document.querySelectorAll("[data-analytics-comparison-metric]").forEach((button) => {
    button.addEventListener("click", () => {
      if (state.analyticsComparison.metric === button.dataset.analyticsComparisonMetric) return;
      state.analyticsComparison.metric = button.dataset.analyticsComparisonMetric;
      syncAnalyticsComparisonMetricControl();
      updateAnalyticsComparisonContent({ animate: true });
    });
  });
  document.querySelectorAll("[data-analytics-comparison-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      const mode = button.dataset.analyticsComparisonMode === "snapshot" ? "snapshot" : "period";
      if (state.analyticsComparison.mode === mode) return;
      state.analyticsComparison.mode = mode;
      syncAnalyticsComparisonModeControl();
      syncAnalyticsComparisonTimeline({ animate: true });
    });
  });
  document.querySelectorAll("[data-analytics-comparison-layout]").forEach((button) => {
    button.addEventListener("click", () => {
      state.analyticsComparison.layout = button.dataset.analyticsComparisonLayout === "overlay" ? "overlay" : "side-by-side";
      syncAnalyticsComparisonLayoutControl();
      updateAnalyticsComparisonContent({ animate: true });
    });
  });
  const bindRange = (input, field) => {
    input?.addEventListener("input", () => {
      const value = Number(input.value);
      if (state.analyticsComparison.mode === "snapshot") {
        state.analyticsComparison.snapshotIndex = value;
      } else if (field === "start") {
        state.analyticsComparison.startIndex = Math.min(value, Number(state.analyticsComparison.endIndex));
      } else {
        state.analyticsComparison.endIndex = Math.max(value, Number(state.analyticsComparison.startIndex));
      }
      syncAnalyticsComparisonTimeline();
    });
  };
  bindRange($("#analyticsComparisonStartTimeline"), "start");
  bindRange($("#analyticsComparisonEndTimeline"), "end");
}

function renderAnalyticsComparisonWorkspace({ animate = false } = {}) {
  const workspace = $("#analyticsComparisonWorkspace");
  if (!workspace) return;
  if (!state.analyticsComparison.payloads.some(Boolean)) {
    workspace.innerHTML = "";
    return;
  }
  const data = analyticsComparisonPreparedData();
  workspace.innerHTML = `
    <section class="athlete-analytics-panel analytics-comparison-panel">
      <div class="athlete-analytics-sticky-menu">${renderAnalyticsComparisonControls(data)}</div>
      <div id="analyticsComparisonContent" class="athlete-analytics-dynamic-content">${renderAnalyticsComparisonContent(data)}</div>
    </section>
  `;
  bindAnalyticsComparisonControls();
  if (animate) updateAnalyticsComparisonContent({ animate: true });
}

function analyticsComparisonSuggestionName(athlete) {
  return athleteCardDisplayName(athlete, `${t("athlete")} ${athlete.id}`);
}

function renderAnalyticsComparisonSuggestions(athletes) {
  const container = $("#analyticsAthleteSuggestions");
  if (!container) return;
  if (!athletes.length) {
    container.innerHTML = `<div class="search-suggestion search-suggestion-status">${escapeHtml(t("analyticsCompareNoSuggestions"))}</div>`;
  } else {
    container.innerHTML = athletes.map((athlete) => `
      <button type="button" class="analytics-comparison-suggestion search-suggestion" role="option" data-analytics-athlete-choice data-athlete-id="${athlete.id}">
        <strong>${escapeHtml(analyticsComparisonSuggestionName(athlete))}</strong>
        <span>${escapeHtml([athlete.country, athlete.discipline, `ID ${athlete.id}`].filter(Boolean).join(" · "))}</span>
      </button>
    `).join("");
  }
  container.hidden = false;
  setSearchSuggestionsOpen(container, true, Math.max(1, athletes.length));
  setSearchSuggestionsBusy(container, false);
  container.querySelectorAll("[data-analytics-athlete-choice]").forEach((button) => {
    button.addEventListener("click", () => selectAnalyticsComparisonAthlete(Number(button.dataset.athleteId)));
  });
}

async function searchAnalyticsComparisonAthletes(query) {
  const container = $("#analyticsAthleteSuggestions");
  if (!container) return;
  const requestId = ++analyticsComparisonSearchRequestId;
  if (!query.trim()) {
    container.hidden = true;
    container.innerHTML = "";
    setSearchSuggestionsOpen(container, false);
    setSearchSuggestionsBusy(container, false);
    return;
  }
  const hadStableSuggestions = !container.hidden && Boolean(container.querySelector("[data-analytics-athlete-choice]"));
  if (container.hidden || !container.childElementCount) {
    container.innerHTML = `<div class="search-suggestion search-suggestion-status">${escapeHtml(t("loading"))}</div>`;
    container.hidden = false;
    setSearchSuggestionsOpen(container, true, 1);
  }
  setSearchSuggestionsBusy(container, true);
  try {
    const discipline = state.analyticsComparison.athletes.find(Boolean)?.discipline || "";
    const athletes = await getJson("/athletes/", { search: query.trim(), discipline, limit: 9, offset: 0 });
    if (requestId !== analyticsComparisonSearchRequestId) return;
    const selectedIds = new Set(state.analyticsComparison.athletes.filter(Boolean).map((athlete) => Number(athlete.id)));
    renderAnalyticsComparisonSuggestions(athletes.filter((athlete) => !selectedIds.has(Number(athlete.id))).slice(0, 8));
  } catch (error) {
    if (requestId !== analyticsComparisonSearchRequestId) return;
    setSearchSuggestionsBusy(container, false);
    if (!hadStableSuggestions) {
      container.innerHTML = `<div class="search-suggestion search-suggestion-status">${escapeHtml(error.message || t("loadFailed"))}</div>`;
      container.hidden = false;
      setSearchSuggestionsOpen(container, true, 1);
    }
  }
}

function refreshAnalyticsFavoritePicker() {
  const picker = $("#analyticsFavoritePicker");
  const toggle = document.querySelector("[data-analytics-favorites-toggle]");
  if (!picker || !toggle) return;
  const isOpen = Boolean(state.analyticsComparison.favoritesOpen);
  picker.hidden = !isOpen;
  picker.innerHTML = isOpen ? renderAnalyticsFavoriteAthletes() : "";
  toggle.setAttribute("aria-pressed", String(isOpen));
  toggle.setAttribute("aria-expanded", String(isOpen));
  bindAnalyticsFavoriteAthleteCards(picker);
}

function bindAnalyticsFavoriteAthleteCards(root = document) {
  root.querySelectorAll("[data-analytics-favorite-athlete-id]").forEach((card) => {
    const selectAthlete = () => selectAnalyticsComparisonAthlete(Number(card.dataset.analyticsFavoriteAthleteId));
    card.addEventListener("click", selectAthlete);
    card.addEventListener("keydown", (event) => {
      if (!["Enter", " "].includes(event.key)) return;
      event.preventDefault();
      selectAthlete();
    });
  });
}

async function loadAnalyticsFavoriteAthletes() {
  const comparison = state.analyticsComparison;
  comparison.favoritesLoading = true;
  comparison.favoritesError = "";
  refreshAnalyticsFavoritePicker();
  try {
    const details = await getJson("/preferences/athletes/followed/details", {}, { auth: true });
    comparison.favoriteDetails = details;
    state.favoriteAthleteIds = new Set(details.map((item) => Number(item.athlete_id)));
    state.favoritesLoaded = true;
  } catch (_error) {
    comparison.favoriteDetails = [];
    comparison.favoritesError = "load_failed";
  } finally {
    comparison.favoritesLoading = false;
    refreshAnalyticsFavoritePicker();
  }
}

async function selectAnalyticsComparisonAthlete(athleteId) {
  const message = $("#analyticsComparisonMessage");
  const selectedAthletes = state.analyticsComparison.athletes.filter(Boolean);
  if (selectedAthletes.some((athlete) => Number(athlete.id) === athleteId)) {
    if (message) message.textContent = t("analyticsCompareSameAthlete");
    return;
  }
  if (selectedAthletes.length >= 2) return;
  const requestId = ++analyticsComparisonProfileRequestId;
  if (message) message.textContent = t("loading");
  try {
    const payload = await getJson(`/analytics/athletes/${athleteId}/profile-view`, { metric: "score", criterion: "average" });
    if (requestId !== analyticsComparisonProfileRequestId) return;
    const athlete = payload.athlete;
    const firstAthlete = selectedAthletes[0];
    if (firstAthlete && firstAthlete.discipline !== athlete.discipline) {
      if (message) message.textContent = t("analyticsCompareSameDiscipline");
      return;
    }
    const slot = selectedAthletes.length;
    state.analyticsComparison.athletes[slot] = athlete;
    state.analyticsComparison.payloads[slot] = payload;
    state.analyticsComparison.startIndex = -1;
    state.analyticsComparison.endIndex = -1;
    state.analyticsComparison.snapshotIndex = -1;
    state.analyticsComparison.apparatuses = ["AA"];
    if (slot === 1) state.analyticsComparison.favoritesOpen = false;
    renderAnalyticsComparison();
  } catch (error) {
    if (requestId !== analyticsComparisonProfileRequestId) return;
    if (message) message.textContent = error.message || t("loadFailed");
  }
}

function bindAnalyticsComparisonPickers() {
  bindSearchClearButtons();
  const form = $("#analyticsAthleteForm");
  form?.addEventListener("click", (event) => event.stopPropagation());
  form?.addEventListener("submit", (event) => {
    event.preventDefault();
    $("#analyticsAthleteSuggestions")?.querySelector("[data-analytics-athlete-choice]")?.click();
  });
  document.querySelectorAll("[data-analytics-athlete-search]").forEach((input) => {
    let timer;
    input.addEventListener("input", () => {
      window.clearTimeout(timer);
      analyticsComparisonSearchRequestId += 1;
      timer = window.setTimeout(() => searchAnalyticsComparisonAthletes(input.value), 140);
    });
    input.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeSearchSuggestions();
        input.blur();
      }
    });
    input.addEventListener("focus", () => searchAnalyticsComparisonAthletes(input.value));
    input.addEventListener("blur", () => {
      window.setTimeout(() => {
        const suggestions = $("#analyticsAthleteSuggestions");
        if (suggestions) {
          suggestions.hidden = true;
          setSearchSuggestionsOpen(suggestions, false);
        }
      }, 160);
    });
  });
  document.querySelectorAll("[data-analytics-remove-athlete]").forEach((button) => {
    button.addEventListener("click", () => {
      const slot = Number(button.dataset.analyticsRemoveAthlete);
      state.analyticsComparison.athletes.splice(slot, 1);
      state.analyticsComparison.payloads.splice(slot, 1);
      state.analyticsComparison.athletes = [...state.analyticsComparison.athletes.filter(Boolean), null, null].slice(0, 2);
      state.analyticsComparison.payloads = [...state.analyticsComparison.payloads.filter(Boolean), null, null].slice(0, 2);
      state.analyticsComparison.startIndex = -1;
      state.analyticsComparison.endIndex = -1;
      state.analyticsComparison.snapshotIndex = -1;
      renderAnalyticsComparison();
    });
  });
  document.querySelector("[data-analytics-favorites-toggle]")?.addEventListener("click", () => {
    const comparison = state.analyticsComparison;
    comparison.favoritesOpen = !comparison.favoritesOpen;
    closeSearchSuggestions();
    refreshAnalyticsFavoritePicker();
    if (comparison.favoritesOpen && !comparison.favoritesLoading) loadAnalyticsFavoriteAthletes();
  });
  bindAnalyticsFavoriteAthleteCards();
}

function renderAnalyticsComparison() {
  setApp(`
    ${pageHeading("analyticsHeading", "analyticsIntro")}
    ${renderAnalyticsComparisonSelection()}
    <div id="analyticsComparisonWorkspace"></div>
  `);
  bindAnalyticsComparisonPickers();
  renderAnalyticsComparisonWorkspace();
}

function renderAdminSelectControl(name, label, value, options) {
  const normalizedOptions = options.map((option) => (
    typeof option === "string" ? { value: option, label: option } : option
  ));
  const selectedOption = normalizedOptions.find((option) => option.value === value) || normalizedOptions[0];
  return `
    <div class="admin-form-field admin-custom-select-field">
      <span>${escapeHtml(label)}</span>
      <details class="admin-custom-select" data-admin-select>
        <summary aria-haspopup="listbox" aria-label="${escapeHtml(label)}">
          <span data-admin-select-label>${escapeHtml(selectedOption?.label || "")}</span>
          <span class="admin-select-caret" aria-hidden="true"></span>
        </summary>
        <div class="admin-custom-select-menu" role="listbox" aria-label="${escapeHtml(label)}">
          ${normalizedOptions.map((option) => `
            <button
              type="button"
              role="option"
              aria-selected="${option.value === selectedOption?.value}"
              data-admin-select-value="${escapeHtml(option.value)}"
            >${escapeHtml(option.label)}</button>
          `).join("")}
        </div>
        <input type="hidden" name="${escapeHtml(name)}" value="${escapeHtml(selectedOption?.value || "")}" data-admin-select-input>
      </details>
    </div>
  `;
}

function closeAdminSelectControls(except = null) {
  document.querySelectorAll("[data-admin-select][open]").forEach((control) => {
    if (control !== except) control.removeAttribute("open");
  });
}

function bindAdminSelectControls(rootNode = document) {
  rootNode.querySelectorAll("[data-admin-select]").forEach((control) => {
    if (control.dataset.adminSelectBound === "true") return;
    control.dataset.adminSelectBound = "true";
    control.addEventListener("toggle", () => {
      if (control.open) closeAdminSelectControls(control);
    });
    control.querySelectorAll("[data-admin-select-value]").forEach((option) => {
      option.addEventListener("click", () => {
        const value = option.dataset.adminSelectValue || "";
        const input = control.querySelector("[data-admin-select-input]");
        const label = control.querySelector("[data-admin-select-label]");
        if (input) input.value = value;
        if (label) label.textContent = option.textContent.trim();
        control.querySelectorAll("[role='option']").forEach((item) => {
          item.setAttribute("aria-selected", String(item === option));
        });
        control.removeAttribute("open");
      });
    });
  });
  if (document.documentElement.dataset.adminSelectOutsideBound === "true") return;
  document.documentElement.dataset.adminSelectOutsideBound = "true";
  document.addEventListener("pointerdown", (event) => {
    if (!event.target.closest("[data-admin-select]")) closeAdminSelectControls();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeAdminSelectControls();
  });
}

function syncAdminFormValue(form, name, value) {
  const input = form?.elements?.namedItem(name);
  if (!input) return;
  input.value = value ?? "";
  const control = input.closest("[data-admin-select]");
  if (!control) return;
  const selected = [...control.querySelectorAll("[data-admin-select-value]")]
    .find((option) => option.dataset.adminSelectValue === String(input.value));
  if (!selected) return;
  const label = control.querySelector("[data-admin-select-label]");
  if (label) label.textContent = selected.textContent.trim();
  control.querySelectorAll("[role='option']").forEach((option) => {
    option.setAttribute("aria-selected", String(option === selected));
  });
}

function updateAthleteProfileSummary(athlete) {
  const panel = $("#athleteProfileSummary");
  if (!panel || !athlete) return;
  const currentImage = panel.querySelector(".athlete-profile-image");
  if (currentImage) currentImage.outerHTML = renderAthleteProfileImage(athlete);
  const title = panel.querySelector(".athlete-profile-title-copy h2");
  if (title) title.textContent = athleteProfileDisplayName(athlete);
  const verification = panel.querySelector(".athlete-profile-verification");
  if (verification) verification.innerHTML = renderAthleteVerificationBadge(athlete);
  const meta = panel.querySelector(".athlete-profile-title-copy .meta");
  if (meta) meta.textContent = [athlete.country, athlete.discipline].filter(Boolean).join(" · ");
  const identity = panel.querySelector(".athlete-identity-panel");
  if (identity) identity.outerHTML = renderAthleteIdentityPanel(athlete, { embedded: true, showHeader: true });
}

function syncAthleteAdminForm(athlete) {
  const form = $("#athleteAdminForm");
  if (!form || !athlete) return;
  ["last_name", "first_name", "birth_year", "country", "discipline", "image_url"].forEach((name) => {
    syncAdminFormValue(form, name, athlete[name]);
  });
  syncAdminFormValue(form, "country_change_year", "");
}

function syncAthleteVerificationControl(athlete) {
  const button = $("#athleteVerificationToggle");
  if (!button || !athlete) return;
  const isVerified = Boolean(athlete.is_profile_verified);
  button.classList.toggle("is-active", isVerified);
  button.setAttribute("aria-pressed", String(isVerified));
  button.textContent = t(isVerified ? "removeVerificationBadge" : "assignVerificationBadge");
}

async function refreshAthleteAdminState(athleteId, options = {}) {
  const {
    refreshProfile = true,
    refreshForm = true,
    refreshSuggestions = true,
    refreshAnalytics = false,
  } = options;
  const adminView = await getJson(`/athletes/${athleteId}/admin-view`, {}, { auth: true });
  const athlete = adminView.athlete;
  if (refreshProfile) updateAthleteProfileSummary(athlete);
  if (refreshForm) syncAthleteAdminForm(athlete);
  syncAthleteVerificationControl(athlete);
  if (refreshSuggestions) {
    const host = $("#athleteSuggestionList");
    if (host) {
      host.innerHTML = renderAthleteSuggestions(adminView.pending_suggestions || []);
      bindAthleteSuggestionActions(athleteId);
    }
  }
  if (refreshAnalytics) await loadAthleteAnalytics(athleteId, { preserveControls: true });
  return athlete;
}

function renderAthleteAdminForm(athlete) {
  return `
    <form class="admin-edit-form" id="athleteAdminForm">
      <div class="section-header compact-section-header">
        <div>
          <h2>${t("editAthlete")}</h2>
        </div>
        <div class="admin-form-header-actions">
          <button
            class="quiet-button athlete-verification-toggle ${athlete.is_profile_verified ? "is-active" : ""}"
            id="athleteVerificationToggle"
            type="button"
            aria-pressed="${Boolean(athlete.is_profile_verified)}"
          >${t(athlete.is_profile_verified ? "removeVerificationBadge" : "assignVerificationBadge")}</button>
          <button class="quiet-button" type="submit">${t("saveChanges")}</button>
        </div>
      </div>
      <div class="admin-form-grid">
        <label>
          <span>${t("lastName")}</span>
          <input name="last_name" value="${escapeHtml(athlete.last_name || "")}" required>
        </label>
        <label>
          <span>${t("firstName")}</span>
          <input name="first_name" value="${escapeHtml(athlete.first_name || "")}" required>
        </label>
        <label>
          <span>${t("birthYear")}</span>
          <input name="birth_year" type="number" min="1900" max="2100" value="${escapeHtml(athlete.birth_year || "")}">
        </label>
        <label>
          <span>${t("country")}</span>
          <input name="country" maxlength="3" value="${escapeHtml(athlete.country || "")}">
        </label>
        <label>
          <span>${t("countryChangeYear")}</span>
          <input name="country_change_year" type="number" min="1900" max="2100">
        </label>
        ${renderAdminSelectControl("discipline", t("discipline"), athlete.discipline, ["MAG", "WAG"])}
        <label class="admin-form-wide">
          <span>${t("imageUrl")}</span>
          <input name="image_url" value="${escapeHtml(athlete.image_url || "")}">
        </label>
      </div>
      <span class="auth-message" id="athleteAdminMessage" role="status" aria-live="polite"></span>
    </form>
  `;
}

function renderAthleteSuggestions(suggestions = []) {
  if (!suggestions.length) return emptyMessage(t("noPendingSuggestions"));
  return `
    <div class="admin-review-list">
      ${suggestions.map((suggestion) => `
        <article class="admin-review-row" data-athlete-suggestion-row="${suggestion.id}">
          <div class="admin-review-copy">
            <span>${escapeHtml(suggestion.field_name)}</span>
            <strong>${escapeHtml(displayValue(suggestion.suggested_value))}</strong>
            ${suggestion.evidence ? `<p>${escapeHtml(suggestion.evidence)}</p>` : ""}
            ${suggestion.source_url ? `<a href="${escapeHtml(suggestion.source_url)}" target="_blank" rel="noreferrer">${escapeHtml(suggestion.source_title || suggestion.source_url)}</a>` : ""}
          </div>
          <div class="admin-review-actions">
            <label>
              <span>${t("suggestedValue")}</span>
              <input data-athlete-suggestion-value="${suggestion.id}" value="${escapeHtml(suggestion.suggested_value || "")}">
            </label>
            <div>
              <button class="quiet-button admin-accept-button" type="button" data-athlete-suggestion-accept="${suggestion.id}">${t("accept")}</button>
              <button class="quiet-button filter-clear-button" type="button" data-athlete-suggestion-reject="${suggestion.id}">${t("reject")}</button>
            </div>
          </div>
        </article>
      `).join("")}
    </div>
  `;
}

function renderWorldGymnasticsCandidateList(response) {
  const warnings = (response.warnings || []).map(localizedWorldGymnasticsWarning);
  const candidates = response.candidates || [];
  if (!candidates.length) {
    return `
      ${warnings.map((warning) => `<div class="context-note"><span>${escapeHtml(warning.type)}</span>${escapeHtml(warning.message)}</div>`).join("")}
      ${emptyMessage(t("noWorldGymnasticsCandidates"))}
    `;
  }
  return `
    <div class="admin-review-list">
      ${candidates.map((candidate) => {
        const name = [candidate.last_name, candidate.first_name].filter(Boolean).join(" ");
        const meta = [candidate.country, candidate.discipline, candidate.status].filter(Boolean).join(" · ");
        return `
          <article class="admin-review-row">
            <div class="admin-review-copy">
              <span>FIG ID ${escapeHtml(candidate.fig_id)}</span>
              <strong>${escapeHtml(name)}</strong>
              <p>${escapeHtml(meta || t("notAvailable"))}</p>
              <a href="${escapeHtml(candidate.profile_url)}" target="_blank" rel="noreferrer">${t("openWorldGymnastics")}</a>
            </div>
            <div class="admin-review-actions admin-candidate-actions">
              <span>${Math.round(Number(candidate.match_score || 0) * 100)}%</span>
              <button class="quiet-button" type="button" data-athlete-wg-use-profile="${escapeHtml(candidate.fig_id)}">${t("useProfile")}</button>
            </div>
          </article>
        `;
      }).join("")}
    </div>
  `;
}

function renderAthleteWorldGymnasticsAdminTools() {
  return `
    <div class="admin-tool-block">
      <div class="section-header compact-section-header">
        <div>
          <h2>${t("worldGymnasticsAssistant")}</h2>
        </div>
        <button class="quiet-button admin-world-gymnastics-search-button" type="button" id="findAthleteWorldGymnasticsCandidates">${t("findProfile")}</button>
      </div>
      <form class="admin-inline-form" id="athleteWorldGymnasticsManualForm">
        <input id="athleteWorldGymnasticsSource" placeholder="${escapeHtml(t("figIdOrUrl"))}">
        <button class="quiet-button admin-world-gymnastics-search-button" type="submit">${t("generateFromProfile")}</button>
      </form>
      <div class="admin-tool-output" id="athleteWorldGymnasticsOutput"></div>
    </div>
  `;
}

function renderAthleteAdminPanel(athlete, adminView, adminViewError = null) {
  if (!isAdminUser()) return "";
  const suggestions = adminView?.pending_suggestions || [];
  return `
    <section class="panel athlete-admin-panel detail-admin-panel" id="athleteAdminPanel" data-admin-tools-panel hidden>
      <div class="section-header compact-section-header">
        <div>
          <p class="eyebrow">ADMIN</p>
          <h2>${t("adminAthleteTools")}</h2>
        </div>
      </div>
      ${renderAthleteAdminForm(athlete)}
      ${renderAthleteWorldGymnasticsAdminTools()}
      <div class="admin-tool-block">
        <div class="section-header compact-section-header">
          <div>
            <h2>${t("adminSuggestions")}</h2>
          </div>
        </div>
        <div id="athleteSuggestionMessage" class="auth-message" role="status" aria-live="polite"></div>
        <div id="athleteSuggestionList">
          ${adminViewError ? errorState(adminViewError) : renderAthleteSuggestions(suggestions)}
        </div>
      </div>
    </section>
  `;
}

function bindAthleteAdminForm(athleteId) {
  const form = $("#athleteAdminForm");
  if (!form) return;
  bindAdminSelectControls(form);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = $("#athleteAdminMessage");
    const submit = form.querySelector("button[type='submit']");
    const formData = new FormData(form);
    const birthYear = String(formData.get("birth_year") || "").trim();
    const countryChangeYear = String(formData.get("country_change_year") || "").trim();
    const payload = {
      first_name: String(formData.get("first_name") || "").trim(),
      last_name: String(formData.get("last_name") || "").trim(),
      birth_year: birthYear ? Number(birthYear) : null,
      country: String(formData.get("country") || "").trim().toUpperCase() || null,
      discipline: String(formData.get("discipline") || "").trim(),
      image_url: String(formData.get("image_url") || "").trim() || null,
    };
    if (countryChangeYear) payload.country_change_year = Number(countryChangeYear);
    message.textContent = "";
    submit.disabled = true;
    try {
      await sendJson(`/athletes/${athleteId}`, { method: "PUT", body: payload });
      await refreshAthleteAdminState(athleteId, { refreshAnalytics: true });
      message.textContent = t("updateSaved");
    } catch (_error) {
      message.textContent = t("updateError");
    } finally {
      submit.disabled = false;
    }
  });
  const verificationButton = $("#athleteVerificationToggle");
  verificationButton?.addEventListener("click", async () => {
    const message = $("#athleteAdminMessage");
    const shouldVerify = verificationButton.getAttribute("aria-pressed") !== "true";
    verificationButton.disabled = true;
    if (message) setAdminSuggestionFeedback(message, "", null);
    try {
      const athlete = await sendJson(`/athletes/${athleteId}`, {
        method: "PUT",
        body: { is_profile_verified: shouldVerify },
      });
      updateAthleteProfileSummary(athlete);
      syncAthleteVerificationControl(athlete);
      if (message) {
        setAdminSuggestionFeedback(
          message,
          t(shouldVerify ? "verificationBadgeAssigned" : "verificationBadgeRemoved"),
          "success",
        );
      }
    } catch (_error) {
      if (message) setAdminSuggestionFeedback(message, t("verificationBadgeError"), "danger");
    } finally {
      verificationButton.disabled = false;
    }
  });
}

async function createWorldGymnasticsAthleteSuggestions(athleteId, payload, outputNode = null) {
  const output = outputNode || $("#athleteWorldGymnasticsOutput");
  if (output) output.innerHTML = loadingState();
  try {
    const response = await sendJson(`/world-gymnastics/athletes/${athleteId}/suggestions`, { body: payload });
    if (output) {
      output.innerHTML = `
        <div class="context-note">
          <span>${escapeHtml(t("profileSuggestionsCreated"))}</span>
          ${escapeHtml(localizedCount(response.created_suggestions?.length || 0, "adminSuggestionSingular", "adminSuggestionPlural"))}
        </div>
      `;
    }
    await refreshAthleteAdminState(athleteId, {
      refreshProfile: false,
      refreshForm: false,
      refreshSuggestions: true,
    });
  } catch (_error) {
    if (output) output.innerHTML = errorState(new Error(t("profileSearchError")));
  }
}

function bindAthleteWorldGymnasticsTools(athleteId) {
  const output = $("#athleteWorldGymnasticsOutput");
  $("#findAthleteWorldGymnasticsCandidates")?.addEventListener("click", async () => {
    if (!output) return;
    output.innerHTML = loadingState();
    try {
      const response = await getJson(`/world-gymnastics/athletes/${athleteId}/candidates`, {}, { auth: true });
      output.innerHTML = renderWorldGymnasticsCandidateList(response);
    } catch (_error) {
      output.innerHTML = errorState(new Error(t("profileSearchError")));
    }
  });
  $("#athleteWorldGymnasticsManualForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const value = $("#athleteWorldGymnasticsSource")?.value.trim();
    if (!value) return;
    const payload = /^https?:\/\//i.test(value)
      ? { fig_profile_url: value }
      : { fig_athlete_id: value };
    await createWorldGymnasticsAthleteSuggestions(athleteId, payload, output);
  });
  output?.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-athlete-wg-use-profile]");
    if (!button) return;
    await createWorldGymnasticsAthleteSuggestions(athleteId, {
      fig_athlete_id: button.dataset.athleteWgUseProfile,
    }, output);
  });
}

function setAdminSuggestionFeedback(message, text, tone) {
  if (!message) return;
  message.classList.remove("is-success", "is-danger");
  if (tone === "success") message.classList.add("is-success");
  if (tone === "danger") message.classList.add("is-danger");
  message.textContent = text;
}

function bindAthleteSuggestionActions(athleteId) {
  document.querySelectorAll("[data-athlete-suggestion-accept]").forEach((button) => {
    button.addEventListener("click", async () => {
      const suggestionId = button.dataset.athleteSuggestionAccept;
      const value = document.querySelector(`[data-athlete-suggestion-value="${suggestionId}"]`)?.value.trim();
      const message = $("#athleteSuggestionMessage");
      button.disabled = true;
      try {
        await sendJson(`/data-suggestions/${suggestionId}/accept`, {
          body: value ? { value } : {},
        });
        await refreshAthleteAdminState(athleteId, { refreshAnalytics: true });
        setAdminSuggestionFeedback(message, t("suggestionAccepted"), "success");
      } catch (_error) {
        setAdminSuggestionFeedback(message, t("suggestionError"), "danger");
      } finally {
        button.disabled = false;
      }
    });
  });
  document.querySelectorAll("[data-athlete-suggestion-reject]").forEach((button) => {
    button.addEventListener("click", async () => {
      const suggestionId = button.dataset.athleteSuggestionReject;
      const message = $("#athleteSuggestionMessage");
      button.disabled = true;
      try {
        await sendJson(`/data-suggestions/${suggestionId}/reject`);
        await refreshAthleteAdminState(athleteId, {
          refreshProfile: false,
          refreshForm: false,
          refreshSuggestions: true,
        });
        setAdminSuggestionFeedback(message, t("suggestionRejected"), "danger");
      } catch (_error) {
        setAdminSuggestionFeedback(message, t("suggestionError"), "danger");
      } finally {
        button.disabled = false;
      }
    });
  });
}

function localizedAnd() {
  return {
    it: "e",
    es: "y",
    fr: "et",
  }[state.language] || "and";
}

function displayEnumValue(value) {
  const text = String(value || "").trim();
  if (!text) return "";
  return text
    .replace(/\b[a-z]/g, (letter) => letter.toUpperCase())
    .replace(/\bAnd\b/g, localizedAnd());
}

function eventCalendarStatusLabel(status) {
  const labels = {
    completed_with_results: t("completedWithResults"),
    completed_no_results: t("completedNoResults"),
    ongoing: t("ongoing"),
    upcoming: t("upcoming"),
  };
  return labels[status] || displayEnumValue(status);
}

function eventInitials(event = {}) {
  const words = String(event.name || "")
    .split(/\s+/)
    .map((word) => word.replace(/[^a-zA-Z0-9]/g, ""))
    .filter(Boolean);
  return words.slice(0, 2).map((word) => word[0]).join("").toUpperCase() || "L";
}

function renderEventProfileImage(event = {}) {
  const image = mediaUrl(event.image_url);
  if (image) {
    return `
      <div class="athlete-profile-image event-profile-image">
        <img src="${escapeHtml(image)}" alt="${escapeHtml(event.name || t("event"))}">
      </div>
    `;
  }
  return `<div class="athlete-profile-image athlete-profile-initials event-profile-image" aria-hidden="true">${escapeHtml(eventInitials(event))}</div>`;
}

function renderEventDetailsPanel(event, options = {}) {
  const embedded = Boolean(options.embedded);
  const showHeader = options.showHeader !== false;
  const profileLink = event.world_gymnastics_event_url
    ? `<a class="feature-link identity-profile-link" href="${escapeHtml(event.world_gymnastics_event_url)}" target="_blank" rel="noreferrer">${escapeHtml(t("openWorldGymnastics"))}</a>`
    : "";
  const resultCount = Number(event.result_count ?? event.results_count ?? 0);
  const calendarStatus = event.calendar_status && event.calendar_status !== "completed_with_results"
    ? eventCalendarStatusLabel(event.calendar_status)
    : "";
  const fields = [
    renderDetailFieldIfPresent(t("leverageId"), event.id),
    renderDetailFieldIfPresent(t("location"), event.location),
    renderDetailFieldIfPresent(t("venue"), event.venue),
    renderDetailFieldIfPresent(t("discipline"), displayEnumValue(event.discipline)),
    renderDetailFieldIfPresent(t("category"), displayEnumValue(event.category)),
    renderDetailFieldIfPresent(t("levelFilter"), event.level),
    renderDetailFieldIfPresent(t("status"), calendarStatus),
    resultCount ? renderDetailField(t("results"), resultCount.toLocaleString()) : "",
    event.world_gymnastics_event_url
      ? renderDetailFieldIfPresent(t("worldGymnasticsEvent"), event.world_gymnastics_event_url, { html: profileLink })
      : "",
  ].filter(Boolean).join("");
  const tag = embedded ? "div" : "section";
  const classes = [
    embedded ? "" : "panel athlete-detail-section",
    "athlete-identity-panel",
    "event-details-panel",
    embedded ? "athlete-identity-panel-embedded" : "",
  ].filter(Boolean).join(" ");
  return `
    <${tag} class="${classes}">
      ${showHeader ? `<div class="section-header compact-section-header">
        <div>
          <h2>${t("eventDetails")}</h2>
        </div>
      </div>` : ""}
      <div class="detail-grid athlete-identity-grid event-details-grid">
        ${fields || emptyMessage(t("notAvailable"))}
      </div>
    </${tag}>
  `;
}

function updateEventProfileSummary(event) {
  const panel = $("#eventProfileSummary");
  if (!panel || !event) return;
  const currentImage = panel.querySelector(".athlete-profile-image");
  if (currentImage) currentImage.outerHTML = renderEventProfileImage(event);
  const title = panel.querySelector(".athlete-profile-title-copy h2");
  if (title) title.textContent = event.name || "";
  const meta = panel.querySelector(".athlete-profile-title-copy .meta");
  if (meta) meta.textContent = formatReadableDateRange(event);
  const details = panel.querySelector(".event-details-panel");
  if (details) details.outerHTML = renderEventDetailsPanel(event, { embedded: true, showHeader: true });
}

function syncEventAdminForm(event) {
  const form = $("#eventAdminForm");
  if (!form || !event) return;
  [
    "name",
    "year",
    "location",
    "venue",
    "start_date",
    "end_date",
    "discipline",
    "category",
    "level",
    "image_url",
  ].forEach((name) => syncAdminFormValue(form, name, event[name]));
}

async function refreshEventAdminState(eventId, options = {}) {
  const {
    refreshProfile = true,
    refreshForm = true,
    refreshSuggestions = true,
  } = options;
  const adminView = await getJson(`/events/${eventId}/admin-view`, {}, { auth: true });
  const currentEvent = state.eventDetail.profile?.event || {};
  const event = {
    ...currentEvent,
    ...(adminView.event || {}),
  };
  if (state.eventDetail.profile) state.eventDetail.profile.event = event;
  if (refreshProfile) updateEventProfileSummary(event);
  if (refreshForm) syncEventAdminForm(event);
  if (refreshSuggestions) {
    const host = $("#eventSuggestionList");
    if (host) {
      host.innerHTML = renderEventSuggestions(adminView.pending_suggestions || []);
      bindEventSuggestionActions(eventId);
    }
  }
  return event;
}

function eventClassificationKey(group = {}) {
  return [
    group.discipline || "",
    group.category || "",
    group.format || "",
    group.round || "",
    group.apparatus || "",
    group.day ?? "",
  ].map((value) => encodeURIComponent(String(value))).join("|");
}

function eventClassificationOrderIndex(value, order) {
  const index = order.indexOf(String(value || ""));
  return index >= 0 ? index : order.length;
}

function eventClassificationApparatusIndex(group = {}) {
  const order = RANKING_APPARATUS_BY_DISCIPLINE[group.discipline] || [
    "AA",
    "FX",
    "PH",
    "SR",
    "VT",
    "PB",
    "HB",
    "UB",
    "BB",
    "VT AVG",
  ];
  return eventClassificationOrderIndex(group.apparatus, order);
}

function officialEventClassificationGroups(profile = state.eventDetail.profile) {
  return [...(profile?.result_groups || [])]
    .filter((group) => group && group.discipline && group.category && group.format && group.round)
    .sort((a, b) => (
      eventClassificationOrderIndex(a.discipline, ["MAG", "WAG"]) - eventClassificationOrderIndex(b.discipline, ["MAG", "WAG"])
      || eventClassificationOrderIndex(a.category, ["senior", "junior"]) - eventClassificationOrderIndex(b.category, ["senior", "junior"])
      || eventClassificationOrderIndex(a.format, ["individual", "apparatus", "team", "mixed team"]) - eventClassificationOrderIndex(b.format, ["individual", "apparatus", "team", "mixed team"])
      || eventClassificationOrderIndex(a.round, ["final", "qualification"]) - eventClassificationOrderIndex(b.round, ["final", "qualification"])
      || eventClassificationApparatusIndex(a) - eventClassificationApparatusIndex(b)
      || Number(a.day || 0) - Number(b.day || 0)
      || String(a.apparatus || "").localeCompare(String(b.apparatus || ""))
    ));
}

function selectedEventClassification(profile = state.eventDetail.profile) {
  const groups = officialEventClassificationGroups(profile);
  if (!groups.length) return null;
  return groups.find((group) => eventClassificationKey(group) === state.eventDetail.selectedClassificationKey) || groups[0];
}

function prepareEventDetailState(eventId, profile) {
  const numericId = Number(eventId);
  const groups = officialEventClassificationGroups(profile);
  const defaultKey = groups.length ? eventClassificationKey(groups[0]) : "";
  if (state.eventDetail.eventId !== numericId) {
    state.eventDetail.eventId = numericId;
    state.eventDetail.profile = profile;
    state.eventDetail.selectedClassificationKey = defaultKey;
    state.eventDetail.sortBy = "score";
    return;
  }
  state.eventDetail.profile = profile;
  if (!groups.some((group) => eventClassificationKey(group) === state.eventDetail.selectedClassificationKey)) {
    state.eventDetail.selectedClassificationKey = defaultKey;
  }
}

function eventClassificationCategoryLabel(value) {
  if (value === "junior") return t("junior");
  if (value === "senior") return t("senior");
  return displayEnumValue(value);
}

function eventClassificationFields() {
  return ["discipline", "category", "round", "format", "apparatus", "day"];
}

function eventClassificationValueKey(value) {
  return value === null || value === undefined ? "" : String(value);
}

function uniqueEventClassificationValues(values = []) {
  const seen = new Set();
  return values.filter((value) => {
    const key = eventClassificationValueKey(value);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function eventClassificationFieldLabel(field) {
  const labels = {
    discipline: t("classificationSection"),
    category: t("category"),
    round: t("round"),
    format: t("format"),
    apparatus: t("apparatus"),
    day: t("day"),
  };
  return labels[field] || displayEnumValue(field);
}

function eventClassificationValueLabel(field, value) {
  if (field === "discipline") return displayEnumValue(value);
  if (field === "category") return eventClassificationCategoryLabel(value);
  if (field === "round" || field === "format") return displayEnumValue(value);
  if (field === "day") return value ? `${t("day")} ${value}` : t("notAvailable");
  return String(value || "");
}

function eventClassificationMatchesPrefix(group, selected, fields) {
  return fields.every((field) => eventClassificationValueKey(group?.[field]) === eventClassificationValueKey(selected?.[field]));
}

function eventClassificationOptionsForField(field, selected, groups) {
  const fields = eventClassificationFields();
  const fieldIndex = fields.indexOf(field);
  const prefixFields = fields.slice(0, Math.max(0, fieldIndex));
  const options = [];
  const seen = new Set();
  groups.forEach((group) => {
    if (!eventClassificationMatchesPrefix(group, selected, prefixFields)) return;
    const value = group?.[field] ?? "";
    const key = eventClassificationValueKey(value);
    if (seen.has(key)) return;
    seen.add(key);
    options.push(value);
  });
  return options;
}

function eventClassificationDisplayOptionsForField(field, selected, groups) {
  const availableOptions = eventClassificationOptionsForField(field, selected, groups);
  if (field === "day") return availableOptions;
  if (field === "apparatus") {
    const discipline = selected?.discipline || groups.find((group) => hasDisplayValue(group?.discipline))?.discipline || "MAG";
    const apparatusOrder = RANKING_APPARATUS_BY_DISCIPLINE[discipline] || [];
    return uniqueEventClassificationValues([
      ...apparatusOrder,
      ...availableOptions.filter((value) => hasDisplayValue(value)),
    ]);
  }
  const fixedOptions = EVENT_CLASSIFICATION_FIXED_OPTIONS[field] || [];
  return fixedOptions.length
    ? uniqueEventClassificationValues([...fixedOptions, ...availableOptions])
    : availableOptions;
}

function eventClassificationOptionIsAvailable(field, value, selected, groups) {
  const selectedKey = eventClassificationValueKey(value);
  return eventClassificationOptionsForField(field, selected, groups)
    .some((option) => eventClassificationValueKey(option) === selectedKey);
}

function nextEventClassificationForChoice(field, value) {
  const groups = officialEventClassificationGroups();
  const selected = selectedEventClassification();
  const fields = eventClassificationFields();
  const fieldIndex = fields.indexOf(field);
  const prefixFields = fields.slice(0, Math.max(0, fieldIndex));
  const selectedValueKey = eventClassificationValueKey(value);
  return groups.find((group) => (
    eventClassificationMatchesPrefix(group, selected, prefixFields)
    && eventClassificationValueKey(group?.[field]) === selectedValueKey
  )) || groups[0] || null;
}

function eventClassificationSegment(field, selected, groups) {
  const options = eventClassificationDisplayOptionsForField(field, selected, groups);
  if (!options.length) return "";
  if (field === "day" && !options.some((value) => hasDisplayValue(value))) return "";
  const selectedValue = eventClassificationValueKey(selected?.[field]);
  const selectedIndex = Math.max(0, options.findIndex((value) => eventClassificationValueKey(value) === selectedValue));
  return `
    <div class="event-classification-segment-field event-classification-segment-field-${escapeHtml(field)}">
      <div
        class="segmented-control event-classification-segment event-classification-segment-${escapeHtml(field)}"
        role="radiogroup"
        aria-label="${escapeHtml(eventClassificationFieldLabel(field))}"
        data-event-classification-control="${escapeHtml(field)}"
        style="--segment-count: ${options.length}; --selected-index: ${selectedIndex};"
      >
        ${options.map((value) => {
          const key = eventClassificationValueKey(value);
          const active = key === selectedValue;
          const available = eventClassificationOptionIsAvailable(field, value, selected, groups);
          return `
            <button
              class="segmented-option event-classification-option"
              type="button"
              role="radio"
              data-event-classification-field="${escapeHtml(field)}"
              data-event-classification-value="${escapeHtml(key)}"
              aria-checked="${active}"
              aria-disabled="${available ? "false" : "true"}"
              ${available ? "" : "disabled"}
            >${escapeHtml(eventClassificationValueLabel(field, value))}</button>
          `;
        }).join("")}
        <span class="segmented-thumb event-classification-thumb" aria-hidden="true"></span>
      </div>
    </div>
  `;
}

function eventDetailSortBy() {
  return normalizeRankingMetricValue(state.eventDetail.sortBy);
}

function renderEventDetailMetricControl() {
  const selectedMetric = eventDetailSortBy();
  const selectedIndex = Math.max(0, RANKING_METRIC_FILTERS.findIndex((metric) => metric.value === selectedMetric));
  return `
    <div class="event-classification-segment-field event-detail-metric-field">
      <div
        class="segmented-control ranking-metric-control event-detail-metric-control"
        role="radiogroup"
        aria-label="${escapeHtml(t("rankingMetric"))}"
        style="--segment-count: ${RANKING_METRIC_FILTERS.length}; --selected-index: ${selectedIndex};"
      >
        ${RANKING_METRIC_FILTERS.map((metric) => `
          <button
            class="segmented-option ranking-metric-option event-detail-metric-option"
            type="button"
            role="radio"
            data-event-detail-metric="${escapeHtml(metric.value)}"
            aria-checked="${String(selectedMetric === metric.value)}"
          >${escapeHtml(metric.label)}</button>
        `).join("")}
        <span class="segmented-thumb ranking-metric-thumb event-detail-metric-thumb" aria-hidden="true"></span>
      </div>
    </div>
  `;
}

function eventDetailRankingParams(limit = 200) {
  const group = selectedEventClassification();
  const params = {
    ranking_limit: limit,
    sort_by: eventDetailSortBy(),
    data_quality: "all",
  };
  if (!group) return params;
  ["discipline", "category", "format", "round", "apparatus", "day"].forEach((key) => {
    if (group[key] !== null && group[key] !== undefined && group[key] !== "") {
      params[key] = group[key];
    }
  });
  return params;
}

function eventResultContextParts(payload = {}) {
  const filters = payload.applied_filters || selectedEventClassification() || {};
  return [
    displayEnumValue(filters.discipline),
    eventClassificationCategoryLabel(filters.category),
    filters.format ? displayEnumValue(filters.format) : "",
    filters.round ? displayEnumValue(filters.round) : "",
    filters.apparatus,
    filters.day ? `${t("day")} ${filters.day}` : "",
  ].filter(Boolean);
}

function renderEventResultContext(payload = {}) {
  const parts = eventResultContextParts(payload);
  const total = Number(payload.total_results || 0);
  const selectedMetric = normalizeRankingMetricValue(payload?.applied_filters?.sort_by || eventDetailSortBy());
  const contextTitle = t("eventClassification").toLocaleUpperCase(state.language);
  const contextDetails = [
    ...parts,
    rankingMetricLabel(selectedMetric),
    localizedCount(total, "result", "results"),
  ].filter(Boolean);
  return `
    <div class="context-note event-result-context sticky-context-note">
      <div class="context-note-copy">
        <span><strong class="context-note-lead">${escapeHtml(contextTitle)}</strong>${contextDetails.length ? ` · ${escapeHtml(contextDetails.join(" · "))}` : ""}</span>
      </div>
      ${renderStickyContextScrollButton("event-detail")}
    </div>
  `;
}

function renderEventResultGroups(profile = state.eventDetail.profile) {
  const groups = officialEventClassificationGroups(profile);
  if (!groups.length) return emptyMessage(t("eventNoResults"));
  const selected = selectedEventClassification(profile);
  const primaryFields = eventClassificationFields().filter((field) => field !== "apparatus");
  const primaryControls = primaryFields.map((field) => eventClassificationSegment(field, selected, groups)).filter(Boolean).join("");
  const apparatusControl = eventClassificationSegment("apparatus", selected, groups);
  return `
    <div class="event-classification-sticky-menu">
      <div class="event-result-groups">
        ${primaryControls ? `
          <div class="event-classification-select-grid event-classification-primary-row">
            ${primaryControls}
          </div>
        ` : ""}
        ${apparatusControl ? `
          <div class="event-classification-select-grid event-classification-apparatus-row">
            ${apparatusControl}
          </div>
        ` : ""}
        <div class="event-classification-select-grid event-classification-metric-row">
          ${renderEventDetailMetricControl()}
        </div>
      </div>
    </div>
  `;
}

function eventResultWarningMessages(results = [], payload = {}) {
  const selectedMetric = normalizeRankingMetricValue(payload?.applied_filters?.sort_by || eventDetailSortBy());
  return [
    ...(selectedMetric === "execution_estimate" ? [t("estimatedEScoreRankingNotice")] : []),
    ...localizedBackendWarnings(results.flatMap((entry) => entry.data_warnings || [])),
  ];
}

function renderEventResultWarnings(results = [], payload = {}) {
  return renderDataWarningStack(eventResultWarningMessages(results, payload), "event-result-warning-stack");
}

function renderEventRankingList(payload = {}) {
  const results = payload.results || payload.default_ranking || [];
  const selectedMetric = normalizeRankingMetricValue(payload?.applied_filters?.sort_by || eventDetailSortBy());
  const selectedApparatus = (payload.applied_filters || {}).apparatus || selectedEventClassification()?.apparatus || "";
  const showVaultAttempts = selectedApparatus === "VT";
  const context = renderEventResultContext(payload);
  const contextInStickyHost = renderContextInStickyHost("eventResultContextHost", context);
  const inlineContext = contextInStickyHost ? "" : context;
  if (!results.length) {
    const unavailableMetricEmpty = rankingUnavailableMetricEmptyState(selectedMetric, [selectedApparatus].filter(Boolean));
    return `${inlineContext}${unavailableMetricEmpty || emptyMessage(t("eventNoResults"))}${renderEventResultWarnings(results, payload)}`;
  }
  return `
    ${inlineContext}
    ${renderLeaderboardList(results, {
      className: "ranking-results-list event-detail-ranking-list",
      selectedMetric,
      returnContext: "classification",
      returnEventId: state.eventDetail.eventId,
      showVaultAttempts,
      showApparatus: false,
      showTags: false,
      rankForEntry: (entry) => (selectedMetric === "score" ? (entry.official_rank || entry.computed_rank) : entry.computed_rank),
      metaForEntry: (entry) => [entry.country],
    })}
    ${renderEventResultWarnings(results, payload)}
  `;
}

function renderEventResultsShell(profile = state.eventDetail.profile) {
  const hasResults = Boolean(profile?.event?.has_results || profile?.total_results);
  return `
    <section class="athlete-analytics-panel event-results-panel">
      ${hasResults ? `
        ${renderEventResultGroups(profile)}
        <div id="eventResultContextHost" class="sticky-summary-host event-detail-summary-sticky" data-sticky-summary="event-detail"></div>
        <div id="eventDetailResults" class="event-detail-results-content" aria-live="polite">
          ${loadingState()}
        </div>
      ` : emptyMessage(t("eventNoResults"))}
    </section>
  `;
}

async function loadEventDetailRanking({ showLoading = false } = {}) {
  const eventId = state.eventDetail.eventId;
  const node = $("#eventDetailResults");
  if (!eventId || !node || !selectedEventClassification()) return;
  const requestId = ++eventDetailRankingRequestId;
  eventDetailRankingAbortController?.abort();
  const abortController = new AbortController();
  eventDetailRankingAbortController = abortController;
  if (showLoading) node.innerHTML = loadingState();
  node.classList.add("is-updating");
  node.setAttribute("aria-busy", "true");
  try {
    const payload = await getJson(`/events/${eventId}/ranking-view`, eventDetailRankingParams(200), {
      signal: abortController.signal,
    });
    if (requestId !== eventDetailRankingRequestId) return;
    node.innerHTML = renderEventRankingList(payload);
  } catch (error) {
    if (error?.name === "AbortError") return;
    if (requestId !== eventDetailRankingRequestId) return;
    node.innerHTML = errorState(error);
  } finally {
    if (requestId === eventDetailRankingRequestId) {
      node.classList.remove("is-updating");
      node.setAttribute("aria-busy", "false");
      if (eventDetailRankingAbortController === abortController) {
        eventDetailRankingAbortController = null;
      }
    }
  }
}

function refreshEventDetailResultsInPlace() {
  window.clearTimeout(eventDetailRankingRefreshTimer);
  eventDetailRankingRequestId += 1;
  eventDetailRankingAbortController?.abort();
  eventDetailRankingAbortController = null;
  const node = $("#eventDetailResults");
  if (node) {
    node.classList.add("is-updating");
    node.setAttribute("aria-busy", "true");
  }
  eventDetailRankingRefreshTimer = window.setTimeout(() => {
    eventDetailRankingRefreshTimer = null;
    loadEventDetailRanking({ showLoading: false });
  }, 80);
  return Promise.resolve();
}

function bindEventClassificationControls(root = document, options = {}) {
  const rootNode = root && typeof root.querySelectorAll === "function" ? root : document;
  if (options.syncThumbs !== false) {
    syncEventDetailSegmentedThumbs(rootNode, { animate: false });
  }
  rootNode.querySelectorAll("[data-event-classification-value]").forEach((button) => {
    if (button.dataset.eventClassificationBound === "true") return;
    button.dataset.eventClassificationBound = "true";
    button.addEventListener("click", () => {
      const next = nextEventClassificationForChoice(button.dataset.eventClassificationField, button.dataset.eventClassificationValue);
      if (!next) return;
      const nextKey = eventClassificationKey(next);
      if (state.eventDetail.selectedClassificationKey === nextKey) return;
      state.eventDetail.selectedClassificationKey = nextKey;
      if (!syncEventDetailClassificationControls()) {
        const host = document.querySelector(".event-classification-sticky-menu");
        if (host) {
          host.outerHTML = renderEventResultGroups();
          bindEventClassificationControls();
        }
      }
      refreshEventDetailResultsInPlace();
    });
  });
  rootNode.querySelectorAll("[data-event-detail-metric]").forEach((button) => {
    if (button.dataset.eventDetailMetricBound === "true") return;
    button.dataset.eventDetailMetricBound = "true";
    button.addEventListener("click", () => {
      const nextMetric = normalizeRankingMetricValue(button.dataset.eventDetailMetric);
      if (eventDetailSortBy() === nextMetric) return;
      state.eventDetail.sortBy = nextMetric;
      syncEventDetailMetricControl();
      refreshEventDetailResultsInPlace();
    });
  });
}

function renderEventAdminForm(event) {
  return `
    <form class="admin-edit-form" id="eventAdminForm">
      <div class="section-header compact-section-header">
        <div>
          <h2>${t("editEvent")}</h2>
        </div>
        <button class="quiet-button" type="submit">${t("saveChanges")}</button>
      </div>
      <div class="admin-form-grid">
        <label class="admin-form-wide">
          <span>${t("event")}</span>
          <input name="name" value="${escapeHtml(event.name || "")}" required>
        </label>
        <label>
          <span>${t("eventYear")}</span>
          <input name="year" type="number" min="1900" max="2100" value="${escapeHtml(event.year || "")}" required>
        </label>
        <label>
          <span>${t("location")}</span>
          <input name="location" value="${escapeHtml(event.location || "")}">
        </label>
        <label>
          <span>${t("venue")}</span>
          <input name="venue" value="${escapeHtml(event.venue || "")}">
        </label>
        <label>
          <span>${t("fromDate")}</span>
          <input name="start_date" type="date" value="${escapeHtml(event.start_date || "")}">
        </label>
        <label>
          <span>${t("toDate")}</span>
          <input name="end_date" type="date" value="${escapeHtml(event.end_date || "")}">
        </label>
        ${renderAdminSelectControl(
          "discipline",
          t("discipline"),
          event.discipline,
          ["MAG", "WAG", "MAG and WAG"].map((value) => ({ value, label: displayEnumValue(value) })),
        )}
        ${renderAdminSelectControl(
          "category",
          t("category"),
          event.category,
          ["senior", "junior", "junior and senior"].map((value) => ({ value, label: displayEnumValue(value) })),
        )}
        ${renderAdminSelectControl("level", t("levelFilter"), event.level, EVENT_LEVEL_FILTERS)}
        <label class="admin-form-wide">
          <span>${t("imageUrl")}</span>
          <input name="image_url" value="${escapeHtml(event.image_url || "")}">
        </label>
      </div>
      <span class="auth-message" id="eventAdminMessage" role="status" aria-live="polite"></span>
    </form>
  `;
}

function renderEventSuggestions(suggestions = []) {
  if (!suggestions.length) return emptyMessage(t("noPendingSuggestions"));
  return `
    <div class="admin-review-list">
      ${suggestions.map((suggestion) => `
        <article class="admin-review-row" data-event-suggestion-row="${suggestion.id}">
          <div class="admin-review-copy">
            <span>${escapeHtml(suggestion.field_name)}</span>
            <strong>${escapeHtml(displayValue(suggestion.suggested_value))}</strong>
            ${suggestion.evidence ? `<p>${escapeHtml(suggestion.evidence)}</p>` : ""}
            ${suggestion.source_url ? `<a href="${escapeHtml(suggestion.source_url)}" target="_blank" rel="noreferrer">${escapeHtml(suggestion.source_title || suggestion.source_url)}</a>` : ""}
          </div>
          <div class="admin-review-actions">
            <label>
              <span>${t("suggestedValue")}</span>
              <input data-event-suggestion-value="${suggestion.id}" value="${escapeHtml(suggestion.suggested_value || "")}">
            </label>
            <div>
              <button class="quiet-button admin-accept-button" type="button" data-event-suggestion-accept="${suggestion.id}">${t("accept")}</button>
              <button class="quiet-button filter-clear-button" type="button" data-event-suggestion-reject="${suggestion.id}">${t("reject")}</button>
            </div>
          </div>
        </article>
      `).join("")}
    </div>
  `;
}

function renderWorldGymnasticsEventCandidateList(response) {
  const warnings = (response.warnings || []).map(localizedWorldGymnasticsWarning);
  const candidates = response.candidates || [];
  if (!candidates.length) {
    return `
      ${warnings.map((warning) => `<div class="context-note"><span>${escapeHtml(warning.type)}</span>${escapeHtml(warning.message)}</div>`).join("")}
      ${emptyMessage(t("noWorldGymnasticsCandidates"))}
    `;
  }
  return `
    <div class="admin-review-list">
      ${candidates.map((candidate) => {
        const period = formatReadableDateRange({
          start_date: candidate.start_date,
          end_date: candidate.end_date,
          year: candidate.start_date ? String(candidate.start_date).slice(0, 4) : "",
        });
        const meta = [
          [candidate.city, candidate.country].filter(Boolean).join(", "),
          period,
          (candidate.disciplines || []).join(", "),
          candidate.status,
        ].filter(Boolean).join(" · ");
        return `
          <article class="admin-review-row">
            <div class="admin-review-copy">
              <span>FIG event ID ${escapeHtml(candidate.event_id)}</span>
              <strong>${escapeHtml(candidate.title || t("event"))}</strong>
              <p>${escapeHtml(meta || t("notAvailable"))}</p>
              <a href="${escapeHtml(candidate.event_url)}" target="_blank" rel="noreferrer">${t("openWorldGymnastics")}</a>
            </div>
            <div class="admin-review-actions admin-candidate-actions">
              <span>${Math.round(Number(candidate.match_score || 0) * 100)}%</span>
              <button class="quiet-button" type="button" data-event-wg-use-event="${escapeHtml(candidate.event_id)}">${t("useEvent")}</button>
            </div>
          </article>
        `;
      }).join("")}
    </div>
  `;
}

function renderEventWorldGymnasticsAdminTools() {
  return `
    <div class="admin-tool-block">
      <div class="section-header compact-section-header">
        <div>
          <h2>${t("worldGymnasticsAssistant")}</h2>
        </div>
        <button class="quiet-button admin-world-gymnastics-search-button" type="button" id="findEventWorldGymnasticsCandidates">${t("findEvent")}</button>
      </div>
      <form class="admin-inline-form" id="eventWorldGymnasticsManualForm">
        <input id="eventWorldGymnasticsSource" placeholder="${escapeHtml(t("figEventIdOrUrl"))}">
        <button class="quiet-button admin-world-gymnastics-search-button" type="submit">${t("generateFromProfile")}</button>
      </form>
      <div class="admin-tool-output" id="eventWorldGymnasticsOutput"></div>
    </div>
  `;
}

function renderEventAdminPanel(event, adminView, adminViewError = null) {
  if (!isAdminUser()) return "";
  const suggestions = adminView?.pending_suggestions || [];
  return `
    <section class="panel athlete-admin-panel event-admin-panel detail-admin-panel" id="eventAdminPanel" data-admin-tools-panel hidden>
      <div class="section-header compact-section-header">
        <div>
          <p class="eyebrow">ADMIN</p>
          <h2>${t("adminEventTools")}</h2>
        </div>
      </div>
      ${renderEventAdminForm(event)}
      ${renderEventWorldGymnasticsAdminTools()}
      <div class="admin-tool-block">
        <div class="section-header compact-section-header">
          <div>
            <h2>${t("adminSuggestions")}</h2>
          </div>
        </div>
        <div id="eventSuggestionMessage" class="auth-message" role="status" aria-live="polite"></div>
        <div id="eventSuggestionList">
          ${adminViewError ? errorState(adminViewError) : renderEventSuggestions(suggestions)}
        </div>
      </div>
    </section>
  `;
}

function bindEventAdminForm(eventId) {
  const form = $("#eventAdminForm");
  if (!form) return;
  bindAdminSelectControls(form);
  form.addEventListener("submit", async (submitEvent) => {
    submitEvent.preventDefault();
    const message = $("#eventAdminMessage");
    const submit = form.querySelector("button[type='submit']");
    const formData = new FormData(form);
    const year = String(formData.get("year") || "").trim();
    const payload = {
      name: String(formData.get("name") || "").trim(),
      location: String(formData.get("location") || "").trim() || null,
      venue: String(formData.get("venue") || "").trim() || null,
      start_date: String(formData.get("start_date") || "").trim() || null,
      end_date: String(formData.get("end_date") || "").trim() || null,
      year: year ? Number(year) : null,
      discipline: String(formData.get("discipline") || "").trim(),
      category: String(formData.get("category") || "").trim(),
      level: String(formData.get("level") || "").trim(),
      image_url: String(formData.get("image_url") || "").trim() || null,
    };
    if (message) message.textContent = "";
    submit.disabled = true;
    try {
      await sendJson(`/events/${eventId}`, { method: "PUT", body: payload });
      await refreshEventAdminState(eventId);
      if (message) message.textContent = t("eventUpdateSaved");
    } catch (_error) {
      if (message) message.textContent = t("eventUpdateError");
    } finally {
      submit.disabled = false;
    }
  });
}

async function createWorldGymnasticsEventSuggestions(eventId, payload, outputNode = null) {
  const output = outputNode || $("#eventWorldGymnasticsOutput");
  if (output) output.innerHTML = loadingState();
  try {
    const response = await sendJson(`/world-gymnastics/events/${eventId}/suggestions`, { body: payload });
    if (output) {
      output.innerHTML = `
        <div class="context-note">
          <span>${escapeHtml(t("profileSuggestionsCreated"))}</span>
          ${escapeHtml(localizedCount(response.created_suggestions?.length || 0, "adminSuggestionSingular", "adminSuggestionPlural"))}
        </div>
      `;
    }
    await refreshEventAdminState(eventId, {
      refreshProfile: false,
      refreshForm: false,
      refreshSuggestions: true,
    });
  } catch (_error) {
    if (output) output.innerHTML = errorState(new Error(t("profileSearchError")));
  }
}

function bindEventWorldGymnasticsTools(eventId) {
  const output = $("#eventWorldGymnasticsOutput");
  $("#findEventWorldGymnasticsCandidates")?.addEventListener("click", async () => {
    if (!output) return;
    output.innerHTML = loadingState();
    try {
      const response = await getJson(`/world-gymnastics/events/${eventId}/candidates`, {}, { auth: true });
      output.innerHTML = renderWorldGymnasticsEventCandidateList(response);
    } catch (_error) {
      output.innerHTML = errorState(new Error(t("profileSearchError")));
    }
  });
  $("#eventWorldGymnasticsManualForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const value = $("#eventWorldGymnasticsSource")?.value.trim();
    if (!value) return;
    const payload = /^https?:\/\//i.test(value)
      ? { fig_event_url: value }
      : { fig_event_id: value };
    await createWorldGymnasticsEventSuggestions(eventId, payload, output);
  });
  output?.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-event-wg-use-event]");
    if (!button) return;
    await createWorldGymnasticsEventSuggestions(eventId, {
      fig_event_id: button.dataset.eventWgUseEvent,
    }, output);
  });
}

function bindEventSuggestionActions(eventId) {
  document.querySelectorAll("[data-event-suggestion-accept]").forEach((button) => {
    button.addEventListener("click", async () => {
      const suggestionId = button.dataset.eventSuggestionAccept;
      const value = document.querySelector(`[data-event-suggestion-value="${suggestionId}"]`)?.value.trim();
      const message = $("#eventSuggestionMessage");
      button.disabled = true;
      try {
        await sendJson(`/data-suggestions/${suggestionId}/accept`, {
          body: value ? { value } : {},
        });
        await refreshEventAdminState(eventId);
        setAdminSuggestionFeedback(message, t("suggestionAccepted"), "success");
      } catch (_error) {
        setAdminSuggestionFeedback(message, t("suggestionError"), "danger");
      } finally {
        button.disabled = false;
      }
    });
  });
  document.querySelectorAll("[data-event-suggestion-reject]").forEach((button) => {
    button.addEventListener("click", async () => {
      const suggestionId = button.dataset.eventSuggestionReject;
      const message = $("#eventSuggestionMessage");
      button.disabled = true;
      try {
        await sendJson(`/data-suggestions/${suggestionId}/reject`);
        await refreshEventAdminState(eventId, {
          refreshProfile: false,
          refreshForm: false,
          refreshSuggestions: true,
        });
        setAdminSuggestionFeedback(message, t("suggestionRejected"), "danger");
      } catch (_error) {
        setAdminSuggestionFeedback(message, t("suggestionError"), "danger");
      } finally {
        button.disabled = false;
      }
    });
  });
}

function savedRankingActiveFilterCount(filters = {}) {
  const hasTimeFilter = Boolean(
    filters.startYear || filters.endYear ||
    filters.startDate || filters.endDate ||
    filters.startPeriod || filters.endPeriod
  );
  return [
    normalizeSavedFilterArray(filters.discipline).length > 0,
    normalizeSavedFilterArray(filters.category).length > 0,
    normalizeSavedFilterArray(filters.level).length > 0,
    normalizeSavedFilterArray(filters.sortBy || filters.sort_by).length > 0,
    normalizeSavedFilterArray(filters.apparatus).length > 0,
    hasTimeFilter || normalizeSavedFilterArray(filters.scoringCycle).length > 0,
  ].filter(Boolean).length;
}

function savedRankingCategoryLabel(filters = {}) {
  const categories = normalizeSavedFilterArray(filters.category)
    .filter((value) => ["junior", "senior"].includes(value));
  if (!categories.length || (categories.includes("junior") && categories.includes("senior"))) {
    return displayEnumValue("junior and senior");
  }
  if (categories[0] === "junior") return t("junior");
  if (categories[0] === "senior") return t("senior");
  return "";
}

function renderSavedRankingViews(views) {
  const rankingViews = views.filter((view) => view.view_type === "ranking");
  if (!rankingViews.length) return emptyMessage(t("noSavedRankingViews"));
  return `<div class="grid-3 ranking-results-list account-preference-card-list account-saved-ranking-list">${rankingViews.map((view) => {
    const filters = view.filters || {};
    const discipline = normalizeSavedFilterArray(filters.discipline)[0] || "MAG";
    const category = savedRankingCategoryLabel(filters);
    const metric = rankingMetricLabel(normalizeRankingMetricValue(normalizeSavedFilterArray(filters.sortBy || filters.sort_by)[0]));
    const activeFilterCount = savedRankingActiveFilterCount(filters);
    const meta = [
      `${activeFilterCount} ${t(activeFilterCount === 1 ? "activeFilterSingular" : "activeFilterPlural")}`,
      view.created_at ? `${t("savedOn")} ${formatReadableDate(String(view.created_at).slice(0, 10))}` : "",
    ].filter(Boolean).join(" · ");
    const pills = [
      { label: discipline, variant: "brand" },
      ...(category ? [{ label: category }] : []),
      { label: metric },
    ];
    return entityCard(
      escapeHtml(view.name),
      escapeHtml(meta),
      pills.map((pill) => ({ ...pill, label: escapeHtml(pill.label) })),
      `#/rankings?savedView=${view.id}`,
      deleteSavedRankingButton(view.id),
    );
  }).join("")}</div>`;
}

function accountViewSection() {
  const value = currentParams().get("section") || "athletes";
  if (["events", "favorite-events"].includes(value)) return "events";
  if (["rankings", "saved-rankings"].includes(value)) return "rankings";
  return "athletes";
}

function renderAccountViewControl(selected) {
  const options = [
    { value: "athletes", label: t("navAthletes") },
    { value: "events", label: t("navEvents") },
    { value: "rankings", label: t("navRankings") },
  ];
  const selectedIndex = Math.max(0, options.findIndex((option) => option.value === selected));
  return `
    <div class="account-view-switcher">
      <div
        class="segmented-control account-view-toggle"
        role="radiogroup"
        aria-label="${escapeHtml(t("accountContentNavigation"))}"
        style="--selected-index: ${selectedIndex};"
      >
        ${options.map((option) => `
          <button
            class="segmented-option"
            type="button"
            role="radio"
            data-account-view="${option.value}"
            aria-checked="${String(option.value === selected)}"
          >${escapeHtml(option.label)}</button>
        `).join("")}
        <span class="segmented-thumb account-view-thumb" aria-hidden="true"></span>
      </div>
    </div>
  `;
}

function setAccountViewSection(section, { updateRoute = false } = {}) {
  const selected = ["athletes", "events", "rankings"].includes(section) ? section : "athletes";
  document.querySelectorAll("[data-account-view]").forEach((button) => {
    button.setAttribute("aria-checked", String(button.dataset.accountView === selected));
  });
  document.querySelectorAll("[data-account-view-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.accountViewPanel !== selected;
  });
  const control = document.querySelector(".account-view-toggle");
  if (control) {
    const selectedIndex = ["athletes", "events", "rankings"].indexOf(selected);
    control.style.setProperty("--selected-index", Math.max(0, selectedIndex));
  }
  if (updateRoute) {
    const route = `/account?section=${encodeURIComponent(selected)}`;
    state.route = route;
    window.history.replaceState(null, "", `#${route}`);
  }
}

function bindAccountViewControl() {
  document.querySelectorAll("[data-account-view]").forEach((button) => {
    button.addEventListener("click", () => {
      setAccountViewSection(button.dataset.accountView, { updateRoute: true });
    });
  });
}

async function renderAccount() {
  if (!state.currentUser) {
    authRequiredPage();
    return;
  }
  const selectedSection = accountViewSection();
  setApp(`
    ${pageHeading("accountHeading", "accountIntro")}
    <section class="panel account-summary">
      <div>
        <strong>${escapeHtml(state.currentUser.email)}</strong>
        <span>${escapeHtml(state.currentUser.role)}</span>
      </div>
      <button class="quiet-button outline-command-button" type="button" id="signOutButton">${t("signOut")}</button>
    </section>
    ${renderAccountViewControl(selectedSection)}
    <section class="account-grid">
      <section class="account-favorites-section account-view-panel" data-account-view-panel="athletes" ${selectedSection === "athletes" ? "" : "hidden"}>
        <div class="section-header">
          <div>
            <h2>${t("favoriteAthletes")}</h2>
          </div>
        </div>
        <div id="accountAthletes">${loadingState()}</div>
      </section>
      <section class="account-favorites-section account-view-panel" data-account-view-panel="events" ${selectedSection === "events" ? "" : "hidden"}>
        <div class="section-header">
          <div>
            <h2>${t("favoriteEvents")}</h2>
          </div>
        </div>
        <div id="accountEvents">${loadingState()}</div>
      </section>
      <section class="account-favorites-section account-ranking-views account-view-panel" id="accountSavedRankings" data-account-view-panel="rankings" ${selectedSection === "rankings" ? "" : "hidden"}>
        <div class="section-header">
          <div>
            <h2>${t("savedRankingViews")}</h2>
          </div>
        </div>
        <div id="accountRankingViews">${loadingState()}</div>
      </section>
    </section>
  `);
  bindAccountViewControl();
  $("#signOutButton").addEventListener("click", () => {
    clearAuth();
    window.location.hash = "#/";
  });
  try {
    const [athletes, events, dashboardViews] = await Promise.all([
      getJson("/preferences/athletes/followed/details", {}, { auth: true }),
      getJson("/preferences/events/saved/details", {}, { auth: true }),
      getJson("/preferences/dashboard-views", {}, { auth: true }),
    ]);
    state.favoriteAthleteIds = new Set(athletes.map((item) => Number(item.athlete_id)));
    state.favoriteEventIds = new Set(events.map((item) => Number(item.event_id)));
    state.favoritesLoaded = true;
    $("#accountAthletes").innerHTML = renderFavoriteAthletes(athletes);
    $("#accountEvents").innerHTML = renderFavoriteEvents(events);
    $("#accountRankingViews").innerHTML = renderSavedRankingViews(dashboardViews);
    bindFavoriteButtons();
    bindSavedRankingDeleteButtons();
  } catch (error) {
    $("#accountAthletes").innerHTML = errorState(error);
    $("#accountEvents").innerHTML = errorState(error);
    $("#accountRankingViews").innerHTML = errorState(error);
  }
}

function athleteDetailBackDestination() {
  const [, query = ""] = state.route.split("?");
  const params = new URLSearchParams(query);
  const source = params.get("from") || "";
  const returnRoute = params.get("return_to") || "";
  if (source === "athletes") {
    const athleteRoute = routeSection(returnRoute) === "athletes"
      ? returnRoute
      : SECTION_BASE_ROUTES.athletes;
    return { href: `#${athleteRoute}`, label: t("backToAthletes") };
  }
  if (source === "ranking") {
    const rankingRoute = routeSection(returnRoute) === "rankings"
      ? returnRoute
      : SECTION_BASE_ROUTES.rankings;
    return { href: `#${rankingRoute}`, label: t("backToRanking") };
  }
  if (source === "classification") {
    if (routeSection(returnRoute) === "events") {
      return { href: `#${returnRoute}`, label: t("backToClassification") };
    }
    const eventId = Number(params.get("event_id"));
    if (Number.isInteger(eventId) && eventId > 0) {
      return { href: `#/events/${eventId}`, label: t("backToClassification") };
    }
  }
  return { href: "#/athletes", label: t("backToAthletes") };
}

async function renderAthleteDetail(athleteId) {
  await ensureFavoritesLoaded().catch(() => {});
  state.athleteAnalytics.metric = "score";
  state.athleteAnalytics.mode = "period";
  state.athleteAnalytics.apparatuses = ["AA"];
  state.athleteAnalytics.payload = null;
  state.athleteAnalytics.startIndex = -1;
  state.athleteAnalytics.endIndex = -1;
  state.athleteAnalytics.snapshotIndex = -1;
  setApp(`<section class="panel">${loadingState()}</section>`);
  try {
    let athlete = await getJson(`/athletes/${athleteId}`);
    let adminView = null;
    let adminViewError = null;
    if (isAdminUser()) {
      try {
        adminView = await getJson(`/athletes/${athleteId}/admin-view`, {}, { auth: true });
        athlete = adminView.athlete || athlete;
      } catch (error) {
        adminViewError = error;
      }
    }
    const name = athleteProfileDisplayName(athlete);
    const backDestination = athleteDetailBackDestination();
    setApp(`
      <div class="detail-topbar">
        <a class="quiet-button detail-back-button" href="${escapeHtml(backDestination.href)}">${escapeHtml(backDestination.label)}</a>
      </div>
      <section class="panel profile-panel athlete-profile-summary-panel" id="athleteProfileSummary">
        <div class="athlete-profile-title-row">
          ${renderAthleteProfileImage(athlete)}
          <div class="athlete-profile-title-copy">
            <p class="eyebrow">${t("athleteProfile")}</p>
            <h2>${escapeHtml(name)}</h2>
            <div class="athlete-profile-verification">${renderAthleteVerificationBadge(athlete)}</div>
            <p class="meta">${escapeHtml([athlete.country, athlete.discipline].filter(Boolean).join(" · "))}</p>
          </div>
          ${detailProfileActions("athlete", athlete.id, state.favoriteAthleteIds.has(Number(athlete.id)))}
        </div>
        ${renderAthleteIdentityPanel(athlete, { embedded: true, showHeader: true })}
      </section>
      ${renderAthleteAdminPanel(athlete, adminView, adminViewError)}
      ${renderAthleteAnalyticsShell()}
    `);
    bindFavoriteButtons();
    bindAdminToolsToggles();
    bindAthleteAdminForm(athlete.id);
    bindAthleteWorldGymnasticsTools(athlete.id);
    bindAthleteSuggestionActions(athlete.id);
    loadAthleteAnalytics(athlete.id);
    rememberCurrentSectionRoute();
    syncSectionNavLinks();
  } catch (error) {
    setApp(errorState(error));
  }
}

async function renderEventDetail(eventId) {
  await ensureFavoritesLoaded().catch(() => {});
  setApp(`<section class="panel">${loadingState()}</section>`);
  try {
    const profile = await getJson(`/events/${eventId}/profile-view`, { ranking_limit: 60 });
    prepareEventDetailState(eventId, profile);
    let event = profile.event || await getJson(`/events/${eventId}`);
    let adminView = null;
    let adminViewError = null;
    if (isAdminUser()) {
      try {
        adminView = await getJson(`/events/${eventId}/admin-view`, {}, { auth: true });
        event = {
          ...event,
          ...(adminView.event || {}),
          result_count: event.result_count,
          has_results: event.has_results,
          calendar_status: event.calendar_status,
        };
      } catch (error) {
        adminViewError = error;
      }
    }
    profile.event = event;
    state.eventDetail.profile = profile;
    const period = formatReadableDateRange(event);
    const meta = [period].filter(Boolean).join(" · ");
    setApp(`
      <div class="detail-topbar">
        <a class="quiet-button detail-back-button" href="#/events">${escapeHtml(t("backToEvents"))}</a>
      </div>
      <section class="panel profile-panel athlete-profile-summary-panel event-profile-summary-panel" id="eventProfileSummary">
        <div class="athlete-profile-title-row">
          ${renderEventProfileImage(event)}
          <div class="athlete-profile-title-copy">
            <p class="eyebrow">${t("eventProfile")}</p>
            <h2>${escapeHtml(event.name)}</h2>
            <p class="meta">${escapeHtml(meta)}</p>
          </div>
          ${detailProfileActions("event", event.id, state.favoriteEventIds.has(Number(event.id)))}
        </div>
        ${renderEventDetailsPanel(event, { embedded: true, showHeader: true })}
      </section>
      ${renderEventAdminPanel(event, adminView, adminViewError)}
      ${renderEventResultsShell(profile)}
    `);
    bindFavoriteButtons();
    bindAdminToolsToggles();
    bindEventClassificationControls();
    loadEventDetailRanking();
    bindEventAdminForm(eventId);
    bindEventWorldGymnasticsTools(eventId);
    bindEventSuggestionActions(eventId);
  } catch (error) {
    setApp(errorState(error));
  }
}

function renderStaticPage(titleKey, introKey) {
  setApp(`
    ${pageHeading(titleKey, introKey)}
    <section class="grid-3">
      ${featureCard(t("rankingPreview"), t("rankingsText"), "#/rankings")}
      ${featureCard(t("compareTitle"), t("compareText"), "#/athletes")}
      ${featureCard(t("recentEvents"), t("eventsText"), "#/events")}
    </section>
  `);
}

function scrollToPageTop() {
  window.scrollTo({ top: 0, behavior: "auto" });
}

function scrollToPageTopSmooth() {
  const startTop = window.scrollY || document.documentElement.scrollTop || 0;
  if (startTop <= 3) return Promise.resolve();
  const maxDuration = Math.min(950, Math.max(320, startTop * 0.35));
  const startedAt = performance.now();
  window.scrollTo({ top: 0, behavior: "smooth" });
  return new Promise((resolve) => {
    const checkPosition = () => {
      const currentTop = window.scrollY || document.documentElement.scrollTop || 0;
      const timedOut = performance.now() - startedAt > maxDuration + 180;
      if (currentTop <= 3 || timedOut) {
        resolve();
        return;
      }
      window.requestAnimationFrame(checkPosition);
    };
    window.requestAnimationFrame(checkPosition);
  });
}

function topbarScrollOffset() {
  const cssTopbarHeight = Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--topbar-height")) || 0;
  const topbarHeight = document.querySelector(".topbar")?.getBoundingClientRect().height || 0;
  return Math.max(cssTopbarHeight, topbarHeight);
}

function sectionResultsSelector(scope) {
  if (scope === "athletes") return "#athleteResults";
  if (scope === "events") return "#eventViewResults";
  if (scope === "rankings") return "#rankingResults";
  if (scope === "event-detail") return "#eventDetailResults";
  return "";
}

function sectionStickyControlsSelector(scope) {
  if (scope === "athletes" || scope === "events") return ".section-search-row";
  if (scope === "rankings") return ".ranking-summary-sticky";
  if (scope === "event-detail") return ".event-detail-summary-sticky";
  return "";
}

function sectionStickyControlsOffset(scope) {
  const selector = sectionStickyControlsSelector(scope);
  const node = selector ? document.querySelector(selector) : null;
  return node?.getBoundingClientRect().height || 0;
}

function scrollToSectionRecordsTop(scope) {
  const selector = sectionResultsSelector(scope);
  const node = selector ? $(selector) : null;
  if (!node) {
    scrollToPageTop();
    return;
  }
  const stickyOffset = topbarScrollOffset() + sectionStickyControlsOffset(scope);
  const targetTop = Math.max(0, node.getBoundingClientRect().top + window.scrollY - stickyOffset - 14);
  window.scrollTo({ top: targetTop, behavior: "smooth" });
}

function refreshListFromFilter(refreshResult, scope = "", options = {}) {
  const scrollMode = Object.prototype.hasOwnProperty.call(options, "scroll")
    ? options.scroll
    : (scope ? "records" : "page");
  Promise.resolve(refreshResult)
    .catch(() => {})
    .finally(() => requestAnimationFrame(() => {
      if (scrollMode === false || scrollMode === "none") {
        return;
      }
      if (scrollMode === "records" && scope) {
        scrollToSectionRecordsTop(scope);
      } else {
        scrollToPageTop();
      }
    }));
  return refreshResult;
}

function setSectionFilterRefresher(scope, refresher) {
  sectionFilterRefreshers[scope] = typeof refresher === "function" ? refresher : null;
}

function refreshSectionFilters(scope, options = {}) {
  const refresher = sectionFilterRefreshers[scope];
  if (typeof refresher === "function") {
    return refresher(options);
  }
  return renderAfterFilterChange(options);
}

function refreshSectionFiltersAtRecordsTop(scope) {
  scrollToSectionRecordsTop(scope);
  return refreshSectionFilters(scope, { scroll: false, showLoading: false });
}

function renderAfterFilterChange(options = {}) {
  return refreshListFromFilter(render(), "", options);
}

function render() {
  normalizeRoute();
  setActiveNav();
  applyTranslations();
  syncTopbarHeight();
  const athleteDetailMatch = state.route.match(/^\/athletes\/(\d+)/);
  const eventDetailMatch = state.route.match(/^\/events\/(\d+)/);
  if (state.route.startsWith("/account")) {
    return renderAccount();
  } else if (athleteDetailMatch) {
    return renderAthleteDetail(athleteDetailMatch[1]);
  } else if (eventDetailMatch) {
    return renderEventDetail(eventDetailMatch[1]);
  } else if (state.route.startsWith("/athletes")) {
    return renderAthletes();
  } else if (state.route.startsWith("/events")) {
    return renderEvents();
  } else if (state.route.startsWith("/rankings")) {
    return renderRankings();
  } else if (state.route.startsWith("/search")) {
    return renderGlobalSearch();
  } else if (state.route.startsWith("/analytics")) {
    return renderAnalyticsComparison();
  } else if (state.route.startsWith("/verify-email")) {
    return renderVerifyEmail();
  } else if (state.route.startsWith("/register")) {
    return renderRegister();
  } else if (state.route.startsWith("/login")) {
    return renderLogin();
  } else {
    return renderHome();
  }
}

async function init() {
  setupIntroSplash();
  bindSectionNavLinks();
  syncLanguageControl();
  $("#languageButton").addEventListener("click", (event) => {
    event.stopPropagation();
    const control = $("#languageControl");
    const isOpen = control.classList.toggle("is-open");
    $("#languageButton").setAttribute("aria-expanded", String(isOpen));
  });
  document.querySelectorAll("[data-language-option]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      setLanguage(button.dataset.languageOption);
      closeLanguageMenu();
    });
  });
  document.addEventListener("click", closeLanguageMenu);
  document.addEventListener("click", closeSearchSuggestions);
  document.addEventListener("pointerdown", closeFilterPopupsOnOutsidePointerDown, true);
  bindAthleteTrendTooltipEvents();
  bindAthleteTrendZoomEvents();
  bindAthleteRadarTooltipEvents();
  bindLeaderboardExpansionEvents();
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeLanguageMenu();
      closeFilterPopups();
      closeRankingSavePopup();
    }
  });
  window.addEventListener("hashchange", render);
  window.addEventListener("resize", () => {
    syncTopbarHeight();
    syncNavIndicator();
    syncEventDetailSegmentedThumbs(document, { animate: false });
  });
  if (state.authToken) {
    await hydrateCurrentUser();
  }
  render();
  syncTopbarHeight();
}

init();
