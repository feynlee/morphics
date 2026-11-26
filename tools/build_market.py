#!/usr/bin/env python3
"""Build the market list: Content/Data/Generated/Market.json.

Rules:
- A limited morph (pass or event exclusive) is NOT listed, unless it has a market_override
  approved by Ziyue Li. The override sets its Prisms price.
- Only forms with unlock type earn or buy are sold. Earned forms list their Prisms skip price
  (Spectrum and Prisms). A bought form lists its Prisms price.
Run tools/validate_data.py first.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Content" / "Data" / "Generated" / "Market.json"


def listed(form):
    if form.get("limited"):
        return "market_override" in form
    return form["unlock"]["type"] in ("earn", "buy")


def prices(form):
    # Prism pricing is deferred (data/pricing.json). Only set prices are listed.
    if form.get("limited"):
        return {k: v for k, v in form["market_override"].items() if k == "prisms"}
    unlock = form["unlock"]
    if unlock["type"] == "earn":
        return dict(unlock["skip"])
    return {}


def main():
    forms = [json.loads(p.read_text()) for p in sorted((ROOT / "data" / "forms").glob("*.json"))]
    items = [
        {"form_id": f["id"], "starter": bool(f.get("starter")), "prices": prices(f), "prism_price": "deferred"}
        for f in forms
        if listed(f)
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(items, indent=2) + "\n")
    print(f"Wrote {len(items)} market items to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
