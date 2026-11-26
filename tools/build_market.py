#!/usr/bin/env python3
"""Build the market list: Content/Data/Generated/Market.json.

Rules:
- A limited morph (pass or event exclusive) is NOT listed, unless it has a market_override
  approved by Ziyue Li. The override sets its Prisms price.
- Only forms with unlock type earn or buy are sold. Earned forms list their skip prices
  (Spectrum and Prisms). A bought form lists its Prisms price.
Run tools/validate_data.py first.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Content" / "Data" / "Generated" / "Market.json"


def listed(form):
    if form.get("limited"):
        return "market_override" in form and "prisms" in form["market_override"]
    return form["unlock"]["type"] in ("earn", "buy")


def prices(form):
    if form.get("limited"):
        return {"prisms": form["market_override"]["prisms"]}
    unlock = form["unlock"]
    if unlock["type"] == "earn":
        return unlock["skip"]
    return {"prisms": unlock["cost"]}


def main():
    forms = [json.loads(p.read_text()) for p in sorted((ROOT / "data" / "forms").glob("*.json"))]
    items = [{"form_id": f["id"], "starter": bool(f.get("starter")), "prices": prices(f)} for f in forms if listed(f)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(items, indent=2) + "\n")
    print(f"Wrote {len(items)} market items to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
