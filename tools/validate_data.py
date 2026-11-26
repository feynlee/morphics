#!/usr/bin/env python3
"""Validate data/forms, data/skills, data/skins against data/schema.

Uses the `jsonschema` package. Also checks cross references:
- every form has a known base, and its variant exists in that base
- every skill id in a form exists
- a form's default_skin exists and is made for the form's base (a skin never works on another base)
- a skin's base and variants exist, and an exclusive skin matches its form's base
Exit code 0 means OK. Exit code 1 means errors.
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load(kind):
    schema = json.loads((DATA / "schema" / f"{kind[:-1]}.schema.json").read_text())
    validator = Draft202012Validator(schema)
    items, errors = {}, []
    for path in sorted((DATA / kind).glob("*.json")):
        doc = json.loads(path.read_text())
        for err in validator.iter_errors(doc):
            errors.append(f"{path.relative_to(ROOT)}: {err.message}")
        if doc.get("id") in items:
            errors.append(f"{path.relative_to(ROOT)}: duplicate id {doc['id']}")
        items[doc.get("id")] = doc
    return items, errors


def main():
    forms, e1 = load("forms")
    skills, e2 = load("skills")
    skins, e3 = load("skins")
    bases, e4 = load("bases")
    errors = e1 + e2 + e3 + e4
    for form in forms.values():
        base = bases.get(form.get("base"))
        if base is None:
            errors.append(f"{form['id']}: unknown base {form.get('base')}")
        elif form.get("variant") not in [x["id"] for x in base["variants"]]:
            errors.append(f"{form['id']}: variant {form.get('variant')} is not in {base['id']}")
        for sid in form.get("skills", []):
            if sid not in skills:
                errors.append(f"{form['id']}: unknown skill {sid}")
        sid = form.get("default_skin")
        skin = skins.get(sid)
        if skin is None:
            errors.append(f"{form['id']}: unknown default_skin {sid}")
        else:
            if skin["base"] != form.get("base"):
                errors.append(f"{sid}: made for {skin['base']}, but {form['id']} is {form.get('base')}")
            if skin.get("form_id") not in (None, form["id"]):
                errors.append(f"{sid}: is exclusive to {skin['form_id']}, not {form['id']}")
            if "variants" in skin and form.get("variant") not in skin["variants"]:
                errors.append(f"{sid}: does not fit variant {form.get('variant')}")
    for skin in skins.values():
        if skin.get("base") not in bases:
            errors.append(f"{skin['id']}: unknown base {skin.get('base')}")
            continue
        known = [x["id"] for x in bases[skin["base"]]["variants"]]
        for var in skin.get("variants", []):
            if var not in known:
                errors.append(f"{skin['id']}: variant {var} is not in {skin['base']}")
        if "form_id" in skin:
            owner = forms.get(skin["form_id"])
            if owner is None:
                errors.append(f"{skin['id']}: unknown form_id {skin['form_id']}")
            elif owner["base"] != skin["base"]:
                errors.append(f"{skin['id']}: base {skin['base']} does not match {owner['id']} ({owner['base']})")
    for err in errors:
        print("ERROR", err)
    print(f"{len(bases)} bases, {len(forms)} forms, {len(skills)} skills, {len(skins)} skins, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
