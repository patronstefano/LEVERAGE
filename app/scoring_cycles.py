from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringCycle:
    start_year: int
    end_year: int
    label: str
    is_covid_extended: bool = False


def scoring_cycle_for_year(year: int) -> ScoringCycle:
    if 2017 <= year <= 2021:
        return ScoringCycle(2017, 2021, "2017-2021", is_covid_extended=True)
    if 2022 <= year <= 2024:
        return ScoringCycle(2022, 2024, "2022-2024")
    if year >= 2025:
        start_year = 2025 + ((year - 2025) // 4) * 4
        return ScoringCycle(start_year, start_year + 3, f"{start_year}-{start_year + 3}")

    start_year = 2013 + ((year - 2013) // 4) * 4
    return ScoringCycle(start_year, start_year + 3, f"{start_year}-{start_year + 3}")


def parse_scoring_cycle(label: str) -> ScoringCycle:
    cleaned = label.strip().replace(" ", "")
    parts = cleaned.split("-")
    if len(parts) != 2:
        raise ValueError("scoring_cycle must use the YYYY-YYYY format")

    try:
        start_year = int(parts[0])
        end_year = int(parts[1])
    except ValueError as exc:
        raise ValueError("scoring_cycle must use numeric years") from exc

    cycle = scoring_cycle_for_year(start_year)
    if cycle.start_year != start_year or cycle.end_year != end_year:
        raise ValueError("scoring_cycle does not match a supported gymnastics scoring cycle")
    return cycle


def unique_scoring_cycles_for_years(years: list[int]) -> list[ScoringCycle]:
    cycles_by_label = {cycle.label: cycle for cycle in (scoring_cycle_for_year(year) for year in years)}
    return sorted(cycles_by_label.values(), key=lambda cycle: cycle.start_year)


def scoring_cycle_payload(cycle: ScoringCycle) -> dict:
    return {
        "label": cycle.label,
        "start_year": cycle.start_year,
        "end_year": cycle.end_year,
        "is_covid_extended": cycle.is_covid_extended,
    }
