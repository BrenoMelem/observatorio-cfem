"""Validate municipal coverage in an official ANM CFEM CSV without exporting personal fields."""

import argparse
import csv
import hashlib
import json
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path


MUNICIPIOS = {
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

SOURCES = {
    "autuacao": {
        "url": "https://dadosabertos.anm.gov.br/CFEM/CFEM_Autuacao.csv",
        "territory_column": "Município",
        "year_column": "AnoPublicação",
        "mode": "name",
    },
    "arrecadacao": {
        "url": "https://dadosabertos.anm.gov.br/CFEM/CFEM_Arrecadacao_2022_2026.csv",
        "territory_column": "CodigoMunicipio",
        "year_column": "Ano",
        "mode": "code",
        "value_column": "ValorRecolhido",
    },
    "distribuicao": {
        "url": "https://dadosabertos.anm.gov.br/CFEM/CFEM_Distribuicao.csv",
        "territory_column": "CodigoEnte",
        "year_column": "Ano",
        "mode": "code",
        "value_column": "Valor",
    },
}


def normalized(value):
    plain = unicodedata.normalize("NFD", str(value).strip())
    return "".join(c for c in plain if unicodedata.category(c) != "Mn").casefold()


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect(path, source):
    spec = SOURCES[source]
    matches = Counter()
    years = Counter()
    blank_years = 0
    amounts = Counter()
    all_year_amounts = Counter()
    invalid_amounts = 0
    invalid_amounts_all_rows = 0
    total = 0
    name_to_code = {normalized(name): code for code, name in MUNICIPIOS.items()}
    with path.open("r", encoding="latin-1", newline="") as stream:
        sample = stream.readline()
        delimiter = ";" if sample.count(";") > sample.count(",") else ","
        stream.seek(0)
        reader = csv.DictReader(stream, delimiter=delimiter)
        headers = reader.fieldnames or []
        required = {spec["territory_column"], spec["year_column"]}
        if spec.get("value_column"):
            required.add(spec["value_column"])
        missing = sorted(required - set(headers))
        if missing:
            raise ValueError(f"Missing expected columns: {missing}; actual: {headers}")
        for row in reader:
            total += 1
            year = str(row.get(spec["year_column"], "")).strip()
            if source == "arrecadacao" and year:
                raw_value = str(row.get(spec["value_column"], "")).strip()
                try:
                    all_year_amounts[year] += Decimal(raw_value.replace(".", "").replace(",", "."))
                except InvalidOperation:
                    invalid_amounts_all_rows += 1
            raw_geo = str(row.get(spec["territory_column"], "")).strip()
            if spec["mode"] == "name":
                code = name_to_code.get(normalized(raw_geo)) if row.get("UF", "").strip().upper() == "PA" else None
            else:
                code = raw_geo if raw_geo in MUNICIPIOS else None
            if not code:
                continue
            matches[code] += 1
            if year:
                years[year] += 1
            else:
                blank_years += 1
            if spec.get("value_column") and year:
                raw_value = str(row.get(spec["value_column"], "")).strip()
                try:
                    amounts[(code, year)] += Decimal(raw_value.replace(".", "").replace(",", "."))
                except InvalidOperation:
                    invalid_amounts += 1
    return {
        "source_url": spec["url"],
        "file_name": path.name,
        "file_size_bytes": path.stat().st_size,
        "sha256": sha256(path),
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "delimiter": delimiter,
        "headers": headers,
        "total_rows": total,
        "target_rows": sum(matches.values()),
        "target_municipalities_present": len(matches),
        "rows_by_municipality": [
            {"ibge_code": code, "municipality": name, "rows": matches[code]}
            for code, name in MUNICIPIOS.items()
        ],
        "years_in_target_rows": dict(sorted(years.items())),
        "target_rows_without_year": blank_years,
        "invalid_amounts_in_target_rows": invalid_amounts,
        "invalid_amounts_all_rows": invalid_amounts_all_rows if source == "arrecadacao" else None,
        "all_brazil_raw_amounts_by_year": {year: str(amount) for year, amount in sorted(all_year_amounts.items())} if source == "arrecadacao" else None,
        "amounts_by_municipality_and_year": [
            {"ibge_code": code, "year": year, "sum_raw_value": str(total)}
            for (code, year), total in sorted(amounts.items())
        ],
        "note": "Raw sums are provisional until reconciled with ANM's published totals. No person/company identifiers exported.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=SOURCES)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inspect(args.csv_path, args.kind)
    content = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    print(content)


if __name__ == "__main__":
    main()
