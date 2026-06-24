from __future__ import annotations

import csv
import hashlib
import re
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass, replace
from difflib import SequenceMatcher
from io import BytesIO, StringIO
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.i18n import translate
from app.result_identity import result_identity_key


MAG_APPARATUS = {"FX", "PH", "SR", "VT", "PB", "HB"}
WAG_APPARATUS = {"VT", "UB", "BB", "FX"}
AA_ALIASES = {"AA", "ALL AROUND", "ALL-AROUND", "ALLAROUND", "TOTAL"}
VT_AVG_ALIASES = {"VT AVG", "VT AVERAGE", "VAULT AVG", "VAULT AVERAGE"}
VT_SUM_ALIASES = {"VT SUM"}
GYMTERNET_POST_2025_COMPONENT_WARNING = (
    "Gymternet legacy import detected results after 2025: 2025 vault and missing-component "
    "rules are applied. Missing E_score, Penalty and Bonus remain not available. "
    "Prefer a dedicated standard import when explicit score components are available."
)

MEET_SUFFIX_MAP = {
    "QF": (models.RoundEnum.QUALIFICATION, models.FormatEnum.INDIVIDUAL),
    "TF": (models.RoundEnum.FINAL, models.FormatEnum.TEAM),
    "AA": (models.RoundEnum.FINAL, models.FormatEnum.INDIVIDUAL),
    "EF": (models.RoundEnum.FINAL, models.FormatEnum.APPARATUS),
}

EVENT_LEVEL_MAP = {
    "olympic games": models.LevelEnum.OLYMPIC_GAMES,
    "olympics": models.LevelEnum.OLYMPIC_GAMES,
    "world championships": models.LevelEnum.WORLD_CHAMPIONSHIPS,
    "worlds": models.LevelEnum.WORLD_CHAMPIONSHIPS,
    "continental championships": models.LevelEnum.CONTINENTAL_CHAMPIONSHIPS,
    "european championships": models.LevelEnum.CONTINENTAL_CHAMPIONSHIPS,
    "asian championships": models.LevelEnum.CONTINENTAL_CHAMPIONSHIPS,
    "pan american championships": models.LevelEnum.CONTINENTAL_CHAMPIONSHIPS,
    "african championships": models.LevelEnum.CONTINENTAL_CHAMPIONSHIPS,
    "world challenge cup": models.LevelEnum.WORLD_CHALLENGE_CUP,
    "challenge cup": models.LevelEnum.WORLD_CHALLENGE_CUP,
    "world cup": models.LevelEnum.WORLD_CUP,
}

SHEET_NAMES = {
    (models.DisciplineEnum.MAG, "final"): "MAG",
    (models.DisciplineEnum.MAG, "dscore"): "MAG D",
    (models.DisciplineEnum.WAG, "final"): "WAG",
    (models.DisciplineEnum.WAG, "dscore"): "WAG D",
}

COUNTRY_CODES = {
    "albania": "ALB",
    "algeria": "ALG",
    "angola": "ANG",
    "andorra": "AND",
    "argentina": "ARG",
    "armenia": "ARM",
    "australia": "AUS",
    "austria": "AUT",
    "azerbaijan": "AZE",
    "bangladesh": "BAN",
    "aruba": "ARU",
    "barbados": "BAR",
    "belarus": "BLR",
    "belgium": "BEL",
    "belglium": "BEL",
    "bermuda": "BER",
    "bolivia": "BOL",
    "bosnia & herzegovina": "BIH",
    "bosnia and herzegovina": "BIH",
    "bosnia": "BIH",
    "brazil": "BRA",
    "bulgaria": "BUL",
    "cambodia": "CAM",
    "cameroon": "CMR",
    "canada": "CAN",
    "cayman islands": "CAY",
    "chad": "CHA",
    "chile": "CHI",
    "china": "CHN",
    "chinese taipei": "TPE",
    "colombia": "COL",
    "costa rica": "CRC",
    "croatia": "CRO",
    "cuba": "CUB",
    "cyprus": "CYP",
    "czech republic": "CZE",
    "czechia": "CZE",
    "denmark": "DEN",
    "dominican republic": "DOM",
    "ecuador": "ECU",
    "egypt": "EGY",
    "el salvador": "ESA",
    "estonia": "EST",
    "ethiopia": "ETH",
    "faroe islands": "FAR",
    "fiinland": "FIN",
    "finland": "FIN",
    "france": "FRA",
    "georgia": "GEO",
    "germany": "GER",
    "great britain": "GBR",
    "greece": "GRE",
    "guatemala": "GUA",
    "haiti": "HAI",
    "hong kong": "HKG",
    "honduras": "HON",
    "hungary": "HUN",
    "hungarian": "HUN",
    "iceland": "ISL",
    "india": "IND",
    "indonesia": "INA",
    "iran": "IRI",
    "ireland": "IRL",
    "iraq": "IRQ",
    "israel": "ISR",
    "italy": "ITA",
    "jamaica": "JAM",
    "japan": "JPN",
    "jordan": "JOR",
    "kazakhstan": "KAZ",
    "kosovo": "KOS",
    "kuwait": "KUW",
    "kyrgyzstan": "KGZ",
    "latvia": "LAT",
    "lebanon": "LBN",
    "liechtenstein": "LIE",
    "libya": "LBA",
    "lithuania": "LTU",
    "luxembourg": "LUX",
    "macedonia": "MKD",
    "malaysia": "MAS",
    "malta": "MLT",
    "mauritius": "MRI",
    "mexico": "MEX",
    "moldova": "MDA",
    "monaco": "MON",
    "mongolia": "MGL",
    "montenegro": "MNE",
    "morocco": "MAR",
    "myanmar": "MYA",
    "namibia": "NAM",
    "netherlands": "NED",
    "new zealand": "NZL",
    "nicaragua": "NCA",
    "nigeria": "NGR",
    "north korea": "PRK",
    "north macedonia": "MKD",
    "norway": "NOR",
    "pakistan": "PAK",
    "palestine": "PLE",
    "panama": "PAN",
    "paraguay": "PAR",
    "peru": "PER",
    "philippines": "PHI",
    "philppines": "PHI",
    "poland": "POL",
    "portugal": "POR",
    "puerto rico": "PUR",
    "qatar": "QAT",
    "romania": "ROU",
    "russia": "RUS",
    "saudi arabia": "KSA",
    "scotland": "SCO",
    "senegal": "SEN",
    "serbia": "SRB",
    "seychelles": "SEY",
    "singapore": "SGP",
    "slovakia": "SVK",
    "slovkia": "SVK",
    "slovenia": "SLO",
    "south africa": "RSA",
    "south korea": "KOR",
    "spain": "ESP",
    "sri lanka": "SRI",
    "sweden": "SWE",
    "switzerland": "SUI",
    "syria": "SYR",
    "thailand": "THA",
    "trinidad & tobago": "TTO",
    "trinidad and tobago": "TTO",
    "tunisia": "TUN",
    "turkiye": "TUR",
    "turkey": "TUR",
    "ita": "ITA",
    "ukraine": "UKR",
    "united arab emirates": "UAE",
    "united kingdom": "GBR",
    "united states": "USA",
    "united states of america": "USA",
    "usa": "USA",
    "uzbekistan": "UZB",
    "venezuela": "VEN",
    "vietnam": "VIE",
    "uruguay": "URU",
    "yemen": "YEM",
    "zimbabwe": "ZIM",
    "taiwan": "TPE",
}


@dataclass(frozen=True)
class ParsedGymternetResult:
    source_sheet: str
    source_row: int
    event_name: str
    year: int
    athlete_name: str
    first_name: str
    last_name: str
    country: Optional[str]
    discipline: models.DisciplineEnum
    category: models.ResultCategoryEnum
    apparatus: str
    vt_attempt: Optional[int]
    format: models.FormatEnum
    round: models.RoundEnum
    score: Optional[float]
    day: Optional[int] = None
    D_score: Optional[float] = None
    vault_attempt_order_uncertain: bool = False

    @property
    def import_key(self) -> tuple:
        return (
            self.event_name.lower(),
            self.year,
            self.athlete_name.lower(),
            self.discipline.value,
            self.category.value,
            self.apparatus,
            self.format.value,
            self.round.value,
            self.vt_attempt,
            self.day,
        )


@dataclass
class GymternetParseOutput:
    records: list[ParsedGymternetResult]
    issues: list[dict]
    orphan_dscore_records: list[ParsedGymternetResult] | None = None


def parse_gymternet_file(
    filename: str,
    content: bytes,
    year_hint: Optional[int] = None,
    csv_discipline: Optional[models.DisciplineEnum] = None,
    csv_score_kind: Optional[str] = None,
) -> GymternetParseOutput:
    suffix = Path(filename).suffix.lower()
    if suffix == ".xlsx":
        parsed = parse_xlsx(filename, content, year_hint)
    elif suffix == ".csv":
        parsed = parse_csv(filename, content, year_hint, csv_discipline, csv_score_kind)
    else:
        return GymternetParseOutput(
            records=[],
            issues=[{"severity": "error", "message": "Only .xlsx and .csv files are supported"}],
        )
    records = assign_automatic_days(parsed.records, parsed.issues)
    append_post_2025_policy_warning(records, parsed.issues)
    return GymternetParseOutput(
        records=records,
        issues=parsed.issues,
        orphan_dscore_records=parsed.orphan_dscore_records or [],
    )


def append_post_2025_policy_warning(
    records: list[ParsedGymternetResult],
    issues: list[dict],
) -> None:
    if any(record.year > 2025 for record in records):
        issues.append({
            "severity": "warning",
            "message": GYMTERNET_POST_2025_COMPONENT_WARNING,
        })


def parse_xlsx(filename: str, content: bytes, year_hint: Optional[int]) -> GymternetParseOutput:
    workbook = read_xlsx_workbook(content)
    issues = []
    final_records = []
    dscore_records = []
    fallback_year = year_hint or infer_year(filename, None)

    for discipline in (models.DisciplineEnum.MAG, models.DisciplineEnum.WAG):
        final_sheet = find_sheet(workbook, [SHEET_NAMES[(discipline, "final")]])
        dscore_sheet = find_sheet(workbook, [SHEET_NAMES[(discipline, "dscore")]])
        if not final_sheet:
            issues.append({
                "severity": "warning",
                "message": f"No final-score sheet found for {discipline.value}",
            })
            continue
        final_records.extend(parse_pivot_rows(
            workbook[final_sheet],
            final_sheet,
            discipline,
            "final",
            fallback_year,
            issues,
        ))
        if dscore_sheet:
            dscore_records.extend(parse_pivot_rows(
                workbook[dscore_sheet],
                dscore_sheet,
                discipline,
                "dscore",
                fallback_year,
                issues,
            ))

    records, orphan_dscore_records = merge_final_and_dscore(final_records, dscore_records, issues)
    return GymternetParseOutput(
        records=records,
        issues=issues,
        orphan_dscore_records=orphan_dscore_records,
    )


def parse_csv(
    filename: str,
    content: bytes,
    year_hint: Optional[int],
    csv_discipline: Optional[models.DisciplineEnum],
    csv_score_kind: Optional[str],
) -> GymternetParseOutput:
    text = content.decode("utf-8-sig")
    rows = list(csv.DictReader(StringIO(text)))
    if not rows:
        return GymternetParseOutput(records=[], issues=[{"severity": "error", "message": "CSV is empty"}])

    headers = {normalize_header(header) for header in rows[0].keys()}
    if {"discipline", "athlete", "event", "apparatus", "score"}.issubset(headers):
        return parse_flat_csv(filename, rows, year_hint)

    discipline = csv_discipline or infer_csv_discipline(filename)
    score_kind = (csv_score_kind or infer_csv_score_kind(filename) or "final").lower()
    if not discipline:
        return GymternetParseOutput(
            records=[],
            issues=[{"severity": "error", "message": "CSV pivot import requires discipline=MAG or WAG"}],
        )
    if score_kind not in {"final", "dscore"}:
        return GymternetParseOutput(
            records=[],
            issues=[{"severity": "error", "message": "CSV score_kind must be final or dscore"}],
        )

    issues = []
    parsed = parse_pivot_rows(rows, filename, discipline, score_kind, year_hint, issues)
    records, orphan_dscore_records = merge_final_and_dscore(parsed, [], issues) if score_kind == "final" else ([], parsed)
    if score_kind == "dscore":
        issues.append({"severity": "warning", "message": "D-score CSV alone has no final-score rows to import"})
    return GymternetParseOutput(
        records=records,
        issues=issues,
        orphan_dscore_records=orphan_dscore_records,
    )


def parse_flat_csv(filename: str, rows: list[dict], year_hint: Optional[int]) -> GymternetParseOutput:
    issues = []
    records = []
    for row_number, row in enumerate(rows, start=2):
        normalized = {normalize_header(key): value for key, value in row.items()}
        try:
            discipline = models.DisciplineEnum(str(normalized["discipline"]).strip().upper())
            category = parse_category(normalized.get("category"), normalized["athlete"])[0]
            event_name, suffix, event_day = parse_event(normalized["event"])
            year = infer_year(event_name, year_hint) or infer_year(filename, None) or 0
            round_value = parse_round(normalized.get("round"))
            format_value = parse_format(normalized.get("format"))
            if not round_value or not format_value:
                round_value, format_value = suffix_round_format(suffix)
            explicit_day = parse_day(normalized.get("day"))
            athlete_name, first_name, last_name, category_from_name = normalize_athlete_name(normalized["athlete"])
            if category_from_name == models.ResultCategoryEnum.JUNIOR:
                category = category_from_name
            apparatus = normalize_apparatus(normalized.get("apparatus"))
            vt_attempt = parse_int(normalized.get("vt_attempt"))
            vault_attempt_order_uncertain = False
            if apparatus == "VT" and vt_attempt is None and should_label_vault_as_attempt_one(year, discipline):
                vt_attempt = 1
                vault_attempt_order_uncertain = True
            records.append(ParsedGymternetResult(
                source_sheet=filename,
                source_row=row_number,
                event_name=event_name,
                year=year,
                athlete_name=athlete_name,
                first_name=first_name,
                last_name=last_name,
                country=normalize_country(normalized.get("country"), issues, filename, row_number),
                discipline=discipline,
                category=category,
                apparatus=apparatus,
                vt_attempt=vt_attempt,
                format=format_value,
                round=round_value,
                score=normalize_score(normalized.get("score")),
                day=explicit_day if explicit_day is not None else event_day,
                D_score=normalize_optional_score(
                    normalized.get("d score")
                ),
                vault_attempt_order_uncertain=vault_attempt_order_uncertain,
            ))
        except Exception as exc:
            issues.append({
                "severity": "error",
                "sheet": filename,
                "row": row_number,
                "message": f"Could not parse flat CSV row: {exc}",
            })
    return GymternetParseOutput(records=records, issues=issues, orphan_dscore_records=[])


def read_xlsx_workbook(content: bytes) -> dict[str, list[dict]]:
    ns = {
        "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    rel_ns = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}
    workbook = {}
    with ZipFile(BytesIO(content)) as archive:
        shared_strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("a:si", ns):
                shared_strings.append("".join(text.text or "" for text in item.findall(".//a:t", ns)))

        wb_root = ET.fromstring(archive.read("xl/workbook.xml"))
        rel_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rid_to_target = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rel_root.findall("rel:Relationship", rel_ns)
        }
        for sheet in wb_root.findall(".//a:sheet", ns):
            name = sheet.attrib["name"]
            rid = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target = rid_to_target[rid]
            if not target.startswith("xl/"):
                target = "xl/" + target
            workbook[name] = read_xlsx_sheet(archive, target, shared_strings, ns)
    return workbook


def read_xlsx_sheet(archive: ZipFile, target: str, shared_strings: list[str], ns: dict) -> list[dict]:
    root = ET.fromstring(archive.read(target))
    rows = []
    header = None
    for row in root.findall(".//a:sheetData/a:row", ns):
        cells = {}
        max_idx = -1
        for cell in row.findall("a:c", ns):
            ref = cell.attrib.get("r", "A1")
            idx = column_index(ref)
            max_idx = max(max_idx, idx)
            value = read_cell_value(cell, shared_strings, ns)
            cells[idx] = value
        values = [cells.get(index, "") for index in range(max_idx + 1)]
        if header is None:
            header = [str(value).strip() for value in values]
            continue
        if any(value not in ("", None) for value in values):
            rows.append({
                header[index]: values[index] if index < len(values) else ""
                for index in range(len(header))
                if header[index]
            })
    return rows


def column_index(cell_ref: str) -> int:
    letters = re.match(r"([A-Z]+)", cell_ref).group(1)
    value = 0
    for letter in letters:
        value = value * 26 + ord(letter) - ord("A") + 1
    return value - 1


def read_cell_value(cell, shared_strings: list[str], ns: dict):
    cell_type = cell.attrib.get("t")
    value = cell.find("a:v", ns)
    if value is None:
        return ""
    if cell_type == "s":
        return shared_strings[int(value.text)]
    return value.text or ""


def is_repeated_pivot_header_row(normalized: dict) -> bool:
    athlete = str(normalized.get("athlete") or normalized.get("name") or normalized.get("atleta") or "").strip().lower()
    country = str(normalized.get("country") or "").strip().lower()
    event = str(normalized.get("event") or "").strip().lower()
    return athlete in {"athlete", "name", "atleta"} and country in {"country", "nation"} and event in {"event", "meet"}


def parse_pivot_rows(
    rows: list[dict],
    sheet_name: str,
    discipline: models.DisciplineEnum,
    score_kind: str,
    year_hint: Optional[int],
    issues: list[dict],
) -> list[ParsedGymternetResult]:
    records = []
    for row_number, row in enumerate(rows, start=2):
        normalized = {normalize_header(key): value for key, value in row.items()}
        if is_repeated_pivot_header_row(normalized):
            continue
        athlete_raw = normalized.get("athlete") or normalized.get("name") or normalized.get("atleta")
        event_raw = normalized.get("event")
        if not athlete_raw or not event_raw:
            continue
        athlete_name, first_name, last_name, category = normalize_athlete_name(athlete_raw)
        event_name, suffix, event_day = parse_event(str(event_raw))
        year = infer_year(event_name, year_hint) or 0
        round_value, base_format = suffix_round_format(suffix)
        explicit_day = parse_day(normalized.get("day"))
        record_day = explicit_day if explicit_day is not None else event_day
        country = normalize_country(
            normalized.get("country"),
            issues,
            sheet_name,
            row_number,
        )

        score_columns = extract_score_columns(normalized, discipline)
        vt_score = score_columns.get("VT")
        vt_avg = score_columns.get("VT AVG")
        vt_sum = score_columns.get("VT SUM")
        label_vault_attempts = should_label_vault_as_attempt_one(year, discipline)
        derive_vt2_final_score = should_derive_vt2_final_score(year, discipline)
        derive_vt2_d_score = should_derive_vt2_d_score(year, discipline)
        create_missing_vt2_final_score = should_create_missing_vt2_final_score(year, discipline)

        for apparatus in sorted((MAG_APPARATUS if discipline == models.DisciplineEnum.MAG else WAG_APPARATUS) - {"VT"}):
            add_record_if_score(
                records,
                sheet_name,
                row_number,
                event_name,
                year,
                athlete_name,
                first_name,
                last_name,
                country,
                discipline,
                category,
                apparatus,
                None,
                base_format,
                round_value,
                score_columns.get(apparatus),
                score_kind,
                day=record_day,
            )

        add_record_if_score(
            records,
            sheet_name,
            row_number,
            event_name,
            year,
            athlete_name,
            first_name,
            last_name,
            country,
            discipline,
            category,
            "VT",
            1 if label_vault_attempts else None,
            base_format,
            round_value,
            vt_score,
            score_kind,
            day=record_day,
            vault_attempt_order_uncertain=label_vault_attempts,
        )
        if vt_avg is not None:
            add_record_if_score(
                records,
                sheet_name,
                row_number,
                event_name,
                year,
                athlete_name,
                first_name,
                last_name,
                country,
                discipline,
                category,
                "VT AVG",
                None,
                base_format,
                round_value,
                vt_avg,
                score_kind,
                day=record_day,
            )
            if derive_vt2_final_score and vt_score is not None and score_kind == "final":
                add_record_if_score(
                    records,
                    sheet_name,
                    row_number,
                    event_name,
                    year,
                    athlete_name,
                    first_name,
                    last_name,
                    country,
                    discipline,
                    category,
                    "VT",
                    2,
                    base_format,
                    round_value,
                    round(vt_avg * 2 - vt_score, 3),
                    score_kind,
                    day=record_day,
                    vault_attempt_order_uncertain=True,
                )
            if create_missing_vt2_final_score and vt_score is not None and score_kind == "final":
                add_record(
                    records,
                    sheet_name,
                    row_number,
                    event_name,
                    year,
                    athlete_name,
                    first_name,
                    last_name,
                    country,
                    discipline,
                    category,
                    "VT",
                    2,
                    base_format,
                    round_value,
                    None,
                    None,
                    day=record_day,
                    vault_attempt_order_uncertain=True,
                )
        if derive_vt2_d_score and vt_sum is not None and vt_score is not None and score_kind == "dscore":
            add_record_if_score(
                records,
                sheet_name,
                row_number,
                event_name,
                year,
                athlete_name,
                first_name,
                last_name,
                country,
                discipline,
                category,
                "VT",
                2,
                base_format,
                round_value,
                round(vt_sum - vt_score, 3),
                score_kind,
                day=record_day,
                vault_attempt_order_uncertain=True,
            )

        aa_value = score_columns.get("AA")
        if aa_value is not None and should_import_aa(suffix):
            add_record_if_score(
                records,
                sheet_name,
                row_number,
                event_name,
                year,
                athlete_name,
                first_name,
                last_name,
                country,
                discipline,
                category,
                "AA",
                None,
                models.FormatEnum.INDIVIDUAL,
                round_value,
                aa_value,
                score_kind,
                day=record_day,
            )
    return records


def add_record_if_score(
    records: list[ParsedGymternetResult],
    sheet_name: str,
    row_number: int,
    event_name: str,
    year: int,
    athlete_name: str,
    first_name: str,
    last_name: str,
    country: Optional[str],
    discipline: models.DisciplineEnum,
    category: models.ResultCategoryEnum,
    apparatus: str,
    vt_attempt: Optional[int],
    format_value: models.FormatEnum,
    round_value: models.RoundEnum,
    raw_score,
    score_kind: str,
    day: Optional[int] = None,
    vault_attempt_order_uncertain: bool = False,
) -> None:
    score = normalize_optional_score(raw_score)
    if score is None:
        return
    final_score = score if score_kind == "final" else None
    d_score = score if score_kind == "dscore" and apparatus != "VT AVG" else None
    add_record(
        records,
        sheet_name,
        row_number,
        event_name,
        year,
        athlete_name,
        first_name,
        last_name,
        country,
        discipline,
        category,
        apparatus,
        vt_attempt,
        format_value,
        round_value,
        final_score,
        d_score,
        day=day,
        vault_attempt_order_uncertain=vault_attempt_order_uncertain,
    )


def add_record(
    records: list[ParsedGymternetResult],
    sheet_name: str,
    row_number: int,
    event_name: str,
    year: int,
    athlete_name: str,
    first_name: str,
    last_name: str,
    country: Optional[str],
    discipline: models.DisciplineEnum,
    category: models.ResultCategoryEnum,
    apparatus: str,
    vt_attempt: Optional[int],
    format_value: models.FormatEnum,
    round_value: models.RoundEnum,
    score: Optional[float],
    D_score: Optional[float],
    day: Optional[int] = None,
    vault_attempt_order_uncertain: bool = False,
) -> None:
    records.append(ParsedGymternetResult(
        source_sheet=sheet_name,
        source_row=row_number,
        event_name=event_name,
        year=year,
        athlete_name=athlete_name,
        first_name=first_name,
        last_name=last_name,
        country=country,
        discipline=discipline,
        category=category,
        apparatus=apparatus,
        vt_attempt=vt_attempt,
        format=format_value,
        round=round_value,
        day=day,
        score=score,
        D_score=D_score,
        vault_attempt_order_uncertain=vault_attempt_order_uncertain,
    ))


def merge_final_and_dscore(
    final_records: list[ParsedGymternetResult],
    dscore_records: list[ParsedGymternetResult],
    issues: list[dict],
) -> tuple[list[ParsedGymternetResult], list[ParsedGymternetResult]]:
    dscore_lookup = {record.import_key: record.D_score for record in dscore_records}
    dscore_uncertainty_lookup = {
        record.import_key: record.vault_attempt_order_uncertain
        for record in dscore_records
    }
    merged = []
    matched_dscore_keys = set()
    for record in final_records:
        d_score = None if record.apparatus == "VT AVG" else dscore_lookup.get(record.import_key)
        if record.score is None and d_score is None:
            continue
        if d_score is not None:
            matched_dscore_keys.add(record.import_key)
        merged.append(ParsedGymternetResult(
            source_sheet=record.source_sheet,
            source_row=record.source_row,
            event_name=record.event_name,
            year=record.year,
            athlete_name=record.athlete_name,
            first_name=record.first_name,
            last_name=record.last_name,
            country=record.country,
            discipline=record.discipline,
            category=record.category,
            apparatus=record.apparatus,
            vt_attempt=record.vt_attempt,
            format=record.format,
            round=record.round,
            score=record.score,
            day=record.day,
            D_score=d_score,
            vault_attempt_order_uncertain=(
                record.vault_attempt_order_uncertain
                or dscore_uncertainty_lookup.get(record.import_key, False)
            ),
        ))
    orphan_lookup = {
        record.import_key: record
        for record in dscore_records
        if record.import_key not in matched_dscore_keys
    }
    orphan_dscore_records = list(orphan_lookup.values())
    if orphan_dscore_records:
        issues.append({
            "severity": "warning",
            "message": f"{len(orphan_dscore_records)} D-score rows did not match a final-score row and need admin review",
        })
    return merged, orphan_dscore_records


def extract_score_columns(normalized: dict, discipline: models.DisciplineEnum) -> dict[str, Optional[float]]:
    columns = {}
    for key, value in normalized.items():
        normalized_key = key.upper()
        if normalized_key in (MAG_APPARATUS if discipline == models.DisciplineEnum.MAG else WAG_APPARATUS):
            columns[normalized_key] = normalize_optional_score(value)
        elif normalized_key in AA_ALIASES:
            columns["AA"] = normalize_optional_score(value)
        elif normalized_key in VT_AVG_ALIASES:
            columns["VT AVG"] = normalize_optional_score(value)
        elif normalized_key in VT_SUM_ALIASES:
            columns["VT SUM"] = normalize_optional_score(value)
    return columns


def split_event_suffix(event: str) -> tuple[str, Optional[str]]:
    parts = event.rsplit(None, 1)
    if len(parts) == 2 and parts[1].upper() in MEET_SUFFIX_MAP:
        return parts[0].strip(), parts[1].upper()
    return event, None


def split_event_day_marker(event: str) -> tuple[str, Optional[int]]:
    match = re.search(r"\s*(?:[-–—,]\s*)?\(?\bday\s*(\d{1,2})\b\)?\s*$", event, flags=re.IGNORECASE)
    if not match:
        return event, None
    day = int(match.group(1))
    if day < 1:
        return event, None
    cleaned = event[:match.start()].strip(" -–—,()")
    return cleaned.strip(), day


def parse_event(event_raw: str) -> tuple[str, Optional[str], Optional[int]]:
    event = str(event_raw).strip()
    event, suffix = split_event_suffix(event)
    event, day = split_event_day_marker(event)
    if suffix is None:
        event, suffix = split_event_suffix(event)
    return event, suffix, day


def suffix_round_format(suffix: Optional[str]) -> tuple[models.RoundEnum, models.FormatEnum]:
    if suffix in MEET_SUFFIX_MAP:
        return MEET_SUFFIX_MAP[suffix]
    return models.RoundEnum.FINAL, models.FormatEnum.INDIVIDUAL


def should_import_aa(suffix: Optional[str]) -> bool:
    return suffix in {None, "QF", "AA"}


def should_label_vault_as_attempt_one(year: int, discipline: models.DisciplineEnum) -> bool:
    return year > 0


def should_derive_vt2_final_score(year: int, discipline: models.DisciplineEnum) -> bool:
    return 0 < year < 2025 or (year >= 2025 and discipline == models.DisciplineEnum.MAG)


def should_derive_vt2_d_score(year: int, discipline: models.DisciplineEnum) -> bool:
    return year > 0


def should_create_missing_vt2_final_score(year: int, discipline: models.DisciplineEnum) -> bool:
    return year >= 2025 and discipline == models.DisciplineEnum.WAG


def normalize_athlete_name(name_raw) -> tuple[str, str, str, models.ResultCategoryEnum]:
    raw = str(name_raw).strip()
    category = models.ResultCategoryEnum.JUNIOR if "*" in raw else models.ResultCategoryEnum.SENIOR
    clean = re.sub(r"\s*\*+\s*$", "", raw).strip()
    parts = clean.split()
    if not parts:
        return "Unknown", "Unknown", "", category
    if len(parts) == 1:
        return parts[0], parts[0], "", category
    return clean, " ".join(parts[:-1]), parts[-1], category


def parse_category(value, athlete_name) -> tuple[models.ResultCategoryEnum, str]:
    if value:
        normalized = str(value).strip().lower()
        if normalized in {"junior", "jr", "j"}:
            return models.ResultCategoryEnum.JUNIOR, ""
        if normalized in {"senior", "sr", "s"}:
            return models.ResultCategoryEnum.SENIOR, ""
    _, _, _, category = normalize_athlete_name(athlete_name)
    return category, ""


def normalize_country_lookup_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    return "".join(character for character in normalized if not unicodedata.combining(character))


def normalize_country(value, issues: list[dict], source: str, row_number: int) -> Optional[str]:
    if value is None or str(value).strip() == "":
        return None
    raw = str(value).strip().rstrip("*").strip()
    if re.fullmatch(r"[A-Z]{3}", raw):
        return raw
    code = COUNTRY_CODES.get(raw.lower()) or COUNTRY_CODES.get(normalize_country_lookup_key(raw))
    if code:
        return code
    fallback = raw.upper()
    issues.append({
        "severity": "warning",
        "sheet": source,
        "row": row_number,
        "message": f"Unknown country mapping for '{raw}', using '{fallback}'",
    })
    return fallback


def normalize_header(value) -> str:
    return str(value).strip().lower().replace("-", " ").replace("_", " ")


def normalize_apparatus(value) -> str:
    normalized = str(value).strip().upper()
    if normalized in VT_AVG_ALIASES:
        return "VT AVG"
    if normalized in AA_ALIASES:
        return "AA"
    return normalized


def normalize_score(value) -> float:
    score = normalize_optional_score(value)
    if score is None:
        raise ValueError("score is required")
    return score


def normalize_optional_score(value) -> Optional[float]:
    if value is None:
        return None
    raw = str(value).strip()
    if raw == "" or raw.lower() == "nan":
        return None
    try:
        score = float(raw)
    except ValueError:
        return None
    if score < 0:
        return None
    return round(score, 3)


def parse_int(value) -> Optional[int]:
    if value is None or str(value).strip() == "":
        return None
    return int(float(str(value).strip()))


def parse_day(value) -> Optional[int]:
    day = parse_int(value)
    if day is not None and day < 1:
        raise ValueError("day must be greater than or equal to 1")
    return day


def parse_round(value) -> Optional[models.RoundEnum]:
    if not value:
        return None
    raw = str(value).strip().lower()
    aliases = {"qf": "qualification", "qual": "qualification", "qualification": "qualification", "final": "final", "f": "final"}
    return models.RoundEnum(aliases.get(raw, raw))


def parse_format(value) -> Optional[models.FormatEnum]:
    if not value:
        return None
    raw = str(value).strip().lower()
    aliases = {"aa": "individual", "ind": "individual", "individual": "individual", "team": "team", "apparatus": "apparatus", "ef": "apparatus"}
    return models.FormatEnum(aliases.get(raw, raw))


def infer_event_level(event_name: str) -> models.LevelEnum:
    lower = event_name.strip().lower()
    for key, level in EVENT_LEVEL_MAP.items():
        if key in lower:
            return level
    return models.LevelEnum.INTERNATIONAL_EVENT


def infer_year(text: str, fallback: Optional[int]) -> Optional[int]:
    match = re.search(r"\b(20\d{2})\b", str(text))
    return int(match.group(1)) if match else fallback


def infer_csv_discipline(filename: str) -> Optional[models.DisciplineEnum]:
    upper = filename.upper()
    if "WAG" in upper:
        return models.DisciplineEnum.WAG
    if "MAG" in upper:
        return models.DisciplineEnum.MAG
    return None


def infer_csv_score_kind(filename: str) -> Optional[str]:
    lower = filename.lower()
    if "d score" in lower or "dscore" in lower or " d " in lower:
        return "dscore"
    if "top" in lower or "final" in lower:
        return "final"
    return None


def find_sheet(workbook: dict[str, list[dict]], candidates: list[str]) -> Optional[str]:
    available = {name.strip().lower(): name for name in workbook}
    for candidate in candidates:
        found = available.get(candidate.strip().lower())
        if found:
            return found
    return None


def event_discipline_for(existing: Optional[models.Event], incoming: models.DisciplineEnum) -> models.EventDisciplineEnum:
    incoming_event_discipline = (
        models.EventDisciplineEnum.MAG if incoming == models.DisciplineEnum.MAG else models.EventDisciplineEnum.WAG
    )
    if not existing or existing.discipline == incoming_event_discipline:
        return incoming_event_discipline
    return models.EventDisciplineEnum.MAG_AND_WAG


def event_category_for(existing: Optional[models.Event], incoming: models.ResultCategoryEnum) -> models.EventCategoryEnum:
    incoming_event_category = (
        models.EventCategoryEnum.JUNIOR if incoming == models.ResultCategoryEnum.JUNIOR else models.EventCategoryEnum.SENIOR
    )
    if not existing or existing.category == incoming_event_category:
        return incoming_event_category
    return models.EventCategoryEnum.JUNIOR_AND_SENIOR


def score_equal(left: Optional[float], right: Optional[float]) -> bool:
    if left is None and right is None:
        return True
    if left is None or right is None:
        return False
    return abs(left - right) < 0.001


def country_equal(left: Optional[str], right: Optional[str]) -> bool:
    return (left or "").strip().upper() == (right or "").strip().upper()


def result_represented_country(result: models.Result) -> Optional[str]:
    return result.represented_country or (result.athlete.country if result.athlete else None)


def dayless_import_key(record: ParsedGymternetResult) -> tuple:
    return (
        record.event_name.lower(),
        record.year,
        record.athlete_name.lower(),
        record.discipline.value,
        record.category.value,
        record.apparatus,
        record.format.value,
        record.round.value,
        record.vt_attempt,
    )


def score_variant_key(record: ParsedGymternetResult) -> tuple:
    return (record.score, record.D_score)


def stable_id(prefix: str, parts: tuple) -> str:
    raw = "|".join("" if part is None else str(part) for part in parts)
    return f"{prefix}_{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:16]}"


def orphan_review_id(record: ParsedGymternetResult) -> str:
    return stable_id(
        "orphan",
        (
            record.source_sheet,
            record.source_row,
            record.event_name,
            record.year,
            record.athlete_name,
            record.country,
            record.discipline.value,
            record.category.value,
            record.apparatus,
            record.vt_attempt,
            record.format.value,
            record.round.value,
            record.day,
            record.D_score,
        ),
    )


def target_record_id(record: ParsedGymternetResult) -> str:
    return stable_id(
        "target",
        (
            record.event_name,
            record.year,
            record.athlete_name,
            record.discipline.value,
            record.category.value,
            record.apparatus,
            record.vt_attempt,
            record.format.value,
            record.round.value,
            record.day,
            record.score,
        ),
    )


def suggestion_id(orphan: ParsedGymternetResult, target: ParsedGymternetResult, suggestion_type: str) -> str:
    return stable_id(
        "suggestion",
        (
            orphan_review_id(orphan),
            target_record_id(target),
            suggestion_type,
        ),
    )


def athlete_match_review_id(record: ParsedGymternetResult) -> str:
    return stable_id(
        "athlete_match",
        (
            record.athlete_name,
            record.first_name,
            record.last_name,
            record.country,
            record.discipline.value,
        ),
    )


def athlete_match_suggestion_id(review_id: str, athlete: models.Athlete) -> str:
    return stable_id(
        "suggestion",
        (
            review_id,
            athlete.id,
            "existing_athlete_match",
        ),
    )


def athlete_country_change_review_id(record: ParsedGymternetResult, athlete: models.Athlete) -> str:
    return stable_id(
        "athlete_country",
        (
            athlete.id,
            athlete.country,
            record.country,
            record.discipline.value,
        ),
    )


def normalized_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, left.lower(), right.lower()).ratio()


def athlete_full_name(athlete: models.Athlete) -> str:
    return f"{athlete.first_name} {athlete.last_name}".strip()


def athlete_name_similarity(record: ParsedGymternetResult, athlete: models.Athlete) -> float:
    imported = record.athlete_name.strip()
    existing = athlete_full_name(athlete)
    existing_reversed = f"{athlete.last_name} {athlete.first_name}".strip()
    return max(
        normalized_similarity(imported, existing),
        normalized_similarity(imported, existing_reversed),
        normalized_similarity(f"{record.first_name} {record.last_name}", existing),
    )


def athlete_payload(athlete: models.Athlete) -> dict:
    return {
        "athlete_id": athlete.id,
        "first_name": athlete.first_name,
        "last_name": athlete.last_name,
        "athlete_name": athlete_full_name(athlete),
        "country": athlete.country,
        "discipline": athlete.discipline.value,
        "birth_year": athlete.birth_year,
    }


def athlete_country_differs(record: ParsedGymternetResult, athlete: models.Athlete) -> bool:
    return bool(record.country and athlete.country and record.country != athlete.country)


def record_athlete_country_change(
    db: Session,
    athlete: models.Athlete,
    to_country: str,
    change_year: int,
    from_country: Optional[str] = None,
) -> bool:
    previous_country = from_country if from_country is not None else athlete.country
    if not to_country or previous_country == to_country:
        return False

    existing = db.query(models.AthleteCountryChange).filter(
        models.AthleteCountryChange.athlete_id == athlete.id,
        models.AthleteCountryChange.from_country == previous_country,
        models.AthleteCountryChange.to_country == to_country,
        models.AthleteCountryChange.change_year == change_year,
    ).first()
    if not existing:
        db.add(models.AthleteCountryChange(
            athlete_id=athlete.id,
            from_country=previous_country,
            to_country=to_country,
            change_year=change_year,
        ))

    athlete.country = to_country
    return True


def name_token(value: Optional[str]) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").lower())


def athlete_candidate_keys(first_name: str, last_name: str, country: Optional[str]) -> set[tuple]:
    first = name_token(first_name)
    last = name_token(last_name)
    keys = set()
    if first and last:
        keys.add(("initials", first[0], last[0]))
        keys.add(("initials", last[0], first[0]))
    if first:
        keys.add(("first", first))
        keys.add(("last", first))
    if last:
        keys.add(("first", last))
        keys.add(("last", last))
    if country:
        keys.add(("country", country))
    return keys


def imported_athlete_payload(record: ParsedGymternetResult, result_count: int) -> dict:
    return {
        "athlete_name": record.athlete_name,
        "first_name": record.first_name,
        "last_name": record.last_name,
        "country": record.country,
        "discipline": record.discipline.value,
        "year": record.year,
        "result_count": result_count,
    }


def target_payload(record: ParsedGymternetResult) -> dict:
    payload = import_record_payload(record)
    payload["target_id"] = target_record_id(record)
    return payload


def target_label(record: ParsedGymternetResult) -> str:
    parts = [
        record.athlete_name,
        f"{record.event_name} {record.year}",
        record.apparatus,
        record.round.value,
        record.format.value,
        f"score {record.score if record.score is not None else 'not available'}",
    ]
    if record.vt_attempt is not None:
        parts.insert(3, f"attempt {record.vt_attempt}")
    if record.day is not None:
        parts.insert(3, f"day {record.day}")
    return " - ".join(parts)


def target_search_text(record: ParsedGymternetResult) -> str:
    values = [
        record.athlete_name,
        record.first_name,
        record.last_name,
        record.country,
        record.event_name,
        record.year,
        record.discipline.value,
        record.category.value,
        record.apparatus,
        record.vt_attempt,
        record.day,
        record.format.value,
        record.round.value,
        record.score,
        record.D_score,
        record.source_sheet,
        record.source_row,
    ]
    return " ".join("" if value is None else str(value) for value in values).lower()


def target_query_score(record: ParsedGymternetResult, query: Optional[str]) -> float:
    if not query or not query.strip():
        return 0.0
    text = target_search_text(record)
    normalized_query = query.strip().lower()
    tokens = [token for token in re.split(r"\s+", normalized_query) if token]
    if not tokens:
        return 0.0
    token_score = sum(1 for token in tokens if token in text) / len(tokens)
    return max(token_score, normalized_similarity(normalized_query, text))


def target_context_score(record: ParsedGymternetResult, review_item: Optional[dict]) -> float:
    if not review_item or "orphan_dscore" not in review_item:
        return 0.0
    orphan = review_item["orphan_dscore"]
    score = 0.0
    if record.event_name.lower() == str(orphan.get("event_name", "")).lower():
        score += 0.22
    if record.year == orphan.get("year"):
        score += 0.08
    if record.athlete_name.lower() == str(orphan.get("athlete_name", "")).lower():
        score += 0.22
    if record.discipline.value == orphan.get("discipline"):
        score += 0.08
    if record.category.value == orphan.get("category"):
        score += 0.08
    if record.apparatus == orphan.get("apparatus"):
        score += 0.12
    if record.vt_attempt == orphan.get("vt_attempt"):
        score += 0.05
    if record.format.value == orphan.get("format"):
        score += 0.05
    if record.round.value == orphan.get("round"):
        score += 0.05
    if record.day == orphan.get("day"):
        score += 0.05
    return min(score, 1.0)


def import_target_suggestion_payload(record: ParsedGymternetResult, confidence: float) -> dict:
    payload = target_payload(record)
    payload["label"] = target_label(record)
    payload["confidence"] = round(min(confidence, 1.0), 3)
    return payload


def find_import_target_suggestions(
    records: list[ParsedGymternetResult],
    query: Optional[str] = None,
    review_item: Optional[dict] = None,
    limit: int = 10,
) -> list[dict]:
    scored = []
    has_query = bool(query and query.strip())
    for record in records:
        query_score = target_query_score(record, query)
        context_score = target_context_score(record, review_item)
        confidence = (query_score * 0.6) + (context_score * 0.4) if has_query else context_score
        if has_query and query_score < 0.2 and context_score < 0.5:
            continue
        if not has_query and review_item is None:
            confidence = 0.0
        scored.append((confidence, record.source_sheet, record.source_row, record))

    scored.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [
        import_target_suggestion_payload(record, confidence)
        for confidence, _, _, record in scored[:limit]
    ]


def build_orphan_suggestion(
    orphan: ParsedGymternetResult,
    target: ParsedGymternetResult,
    suggestion_type: str,
    confidence: float,
    message: str,
    changes: dict,
) -> dict:
    return {
        "suggestion_id": suggestion_id(orphan, target, suggestion_type),
        "suggestion_type": suggestion_type,
        "confidence": round(confidence, 3),
        "message": message,
        "action": "attach_d_score_to_target_result",
        "changes": changes,
        "target_result": target_payload(target),
    }


def build_orphan_review_items(
    orphan_dscore_records: list[ParsedGymternetResult],
    final_records: list[ParsedGymternetResult],
) -> list[dict]:
    review_items = []

    for orphan in orphan_dscore_records:
        suggestions = []

        same_context = [
            record for record in final_records
            if record.event_name == orphan.event_name
            and record.year == orphan.year
            and record.discipline == orphan.discipline
            and record.category == orphan.category
            and record.apparatus == orphan.apparatus
            and record.vt_attempt == orphan.vt_attempt
            and record.format == orphan.format
            and record.round == orphan.round
            and record.day == orphan.day
        ]
        best_athlete_match = best_record_match(
            same_context,
            orphan.athlete_name,
            lambda record: record.athlete_name,
        )
        if best_athlete_match and best_athlete_match[1] >= 0.88:
            target, confidence = best_athlete_match
            suggestions.append(build_orphan_suggestion(
                orphan,
                target,
                "athlete_name_correction",
                confidence,
                (
                    f"D-score athlete '{orphan.athlete_name}' probably matches "
                    f"score-sheet athlete '{target.athlete_name}'."
                ),
                {"athlete_name": {"from": orphan.athlete_name, "to": target.athlete_name}},
            ))

        same_athlete_context = [
            record for record in final_records
            if record.athlete_name == orphan.athlete_name
            and record.discipline == orphan.discipline
            and record.category == orphan.category
            and record.apparatus == orphan.apparatus
            and record.vt_attempt == orphan.vt_attempt
            and record.format == orphan.format
            and record.round == orphan.round
            and record.day == orphan.day
        ]
        best_event_match = best_record_match(
            same_athlete_context,
            orphan.event_name,
            lambda record: record.event_name,
        )
        if best_event_match and best_event_match[1] >= 0.88:
            target, confidence = best_event_match
            suggestions.append(build_orphan_suggestion(
                orphan,
                target,
                "event_name_correction",
                confidence,
                (
                    f"D-score event '{orphan.event_name}' may match "
                    f"score-sheet event '{target.event_name}'."
                ),
                {"event_name": {"from": orphan.event_name, "to": target.event_name}},
            ))

        same_athlete_event_apparatus = [
            record for record in final_records
            if record.event_name == orphan.event_name
            and record.year == orphan.year
            and record.athlete_name == orphan.athlete_name
            and record.discipline == orphan.discipline
            and record.category == orphan.category
            and record.apparatus == orphan.apparatus
            and record.vt_attempt == orphan.vt_attempt
        ]
        for target in same_athlete_event_apparatus[:3]:
            if target.format != orphan.format or target.round != orphan.round or target.day != orphan.day:
                suggestions.append(build_orphan_suggestion(
                    orphan,
                    target,
                    "context_correction",
                    0.65,
                    (
                        "Same athlete/event/apparatus exists in the score sheet, "
                        "but format, round, or day is different."
                    ),
                    {
                        "format": {"from": orphan.format.value, "to": target.format.value},
                        "round": {"from": orphan.round.value, "to": target.round.value},
                        "day": {"from": orphan.day, "to": target.day},
                    },
                ))

        problem_type, message = classify_orphan_problem(orphan, final_records, suggestions)
        review_items.append({
            "review_id": orphan_review_id(orphan),
            "problem_type": problem_type,
            "severity": "review",
            "message": message,
            "orphan_dscore": import_record_payload(orphan),
            "suggestions": unique_suggestions(suggestions)[:5],
            "allowed_actions": ["accept_suggestion", "discard", "manual_target"],
        })

    return review_items


def best_record_match(records: list[ParsedGymternetResult], value: str, getter) -> Optional[tuple[ParsedGymternetResult, float]]:
    best = None
    best_ratio = 0.0
    for record in records:
        ratio = normalized_similarity(value, getter(record))
        if ratio > best_ratio:
            best = record
            best_ratio = ratio
    if best is None:
        return None
    return best, best_ratio


def unique_suggestions(suggestions: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for suggestion in sorted(suggestions, key=lambda item: item["confidence"], reverse=True):
        key = suggestion["suggestion_id"]
        if key in seen:
            continue
        seen.add(key)
        unique.append(suggestion)
    return unique


def classify_orphan_problem(
    orphan: ParsedGymternetResult,
    final_records: list[ParsedGymternetResult],
    suggestions: list[dict],
) -> tuple[str, str]:
    if suggestions:
        first_type = unique_suggestions(suggestions)[0]["suggestion_type"]
        if first_type == "athlete_name_correction":
            return "possible_athlete_name_typo", "Possible athlete-name typo between the D sheet and the score sheet."
        if first_type == "event_name_correction":
            return "possible_event_name_mismatch", "Possible event-name mismatch between the D sheet and the score sheet."
        return "possible_context_mismatch", "Possible format, round, or day mismatch."

    same_athlete_event = [
        record for record in final_records
        if record.event_name == orphan.event_name
        and record.year == orphan.year
        and record.athlete_name == orphan.athlete_name
        and record.discipline == orphan.discipline
        and record.category == orphan.category
    ]
    if same_athlete_event:
        return "missing_final_score_for_context", "The athlete/event exists, but not this apparatus/context."

    same_event_context = [
        record for record in final_records
        if record.event_name == orphan.event_name
        and record.year == orphan.year
        and record.discipline == orphan.discipline
        and record.category == orphan.category
        and record.apparatus == orphan.apparatus
        and record.vt_attempt == orphan.vt_attempt
        and record.format == orphan.format
        and record.round == orphan.round
        and record.day == orphan.day
    ]
    if same_event_context:
        return "athlete_missing_in_score_sheet", "The event/apparatus/context exists, but this athlete is missing in the score sheet."

    return "missing_score_sheet_context", "No matching final-score result is available in the score sheet."


def result_target_key(record: ParsedGymternetResult) -> tuple:
    return (
        record.event_name.lower(),
        record.year,
        record.athlete_name.lower(),
        record.discipline.value,
        record.category.value,
        record.apparatus,
        record.vt_attempt,
        record.format.value,
        record.round.value,
        record.day,
    )


def manual_target_key(target: dict) -> tuple:
    return (
        str(target["event_name"]).lower(),
        int(target["year"]),
        str(target["athlete_name"]).lower(),
        str(target["discipline"]),
        str(target["category"]),
        target.get("apparatus"),
        target.get("vt_attempt"),
        str(target["format"]),
        str(target["round"]),
        target.get("day"),
    )


def apply_orphan_dscore_decisions(
    records: list[ParsedGymternetResult],
    review_items: list[dict],
    decisions: list[dict],
    issues: list[dict],
) -> tuple[list[ParsedGymternetResult], dict]:
    stats = {
        "accepted_suggestions": 0,
        "manual_corrections": 0,
        "discarded": 0,
        "invalid_decisions": 0,
        "unresolved": len(review_items),
    }
    if not decisions:
        return records, stats

    updated = list(records)
    record_by_target_id = {target_record_id(record): index for index, record in enumerate(updated)}
    record_by_key = {result_target_key(record): index for index, record in enumerate(updated)}
    review_by_id = {item["review_id"]: item for item in review_items}

    for decision in decisions:
        review = review_by_id.get(decision.get("review_id"))
        if not review:
            stats["invalid_decisions"] += 1
            issues.append({
                "severity": "warning",
                "message": f"Ignored orphan D-score decision with unknown review_id '{decision.get('review_id')}'",
            })
            continue

        action = decision.get("action")
        if action == "discard":
            stats["discarded"] += 1
            continue

        target_index = None
        if action == "accept_suggestion":
            suggestion = find_review_suggestion(review, decision.get("suggestion_id"))
            if suggestion:
                target_index = record_by_target_id.get(suggestion["target_result"]["target_id"])
            else:
                stats["invalid_decisions"] += 1
                issues.append({
                    "severity": "warning",
                    "message": f"Ignored orphan D-score decision with unknown suggestion_id '{decision.get('suggestion_id')}'",
                })
                continue
        elif action == "manual_target":
            target = decision.get("target") or {}
            target_id = decision.get("target_id")
            if target_id:
                target_index = record_by_target_id.get(target_id)
            elif target:
                try:
                    target_index = record_by_key.get(manual_target_key(target))
                except KeyError:
                    target_index = None
            if target_index is None:
                stats["invalid_decisions"] += 1
                issues.append({
                    "severity": "warning",
                    "message": f"Ignored manual orphan D-score decision for review_id '{review['review_id']}' because target was not found",
                })
                continue
        else:
            stats["invalid_decisions"] += 1
            issues.append({
                "severity": "warning",
                "message": f"Ignored orphan D-score decision with invalid action '{action}'",
            })
            continue

        orphan_dscore = review["orphan_dscore"]["D_score"]
        target_record = updated[target_index]
        if target_record.D_score is not None and not score_equal(target_record.D_score, orphan_dscore):
            stats["invalid_decisions"] += 1
            issues.append({
                "severity": "warning",
                "message": (
                    f"Ignored orphan D-score decision for review_id '{review['review_id']}' "
                    "because target already has a different D_score"
                ),
            })
            continue
        updated[target_index] = replace(target_record, D_score=orphan_dscore)
        if action == "accept_suggestion":
            stats["accepted_suggestions"] += 1
        else:
            stats["manual_corrections"] += 1

    resolved = stats["accepted_suggestions"] + stats["manual_corrections"] + stats["discarded"]
    stats["unresolved"] = max(len(review_items) - resolved, 0)
    return updated, stats


def find_review_suggestion(review: dict, suggestion_id_value: Optional[str]) -> Optional[dict]:
    for suggestion in review.get("suggestions", []):
        if suggestion["suggestion_id"] == suggestion_id_value:
            return suggestion
    return None


def athlete_key_from_imported_payload(imported_athlete: dict) -> tuple:
    return (
        str(imported_athlete["first_name"]).lower(),
        str(imported_athlete["last_name"]).lower(),
        str(imported_athlete["discipline"]),
        str(imported_athlete.get("country") or ""),
    )


def athlete_identity_key(record: ParsedGymternetResult) -> tuple:
    return (record.first_name.lower(), record.last_name.lower(), record.discipline.value)


def athlete_identity_collision_review_id(
    identity_key: tuple,
    countries: list[str],
) -> str:
    return stable_id("athlete_identity_collision", (*identity_key, *countries))


def athlete_variant_payload(
    records: list[ParsedGymternetResult],
) -> dict:
    first = records[0]
    years = sorted({record.year for record in records})
    return {
        "country": first.country,
        "result_count": len(records),
        "years": years,
        "first_year": years[0],
        "last_year": years[-1],
        "sample_results": [import_record_payload(record) for record in records[:5]],
    }


def build_athlete_match_review_items(
    db: Session,
    records: list[ParsedGymternetResult],
) -> list[dict]:
    all_athletes = db.query(models.Athlete).filter(models.Athlete.is_deleted.is_(False)).all()
    existing_athletes = {
        (
            athlete.first_name.lower(),
            athlete.last_name.lower(),
            athlete.discipline.value,
            athlete.country or "",
        ): athlete
        for athlete in all_athletes
    }
    athletes_by_identity: dict[tuple, list[models.Athlete]] = {}
    for athlete in all_athletes:
        identity_key = (
            athlete.first_name.lower(),
            athlete.last_name.lower(),
            athlete.discipline.value,
        )
        athletes_by_identity.setdefault(identity_key, []).append(athlete)

    athlete_candidate_index: dict[models.DisciplineEnum, dict[tuple, list[models.Athlete]]] = {}
    for athlete in all_athletes:
        discipline_index = athlete_candidate_index.setdefault(athlete.discipline, {})
        for key in athlete_candidate_keys(athlete.first_name, athlete.last_name, athlete.country):
            discipline_index.setdefault(key, []).append(athlete)

    grouped: dict[tuple, list[ParsedGymternetResult]] = {}
    country_change_groups: dict[tuple, list[ParsedGymternetResult]] = {}
    records_by_identity: dict[tuple, list[ParsedGymternetResult]] = {}
    for record in records:
        records_by_identity.setdefault(athlete_identity_key(record), []).append(record)

    collision_identity_keys = {
        identity_key
        for identity_key, identity_records in records_by_identity.items()
        if len({record.country for record in identity_records if record.country}) > 1
    }

    review_items = []
    for identity_key in collision_identity_keys:
        identity_records = records_by_identity[identity_key]
        records_by_country: dict[str, list[ParsedGymternetResult]] = {}
        for record in identity_records:
            records_by_country.setdefault(record.country or "", []).append(record)
        variants = [
            athlete_variant_payload(variant_records)
            for _, variant_records in sorted(records_by_country.items())
        ]
        first = identity_records[0]
        existing_candidates = athletes_by_identity.get(identity_key, [])
        suggestions = [
            {
                "suggestion_id": athlete_match_suggestion_id(
                    athlete_identity_collision_review_id(
                        identity_key,
                        sorted(country for country in records_by_country if country),
                    ),
                    athlete,
                ),
                "suggestion_type": "existing_athlete_match",
                "confidence": 1.0,
                "message": (
                    f"All country variants can be linked to existing athlete "
                    f"'{athlete_full_name(athlete)}'."
                ),
                "action": "use_existing_athlete",
                "target_athlete": athlete_payload(athlete),
            }
            for athlete in existing_candidates
        ]
        countries = sorted(country for country in records_by_country if country)
        review_items.append({
            "review_id": athlete_identity_collision_review_id(identity_key, countries),
            "problem_type": "possible_athlete_identity_collision",
            "severity": "review",
            "message": (
                f"Imported name '{first.athlete_name}' appears with multiple countries "
                f"({', '.join(countries)}). Confirm whether this is one athlete who changed "
                "representation or different athletes with the same name."
            ),
            "imported_athlete": {
                **imported_athlete_payload(first, len(identity_records)),
                "country": None,
            },
            "country_variants": variants,
            "suggestions": suggestions,
            "allowed_actions": [
                "merge_as_same_athlete",
                "keep_separate",
                "accept_suggestion",
                "manual_target",
            ],
        })

    for record in records:
        if athlete_identity_key(record) in collision_identity_keys:
            continue
        athlete_key = athlete_lookup_key(record)
        existing_athlete = existing_athletes.get(athlete_key)
        if existing_athlete:
            continue
        same_identity_athletes = athletes_by_identity.get(athlete_identity_key(record), [])
        if len(same_identity_athletes) == 1 and athlete_country_differs(record, same_identity_athletes[0]):
            country_change_groups.setdefault(
                (athlete_key, same_identity_athletes[0].id),
                [],
            ).append(record)
            continue
        grouped.setdefault(athlete_key, []).append(record)

    for (athlete_key, athlete_id), grouped_records in country_change_groups.items():
        record = grouped_records[0]
        athlete = next(athlete for athlete in all_athletes if athlete.id == athlete_id)
        review_items.append({
            "review_id": athlete_country_change_review_id(record, athlete),
            "problem_type": "possible_athlete_country_change",
            "severity": "review",
            "message": (
                f"Imported athlete '{record.athlete_name}' already exists, "
                f"but country changed from '{athlete.country}' to '{record.country}'."
            ),
            "imported_athlete": imported_athlete_payload(record, len(grouped_records)),
            "existing_athlete": athlete_payload(athlete),
            "country_change": {
                "from": athlete.country,
                "to": record.country,
                "year": record.year,
            },
            "sample_results": [import_record_payload(sample) for sample in grouped_records[:5]],
            "suggestions": [],
            "allowed_actions": [
                "update_country",
                "keep_existing_country",
                "create_new",
                "manual_target",
            ],
        })

    for athlete_key, grouped_records in grouped.items():
        record = grouped_records[0]
        suggestions = []
        candidates = {}
        discipline_index = athlete_candidate_index.get(record.discipline, {})
        for key in athlete_candidate_keys(record.first_name, record.last_name, record.country):
            for athlete in discipline_index.get(key, []):
                candidates[athlete.id] = athlete

        for athlete in candidates.values():
            confidence = athlete_name_similarity(record, athlete)
            if confidence < 0.88:
                continue
            country_matches = bool(record.country and athlete.country and record.country == athlete.country)
            requires_country_decision = athlete_country_differs(record, athlete)
            review_id = athlete_match_review_id(record)
            suggestions.append({
                "suggestion_id": athlete_match_suggestion_id(review_id, athlete),
                "suggestion_type": "existing_athlete_match",
                "confidence": round(confidence, 3),
                "message": (
                    f"Imported athlete '{record.athlete_name}' may already exist as "
                    f"'{athlete_full_name(athlete)}'."
                ),
                "action": "use_existing_athlete",
                "changes": {
                    "athlete_name": {
                        "from": record.athlete_name,
                        "to": athlete_full_name(athlete),
                    },
                    "country": {
                        "from": record.country,
                        "to": athlete.country,
                    },
                },
                "country_matches": country_matches,
                "requires_country_decision": requires_country_decision,
                "country_decision_actions": (
                    ["update_country", "keep_existing_country"]
                    if requires_country_decision
                    else []
                ),
                "target_athlete": athlete_payload(athlete),
            })

        if not suggestions:
            continue

        suggestions = sorted(suggestions, key=lambda item: item["confidence"], reverse=True)[:5]
        review_items.append({
            "review_id": athlete_match_review_id(record),
            "problem_type": "possible_existing_athlete_match",
            "severity": "review",
            "message": (
                f"Imported athlete '{record.athlete_name}' is similar to existing athlete "
                f"'{suggestions[0]['target_athlete']['athlete_name']}'. Confirm whether they are the same person."
            ),
            "imported_athlete": imported_athlete_payload(record, len(grouped_records)),
            "sample_results": [import_record_payload(sample) for sample in grouped_records[:5]],
            "suggestions": suggestions,
            "allowed_actions": ["accept_suggestion", "create_new", "manual_target"],
        })

    return sorted(
        review_items,
        key=lambda item: item["suggestions"][0]["confidence"] if item["suggestions"] else 1.0,
        reverse=True,
    )


def find_athlete_review_suggestion(review: dict, suggestion_id_value: Optional[str]) -> Optional[dict]:
    for suggestion in review.get("suggestions", []):
        if suggestion["suggestion_id"] == suggestion_id_value:
            return suggestion
    return None


def resolve_manual_athlete_target(db: Session, target: dict) -> Optional[models.Athlete]:
    athlete_id = target.get("athlete_id")
    if athlete_id is not None:
        return db.query(models.Athlete).filter(
            models.Athlete.id == int(athlete_id),
            models.Athlete.is_deleted.is_(False),
        ).first()

    first_name = target.get("first_name")
    last_name = target.get("last_name")
    discipline = target.get("discipline")
    if not first_name or not last_name or not discipline:
        return None
    try:
        discipline_value = models.DisciplineEnum(str(discipline))
    except ValueError:
        return None

    return db.query(models.Athlete).filter(
        func.lower(models.Athlete.first_name) == str(first_name).lower(),
        func.lower(models.Athlete.last_name) == str(last_name).lower(),
        models.Athlete.discipline == discipline_value,
        models.Athlete.is_deleted.is_(False),
    ).first()


def apply_athlete_match_decisions(
    db: Session,
    review_items: list[dict],
    decisions: Optional[list[dict]],
    issues: list[dict],
) -> tuple[dict[tuple, int], dict[int, dict], dict[tuple, tuple], dict[tuple, str], dict]:
    stats = {
        "accepted_suggestions": 0,
        "manual_corrections": 0,
        "confirmed_new": 0,
        "identity_merges": 0,
        "identity_kept_separate": 0,
        "country_updates": 0,
        "country_kept": 0,
        "represented_country_corrections": 0,
        "invalid_decisions": 0,
        "unresolved": len(review_items),
    }
    if not decisions:
        return {}, {}, {}, {}, stats

    review_by_id = {item["review_id"]: item for item in review_items}
    resolutions: dict[tuple, int] = {}
    country_updates: dict[int, dict] = {}
    merge_keys: dict[tuple, tuple] = {}
    represented_country_overrides: dict[tuple, str] = {}
    resolved_review_ids = set()

    for decision in decisions:
        review = review_by_id.get(decision.get("review_id"))
        if not review:
            stats["invalid_decisions"] += 1
            issues.append({
                "severity": "warning",
                "message": f"Ignored athlete-match decision with unknown review_id '{decision.get('review_id')}'",
            })
            continue

        action = decision.get("action")

        if review["problem_type"] == "possible_athlete_identity_collision":
            imported_athlete = review["imported_athlete"]
            variant_keys = [
                (
                    str(imported_athlete["first_name"]).lower(),
                    str(imported_athlete["last_name"]).lower(),
                    str(imported_athlete["discipline"]),
                    str(variant.get("country") or ""),
                )
                for variant in review["country_variants"]
            ]
            if action == "keep_separate":
                stats["identity_kept_separate"] += 1
                resolved_review_ids.add(review["review_id"])
                continue
            if action == "merge_as_same_athlete":
                canonical_country = str(decision.get("canonical_country") or "")
                canonical_key = next(
                    (key for key in variant_keys if key[3] == canonical_country),
                    None,
                )
                if canonical_key is None:
                    stats["invalid_decisions"] += 1
                    issues.append({
                        "severity": "warning",
                        "message": (
                            f"Ignored athlete identity decision for review_id '{review['review_id']}' "
                            "because canonical_country does not match a country variant"
                        ),
                    })
                    continue
                country_overrides = identity_country_overrides_from_decision(
                    decision,
                    variant_keys,
                    canonical_country,
                    issues,
                    review["review_id"],
                )
                if country_overrides is None:
                    stats["invalid_decisions"] += 1
                    continue
                for variant_key in variant_keys:
                    merge_keys[variant_key] = canonical_key
                represented_country_overrides.update(country_overrides)
                stats["represented_country_corrections"] += sum(
                    1
                    for variant_key, target_country in country_overrides.items()
                    if str(variant_key[3]) != target_country
                )
                stats["identity_merges"] += 1
                resolved_review_ids.add(review["review_id"])
                continue

            athlete = None
            if action == "accept_suggestion":
                suggestion = find_athlete_review_suggestion(review, decision.get("suggestion_id"))
                if suggestion:
                    athlete = db.query(models.Athlete).filter(
                        models.Athlete.id == suggestion["target_athlete"]["athlete_id"],
                        models.Athlete.is_deleted.is_(False),
                    ).first()
            elif action == "manual_target":
                athlete = resolve_manual_athlete_target(db, decision.get("target") or decision)

            if athlete is None or athlete.discipline.value != imported_athlete["discipline"]:
                stats["invalid_decisions"] += 1
                issues.append({
                    "severity": "warning",
                    "message": (
                        f"Ignored athlete identity decision for review_id '{review['review_id']}' "
                        "because the target athlete was not found or has a different discipline"
                    ),
                })
                continue
            for variant_key in variant_keys:
                resolutions[variant_key] = athlete.id
            if action == "accept_suggestion":
                stats["accepted_suggestions"] += 1
            else:
                stats["manual_corrections"] += 1
            stats["identity_merges"] += 1
            resolved_review_ids.add(review["review_id"])
            continue

        imported_key = athlete_key_from_imported_payload(review["imported_athlete"])

        if review["problem_type"] == "possible_athlete_country_change":
            athlete_id = review["existing_athlete"]["athlete_id"]
            new_country = review["country_change"]["to"]
            if action == "update_country":
                country_updates[athlete_id] = {
                    "from_country": review["country_change"]["from"],
                    "to_country": new_country,
                    "change_year": review["country_change"]["year"],
                }
                stats["country_updates"] += 1
                resolutions[imported_key] = athlete_id
                resolved_review_ids.add(review["review_id"])
            elif action == "keep_existing_country":
                stats["country_kept"] += 1
                resolutions[imported_key] = athlete_id
                resolved_review_ids.add(review["review_id"])
            elif action == "create_new":
                stats["confirmed_new"] += 1
                resolved_review_ids.add(review["review_id"])
            elif action == "manual_target":
                athlete = resolve_manual_athlete_target(db, decision.get("target") or decision)
                if athlete is None or athlete.discipline.value != review["imported_athlete"]["discipline"]:
                    stats["invalid_decisions"] += 1
                    issues.append({
                        "severity": "warning",
                        "message": (
                            f"Ignored athlete country decision for review_id '{review['review_id']}' "
                            "because the target athlete was not found or has a different discipline"
                        ),
                    })
                    continue
                resolutions[imported_key] = athlete.id
                stats["manual_corrections"] += 1
                resolved_review_ids.add(review["review_id"])
            else:
                stats["invalid_decisions"] += 1
                issues.append({
                    "severity": "warning",
                    "message": f"Ignored athlete country decision with invalid action '{action}'",
                })
            continue

        if action == "create_new":
            stats["confirmed_new"] += 1
            resolved_review_ids.add(review["review_id"])
            continue

        athlete = None
        if action == "accept_suggestion":
            suggestion = find_athlete_review_suggestion(review, decision.get("suggestion_id"))
            if suggestion:
                athlete = db.query(models.Athlete).filter(
                    models.Athlete.id == suggestion["target_athlete"]["athlete_id"]
                ).first()
            else:
                stats["invalid_decisions"] += 1
                issues.append({
                    "severity": "warning",
                    "message": f"Ignored athlete-match decision with unknown suggestion_id '{decision.get('suggestion_id')}'",
                })
                continue
        elif action == "manual_target":
            athlete = resolve_manual_athlete_target(db, decision.get("target") or decision)
            if athlete is None:
                stats["invalid_decisions"] += 1
                issues.append({
                    "severity": "warning",
                    "message": f"Ignored manual athlete-match decision for review_id '{review['review_id']}' because target athlete was not found",
                })
                continue
        else:
            stats["invalid_decisions"] += 1
            issues.append({
                "severity": "warning",
                "message": f"Ignored athlete-match decision with invalid action '{action}'",
            })
            continue

        if athlete.discipline.value != review["imported_athlete"]["discipline"]:
            stats["invalid_decisions"] += 1
            issues.append({
                "severity": "warning",
                "message": (
                    f"Ignored athlete-match decision for review_id '{review['review_id']}' "
                    "because target athlete has a different discipline"
                ),
            })
            continue

        imported_country = review["imported_athlete"].get("country")
        if imported_country and athlete.country and imported_country != athlete.country:
            country_action = decision.get("country_action")
            if country_action == "update_country":
                country_updates[athlete.id] = {
                    "from_country": athlete.country,
                    "to_country": imported_country,
                    "change_year": review["imported_athlete"]["year"],
                }
                stats["country_updates"] += 1
            elif country_action == "keep_existing_country":
                stats["country_kept"] += 1
            else:
                stats["invalid_decisions"] += 1
                issues.append({
                    "severity": "warning",
                    "message": (
                        f"Ignored athlete-match decision for review_id '{review['review_id']}' "
                        "because country changed and country_action was not provided"
                    ),
                })
                continue

        resolutions[imported_key] = athlete.id
        resolved_review_ids.add(review["review_id"])
        if action == "accept_suggestion":
            stats["accepted_suggestions"] += 1
        else:
            stats["manual_corrections"] += 1

    stats["unresolved"] = max(len(review_items) - len(resolved_review_ids), 0)
    return resolutions, country_updates, merge_keys, represented_country_overrides, stats


def assign_automatic_days(
    records: list[ParsedGymternetResult],
    issues: list[dict],
) -> list[ParsedGymternetResult]:
    grouped: dict[tuple, list[int]] = {}
    for index, record in enumerate(records):
        grouped.setdefault(dayless_import_key(record), []).append(index)

    updated = list(records)
    assigned_groups = 0
    assigned_records = 0
    max_assigned_day = 0

    for indexes in grouped.values():
        if len(indexes) < 2:
            continue
        group = [records[index] for index in indexes]
        if any(record.day is not None for record in group):
            continue

        variant_days: dict[tuple, int] = {}
        for record in group:
            variant = score_variant_key(record)
            if variant not in variant_days:
                variant_days[variant] = len(variant_days) + 1

        if len(variant_days) <= 1:
            continue

        assigned_groups += 1
        max_assigned_day = max(max_assigned_day, max(variant_days.values()))
        for index in indexes:
            record = records[index]
            updated[index] = replace(record, day=variant_days[score_variant_key(record)])
            assigned_records += 1

    if assigned_groups:
        issues.append({
            "severity": "warning",
            "message": (
                "Automatic day assignment applied to "
                f"{assigned_groups} multi-day result keys without an explicit Day column; "
                f"{assigned_records} rows received day values up to {max_assigned_day}."
            ),
        })

    return updated


def find_existing_athlete(db: Session, record: ParsedGymternetResult) -> Optional[models.Athlete]:
    return db.query(models.Athlete).filter(
        func.lower(models.Athlete.first_name) == record.first_name.lower(),
        func.lower(models.Athlete.last_name) == record.last_name.lower(),
        models.Athlete.discipline == record.discipline,
        models.Athlete.country == record.country,
        models.Athlete.is_deleted.is_(False),
    ).first()


def find_existing_event(db: Session, record: ParsedGymternetResult) -> Optional[models.Event]:
    return db.query(models.Event).filter(
        func.lower(models.Event.name) == record.event_name.lower(),
        models.Event.year == record.year,
    ).first()


def find_existing_result(
    db: Session,
    athlete_id: int,
    event_id: int,
    record: ParsedGymternetResult,
) -> Optional[models.Result]:
    query = db.query(models.Result).filter(
        models.Result.athlete_id == athlete_id,
        models.Result.event_id == event_id,
        models.Result.discipline == record.discipline,
        models.Result.category == record.category,
        models.Result.format == record.format,
        models.Result.round == record.round,
    )
    query = query.filter(models.Result.apparatus == record.apparatus)
    if record.vt_attempt is None:
        query = query.filter(models.Result.vt_attempt.is_(None))
    else:
        query = query.filter(models.Result.vt_attempt == record.vt_attempt)
    if record.day is None:
        query = query.filter(models.Result.day.is_(None))
    else:
        query = query.filter(models.Result.day == record.day)
    return query.first()


def athlete_lookup_key(record: ParsedGymternetResult) -> tuple:
    return (
        record.first_name.lower(),
        record.last_name.lower(),
        record.discipline.value,
        record.country or "",
    )


def result_represented_country_for_record(
    record: ParsedGymternetResult,
    represented_country_overrides: Optional[dict[tuple, str]] = None,
) -> Optional[str]:
    represented_country_overrides = represented_country_overrides or {}
    return represented_country_overrides.get(athlete_lookup_key(record), record.country)


def normalize_decision_country(
    value,
    issues: list[dict],
    review_id: str,
) -> Optional[str]:
    country = normalize_country(value, issues, "athlete_match_decision", 0)
    if country is None:
        issues.append({
            "severity": "warning",
            "message": (
                f"Ignored athlete identity decision for review_id '{review_id}' "
                "because a country correction was empty"
            ),
        })
    return country


def identity_country_overrides_from_decision(
    decision: dict,
    variant_keys: list[tuple],
    canonical_country: str,
    issues: list[dict],
    review_id: str,
) -> Optional[dict[tuple, str]]:
    strategy = (
        decision.get("country_strategy")
        or decision.get("represented_country_strategy")
        or decision.get("country_resolution")
        or "preserve_represented_country"
    )
    strategy = str(strategy).strip().lower()
    variant_by_country = {str(key[3]): key for key in variant_keys}

    if strategy in {
        "preserve",
        "preserve_represented_country",
        "preserve_source_country",
        "historical_country",
        "country_history",
        "country_correction",
    }:
        overrides: dict[tuple, str] = {}
    elif strategy in {
        "correct_to_canonical",
        "correct_all_to_canonical",
        "country_correction_to_canonical",
    }:
        overrides = {variant_key: canonical_country for variant_key in variant_keys}
    else:
        issues.append({
            "severity": "warning",
            "message": (
                f"Ignored athlete identity decision for review_id '{review_id}' "
                f"because country_strategy '{strategy}' is not supported"
            ),
        })
        return None

    raw_corrections = (
        decision.get("country_corrections")
        or decision.get("represented_country_overrides")
        or {}
    )
    if raw_corrections:
        if not isinstance(raw_corrections, dict):
            issues.append({
                "severity": "warning",
                "message": (
                    f"Ignored athlete identity decision for review_id '{review_id}' "
                    "because country_corrections must be an object"
                ),
            })
            return None
        for source_country, target_country in raw_corrections.items():
            normalized_source = normalize_decision_country(source_country, issues, review_id)
            normalized_target = normalize_decision_country(target_country, issues, review_id)
            if normalized_source is None or normalized_target is None:
                return None
            variant_key = variant_by_country.get(normalized_source)
            if variant_key is None:
                issues.append({
                    "severity": "warning",
                    "message": (
                        f"Ignored athlete identity decision for review_id '{review_id}' "
                        f"because source country '{normalized_source}' is not a variant"
                    ),
                })
                return None
            overrides[variant_key] = normalized_target

    return overrides


def event_lookup_key(record: ParsedGymternetResult) -> tuple:
    return (record.event_name.lower(), record.year)


def result_lookup_key(
    athlete_id: int,
    event_id: int,
    record: ParsedGymternetResult,
) -> tuple:
    return result_identity_key(
        athlete_id,
        event_id,
        record.discipline,
        record.category,
        record.apparatus,
        record.vt_attempt,
        record.day,
        record.format,
        record.round,
    )


def build_existing_indexes(db: Session) -> tuple[dict, dict, dict]:
    athletes = {
        (
            athlete.first_name.lower(),
            athlete.last_name.lower(),
            athlete.discipline.value,
            athlete.country or "",
        ): athlete
        for athlete in db.query(models.Athlete).filter(models.Athlete.is_deleted.is_(False)).all()
    }
    events = {
        (event.name.lower(), event.year): event
        for event in db.query(models.Event).filter(models.Event.is_deleted.is_(False)).all()
    }
    results = {
        result_identity_key(
            result.athlete_id,
            result.event_id,
            result.discipline,
            result.category,
            result.apparatus,
            result.vt_attempt,
            result.day,
            result.format,
            result.round,
        ): result
        for result in db.query(models.Result).filter(models.Result.is_deleted.is_(False)).all()
    }
    return athletes, events, results


def resolved_athlete_for_key(
    db: Session,
    athlete_resolution_ids: dict[tuple, int],
    athlete_key: tuple,
    athlete_cache: dict[int, models.Athlete],
) -> Optional[models.Athlete]:
    athlete_id = athlete_resolution_ids.get(athlete_key)
    if athlete_id is None:
        return None
    if athlete_id not in athlete_cache:
        athlete_cache[athlete_id] = db.query(models.Athlete).filter(models.Athlete.id == athlete_id).first()
    return athlete_cache[athlete_id]


def summarize_records(
    db: Session,
    records: list[ParsedGymternetResult],
    issues: list[dict],
    athlete_resolution_ids: Optional[dict[tuple, int]] = None,
    athlete_merge_keys: Optional[dict[tuple, tuple]] = None,
    represented_country_overrides: Optional[dict[tuple, str]] = None,
) -> dict:
    seen = {}
    duplicates = []
    conflicts = []
    importable = []
    athlete_keys = set()
    event_keys = set()
    existing_athletes, existing_events, existing_results = build_existing_indexes(db)
    athlete_resolution_ids = athlete_resolution_ids or {}
    athlete_merge_keys = athlete_merge_keys or {}
    represented_country_overrides = represented_country_overrides or {}
    resolved_athlete_cache: dict[int, models.Athlete] = {}

    for record in records:
        if record.year <= 0:
            issues.append({
                "severity": "error",
                "sheet": record.source_sheet,
                "row": record.source_row,
                "message": "Missing event year. Provide year_hint or include a year in the file/event name.",
            })
            continue
        existing_in_file = seen.get(record.import_key)
        record_country = result_represented_country_for_record(record, represented_country_overrides)
        if existing_in_file:
            existing_country = result_represented_country_for_record(
                existing_in_file,
                represented_country_overrides,
            )
            if score_equal(existing_in_file.score, record.score) and score_equal(existing_in_file.D_score, record.D_score):
                if not country_equal(existing_country, record_country):
                    conflicts.append(conflict_payload(record, None, "country_conflict_in_file", existing_in_file))
                    continue
                duplicates.append(import_record_payload(record, reason="duplicate_in_file"))
                continue
            conflicts.append(conflict_payload(record, None, "conflict_in_file", existing_in_file))
            continue
        seen[record.import_key] = record

        source_athlete_key = athlete_lookup_key(record)
        athlete_key = athlete_merge_keys.get(source_athlete_key, source_athlete_key)
        athlete = (
            resolved_athlete_for_key(db, athlete_resolution_ids, source_athlete_key, resolved_athlete_cache)
            or resolved_athlete_for_key(db, athlete_resolution_ids, athlete_key, resolved_athlete_cache)
            or existing_athletes.get(athlete_key)
        )
        event = existing_events.get(event_lookup_key(record))
        if athlete and event:
            result = existing_results.get(result_lookup_key(athlete.id, event.id, record))
            if result:
                if score_equal(result.score, record.score) and score_equal(result.D_score, record.D_score):
                    if not country_equal(result_represented_country(result), record_country):
                        conflicts.append(conflict_payload(record, result, "country_conflict_existing"))
                        continue
                    duplicates.append(import_record_payload(record, result.id, reason="duplicate_existing"))
                    continue
                conflicts.append(conflict_payload(record, result, "conflict_existing"))
                continue

        importable.append(record)
        if not athlete:
            athlete_keys.add(athlete_key)
        if not event:
            event_keys.add(event_lookup_key(record))

    return {
        "parsed_rows": len(records),
        "importable_results": len(importable),
        "duplicates": duplicates,
        "conflicts": conflicts,
        "would_create_athletes": len(athlete_keys),
        "would_create_events": len(event_keys),
        "issues": issues,
        "sample_results": [import_record_payload(record) for record in importable[:20]],
        "importable_records": importable,
    }


def import_record_payload(record: ParsedGymternetResult, existing_result_id: Optional[int] = None, reason: Optional[str] = None) -> dict:
    payload = {
        "event_name": record.event_name,
        "year": record.year,
        "athlete_name": record.athlete_name,
        "country": record.country,
        "discipline": record.discipline.value,
        "category": record.category.value,
        "apparatus": record.apparatus,
        "vt_attempt": record.vt_attempt,
        "day": record.day,
        "format": record.format.value,
        "round": record.round.value,
        "score": record.score,
        "D_score": record.D_score,
        "vault_attempt_order_uncertain": record.vault_attempt_order_uncertain,
        "source_sheet": record.source_sheet,
        "source_row": record.source_row,
    }
    if existing_result_id is not None:
        payload["existing_result_id"] = existing_result_id
    if reason:
        payload["reason"] = reason
    return payload


def conflict_payload(
    record: ParsedGymternetResult,
    existing_result: Optional[models.Result],
    reason: str,
    existing_record: Optional[ParsedGymternetResult] = None,
) -> dict:
    payload = import_record_payload(record, existing_result.id if existing_result else None, reason)
    if existing_result:
        payload["existing_score"] = existing_result.score
        payload["existing_D_score"] = existing_result.D_score
        payload["existing_country"] = result_represented_country(existing_result)
    if existing_record:
        payload["existing_score"] = existing_record.score
        payload["existing_D_score"] = existing_record.D_score
        payload["existing_country"] = existing_record.country
    return payload


def commit_records(
    db: Session,
    records: list[ParsedGymternetResult],
    notification_user_id: Optional[int] = None,
    athlete_resolution_ids: Optional[dict[tuple, int]] = None,
    athlete_country_update_ids: Optional[dict[int, dict]] = None,
    athlete_merge_keys: Optional[dict[tuple, tuple]] = None,
    represented_country_overrides: Optional[dict[tuple, str]] = None,
    pre_skipped_duplicates: int = 0,
    orphan_dscore_review_uncommitted: int = 0,
) -> dict:
    stats = {
        "created_athletes": 0,
        "created_events": 0,
        "created_results": 0,
        "created_complete_results": 0,
        "created_partial_results": 0,
        "orphan_dscore_review_uncommitted": orphan_dscore_review_uncommitted,
        "updated_events": 0,
        "updated_athlete_countries": 0,
        "corrected_represented_countries": 0,
        "athletes_with_new_results": 0,
        "events_with_new_results": 0,
        "created_admin_notifications": 0,
        "skipped_duplicates": pre_skipped_duplicates,
    }
    existing_athletes, existing_events, existing_results = build_existing_indexes(db)
    athlete_resolution_ids = athlete_resolution_ids or {}
    athlete_country_update_ids = athlete_country_update_ids or {}
    athlete_merge_keys = athlete_merge_keys or {}
    represented_country_overrides = represented_country_overrides or {}
    resolved_athlete_cache: dict[int, models.Athlete] = {}
    created_athletes_for_notification: list[models.Athlete] = []
    created_events_for_notification: list[models.Event] = []
    athletes_with_new_results: set[int] = set()
    events_with_new_results: set[int] = set()

    for athlete_id, country_update in athlete_country_update_ids.items():
        athlete = db.query(models.Athlete).filter(models.Athlete.id == athlete_id).first()
        if athlete and record_athlete_country_change(
            db,
            athlete,
            country_update["to_country"],
            int(country_update["change_year"]),
            country_update.get("from_country"),
        ):
            stats["updated_athlete_countries"] += 1

    for record in records:
        source_athlete_key = athlete_lookup_key(record)
        athlete_key = athlete_merge_keys.get(source_athlete_key, source_athlete_key)
        athlete = (
            resolved_athlete_for_key(db, athlete_resolution_ids, source_athlete_key, resolved_athlete_cache)
            or resolved_athlete_for_key(db, athlete_resolution_ids, athlete_key, resolved_athlete_cache)
            or existing_athletes.get(athlete_key)
        )
        if not athlete:
            athlete = models.Athlete(
                first_name=record.first_name,
                last_name=record.last_name,
                country=athlete_key[3] or None,
                discipline=record.discipline,
            )
            db.add(athlete)
            db.flush()
            existing_athletes[athlete_key] = athlete
            stats["created_athletes"] += 1
            created_athletes_for_notification.append(athlete)
        elif not athlete.country and record.country:
            athlete.country = record.country

        event_key = event_lookup_key(record)
        event = existing_events.get(event_key)
        if not event:
            event = models.Event(
                name=record.event_name,
                year=record.year,
                discipline=event_discipline_for(None, record.discipline),
                category=event_category_for(None, record.category),
                level=infer_event_level(record.event_name),
            )
            db.add(event)
            db.flush()
            existing_events[event_key] = event
            stats["created_events"] += 1
            created_events_for_notification.append(event)
        else:
            new_discipline = event_discipline_for(event, record.discipline)
            new_category = event_category_for(event, record.category)
            if event.discipline != new_discipline:
                event.discipline = new_discipline
                stats["updated_events"] += 1
            if event.category != new_category:
                event.category = new_category
                stats["updated_events"] += 1

        result_key = result_lookup_key(athlete.id, event.id, record)
        existing = existing_results.get(result_key)
        if existing:
            stats["skipped_duplicates"] += 1
            continue

        result = models.Result(
            athlete_id=athlete.id,
            event_id=event.id,
            represented_country=result_represented_country_for_record(record, represented_country_overrides),
            discipline=record.discipline,
            category=record.category,
            apparatus=record.apparatus,
            vt_attempt=record.vt_attempt,
            day=record.day,
            format=record.format,
            round=record.round,
            D_score=record.D_score,
            E_score=None,
            Penalty=None,
            Bonus=None,
            score=record.score,
            rank=None,
            vault_attempt_order_uncertain=record.vault_attempt_order_uncertain,
        )
        db.add(result)
        if result.represented_country != record.country:
            stats["corrected_represented_countries"] += 1
        existing_results[result_key] = result
        stats["created_results"] += 1
        if record.score is not None and record.D_score is not None:
            stats["created_complete_results"] += 1
        else:
            stats["created_partial_results"] += 1
        athletes_with_new_results.add(athlete.id)
        events_with_new_results.add(event.id)

    stats["athletes_with_new_results"] = len(athletes_with_new_results)
    stats["events_with_new_results"] = len(events_with_new_results)
    if notification_user_id is not None and any(
        stats[key] > 0
        for key in (
            "created_athletes",
            "created_events",
            "created_results",
            "created_complete_results",
            "created_partial_results",
            "orphan_dscore_review_uncommitted",
            "updated_events",
            "updated_athlete_countries",
            "corrected_represented_countries",
            "skipped_duplicates",
        )
    ):
        notification_user = db.query(models.User).filter(models.User.id == notification_user_id).first()
        db.add(models.Notification(
            user_id=notification_user_id,
            type=models.NotificationTypeEnum.IMPORT_SUMMARY,
            message=translate(
                "notification.import_summary",
                notification_user.preferred_language if notification_user else models.LanguageEnum.EN,
                created_athletes=stats["created_athletes"],
                created_events=stats["created_events"],
                created_results=stats["created_results"],
                created_complete_results=stats["created_complete_results"],
                created_partial_results=stats["created_partial_results"],
                athletes_with_new_results=stats["athletes_with_new_results"],
                events_with_new_results=stats["events_with_new_results"],
                updated_events=stats["updated_events"],
                updated_athlete_countries=stats["updated_athlete_countries"],
                corrected_represented_countries=stats["corrected_represented_countries"],
                orphan_dscore_review_uncommitted=stats["orphan_dscore_review_uncommitted"],
                skipped_duplicates=stats["skipped_duplicates"],
            ),
            related_athlete_id=created_athletes_for_notification[0].id if created_athletes_for_notification else None,
            related_event_id=created_events_for_notification[0].id if created_events_for_notification else None,
        ))
        stats["created_admin_notifications"] += 1
    return stats
