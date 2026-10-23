"""Small municipal probe of official IPEADATA OData employment series."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


BASE = "http://www.ipeadata.gov.br/api/odata4"
SERIES = ("ADMISNC", "DESLIGNC")
MUNICIPALITIES = ("1502152", "1505536")


def get_json(url, max_bytes=2_000_000):
    request = Request(url, headers={"User-Agent": "Observatorio-CFEM-validation/0.1"})
    with urlopen(request, timeout=90) as response:
        declared_length = int(response.headers.get("Content-Length", "0"))
        if declared_length > max_bytes:
            prefix = response.read(500).decode("utf-8", "replace")
            raise ValueError(
                f"Declared response length {declared_length} exceeds {max_bytes} bytes "
                f"despite requested filter/top; prefix={prefix[:120]!r}"
            )
        body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise ValueError(f"Response exceeds {max_bytes} bytes; filter may have been ignored")
        return json.loads(body.decode("utf-8-sig"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("output/validacao-ipeadata-emprego-2026-10-15.json"))
    args = parser.parse_args()
    evidence = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "IPEADATA official OData API",
        "tests": [],
    }
    for series in SERIES:
        metadata_url = f"{BASE}/Metadados('{series}')"
        try:
            metadata = get_json(metadata_url).get("value", [])
            selected_metadata = [
                {key: item.get(key) for key in ("SERCODIGO", "SERNOME", "SERUNIDADE", "SERFREQ", "SERNUMERICA")}
                for item in metadata[:1]
            ]
        except Exception as exc:
            selected_metadata = []
            metadata_error = f"{type(exc).__name__}: {exc}"
        else:
            metadata_error = None
        for code in MUNICIPALITIES:
            filter_expr = quote(f"TERCODIGO eq '{code}'", safe="'")
            url = f"{BASE}/ValoresSerie(SERCODIGO='{series}')?$filter={filter_expr}&$top=10"
            entry = {"series": series, "municipality_ibge_code": code, "metadata": selected_metadata,
                     "metadata_error": metadata_error, "request_url": url}
            try:
                payload = get_json(url)
                values = payload.get("value", [])
                entry["rows_returned"] = len(values)
                entry["all_rows_match_municipality"] = all(str(row.get("TERCODIGO")) == code for row in values)
                entry["sample"] = [
                    {key: row.get(key) for key in ("SERCODIGO", "TERCODIGO", "NIVNOME", "VALDATA", "VALVALOR")}
                    for row in values[:3]
                ]
                entry["next_link_present"] = "@odata.nextLink" in payload
            except Exception as exc:
                entry["error"] = f"{type(exc).__name__}: {exc}"
            evidence["tests"].append(entry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tests": [{k: v for k, v in entry.items() if k in ("series", "municipality_ibge_code", "rows_returned", "all_rows_match_municipality", "error")}
                                for entry in evidence["tests"]]}, ensure_ascii=True))


if __name__ == "__main__":
    main()
