# Morphics: Design Doc (v0.2 draft)

Status: DRAFT. Not agreed. No code until this doc is agreed.
All mechanics, names, and art are original.

## 1. Pitch
Morphics is a 3D game for Windows where the player changes into different **forms**.
Each form has its own look, skills, and abilities.
Forms and skins are the main product the studio sells.

## 2. Decisions and assumptions
Decided by Ziyue:
- Platform: Windows PC.
- Visuals: 3D.

Assumed (to confirm):
- Genre: a session-based action game (short runs, 5 to 10 minutes).
- Camera: third-person.
- Players: solo play first. Online features come later.
- Style: stylized 3D with readable silhouettes. Each form must be easy to tell apart from far away.
- Input: keyboard and mouse, plus gamepad support.

## 3. Core loop
1. Start a run with one equipped form.
2. Fight, explore, and collect **Essence** (a run currency).
3. During a run, spend Essence to **morph** into a different owned form for a short time.
4. Finish the run. Get rewards (soft currency, form XP, cosmetic fragments).
5. Spend rewards in the Hub: level up forms, unlock skills, equip skins.
6. Start the next run.

The "morph" action is the key moment. It must feel fast and good to watch.

## 4. Form data model
A **Form** is data, not code. This lets us add forms without new builds.

| Field | Meaning |
|---|---|
| id | Stable unique key |
| name, lore | Display text |
| role | Tank, Striker, Support, Scout, Controller |
| base_stats | HP, speed, power, defense |
| skills[] | 1 basic attack, 2 active skills, 1 ultimate |
| passives[] | Always-on traits (for example: "faster on water") |
| model | 3D mesh, skeleton (rig), and animation set |
| hitbox | Collision shape. It must match the gameplay size, not only the mesh. |
| morph_in / morph_out | Transition effect ids |
| skins[] | List of Skin ids |
| unlock | Unlock rule (see section 6) |
| rarity | Common, Rare, Epic, Legendary (sets cosmetic tier, NOT power tier) |

A **Skin** is cosmetic only:

| Field | Meaning |
|---|---|
| id, form_id | Identity and parent form |
| look | Mesh variant or material set, textures, palette, VFX set |
| sfx_pack | Optional sound set |
| unlock | Purchase, event, or earned |

Rules:
- **Skins never change stats, skills, or hitbox.**
- A skin must use the same skeleton as its form, so all animations work on it.

A **Skill** has: id, type (attack, buff, move, summon), cooldown, cost, effect list, and VFX id.
Effects use a small shared set of building blocks (damage, heal, push, status, spawn).
New forms mostly recombine these blocks.

## 5. Balance rules
- Every form has a strength and a clear weakness.
- Counter-play over raw power. No form is best in all cases.
- Paid forms must be **equal in power** to earned forms (see section 6).
- Rarity changes the look and the effects only.

## 6. Monetization model (assumed)
**Model: free-to-play, cosmetic-first, with purchasable forms.** No pay-to-win.

| Item | How to get it |
|---|---|
| Starter forms (3 to 4) | Free for all players |
| Standard forms | Earn in play (soft currency) OR buy directly |
| Premium forms | Buy directly or from a seasonal pass |
| Skins | Buy, earn from events, or from pass tiers |
| Form XP and skill upgrades | Earned in play only |

Principles:
1. Anything that changes power can be earned in play. Paid forms give variety, not advantage.
2. Skins are cosmetic, so they can be sold without balance risk.
3. Show the real price. No hidden odds. If loot boxes are ever added, show drop rates and check platform rules.
4. Offer a **preview** (try-on, with a 3D model viewer) for every form and skin before purchase.
5. Seasonal pass: one free track, one paid track. Both tracks give forms or skins.

Revenue levers (in order of priority):
1. Skins and form bundles.
2. Seasonal pass.
3. Premium forms.
4. Optional supporter or starter packs.

Platform notes: on Windows, the likely storefronts are Steam and the Microsoft Store. Each one has its own store fee and its own in-app purchase rules. Pick the storefront early, because it decides the purchase and account system.

## 7. Content pipeline
- Forms and skins are data files plus 3D art assets.
- Content can be shipped by remote config or asset download, to avoid a full game update.
- Set a per-form budget early (triangle count, texture size, animation count) so that many forms stay affordable to make.
- Target: one new form every 2 to 4 weeks after launch. 3D art is the main cost, so check this against the art plan.

## 8. Milestones
1. **M0 Design agreed** (this doc).
2. **M1 Prototype**: one arena, 3 forms (placeholder 3D models), the morph action. No store.
3. **M2 Vertical slice**: hub, progression, 6 forms, 2 skins each.
4. **M3 Store and pass**: purchase flow, 3D preview, receipts.
5. **M4 Soft launch**, then tune balance and prices.

## 9. Open questions for Ziyue
1. Camera and genre: third-person action arena (assumed), top-down, or other?
2. Engine: Unity, Unreal, or Godot? (Windows and 3D are fixed.)
3. Single-player, co-op, or PvP? PvP raises the cost of pay-to-win concerns.
4. Is the morph a swap of the whole character, or a short temporary transformation during a run?
5. Art: who makes the 3D art, and what style? How many forms at launch?
6. Is the monetization model in section 6 right? Is a seasonal pass wanted? Are loot boxes ruled out? Steam or Microsoft Store?
7. Target audience and age range?
8. Budget and timeline for M1?
