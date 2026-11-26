#!/usr/bin/env python3
"""Validate data/forms, data/skills, data/skins against data/schema.

Uses the `jsonschema` package. Also checks cross references:
- every form has a known base, and its variant exists in that base
- every skill id in a form exists
- every skin id in a form exists and points back to that form
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
        for sid in form.get("skins", []):
            if sid not in skins:
                errors.append(f"{form['id']}: unknown skin {sid}")
            elif skins[sid]["form_id"] != form["id"]:
                errors.append(f"{sid}: form_id does not match {form['id']}")
    for err in errors:
        print("ERROR", err)
    print(f"{len(bases)} bases, {len(forms)} forms, {len(skills)} skills, {len(skins)} skins, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
