# Morphics: Art pipeline (draft v2)

Claude makes the 3D art and animations. Ziyue directs and approves.
This is the main production task. This doc says how, and what is still unproven.

## Visual style
Target: realistic-stylized, similar in feel to ARK: Survival Ascended. **Decided by Ziyue (2026-11-26): more realistic, with no cartoon exaggeration.** The Palworld-like option is dropped. All art is original. We copy no creature, design, or asset from any game. See `DESIGN.md` section 1b.
- The first quality-test form is the Wolf, the plain four-legged starter. Its brief is in `art/WOLF_BRIEF.md`. Ziyue approves it before we scale.
- Starters are plain and basic archetypes. Themed variants (Ember Fox, and so on) come after and are farmed.

## Honest limits
- Claude works through code and tools. It does not sculpt by hand.
- Models come from scripts (Blender Python), procedural tools, or AI 3D generation tools if available.
- Visual quality sells the game. The first form is a **test of the quality bar**. Ziyue judges it before we scale.
- Blender is not confirmed installed in the cloud environment. First task: check, or run the pipeline on Ziyue's PC.

## Body types (a tree)
Animation is made **per top-level body type, not per form**. See `DESIGN.md` section 4b for the tree.
- Body types live in `data/bases/*.json` as a tree. Example: Four-legged beast > Small four-legged beast > Ember Fox (a farmable variant).
- Each top-level body type has ONE skeleton and ONE required animation list.
- Each subcategory (small, medium, large, and so on) reuses the animations through retargeting (Unreal IK Retargeter) with its proportion settings.
- A form picks a node. An orc and a human both use `base.humanoid.medium`. A dwarf uses `base.humanoid.short`.
- Cost effect: a new form in an existing node needs a model, textures, a default skin, and VFX. It needs no new skeleton and no new animation set.
- **Inherit first, override only what changes.** A subcategory starts with every parent animation, retargeted. After a test pass, the artist lists the few that need changes (for example the run and jump of a small beast) in `animation_overrides` and makes those.
- Lookup order for an animation: form extra, then subcategory override, then parent, then root.
- Fix a problem shared by all children in the parent set. Fix a size-specific problem as an override. This keeps the work small.
- A new subcategory needs a retarget setup and a test pass.
- A new top-level body type is the expensive step: new skeleton, full animation set, and retarget tests.
- Build order: humanoid and four-legged first (they are `active`). Bird and bipedal dinosaur after the first two work in game.

## Pipeline per form
1. **Brief** (JSON `look` notes plus a short text): silhouette, colors, materials, motion style.
2. **Concept check**: render a turnaround with simple shapes. Ziyue approves the silhouette.
3. **Model**: Blender script builds the mesh (base shapes, sculpt-style modifiers, detail). Output: FBX.
4. **UV and textures**: scripted UVs, procedural materials, baked texture maps.
5. **Rig**: use the form's base skeleton. The model must be skinned to it. A new body type means a new base (see above). Skins reuse the rig.
6. **Animation**: use the base animation set (idle, walk, run, jump, basic attack, 2 skills, ultimate, morph in, morph out, hit, death) for the form's node (retargeted to its proportions). Add only form-specific `extra_animations`.
7. **Import to Unreal**: FBX import, material instances, Niagara effects for the morph and skills.
8. **Review**: Ziyue checks it in the editor and in game camera (third-person).
9. **Skins**: a skin is made for one body-type node, not for one form. **Narrow is the default**: it fits that node only, and we tune it to those proportions. Make many narrow variations per node, because each one is a separate product. A broad skin (`fit: subtree`) is an exception for shared patterns and needs Ziyue's approval. Build on the root skeleton and test on every form the skin fits. It must never be used on another branch (the validator checks this).

## Making it scale ("many forms at launch")
- Body-type tree: one skeleton and one animation set per top-level body type, with size subcategories.
- Modular parts (heads, tails, horns, armor) and a material library.
- A per-form budget (triangles, texture size, animation count) and a checklist.
- Batch export and import scripts, so one command rebuilds all art from source.

## Repo layout (proposed)
- `art/source/` Blender scripts and source files (text first; large files in Git LFS).
- `art/export/` generated FBX (not committed unless needed).
- `tools/art/` batch scripts.

## Next steps
1. Check which tools can run where (Blender, Python, Unreal command line).
2. Build the first base end to end. Four-legged is a good first test: skeleton, the 12 required animations for the small subcategory, then Wolf (the plain starter: model, textures, default skin). Ember Fox is a later, farmable variant.
3. Retarget to the large subcategory and test with Stone Tortoise or Ember Fox.
4. Ziyue reviews it in the editor. Decide: continue, adjust, or change the plan.
