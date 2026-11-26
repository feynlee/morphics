#!/usr/bin/env python3
"""Validate data/bases, forms, skills, skins against data/schema.

Needs the `jsonschema` package. Cross checks:
- bases form a tree: parents exist, no cycles, a child id is parent id + one segment,
  a root has required_animations, a child is not "active" under a "planned" parent
- animation_overrides only name animations that the root requires
- a form's base exists
- a skin's base exists
- a form's skills exist
- a form's default_skin exists and fits the form. Narrow is the default: a skin fits its
  node only. A skin with fit="subtree" (broad, opt-in) also fits every node below it.
  A skin never works on another branch of the tree
- an exclusive skin (form_id) names a real form that it fits
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


def chain(bases, base_id):
    """Return [base_id, parent, grandparent, ...]. Stops at a root or a bad link."""
    out, seen = [], set()
    while base_id in bases and base_id not in seen:
        seen.add(base_id)
        out.append(base_id)
        base_id = bases[base_id].get("parent")
    return out


def skin_fits(bases, skin, form_base):
    """Narrow by default: exact node. fit="subtree" also allows descendants."""
    if skin.get("fit", "node") == "subtree":
        return skin.get("base") in chain(bases, form_base)
    return skin.get("base") == form_base


def check_bases(bases):
    errors = []
    for b in bases.values():
        parent_id = b.get("parent")
        if parent_id is None:
            if "required_animations" not in b:
                errors.append(f"{b['id']}: a root base needs required_animations")
            continue
        parent = bases.get(parent_id)
        if parent is None:
            errors.append(f"{b['id']}: unknown parent {parent_id}")
            continue
        if not b["id"].startswith(parent_id + "."):
            errors.append(f"{b['id']}: id must start with parent id {parent_id}.")
        if b["id"].count(".") != parent_id.count(".") + 1:
            errors.append(f"{b['id']}: id must add exactly one segment to {parent_id}")
        root_id = chain(bases, parent_id)[-1]
        required = bases[root_id].get("required_animations", [])
        for anim in b.get("animation_overrides", []):
            if anim not in required:
                errors.append(f"{b['id']}: override {anim} is not in the required animations of {root_id}")
        if parent["status"] == "planned" and b["status"] == "active":
            errors.append(f"{b['id']}: cannot be active under planned parent {parent_id}")
        if parent_id not in chain(bases, parent_id) or b["id"] in chain(bases, parent_id):
            errors.append(f"{b['id']}: parent chain has a cycle")
    return errors


def main():
    bases, e0 = load("bases")
    forms, e1 = load("forms")
    skills, e2 = load("skills")
    skins, e3 = load("skins")
    errors = e0 + e1 + e2 + e3 + check_bases(bases)

    for skin in skins.values():
        if skin.get("base") not in bases:
            errors.append(f"{skin['id']}: unknown base {skin.get('base')}")
        if "form_id" in skin:
            owner = forms.get(skin["form_id"])
            if owner is None:
                errors.append(f"{skin['id']}: unknown form_id {skin['form_id']}")
            elif not skin_fits(bases, skin, owner.get("base")):
                errors.append(f"{skin['id']}: base {skin['base']} does not fit {owner['id']} ({owner.get('base')})")

    for form in forms.values():
        if form.get("base") not in bases:
            errors.append(f"{form['id']}: unknown base {form.get('base')}")
        for sid in form.get("skills", []):
            if sid not in skills:
                errors.append(f"{form['id']}: unknown skill {sid}")
        sid = form.get("default_skin")
        skin = skins.get(sid)
        if skin is None:
            errors.append(f"{form['id']}: unknown default_skin {sid}")
            continue
        if not skin_fits(bases, skin, form.get("base")):
            errors.append(f"{sid}: made for {skin.get('base')}, which does not fit {form['id']} ({form.get('base')})")
        if skin.get("form_id") not in (None, form["id"]):
            errors.append(f"{sid}: is exclusive to {skin['form_id']}, not {form['id']}")

    for err in errors:
        print("ERROR", err)
    print(f"{len(bases)} bases, {len(forms)} forms, {len(skills)} skills, {len(skins)} skins, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
