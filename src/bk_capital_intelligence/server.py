"""Dependency-free HTTP MVP for BK Capital Intelligence."""
from __future__ import annotations

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .scanner import scan
from .sources import source_map

_CACHE: dict[str, object] = {"timestamp": 0.0, "rows": []}
_LOCK = threading.Lock()
CACHE_SECONDS = int(os.getenv("SCAN_CACHE_SECONDS", "900"))

HTML = """<!doctype html>
<html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>BK Capital Intelligence</title>
<style>body{font-family:Inter,system-ui,sans-serif;margin:0;background:#0b1020;color:#eef2ff}main{max-width:1200px;margin:auto;padding:36px}h1{margin-bottom:6px}.muted{color:#9aa4bd}.card{background:#141b2d;border:1px solid #26314a;border-radius:14px;padding:18px;margin:18px 0}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:10px;border-bottom:1px solid #26314a}th{color:#9aa4bd}.pill{display:inline-block;padding:4px 8px;border-radius:999px;background:#1d2943}.error{color:#ff9d9d}</style></head>
<body><main><h1>BK Capital Intelligence</h1><div class='muted'>Risk-adjusted digital-capital research engine · research mode · no custody</div>
<div class='card'><strong>Decision rule:</strong> APY is an input, not the objective. Opportunities require risk, liquidity and sustainability controls before ranking.</div>
<div id='status' class='card'>Loading live opportunity universe…</div>
<div class='card'><h2>Risk-adjusted opportunities</h2><table><thead><tr><th>Rank</th><th>Protocol</th><th>Chain</th><th>Asset</th><th>APY</th><th>Risk</th><th>Adjusted</th><th>TVL</th></tr></thead><tbody id='rows'></tbody></table></div>
<script>async function load(){try{const r=await fetch('/api/scan?limit=25');const j=await r.json();if(!r.ok)throw new Error(j.error||'scan failed');document.getElementById('status').textContent='Live scan completed at '+new Date().toLocaleString()+'. Source data is provisional and requires enrichment before any capital use.';document.getElementById('rows').innerHTML=j.data.map((x,i)=>`<tr><td>${i+1}</td><td>${x.protocol}</td><td>${x.chain}</td><td>${x.asset}</td><td>${(x.gross_apy*100).toFixed(2)}%</td><td><span class='pill'>${x.risk_score.toFixed(1)}</span></td><td>${(x.risk_adjusted_yield*100).toFixed(2)}%</td><td>$${Number(x.tvl_usd).toLocaleString()}</td></tr>`).join('')}catch(e){document.getElementById('status').innerHTML='<span class=error>'+e.message+'</span>'}}load();</script></main></body></html>"""


def _get_scan(limit: int) -> list[dict]:
    now = time.time()
    with _LOCK:
        if now - float(_CACHE["timestamp"]) < CACHE_SECONDS and _CACHE["rows"]:
            return list(_CACHE["rows"])
        rows = scan(limit=max(limit, 25))
        _CACHE["timestamp"] = now
        _CACHE["rows"] = rows
        return rows[:limit]


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send(200, HTML.encode(), "text/html; charset=utf-8")
            return
        if parsed.path == "/health":
            self._send(200, json.dumps({"status": "ok", "service": "bk-capital-intelligence"}).encode())
            return
        if parsed.path == "/api/sources":
            self._send(200, json.dumps({name: vars(spec) for name, spec in source_map().items()}).encode())
            return
        if parsed.path == "/api/scan":
            try:
                limit = max(1, min(100, int(parse_qs(parsed.query).get("limit", [25])[0])))
                rows = _get_scan(limit)
                self._send(200, json.dumps({"count": len(rows), "data": rows}, default=str).encode())
            except Exception as exc:
                self._send(502, json.dumps({"error": str(exc)}).encode())
            return
        self._send(404, b'{"error":"not found"}')

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    port = int(os.getenv("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"BK Capital Intelligence listening on {port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
