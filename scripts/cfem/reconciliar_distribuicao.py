"""Compare one ANM CFEM CSV slice with an independently published ANM PDF.

Reference: remessa 696, issued 2025-05-07, for the producer distribution
to three municipalities. Only aggregates and source metadata are exported.
"""

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


PDF_URL = "https://www.gov.br/anm/pt-br/itens/arquivos/cfem-abril-maio-25.pdf"
EXPECTED = {
    "1502152": ("Canaã dos Carajás", Decimal("60776801.44")),
    "1505536": ("Parauapebas", Decimal("42951670.43")),
    "1504208": ("Marabá", Decimal("17289067.88")),
}


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--output", type=Path, default=Path("output/reconciliacao-anm-distribuicao-maio-2025.json"))
    args = parser.parse_args()

    amounts = defaultdict(lambda: Decimal(0))
    counts = defaultdict(int)
    with args.csv_path.open(encoding="latin-1", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("CSV has no header")
        month_column, distribution_type_column = reader.fieldnames[2], reader.fieldnames[7]
        for row in reader:
            code = row["CodigoEnte"]
            if (row["Ano"] != "2025" or row[month_column] != "5"
                    or row[distribution_type_column] != "Produtor" or code not in EXPECTED):
                continue
            raw = row["Valor"].strip().replace(".", "").replace(",", ".")
            amounts[code] += Decimal(raw)
            counts[code] += 1

    checks = []
    for code, (municipality, pdf_amount) in EXPECTED.items():
        csv_amount = amounts[code].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        checks.append({
            "ibge_code": code,
            "municipality": municipality,
            "csv_rows": counts[code],
            "csv_sum_unrounded": str(amounts[code]),
            "csv_sum_rounded_brl": str(csv_amount),
            "pdf_amount_brl": str(pdf_amount),
            "matches_pdf": counts[code] > 0 and csv_amount == pdf_amount,
        })

    evidence = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "csv_sha256": file_sha256(args.csv_path),
        "pdf_source_url": PDF_URL,
        "pdf_remittance": 696,
        "pdf_issued_date": "2025-05-07",
        "filter": {"year": 2025, "month": 5, "distribution_type": "Produtor"},
        "checks": checks,
        "matched": sum(item["matches_pdf"] for item in checks),
        "tested": len(checks),
        "scope_note": "Three producer municipalities in one month. Annual totals and other distribution types remain unchecked.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"matched": evidence["matched"], "tested": evidence["tested"]}))
    if evidence["matched"] != evidence["tested"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
