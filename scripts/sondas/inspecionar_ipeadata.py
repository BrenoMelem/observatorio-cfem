"""Save headers and a short prefix of a filtered IPEADATA response."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


base = "http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='ADMISNC')"
query = urlencode({"$filter": "TERCODIGO eq '1502152'", "$top": "1"})
url = f"{base}?{query}"
request = Request(url, headers={"User-Agent": "Observatorio-CFEM-validation/0.1"})
with urlopen(request, timeout=90) as response:
    prefix = response.read(500).decode("utf-8", "replace")
    first_code = re.search(r'"TERCODIGO"\s*:\s*"([^"]+)"', prefix)
    result = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "request_url": url,
        "requested_municipality_code": "1502152",
        "requested_top": 1,
        "http_status": response.status,
        "content_length_bytes": int(response.headers.get("Content-Length", "0")),
        "first_returned_municipality_code": first_code.group(1) if first_code else None,
        "filter_applied_to_first_row": bool(first_code and first_code.group(1) == "1502152"),
        "response_prefix": prefix,
    }
out = Path("output/diagnostico-ipeadata-filtro-2026-10-15.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: value for key, value in result.items() if key != "response_prefix"}, ensure_ascii=False))
