from collections import defaultdict
import re

from app.gymternet_import import COUNTRY_CODES, normalize_country_lookup_key


LOCALIZED_COUNTRY_ALIASES = {
    "afganistan": "AFG",
    "albanie": "ALB",
    "alemania": "GER",
    "algerie": "ALG",
    "allemagne": "GER",
    "arabia saudita": "KSA",
    "arabie saoudite": "KSA",
    "argelia": "ALG",
    "argentine": "ARG",
    "armenie": "ARM",
    "azerbaigian": "AZE",
    "azerbaiyan": "AZE",
    "azerbaijan": "AZE",
    "belgica": "BEL",
    "belgique": "BEL",
    "belgio": "BEL",
    "belice": "BIZ",
    "bielorussia": "BLR",
    "bielorrusia": "BLR",
    "bresil": "BRA",
    "brasil": "BRA",
    "brasile": "BRA",
    "bulgarie": "BUL",
    "camboya": "CAM",
    "camerun": "CMR",
    "cameroun": "CMR",
    "canada": "CAN",
    "cechia": "CZE",
    "chili": "CHI",
    "chine": "CHN",
    "chypre": "CYP",
    "cina": "CHN",
    "colombie": "COL",
    "corea del nord": "PRK",
    "corea del sur": "KOR",
    "corea del sud": "KOR",
    "coree du nord": "PRK",
    "coree du sud": "KOR",
    "costa d'avorio": "CIV",
    "costa de marfil": "CIV",
    "cote d'ivoire": "CIV",
    "croacia": "CRO",
    "croatie": "CRO",
    "croazia": "CRO",
    "danemark": "DEN",
    "danimarca": "DEN",
    "dinamarca": "DEN",
    "egipto": "EGY",
    "egypte": "EGY",
    "egitto": "EGY",
    "emirati arabi uniti": "UAE",
    "emiratos arabes unidos": "UAE",
    "emirats arabes unis": "UAE",
    "eslovaquia": "SVK",
    "eslovenia": "SLO",
    "espagne": "ESP",
    "espana": "ESP",
    "estados unidos": "USA",
    "etats unis": "USA",
    "etiopia": "ETH",
    "ethiopie": "ETH",
    "filippine": "PHI",
    "filipinas": "PHI",
    "finlandia": "FIN",
    "finlande": "FIN",
    "francia": "FRA",
    "francia": "FRA",
    "georgie": "GEO",
    "georgie": "GEO",
    "germania": "GER",
    "giappone": "JPN",
    "grande bretagna": "GBR",
    "grecia": "GRE",
    "grece": "GRE",
    "grecia": "GRE",
    "hong kong": "HKG",
    "hongrie": "HUN",
    "hungria": "HUN",
    "inde": "IND",
    "indie": "IND",
    "indonesia": "INA",
    "irak": "IRQ",
    "iran": "IRI",
    "irlanda": "IRL",
    "irlande": "IRL",
    "islanda": "ISL",
    "islande": "ISL",
    "israele": "ISR",
    "israel": "ISR",
    "italia": "ITA",
    "italie": "ITA",
    "italian": "ITA",
    "italiana": "ITA",
    "italiane": "ITA",
    "italiani": "ITA",
    "italiano": "ITA",
    "japon": "JPN",
    "kazajistan": "KAZ",
    "kazakistan": "KAZ",
    "kazakhstan": "KAZ",
    "lettonia": "LAT",
    "letonia": "LAT",
    "lettonie": "LAT",
    "libano": "LBN",
    "liban": "LBN",
    "lituania": "LTU",
    "lituanie": "LTU",
    "lituanie": "LTU",
    "lussemburgo": "LUX",
    "luxembourg": "LUX",
    "malesia": "MAS",
    "malaisie": "MAS",
    "marruecos": "MAR",
    "maroc": "MAR",
    "marocco": "MAR",
    "messico": "MEX",
    "mexique": "MEX",
    "moldavia": "MDA",
    "moldavie": "MDA",
    "mongolie": "MGL",
    "noruega": "NOR",
    "norvege": "NOR",
    "norvegia": "NOR",
    "nuova zelanda": "NZL",
    "nouvelle zelande": "NZL",
    "nueva zelanda": "NZL",
    "paesi bassi": "NED",
    "pais bas": "NED",
    "paises bajos": "NED",
    "palestina": "PLE",
    "palestine": "PLE",
    "paraguay": "PAR",
    "peru": "PER",
    "pologne": "POL",
    "polonia": "POL",
    "portogallo": "POR",
    "portugal": "POR",
    "puerto rico": "PUR",
    "qatar": "QAT",
    "reino unido": "GBR",
    "regno unito": "GBR",
    "republique tcheque": "CZE",
    "republique dominicaine": "DOM",
    "repubblica ceca": "CZE",
    "repubblica dominicana": "DOM",
    "republika ceca": "CZE",
    "republica checa": "CZE",
    "republica dominicana": "DOM",
    "roumanie": "ROU",
    "royaume uni": "GBR",
    "rumania": "ROU",
    "russie": "RUS",
    "russia": "RUS",
    "scozia": "SCO",
    "scotland": "SCO",
    "serbie": "SRB",
    "singapur": "SGP",
    "singapour": "SGP",
    "slovaquie": "SVK",
    "slovenie": "SLO",
    "spagna": "ESP",
    "stati uniti": "USA",
    "stati uniti d'america": "USA",
    "sudafrica": "RSA",
    "suecia": "SWE",
    "suede": "SWE",
    "sud africa": "RSA",
    "sudafrica": "RSA",
    "sud africa": "RSA",
    "svezia": "SWE",
    "svizzera": "SUI",
    "suisse": "SUI",
    "suiza": "SUI",
    "syrie": "SYR",
    "taipei cinese": "TPE",
    "taipei chino": "TPE",
    "taipei chinois": "TPE",
    "tailandia": "THA",
    "thailande": "THA",
    "turchia": "TUR",
    "turquie": "TUR",
    "ucraina": "UKR",
    "ukraine": "UKR",
    "ungheria": "HUN",
    "uruguay": "URU",
    "uzbekistan": "UZB",
    "venezuela": "VEN",
    "vietnam": "VIE",
}


def country_search_key(value: str) -> str:
    normalized = normalize_country_lookup_key(value)
    return re.sub(r"[^a-z0-9]+", " ", normalized).strip()


def normalized_country_aliases() -> dict[str, str]:
    aliases: dict[str, str] = {}
    for source in (COUNTRY_CODES, LOCALIZED_COUNTRY_ALIASES):
        for alias, code in source.items():
            aliases[str(alias).strip().lower()] = code
            aliases[normalize_country_lookup_key(str(alias))] = code
            aliases[country_search_key(str(alias))] = code
    for code in set(aliases.values()):
        aliases[code.lower()] = code
    return aliases


COUNTRY_ALIAS_CODES = normalized_country_aliases()


def country_aliases_by_code() -> dict[str, set[str]]:
    aliases: dict[str, set[str]] = defaultdict(set)
    for alias, code in COUNTRY_ALIAS_CODES.items():
        aliases[code].add(alias)
    return aliases


COUNTRY_ALIASES_BY_CODE = country_aliases_by_code()


def resolve_exact_country_codes(query: str) -> set[str]:
    lookup_values = {
        query.strip().lower(),
        normalize_country_lookup_key(query),
        country_search_key(query),
    }
    return {
        COUNTRY_ALIAS_CODES[value]
        for value in lookup_values
        if value and value in COUNTRY_ALIAS_CODES
    }


def resolve_country_codes(query: str) -> set[str]:
    codes = resolve_exact_country_codes(query)
    normalized_query = f" {country_search_key(query)} "
    for alias, code in COUNTRY_ALIAS_CODES.items():
        normalized_alias = country_search_key(alias)
        if normalized_alias and f" {normalized_alias} " in normalized_query:
            codes.add(code)
    return codes


def resolve_country_terms(country_codes: set[str]) -> set[str]:
    terms = set(country_codes)
    for code in country_codes:
        terms.update(COUNTRY_ALIASES_BY_CODE.get(code, set()))
    return {term for term in terms if term}
