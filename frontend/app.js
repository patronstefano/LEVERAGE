const API_BASE_KEY = "leverage.apiBase";
const LANGUAGE_KEY = "leverage.language";

const state = {
  route: "/",
  language: localStorage.getItem(LANGUAGE_KEY) || "en",
  apiBase: localStorage.getItem(API_BASE_KEY) || "http://localhost:8000",
  filters: {
    discipline: "",
    category: "",
  },
};
const CURRENT_YEAR = new Date().getFullYear();

const translations = {
  en: {
    navAthletes: "Athletes",
    navEvents: "Events",
    navRankings: "Rankings",
    navAnalytics: "Analytics",
    signIn: "Sign in",
    language: "Language",
    save: "Save",
    footerTagline: "Artistic Gymnastics Analytics",
    heroEyebrow: "Elite gymnastics, structured.",
    heroTitle: "LEVERAGE",
    heroSubtitle: "Artistic Gymnastics Analytics",
    heroBody: "Search athletes, events and rankings from a curated gymnastics database built for comparison, context and clarity.",
    searchPlaceholder: "Search athletes, events, countries...",
    search: "Search",
    systemStatus: "API status",
    online: "Online",
    offline: "Offline",
    startApi: "Start the FastAPI backend to load live data.",
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
    recentEvents: "Calendar preview",
    rankingPreview: "Ranking preview",
    viewAll: "View all",
    athletesHeading: "Athletes",
    athletesIntro: "Search the athlete database with discipline and country-aware filters.",
    eventsHeading: "Events",
    eventsIntro: "Calendar entries, completed competitions and upcoming events in one view.",
    rankingsHeading: "Rankings",
    rankingsIntro: "A first public ranking view powered by LEVERAGE analytics endpoints.",
    analyticsHeading: "Analytics",
    analyticsIntro: "The backend is ready for trends, comparisons, apparatus profiles and age analysis.",
    loginHeading: "Sign in",
    loginIntro: "User and admin areas will use the authentication system already implemented in the backend.",
    noResults: "No results found.",
    loading: "Loading...",
    discipline: "Discipline",
    category: "Category",
    all: "All",
    senior: "Senior",
    junior: "Junior",
    results: "results",
    result: "result",
    score: "Score",
    country: "Country",
    date: "Date",
    status: "Status",
    event: "Event",
    athlete: "Athlete",
    comingSoon: "Coming soon",
  },
  it: {
    navAthletes: "Atleti",
    navEvents: "Eventi",
    navRankings: "Classifiche",
    navAnalytics: "Analytics",
    signIn: "Accedi",
    language: "Lingua",
    save: "Salva",
    footerTagline: "Artistic Gymnastics Analytics",
    heroEyebrow: "Ginnastica elite, strutturata.",
    heroTitle: "LEVERAGE",
    heroSubtitle: "Artistic Gymnastics Analytics",
    heroBody: "Cerca atleti, eventi e classifiche in un database di ginnastica progettato per confronto, contesto e chiarezza.",
    searchPlaceholder: "Cerca atleti, eventi, nazioni...",
    search: "Cerca",
    systemStatus: "Stato API",
    online: "Online",
    offline: "Offline",
    startApi: "Avvia il backend FastAPI per caricare i dati live.",
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
    recentEvents: "Anteprima calendario",
    rankingPreview: "Anteprima classifica",
    viewAll: "Vedi tutto",
    athletesHeading: "Atleti",
    athletesIntro: "Cerca nel database atleti con filtri per disciplina e nazione.",
    eventsHeading: "Eventi",
    eventsIntro: "Calendario, competizioni concluse ed eventi futuri in una sola vista.",
    rankingsHeading: "Classifiche",
    rankingsIntro: "Prima vista pubblica delle classifiche basata sugli endpoint analytics.",
    analyticsHeading: "Analytics",
    analyticsIntro: "Il backend e pronto per trend, confronti, profili attrezzi e analisi eta.",
    loginHeading: "Accedi",
    loginIntro: "Le aree utente e admin useranno il sistema di autenticazione gia implementato.",
    noResults: "Nessun risultato trovato.",
    loading: "Caricamento...",
    discipline: "Disciplina",
    category: "Categoria",
    all: "Tutto",
    senior: "Senior",
    junior: "Junior",
    results: "risultati",
    result: "risultato",
    score: "Score",
    country: "Nazione",
    date: "Data",
    status: "Stato",
    event: "Evento",
    athlete: "Atleta",
    comingSoon: "In arrivo",
  },
  es: {
    navAthletes: "Atletas",
    navEvents: "Eventos",
    navRankings: "Rankings",
    navAnalytics: "Analitica",
    signIn: "Entrar",
    language: "Idioma",
    save: "Guardar",
    footerTagline: "Artistic Gymnastics Analytics",
    heroEyebrow: "Gimnasia elite, estructurada.",
    heroTitle: "LEVERAGE",
    heroSubtitle: "Artistic Gymnastics Analytics",
    heroBody: "Busca atletas, eventos y rankings en una base de datos de gimnasia creada para comparar con claridad.",
    searchPlaceholder: "Buscar atletas, eventos, paises...",
    search: "Buscar",
    systemStatus: "Estado API",
    online: "Online",
    offline: "Offline",
    startApi: "Inicia el backend FastAPI para cargar datos reales.",
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
    recentEvents: "Vista calendario",
    rankingPreview: "Vista rankings",
    viewAll: "Ver todo",
    athletesHeading: "Atletas",
    athletesIntro: "Busca atletas con filtros por disciplina y pais.",
    eventsHeading: "Eventos",
    eventsIntro: "Calendario, competiciones completadas y eventos futuros.",
    rankingsHeading: "Rankings",
    rankingsIntro: "Primera vista publica conectada a los endpoints analytics.",
    analyticsHeading: "Analitica",
    analyticsIntro: "El backend ya soporta tendencias, comparaciones y perfiles por aparato.",
    loginHeading: "Entrar",
    loginIntro: "Las areas de usuario y admin usaran el sistema de autenticacion ya implementado.",
    noResults: "No se encontraron resultados.",
    loading: "Cargando...",
    discipline: "Disciplina",
    category: "Categoria",
    all: "Todo",
    senior: "Senior",
    junior: "Junior",
    results: "resultados",
    result: "resultado",
    score: "Score",
    country: "Pais",
    date: "Fecha",
    status: "Estado",
    event: "Evento",
    athlete: "Atleta",
    comingSoon: "Proximamente",
  },
  fr: {
    navAthletes: "Athletes",
    navEvents: "Evenements",
    navRankings: "Classements",
    navAnalytics: "Analytique",
    signIn: "Connexion",
    language: "Langue",
    save: "Enregistrer",
    footerTagline: "Artistic Gymnastics Analytics",
    heroEyebrow: "Gymnastique elite, structuree.",
    heroTitle: "LEVERAGE",
    heroSubtitle: "Artistic Gymnastics Analytics",
    heroBody: "Recherchez athletes, evenements et classements dans une base de donnees concue pour comparer clairement.",
    searchPlaceholder: "Rechercher athletes, evenements, pays...",
    search: "Rechercher",
    systemStatus: "Statut API",
    online: "Online",
    offline: "Offline",
    startApi: "Lancez le backend FastAPI pour charger les donnees.",
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
    recentEvents: "Apercu calendrier",
    rankingPreview: "Apercu classement",
    viewAll: "Tout voir",
    athletesHeading: "Athletes",
    athletesIntro: "Recherchez dans la base avec filtres discipline et pays.",
    eventsHeading: "Evenements",
    eventsIntro: "Calendrier, competitions terminees et evenements futurs.",
    rankingsHeading: "Classements",
    rankingsIntro: "Premiere vue publique basee sur les endpoints analytics.",
    analyticsHeading: "Analytique",
    analyticsIntro: "Le backend supporte tendances, comparaisons et profils par appareil.",
    loginHeading: "Connexion",
    loginIntro: "Les espaces utilisateur et admin utiliseront l'authentification deja implementee.",
    noResults: "Aucun resultat.",
    loading: "Chargement...",
    discipline: "Discipline",
    category: "Categorie",
    all: "Tout",
    senior: "Senior",
    junior: "Junior",
    results: "resultats",
    result: "resultat",
    score: "Score",
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
    button.setAttribute("aria-selected", String(button.dataset.languageOption === state.language));
  });
}

function closeLanguageMenu() {
  const control = $("#languageControl");
  const button = $("#languageButton");
  if (!control || !button) return;
  control.classList.remove("is-open");
  button.setAttribute("aria-expanded", "false");
}

function apiUrl(path, params = {}) {
  const url = new URL(path, state.apiBase);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
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

function formatDateRange(item) {
  const start = item.start_date || "";
  const end = item.end_date || "";
  if (!start && !end) return "";
  if (start === end || !end) return start;
  return `${start} - ${end}`;
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
  document.querySelectorAll(".nav-links a").forEach((link) => {
    const route = link.getAttribute("href")?.replace("#", "");
    const active = route !== "/" && state.route.startsWith(route);
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

function errorState(error) {
  return `<div class="error-state">${t("startApi")} ${error ? `<br>${error.message}` : ""}</div>`;
}

function loadingState() {
  return `<div class="empty-state loading">${t("loading")}</div>`;
}

function emptyState() {
  return `<div class="empty-state">${t("noResults")}</div>`;
}

async function renderHome() {
  setApp(`
    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow">${t("heroEyebrow")}</p>
        <h1>${t("heroTitle")}</h1>
        <p class="hero-subtitle">${t("heroSubtitle")}</p>
        <p class="hero-subtitle">${t("heroBody")}</p>
        <div class="search-panel">
          <form class="search-form" id="globalSearchForm">
            <input class="search-input" id="globalSearchInput" type="search" autocomplete="off" placeholder="${t("searchPlaceholder")}">
            <button class="primary-button" type="submit">${t("search")}</button>
          </form>
          <div class="filter-row">
            ${filterButton("MAG", "discipline", "MAG")}
            ${filterButton("WAG", "discipline", "WAG")}
            ${filterButton(t("senior"), "category", "senior")}
            ${filterButton(t("junior"), "category", "junior")}
          </div>
        </div>
      </div>
      <aside class="hero-aside">
        <div class="snapshot" id="apiSnapshot">
          <div>
            <img class="snapshot-logo" src="./assets/leverage-logo.png" alt="">
            <h2>${t("exploreTitle")}</h2>
            <p>${t("exploreSubtitle")}</p>
          </div>
          <div class="status-line">
            <span><span class="status-dot" id="statusDot"></span>${t("systemStatus")}</span>
            <strong id="statusText">${t("loading")}</strong>
          </div>
        </div>
      </aside>
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

    <section class="section content-grid">
      <div class="panel">
        <div class="section-header">
          <h2>${t("recentEvents")}</h2>
          <a class="quiet-button" href="#/events">${t("viewAll")}</a>
        </div>
        <div id="homeEvents">${loadingState()}</div>
      </div>
      <div class="panel">
        <div class="section-header">
          <h2>${t("rankingPreview")}</h2>
          <a class="quiet-button" href="#/rankings">${t("viewAll")}</a>
        </div>
        <div id="homeRankings">${loadingState()}</div>
      </div>
    </section>
  `);

  $("#globalSearchForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const query = $("#globalSearchInput").value.trim();
    window.location.hash = query ? `#/athletes?search=${encodeURIComponent(query)}` : "#/athletes";
  });

  bindFilterButtons();
  await hydrateHome();
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

function filterButton(label, type, value) {
  return `<button class="filter-button" type="button" data-filter-type="${type}" data-filter-value="${value}" aria-pressed="${state.filters[type] === value}">${label}</button>`;
}

function bindFilterButtons() {
  document.querySelectorAll("[data-filter-type]").forEach((button) => {
    button.addEventListener("click", () => {
      const type = button.dataset.filterType;
      const value = button.dataset.filterValue;
      state.filters[type] = state.filters[type] === value ? "" : value;
      render();
    });
  });
}

async function hydrateHome() {
  try {
    const [events, rankings] = await Promise.all([
      getJson("/events/calendar", {
        year: CURRENT_YEAR,
        limit: 80,
        discipline: state.filters.discipline,
        category: state.filters.category,
      }),
      getJson("/analytics/rankings", {
        limit: 6,
        discipline: state.filters.discipline,
        category: state.filters.category,
      }),
    ]);
    $("#statusDot").className = "status-dot online";
    $("#statusText").textContent = t("online");
    renderEventList("#homeEvents", sortCalendarItems(events).slice(0, 6));
    renderRankingList("#homeRankings", rankings.ranking?.slice(0, 6) || []);
  } catch (error) {
    $("#statusDot").className = "status-dot offline";
    $("#statusText").textContent = t("offline");
    $("#homeEvents").innerHTML = errorState(error);
    $("#homeRankings").innerHTML = errorState(error);
  }
}

function renderEventList(selector, events) {
  const node = $(selector);
  if (!events.length) {
    node.innerHTML = emptyState();
    return;
  }
  node.innerHTML = `<div class="entity-list">${events.map((event) => {
    const pills = [
      { label: event.discipline },
      { label: event.category },
      { label: event.calendar_status, variant: event.has_results ? "success" : "warning" },
      { label: resultLabel(event.result_count) },
    ];
    return entityCard(event.name, [event.location, formatDateRange(event)].filter(Boolean).join(" · "), pills, `#/events/${event.id}`);
  }).join("")}</div>`;
}

function renderRankingList(selector, rankings) {
  const node = $(selector);
  if (!rankings.length) {
    node.innerHTML = emptyState();
    return;
  }
  node.innerHTML = `<div class="entity-list">${rankings.map((entry) => {
    const score = entry.score === null || entry.score === undefined ? "not available" : Number(entry.score).toFixed(3);
    const pills = [
      { label: `${t("score")} ${score}`, variant: "brand" },
      { label: entry.apparatus || "AA" },
      { label: entry.discipline },
    ];
    return entityCard(`#${entry.computed_rank} ${entry.athlete_name}`, `${entry.event_name} · ${entry.country || ""}`, pills, `#/athletes/${entry.athlete_id}`);
  }).join("")}</div>`;
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
      <input class="search-input" id="athleteSearchInput" type="search" value="${search}" placeholder="${t("searchPlaceholder")}">
      <button class="primary-button" type="submit">${t("search")}</button>
      ${filterButton("MAG", "discipline", "MAG")}
      ${filterButton("WAG", "discipline", "WAG")}
    </form>
    <div id="athleteResults">${loadingState()}</div>
  `);
  bindFilterButtons();
  $("#athleteSearchForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const query = $("#athleteSearchInput").value.trim();
    window.location.hash = query ? `#/athletes?search=${encodeURIComponent(query)}` : "#/athletes";
  });
  try {
    const athletes = await getJson("/athletes", {
      search,
      discipline: state.filters.discipline,
      limit: 40,
    });
    if (!athletes.length) {
      $("#athleteResults").innerHTML = emptyState();
      return;
    }
    $("#athleteResults").innerHTML = `<div class="grid-3">${athletes.map((athlete) => {
      const pills = [
        { label: athlete.discipline, variant: "brand" },
        { label: athlete.country || t("country") },
        ...(athlete.birth_year ? [{ label: String(athlete.birth_year) }] : []),
      ];
      return entityCard(`${athlete.first_name} ${athlete.last_name}`, athlete.world_gymnastics_status || "Official profile pending", pills, `#/athletes/${athlete.id}`);
    }).join("")}</div>`;
  } catch (error) {
    $("#athleteResults").innerHTML = errorState(error);
  }
}

async function renderEvents() {
  setApp(`
    ${pageHeading("eventsHeading", "eventsIntro")}
    <div class="toolbar">
      ${filterButton("MAG", "discipline", "MAG")}
      ${filterButton("WAG", "discipline", "WAG")}
      ${filterButton(t("senior"), "category", "senior")}
      ${filterButton(t("junior"), "category", "junior")}
    </div>
    <div id="eventResults">${loadingState()}</div>
  `);
  bindFilterButtons();
  try {
    const events = await getJson("/events/calendar", {
      year: CURRENT_YEAR,
      limit: 80,
      discipline: state.filters.discipline,
      category: state.filters.category,
    });
    renderEventList("#eventResults", sortCalendarItems(events));
  } catch (error) {
    $("#eventResults").innerHTML = errorState(error);
  }
}

async function renderRankings() {
  setApp(`
    ${pageHeading("rankingsHeading", "rankingsIntro")}
    <div class="toolbar">
      ${filterButton("MAG", "discipline", "MAG")}
      ${filterButton("WAG", "discipline", "WAG")}
      ${filterButton(t("senior"), "category", "senior")}
      ${filterButton(t("junior"), "category", "junior")}
    </div>
    <div id="rankingResults">${loadingState()}</div>
  `);
  bindFilterButtons();
  try {
    const rankings = await getJson("/analytics/rankings", {
      limit: 60,
      discipline: state.filters.discipline,
      category: state.filters.category,
    });
    renderRankingList("#rankingResults", rankings.ranking || []);
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
  } else if (state.route.startsWith("/analytics")) {
    renderStaticPage("analyticsHeading", "analyticsIntro");
  } else if (state.route.startsWith("/login")) {
    renderStaticPage("loginHeading", "loginIntro");
  } else {
    renderHome();
  }
}

function init() {
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
  render();
}

init();
