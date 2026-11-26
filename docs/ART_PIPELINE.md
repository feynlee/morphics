# Morphics: Art pipeline (draft)

Claude makes the 3D art and animations. Ziyue directs and approves.
This is the main production task. This doc says how, and what is still unproven.

## Honest limits
- Claude works through code and tools. It does not sculpt by hand.
- Models come from scripts (Blender Python), procedural tools, or AI 3D generation tools if available.
- Visual quality sells the game. The first form is a **test of the quality bar**. Ziyue judges it before we scale.
- Blender is not confirmed installed in the cloud environment. First task: check, or run the pipeline on Ziyue's PC.

## Pipeline per form
1. **Brief** (JSON `look` notes plus a short text): silhouette, colors, materials, motion style.
2. **Concept check**: render a turnaround with simple shapes. Ziyue approves the silhouette.
3. **Model**: Blender script builds the mesh (base shapes, sculpt-style modifiers, detail). Output: FBX.
4. **UV and textures**: scripted UVs, procedural materials, baked texture maps.
5. **Rig**: shared skeleton per body type (for example: quadruped, biped, bird). Skins reuse it.
6. **Animation**: idle, walk, run, jump, basic attack, 2 skills, ultimate, morph in, morph out, hit, death. Start from shared animation sets per skeleton, then add form-specific motion.
7. **Import to Unreal**: FBX import, material instances, Niagara effects for the morph and skills.
8. **Review**: Ziyue checks it in the editor and in game camera (third-person).
9. **Skins**: material instances and texture sets on the same skeleton.

## Making it scale ("many forms at launch")
- Body-type skeletons and shared animation sets.
- Modular parts (heads, tails, horns, armor) and a material library.
- A per-form budget (triangles, texture size, animation count) and a checklist.
- Batch export and import scripts, so one command rebuilds all art from source.

## Repo layout (proposed)
- `art/source/` Blender scripts and source files (text first; large files in Git LFS).
- `art/export/` generated FBX (not committed unless needed).
- `tools/art/` batch scripts.

## Next steps
1. Check which tools can run where (Blender, Python, Unreal command line).
2. Make ONE form end to end (Ember Fox): model, rig, 4 animations, one skin.
3. Ziyue reviews it in the editor. Decide: continue, adjust, or change the plan.
