# M1 prototype: scope and status

Goal: one arena, 3 forms, the morph action, Steam login. No store.

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
- a body-type tree (`data/bases`, 4 top-level types with 2 or 3 subcategories each) and 4 placeholder forms with original names: Wanderer (humanoid starter), Ember Fox (four-legged starter), Stone Tortoise (four-legged), Gale Heron (bird starter, planned base).
- M1 note: Gale Heron uses a planned base, so M1 needs only the four-legged base for playable forms. Add a humanoid form if a humanoid test is wanted.

## Not verified yet
- The C++ module was NOT compiled. The scaffold was written without Unreal installed.
  First task on the dev PC: open `Morphics.uproject` in UE 5.8.4, let it generate and build, fix any errors.
- The Data Table import was NOT tested in the editor.

## Opening in M1
M1 includes a minimal opening: spirit state, find a vessel, a starter picker with the two active starters (Wanderer for humanoid, Ember Fox for four-legged), inhabit the chosen form, then unlock morph. Bird and dinosaur starters wait until those body types are active. See `DESIGN.md` section 3a.

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
