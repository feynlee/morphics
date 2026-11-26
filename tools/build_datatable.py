#!/usr/bin/env python3
"""Build the Unreal Data Table JSON from data/forms/*.json.

Output: Content/Data/Generated/Forms.json
Import it in the editor: Content Browser > Import > pick FMorphFormRow as the row type.
Unreal reads a JSON array of objects. Each object has a "Name" key (the row name).
The other keys match the property names in Source/Morphics/MorphFormRow.h.
Run tools/validate_data.py first.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Content" / "Data" / "Generated" / "Forms.json"


def row(form):
    stats = form["base_stats"]
    return {
        "Name": form["id"].replace(".", "_"),
        "FormId": form["id"],
        "DisplayName": form["name"],
        "Role": form["role"],
        "Rarity": form["rarity"],
        "BaseId": form["base"],
        "Hp": stats["hp"],
        "Speed": stats["speed"],
        "Power": stats["power"],
        "Defense": stats["defense"],
        "SkillIds": form["skills"],
        "DefaultSkinId": form["default_skin"],
        "Model": form.get("model", ""),
        "UnlockType": form["unlock"]["type"],
        "CraftMorphic": form["unlock"].get("craft", {}).get("morphic", ""),
        "CraftSourceBoss": form["unlock"].get("craft", {}).get("source_boss", ""),
        "CraftBossDropChanceSolo": form["unlock"].get("craft", {}).get("boss_drop_chance_solo", 0.0),
        "CraftComponents": [
            {"Item": c["item"], "Count": c["count"]} for c in form["unlock"].get("craft", {}).get("components", [])
        ],
        "CraftSpectrumId": form["unlock"].get("craft", {}).get("spectrum", {}).get("id", ""),
        "CraftSpectrumAmount": form["unlock"].get("craft", {}).get("spectrum", {}).get("amount", 0),
    }


def main():
    forms = [json.loads(p.read_text()) for p in sorted((ROOT / "data" / "forms").glob("*.json"))]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps([row(f) for f in forms], indent=2) + "\n")
    print(f"Wrote {len(forms)} rows to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
