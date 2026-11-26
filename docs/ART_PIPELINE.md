# Morphics: Art pipeline (draft v2)

Claude makes the 3D art and animations. Ziyue directs and approves.
This is the main production task. This doc says how, and what is still unproven.

## Visual style
Target: **stylized, closer to Palworld** (decided by Ziyue on 2026-11-26 after seeing the first Wolf, replacing the earlier realistic target). Bold silhouettes, friendly proportions, simple shapes, hand-painted style textures, rich lighting. All art is original. We copy no creature, design, or asset from any game. See `DESIGN.md` section 1b.

### Budget per form (proposal, Ziyue to confirm)
| Item | Medium creature | Small form | Large form |
|---|---|---|---|
| Triangles, LOD0 | 8,000 to 12,000 | 5,000 to 8,000 | 12,000 to 18,000 |
| Lower levels of detail | LOD1 50%, LOD2 25%, LOD3 10% | same | same |
| Materials | 1 | 1 | 1 |
| Base color texture | 2K | 1K | 2K |
| Normal map | 1K | 512 | 1K |
| Bones (shared body-type skeleton) | about 45 | same | same |
- **Detail comes from textures.** Fur, scales, and feathers are painted into the base color and normal map. No Groom, no hair strands, no fur cards. A few simple low-poly tufts (neck, tail tip) can shape the silhouette.
- **A skin costs texture data only.** It reuses the mesh and swaps textures and material parameters. Skins must not add geometry, so the budget holds.
- The validator and the build script check the triangle count of each form's model against its body-type budget (to add when models are imported).
- The first quality-test form is the Wolf, the plain beast starter. Its brief is in `docs/art/WOLF_BRIEF.md`. Ziyue approves it before we scale.
- Starters are plain and basic archetypes. Themed variants (Ember Fox, and so on) come after and are farmed.

## Honest limits
- Claude works through code and tools. It does not sculpt by hand.
- Models come from scripts (Blender Python), procedural tools, or AI 3D generation tools if available. Low poly plus painted textures is also much easier to make by script than detailed fur.
- Visual quality sells the game. The first form is a **test of the quality bar**. Ziyue judges it before we scale.
- Blender is not confirmed installed in the cloud environment. First task: check, or run the pipeline on Ziyue's PC.

## Body types (a tree)
Animation is made **per subcategory, not per form**. See `DESIGN.md` section 4b for the tree.
- Body types live in `data/bases/*.json` as a tree. Example: Walker > Canine > Small canine > Ember Fox (a farmable variant).
- Each subcategory has ONE skeleton (rig), ONE gait set, ONE base mesh and ONE required animation list. The three top categories (Walker, Swimmer, Flyer) have none of these.
- Each subcategory (small, medium, large, and so on) reuses the animations through retargeting (Unreal IK Retargeter) with its proportion settings.
- A form picks a node. An orc and a human both use `base.walker.humanoid.medium`. A dwarf uses `base.walker.humanoid.short`.
- Cost effect: a new form in an existing node needs a model, textures, a default skin, and VFX. It needs no new skeleton and no new animation set.
- **Inherit first, override only what changes.** A subcategory starts with every parent animation, retargeted. After a test pass, the artist lists the few that need changes (for example the run and jump of a small beast) in `animation_overrides` and makes those.
- Lookup order for an animation: form extra, then size override, then subcategory.
- Fix a problem shared by all children in the parent set. Fix a size-specific problem as an override. This keeps the work small.
- A new subcategory needs a retarget setup and a test pass.
- A new subcategory is the expensive step: new skeleton, mesh, full animation set, and retarget tests.
- Build order: Humanoid, canine, hoofed and shelled first (they are `active`). Flier, raptor and the planned ones after the first two work in game.

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
- Body-type tree: one skeleton, gait set and mesh per subcategory, with sizes as scales.
- Modular parts (heads, tails, horns, armor) and a material library.
- A per-form budget (triangles, texture size, animation count) and a checklist.
- Batch export and import scripts, so one command rebuilds all art from source.

## Repo layout (proposed)
- `art/source/` Blender scripts and source files (text first; large files in Git LFS).
- `art/export/` generated FBX (not committed unless needed).
- `tools/art/` batch scripts.

## Next steps
1. Check which tools can run where (Blender, Python, Unreal command line).
2. Build the first base end to end. Canine is a good first test: rig `rig.walker.canine`, the 12 required animations for the canine subcategory, then Wolf (the plain starter: model, textures, default skin). Ember Fox is a later, farmable variant.
3. Retarget to the large subcategory and test with Stone Tortoise or Ember Fox.
4. Ziyue reviews it in the editor. Decide: continue, adjust, or change the plan.
