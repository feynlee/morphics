# Morphics: Design Doc (v0.3 draft)

Status: DRAFT. Not agreed. No code until this doc is agreed.
All mechanics, names, and art are original.
See also: `ENGINE_AND_STEAM.md`.

## 1. Pitch
Morphics is a 3D game for Windows (sold on Steam) where the player changes into different **forms**.
Each form has its own look, skills, and abilities.
Forms and skins are the main product the studio sells. Visual quality is the key selling point.

## 2. Decisions and assumptions
Decided by Ziyue:
- Platform: Windows PC, sold on Steam.
- Visuals: 3D, high visual quality.
- Engine: Unreal Engine.
- Form data: plain JSON files.

Assumed (to confirm):
- Genre: a session-based action game (short runs, 5 to 10 minutes).
- Camera: third-person.
- Players: solo play first. Online features come later.
- Style: high-fidelity 3D with readable silhouettes. Each form must be easy to tell apart from far away.
- Input: keyboard and mouse, plus gamepad support.

## 3. Core loop
1. Start a run with one equipped form.
2. Fight, explore, and collect **Essence** (a run currency).
3. During a run, spend Essence to **morph** into a different owned form for a short time.
4. Finish the run. Get rewards (soft currency, form XP, cosmetic fragments).
5. Spend rewards in the Hub: level up forms, unlock skills, equip skins.
6. Start the next run.

The "morph" action is the key moment. It must feel fast and good to watch. It is also the best showcase for the visuals we sell.

## 4. Form data model
A **Form** is data, not code. Forms live in plain JSON files in the repo.
A build step imports them into Unreal Data Assets or Data Tables.
This lets us add forms without code changes.

| Field | Meaning |
|---|---|
| id | Stable unique key |
| name, lore | Display text |
| role | Tank, Striker, Support, Scout, Controller |
| base_stats | HP, speed, power, defense |
| skills[] | 1 basic attack, 2 active skills, 1 ultimate |
| passives[] | Always-on traits (for example: "faster on water") |
| model | Asset path: skeletal mesh, skeleton, animation set |
| hitbox | Collision shape. It must match the gameplay size, not only the mesh. |
| morph_in / morph_out | Transition effect ids (Niagara systems) |
| skins[] | List of Skin ids |
| unlock | Unlock rule (see section 6) |
| rarity | Common, Rare, Epic, Legendary (sets cosmetic tier, NOT power tier) |

A **Skin** is cosmetic only:

| Field | Meaning |
|---|---|
| id, form_id | Identity and parent form |
| look | Material instance, textures, optional mesh parts, VFX set |
| sfx_pack | Optional sound set |
| unlock | Purchase, event, or earned |

Rules:
- **Skins never change stats, skills, or hitbox.**
- A skin must use the same skeleton as its form, so all animations work on it.

A **Skill** has: id, type (attack, buff, move, summon), cooldown, cost, effect list, and VFX id.
Effects use a small shared set of building blocks (damage, heal, push, status, spawn).
New forms mostly recombine these blocks.

A JSON schema checks every data file in CI before import.

## 5. Balance rules
- Every form has a strength and a clear weakness.
- Counter-play over raw power. No form is best in all cases.
- Paid forms must be **equal in power** to earned forms (see section 6).
- Rarity changes the look and the effects only.

## 6. Monetization model (assumed)
**Model: cosmetic-first, with purchasable forms. No pay-to-win.**
Free-to-play or a paid base game is still open (see section 9).

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
3. Show the real price. No hidden odds. If loot boxes are ever added, show drop rates and check Steam rules.
4. Offer a **preview** (3D try-on viewer) for every form and skin before purchase.
5. Seasonal pass: one free track, one paid track. Both tracks give forms or skins.

Revenue levers (in order of priority):
1. Skins and form bundles.
2. Seasonal pass.
3. Premium forms.
4. Optional supporter or starter packs.

Platform notes: Steam is the storefront. Steam takes a share of sales, so plan prices with that fee. See `ENGINE_AND_STEAM.md` for the integration plan.

## 7. Content pipeline
- Forms and skins are JSON data plus 3D art assets.
- New content can ship as DLC or store items, without a full game update where possible.
- Set a per-form budget early (triangle count, texture size, material cost, animation count) so that many forms stay affordable.
- Target: one new form every 2 to 4 weeks after launch. High-quality 3D art is the main cost, so check this against the art plan.

## 8. Milestones
1. **M0 Design agreed** (this doc).
2. **M1 Prototype**: one arena, 3 forms (placeholder models), the morph action, Steam login. No store.
3. **M2 Vertical slice**: hub, progression, 6 forms, 2 skins each, JSON importer.
4. **M3 Store and pass**: Steam purchase flow, 3D preview.
5. **M4 Playtest and Steam page**, then tune balance and prices.

## 9. Open questions for Ziyue
1. Camera and genre: third-person action arena (assumed), top-down, or other?
2. Solo, co-op, or PvP? PvP raises the cost of pay-to-win concerns.
3. Is the morph a swap of the whole character, or a short temporary transformation during a run?
4. Art: who makes the high-quality 3D art (in-house, contractor, marketplace)? How many forms at launch?
5. Free-to-play on Steam, or a paid base game with paid cosmetics? Is a seasonal pass wanted? Are loot boxes ruled out?
6. Target audience and age range?
7. Minimum PC spec to target?
8. Budget and timeline for M1?
