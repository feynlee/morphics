# Morphics: Design Doc (v0.49)

Status: AGREED by Ziyue for M1. Later sections may still change.
All mechanics, names, and art are original.
See also: `ENGINE_AND_STEAM.md`.

## 1. Pitch
Morphics is a 3D game for Windows (sold on Steam) where the player changes into different **forms**.
Each form has its own look, skills, and abilities.
Forms and skins are the main product the studio sells. Visual quality is the key selling point.

## 1b. Visual style
- **Decided by Ziyue (2026-11-26, after seeing the first Wolf): a stylized look closer to Palworld.** This reverses the earlier "more realistic" decision. Creatures have a bold readable silhouette, friendly proportions (a larger head, thicker limbs), simple clean shapes, and hand-painted style textures. The reason is data: the realistic Wolf with real fur needed dense geometry and fur strands, which is a lot of data for little gain. **Detail comes from textures, not from triangles or strands.**
- **Per-form budget (proposal, Ziyue to confirm):** a medium creature is about 8,000 to 12,000 triangles at the top level of detail, with 3 lower levels of detail. One material per form, with a 2K base color texture (1K for small forms) and a 1K normal map. No dense fur, no hair strands, no Groom. Fur is painted into the texture. A few simple low-poly tufts are allowed on the neck and tail for the silhouette. Skins reuse the same mesh and swap textures and material parameters, so a skin costs texture data only.
- Mood and lighting stay rich and warm (Unreal Lumen and soft shadows), because the lighting is what makes simple shapes look good. The earlier ARK: Survival Ascended look remains a mood reference only, not the model detail target.
- **All art is original.** We use these games only as a rough guide to quality and mood. We do not copy any creature, character, name, design, texture, or asset from them or from any other game.
- Readability first: because skins are the product, every morph needs a clear silhouette and a distinct main color (section 4b).
- Unreal fits this look: Lumen for light, Niagara for effects, material instances for skin variants. Nanite is not required because the meshes are low poly.

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
- Opening: the player starts as an amorphic spirit. The spirit is for **game setup and storytelling only**, with no gameplay. The player picks a starter form during setup, so gameplay always starts in a form. Inhabiting the first form unlocks gaining more forms and morphing at will. See section 3a.
- Visual style: **stylized, closer to Palworld** (decided after the first Wolf), with low-poly models and texture-based detail. Rich lighting. All art is original (section 1b).
- Starters are **very plain and basic archetypes**. Themed variants (such as Ember Fox) are farmable, not starters.
- Roles come from a **skill tree**. Ziyue will detail it later (section 4c, pending).
- Skins are **named after the morph** (section 4).
- Skill points are **earned only, through experience and quest rewards. They are never bought with currency.** Two experience tracks: the player (spirit) track, whose points can be spent on any owned morph, and a per-morph track, whose points must be earned in that morph (section 4d).
- **Prism pricing is deferred.** No Prism prices are set now. Ziyue will cover it later in development (see `REMINDERS.md`).
- Retention goal: a "continual playthrough" game. There is always something new to unlock or farm, so the player's investment feels worthwhile.

Assumed (to confirm):
- Genre: action game with missions or runs (short, repeatable sessions).
- Co-op size: 2 to 4 players.
- Input: keyboard and mouse, plus gamepad support.
- Style: high-fidelity 3D with readable silhouettes. Each form must be easy to tell apart from far away.

## 3a. Opening: the spirit (setup and story only)
The spirit is a **setup and storytelling state, not a gameplay state.** By the time the player is playing, they have already picked a starting form. Gameplay always starts in a form.

**Spirit state**
- The player starts as an **amorphic spirit**: a formless, glowing presence with no body, no skin, and no body type.
- It exists only in the setup and story sequence at the start of a new game. It has no combat, no skills, no threats, and no fail state.
- The spirit is not a form. It is a presentation state outside the body-type tree. It needs a light visual and simple camera or movement for the sequence, but no skeleton or animation set from the tree, and no balance work.
- The player can never return to spirit state during play. (This answers the earlier question. If the story needs a spirit scene later, it is a cutscene, not a playable state.)

**Setup sequence (short)**
1. Story intro: the spirit, the world, and why it needs a body. Short, skippable on later playthroughs.
2. Game setup in the same scene: the player name, and settings such as co-op or solo, if needed.
3. **Starter pick**: the spirit meets one vessel for each top-level body type. The player picks one.
4. **First inhabitation**: the spirit enters the chosen vessel. This uses the morph-in effect and it is the first time the player sees their skin. It must look great, because it shows what the game sells.
5. Gameplay begins in the chosen form.

Target length: a few minutes. It is mostly presentation, so it is cheap to build, but it needs quality visuals and writing.

**Unlock of morphing**
- Inhabiting the first form **unlocks the ability to gain more forms**. It also unlocks the morph action: change into any owned form at will (no time limit, short cooldown only, see section 3).
- The collection screen and the Hub open in steps after inhabitation, so the first mission is not overwhelming. The **market is open from the start** (see section 6b). The first gameplay teaches movement, combat, and then morphing, all as a form.
- Story idea (placeholder): the spirit "remembers" how to take forms as it learns each body. Each new form adds to the collection.

**Co-op and repeat play**
- Setup is per player. Each player does the setup once per save and picks their own starter. A player who joins a co-op game with a finished save skips it.
- A new player joining a friend's game does the setup in their own short scene, then joins in their chosen form.
- The spirit is never shown to other players during gameplay, because it is not a playable state.

**How the first form is chosen (decided)**
- During setup, the player **picks a starter form**.
- There is **one starter per top-level body type**. Each starter is a very basic form of that body type, so the choice shows the variety of the game on the first screen.
- The starter the player picks is **granted free** in setup. All the other starters are **free to acquire through farming and gameplay** (decided). They are marked `starter: true` in their JSON.
- Validator rule: **exactly one starter per top-level body type**, planned types included. A starter's unlock type is `free` or `earn`, never `buy`, `pass`, or `event`. It can still be skipped with Prisms like any earned form.
- **Starters look very plain and basic**: a plain archetype of the body type (a plain wolf, a plain hawk, a plain raptor, a plain human). No elemental or special theme. Themed morphs are variations that players **farm for**. Example: Ember Fox is a farmable variant of the beast, and a plain Wolf is the starter.
- Winged creature and bipedal dinosaur starters are part of the plan now (Hawk and Raptor). Their body types are still `planned` until the art exists.

Starter slots:

| Slot | Top-level body type | Status | Starter (plain) | Farmable variants (examples in data) |
|---|---|---|---|---|
| 1 | Humanoid (bipedal human) | active | Wanderer | none yet |
| 2 | Beast | active | Wolf | Ember Fox, Stone Tortoise |
| 3 | Winged creature | planned | Hawk | Gale Heron |
| 4 | Bipedal dinosaur | planned | Raptor | none yet |

Notes:
- The starter names and stats are placeholders. Wanderer may become a plain "Human". Starters stay plain.
- Adding a new top-level body type adds a new starter slot. The picker shows one card per top-level body type.
- **Unpicked starters are earned in play, for free.** The player does not need to pay for them. They are crafted like other earned morphs (section 3c). They are not unlocked instantly in the hub. So the pick is a first step, not a lock, and every player can own all starters over time.
- **Skip farming with Prisms.** Players can always buy a starter in the market with Prisms to skip the farming for it. This is the same rule as for every other morph (decided: every morph can be bought with Prisms to bypass farming).
- Data: starters use unlock type `earn` with a crafting recipe (`craft`, section 3c) and a Prisms skip price (`skip`, value `deferred` for now). The picked starter is granted by the setup rule and does not use that recipe.
- Farming goal: the unpicked starters are an early target for new players, and they give a reason to play missions in the first sessions.
- Skins for a starter are sold like any other skin. Starters are a good first target for early skin sales, because every player owns one.

Open questions for Ziyue:
- (Answered) Unpicked starters are free to acquire through farming and gameplay.
- Does the spirit get cosmetics (aura, trail) that are sold? (Default: no. The spirit is setup-only and not seen in play, so it would not sell.)

## 3. Core loop
1. Pick a mission (alone or with co-op friends). Choose a starting form.
2. Fight and explore. Collect crafting drops and loot. A dungeon ends in a boss (section 3c).
3. **Morph** between owned forms at any time. A morph has no time limit. A short cooldown after a morph stops swap spam.
4. Finish the mission. Get rewards: form XP, materials, gear. Spectrums drop from wild enemies, not from missions.
5. Spend rewards in the Hub: level up forms, unlock skills, equip skins, craft or buy forms.
6. Start the next mission.

Because morphs do not expire, **form choice is a build choice**. A player can stay in a favorite form, and the skin is on screen all the time. That is why the camera is third-person.

The "morph" action is still the key moment. It must feel fast and good to watch.

## 3c. Earning a morph: bosses, components, Morphics
Decided by Ziyue. Every earned morph is unlocked by crafting its **Morphic** and consuming it.

**Terms**
- **Morphic**: the crafted item for one morph, named "<morph name> Morphic" (for example "Ember Fox Morphic"). It is a crafting currency specific to that morph. Consuming it unlocks the morph. (An earlier draft said "essence". That term is now only a crafting component.)
- **Component**: a drop that is one input of a Morphic recipe (an ear, a tail, an essence).

**Flow**
1. The player runs a dungeon. A dungeon ends in a **boss**. Example: an Ember Fox boss.
2. The boss can drop **crafting components** for its morph (ears, tail, essence). Drops use **loot tables**: in solo play the Ember Fox boss has a **20 percent chance** to roll on its crafting material loot table (placeholder). The table then picks one item: **50% Ember Fox ear, 25% Ember Fox tail, 25% Ember Fox essence** (placeholder). So a boss kill gives either nothing or one material. **The boss never drops the Morphic itself**, because that would skip the whole farming process. It also never drops Spectrums.
3. The player collects all components of the recipe, and also pays a set amount of the morph's **own category Spectrum** (Ember Fox is a beast, so Green). **Spectrums drop only from regular enemies found in the wild** (for example regular Ember Foxes), so the player must also farm out in the world. This diversifies the farming (section 6c).
4. The player crafts the Morphic and consumes it. The morph is unlocked.

**Example recipe (placeholder numbers):** Ember Fox Morphic = 2 Ember Fox ears + 1 Ember Fox tail + 1 Ember Fox essence + 80 Green Spectrums.

**Rules**
- Components are specific to one morph (`item.<morph>.<part>`) and drop only from that morph's boss. Spectrums drop only from wild enemies (section 6c) and cannot be converted, so the player must fight that category in the wild.
- Two drop systems, kept apart: the **boss drops** (`data/boss_drops.json` sets the roll chance and names a loot table in `data/loot_tables.json`, components only) and the **wild-enemy table** (`data/drops.json`, Spectrums only).
- **Loot tables** (`data/loot_tables.json`): a list of items with a weight in percent. The weights of one table sum to 100. A roll picks one item.
- The 20 percent solo chance, the component counts, and the Spectrum amounts are **placeholders**. They need playtesting. **Multiplayer scaling is not defined yet.**
- Prisms skip all of this: buying the morph in the market with Prisms bypasses the crafting (section 6). Spectrums and components cannot be bought.
- Show drop chances and recipes in the game (Teen+ care, no hidden odds).

**Data** (`unlock.craft` on every `earn` form, and the boss table in `data/boss_drops.json`, checked by the validator)
```json
"craft": {
  "morphic": "Ember Fox Morphic",
  "source_boss": "boss.ember_fox",
  "components": [
    { "item": "item.ember_fox.ear", "count": 2 },
    { "item": "item.ember_fox.tail", "count": 1 },
    { "item": "item.ember_fox.essence", "count": 1 }
  ],
  "spectrum": { "id": "green", "amount": 80 }
}
```
**Planned (not designed):** more loot tables will be added later, for wild enemies and bosses, for other crafting and materials. Ziyue has no ideas for them yet, so they are left for when they are relevant. The validator accepts extra tables in `data/loot_tables.json`. Every table must still have weights that sum to 100, and no table may hold a Morphic or a Spectrum.

Boss entry (`data/boss_drops.json`) and its loot table (`data/loot_tables.json`):
```json
{ "boss": "boss.ember_fox", "form_id": "form.ember_fox", "roll_chance_solo": 0.2,
  "loot_table": "loot.boss.ember_fox.materials" }

{ "id": "loot.boss.ember_fox.materials", "entries": [
  { "item": "item.ember_fox.ear", "weight": 50 },
  { "item": "item.ember_fox.tail", "weight": 25 },
  { "item": "item.ember_fox.essence", "weight": 25 } ] }
```
The other earned morphs have placeholder tables, with weights set in proportion to the recipe counts.
The validator requires: a recipe on every earned morph; the name "<morph name> Morphic"; boss id `boss.<morph>`; every earned morph has a boss entry with a loot table; the table weights sum to 100; the table holds exactly the recipe components, each table belongs to one boss; a loot table never holds a Morphic or a Spectrum; at least one component, each with a count of 1 or more and an id that starts with `item.<morph>.`; and a Spectrum amount in the morph's own category Spectrum. `unlock.cost` (fragments) is removed from forms.

## 3b. Retention: always something to do
Goal: a player at any level has a next target.
- **Form mastery**: each form has levels, skill upgrades, and mastery rewards (titles, emotes, skin variants).
- **Farm targets** (every one can be skipped with currency, see section 6): dungeon bosses drop crafting components for a morph. Collect all of them, add Spectrums, and craft the morph's Morphic (section 3c).
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
| role | Tank, Striker, Support, Scout, Controller. **Placeholder** until the skill tree is defined (section 4c). |
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
- **Skins are named after the morph.** A form's default skin has the same name as the form (the Wolf form has the "Wolf" skin). A form-exclusive skin name starts with the morph's name (for example "Ember Fox" or "Ember Fox: Frostbite"). The validator checks this. A skin for a body type (not tied to one form) is named after the morph look it shows.
- A skin is made for one base and uses that base's skeleton, so all base animations work on it.
- **A skin works on any form in its base, and never on a form in another base.** A skin made for a humanoid would look out of proportion on a beast body. The validator rejects it.

A **Skill** has: id, type (attack, buff, move, summon), cooldown, cost, effect list, and VFX id.
Effects use a small shared set of building blocks (damage, heal, push, status, spawn).
New forms mostly recombine these blocks.

A JSON schema checks every data file in CI before import.

## 4b. Body types (a tree)
A **body type** is a node in a tree. Forms under one top-level body type share a skeleton and one animation set.
This lets us make many forms: a new form is a new look plus skills, not a new animation set.

Naming (Ziyue): the family "Four-legged beast" is now **Beast**, and "Bird" is now **Winged creature**. Ids stay `base.quadruped*` and `base.bird*` so data and saves do not break. Winged creature is a winged creature that usually stands and walks on two legs and has two wings. It covers birds and may later cover other winged shapes. Beast has four legs and can include four-legged dinosaurs. Decided by Ziyue: four-legged dinosaurs (such as a triceratops type) are large beasts (`base.quadruped.large`).

Structure: **top-level body type > subcategory > form**. Example: Beast > Small beast > Ember Fox.
- The **top level** (root) sets the skeleton and the required animation list.
- A **subcategory** sets size and build (small, medium, large). It **inherits the skeleton and all animations** from its parent and retargets them to its proportions.
- A **form** declares the node it uses. Usually that is a subcategory.
- Deeper levels are allowed when needed (for example: Large beast > Heavy large beast). One more segment per level.

```
base.humanoid                  Humanoid
  base.humanoid.medium         human, orc, elf
  base.humanoid.short          dwarf, gnome, halfling
  base.humanoid.large          ogre, giant
base.quadruped                 Beast
  base.quadruped.small         fox, lynx, small canine      <- Ember Fox (farmable)
  base.quadruped.medium        large cat, large canine
  base.quadruped.large         bear, boar, tortoise, four-legged dinosaur  <- Stone Tortoise
base.bird (planned)            Winged creature
  base.bird.medium             heron, hawk                  <- Gale Heron (farmable)
  base.bird.large              eagle, roc
base.biped_dino (planned)      Bipedal dinosaur
  base.biped_dino.medium       raptor
  base.biped_dino.large        rex type
```

### 4b-1. Proposal: define subcategories by rig and gait, not by species (draft, needs Ziyue's choice)
Problem (Ziyue): if the top level is broad, one animation set must suit very different animals. A wolf, a bear and a tortoise do not share a good walk.

Proposal:
- **Top level stays the body type.** It sets the skeleton layout, the Spectrum color and the required animation list.
- **A subcategory is a rig profile.** It is a set of bone proportions plus a gait set (walk, run, jump, attack) that the whole group can share. Size (small, medium, large) is then a scale of that profile, not the main split.
- **Test for a new species.** A species fits an existing subcategory when its bones map to the profile and the shared animations play with only a scale change. If it needs a different gait or a different spine, it needs its own subcategory.
- **A new species under an existing subcategory costs no animation work.** Example: a Frost Wolf is a new look plus skills under the canine profile. A jackal or a fox fits it too.
- **Ids.** Existing ids stay. New profiles would use one more segment, for example `base.quadruped.canine.medium`. Nothing changes in the data until Ziyue picks an option.

Draft split for Beast (to check with Ziyue):

| Profile | Gait | Species that fit | Forms today |
|---|---|---|---|
| Canine | Trot and lope, flexible spine | wolf, fox, jackal, coyote, dog | Wolf, Ember Fox |
| Feline | Stalk and pounce, very flexible spine | lynx, lion, panther | none yet |
| Bear and boar | Heavy plantigrade walk | bear, boar | none yet |
| Hoofed | Long legs, trot and gallop | stag, deer, horse | Prism Stag |
| Shelled | Slow walk, no real run, head and limbs retract | tortoise, turtle | Stone Tortoise |
| Four-legged dinosaur | Heavy, tail balance, charge | triceratops, ankylosaur | none yet |

Species that would need their own subcategory (they do not fit the canine profile): cats, bears and boars, hoofed animals, shelled animals and four-legged dinosaurs. Heron, a tall wading bird, would also need its own profile under Winged creature, apart from hawk (a short-legged perch and dive flier). Raptor stays alone under Bipedal dinosaur for now.

Cost: each profile is one rig and one animation set (12 required animations). More profiles mean more animation work but the animations fit every form in the group. Order of work: canine first (Wolf is the quality test), then the profile of the next form that ships.

### 4b-2. Proposal: Walkers, Swimmers and Flyers on top; subcategories own skeleton, gait and mesh (draft, not applied)
Decision (Ziyue): the overall categories are **Walkers, Swimmers and Flyers**. From there we create subcategories. Each subcategory is a unique **skeleton, gait set and base mesh**. Skins attach to that mesh, and different morphs are made by putting a skin and skills on a subcategory.

Levels:
- **Top category (movement domain):** Walker, Swimmer or Flyer. It has no skeleton, no gait and no mesh. It only groups subcategories.
- **Subcategory:** owns the `rig` (skeleton), the `gait` set, the required animations and the base mesh (`mesh`). Skins fit a subcategory mesh. A new morph under a subcategory is a new skin plus skills, with no new animation work.
- **Size:** a scale of the subcategory mesh (small, medium, large), with optional animation overrides.

Mapping of the existing groups under the three top categories (new ids are proposed; every existing body-type id would change):

| Top category | Subcategory | Color | Old id | Proposed id | Forms today |
|---|---|---|---|---|---|
| Walker | Humanoid | Red | `base.humanoid.*` | `base.walker.humanoid` (sizes: short, medium, large) | Wanderer |
| Walker | Canine | Green | `base.quadruped.small`, `.medium` | `base.walker.canine` (small, medium) | Ember Fox, Wolf |
| Walker | Hoofed | Green | `base.quadruped.medium` | `base.walker.hoofed` (medium) | Prism Stag |
| Walker | Shelled | Green | `base.quadruped.large` | `base.walker.shelled` (large) | Stone Tortoise |
| Walker | Feline, Heavy beast | Green | new | `base.walker.feline`, `base.walker.heavy` | none (planned) |
| Walker | Four-legged dinosaur | Green | new | `base.walker.quadruped_dino` | none (planned) |
| Walker | Raptor, Tyrant | Green | `base.biped_dino.*` | `base.walker.raptor`, `base.walker.tyrant` | Raptor (planned) |
| Flyer | Flier | Yellow | `base.bird.medium`, `.large` | `base.flyer.flier` (medium, large) | Hawk (planned) |
| Flyer | Wader (heron) | Yellow | `base.bird.medium` | `base.flyer.wader` (medium) | Gale Heron (planned) |
| Swimmer | none yet | Blue | none | `base.swimmer.*` | none |

Decided (Ziyue): a creature that flies is a Flyer, even if it can also walk. So the Gale Heron is a Flier.

Open points for Ziyue:
- Swimmers have no forms yet. Fish, sea creatures and other swimmers would each need their own subcategory.
- Dragons, winged humanoids and centaurs mix movement types. A hybrid goes under the domain of its main gait, and a creature that flies is a Flyer.
- Orange and Purple stay **reserved and unused** for expansion (Ziyue). Raptor and Tyrant are considered beasts for now (Ziyue), so they are Green.

Spectrum colors (Ziyue): color is assigned **per subcategory**, not per top category or family.
- Six colors: red, orange, yellow, green, blue, purple. `data/spectrums.json` stays the source of truth.
- Red: Humanoid. Green: the Beast subcategories (Canine, Feline, Heavy, Hoofed, Shelled, Four-legged dinosaur, Raptor, Tyrant). Yellow: all Flyer subcategories. Blue: all Swimmer subcategories. Orange and Purple: reserved for expansion, unused for now.
- Several subcategories may share a color. The old family groups (Humanoid, Beast, Winged creature, Bipedal dinosaur) are dropped as a level.
- Wild drops follow the subcategory color: an enemy of a subcategory (any size) drops that subcategory's color. `data/drops.json` has one entry per color in use. The validator checks that each active subcategory's color has an entry and that the entry drops that same color.

Validator and data changes when applied:
- A top category has `status` only. It must not have `rig`, `gait`, `mesh`, `required_animations` or `spectrum`. A top category's id is one of `base.walker`, `base.swimmer`, `base.flyer`.
- A subcategory (child of a top category) needs `rig`, `gait`, `mesh`, `skeleton`, `required_animations` and a `spectrum` (a color id). A size (child of a subcategory) has no rig fields.
- A subcategory's `spectrum` must be a color in `data/spectrums.json`. Subcategories may share a color. A color may have no subcategory. Sizes inherit the color.
- A size under a top category, or a subcategory under a subcategory, is an error. Add negative tests for each rule.
- Skins fit a subcategory mesh or one of its sizes. The existing skin rule (narrow by default) stays.
- Forms, skins, skill tree base-variant nodes and drops move to the new ids. `Forms.json` BaseId changes, so the Unreal Data Table needs a re-import by the build thread. The Wolf rig is `rig.walker.canine`.
- `amber` becomes `orange` and `violet` becomes `purple` in the color set.

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
  - A narrow skin for `base.quadruped.small` fits every small beast (fox, lynx, small canine). It does not fit a medium or large beast.
  - A narrow skin for `base.humanoid.short` fits dwarf, gnome, and halfling forms, and no medium humanoid.
- **Broad skins are an option** (`fit: subtree`): the skin fits its node and every node below it. Use this only for shared patterns and materials (for example a fur pattern or an armor-plate set) that look right at every size. A broad skin is the exception, and Ziyue approves each one.
- A skin can also be exclusive to one form (`form_id`). Default looks work this way. This is the narrowest option.
- A player who owns a skin can wear it on any owned form it fits.
- Store UI: show the skin on every owned form it fits, and show which body type it fits.
- Each form has a `default_skin` that fits its body type, so a form always has a look.
- Ownership: a player owns skins and forms separately. Equipping checks the fit rule.
- Art cost: a narrow skin is tested on one node only, which keeps each skin cheap to make and check. Many narrow variations are the main way we grow the skin catalog.

## 4c. Roles and the skill tree
**Direction decided by Ziyue. The detailed tree layout is pending Ziyue's design.**

**One shared tree, with a different start for each form**
- There is **one overall skill tree**, like the ones in Path of Exile or Final Fantasy X: a large map of connected nodes.
- **Each form starts at its own node** on the tree. Forms start in different places, so some forms **reach certain skills faster**. That gives each form a natural role: a form that starts near the guard area reaches guard skills quickly.
- **Players can move anywhere.** Every node can be reached from every start. So a form can **veer away** from its natural role and the player **defines the role they want**.
- Result: roles are not fixed labels. A role is what a player builds on the tree. The start node is a head start, not a limit.

**Base-variant nodes at the start of every tree**
- Every morph's tree begins with **base-variant nodes**: nodes made for a body type, such as small beast.
- **Only a morph of that body type can invest in them.** A small beast can invest in the small-beast nodes. A large beast or a humanoid cannot. A node made for a broader body type (such as beast) can be used by every morph under it.
- **Any points can buy these nodes**: spirit points or morph points. There is no special currency for them.
- The validator checks that each of these nodes names a real body type, that every form has base-variant nodes it can invest in, and that the rules file keeps them payable with any points.

**Respec (decided: it has a cost)**
- A player can respec a morph's tree (undo node choices and spend the points again), and **respec costs Spectrums**. (Ziyue said "likely": Spectrums is the working decision.)
- **Amount and rules are pending.** They will be set later. Not decided yet: the amount, whether the first respec is free, whether the cost scales or is per node or for the whole tree, and any cooldown.
- **Confirmed by Ziyue:** the cost is the respecced morph's own Spectrum color (the color of its body type). Respec is an in-game use of Spectrums. It is not paid in Prisms (see "Currency scope" in section 6).
- Respec returns the points that were spent on that morph's tree. It never changes the spirit balance, which is shared (section 4d).
- Prisms are never used for respec, because Prisms are a market resource and not an in-game cost (confirmed). The validator allows only Spectrums.
- Data: `data/respec.json` holds the cost with `status: pending` and no amount. The validator requires that a respec cost is declared, that it is in Spectrums, that a pending cost has a null amount, and that a cost marked `set` has a whole-number amount.
- Reminder: set the respec cost and rules before M2 (`REMINDERS.md`).

**How it works with the other systems**
- Players spend **skill points** on nodes: spirit points on any owned morph, and each morph's own morph points on that morph only (section 4d).
- **Each morph has its own build** on the shared tree, starting at that morph's node. Switching morph switches to that morph's build. The spirit points are shared, so every morph's build can use the full spirit balance.
- The `role` field on a form is a **placeholder** and may become a label derived from where the player has gone on the tree. Do not rely on it for gameplay.
- Nodes will grant skills, stat changes, and passives. Which skills attach to which nodes is pending.
- Balance: because a paid morph and an earned morph start at different nodes but can reach the same places, power stays equal (section 5). The start node must not give an unfair head start to paid forms.
- Co-op: a team can mix builds. Each player's build is visible to them. (Open: do teammates see each other's build?)

**Data** (`data/skill_tree.json`, `tree_start` on each form)
- A graph of nodes and edges. Each node has an id, a name, and a region. Base-variant nodes also name the body type that may invest in them (`restricted_to_base`). Regions suggest roles (guard, strike, support, scout, control) but do not block anyone.
- Each form names its `tree_start` node.
- **Validator rules:** every edge names real nodes; the tree is **connected**, so every node can be reached from every start (this is what lets players move anywhere); every form has a valid start node.
- **The current tree is a placeholder** (one center node and five 2-node regions in a ring). The layout is pending Ziyue's detailed design. Only the rules above are real.

**Pending: Ziyue's detailed tree design.** Open questions for when Ziyue details it:
1. Node types and sizes (small, notable, keystone), like Path of Exile? Or a grid like Final Fantasy X's Sphere Grid?
2. Respec rules: the cost is decided (Spectrums, pending amount, see above). Left to set: the amount, free first respec, scaling, and any cooldown.
3. Are there locked areas that need a gate (a level or an item)?
4. How many nodes, and how much does each cost? (There is no point cap, so tree size and costs decide how long the "always something to earn" loop lasts.)
5. Does each skill stay within a body type, or can any form learn any skill? (Body types change animations. A skill needs an animation that fits the body.)

## 4d. Experience tracks and skill points
**Decided by Ziyue:**
- Skill points cannot be purchased with currency. They are earned only through **experience** (farming XP) and **quest rewards**.
- There are **two experience tracks**: the player (spirit) track and a per-morph track.

Skill points feed the skill tree (section 4c). They are not sold in the market, not skippable and not bought with Spectrums or Prisms, and not in any bundle or paid pass track.

### The two tracks
| | Spirit track (the player) | Morph track (one per morph) |
|---|---|---|
| Who earns it | The player, the spirit that inhabits any form | Each morph, on its own |
| Experience | Player level | Morph level |
| Skill points | **Spirit points** | **Morph points** |
| Earned | In any form, in any mission | **Only while playing that morph** |
| Spent on | **Every morph the player owns**, each one using the full balance | **Only the morph that earned them** |

**What this means**
- The spirit track is the player's overall progress. **Spirit points are shared by every morph.** Each owned morph can spend the **full spirit balance** on its own upgrade track. So a player with 10 spirit points can put 10 points into the upgrade track of **every** morph they own. Spending on one morph does **not** reduce what another morph can spend.
- When the player **gains a new morph, all their spirit points can be spent on it right away**, because the spirit already earned them. The new morph is playable and buildable from the first minute.
- Spirit points are **not moved or respec'd between morphs.** They are shared, so there is nothing to move: every morph already has access to the whole balance.
- The **morph-specific experience and morph points must be earned** in that morph. A new morph starts at morph level 1 with no morph points. So every morph has its own growth to look forward to, and mastery cannot be skipped.
- Morph points never come from the spirit track, and spirit points are never turned into morph points. The two stay separate.

**Rules (enforced by the validator)**
- Every skill point source belongs to one track. A spirit-track source grants spirit points only. A morph-track source grants morph points only, and it requires that the player is playing that morph.
- Morph points are **never granted or spent through the player track.**
- Spirit points are shared by every owned morph (each can spend the full balance). Morph points can be spent only on the morph that earned them. These are fixed in `data/skill_point_rules.json`, and the validator rejects any change.
- **There is no cap** on spirit points, morph points, or skill points in general. The only limit is how fast a player can earn them. The validator rejects any cap in the rules.
- No price, skip price, or purchase can be attached to spirit points or morph points.

### Sources (`data/skill_point_sources.json`; amounts are pending the tree design)

*Spirit track (earned in any form)*
- Player level-ups (experience).
- Mission clears, and optional mission objectives.
- First defeat of a boss, and first defeat of each enemy category.
- Discoveries and exploration.
- Challenges and achievements.
- Daily and weekly goals.
- Co-op milestones.
- The first time a morph is earned in play (by farming), and the first time a piece of gear is earned in play. Only earning counts: a morph or gear that is bought (market, Prisms) gives no skill points.
- Collection milestones, counted from earned items only.
- Event quests.
- The **free** pass track. The paid track never gives skill points. (Open question: should the pass give points at all? Default: free track only.)

*Morph track (earned only while playing that morph)*
- Morph level-ups (morph experience).
- Morph challenges: goals done with that morph.
- Morph mission objectives done with that morph.

### Design notes
- Why two tracks: the spirit track makes a new morph usable right away, so players are not afraid to try morphs. The morph track keeps each morph worth playing for its own sake, which helps the "always something to farm" goal and the value of owning many morphs.
- Balance: a paid morph and an earned morph both start with zero morph points, and both can use the player's spirit points. Spending money gives no skill points, so power stays equal (section 5).
- Every source gives a fair amount, so no single source is required.
- The point totals and the tree costs are set after Ziyue defines the tree.

**Respec** is covered in section 4c: it costs Spectrums, with the amount and rules pending. Spirit points are never moved or respec'd between morphs.

## 5. Balance rules
- Every form has a strength and a clear weakness.
- Counter-play over raw power. No form is best in all cases.
- Paid forms must be **equal in power** to earned forms (see section 6).
- Rarity changes the look and the effects only.

## 6. Monetization model
**Model: Prisms (premium, sold on Steam) and Spectrums (soft, earned in play). Forms and skins are bought with in-game currency.** No pay-to-win.

Currencies (theme: light and the spectrum of light):
- **Spectrums** (soft): earned only in play. There are several, each with its own color. **Each spectrum is the currency for one type of form**, set by the form's top-level body type. Respec of a form's tree costs its own spectrum.
- **Prisms** (premium): a combination of all spectrums, so in the market they can buy any morph or skin. **Prisms are a market resource and nothing else (confirmed by Ziyue): they are not an in-game cost.** They are bought in Steam bundles. They may also drop in small amounts from play (to confirm).

Spectrum colors (placeholders, set in `data/spectrums.json`; each top-level body type names its spectrum in its JSON):

| Spectrum | Color | Top-level body type (form type) |
|---|---|---|
| Red | `#E5484D` | Humanoid |
| Green | `#30A46C` | Beast |
| Blue | `#3E63DD` | Winged creature (planned) |
| Amber | `#F5A524` | Bipedal dinosaur (planned) |
| Violet | `#8E4EC6` | unused, reserved for a fifth body type |

Rules:
- A skin uses the spectrum of its body type's top level. All forms and skins under one top level share a spectrum.
- A new top-level body type needs a new spectrum (the validator requires one, and no two share). This is one more reason a new top-level type is a big step.
- **Prisms are market-only (confirmed).** They are not used for respec, skill points, or any in-game cost. In the market they can buy any morph, starters included, to bypass farming (section 6).
- Spectrums are earned as **rare drops from wild enemies** of that category (bosses never drop them) (section 6c). Enemies never drop another category's spectrum.
- Crafting components do not cost currency. They drop from boss **loot tables** (section 3c), and bosses never drop Spectrums or Morphics.
- **No conversion (decided): players cannot convert one spectrum into another.** There is no exchange, trade, or swap item, in the market or anywhere else. Each spectrum is only earned by play and only spent on its own form type. Prisms are the one currency that works across types, and they are bought with money, not made from spectrums. The validator rejects any data file that defines a conversion.
- Consequence: a player must fight enemies of a category to earn that category's spectrum. This pushes players to try many form types. It also means a player with a lot of one spectrum cannot spend it on another type, so Prisms are the way to skip farming.
### Currency scope (resolved)
Confirmed by Ziyue:
- **Prisms are only used to buy things in the market** (morphs, skins, and skipping farming). They are never a cost for respec, skill points, upgrades, or any other in-game action. `data/pricing.json` records `prisms_use: market_only`. The validator rejects Prisms anywhere except a market price.
- **Spectrums are in-game currency and are what players farm for.** Uses: respec (the respecced morph's own Spectrum color) and other in-game uses (to detail). They are **not** used in the market and they **do not skip farming**.
- Spectrums are earned only by play (drops from wild enemies only) and cannot be converted.

- UI: each spectrum shows as a colored bar or gem. Prisms show as a white prism that splits into all the colors.

| Item | How to get it |
|---|---|
| Starter forms (3 to 4) | Free for all players |
| Standard forms | Craft the Morphic from boss drops and Spectrums (section 3c), OR skip the farming by buying with Prisms |
| Premium forms | Prisms |
| Skins | Prisms, event rewards, or pass tiers |
| Form XP and skill upgrades | Earned in play only (never bought) |

Skip farming (decided): **there is always an option to skip farming, and it is done with Prisms in the market.** Every morph in the game can be bought with Prisms to bypass farming. Spectrums never skip farming.
- Every `earn` unlock has a `skip` price (the validator requires it).
- **Every earned morph (form), starters included, has a Prisms skip price.** The validator requires it, and rejects any Spectrum skip or market price. While pricing is deferred, the value is the text `deferred`.
- **Prism prices are deferred (decided).** Every morph can be bought with Prisms to bypass farming, but the Prism prices are not set now. The validator rejects any Prism price while `data/pricing.json` says `prism_pricing: deferred`. When Ziyue decides, we change that flag and add the prices. Reminder: `REMINDERS.md`.
- Data example: `"skip": { "prisms": "deferred" }`. Later: `"skip": { "prisms": 300 }`.
- Spectrums are earned by play and are in-game currency only. They cannot skip farming and cannot buy market items.
- Prisms skip farming for any earned morph, starters included. The Prisms price is **to be decided later** (not set now). When set, it should be a convenience, fair against the farming effort (check by playtest).
- Skipping gives the same item as farming. It changes only how the player gets it, so it does not break the no-pay-to-win rule.
- Price care: set skip prices so that farming is a real, fair path and skipping is a convenience. Show both options on the item. Check this with playtests.

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

## 6c. Spectrum drops (wild enemies only)
Decided by Ziyue: players **earn Spectrums as rare drops by defeating regular enemies of a morph category out in the wild** (for example regular Ember Foxes). **Bosses never drop Spectrums.** Bosses drop only crafting components (section 3c). This keeps Spectrum farming in the open world and component farming in dungeons.

**Rules**
- Enemies belong to a **morph category**: a top-level body type (humanoid, beast, winged creature, bipedal dinosaur). Enemy design follows the same body-type tree.
- Defeating an enemy of a category can drop **that category's own Spectrum color**. Humanoid enemies drop Red, beasts drop Green, winged creatures drop Blue, bipedal dinosaurs drop Amber.
- **Body type decides the color (confirmed by Ziyue).** The match is on the top-level body type, so every subcategory inherits it. A wild enemy under beast drops Green, including small beast (for example a regular Ember Fox), medium beast, and large beast. A new subcategory needs no new drop entry. A new top-level type needs its own Spectrum and drop entry.
- Drops are **rare**. The validator caps the drop chance at 10 percent per defeated enemy.
- Enemies never drop another category's Spectrum. (Spectrums cannot be converted, so battle is the way to earn each one.)
- A drop shows as a small glowing colored mote the player picks up. In co-op, each player gets their own drop, so players do not compete for them.
- Drops are tied to battle, not to the form the player is wearing. A player can earn Green from beasts while playing as a humanoid.
- Wild enemies are the only Spectrum source. A boss never drops a Spectrum, and the validator rejects it.

**Why this design**
- It gives a reason to fight each kind of enemy, so missions need variety in enemy categories.
- A player who wants a Green form fights beasts. The choice of mission or region becomes a farming choice, which supports the "always something to farm" goal.

**Data** (`data/drops.json`, checked by the validator)
- One entry per top-level body type: `source` (always `wild_enemy`), `match` (always `body_type_root`), `enemy_base` (the root), `spectrum`, `chance`, `amount_min`, `amount_max`. Boss drops are separate: `data/boss_drops.json` and `data/loot_tables.json` (section 3c).
- The spectrum must be the category's own spectrum. Every active body type needs an entry. The amount range must be valid.
- Example: `{ "enemy_base": "base.quadruped", "spectrum": "green", "chance": 0.03, "amount_min": 1, "amount_max": 3 }`.

**Tuning: needs playtesting**
- The current numbers (3 percent chance, 1 to 3 per drop) are **placeholders**, not tested. Drop rates must be set by playtest.
- Things to test: how long it takes to earn a typical skip price, how it feels to wait for a rare drop, and how long farming takes compared with the Prisms skip price (section 6).
- Possible tuning tools, to decide later: higher chance from elite or boss enemies, a "pity" counter so a long dry streak ends in a drop, and a per-mission cap. Any pity rule must be visible to the player (no hidden odds).
- Teen+ care: show drop chances in the game's info screen.

## 6b. In-game market
Decided by Ziyue: there is an **in-game market that players can use from the beginning**, where they can buy any morph they like.

**What it sells**
- **Any morph, starters included**, for **Prisms** only (bought on Steam). Buying an earned morph skips its farming.
- **Skins** (morphs are ultimately skins), for Prisms only, with the fit rule shown (which body types the skin fits).
- **Currency**: a "Get Prisms" button opens the Steam bundle purchase. All real-money purchases go through Steam.
- **Limited morphs are not sold here** (see below).

**Access**
- Open from the start of gameplay: the first mission ends, or the player walks into the Hub, and the market is there. It is not locked behind progress.
- It is not part of the setup sequence (section 3a). The spirit never sees the market.
- Players can preview any item in 3D before buying (a full try-on, with their equipped skin and any skin on sale).

**How it fits the other rules**
- Buying an earned form in the market is the same as skipping farming (section 6). The same price rules apply: every `earn` item has a `skip` price. A `buy` item has a Prisms price.
- Prisms prices (deferred) must keep farming a real, fair path and the market a convenience. Set them by playtest.
- No pay-to-win: the market sells variety, not power. Bought forms equal earned forms in power (section 5).
- Teen+ care: show the real price, ask for confirmation, and show total Prisms spent on request.
- No loot boxes and no random offers. The market shows fixed prices.

**Starters in the market (decided)**
Every morph, starters included, can be bought with Prisms to bypass farming. So the market sells **any morph** for Prisms. This replaced the earlier rule that blocked Prisms on starters, and the validator no longer rejects it.
- The picked starter is granted free in setup. Unpicked starters are earned in play, or bought in the market.
- Note for pricing: a starter is a very basic form, so its price should be low. Players may feel that a paid basic form is a bad deal. Keep starter prices modest, and show that they can also be earned for free.

**Limited morphs (decided)**
- **Pass and event exclusive morphs are limited.** They are **not available in the market unless Ziyue says so.**
- Data: a form sets `limited: true`. The validator requires it for any `pass` or `event` unlock.
- A limited morph is excluded from the market by default. The market list is built by `tools/build_market.py`, which skips limited forms.
- To sell a limited morph in the market, the form needs a `market_override` with `approved_by: "Ziyue Li"`. (The Prisms price is added later, when Prism pricing is decided.) The validator rejects an override approved by anyone else and an override on a non-limited form.
- Process rule: Claude does not add a `market_override` on its own. It is added only after Ziyue says so for that morph.
- Why: limited morphs keep their special value for the people who earned them in the pass or event. Selling them later is a business decision that stays with Ziyue.
- Design care for teen+: say clearly on the pass or event screen that the morph is limited and how long it is available. No fake urgency.
- Limited morphs are still balanced like any other morph (section 5). Limited means availability, not power.
- Limited morphs cannot be farmed or skipped. They are not `earn` unlocks, so they have no skip price.
- Sample data: Prism Stag is a placeholder pass-exclusive morph.

Other open questions for the market:
- Rotating sales or discounts? (Default: none at first. If used, they must be honest and not fake scarcity.)

Milestone note: the market is built in M3. M1 has no market.

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
