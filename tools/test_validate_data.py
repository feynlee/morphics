#!/usr/bin/env python3
"""Negative tests for tools/validate_data.py.

Each case copies data/ and tools/ to a temp folder, breaks one rule, and expects the validator to fail
with a message that contains the given text. The unbroken data must pass.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def edit(path, fn):
    doc = json.loads(path.read_text())
    fn(doc)
    path.write_text(json.dumps(doc, indent=2) + "\n")


def run(tmp):
    return subprocess.run([sys.executable, str(tmp / "tools" / "validate_data.py")], capture_output=True, text=True)


def case(name, expect, mutate):
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        shutil.copytree(ROOT / "data", tmp / "data")
        shutil.copytree(ROOT / "tools", tmp / "tools")
        mutate(tmp / "data")
        res = run(tmp)
        ok = res.returncode == 1 and expect in res.stdout
        print(("PASS " if ok else "FAIL ") + name)
        if not ok:
            print(res.stdout[-800:])
        return ok


def add_base(d, new):
    (d / "bases" / (new["id"].replace("base.", "", 1) + ".json")).write_text(json.dumps(new, indent=2) + "\n")


def sub(**kw):
    base = {"id": "base.walker.test", "name": "Test", "parent": "base.walker", "status": "planned", "rig": "rig.walker.test",
            "mesh": "mesh.walker.test", "gait": "x", "skeleton": "", "required_animations": ["idle"], "spectrum": "green"}
    base.update(kw)
    return base


def main():
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        shutil.copytree(ROOT / "data", tmp / "data")
        shutil.copytree(ROOT / "tools", tmp / "tools")
        res = run(tmp)
        good = res.returncode == 0
        print(("PASS " if good else "FAIL ") + "unbroken data passes")
        if not good:
            print(res.stdout[-800:])
    results = [good]
    results.append(case("top category with a rig", "a top category has no rig",
        lambda d: edit(d / "bases/walker.json", lambda b: b.update(rig="rig.walker"))))
    results.append(case("top category with a spectrum", "a top category has no spectrum",
        lambda d: edit(d / "bases/walker.json", lambda b: b.update(spectrum="green"))))
    results.append(case("unknown top category", "must be one of",
        lambda d: add_base(d, {"id": "base.crawler", "name": "Crawler", "status": "planned"})))
    results.append(case("subcategory without a rig", "needs rig",
        lambda d: add_base(d, {k: v for k, v in sub().items() if k != "rig"})))
    results.append(case("subcategory without a spectrum", "needs spectrum",
        lambda d: add_base(d, {k: v for k, v in sub().items() if k != "spectrum"})))
    results.append(case("subcategory with an unknown color", "unknown or missing spectrum",
        lambda d: add_base(d, sub(spectrum="pink"))))
    results.append(case("size with a rig", "a size has no rig",
        lambda d: edit(d / "bases/walker.canine.small.json", lambda b: b.update(rig="rig.x.y"))))
    results.append(case("size with a spectrum", "a size has no spectrum",
        lambda d: edit(d / "bases/walker.canine.small.json", lambda b: b.update(spectrum="red"))))
    results.append(case("size directly under a top category", "a subcategory needs",
        lambda d: add_base(d, {"id": "base.walker.tiny", "name": "Tiny", "parent": "base.walker", "status": "planned"})))
    results.append(case("size under a size", "too deep",
        lambda d: add_base(d, {"id": "base.walker.canine.small.mini", "name": "Mini", "parent": "base.walker.canine.small", "status": "planned"})))
    results.append(case("override not in the subcategory list", "is not in the required animations",
        lambda d: edit(d / "bases/walker.canine.small.json", lambda b: b.update(animation_overrides=["fly"]))))
    results.append(case("spectrum set is not the six colors", "the colors must be",
        lambda d: edit(d / "spectrums.json", lambda s: s.pop())))
    results.append(case("color in use has no drop entry", "has no drop entry",
        lambda d: edit(d / "drops.json", lambda x: x.pop(0))))
    results.append(case("drop for a color nobody uses", "no subcategory uses it",
        lambda d: edit(d / "drops.json", lambda x: x.append({"source": "wild_enemy", "match": "subcategory_color", "spectrum": "purple", "chance": 0.03, "amount_min": 1, "amount_max": 3}))))
    results.append(case("two drop entries for one color", "more than one drop entry",
        lambda d: edit(d / "drops.json", lambda x: x.append(dict(x[0])))))
    results.append(case("drop from a boss", "Spectrums drop only from wild enemies",
        lambda d: edit(d / "drops.json", lambda x: x[0].update(source="boss"))))
    results.append(case("craft Spectrum is not the form's color", "craft Spectrum must be",
        lambda d: edit(d / "forms/hawk.json", lambda f: f["unlock"]["craft"]["spectrum"].update(id="red"))))
    results.append(case("two starters in one subcategory", "more than one starter",
        lambda d: edit(d / "forms/ember_fox.json", lambda f: f.update(starter=True, base="base.walker.canine.medium"))))
    results.append(case("active color with no starter", "has no starter form",
        lambda d: edit(d / "forms/wanderer.json", lambda f: f.update(starter=False))))
    results.append(case("height range does not match the variation", "height min_m should be",
        lambda d: edit(d / "bases/walker.humanoid.medium.json", lambda b: b["height"].update(min_m=1.2))))
    results.append(case("height on a subcategory", "only a size has a height range",
        lambda d: edit(d / "bases/walker.canine.json", lambda b: b.update(height={"basis": "shoulder", "reference_m": {"avg": 0.5}, "variation_pct": 0, "min_m": 0.5, "max_m": 0.5}))))
    bad = results.count(False)
    print(f"{len(results) - bad} passed, {bad} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
