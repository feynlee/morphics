# M1 prototype: scope and status

Goal: one arena, 3 forms, the morph action, Steam login. No store.

## Proof of concept scope (Ziyue, 2026-11-26)
First we build a proof of concept with three forms, one per top group of the body-type tree:
- **Humanoid:** a human (`base.walker.humanoid.medium`, form Wanderer, which may become a plain Human). Red.
- **Beast:** a canine (`base.walker.canine.medium`, form Wolf). Green.
- **Winged:** a hawk (`base.flyer.flier.medium`, form Hawk). Yellow.

The other subcategories, forms and colors stay in the data as planned entries. They are not built until the proof of concept works. The Hawk subcategory (Flier) is `planned` in the data. It becomes `active` when the Flier rig and art exist.


## Done in this scaffold
- Unreal project file `Morphics.uproject` (engine 5.8, Steam subsystem plugins on).
- C++ game module skeleton in `Source/Morphics/`.
- `FMorphFormRow`: the Data Table row struct for forms.
- JSON data pipeline:
  1. Edit `data/forms`, `data/skills`, `data/skins`.
  2. `python tools/validate_data.py` checks schema and cross references.
  3. `python tools/build_datatable.py` writes `Content/Data/Generated/Forms.json`.
  4. Import that file in the editor as a Data Table (row type `MorphFormRow`).
- CI (`.github/workflows/data.yml`) runs steps 2 and 3 on each PR.
- a body-type tree (`data/bases`: 3 top categories, 11 subcategories and their sizes) and 8 placeholder forms with original names: four plain starters (Wanderer, Wolf, Hawk, Raptor), three farmable variants (Ember Fox, Stone Tortoise, Gale Heron), and one limited pass morph (Prism Stag).
- M1 note: Hawk and Raptor use planned bases, so they are data only in M1. Playable M1 forms need the humanoid and beast bases.

## Not verified yet
- The C++ module was NOT compiled. The scaffold was written without Unreal installed.
  First task on the dev PC: open `Morphics.uproject` in UE 5.8.4, let it generate and build, fix any errors.
- The Data Table import was NOT tested in the editor.

## Opening in M1
M1 includes a minimal setup scene: a short spirit intro (no gameplay), a starter picker with the two active starters (Wanderer for humanoid, Wolf for beast), and inhabitation. Gameplay then starts in the chosen form and unlocks morph. Flier and Raptor starters wait until those subcategories are active. See `DESIGN.md` section 3a.

## Next tasks (need the editor)
1. Compile and open the project.
2. Import `Forms.json` as a Data Table.
3. Test map with a player character and a placeholder mesh per form.
4. Morph action: swap form on key press, with a simple Niagara effect.
5. Steam login through Online Subsystem Steam (needs a Steam app id; use the test id 480 for local tests only).

## Open design questions (not needed for M1)
Marked in `DESIGN.md` section 9. M1 does not need: free-to-play vs paid, art source, audience, minimum spec, budget.
Decided for M1: third-person camera, PvE, morph = swap of the whole character with no time limit (a short cooldown only).
Co-op is NOT part of M1 (planned for M2).
