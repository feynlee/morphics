# Morphics: Art pipeline (draft v2)

Claude makes the 3D art and animations. Ziyue directs and approves.
This is the main production task. This doc says how, and what is still unproven.

## Honest limits
- Claude works through code and tools. It does not sculpt by hand.
- Models come from scripts (Blender Python), procedural tools, or AI 3D generation tools if available.
- Visual quality sells the game. The first form is a **test of the quality bar**. Ziyue judges it before we scale.
- Blender is not confirmed installed in the cloud environment. First task: check, or run the pipeline on Ziyue's PC.

## Body types (a tree)
Animation is made **per top-level body type, not per form**. See `DESIGN.md` section 4b for the tree.
- Body types live in `data/bases/*.json` as a tree. Example: Four-legged beast > Small four-legged beast > Ember Fox.
- Each top-level body type has ONE skeleton and ONE required animation list.
- Each subcategory (small, medium, large, and so on) reuses the animations through retargeting (Unreal IK Retargeter) with its proportion settings.
- A form picks a node. An orc and a human both use `base.humanoid.medium`. A dwarf uses `base.humanoid.short`.
- Cost effect: a new form in an existing node needs a model, textures, a default skin, and VFX. It needs no new skeleton and no new animation set.
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
9. **Skins**: a skin is made for a body-type node, not for one form. It fits that node and all nodes below it. Build it on the root skeleton and test it on every form it fits. It must never be used on another branch (the validator checks this).

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
2. Build the first base end to end. Four-legged is a good first test: skeleton, the 12 required animations for the small subcategory, then Ember Fox (model, textures, default skin).
3. Retarget to the large subcategory and test with Stone Tortoise.
4. Ziyue reviews it in the editor. Decide: continue, adjust, or change the plan.
