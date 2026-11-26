# Base meshes (first pass)

Built with Blender Python (`pip install bpy`). Shared helpers are in `art/common/morph_lib.py`.

| Form | Subcategory id | Rig id | Mesh id | Script | Triangles | Bones |
|---|---|---|---|---|---|---|
| Human | base.walker.humanoid.medium | rig.walker.humanoid | mesh.walker.humanoid | `art/human/build_human.py` | 9,020 | 22 |
| Hawk | base.flyer.flier.medium | rig.flyer.flier | mesh.flyer.flier | `art/hawk/build_hawk.py` | 8,772 | 24 |
| Wolf (canine) | base.walker.canine.medium | rig.walker.canine | mesh.walker.canine | `art/wolf/build_wolf.py` | 10,000 | existing |

Run: `python3 art/<name>/build_<name>.py --render --sheet --fbx`. Output goes to `art/<name>/out/`.

Style: matches the test map. Flat saturated colors, rounded chunky shapes, no noise texture, no normal map.
Colors come from per-texel zones in the paint material, so edges stay sharp.

Animations (30 fps, FK, no foot IK yet):
- Human: idle, walk, run, jump, attack_basic, hit, death.
- Hawk: idle, walk, run, fly, glide, jump, attack_basic, hit, death.
- Wolf: idle, walk, run only. Jump, attack, hit and death are NOT built yet.

Gaps: no skill, ultimate, morph_in or morph_out clips. No LODs. First pass poses need a look in the editor.
