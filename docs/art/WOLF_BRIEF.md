# Wolf art brief (form.wolf)

Status: draft for Ziyue to approve. Style is **realistic, no cartoon exaggeration** (decided 2026-11-26). All art is original.

## Role
The plain starter for the four-legged beast family (`base.quadruped.medium`). It sets the quality bar. Starters are plain and basic. Themed variants come later.

## Look
- **Anatomy:** a grey wolf with real proportions. Deep narrow chest, long legs, a long muzzle, a medium head, upright ears, a bushy tail carried low. Shoulder height about 0.8 m in the world scale used for the body type (a large dog to a large wolf).
- **Silhouette:** clear from behind and from the side. The player sees it from behind most of the time, so the back, ears and tail must read well.
- **Coat:** layered fur. A grey-brown saddle over the back and flanks, darker on the spine and tail tip, a light cream on the cheeks, chest, belly and inner legs. Soft fur cards or strands on the neck ruff and tail. Short coat on the legs and face.
- **Colors (default skin):** coat `#8A7D6E`, dark `#4A4038`, light `#E6DCCB`, eyes amber `#E8B64A`, nose near black. Muted and natural. No glow, no saturated accent.
- **Face:** narrow eyes, a dark nose, a visible mouth line. A calm, alert expression. No exaggerated features.
- **Materials:** fur shader with root to tip color, subsurface hint on ears, wet gloss on the nose and eyes. Roughness high on the coat.
- **Detail budget (first pass):** body about 20k triangles plus fur cards. Final in Unreal with Nanite where possible. Textures 2K, in material instances so skins swap cleanly.

## Rig (body type skeleton `base.quadruped`)
Root, pelvis, spine (4), chest, neck (2), head, jaw, ears (2), tail (5), four legs (upper, lower, paw, toe). Digitigrade hind legs. All quadruped morphs retarget to this skeleton.

## Animations (first set)
Idle (breathing, tail and ear motion), walk, run. Then jump, basic attack (bite), pounce, howl, hit, death, morph in and out. Walk and run follow real gait timing: the walk is a lateral-sequence 4-beat gait, the run is a gallop.

## Skins
The default skin is the coat above. A skin for `base.quadruped.medium` changes color, markings and fur only. It never changes the proportions.

## Not allowed
No copying of creatures, designs or assets from other games. No cartoon exaggeration.

## Approval
Ziyue approves the silhouette first (turnaround render), then the textured model, then the animations in the engine third-person camera.
