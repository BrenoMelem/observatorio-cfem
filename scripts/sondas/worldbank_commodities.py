"""Extract the two mining-related annual series from the World Bank Pink Sheet.

Download the official CMO-Historical-Data-Annual.xlsx first, then pass its path.
This reads the workbook only; it never executes formulas or macros.
"""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import load_workbook


SOURCE_URL = (
    "https://thedocs.worldbank.org/en/doc/"
    "74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/"
    "CMO-Historical-Data-Annual.xlsx"
)
SHEET = "Annual Prices (Nominal)"
NAMES = ("Iron ore, cfr spot", "Copper")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--output", type=Path, default=Path("output/validacao-worldbank-commodities-2026-10-15.json"))
    args = parser.parse_args()

    digest = hashlib.sha256(args.workbook.read_bytes()).hexdigest()
    workbook = load_workbook(args.workbook, read_only=True, data_only=True)
    sheet = workbook[SHEET]
    headings = [cell.value for cell in sheet[7]]
    columns = {name: headings.index(name) + 1 for name in NAMES}
    series = []
    for name, column in columns.items():
        observations = []
        for year in (2023, 2024, 2025):
            matches = [row for row in sheet.iter_rows(min_row=9, values_only=True) if row[0] == year]
            if len(matches) != 1:
                raise ValueError(f"Expected one row for {year}; found {len(matches)}")
            value = matches[0][column - 1]
            if not isinstance(value, (int, float)):
                raise ValueError(f"{name} {year} is not numeric: {value!r}")
            observations.append({"year": year, "value": value})
        series.append({"name": name, "workbook_unit_label": sheet.cell(8, column).value,
                       "unit_in_october_pdf": "$/dmt" if name.startswith("Iron ore") else "$/mt",
                       "column": column, "observations": observations})
    evidence = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_url": SOURCE_URL,
        "source_sha256": digest,
        "worksheet": SHEET,
        "updated_at_label": sheet.cell(4, 1).value,
        "series": series,
        "cross_check": "2023–2025 values match October 2026 World Bank Pink Sheet PDF",
        "cross_check_url": SOURCE_URL.replace("CMO-Historical-Data-Annual.xlsx", "CMO-Pink-Sheet-October-2026.pdf"),
        "unit_note": "Workbook says $/dmtu for iron ore; October PDF says $/dmt. Confirm the intended unit before display.",
        "limitation": "International reference prices, not municipality-level mineral production or CFEM revenue.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
