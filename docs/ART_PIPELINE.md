# Morphics: Art pipeline (draft v2)

Claude makes the 3D art and animations. Ziyue directs and approves.
This is the main production task. This doc says how, and what is still unproven.

## Honest limits
- Claude works through code and tools. It does not sculpt by hand.
- Models come from scripts (Blender Python), procedural tools, or AI 3D generation tools if available.
- Visual quality sells the game. The first form is a **test of the quality bar**. Ziyue judges it before we scale.
- Blender is not confirmed installed in the cloud environment. First task: check, or run the pipeline on Ziyue's PC.

## Base categories (body types)
Animation is made **per base and variant, not per form**.
- Bases live in `data/bases/*.json`: humanoid, four-legged (active), bird and bipedal dinosaur (planned).
- Each base has variants for size and proportion (for example: medium, short, large humanoid).
- Each base has ONE skeleton and ONE required animation list.
- Variants reuse the base animations through retargeting (Unreal IK Retargeter) with proportion settings.
- A form picks `base` and `variant`. An orc and a human both use `base.humanoid / medium`. A dwarf uses `base.humanoid / short`.
- Cost effect: a new form in an existing base needs a model, textures, a skin set, and VFX. It needs no new skeleton and no new base animation set.
- A new base is the expensive step: new skeleton, full animation set, and a retarget test.
- Build order: humanoid and four-legged first (they are `active`). Bird and bipedal dinosaur after the first two work in game.

## Pipeline per form
1. **Brief** (JSON `look` notes plus a short text): silhouette, colors, materials, motion style.
2. **Concept check**: render a turnaround with simple shapes. Ziyue approves the silhouette.
3. **Model**: Blender script builds the mesh (base shapes, sculpt-style modifiers, detail). Output: FBX.
4. **UV and textures**: scripted UVs, procedural materials, baked texture maps.
5. **Rig**: use the form's base skeleton. The model must be skinned to it. A new body type means a new base (see above). Skins reuse the rig.
6. **Animation**: use the base animation set (idle, walk, run, jump, basic attack, 2 skills, ultimate, morph in, morph out, hit, death) for the form's variant. Add only form-specific `extra_animations`.
7. **Import to Unreal**: FBX import, material instances, Niagara effects for the morph and skills.
8. **Review**: Ziyue checks it in the editor and in game camera (third-person).
9. **Skins**: material instances and texture sets on the same skeleton.

## Making it scale ("many forms at launch")
- Base categories: one skeleton and one animation set per body type, with size variants.
- Modular parts (heads, tails, horns, armor) and a material library.
- A per-form budget (triangles, texture size, animation count) and a checklist.
- Batch export and import scripts, so one command rebuilds all art from source.

## Repo layout (proposed)
- `art/source/` Blender scripts and source files (text first; large files in Git LFS).
- `art/export/` generated FBX (not committed unless needed).
- `tools/art/` batch scripts.

## Next steps
1. Check which tools can run where (Blender, Python, Unreal command line).
2. Build the first base end to end. Four-legged is a good first test: skeleton, the 12 required animations for the lean variant, then Ember Fox (model, textures, one skin).
3. Retarget to the heavy variant and test with Stone Tortoise.
4. Ziyue reviews it in the editor. Decide: continue, adjust, or change the plan.
