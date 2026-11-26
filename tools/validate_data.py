#!/usr/bin/env python3
"""Validate data/bases, forms, skills, skins against data/schema.

Needs the `jsonschema` package. Cross checks:
- spectrum drops (data/drops.json): one entry per active top-level body type, the drop is that
  category's own spectrum, the chance is rare (at most 10 percent), amount_min <= amount_max
- skill points are never sold: data/skill_point_sources.json has only experience and quest
  channels, and no data file may attach a currency price, skip, or purchase to skill points
- two skill point tracks: a spirit-track source awards spirit_points only, a morph-track source awards
  morph_points only and requires the active morph; morph_points are never granted or spent through the
  spirit track (data/skill_point_rules.json: spirit_points spend on any owned morph, morph_points only
  on the morph that earned them)
- skill tree (data/skill_tree.json): edges name real nodes, the tree is connected (every node can be
  reached from every other, so players can move anywhere), and every form has a tree_start node
- no data file may define a spectrum conversion or exchange (spectrums cannot be converted)
- every top-level body type has a spectrum from data/spectrums.json, and no two share one
- bases form a tree: parents exist, no cycles, a child id is parent id + one segment,
  a root has required_animations, a child is not "active" under a "planned" parent
- animation_overrides only name animations that the root requires
- a starter form is never sold: its unlock type is "free" or "earn"
- exactly one starter form per top-level body type (planned types included)
- an `earn` unlock must have a skip price (always an option to skip farming), and `skip` is only for `earn`
- every earned form (morph), starters included, has a spectrum skip price
- Prism pricing is deferred (data/pricing.json): no Prism price may be set until Ziyue decides
- skins are named after the morph: a default skin has its form's name; a form-exclusive skin
  name starts with its form's name
- limited morphs: a pass or event unlock must set limited true; market_override needs limited true
  and approval by Ziyue Li (a limited morph is not sold in the market unless Ziyue says so)
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


CONVERSION_WORDS = ("convert", "conversion", "exchange", "swap_spectrum", "trade_spectrum")


def find_conversion(node, path):
    """Yield the path of any key or string value that defines a conversion."""
    if isinstance(node, dict):
        for key, value in node.items():
            if any(w in str(key).lower() for w in CONVERSION_WORDS):
                yield f"{path}.{key}"
            yield from find_conversion(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from find_conversion(value, f"{path}[{i}]")
    elif isinstance(node, str) and path.split(".")[-1] in ("type", "kind", "id"):
        if any(w in node.lower() for w in CONVERSION_WORDS):
            yield f"{path} = {node}"


def check_no_conversion():
    errors = []
    for file in sorted(DATA.rglob("*.json")):
        if "schema" in file.parts:
            continue
        for hit in find_conversion(json.loads(file.read_text()), file.relative_to(ROOT).as_posix()):
            errors.append(f"{hit}: spectrums cannot be converted into each other")
    return errors


PRICE_KEYS = {"price", "prices", "cost", "skip", "prisms", "spectrum", "currency", "buy", "purchase"}


def find_skill_point_price(node, path):
    """Yield paths where skill points are given a currency price or are bought."""
    if isinstance(node, dict):
        words = ("skill_point", "spirit_points", "morph_points")
        mentions = any(
            any(w in str(k).lower() for w in words) or (isinstance(v, str) and any(w in v.lower() for w in words))
            for k, v in node.items()
        )
        if mentions and any(k in PRICE_KEYS for k in node):
            yield path
        for key, value in node.items():
            yield from find_skill_point_price(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from find_skill_point_price(value, f"{path}[{i}]")


def check_skill_points():
    errors = []
    sources_file = DATA / "skill_point_sources.json"
    schema = json.loads((DATA / "schema" / "skill_point_source.schema.json").read_text())
    doc = json.loads(sources_file.read_text())
    for err in Draft202012Validator(schema).iter_errors(doc):
        errors.append(f"data/skill_point_sources.json: {err.message}")
    for s in doc.get("sources", []):
        if s.get("track") == "spirit" and s.get("awards") != "spirit_points":
            errors.append(f"{s['id']}: the spirit track cannot grant {s.get('awards')}. Morph points are never granted through the player track")
        if s.get("track") == "morph":
            if s.get("awards") != "morph_points":
                errors.append(f"{s['id']}: the morph track must grant morph_points, not {s.get('awards')}")
            if s.get("requires_active_morph") is not True:
                errors.append(f"{s['id']}: a morph-track source must require playing that morph")
    rules_schema = json.loads((DATA / "schema" / "skill_point_rules.schema.json").read_text())
    rules = json.loads((DATA / "skill_point_rules.json").read_text())
    for err in Draft202012Validator(rules_schema).iter_errors(rules):
        errors.append(f"data/skill_point_rules.json: {err.message}")
    ids = [s.get("id") for s in doc.get("sources", [])]
    if len(ids) != len(set(ids)):
        errors.append("data/skill_point_sources.json: duplicate source id")
    for file in sorted(DATA.rglob("*.json")):
        if "schema" in file.parts:
            continue
        for hit in find_skill_point_price(json.loads(file.read_text()), file.relative_to(ROOT).as_posix()):
            errors.append(f"{hit}: skill points cannot be bought or priced in currency")
    return errors


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
    errors = e0 + e1 + e2 + e3 + check_bases(bases) + check_no_conversion() + check_skill_points()

    spectrums = json.loads((DATA / "spectrums.json").read_text())
    spectrum_schema = json.loads((DATA / "schema" / "spectrum.schema.json").read_text())
    for err in Draft202012Validator(spectrum_schema).iter_errors(spectrums):
        errors.append(f"data/spectrums.json: {err.message}")
    spectrum_ids = [s["id"] for s in spectrums]
    used = {}
    for b in bases.values():
        if "parent" in b:
            if "spectrum" in b:
                errors.append(f"{b['id']}: only a top-level body type sets a spectrum")
            continue
        sp = b.get("spectrum")
        if sp not in spectrum_ids:
            errors.append(f"{b['id']}: unknown or missing spectrum {sp}")
        elif sp in used:
            errors.append(f"{b['id']}: spectrum {sp} is already used by {used[sp]}")
        else:
            used[sp] = b["id"]

    for skin in skins.values():
        if skin.get("base") not in bases:
            errors.append(f"{skin['id']}: unknown base {skin.get('base')}")
        if "form_id" in skin:
            owner = forms.get(skin["form_id"])
            if owner is None:
                errors.append(f"{skin['id']}: unknown form_id {skin['form_id']}")
            elif not skin["name"].startswith(owner["name"]):
                errors.append(f"{skin['id']}: a form-exclusive skin is named after its morph ({owner['name']})")
            elif not skin_fits(bases, skin, owner.get("base")):
                errors.append(f"{skin['id']}: base {skin['base']} does not fit {owner['id']} ({owner.get('base')})")

    for form in forms.values():
        if form.get("base") not in bases:
            errors.append(f"{form['id']}: unknown base {form.get('base')}")
        for sid in form.get("skills", []):
            if sid not in skills:
                errors.append(f"{form['id']}: unknown skill {sid}")
        if form.get("starter") and form["unlock"]["type"] not in ("free", "earn"):
            errors.append(f"{form['id']}: a starter form must be free or earned, not {form['unlock']['type']}")
        utype = form["unlock"]["type"]
        if utype in ("pass", "event") and not form.get("limited"):
            errors.append(f"{form['id']}: a {utype} exclusive must set limited: true")
        if "market_override" in form:
            if not form.get("limited"):
                errors.append(f"{form['id']}: market_override is only for limited morphs")
            if pricing.get("prism_pricing") != "deferred" and "prisms" not in form["market_override"]:
                errors.append(f"{form['id']}: market_override needs a prisms price")
            if form["market_override"].get("approved_by") != "Ziyue Li":
                errors.append(f"{form['id']}: market_override must be approved by Ziyue Li")
        sid = form.get("default_skin")
        skin = skins.get(sid)
        if skin is None:
            errors.append(f"{form['id']}: unknown default_skin {sid}")
            continue
        if not skin_fits(bases, skin, form.get("base")):
            errors.append(f"{sid}: made for {skin.get('base')}, which does not fit {form['id']} ({form.get('base')})")
        if skin.get("name") != form.get("name") and sid == form.get("default_skin") and skin.get("form_id") is None:
            errors.append(f"{sid}: a default skin is named after its morph ({form.get('name')})")
        if skin.get("form_id") not in (None, form["id"]):
            errors.append(f"{sid}: is exclusive to {skin['form_id']}, not {form['id']}")

    pricing = json.loads((DATA / "pricing.json").read_text())
    for item in list(forms.values()) + list(skins.values()):
        unlock = item.get("unlock", {})
        if unlock.get("type") == "earn" and "skip" not in unlock:
            errors.append(f"{item['id']}: an earn unlock needs a skip price")
        if unlock.get("type") != "earn" and "skip" in unlock:
            errors.append(f"{item['id']}: skip is only for earn unlocks")
        if unlock.get("type") == "earn" and item["id"] in forms and "spectrum" not in unlock.get("skip", {}):
            errors.append(f"{item['id']}: an earned form needs a spectrum skip price")
        if pricing.get("prism_pricing") == "deferred":
            if "prisms" in unlock.get("skip", {}):
                errors.append(f"{item['id']}: Prism pricing is deferred. Do not set a Prism price yet")
            if "prisms" in item.get("market_override", {}):
                errors.append(f"{item['id']}: Prism pricing is deferred. Do not set a market Prism price yet")

    drops = json.loads((DATA / "drops.json").read_text())
    drop_schema = json.loads((DATA / "schema" / "drop.schema.json").read_text())
    for err in Draft202012Validator(drop_schema).iter_errors(drops):
        errors.append(f"data/drops.json: {err.message}")
    seen_drop = {}
    for entry in drops:
        root = bases.get(entry.get("enemy_base"))
        if root is None or "parent" in root:
            errors.append(f"data/drops.json: {entry.get('enemy_base')} is not a top-level body type")
            continue
        if entry.get("enemy_base") in seen_drop:
            errors.append(f"data/drops.json: more than one drop entry for {entry['enemy_base']}")
        seen_drop[entry["enemy_base"]] = True
        if entry.get("spectrum") != root.get("spectrum"):
            errors.append(f"data/drops.json: {root['id']} drops {entry.get('spectrum')}, but its spectrum is {root.get('spectrum')}")
        if entry.get("amount_min", 1) > entry.get("amount_max", 1):
            errors.append(f"data/drops.json: {root['id']} has amount_min above amount_max")
    for b in bases.values():
        if "parent" not in b and b.get("status") == "active" and b["id"] not in seen_drop:
            errors.append(f"data/drops.json: active body type {b['id']} needs a drop entry")

    tree = json.loads((DATA / "skill_tree.json").read_text())
    tree_schema = json.loads((DATA / "schema" / "skill_tree.schema.json").read_text())
    for err in Draft202012Validator(tree_schema).iter_errors(tree):
        errors.append(f"data/skill_tree.json: {err.message}")
    node_ids = {n["id"] for n in tree["nodes"]}
    if len(node_ids) != len(tree["nodes"]):
        errors.append("data/skill_tree.json: duplicate node id")
    graph = {n: set() for n in node_ids}
    for a, b in tree["edges"]:
        if a not in node_ids or b not in node_ids:
            errors.append(f"data/skill_tree.json: edge {a} - {b} names an unknown node")
        else:
            graph[a].add(b)
            graph[b].add(a)
    if node_ids:
        start = next(iter(sorted(node_ids)))
        reached, todo = {start}, [start]
        while todo:
            for nxt in graph[todo.pop()]:
                if nxt not in reached:
                    reached.add(nxt)
                    todo.append(nxt)
        for lost in sorted(node_ids - reached):
            errors.append(f"data/skill_tree.json: {lost} cannot be reached. The tree must be connected")
    for form in forms.values():
        if form.get("tree_start") not in node_ids:
            errors.append(f"{form['id']}: tree_start {form.get('tree_start')} is not a node in the skill tree")

    starters = {}
    for form in forms.values():
        if form.get("starter") and form.get("base") in bases:
            starters.setdefault(chain(bases, form["base"])[-1], []).append(form["id"])
    for b in bases.values():
        if "parent" in b:
            continue
        found = starters.get(b["id"], [])
        if len(found) > 1:
            errors.append(f"{b['id']}: more than one starter form: {', '.join(found)}")
        elif not found:
            errors.append(f"{b['id']}: needs exactly one starter form, found none")

    for err in errors:
        print("ERROR", err)
    print(f"{len(bases)} bases, {len(forms)} forms, {len(skills)} skills, {len(skins)} skins, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
