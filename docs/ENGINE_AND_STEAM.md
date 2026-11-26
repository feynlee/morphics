# Morphics: Engine and Steam plan

Status: Engine DECIDED by Ziyue: **Unreal Engine** (visual quality sells the morphs).
Extends `DESIGN.md`. Prices and license terms change. Check Epic's and Valve's current terms before you commit.

## 1. Why Unreal
Morphics sells how forms look. Unreal gives the best 3D visuals out of the box:
- Nanite and Lumen for detailed models and lighting.
- Niagara for morph and ability effects.
- Material Editor for skin variants (color, pattern, shine) without new meshes.
- MetaHuman and Control Rig tools for characters and animation.
- Built-in Steam support (Online Subsystem Steam or the Steam plugins).
- Epic's royalty applies after a revenue threshold. Check current terms.

Trade-offs to accept:
- Steeper learning curve and larger builds than Unity or Godot.
- C++ for core systems, Blueprints for content and effects.
- Higher PC hardware needs. Set a minimum spec early and add quality settings.

For reference, the other two engines were considered:

| | Unity | Unreal (chosen) | Godot |
|---|---|---|---|
| 3D quality | Good | Best | Good for stylized |
| Language | C# | C++ and Blueprints | GDScript or C# |
| Learning curve | Medium | Steep | Gentle |
| Cost | Free tier, then plans | Royalty after threshold | Free, MIT |

## 2. Form data in plain JSON
Form, skin, and skill definitions live in **plain JSON files** in the repo (for example `data/forms/*.json`).
- Designers and tools (including AI tools) can edit them without opening the editor.
- A build step imports the JSON into Unreal **Data Assets** or **Data Tables**.
- 3D assets are referenced by asset path (mesh, skeleton, material, Niagara system).
- A JSON schema file checks each file in CI before import.

Example (sketch, not final):
```json
{
  "id": "form.ember_fox",
  "role": "Striker",
  "base_stats": { "hp": 100, "speed": 7, "power": 12, "defense": 4 },
  "skills": ["skill.fox_dash", "skill.flame_burst", "skill.cinder_storm"],
  "model": "/Game/Forms/EmberFox/SK_EmberFox",
  "skins": ["skin.ember_fox.default", "skin.ember_fox.frost"],
  "unlock": { "type": "earn", "cost": 1200 }
}
```
(All names here are placeholders and original.)

## 3. Skin variants in Unreal
- A skin = a material instance, texture set, and optional mesh parts on the SAME skeleton.
- Skins use Niagara VFX sets for premium looks.
- Set a per-form budget (triangles, texture size, material cost) so quality stays high but affordable.

## 4. Steam integration plan

### Setup (one time)
1. Create a Steamworks partner account.
2. Pay the per-game app fee (about USD 100, check current terms).
3. Complete the tax and bank forms. Create the store page.
4. Steam takes a share of sales (commonly 30%). Plan prices with that in mind.

### Game features to build
| Feature | Steam tool | Phase |
|---|---|---|
| Login and player identity | Steamworks SDK / Online Subsystem Steam | M1 |
| Achievements and stats | Steam Achievements and Stats | M2 |
| Save sync | Steam Cloud | M2 |
| Paid forms and skins | Steam in-game purchases or DLC | M3 |
| Item ownership | Steam Inventory Service (optional) | M3 |
| Seasonal pass | DLC or a pass item | M3 |

Design rule: the game checks "does this player own form X?" through ONE ownership interface.
Steam is one back end behind it.

### Release path
1. Playtest with Steam Playtest or a beta branch.
2. Publish the "Coming soon" page early. Wishlists drive launch sales.
3. Upload builds with SteamPipe (default and beta branches).
4. Demo or Steam Next Fest to build wishlists.
5. Launch. Free-to-play is allowed on Steam.
6. After launch: ship new forms as DLC or store items on a fixed schedule.

### Risks
- 3D art cost per form is the main budget risk.
- Unreal builds are large. Plan download size and DLC size.
- Free-to-play with purchases needs clear price display and refund handling.

## 5. Next steps (after design is agreed)
1. Install Unreal and make a one-character test: model, morph effect, Steam login.
2. Write the JSON schema and the importer.
3. Build the M1 prototype.

## 6. Still open for Ziyue
1. Free-to-play on Steam, or a paid base game with paid cosmetics?
2. Art source: in-house, contractor, or marketplace assets for placeholders?
3. Minimum PC spec to target?
