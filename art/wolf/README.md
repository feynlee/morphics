# Wolf art (form.wolf)

This folder builds the quality-test model. The brief is `docs/art/WOLF_BRIEF.md`.
Art direction: cartoony and stylized, low poly, detail in textures (decided 2026-11-26).

## Status: cartoony pass (2026-11-26)
- Style: cartoony and stylized (Ziyue's request). Chibi proportions: big head, big round eyes, short sturdy legs, round paws with toes, a mouth line.
- `build_wolf.py` makes 10,000 triangles at LOD0, one material, a 2K base color texture and a 1K normal map, and the canine rig (`rig.walker.canine`) with `idle`, `walk` and `run` actions.
- Colors and fur strokes are painted by script into the textures. No hair particles and no fur cards.
- Known problems: the front legs still read paler than the body, the ears are plain cones, the tail is a ball, and there are no lower levels of detail yet. A hand-sculpt pass is needed for final quality.
- The earlier realistic version is kept as a reference: `build_wolf_realistic.py` and `reference_realistic/`. It is not used in the game.

## Run it
```
pip install bpy
python3 art/wolf/build_wolf.py --render --strip --fbx --out art/wolf/out
```
Environment variables: `SAMPLES` (render samples, default 32), `VIEWS` (comma list of `side,front34,back34,head`), `TARGET_TRIS` (default 10000), `TEX` (texture size, default 2048).

## Files in `out/`
`SK_Wolf.fbx` (mesh and rig with all actions), `wolf_basecolor.png`, `wolf_normal.png`, `wolf.blend`, and preview renders (`wolf_*.png`, `walk_sheet.png`).

## Rig (`rig.walker.canine`)
`root`, `pelvis`, `spine_1`, `spine_2`, `neck_1`, `neck_2`, `head`, `jaw`, `ear_L`, `ear_R`, `tail_1` to `tail_5`, and for each side `f_upper`, `f_lower`, `f_paw`, `h_upper`, `h_lower`, `h_paw` (L and R prefix). Names are the contract for retargeting other quadruped morphs.

## Animations
`idle` (90 frames at 30 fps), `walk` (36 frames, 4-beat gait), `run` (20 frames). All loop. They are sine-based forward kinematics, so foot sliding is possible. A later pass adds foot IK.

## Next steps
1. Shape pass: front-leg color, ear shape, tail shape, then lower levels of detail.
2. Import into Unreal and check the look in the third-person camera.
3. Add a triangle budget check to the build.
