"""Create a provisional municipal CFEM distribution table from the ANM CSV.

The output keeps only aggregate amounts. Missing municipalities are reported in
the manifest and are not manufactured as zero-valued observations.
"""

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


SOURCE_URL = "https://dadosabertos.anm.gov.br/CFEM/CFEM_Distribuicao.csv"
MUNICIPALITIES = {
    "1501576": "Bom Jesus do Tocantins",
    "1501758": "Brejo Grande do Araguaia",
    "1502152": "Canaã dos Carajás",
    "1502772": "Curionópolis",
    "1502954": "Eldorado do Carajás",
    "1504208": "Marabá",
    "1505494": "Palestina do Pará",
    "1505536": "Parauapebas",
    "1505635": "Piçarra",
    "1507151": "São Domingos do Araguaia",
    "1507458": "São Geraldo do Araguaia",
    "1507508": "São João do Araguaia",
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
    parser.add_argument("--year", type=int, default=2025)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--reconciliation", type=Path, help="Independent ANM PDF comparison JSON for this exact source file")
    args = parser.parse_args()
    output_path = args.output or Path(f"output/derived/cfem-distribuicao-municipal-{args.year}.csv")

    sums = defaultdict(lambda: Decimal(0))
    counts = Counter()
    all_brazil_rows_by_month = Counter()
    invalid_amounts = 0
    invalid_months = 0
    with args.csv_path.open(encoding="latin-1", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"Ano", "Mês", "CodigoEnte", "TipoDistribuição", "Valor"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"Unexpected CSV columns: {reader.fieldnames}")
        for row in reader:
            code = row["CodigoEnte"].strip()
            if row["Ano"].strip() != str(args.year):
                continue
            month = row["Mês"].strip()
            all_brazil_rows_by_month[month] += 1
            if code not in MUNICIPALITIES:
                continue
            if not month.isdigit() or not 1 <= int(month) <= 12:
                invalid_months += 1
                continue
            kind = row["TipoDistribuição"].strip()
            if not kind:
                raise ValueError("Blank distribution type in target row")
            raw = row["Valor"].strip().replace(".", "").replace(",", ".")
            try:
                amount = Decimal(raw)
            except InvalidOperation:
                invalid_amounts += 1
                continue
            key = (code, int(month), kind)
            sums[key] += amount
            counts[key] += 1

    if invalid_months or invalid_amounts:
        raise ValueError(f"Invalid month/amount in selected rows: {invalid_months}/{invalid_amounts}")

    source_hash = file_sha256(args.csv_path)
    reconciliation = None
    if args.reconciliation:
        reference = json.loads(args.reconciliation.read_text(encoding="utf-8"))
        if reference.get("csv_sha256") != source_hash:
            raise ValueError("Reconciliation JSON was produced from a different source CSV")
        reconciliation = {
            "evidence_path": str(args.reconciliation),
            "tested": reference.get("tested"),
            "matched": reference.get("matched"),
        }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("ibge_code", "municipality", "year", "month", "distribution_type", "amount_brl", "source_rows"))
        for (code, month, kind), amount in sorted(sums.items()):
            rounded = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            writer.writerow((code, MUNICIPALITIES[code], args.year, month, kind, str(rounded), counts[(code, month, kind)]))

    present = sorted({code for code, _, _ in sums})
    missing_months = [month for month in range(1, 13) if str(month) not in all_brazil_rows_by_month]
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_url": SOURCE_URL,
        "source_sha256": source_hash,
        "year": args.year,
        "output_csv": str(output_path),
        "output_sha256": file_sha256(output_path),
        "output_rows": len(sums),
        "source_rows_aggregated": sum(counts.values()),
        "municipalities_present": present,
        "municipalities_missing": [code for code in MUNICIPALITIES if code not in present],
        "all_brazil_source_rows_by_month": dict(sorted(all_brazil_rows_by_month.items(), key=lambda pair: int(pair[0]))),
        "months_absent_in_full_source_file": missing_months,
        "annual_aggregation_allowed": not missing_months,
        "publication_ready": False,
        "independent_reconciliation": reconciliation,
        "amount_rule": "Sum raw Decimal values by IBGE code, year, month and distribution type; then round half up to BRL cents.",
        "status": "annual total blocked: one or more months absent in full source file" if missing_months else "monthly aggregates produced; independent validation still required",
        "july_distribution_news_url": "https://www.gov.br/anm/pt-br/assuntos/noticias/distribuidos-r-478-milhoes-de-royalties-da-mineracao-a-estados-e-municipios-produtores" if args.year == 2025 and 7 in missing_months else None,
    }
    manifest_path = output_path.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(sums), "municipalities_present": len(present),
                      "municipalities_missing": manifest["municipalities_missing"],
                      "manifest": str(manifest_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
