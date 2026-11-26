# Morphics: Design Doc (v0.13)

Status: AGREED by Ziyue for M1. Later sections may still change.
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
- Engine: Unreal Engine 5.8.4.
- Form data: plain JSON files.
- Camera: third-person, so players always see the skins they buy.
- Mode: PvE with co-op. No PvP for now.
- Morphs have **no time limit**. A player keeps a form until the player picks another.
- Launch content: as many forms as possible. Ziyue and Claude design the forms together.
- Monetization: forms are sold for an in-game currency. Currency bundles are sold on Steam.
- Audience: teen and older (teen+).
- Body types are a **tree**. Every form declares one body type (a node in the tree). Forms under one top-level body type share a skeleton and animations. See section 4b.
- Art: Claude makes the 3D art and animations (models, rigs, animations, VFX briefs), with Ziyue's direction and approval.
- Budget and timeline: none set. Work is scoped by milestones, not by dates.
- Storefronts: Steam first. Epic Games Store is added as a later storefront.
- Opening: the player starts as an amorphic spirit with no body. The goal is to inhabit a first form. Inhabiting it unlocks the ability to gain more forms and morph into them at will. See section 3a.
- Retention goal: a "continual playthrough" game. There is always something new to unlock or farm, so the player's investment feels worthwhile.

Assumed (to confirm):
- Genre: action game with missions or runs (short, repeatable sessions).
- Co-op size: 2 to 4 players.
- Input: keyboard and mouse, plus gamepad support.
- Style: high-fidelity 3D with readable silhouettes. Each form must be easy to tell apart from far away.

## 3a. Opening: the spirit
**Spirit state**
- The player starts as an **amorphic spirit**: a formless, glowing presence with no body, no skin, and no body type.
- The spirit can float and look around, and it can reach the world, but it cannot fight. It has no skills.
- The spirit is not a form. It is a special state outside the body-type tree. (No skeleton or animation set from the tree. It needs its own light visual and movement.)
- In co-op, every player starts as a spirit. Spirits are tinted with the player's color so players can find each other, until each one takes a form.

**First inhabitation**
- The opening goal is to **inhabit a first form**: find a vessel in the world and enter it.
- A short guided sequence (about 10 to 15 minutes): learn to move, find the vessel, face a small threat that the spirit cannot beat, then inhabit.
- Inhabiting is a strong moment. It uses the morph-in effect, and it is the first time the player sees their skin. It must look great, because it shows what the game sells.
- The first form is free. Starter forms are marked `starter: true` in their JSON, and the validator requires them to be free.

**Unlock of morphing**
- Inhabiting the first form **unlocks the ability to gain more forms**. It also unlocks the morph action: change into any owned form at will (no time limit, short cooldown only, see section 3).
- The collection screen, the Hub, and the form store open at this moment, in steps, so the first session is not overwhelming.
- Story idea (placeholder): the spirit "remembers" how to take forms as it learns each body. Each new form adds to the collection.
- Returning players and new co-op joiners skip the opening after they have done it once. A joining player who has not done it plays it as a short solo part, then joins.

**How the first form is chosen (decided)**
- At the start of a new game, the player **picks a starter form**.
- There is **one starter per top-level body type**. Each starter is a very basic form of that body type, so the choice shows the variety of the game on the first screen.
- The starter picker is part of the opening, just before inhabitation: the spirit meets the vessels and picks one.
- Starters are free. They are marked `starter: true` in their JSON.
- Validator rule: **exactly one starter per top-level body type**. For a body type that is still `planned` (no art yet), zero starters are allowed until it becomes `active`, and at most one. A starter must be free.
- Starters should be plain, with no strong elemental or special theme. Special forms are for the store and for farming.

Starter slots:

| Slot | Top-level body type | Status | Starter (placeholder) |
|---|---|---|---|
| 1 | Humanoid (bipedal human) | active | Wanderer |
| 2 | Four-legged beast | active | Ember Fox |
| 3 | Bird | planned | Gale Heron |
| 4 | Bipedal dinosaur | planned | not made yet |

Notes:
- The starters are placeholders. In particular, Ember Fox and Gale Heron have a themed look and should be replaced with plain starters (for example a plain wolf and a plain hawk) before launch.
- Adding a new top-level body type adds a new starter slot. The picker shows one card per top-level body type.
- Players keep access to all starters. A player who picks one can later get the others (they are free), so the pick is a first step, not a lock.
- Skins for a starter are sold like any other skin. Starters are a good first target for early skin sales, because every player owns one.

Open questions for Ziyue:
- Do all starters stay free for everyone, or can a player who picks one get the other starters only by earning them in play? (Default: all starters are free to unlock in the opening hub, in any order.)
- Can the player return to spirit state later (for example to rest, to escape, or as a free "form")? (Default: no, to keep the game simple.)
- Does the spirit get cosmetics (aura, trail) that are sold? (Default: not yet. It is a later option and it would be cosmetic only.)

## 3. Core loop
1. Pick a mission (alone or with co-op friends). Choose a starting form.
2. Fight and explore. Collect **Essence** and loot.
3. **Morph** between owned forms at any time. A morph has no time limit. A short cooldown after a morph stops swap spam.
4. Finish the mission. Get rewards: soft currency, form XP, materials, cosmetic fragments.
5. Spend rewards in the Hub: level up forms, unlock skills, equip skins, craft or buy forms.
6. Start the next mission.

Because morphs do not expire, **form choice is a build choice**. A player can stay in a favorite form, and the skin is on screen all the time. That is why the camera is third-person.

The "morph" action is still the key moment. It must feel fast and good to watch.

## 3b. Retention: always something to do
Goal: a player at any level has a next target.
- **Form mastery**: each form has levels, skill upgrades, and mastery rewards (titles, emotes, skin variants).
- **Farm targets**: missions drop form fragments and materials. A set of fragments unlocks or upgrades a form.
- **Rotating content**: weekly missions and daily goals.
- **Seasons**: a new season every 8 to 12 weeks with new missions, new forms, and a new reward track.
- **New forms on a schedule**: a new form every 2 to 4 weeks.
- **Collection screen**: shows owned forms and skins, so gaps are easy to see.
- Rules: respect the player's time. No fake scarcity and no dark patterns (audience is teen+).

## 4. Form data model
A **Form** is data, not code. Forms live in plain JSON files in the repo.
A build step imports them into Unreal Data Assets or Data Tables.
This lets us add forms without code changes.

| Field | Meaning |
|---|---|
| id | Stable unique key |
| name, lore | Display text |
| role | Tank, Striker, Support, Scout, Controller |
| base | Body type: a node in the body-type tree (see section 4b). Sets skeleton and shared animations. |
| extra_animations[] | Optional form-specific animations on top of the base set |
| base_stats | HP, speed, power, defense |
| skills[] | 1 basic attack, 2 active skills, 1 ultimate |
| passives[] | Always-on traits (for example: "faster on water") |
| model | Asset path: skeletal mesh, skeleton, animation set |
| hitbox | Collision shape. It must match the gameplay size, not only the mesh. |
| morph_in / morph_out | Transition effect ids (Niagara systems) |
| default_skin | Skin id of the form's default look. Must be made for the form's base. |
| unlock | Unlock rule (see section 6) |
| rarity | Common, Rare, Epic, Legendary (sets cosmetic tier, NOT power tier) |

A **Skin** is cosmetic only, and it is made for **one base** (body type):

| Field | Meaning |
|---|---|
| id | Stable unique key |
| base | The body-type node the skin is made for (required) |
| fit | `node` (default, narrow): fits only forms of exactly that node. `subtree` (broad, opt-in): also fits every node below it. |
| form_id | Optional: makes the skin exclusive to one form (for example a form's default look) |
| look | Material instance, textures, optional mesh parts, VFX set |
| sfx_pack | Optional sound set |
| unlock | Purchase, event, or earned |

Rules:
- **Skins never change stats, skills, or hitbox.**
- A skin is made for one base and uses that base's skeleton, so all base animations work on it.
- **A skin works on any form in its base, and never on a form in another base.** A skin made for a humanoid would look out of proportion on a four-legged body. The validator rejects it.

A **Skill** has: id, type (attack, buff, move, summon), cooldown, cost, effect list, and VFX id.
Effects use a small shared set of building blocks (damage, heal, push, status, spawn).
New forms mostly recombine these blocks.

A JSON schema checks every data file in CI before import.

## 4b. Body types (a tree)
A **body type** is a node in a tree. Forms under one top-level body type share a skeleton and one animation set.
This lets us make many forms: a new form is a new look plus skills, not a new animation set.

Structure: **top-level body type > subcategory > form**. Example: Four-legged beast > Small four-legged beast > Ember Fox.
- The **top level** (root) sets the skeleton and the required animation list.
- A **subcategory** sets size and build (small, medium, large). It **inherits the skeleton and all animations** from its parent and retargets them to its proportions.
- A **form** declares the node it uses. Usually that is a subcategory.
- Deeper levels are allowed when needed (for example: Large four-legged beast > Heavy large four-legged beast). One more segment per level.

```
base.humanoid                  Humanoid
  base.humanoid.medium         human, orc, elf
  base.humanoid.short          dwarf, gnome, halfling
  base.humanoid.large          ogre, giant
base.quadruped                 Four-legged beast
  base.quadruped.small         fox, lynx, small canine      <- Ember Fox
  base.quadruped.medium        large cat, large canine
  base.quadruped.large         bear, boar, tortoise         <- Stone Tortoise
base.bird (planned)            Bird
  base.bird.medium             heron, hawk                  <- Gale Heron
  base.bird.large              eagle, roc
base.biped_dino (planned)      Bipedal dinosaur
  base.biped_dino.medium       raptor
  base.biped_dino.large        rex type
```

Data rules (`data/bases/*.json`, checked by the validator):
- A node has `id`, `name`, `status` (active or planned), and an optional `parent`.
- A child id is its parent's id plus one segment (`base.quadruped` > `base.quadruped.small`).
- A root has `required_animations` (idle, walk, run, jump, basic attack, 2 skills, ultimate, morph in, morph out, hit, death) and a `skeleton`.
- **Inheritance**: a subcategory reuses the parent's animations by default. It lists only the animations it changes in `animation_overrides` (for example, a small beast has its own run and jump). An override must name an animation from the root's required list. Everything not listed is inherited.
- Expect some tuning: retargeted animations may need small fixes per subcategory. Fix a shared problem at the parent, so all children gain. Fix a size-specific problem as an override.
- A form may add `extra_animations` on top, for its own signature moves. Order of lookup: form extra, then subcategory override, then parent, then root.
- A node cannot be `active` under a `planned` parent.
- Every form declares `base`. The validator rejects an unknown node.
- A form may add `extra_animations` for its own signature moves.
- New top-level body types are added as data. A new top level needs a new skeleton and a full animation set, so it is a bigger task than a new subcategory or a new form.
- Gameplay: the node sets default movement feel and hitbox size range. A form can change them within limits.

### Skins and what players see
- The **look is a skin worn over the body type**. The body type is a gameplay detail. It sets skeleton, animations, and movement feel.
- **Every player sees every other player's skin**, in co-op and in shared spaces. Skins are the way teammates recognize each other in the 3D world.
- Skins are always shown. Players cannot turn off other players' skins or replace them with a default look. (A "reduce effects" option may lower VFX, but the model and colors stay.)
- Skin readability rules: a skin keeps a clear silhouette and a distinct main color. It must still read from far away, and two teammates in different skins must be easy to tell apart.
- Fairness rule: a skin's silhouette must stay inside the form's hitbox size range. A skin cannot make a player look smaller or larger than the real hitbox. (Teammates and enemies read hitboxes from the look.)
- Because skins are the main product, the **hub, the store preview, and co-op lobbies** all show the full 3D skin.

Body-type cue (recommendation, for Ziyue to decide):
- Show a **small role icon** on the teammate nameplate (Tank, Striker, Support, Scout, Controller). Role helps co-op play. It is a small icon and does not cover the skin.
- Do NOT show the body type as an icon. The silhouette already shows it, and it is not useful information for a teammate.
- The nameplate is hidden or small by default, so the skin stays the main identity. Players can show or hide nameplates.
- Optional: ping or highlight outline on a teammate when they are off screen or behind cover.

### Skins are sold per body type, and narrow by default (decided)
- Each skin is made for one body-type node. **Narrow is the default: a skin fits forms of exactly that node.** It never fits another branch of the tree.
- Why narrow: skins are the product. A narrow skin is made for exact proportions, so it looks its best. It also lets us make many separate variations and sell each one. For example, a different fox skin, lynx skin, and small-canine skin can each be sold on their own.
- Examples:
  - A narrow skin for `base.quadruped.small` fits every small four-legged beast (fox, lynx, small canine). It does not fit a medium or large beast.
  - A narrow skin for `base.humanoid.short` fits dwarf, gnome, and halfling forms, and no medium humanoid.
- **Broad skins are an option** (`fit: subtree`): the skin fits its node and every node below it. Use this only for shared patterns and materials (for example a fur pattern or an armor-plate set) that look right at every size. A broad skin is the exception, and Ziyue approves each one.
- A skin can also be exclusive to one form (`form_id`). Default looks work this way. This is the narrowest option.
- A player who owns a skin can wear it on any owned form it fits.
- Store UI: show the skin on every owned form it fits, and show which body type it fits.
- Each form has a `default_skin` that fits its body type, so a form always has a look.
- Ownership: a player owns skins and forms separately. Equipping checks the fit rule.
- Art cost: a narrow skin is tested on one node only, which keeps each skin cheap to make and check. Many narrow variations are the main way we grow the skin catalog.

## 5. Balance rules
- Every form has a strength and a clear weakness.
- Counter-play over raw power. No form is best in all cases.
- Paid forms must be **equal in power** to earned forms (see section 6).
- Rarity changes the look and the effects only.

## 6. Monetization model
**Model: two currencies. Forms and skins are bought with the in-game premium currency. Premium currency is sold in bundles on Steam.** No pay-to-win.

Currencies (names are placeholders):
- **Prisms** (premium): bought in Steam bundles. May also drop in small amounts from play (to confirm).
- **Shards** (soft): earned only in play.

| Item | How to get it |
|---|---|
| Starter forms (3 to 4) | Free for all players |
| Standard forms | Prisms, OR earn with form fragments from missions |
| Premium forms | Prisms |
| Skins | Prisms, event rewards, or pass tiers |
| Form XP and skill upgrades | Earned in play only (Shards, materials) |

Principles:
1. Anything that changes power can be earned in play. Paid forms give variety, not advantage.
2. Skins are cosmetic, so they can be sold without balance risk.
3. Show real prices: every Prism price also shows the cost in money (bundle value). No hidden odds. **No loot boxes** (recommended for a teen+ audience and for platform and legal safety).
4. Offer a **preview** (3D try-on viewer) for every form and skin before purchase.
5. Seasonal pass (optional): one free track, one paid track. Both give forms or skins.
6. Teen+ care: clear spending totals, a purchase confirmation step, and a refund policy that follows Steam rules.
7. Bundle sizes should not leave odd Prism leftovers that push players to buy more.

Revenue levers (in order of priority):
1. Currency bundles (to buy forms and skins).
2. Skins and form bundles.
3. Seasonal pass.
4. Supporter or starter packs.

Platform notes: Steam is the storefront. Steam takes a share of sales, so plan bundle prices with that fee. See `ENGINE_AND_STEAM.md`. Currency sold on Steam must follow Steam's rules for virtual items. Check the current rules before the store page goes live.

## 7. Content pipeline
- Forms and skins are JSON data plus 3D art assets.
- **Forms are made together**: Ziyue sets the idea, and Claude drafts the form (role, stats, skills, lore, look brief) as JSON. The validator checks it. Ziyue approves.
- **Goal: as many forms as possible at launch.** Plan a form "factory": a template, a stat budget per role, and a checklist per form (design, JSON, model, rig, animations, VFX, skin, test).
- **Art pipeline is the main production task.** See `ART_PIPELINE.md`. Claude makes the 3D art and animations, so the pipeline must be scriptable and repeatable.
- Set a per-form budget early (triangle count, texture size, material cost, animation count). 3D art and animation are the bottleneck, not design or data.
- Reuse where it is cheap and still reads as different: shared skeletons per body type, shared animation sets, material-based skin variants.
- New content can ship as DLC or store items, without a full game update where possible.

## 8. Milestones
1. **M0 Design agreed** (this doc).
2. **M1 Prototype**: one arena, 3 forms (placeholder models), the morph action (no timer), Steam login. No store.
3. **M2 Vertical slice**: hub, progression, form mastery, 6 forms, 2 skins each, JSON importer, co-op for 2 players.
4. **M3 Store**: Prism bundles on Steam, form and skin purchase, 3D preview.
5. **M4 Content scale-up**: the form factory, seasonal structure, many forms.
6. **M5 Playtest and Steam page**, then tune balance and prices.

## 9. Open questions for Ziyue
Decided questions were removed. Still open:
1. **Art quality bar**: Claude's art is made with scripts and tools (see `ART_PIPELINE.md`). Visual quality is the product, so Ziyue should judge the first form and set the bar. If it is not enough, we change the plan (for example: add a human artist for hero forms, or use licensed assets).
2. **Epic Games Store**: ownership and currency use one interface, so adding Epic later is planned. When should Epic be added (after launch, or at launch)?

Smaller points, with a default if you do not answer:
- Free-to-play or a paid base game? (Default: free-to-play, because currency bundles carry the revenue.)
- Can Prisms drop from play? (Default: yes, in small amounts.)
- Seasonal pass? (Default: add in M4.)
- Co-op size? (Default: 2 to 4.)
- Minimum PC spec? (Default: decide at M2.)
