# Wolf art (form.wolf)

This folder builds the first quality-test model. The brief is `docs/art/WOLF_BRIEF.md`.

## Status: realistic reference only. The art direction changed to a stylized, low-poly look (see `docs/art/WOLF_BRIEF.md`). The model in `out/` is the old realistic version and will be replaced.

## Old status: first pass, not final quality
- The body is a generated mesh (Blender Skin modifier, voxel remesh, smoothing). It has a real rig and three looping animations, but it is not a hand-sculpted model.
- Fur is Blender hair particles. It is for previews only. It does not export to Unreal. The game needs fur cards or Unreal Groom, made later.
- No UV unwrap or baked textures yet. Colors come from a procedural shader.
- Known problems: the legs are still simple tubes, the ears and nose are plain shapes, toes are not modeled, and the lower legs read pale. The head and haunches were enlarged in the second pass, and short fur now covers the muzzle, ears and paws.

## Run it
```
pip install bpy
python3 art/wolf/build_wolf.py --render --out art/wolf/out     # turnaround views
python3 art/wolf/build_wolf.py --strip --fbx --out art/wolf/out  # walk strip and FBX
```
Environment variables: `SAMPLES` (render samples, default 32) and `VIEWS` (comma list of `side,front34,back34,head`).

## Files
- `build_wolf.py`: builds mesh, materials, fur, rig, and the actions `idle`, `walk`, `run`. It can render and export FBX.
- `out/`: preview images (committed) and `SK_Wolf.fbx` (the game export, mesh and rig with all actions).

## Rig (`base.quadruped` skeleton)
`root`, `pelvis`, `spine_1`, `spine_2`, `neck_1`, `neck_2`, `head`, `jaw`, `ear_L`, `ear_R`, `tail_1` to `tail_5`, and for each side `f_upper`, `f_lower`, `f_paw`, `h_upper`, `h_lower`, `h_paw` (L and R prefix). Names are the contract for retargeting other quadruped morphs.

## Animations
- `idle` (90 frames at 30 fps): breathing, head and tail motion.
- `walk` (36 frames): 4-beat lateral gait.
- `run` (20 frames): gallop-style diagonal pairs.
All loop. They are forward kinematics with sine curves, so foot sliding is possible. A later pass adds foot IK.

## Next steps
1. Refine the legs and paws (toes, tendons) and the face (brow, lips, eye shape).
2. UV unwrap and bake textures. Move fur to cards or Groom.
3. Import into Unreal, set up the third-person test level, and check the look in the game camera.
