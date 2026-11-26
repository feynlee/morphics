# Morphics

A 3D Windows game (Unreal Engine 5.8.4, sold on Steam) where players become different forms and skins.
Each form has its own look, skills, and abilities.

- Design: `docs/DESIGN.md`
- Art pipeline: `docs/ART_PIPELINE.md`
- Engine and Steam plan: `docs/ENGINE_AND_STEAM.md`
- M1 prototype status: `docs/M1_PLAN.md`

## Game data
Forms, skills, and skins are plain JSON in `data/`.

```
pip install jsonschema
python tools/validate_data.py
python tools/build_datatable.py
python tools/build_market.py
```

## Open the project
Install Unreal Engine 5.8.4, then open `Morphics.uproject`.
Large binary assets use Git LFS (`git lfs install` first).
