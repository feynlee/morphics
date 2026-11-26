# Wolf art brief (form.wolf)

Status: draft v2 for Ziyue to approve. Style is **cartoony and stylized, Palworld-like** (decided 2026-11-26, replacing the realistic version). All art is original.

**What changed after the first realistic Wolf:** the realistic Wolf used dense hair particles and a smooth high-detail body. That is a lot of data, and fur does not export to the game. The Wolf is now rebuilt as a low-poly stylized model with painted textures. The old realistic version stays in the repo as a reference render.
**Cartoony pass (Ziyue):** the Wolf now has chibi proportions, big eyes, short legs, round paws with toes and a mouth line. The budget is still 10,000 triangles.

## Role
The plain starter for the canine subcategory (`base.walker.canine.medium`). It sets the quality bar. Starters are plain and basic. Themed variants come later.

## Look
- **Shape:** a wolf with friendly, readable proportions. A larger head (about one third of the body length), a short strong muzzle, big upright ears, thicker legs, a chunky body, and a big bushy tail. Clear silhouette from behind and from the side. No gore or harsh features, because the audience is teen and up and the look is friendly.
- **Surface:** clean simple forms with soft bevels. Fur is painted into the texture as soft clumps and strokes. A few low-poly tufts on the neck ruff and the tail tip.
- **Colors (default skin):** a grey-brown coat `#8A7D6E` with a darker saddle `#4A4038`, cream chest, belly, muzzle and inner legs `#E6DCCB`, amber eyes `#E8B64A`, near-black nose. Muted and natural so the starter stays plain. Themed variants carry the louder colors later.
- **Face:** large eyes with a simple highlight, a clear nose and mouth line, a calm alert expression.
- **Material:** one material. Base color 2K, normal map 1K. Stylized shading with a soft rim light. No fur shader and no Groom.
- **Budget:** about 10,000 triangles at LOD0, plus 3 lower levels of detail. About 45 bones from the shared quadruped skeleton.

## Rig (canine subcategory, `rig.walker.canine`)
Root, pelvis, spine (4), chest, neck (2), head, jaw, ears (2), tail (5), four legs (upper, lower, paw, toe). Digitigrade hind legs. All quadruped morphs retarget to this skeleton.

## Animations (first set)
Idle (breathing, tail and ear motion), walk, run. Then jump, basic attack (bite), pounce, howl, hit, death, morph in and out. Walk and run follow real gait timing: the walk is a lateral-sequence 4-beat gait, the run is a gallop.

## Skins
The default skin is the coat above. A skin for `base.walker.canine.medium` changes color, markings and fur only. It never changes the proportions.

## Not allowed
No copying of creatures, designs or assets from other games. No cartoon exaggeration.

## Approval
Ziyue approves the silhouette first (turnaround render), then the textured model, then the animations in the engine third-person camera.
