const API_BASE_KEY = "leverage.apiBase";
const LANGUAGE_KEY = "leverage.language";

const state = {
  route: "/",
  language: localStorage.getItem(LANGUAGE_KEY) || "en",
  apiBase: localStorage.getItem(API_BASE_KEY) || "http://localhost:8000",
  homeCalendarMonthOffset: 0,
  eventsCalendarMonthOffset: 0,
  filters: {
    athletes: {
      discipline: [],
      category: [],
    },
    events: {
      discipline: [],
      category: [],
      level: [],
      calendarStatus: "",
    },
    rankings: {
      discipline: [],
      category: [],
      apparatus: [],
      scoringCycle: [],
      startYear: "",
      endYear: "",
      startDate: "",
      endDate: "",
    },
  },
};
const CURRENT_YEAR = new Date().getFullYear();
const TODAY = new Date();
const RANKING_APPARATUS_BY_DISCIPLINE = {
  MAG: ["AA", "FX", "PH", "SR", "VT", "PB", "HB"],
  WAG: ["AA", "VT", "UB", "BB", "FX"],
};
const SCORING_CYCLE_FILTERS = ["2017-2021", "2022-2024", "2025-2028"];
const RANKING_YEAR_FILTERS = Array.from(
  { length: Math.max(0, CURRENT_YEAR - 2018 + 1) },
  (_, index) => String(2018 + index),
);
const EVENT_LEVEL_FILTERS = [
  { label: "Olympic Games", value: "Olympic Games" },
  { label: "World Championships", value: "World Championships" },
  { label: "Continental Championships", value: "Continental Championships" },
  { label: "FIG World Cups", value: "World Cup" },
  { label: "FIG Challenge", value: "World Challenge Cup" },
  { label: "International Events", value: "International Event" },
  { label: "National Events", value: "National Event" },
];
let searchAutocompleteRequestId = 0;
let athleteSearchRequestId = 0;
let eventSearchRequestId = 0;

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
    language: "Language",
    save: "Save",
    footerTagline: "Artistic Gymnastics Analytics",
    heroEyebrow: "Elite gymnastics, structured.",
    heroTitle: "LEVERAGE",
    heroSubtitle: "Artistic Gymnastics Analytics",
    heroBody: "Search athletes, events and rankings from a curated gymnastics database built for comparison, context and clarity.",
    searchPlaceholder: "Search athletes, events, countries, apparatus...",
    athleteSearchPlaceholder: "Search athletes by name, ID or country...",
    search: "Search",
    globalSearchHeading: "Search",
    globalSearchIntro: "Search across athletes, events, countries, apparatus and results.",
    matchingAthletes: "Athletes",
    matchingEvents: "Events",
    matchingCountries: "Countries",
    matchingApparatuses: "Apparatus",
    matchingResults: "Results",
    filteredResults: "Filtered results",
    relatedResults: "Related results",
    noGlobalSearchQuery: "Type a search term to explore all LEVERAGE data.",
    noGlobalSearchResults: "No global results found.",
    noStructuredSearchResults: "No results match all the search filters together. Related matches are shown below.",
    dataLoadError: "Unable to load live data. Please try again in a moment.",
    exploreTitle: "Start with the data",
    exploreSubtitle: "Four clear paths into the platform.",
    athletesTitle: "Explore athletes",
    athletesText: "Find gymnasts by name, country or discipline.",
    eventsTitle: "Browse events",
    eventsText: "Use the calendar to move through seasons and competitions.",
    rankingsTitle: "View rankings",
    rankingsText: "Sort results by final score, D score or available metrics.",
    compareTitle: "Compare performance",
    compareText: "Prepare athlete comparisons and long-term trends.",
    open: "Open",
    recentEvents: "Calendar",
    calendarMonth: "Calendar month",
    currentMonth: "Current month",
    previousMonth: "Previous month",
    nextMonth: "Next month",
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
    athletesIntro: "Search the athlete database with discipline and country-aware filters.",
    eventsHeading: "Events",
    eventsIntro: "Calendar entries, completed competitions and upcoming events in one view.",
    eventSearchPlaceholder: "Search events by competition, year or place...",
    eventListHeading: "Competitions",
    eventListIntro: "Live event results from the current search and filters.",
    rankingsHeading: "Rankings",
    rankingsIntro: "Rankings stay separated by discipline and scoring cycle to keep comparisons meaningful.",
    analyticsHeading: "Analytics",
    analyticsIntro: "The backend is ready for trends, comparisons, apparatus profiles and age analysis.",
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
    scoringCycle: "Scoring cycle",
    allCycles: "All cycles",
    timeInterval: "Time interval",
    wholeYear: "Whole year",
    fromYear: "From year",
    toYear: "To year",
    fromDate: "From date",
    toDate: "To date",
    clearPeriod: "Clear period",
    eventYear: "Event year",
    country: "Country",
    date: "Date",
    status: "Status",
    event: "Event",
    athlete: "Athlete",
    comingSoon: "Coming soon",
  },
  it: {
    navHome: "Home",
    navAthletes: "Atleti",
    navEvents: "Eventi",
    navRankings: "Classifiche",
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
    rankingsMenuScores: "Classifiche score",
    rankingsMenuScoresText: "Ordina per final score e componenti disponibili.",
    rankingsMenuFilters: "Filtri smart",
    rankingsMenuFiltersText: "Usa solo valori realmente presenti nei dati.",
    rankingsMenuQuality: "Qualita dati",
    rankingsMenuQualityText: "Riconosci valori stimati o non disponibili.",
    analyticsMenuTrends: "Trend performance",
    analyticsMenuTrendsText: "Segui i punteggi in periodi selezionati.",
    analyticsMenuAge: "Eta e nazione",
    analyticsMenuAgeText: "Studia distribuzioni eta per nazione ed evento.",
    analyticsMenuApparatus: "Profili attrezzo",
    analyticsMenuApparatusText: "Prepara diagrammi MAG e WAG per attrezzo.",
    signIn: "Accedi",
    language: "Lingua",
    save: "Salva",
    footerTagline: "Artistic Gymnastics Analytics",
    heroEyebrow: "Ginnastica elite, strutturata.",
    heroTitle: "LEVERAGE",
    heroSubtitle: "Artistic Gymnastics Analytics",
    heroBody: "Cerca atleti, eventi e classifiche in un database di ginnastica progettato per confronto, contesto e chiarezza.",
    searchPlaceholder: "Cerca atleti, eventi, nazioni, attrezzi...",
    athleteSearchPlaceholder: "Cerca atleti per nome, ID o nazione...",
    search: "Cerca",
    globalSearchHeading: "Ricerca",
    globalSearchIntro: "Cerca in atleti, eventi, nazioni, attrezzi e risultati.",
    matchingAthletes: "Atleti",
    matchingEvents: "Eventi",
    matchingCountries: "Nazioni",
    matchingApparatuses: "Attrezzi",
    matchingResults: "Risultati",
    filteredResults: "Risultati filtrati",
    relatedResults: "Risultati collegati",
    noGlobalSearchQuery: "Scrivi un termine per cercare in tutti i dati di LEVERAGE.",
    noGlobalSearchResults: "Nessun risultato globale trovato.",
    noStructuredSearchResults: "Nessun risultato corrisponde a tutti i filtri della ricerca. Sotto trovi i match collegati.",
    dataLoadError: "Impossibile caricare i dati live. Riprova tra poco.",
    exploreTitle: "Parti dai dati",
    exploreSubtitle: "Quattro percorsi chiari nella piattaforma.",
    athletesTitle: "Esplora atleti",
    athletesText: "Trova ginnasti per nome, nazione o disciplina.",
    eventsTitle: "Sfoglia eventi",
    eventsText: "Usa il calendario per navigare stagioni e competizioni.",
    rankingsTitle: "Vedi classifiche",
    rankingsText: "Ordina i risultati per score, D score o metriche disponibili.",
    compareTitle: "Confronta performance",
    compareText: "Prepara confronti atleta e trend nel tempo.",
    open: "Apri",
    recentEvents: "Calendario",
    calendarMonth: "Mese calendario",
    currentMonth: "Mese corrente",
    previousMonth: "Mese precedente",
    nextMonth: "Mese successivo",
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
    athletesIntro: "Cerca nel database atleti con filtri per disciplina e nazione.",
    eventsHeading: "Eventi",
    eventsIntro: "Calendario, competizioni concluse ed eventi futuri in una sola vista.",
    eventSearchPlaceholder: "Cerca eventi per competizione, anno o luogo...",
    eventListHeading: "Competizioni",
    eventListIntro: "Lista eventi aggiornata in tempo reale da ricerca e filtri.",
    rankingsHeading: "Classifiche",
    rankingsIntro: "Le classifiche restano separate per disciplina e ciclo di punteggio, cosi i confronti restano significativi.",
    analyticsHeading: "Analytics",
    analyticsIntro: "Il backend e pronto per trend, confronti, profili attrezzi e analisi eta.",
    loginHeading: "Accedi",
    loginIntro: "Le aree utente e admin useranno il sistema di autenticazione gia implementato.",
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
    scoringCycle: "Ciclo punteggio",
    allCycles: "Tutti i cicli",
    timeInterval: "Intervallo di tempo",
    wholeYear: "Anno intero",
    fromYear: "Da anno",
    toYear: "A anno",
    fromDate: "Da data",
    toDate: "A data",
    clearPeriod: "Cancella periodo",
    eventYear: "Anno gara",
    country: "Nazione",
    date: "Data",
    status: "Stato",
    event: "Evento",
    athlete: "Atleta",
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
    language: "Idioma",
    save: "Guardar",
    footerTagline: "Artistic Gymnastics Analytics",
    heroEyebrow: "Gimnasia elite, estructurada.",
    heroTitle: "LEVERAGE",
    heroSubtitle: "Artistic Gymnastics Analytics",
    heroBody: "Busca atletas, eventos y rankings en una base de datos de gimnasia creada para comparar con claridad.",
    searchPlaceholder: "Buscar atletas, eventos, paises, aparatos...",
    athleteSearchPlaceholder: "Buscar atletas por nombre, ID o pais...",
    search: "Buscar",
    globalSearchHeading: "Buscar",
    globalSearchIntro: "Busca en atletas, eventos, paises, aparatos y resultados.",
    matchingAthletes: "Atletas",
    matchingEvents: "Eventos",
    matchingCountries: "Paises",
    matchingApparatuses: "Aparatos",
    matchingResults: "Resultados",
    filteredResults: "Resultados filtrados",
    relatedResults: "Resultados relacionados",
    noGlobalSearchQuery: "Escribe un termino para explorar todos los datos de LEVERAGE.",
    noGlobalSearchResults: "No se encontraron resultados globales.",
    noStructuredSearchResults: "Ningun resultado coincide con todos los filtros de busqueda. Abajo se muestran coincidencias relacionadas.",
    dataLoadError: "No se pueden cargar los datos en vivo. Intentalo de nuevo en un momento.",
    exploreTitle: "Empieza por los datos",
    exploreSubtitle: "Cuatro caminos claros dentro de la plataforma.",
    athletesTitle: "Explorar atletas",
    athletesText: "Encuentra gimnastas por nombre, pais o disciplina.",
    eventsTitle: "Ver eventos",
    eventsText: "Usa el calendario para navegar temporadas y competiciones.",
    rankingsTitle: "Ver rankings",
    rankingsText: "Ordena resultados por score, D score o metricas disponibles.",
    compareTitle: "Comparar rendimiento",
    compareText: "Prepara comparaciones y tendencias a largo plazo.",
    open: "Abrir",
    recentEvents: "Calendario",
    calendarMonth: "Mes calendario",
    currentMonth: "Mes actual",
    previousMonth: "Mes anterior",
    nextMonth: "Mes siguiente",
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
    athletesIntro: "Busca atletas con filtros por disciplina y pais.",
    eventsHeading: "Eventos",
    eventsIntro: "Calendario, competiciones completadas y eventos futuros.",
    eventSearchPlaceholder: "Buscar eventos por competicion, ano o lugar...",
    eventListHeading: "Competiciones",
    eventListIntro: "Lista de eventos actualizada con busqueda y filtros.",
    rankingsHeading: "Rankings",
    rankingsIntro: "Los rankings se separan por disciplina y ciclo de puntuacion para mantener comparaciones coherentes.",
    analyticsHeading: "Analitica",
    analyticsIntro: "El backend ya soporta tendencias, comparaciones y perfiles por aparato.",
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
    scoringCycle: "Ciclo de puntuacion",
    allCycles: "Todos los ciclos",
    timeInterval: "Intervalo de tiempo",
    wholeYear: "Ano completo",
    fromYear: "Desde ano",
    toYear: "Hasta ano",
    fromDate: "Desde fecha",
    toDate: "Hasta fecha",
    clearPeriod: "Borrar periodo",
    eventYear: "Ano del evento",
    country: "Pais",
    date: "Fecha",
    status: "Estado",
    event: "Evento",
    athlete: "Atleta",
    comingSoon: "Proximamente",
  },
  fr: {
    navHome: "Accueil",
    navAthletes: "Athletes",
    navEvents: "Evenements",
    navRankings: "Classements",
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
    rankingsMenuScores: "Classements score",
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
    language: "Langue",
    save: "Enregistrer",
    footerTagline: "Artistic Gymnastics Analytics",
    heroEyebrow: "Gymnastique elite, structuree.",
    heroTitle: "LEVERAGE",
    heroSubtitle: "Artistic Gymnastics Analytics",
    heroBody: "Recherchez athletes, evenements et classements dans une base de donnees concue pour comparer clairement.",
    searchPlaceholder: "Rechercher athletes, evenements, pays, appareils...",
    athleteSearchPlaceholder: "Rechercher athletes par nom, ID ou pays...",
    search: "Rechercher",
    globalSearchHeading: "Recherche",
    globalSearchIntro: "Recherchez athletes, evenements, pays, appareils et resultats.",
    matchingAthletes: "Athletes",
    matchingEvents: "Evenements",
    matchingCountries: "Pays",
    matchingApparatuses: "Appareils",
    matchingResults: "Resultats",
    filteredResults: "Resultats filtres",
    relatedResults: "Resultats lies",
    noGlobalSearchQuery: "Saisissez un terme pour explorer toutes les donnees LEVERAGE.",
    noGlobalSearchResults: "Aucun resultat global trouve.",
    noStructuredSearchResults: "Aucun resultat ne correspond a tous les filtres de recherche. Les correspondances liees sont affichees ci-dessous.",
    dataLoadError: "Impossible de charger les donnees en direct. Reessayez dans un instant.",
    exploreTitle: "Commencer par les donnees",
    exploreSubtitle: "Quatre entrees simples dans la plateforme.",
    athletesTitle: "Explorer les athletes",
    athletesText: "Trouvez les gymnastes par nom, pays ou discipline.",
    eventsTitle: "Voir les evenements",
    eventsText: "Utilisez le calendrier pour parcourir les saisons.",
    rankingsTitle: "Voir les classements",
    rankingsText: "Triez les resultats par score, D score ou metriques disponibles.",
    compareTitle: "Comparer les performances",
    compareText: "Preparez comparaisons et tendances dans le temps.",
    open: "Ouvrir",
    recentEvents: "Calendrier",
    calendarMonth: "Mois calendrier",
    currentMonth: "Mois courant",
    previousMonth: "Mois precedent",
    nextMonth: "Mois suivant",
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
    athletesIntro: "Recherchez dans la base avec filtres discipline et pays.",
    eventsHeading: "Evenements",
    eventsIntro: "Calendrier, competitions terminees et evenements futurs.",
    eventSearchPlaceholder: "Rechercher evenements par competition, annee ou lieu...",
    eventListHeading: "Competitions",
    eventListIntro: "Liste d'evenements mise a jour par recherche et filtres.",
    rankingsHeading: "Classements",
    rankingsIntro: "Les classements restent separes par discipline et cycle de notation pour garder des comparaisons coherentes.",
    analyticsHeading: "Analytique",
    analyticsIntro: "Le backend supporte tendances, comparaisons et profils par appareil.",
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
    scoringCycle: "Cycle de notation",
    allCycles: "Tous les cycles",
    timeInterval: "Intervalle",
    wholeYear: "Annee complete",
    fromYear: "Depuis annee",
    toYear: "Jusqu'a annee",
    fromDate: "Depuis date",
    toDate: "Jusqu'a date",
    clearPeriod: "Effacer periode",
    eventYear: "Annee competition",
    country: "Pays",
    date: "Date",
    status: "Statut",
    event: "Evenement",
    athlete: "Athlete",
    comingSoon: "Bientot",
  },
};

const $ = (selector) => document.querySelector(selector);
const t = (key) => translations[state.language]?.[key] || translations.en[key] || key;
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

function closeLanguageMenu() {
  const control = $("#languageControl");
  const button = $("#languageButton");
  if (!control || !button) return;
  control.classList.remove("is-open");
  button.setAttribute("aria-expanded", "false");
}

function closeSearchSuggestions() {
  document.querySelectorAll(".search-suggestions").forEach((node) => {
    node.hidden = true;
    node.innerHTML = "";
    setSearchSuggestionsOpen(node, false);
  });
}

function setSearchSuggestionsOpen(suggestions, isOpen, itemCount = 4) {
  const form = suggestions.closest(".search-form");
  if (!form) return;
  form.classList.toggle("search-suggestions-open", isOpen);
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

function apiUrl(path, params = {}) {
  const url = new URL(path, state.apiBase);
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

async function getJson(path, params = {}) {
  const response = await fetch(apiUrl(path, params), { headers: { Accept: "application/json" } });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
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

function setActiveNav() {
  document.querySelectorAll(".nav-trigger").forEach((link) => {
    const route = link.getAttribute("href")?.replace("#", "");
    const active = route === "/"
      ? state.route === "/" || state.route.startsWith("/search")
      : (
          state.route === route ||
          state.route.startsWith(`${route}/`) ||
          state.route.startsWith(`${route}?`)
        );
    if (active) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  });
}

function setApp(html) {
  $("#app").innerHTML = html;
  $("#app").focus({ preventScroll: true });
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

function entityCard(title, meta, pills = [], href = "") {
  const content = `
    <article class="entity-card">
      <div class="entity-row">
        <h3>${title}</h3>
      </div>
      <p class="meta">${meta}</p>
      <div class="pill-row">
        ${pills.map((pill) => `<span class="pill ${pill.variant || ""}">${pill.label}</span>`).join("")}
      </div>
    </article>
  `;
  return href ? `<a href="${href}">${content}</a>` : content;
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

function messageState(message) {
  return `<div class="empty-state">${message}</div>`;
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
            <input class="search-input" id="globalSearchInput" type="search" autocomplete="off" placeholder="${t("searchPlaceholder")}">
            <button class="primary-button" type="submit">${t("search")}</button>
            <div class="search-suggestions" id="globalSearchSuggestions" role="listbox" hidden></div>
          </form>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <div>
          <h2>${t("exploreTitle")}</h2>
          <p>${t("exploreSubtitle")}</p>
        </div>
      </div>
      <div class="grid-4">
        ${featureCard(t("athletesTitle"), t("athletesText"), "#/athletes")}
        ${featureCard(t("eventsTitle"), t("eventsText"), "#/events")}
        ${featureCard(t("rankingsTitle"), t("rankingsText"), "#/rankings")}
        ${featureCard(t("compareTitle"), t("compareText"), "#/analytics")}
      </div>
    </section>

    <section class="section content-grid home-preview-grid">
      <div class="panel home-calendar-panel" id="homeCalendarPanel">
        <div class="section-header">
          <h2>${t("recentEvents")}</h2>
          <a class="quiet-button" href="#/events">${t("viewAll")}</a>
        </div>
        <div id="homeEvents">${loadingState()}</div>
      </div>
      <div class="panel home-ranking-panel" id="homeRankingPanel">
        <div class="section-header">
          <h2>${t("rankingPreview")}</h2>
          <a class="quiet-button" href="#/rankings">${t("viewAll")}</a>
        </div>
        <div class="home-ranking-scroll" id="homeRankingScroll">
          <div id="homeRankings">${loadingState()}</div>
        </div>
      </div>
    </section>
  `);

  $("#globalSearchForm").addEventListener("submit", (event) => {
    event.preventDefault();
    closeSearchSuggestions();
    const query = $("#globalSearchInput").value.trim();
    window.location.hash = query ? `#/search?q=${encodeURIComponent(query)}` : "#/search";
  });
  setupSearchAutocomplete("#globalSearchInput", "#globalSearchSuggestions");

  await hydrateHome();
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

function facetSuggestion(label, query, meta) {
  return {
    label,
    meta,
    query,
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
  const countries = data.countries || [];
  const apparatuses = data.apparatuses || [];
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
  appendUniqueSuggestions(items, apparatuses.slice(0, 3).map((apparatus) => (
    facetSuggestion(
      apparatus.label,
      apparatus.value,
      suggestionMeta([t("matchingApparatuses"), resultLabel(apparatus.result_count)])
    )
  )), (item) => item.query || item.label);
  appendUniqueSuggestions(items, countries.slice(0, 3).map((country) => (
    facetSuggestion(
      country.label,
      country.value,
      suggestionMeta([t("country"), searchCountLabel(country)])
    )
  )), (item) => item.query || item.label);

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
    container.hidden = true;
    container.innerHTML = "";
    setSearchSuggestionsOpen(container, false);
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
    if (query.length < 2) {
      suggestions.hidden = true;
      suggestions.innerHTML = "";
      setSearchSuggestionsOpen(suggestions, false);
      return;
    }
    suggestions.innerHTML = `<div class="search-suggestion search-suggestion-status">${t("loading")}</div>`;
    suggestions.hidden = false;
    setSearchSuggestionsOpen(suggestions, true, 1);
    debounceTimer = window.setTimeout(async () => {
      const requestId = ++searchAutocompleteRequestId;
      try {
        const data = await getJson("/search/", { q: query, limit: 5 });
        if (requestId !== searchAutocompleteRequestId) return;
        renderSearchSuggestions(suggestions, buildSuggestionItems(data));
      } catch (_error) {
        if (requestId !== searchAutocompleteRequestId) return;
        suggestions.hidden = true;
        suggestions.innerHTML = "";
        setSearchSuggestionsOpen(suggestions, false);
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

function searchCountLabel(item) {
  const parts = [];
  if (item.result_count) parts.push(resultLabel(item.result_count));
  if (item.athlete_count) parts.push(`${item.athlete_count.toLocaleString()} ${t("navAthletes").toLowerCase()}`);
  return parts.join(" · ") || t("noResults");
}

function scoreLabel(value) {
  return value === null || value === undefined ? "not available" : Number(value).toFixed(3);
}

function componentValueLabel(value, status) {
  if (value !== null && value !== undefined) return Number(value).toFixed(3);
  if (status === "not_applicable") return "not applicable";
  return "not available";
}

function rankingScoreComposition(entry) {
  if ((entry.apparatus || "AA") === "AA") {
    const apparatusScores = entry.apparatus_scores || [];
    if (!apparatusScores.length) {
      return `<div class="score-composition muted-composition">Apparatus scores not available</div>`;
    }
    return `
      <div class="score-composition aa-composition" aria-label="AA apparatus scores">
        ${apparatusScores.map((component) => {
          const attempt = component.vt_attempt ? ` ${component.vt_attempt}` : "";
          return `
            <span class="score-component">
              <strong>${escapeHtml(`${component.apparatus}${attempt}`)}</strong>
              <span>${scoreLabel(component.score)}</span>
            </span>
          `;
        }).join("")}
      </div>
    `;
  }

  const eLabel = entry.execution_estimate === null || entry.execution_estimate === undefined
    ? componentValueLabel(entry.E_score, entry.e_score_status)
    : scoreLabel(entry.execution_estimate);
  const components = [
    ["D", componentValueLabel(entry.D_score)],
    ["E est.", eLabel],
    ["P", componentValueLabel(entry.Penalty, entry.penalty_status)],
    ["B", componentValueLabel(entry.Bonus, entry.bonus_status)],
  ];
  return `
    <div class="score-composition" aria-label="Score composition">
      ${components.map(([label, value]) => `
        <span class="score-component">
          <strong>${label}</strong>
          <span>${value}</span>
        </span>
      `).join("")}
    </div>
  `;
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
      { label: event.discipline, variant: "brand" },
      { label: event.category },
      { label: resultLabel(event.result_count) },
    ];
    const meta = [event.location, formatDateRange(event) || String(event.year)].filter(Boolean).join(" · ");
    return entityCard(event.name, meta, pills, `#/events/${event.id}`);
  });
  const countryItems = data.countries.map((country) => (
    entityCard(country.label, searchCountLabel(country), [{ label: t("country"), variant: "brand" }], `#/search?q=${encodeURIComponent(country.value)}`)
  ));
  const apparatusItems = data.apparatuses.map((apparatus) => (
    entityCard(apparatus.label, resultLabel(apparatus.result_count), [{ label: t("matchingApparatuses"), variant: "brand" }], `#/search?q=${encodeURIComponent(apparatus.value)}`)
  ));
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
          ${searchSection(t("matchingCountries"), countryItems)}
          ${searchSection(t("matchingApparatuses"), apparatusItems)}
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
      ${searchSection(t("matchingCountries"), countryItems)}
      ${searchSection(t("matchingApparatuses"), apparatusItems)}
      ${searchSection(t("matchingResults"), resultItems)}
    </div>
  `;
}

async function renderGlobalSearch() {
  const params = currentParams();
  const query = params.get("q") || "";
  const escapedQuery = escapeHtml(query);
  setApp(`
    ${pageHeading("globalSearchHeading", "globalSearchIntro")}
    <form class="search-form search-page-form" id="globalSearchPageForm">
      <input class="search-input" id="globalSearchPageInput" type="search" autocomplete="off" value="${escapedQuery}" placeholder="${t("searchPlaceholder")}">
      <button class="primary-button" type="submit">${t("search")}</button>
      <div class="search-suggestions" id="globalSearchPageSuggestions" role="listbox" hidden></div>
    </form>
    <div id="globalSearchResults">${query ? loadingState() : messageState(t("noGlobalSearchQuery"))}</div>
  `);
  $("#globalSearchPageForm").addEventListener("submit", (event) => {
    event.preventDefault();
    closeSearchSuggestions();
    const nextQuery = $("#globalSearchPageInput").value.trim();
    window.location.hash = nextQuery ? `#/search?q=${encodeURIComponent(nextQuery)}` : "#/search";
  });
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

function featureCard(title, text, href) {
  return `
    <a class="feature-card" href="${href}">
      <div>
        <h3>${title}</h3>
        <p>${text}</p>
      </div>
      <span class="feature-link">${t("open")}</span>
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

function multiFilterParam(type, scope = currentFilterScope()) {
  return filterValues(type, scope).join(",");
}

function singleFilterParam(type, scope = currentFilterScope()) {
  const values = filterValues(type, scope);
  return values.length === 1 ? values[0] : "";
}

function filterIsActive(type, value, scope = currentFilterScope(), activeValue = scopedFilters(scope)[type]) {
  if (scope === "rankings" && type === "scoringCycle") {
    const values = Array.isArray(activeValue) ? activeValue : (activeValue ? [activeValue] : []);
    if (values.includes("all")) return true;
    if (value === "all") return SCORING_CYCLE_FILTERS.every((cycle) => values.includes(cycle));
  }
  return Array.isArray(activeValue) ? activeValue.includes(value) : activeValue === value;
}

function rankingDiscipline() {
  return singleFilterParam("discipline", "rankings") || "MAG";
}

function rankingApparatusFilters() {
  return RANKING_APPARATUS_BY_DISCIPLINE[rankingDiscipline()] || [];
}

function calendarStatusParam() {
  return scopedFilters("events").calendarStatus || "";
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
  };
}

function rankingHasTimeFilter() {
  const filters = rankingTimeFilters();
  return Boolean(filters.startYear || filters.endYear || filters.startDate || filters.endDate);
}

function rankingWholeYearIsActive(year) {
  const filters = rankingTimeFilters();
  return filters.startYear === year && filters.endYear === year && !filters.startDate && !filters.endDate;
}

function rankingQueryParams(limit) {
  const scoringCycles = filterValues("scoringCycle", "rankings");
  const timeFilters = rankingTimeFilters();
  const params = {
    limit,
    discipline: rankingDiscipline(),
    category: rankingCategory(),
    apparatus: filterValues("apparatus", "rankings"),
  };
  if (timeFilters.startYear) params.start_year = timeFilters.startYear;
  if (timeFilters.endYear) params.end_year = timeFilters.endYear;
  if (timeFilters.startDate) params.start_date = timeFilters.startDate;
  if (timeFilters.endDate) params.end_date = timeFilters.endDate;
  if (rankingHasTimeFilter()) {
    return params;
  }
  if (scoringCycles.includes("all") || SCORING_CYCLE_FILTERS.every((cycle) => scoringCycles.includes(cycle))) {
    params.include_all_scoring_cycles = true;
  } else if (scoringCycles.length) {
    params.scoring_cycle = scoringCycles;
  }
  return params;
}

function calendarDateFromOffset(offset) {
  return new Date(TODAY.getFullYear(), TODAY.getMonth() + offset, 1);
}

function homeCalendarDate() {
  return calendarDateFromOffset(state.homeCalendarMonthOffset);
}

function eventsCalendarDate() {
  return calendarDateFromOffset(state.eventsCalendarMonthOffset);
}

function filterButton(label, type, value, scope = currentFilterScope()) {
  return `<button class="filter-button" type="button" data-filter-scope="${scope}" data-filter-type="${type}" data-filter-value="${value}" aria-pressed="${filterIsActive(type, value, scope)}">${label}</button>`;
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

function bindFilterButtons() {
  document.querySelectorAll("[data-filter-type]").forEach((button) => {
    button.addEventListener("click", () => {
      const scope = button.dataset.filterScope || currentFilterScope();
      const type = button.dataset.filterType;
      const value = button.dataset.filterValue;
      const filters = scopedFilters(scope);
      if (scope === "rankings" && type === "scoringCycle") {
        clearRankingTimeFilters();
        const values = filterValues(type, scope);
        if (value === "all") {
          filters[type] = values.includes("all") ? [] : ["all"];
        } else {
          const cycleValues = values.filter((item) => item !== "all");
          filters[type] = cycleValues.includes(value)
            ? cycleValues.filter((item) => item !== value)
            : [...cycleValues, value];
        }
        render();
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
      render();
    });
  });
}

function bindRankingDisciplineControl() {
  document.querySelectorAll("[data-ranking-discipline]").forEach((button) => {
    button.addEventListener("click", () => {
      scopedFilters("rankings").discipline = [button.dataset.rankingDiscipline];
      const allowedApparatuses = RANKING_APPARATUS_BY_DISCIPLINE[button.dataset.rankingDiscipline] || [];
      scopedFilters("rankings").apparatus = filterValues("apparatus", "rankings").filter((value) => (
        allowedApparatuses.includes(value)
      ));
      render();
    });
  });
}

function clearRankingTimeFilters() {
  Object.assign(scopedFilters("rankings"), {
    startYear: "",
    endYear: "",
    startDate: "",
    endDate: "",
  });
}

function setRankingYearFilter(year) {
  const filters = scopedFilters("rankings");
  if (rankingWholeYearIsActive(year)) {
    clearRankingTimeFilters();
  } else {
    Object.assign(filters, {
      startYear: year,
      endYear: year,
      startDate: "",
      endDate: "",
      scoringCycle: [],
    });
  }
  render();
}

function setRankingYearRange(startYear, endYear) {
  Object.assign(scopedFilters("rankings"), {
    startYear,
    endYear,
    startDate: "",
    endDate: "",
    scoringCycle: [],
  });
  render();
}

function setRankingDateRange(startDate, endDate) {
  Object.assign(scopedFilters("rankings"), {
    startYear: "",
    endYear: "",
    startDate,
    endDate,
    scoringCycle: [],
  });
  render();
}

function bindRankingTimeFilters() {
  document.querySelectorAll("[data-ranking-year]").forEach((button) => {
    button.addEventListener("click", () => setRankingYearFilter(button.dataset.rankingYear));
  });
  document.querySelectorAll("[data-ranking-clear-period]").forEach((button) => {
    button.addEventListener("click", () => {
      clearRankingTimeFilters();
      render();
    });
  });
  const startYear = $("#rankingStartYear");
  const endYear = $("#rankingEndYear");
  const startDate = $("#rankingStartDate");
  const endDate = $("#rankingEndDate");
  const applyYearRange = () => setRankingYearRange(startYear?.value.trim() || "", endYear?.value.trim() || "");
  const applyDateRange = () => setRankingDateRange(startDate?.value || "", endDate?.value || "");
  startYear?.addEventListener("change", applyYearRange);
  endYear?.addEventListener("change", applyYearRange);
  startDate?.addEventListener("change", applyDateRange);
  endDate?.addEventListener("change", applyDateRange);
}

async function hydrateHome() {
  try {
    const [rankings] = await Promise.all([
      getJson("/analytics/rankings", {
        limit: 60,
        discipline: "MAG",
      }),
      hydrateHomeCalendar(),
    ]);
    renderRankingList("#homeRankings", rankings);
    syncHomePreviewHeights();
  } catch (error) {
    $("#homeEvents").innerHTML = errorState(error);
    $("#homeRankings").innerHTML = errorState(error);
  }
}

async function hydrateHomeCalendar() {
  const calendarDate = homeCalendarDate();
  const monthStart = new Date(calendarDate.getFullYear(), calendarDate.getMonth(), 1);
  const monthEnd = new Date(calendarDate.getFullYear(), calendarDate.getMonth() + 1, 0);
  const events = await getJson("/events/calendar", {
    start_date: formatLocalIso(monthStart),
    end_date: formatLocalIso(monthEnd),
    as_of: formatLocalIso(TODAY),
    limit: 1000,
  });
  renderHomeCalendar("#homeEvents", events, calendarDate);
  requestAnimationFrame(syncHomePreviewHeights);
}

async function changeHomeCalendarMonth(delta) {
  state.homeCalendarMonthOffset += delta;
  try {
    await hydrateHomeCalendar();
  } catch (error) {
    $("#homeEvents").innerHTML = errorState(error);
  }
}

function syncHomePreviewHeights() {
  const calendarPanel = $("#homeCalendarPanel");
  const rankingPanel = $("#homeRankingPanel");
  const rankingScroll = $("#homeRankingScroll");
  if (!calendarPanel || !rankingPanel || !rankingScroll) return;

  rankingPanel.style.height = "";
  rankingScroll.style.maxHeight = "";

  const calendarHeight = calendarPanel.getBoundingClientRect().height;
  if (!calendarHeight) return;

  rankingPanel.style.height = `${Math.round(calendarHeight)}px`;
  const panelStyle = getComputedStyle(rankingPanel);
  const header = rankingPanel.querySelector(".section-header");
  const headerStyle = header ? getComputedStyle(header) : null;
  const headerHeight = header ? header.getBoundingClientRect().height : 0;
  const headerMargin = headerStyle ? parseFloat(headerStyle.marginBottom) || 0 : 0;
  const verticalPadding = (parseFloat(panelStyle.paddingTop) || 0) + (parseFloat(panelStyle.paddingBottom) || 0);
  const scrollHeight = Math.max(140, calendarHeight - verticalPadding - headerHeight - headerMargin);
  rankingScroll.style.maxHeight = `${Math.round(scrollHeight)}px`;
}

async function resetHomeCalendarMonth() {
  state.homeCalendarMonthOffset = 0;
  try {
    await hydrateHomeCalendar();
  } catch (error) {
    $("#homeEvents").innerHTML = errorState(error);
  }
}

async function hydrateEventsCalendar() {
  const calendarDate = eventsCalendarDate();
  const monthStart = new Date(calendarDate.getFullYear(), calendarDate.getMonth(), 1);
  const monthEnd = new Date(calendarDate.getFullYear(), calendarDate.getMonth() + 1, 0);
  const events = await getJson("/events/calendar", {
    start_date: formatLocalIso(monthStart),
    end_date: formatLocalIso(monthEnd),
    as_of: formatLocalIso(TODAY),
    limit: 1000,
    discipline: multiFilterParam("discipline", "events"),
    category: multiFilterParam("category", "events"),
    level: filterValues("level", "events"),
    status: calendarStatusParam(),
  });
  renderHomeCalendar("#eventResults", events, calendarDate, {
    navScope: "events",
    wrapperClass: "home-calendar full-calendar",
    maxVisibleLanes: 6,
  });
}

async function changeEventsCalendarMonth(delta) {
  state.eventsCalendarMonthOffset += delta;
  try {
    await hydrateEventsCalendar();
  } catch (error) {
    $("#eventResults").innerHTML = errorState(error);
  }
}

async function resetEventsCalendarMonth() {
  state.eventsCalendarMonthOffset = 0;
  try {
    await hydrateEventsCalendar();
  } catch (error) {
    $("#eventResults").innerHTML = errorState(error);
  }
}

function renderEventList(selector, events) {
  const node = $(selector);
  if (!events.length) {
    node.innerHTML = emptyState();
    return;
  }
  const displayEvents = events.filter((event) => (
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
  node.innerHTML = `<div class="entity-list">${displayEvents.map((event) => {
    const period = formatReadableDateRange(event);
    const meta = [
      period,
      event.location,
      event.venue,
    ].filter(Boolean).join(" · ");
    const pills = [
      { label: period, variant: "brand" },
      { label: event.discipline },
      { label: event.category },
      { label: event.level },
    ];
    if (event.is_calendar_only) {
      pills.push({ label: t("calendarOnly") });
    }
    return entityCard(event.name, meta, pills, event.id ? `#/events/${event.id}` : "");
  }).join("")}</div>`;
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

  node.innerHTML = `
    <div class="${wrapperClass}" aria-label="${escapeHtml(`${t("calendarMonth")} ${monthName}`)}">
      <div class="calendar-toolbar">
        <div class="calendar-title-row">
          <button class="calendar-nav-button" type="button" data-calendar-nav="-1" data-calendar-nav-scope="${navScope}" aria-label="${t("previousMonth")}" title="${t("previousMonth")}">&#8249;</button>
          <div class="calendar-title-label">
            <span class="calendar-kicker">${t("calendarMonth")}</span>
            <strong>${escapeHtml(monthTitle.month)}</strong>
            <span class="calendar-year">${escapeHtml(monthTitle.year)}</span>
          </div>
          <button class="calendar-nav-button" type="button" data-calendar-nav="1" data-calendar-nav-scope="${navScope}" aria-label="${t("nextMonth")}" title="${t("nextMonth")}">&#8250;</button>
          <button class="calendar-today-button" type="button" data-calendar-today-scope="${navScope}" aria-label="${t("today")}" title="${t("today")}">${t("today")}</button>
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
                    ? `data-today-label="${escapeHtml(t("today"))}" title="${escapeHtml(t("today"))}" tabindex="0"`
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
                  const title = [
                    event.name,
                    formatDateRange(event),
                    event.calendar_status,
                    event.is_calendar_only ? t("calendarOnly") : "",
                  ].filter(Boolean).join(" · ");
                  const element = `
                    <span class="calendar-event-label">${escapeHtml(event.name)}</span>
                  `;
                  const style = `grid-column: ${segment.startColumn} / ${segment.endColumn + 1}; grid-row: ${segment.lane + 1};`;
                  const className = `calendar-event-bar ${calendarStatusClass(event)}`;
                  return href
                    ? `<a class="${className}" href="${href}" style="${style}" title="${escapeHtml(title)}">${element}</a>`
                    : `<span class="${className}" style="${style}" title="${escapeHtml(title)}">${element}</span>`;
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
      const delta = Number(button.dataset.calendarNav || 0);
      if (button.dataset.calendarNavScope === "events") {
        changeEventsCalendarMonth(delta);
        return;
      }
      changeHomeCalendarMonth(delta);
    });
  });
  node.querySelectorAll("[data-calendar-today-scope]").forEach((button) => {
    button.addEventListener("click", () => {
      if (button.dataset.calendarTodayScope === "events") {
        resetEventsCalendarMonth();
        return;
      }
      resetHomeCalendarMonth();
    });
  });
}

function renderRankingContext(payload) {
  const parts = [];
  if (payload?.discipline) parts.push(payload.discipline);
  if (payload?.scoring_cycle?.label) {
    parts.push(`${t("scoringCycle")} ${payload.scoring_cycle.label}`);
  } else if (payload?.available_scoring_cycles?.length) {
    parts.push(`${t("scoringCycle")} ${payload.available_scoring_cycles.map((cycle) => cycle.label).join(", ")}`);
  }
  const warnings = payload?.warnings || [];
  if (!parts.length && !warnings.length) return "";
  return `
    <div class="context-note">
      ${parts.length ? `<span>${escapeHtml(parts.join(" · "))}</span>` : ""}
      ${warnings.map((warning) => `<span>${escapeHtml(warning)}</span>`).join("")}
    </div>
  `;
}

function renderRankingTimeFilter() {
  const filters = rankingTimeFilters();
  return `
    <details class="ranking-time-filter" ${rankingHasTimeFilter() ? "open" : ""}>
      <summary class="filter-button ranking-time-summary" aria-pressed="${rankingHasTimeFilter()}">${t("timeInterval")}</summary>
      <div class="ranking-time-panel">
        <div class="ranking-time-group">
          <span class="ranking-time-label">${t("wholeYear")}</span>
          <div class="ranking-year-grid">
            ${RANKING_YEAR_FILTERS.map((year) => `
              <button
                class="filter-button year-filter-button"
                type="button"
                data-ranking-year="${year}"
                aria-pressed="${rankingWholeYearIsActive(year)}"
              >${year}</button>
            `).join("")}
          </div>
        </div>
        <div class="ranking-time-inputs">
          <label>${t("fromYear")}<input id="rankingStartYear" type="number" inputmode="numeric" min="1900" max="2100" value="${escapeHtml(filters.startYear)}"></label>
          <label>${t("toYear")}<input id="rankingEndYear" type="number" inputmode="numeric" min="1900" max="2100" value="${escapeHtml(filters.endYear)}"></label>
          <label>${t("fromDate")}<input id="rankingStartDate" type="date" value="${escapeHtml(filters.startDate)}"></label>
          <label>${t("toDate")}<input id="rankingEndDate" type="date" value="${escapeHtml(filters.endDate)}"></label>
          <button class="quiet-button" type="button" data-ranking-clear-period>${t("clearPeriod")}</button>
        </div>
      </div>
    </details>
  `;
}

function renderRankingList(selector, payloadOrRankings) {
  const node = $(selector);
  const payload = Array.isArray(payloadOrRankings) ? { ranking: payloadOrRankings } : (payloadOrRankings || {});
  const rankings = payload.ranking || [];
  const context = renderRankingContext(payload);
  if (!rankings.length) {
    node.innerHTML = `${context}${emptyState()}`;
    return;
  }
  node.innerHTML = `${context}<div class="entity-list">${rankings.map((entry) => {
    const eventDate = entry.date ? formatReadableDate(entry.date) : "";
    const eventYear = entry.year ? `${t("eventYear")} ${entry.year}` : "";
    const meta = [
      entry.event_name,
      eventDate || eventYear,
      entry.country,
    ].filter(Boolean).join(" · ");
    const pills = [
      { label: `${t("score")} ${scoreLabel(entry.score)}`, variant: "brand" },
      { label: entry.apparatus || "AA" },
      { label: entry.discipline },
      ...(entry.year ? [{ label: String(entry.year) }] : []),
    ];
    const content = `
      <article class="entity-card ranking-card">
        <div class="entity-row">
          <h3>#${entry.computed_rank} ${escapeHtml(entry.athlete_name)}</h3>
        </div>
        <p class="meta">${escapeHtml(meta)}</p>
        <div class="pill-row">
          ${pills.map((pill) => `<span class="pill ${pill.variant || ""}">${escapeHtml(pill.label)}</span>`).join("")}
        </div>
        ${rankingScoreComposition(entry)}
      </article>
    `;
    return `<a href="#/athletes/${entry.athlete_id}">${content}</a>`;
  }).join("")}</div>`;
}

function athleteSearchRoute(query) {
  return query ? `/athletes?search=${encodeURIComponent(query)}` : "/athletes";
}

function syncAthleteSearchRoute(query) {
  const route = athleteSearchRoute(query);
  state.route = route;
  window.history.replaceState(null, "", `#${route}`);
  setActiveNav();
}

function renderAthleteCards(athletes) {
  if (!athletes.length) return emptyState();
  return `<div class="grid-3">${athletes.map((athlete) => {
    const pills = [
      { label: athlete.discipline, variant: "brand" },
      { label: athlete.country || t("country") },
      { label: `ID ${athlete.id}` },
      ...(athlete.birth_year ? [{ label: String(athlete.birth_year) }] : []),
    ];
    return entityCard(`${athlete.first_name} ${athlete.last_name}`, athlete.world_gymnastics_status || "Official profile pending", pills, `#/athletes/${athlete.id}`);
  }).join("")}</div>`;
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

function currentParams() {
  const [, query = ""] = state.route.split("?");
  return new URLSearchParams(query);
}

async function renderAthletes() {
  const params = currentParams();
  const search = params.get("search") || "";
  setApp(`
    ${pageHeading("athletesHeading", "athletesIntro")}
    <form class="toolbar" id="athleteSearchForm">
      <input class="search-input" id="athleteSearchInput" type="search" value="${escapeHtml(search)}" placeholder="${t("athleteSearchPlaceholder")}">
      <button class="primary-button" type="submit">${t("search")}</button>
      ${filterButton("MAG", "discipline", "MAG", "athletes")}
      ${filterButton("WAG", "discipline", "WAG", "athletes")}
      ${filterButton(t("junior"), "category", "junior", "athletes")}
      ${filterButton(t("senior"), "category", "senior", "athletes")}
    </form>
    <div class="athlete-results" id="athleteResults" aria-live="polite">${loadingState()}</div>
  `);
  bindFilterButtons();
  const form = $("#athleteSearchForm");
  const input = $("#athleteSearchInput");
  const resultsNode = $("#athleteResults");
  let searchTimer;
  const loadAthletes = async (query, options = {}) => {
    const { showLoading = false, updateRoute = false } = options;
    const requestId = ++athleteSearchRequestId;
    if (updateRoute) syncAthleteSearchRoute(query);
    if (showLoading) resultsNode.innerHTML = loadingState();
    resultsNode.classList.add("is-updating");
    resultsNode.setAttribute("aria-busy", "true");
    try {
      const athletes = await getJson("/athletes/", {
        search: query,
        discipline: singleFilterParam("discipline", "athletes"),
        category: filterValues("category", "athletes"),
        limit: 40,
      });
      if (requestId !== athleteSearchRequestId) return;
      resultsNode.innerHTML = renderAthleteCards(athletes);
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

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const query = input.value.trim();
    window.clearTimeout(searchTimer);
    loadAthletes(query, { showLoading: true, updateRoute: true });
  });
  input.addEventListener("input", () => {
    const query = input.value.trim();
    syncAthleteSearchRoute(query);
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => {
      loadAthletes(query);
    }, 140);
  });
  await loadAthletes(search, { showLoading: true });
}

async function renderEvents() {
  const params = currentParams();
  const search = params.get("search") || "";
  setApp(`
    ${pageHeading("eventsHeading", "eventsIntro")}
    <div class="toolbar">
      ${filterButton("MAG", "discipline", "MAG", "events")}
      ${filterButton("WAG", "discipline", "WAG", "events")}
      ${filterButton(t("senior"), "category", "senior", "events")}
      ${filterButton(t("junior"), "category", "junior", "events")}
      ${filterButton(t("completedWithResults"), "calendarStatus", "completed_with_results", "events")}
      ${filterButton(t("completedNoResults"), "calendarStatus", "completed_no_results", "events")}
      ${filterButton(t("ongoing"), "calendarStatus", "ongoing", "events")}
      ${filterButton(t("upcoming"), "calendarStatus", "upcoming", "events")}
    </div>
    <div class="toolbar secondary-toolbar">
      ${EVENT_LEVEL_FILTERS.map((level) => filterButton(level.label, "level", level.value, "events")).join("")}
    </div>
    <form class="search-form section-search-form" id="eventSearchForm">
      <input class="search-input" id="eventSearchInput" type="search" value="${escapeHtml(search)}" placeholder="${t("eventSearchPlaceholder")}">
      <button class="primary-button" type="submit">${t("search")}</button>
    </form>
    <section class="panel event-list-panel">
      <div class="section-header">
        <div>
          <h2>${t("eventListHeading")}</h2>
          <p>${t("eventListIntro")}</p>
        </div>
      </div>
      <div class="event-live-results" id="eventLiveResults" aria-live="polite">${loadingState()}</div>
    </section>
    <section class="panel calendar-page-panel">
      <div id="eventResults">${loadingState()}</div>
    </section>
  `);
  bindFilterButtons();
  const form = $("#eventSearchForm");
  const input = $("#eventSearchInput");
  const resultsNode = $("#eventLiveResults");
  let searchTimer;
  const loadEvents = async (query, options = {}) => {
    const { showLoading = false, updateRoute = false } = options;
    const requestId = ++eventSearchRequestId;
    if (updateRoute) syncEventSearchRoute(query);
    if (showLoading) resultsNode.innerHTML = loadingState();
    resultsNode.classList.add("is-updating");
    resultsNode.setAttribute("aria-busy", "true");
    try {
      const events = await getJson("/events/calendar", {
        search: query,
        discipline: filterValues("discipline", "events"),
        category: filterValues("category", "events"),
        level: filterValues("level", "events"),
        status: calendarStatusParam(),
        as_of: formatLocalIso(TODAY),
        limit: 80,
      });
      if (requestId !== eventSearchRequestId) return;
      renderEventList("#eventLiveResults", events);
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

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const query = input.value.trim();
    window.clearTimeout(searchTimer);
    loadEvents(query, { showLoading: true, updateRoute: true });
  });
  input.addEventListener("input", () => {
    const query = input.value.trim();
    syncEventSearchRoute(query);
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => {
      loadEvents(query);
    }, 140);
  });
  try {
    await Promise.all([
      hydrateEventsCalendar(),
      loadEvents(search, { showLoading: true }),
    ]);
  } catch (error) {
    $("#eventResults").innerHTML = errorState(error);
    $("#eventLiveResults").innerHTML = errorState(error);
  }
}

async function renderRankings() {
  const apparatusFilters = rankingApparatusFilters();
  setApp(`
    ${pageHeading("rankingsHeading", "rankingsIntro")}
    <div class="toolbar">
      ${disciplineSegmentedControl()}
      ${filterButton(t("senior"), "category", "senior", "rankings")}
      ${filterButton(t("junior"), "category", "junior", "rankings")}
    </div>
    <div class="toolbar secondary-toolbar" aria-label="${t("apparatus")}">
      ${apparatusFilters.map((apparatus) => filterButton(apparatus, "apparatus", apparatus, "rankings")).join("")}
    </div>
    <div class="toolbar secondary-toolbar">
      ${filterButton("2017-2021", "scoringCycle", "2017-2021", "rankings")}
      ${filterButton("2022-2024", "scoringCycle", "2022-2024", "rankings")}
      ${filterButton("2025-2028", "scoringCycle", "2025-2028", "rankings")}
      ${filterButton(t("allCycles"), "scoringCycle", "all", "rankings")}
    </div>
    ${renderRankingTimeFilter()}
    <div id="rankingResults">${loadingState()}</div>
  `);
  bindFilterButtons();
  bindRankingDisciplineControl();
  bindRankingTimeFilters();
  try {
    const rankings = await getJson("/analytics/rankings", {
      ...rankingQueryParams(60),
    });
    renderRankingList("#rankingResults", rankings);
  } catch (error) {
    $("#rankingResults").innerHTML = errorState(error);
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

function render() {
  normalizeRoute();
  setActiveNav();
  applyTranslations();
  if (state.route.startsWith("/athletes/")) {
    renderStaticPage("athletesHeading", "analyticsIntro");
  } else if (state.route.startsWith("/events/")) {
    renderStaticPage("eventsHeading", "eventsIntro");
  } else if (state.route.startsWith("/athletes")) {
    renderAthletes();
  } else if (state.route.startsWith("/events")) {
    renderEvents();
  } else if (state.route.startsWith("/rankings")) {
    renderRankings();
  } else if (state.route.startsWith("/search")) {
    renderGlobalSearch();
  } else if (state.route.startsWith("/analytics")) {
    renderStaticPage("analyticsHeading", "analyticsIntro");
  } else if (state.route.startsWith("/login")) {
    renderStaticPage("loginHeading", "loginIntro");
  } else {
    renderHome();
  }
}

function init() {
  setupIntroSplash();
  $("#apiBaseInput").value = state.apiBase;
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
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeLanguageMenu();
    }
  });
  $("#apiConfigForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const value = $("#apiBaseInput").value.trim().replace(/\/$/, "");
    if (value) {
      state.apiBase = value;
      localStorage.setItem(API_BASE_KEY, value);
      render();
    }
  });
  window.addEventListener("hashchange", render);
  window.addEventListener("resize", () => {
    syncHomePreviewHeights();
  });
  render();
}

init();
