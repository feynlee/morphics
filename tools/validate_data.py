#!/usr/bin/env python3
"""Validate data/bases, forms, skills, skins against data/schema.

Needs the `jsonschema` package. Cross checks:
- boss drops (data/boss_drops.json): every earned morph has one boss entry. A boss rolls (solo chance) on a
  crafting material loot table (data/loot_tables.json). Loot table weights sum to 100, the table holds exactly
  the recipe's components, never a Morphic, never a Spectrum, each boss table belongs to one boss, and other tables are allowed
- Spectrums drop only from wild enemies (data/drops.json, source wild_enemy), never from bosses
- Spectrum drops match on the subcategory color (match: subcategory_color): a wild enemy of any size
  under a subcategory (for example small canine) drops the Spectrum of that subcategory (canine: Green)
- spectrum drops (data/drops.json): one entry per color that a subcategory uses, the chance is rare
  (at most 10 percent), amount_min <= amount_max
- skill points are never sold: data/skill_point_sources.json has only experience and quest
  channels, and no data file may attach a currency price, skip, or purchase to skill points
- two skill point tracks: a spirit-track source awards spirit_points only, a morph-track source awards
  morph_points only and requires the active morph; morph_points are never granted or spent through the
  spirit track (data/skill_point_rules.json: spirit_points spend on any owned morph, morph_points only
  on the morph that earned them)
- no cap on spirit points or morph points (data/skill_point_rules.json); spirit points are shared by
  every morph; base-variant tree nodes name a real body type and every form has one it can invest in
- Prisms are market-only (data/pricing.json prisms_use is market_only): the word prisms may appear in
  data only as a market price (unlock.skip.prisms or market_override.prisms on a form or skin). Any other
  use, such as in respec, drops, skills, the skill tree, or skill points, is rejected
- respec cost (data/respec.json): a respec cost is declared, in Spectrums. While pending the amount is
  null. Once set it must be a whole number of at least 1
- skill tree (data/skill_tree.json): edges name real nodes, the tree is connected (every node can be
  reached from every other, so players can move anywhere), and every form has a tree_start node
- no data file may define a spectrum conversion or exchange (spectrums cannot be converted)
- data/spectrums.json holds exactly six colors: red, orange, yellow, green, blue, purple
- body types form three levels: top category (base.walker, base.swimmer, base.flyer) > subcategory > size.
  A top category has no rig fields and no spectrum. A subcategory has rig, mesh, gait, skeleton,
  required_animations and a spectrum from data/spectrums.json (subcategories may share a color; a color
  may have no subcategory). A size has no rig fields and no spectrum. Sizes sit under a subcategory only
- bases form a tree: parents exist, no cycles, a child id is parent id + one segment,
  a child is not "active" under a "planned" parent
- animation_overrides only name animations that the subcategory requires
- every size has a height range (height: reference_m, variation_pct, min_m, max_m). It is only for sizes, and
  min_m and max_m must match the references plus or minus the variation (within 0.01 m)
- a starter form is never sold: its unlock type is "free" or "earn"
- at most one starter form per subcategory, and every color used by an active subcategory has at least one starter
- an `earn` unlock must have a skip price (always an option to skip farming), and `skip` is only for `earn`
- every earned form (morph), starters included, has a Prisms skip price (the value is "deferred" until
  Prism pricing is set), and no unlock or market price uses Spectrums (Spectrums are in-game currency only)
- every earned form (morph) lists how it is crafted (unlock.craft): a Morphic named '<morph name> Morphic',
  a source boss, at least one component with a count, and a Spectrum amount in the
  form's own category Spectrum (a boss id is boss.<form short id>; components are item.<form short id>.<part>)
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


PRISMS_OK = ("unlock.skip.prisms", "market_override.prisms")


def find_prisms_outside_market(node, path):
    """Yield paths where Prisms appear outside a market price."""
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}"
            if str(key).lower() == "prisms" and not here.endswith(PRISMS_OK):
                yield here
            yield from find_prisms_outside_market(value, here)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from find_prisms_outside_market(value, f"{path}[{i}]")
    elif isinstance(node, str) and node.lower() in ("prisms", "prism"):
        yield f"{path} = {node}"


def check_prisms_market_only():
    errors = []
    for file in sorted(DATA.rglob("*.json")):
        if "schema" in file.parts or file.name == "pricing.json":
            continue
        for hit in find_prisms_outside_market(json.loads(file.read_text()), file.relative_to(ROOT).as_posix()):
            errors.append(f"{hit}: Prisms are only used to buy things from the market")
    return errors


TOP_CATEGORIES = ("base.walker", "base.swimmer", "base.flyer")
RIG_FIELDS = ("rig", "mesh", "gait", "skeleton", "required_animations")


def level(bases, base_id):
    """0 = top category, 1 = subcategory, 2 = size, 3 or more = too deep."""
    return len(chain(bases, base_id)) - 1


def subcategory_of(bases, base_id):
    """The subcategory id that holds this node (itself, or its parent for a size)."""
    ids = chain(bases, base_id)
    return ids[-2] if len(ids) >= 2 else None


def color_of(bases, base_id):
    sub = subcategory_of(bases, base_id)
    return bases[sub].get("spectrum") if sub else None


def check_height(b):
    h = b.get("height")
    if not h:
        return []
    errors = []
    refs = list(h.get("reference_m", {}).values())
    if not refs:
        return [f"{b['id']}: height needs at least one reference"]
    low = min(refs) * (1 - h.get("variation_pct", 0) / 100)
    high = max(refs) * (1 + h.get("variation_pct", 0) / 100)
    if abs(h.get("min_m", 0) - low) > 0.01:
        errors.append(f"{b['id']}: height min_m should be {low:.2f} for these references and variation")
    if abs(h.get("max_m", 0) - high) > 0.01:
        errors.append(f"{b['id']}: height max_m should be {high:.2f} for these references and variation")
    return errors


def check_bases(bases):
    errors = []
    for b in bases.values():
        lvl = level(bases, b["id"])
        parent_id = b.get("parent")
        if parent_id is None:
            if b["id"] not in TOP_CATEGORIES:
                errors.append(f"{b['id']}: a top category must be one of {', '.join(TOP_CATEGORIES)}")
            for field in RIG_FIELDS + ("spectrum",):
                if field in b:
                    errors.append(f"{b['id']}: a top category has no {field}. Subcategories own skeleton, gait, mesh and color")
            continue
        parent = bases.get(parent_id)
        if parent is None:
            errors.append(f"{b['id']}: unknown parent {parent_id}")
            continue
        if not b["id"].startswith(parent_id + "."):
            errors.append(f"{b['id']}: id must start with parent id {parent_id}.")
        if b["id"].count(".") != parent_id.count(".") + 1:
            errors.append(f"{b['id']}: id must add exactly one segment to {parent_id}")
        if parent_id not in chain(bases, parent_id) or b["id"] in chain(bases, parent_id):
            errors.append(f"{b['id']}: parent chain has a cycle")
            continue
        if lvl == 1:
            for field in RIG_FIELDS + ("spectrum",):
                if field not in b:
                    errors.append(f"{b['id']}: a subcategory needs {field}")
        elif lvl == 2:
            for field in RIG_FIELDS + ("spectrum",):
                if field in b:
                    errors.append(f"{b['id']}: a size has no {field}. It inherits from {parent_id}")
            if "height" not in b:
                errors.append(f"{b['id']}: a size needs a height range (height)")
            errors.extend(check_height(b))
            required = parent.get("required_animations", [])
            for anim in b.get("animation_overrides", []):
                if anim not in required:
                    errors.append(f"{b['id']}: override {anim} is not in the required animations of {parent_id}")
        else:
            errors.append(f"{b['id']}: too deep. Use top category > subcategory > size")
        if parent["status"] == "planned" and b["status"] == "active":
            errors.append(f"{b['id']}: cannot be active under planned parent {parent_id}")
        if lvl != 2 and "height" in b:
            errors.append(f"{b['id']}: only a size has a height range")
    return errors


def main():
    bases, e0 = load("bases")
    forms, e1 = load("forms")
    skills, e2 = load("skills")
    skins, e3 = load("skins")
    errors = e0 + e1 + e2 + e3 + check_bases(bases) + check_no_conversion() + check_skill_points() + check_prisms_market_only()

    spectrums = json.loads((DATA / "spectrums.json").read_text())
    spectrum_schema = json.loads((DATA / "schema" / "spectrum.schema.json").read_text())
    for err in Draft202012Validator(spectrum_schema).iter_errors(spectrums):
        errors.append(f"data/spectrums.json: {err.message}")
    spectrum_ids = [s["id"] for s in spectrums]
    if spectrum_ids != ["red", "orange", "yellow", "green", "blue", "purple"]:
        errors.append(f"data/spectrums.json: the colors must be red, orange, yellow, green, blue, purple (found {', '.join(spectrum_ids)})")
    for b in bases.values():
        if level(bases, b["id"]) == 1 and b.get("spectrum") not in spectrum_ids:
            errors.append(f"{b['id']}: unknown or missing spectrum {b.get('spectrum')}")

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
        craft = form["unlock"].get("craft")
        if utype == "earn" and craft is None:
            errors.append(f"{form['id']}: an earned morph needs unlock.craft (components and a Spectrum amount)")
        if utype != "earn" and craft is not None:
            errors.append(f"{form['id']}: unlock.craft is only for earned morphs")
        if craft is not None:
            short = form["id"].split(".", 1)[-1]
            if craft.get("morphic") != f"{form.get('name')} Morphic":
                errors.append(f"{form['id']}: the crafted item is named '{form.get('name')} Morphic'")
            if craft.get("source_boss") != f"boss.{short}":
                errors.append(f"{form['id']}: source_boss must be boss.{short}")
            own = color_of(bases, form.get("base"))
            if craft.get("spectrum", {}).get("id") != own:
                errors.append(f"{form['id']}: craft Spectrum must be the form's own category Spectrum ({own})")
            seen_items = set()
            for comp in craft.get("components", []):
                if not str(comp.get("item", "")).startswith(f"item.{short}."):
                    errors.append(f"{form['id']}: component {comp.get('item')} must start with item.{short}.")
                if comp.get("item") in seen_items:
                    errors.append(f"{form['id']}: component {comp.get('item')} is listed twice")
                seen_items.add(comp.get("item"))
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
        if "spectrum" in unlock.get("skip", {}) or "spectrum" in item.get("market_override", {}):
            errors.append(f"{item['id']}: Spectrums are not a market or skip price. Use Prisms")
        if unlock.get("type") == "earn" and "prisms" not in unlock.get("skip", {}):
            errors.append(f"{item['id']}: an earned item needs a Prisms skip price")
        if pricing.get("prism_pricing") == "deferred":
            if unlock.get("skip", {}).get("prisms", "deferred") != "deferred":
                errors.append(f"{item['id']}: Prism pricing is deferred. Do not set a Prism price yet")
            if "prisms" in item.get("market_override", {}):
                errors.append(f"{item['id']}: Prism pricing is deferred. Do not set a market Prism price yet")

    loot = json.loads((DATA / "loot_tables.json").read_text())
    loot_schema = json.loads((DATA / "schema" / "loot_table.schema.json").read_text())
    for err in Draft202012Validator(loot_schema).iter_errors(loot):
        errors.append(f"data/loot_tables.json: {err.message}")
    tables = {}
    for table in loot:
        if table.get("id") in tables:
            errors.append(f"data/loot_tables.json: duplicate table {table.get('id')}")
        tables[table.get("id")] = table
        total = sum(e.get("weight", 0) for e in table.get("entries", []))
        if total != 100:
            errors.append(f"data/loot_tables.json: {table.get('id')} weights sum to {total}, not 100")
        names = [e.get("item") for e in table.get("entries", [])]
        if len(names) != len(set(names)):
            errors.append(f"data/loot_tables.json: {table.get('id')} lists an item twice")
        for item in names:
            low = str(item).lower()
            if "morphic" in low:
                errors.append(f"data/loot_tables.json: {table.get('id')} holds {item}. A loot table never holds a Morphic (it would skip farming)")
            if "spectrum" in low:
                errors.append(f"data/loot_tables.json: {table.get('id')} holds {item}. Spectrums drop only from wild enemies")

    boss_drops = json.loads((DATA / "boss_drops.json").read_text())
    boss_schema = json.loads((DATA / "schema" / "boss_drops.schema.json").read_text())
    for err in Draft202012Validator(boss_schema).iter_errors(boss_drops):
        errors.append(f"data/boss_drops.json: {err.message}")
    by_boss = {}
    used_tables = set()
    for entry in boss_drops:
        if entry.get("boss") in by_boss:
            errors.append(f"data/boss_drops.json: more than one entry for {entry.get('boss')}")
        by_boss[entry.get("boss")] = entry
        if entry.get("loot_table") not in tables:
            errors.append(f"data/boss_drops.json: {entry.get('boss')} names unknown loot table {entry.get('loot_table')}")
        elif entry["loot_table"] in used_tables:
            errors.append(f"data/boss_drops.json: loot table {entry['loot_table']} is used by more than one boss")
        used_tables.add(entry.get("loot_table"))
    needed = set()
    for form in forms.values():
        craft = form["unlock"].get("craft")
        if not craft:
            continue
        needed.add(craft.get("source_boss"))
        entry = by_boss.get(craft.get("source_boss"))
        if entry is None:
            errors.append(f"{form['id']}: no entry in data/boss_drops.json for {craft.get('source_boss')}")
            continue
        if entry.get("form_id") != form["id"]:
            errors.append(f"data/boss_drops.json: {entry.get('boss')} must name {form['id']}")
        table = tables.get(entry.get("loot_table"))
        if table is not None:
            parts = {c.get("item") for c in craft.get("components", [])}
            held = {e.get("item") for e in table.get("entries", [])}
            if held != parts:
                errors.append(f"data/loot_tables.json: {table.get('id')} must hold exactly the components of {form['id']}")
    for boss in by_boss:
        if boss not in needed:
            errors.append(f"data/boss_drops.json: {boss} is not the source boss of any earned morph")
    # Other loot tables (wild enemies, other crafting and materials) are planned and not designed yet.
    # So a table that no boss uses is allowed. The weight, no-Morphic, and no-Spectrum rules still apply to every table.

    drops = json.loads((DATA / "drops.json").read_text())
    drop_schema = json.loads((DATA / "schema" / "drop.schema.json").read_text())
    for err in Draft202012Validator(drop_schema).iter_errors(drops):
        errors.append(f"data/drops.json: {err.message}")
    seen_drop = {}
    for entry in drops:
        if entry.get("source") != "wild_enemy":
            errors.append(f"data/drops.json: Spectrums drop only from wild enemies, not {entry.get('source')}")
        color = entry.get("spectrum")
        if color not in spectrum_ids:
            errors.append(f"data/drops.json: unknown Spectrum {color}")
            continue
        if color in seen_drop:
            errors.append(f"data/drops.json: more than one drop entry for {color}")
        seen_drop[color] = True
        if entry.get("amount_min", 1) > entry.get("amount_max", 1):
            errors.append(f"data/drops.json: {color} has amount_min above amount_max")
    # A wild enemy of a subcategory drops the Spectrum of that subcategory. So every color in use needs an entry.
    for b in bases.values():
        if level(bases, b["id"]) == 1 and b.get("spectrum") not in seen_drop:
            errors.append(f"data/drops.json: {b['id']} uses {b.get('spectrum')}, which has no drop entry")
    for color in seen_drop:
        if not any(level(bases, b["id"]) == 1 and b.get("spectrum") == color for b in bases.values()):
            errors.append(f"data/drops.json: {color} is dropped, but no subcategory uses it")

    if pricing.get("prisms_use") != "market_only":
        errors.append("data/pricing.json: prisms_use must be market_only (Prisms are a market resource, not an in-game cost)")
    respec = json.loads((DATA / "respec.json").read_text())
    respec_schema = json.loads((DATA / "schema" / "respec.schema.json").read_text())
    for err in Draft202012Validator(respec_schema).iter_errors(respec):
        errors.append(f"data/respec.json: {err.message}")
    cost = respec.get("cost", {})
    if cost.get("status") == "pending" and cost.get("amount") is not None:
        errors.append("data/respec.json: the respec cost is pending, so the amount must be null")
    if cost.get("status") == "set" and not isinstance(cost.get("amount"), int):
        errors.append("data/respec.json: the respec cost is set, so it needs a whole-number amount")

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
    for node in tree["nodes"]:
        if "restricted_to_base" in node and node["restricted_to_base"] not in bases:
            errors.append(f"{node['id']}: restricted_to_base {node['restricted_to_base']} is not a body type")
    restricted = {n["restricted_to_base"] for n in tree["nodes"] if "restricted_to_base" in n}
    for form in forms.values():
        if not restricted.intersection(chain(bases, form.get("base"))):
            errors.append(f"{form['id']}: the skill tree has no base-variant node for body type {form.get('base')}")
        if form.get("tree_start") not in node_ids:
            errors.append(f"{form['id']}: tree_start {form.get('tree_start')} is not a node in the skill tree")

    starters = {}
    for form in forms.values():
        if form.get("starter") and form.get("base") in bases:
            starters.setdefault(subcategory_of(bases, form["base"]), []).append(form["id"])
    for sub_id, found in starters.items():
        if len(found) > 1:
            errors.append(f"{sub_id}: more than one starter form: {', '.join(found)}")
    colors_with_starter = {bases[sub_id].get("spectrum") for sub_id in starters if sub_id in bases}
    for b in bases.values():
        if level(bases, b["id"]) == 1 and b.get("status") == "active" and b.get("spectrum") not in colors_with_starter:
            errors.append(f"{b['id']}: its color {b.get('spectrum')} has no starter form")
            colors_with_starter.add(b.get("spectrum"))

    for err in errors:
        print("ERROR", err)
    print(f"{len(bases)} bases, {len(forms)} forms, {len(skills)} skills, {len(skins)} skins, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
