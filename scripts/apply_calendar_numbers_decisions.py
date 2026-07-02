from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from numbers_parser import Document


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip().strip('"').strip("“”")


def read_numbers_rows(path: Path) -> list[dict[str, str]]:
    document = Document(path)
    table = document.sheets[0].tables[0]
    headers = [clean(table.cell(0, column).value) for column in range(table.num_cols)]
    rows: list[dict[str, str]] = []
    for row_index in range(1, table.num_rows):
        row = {
            header: clean(table.cell(row_index, column).value)
            for column, header in enumerate(headers)
            if header
        }
        if any(row.values()):
            rows.append(row)
    return rows


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def by_key(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        value = clean(row.get(key))
        if value:
            indexed[value] = row
    return indexed


def transfer(
    csv_path: Path,
    numbers_path: Path,
    key: str,
    decision_columns: list[str],
) -> dict[str, Any]:
    csv_rows, fieldnames = read_csv(csv_path)
    numbers_rows = read_numbers_rows(numbers_path)
    decisions = by_key(numbers_rows, key)
    updated = 0
    missing = []

    for row in csv_rows:
        key_value = clean(row.get(key))
        numbers_row = decisions.get(key_value)
        if not numbers_row:
            missing.append(key_value)
            continue
        for column in decision_columns:
            row[column] = clean(numbers_row.get(column))
        updated += 1

    extra = sorted(set(decisions) - {clean(row.get(key)) for row in csv_rows})
    if missing or extra:
        raise ValueError(
            f"Mismatch for {csv_path}: missing_in_numbers={missing[:5]}, extra_in_numbers={extra[:5]}"
        )

    write_csv(csv_path, csv_rows, fieldnames)
    return {
        "csv": str(csv_path),
        "numbers": str(numbers_path),
        "key": key,
        "updated": updated,
        "decision_columns": decision_columns,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transfer Calendar review decisions from Numbers files into operational CSVs."
    )
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--report-dir", type=Path, default=Path("docs/import_reports"))
    args = parser.parse_args()

    report_dir = args.report_dir
    transfers = [
        transfer(
            report_dir / f"calendar_{args.year}_calendar_unmatched_current.csv",
            report_dir / f"calendar_{args.year}_calendar_unmatched_current.numbers",
            "calendar_row",
            ["choice", "manual_event_id", "notes"],
        ),
        transfer(
            report_dir / f"calendar_{args.year}_db_unmatched_current.csv",
            report_dir / f"calendar_{args.year}_db_unmatched_current.numbers",
            "event_id",
            ["choice_calendar_row", "notes"],
        ),
        transfer(
            report_dir / f"calendar_{args.year}_source_conflicts_slim.csv",
            report_dir / f"calendar_{args.year}_source_conflicts_slim.numbers",
            "conflict_group",
            ["choice", "notes"],
        ),
    ]

    for item in transfers:
        print(item)


if __name__ == "__main__":
    main()
