# Morphics: Engine choice and Steam plan

Status: OPEN DECISION for Ziyue. Extends `DESIGN.md` (question 2 and the storefront part of question 6).
Prices and license terms change. Check each vendor's current terms before you commit.

## 1. Engine comparison (3D, Windows, Steam)

| | Unity | Unreal Engine | Godot |
|---|---|---|---|
| Language | C# | C++ and Blueprints (visual) | GDScript or C# |
| 3D quality out of the box | Good. Wide range of looks. | Best. High-end lighting and effects. | Good for stylized 3D. Behind the other two for high-end. |
| Learning curve | Medium | Steep | Gentle |
| Data-driven forms | ScriptableObjects, Addressables for downloadable content | Data Assets, Data Tables | Custom Resources |
| Steam support | Steamworks.NET or Facepunch.Steamworks (free libraries) | Built-in Steam online subsystem | GodotSteam (community plugin) |
| Cost | Free tier, then paid plans. Check current revenue limits. | Free until a revenue threshold, then a royalty. Check current terms. | Free, MIT license, no royalty |
| Asset and plugin market | Very large | Large | Smaller |
| Build size and speed | Medium | Large and heavy | Small and light |
| Fit for a small team | Strong | Good, but heavy for solo work | Strong, with fewer ready-made tools |

## 2. Recommendation
**Unity** is the default pick for this game.
- C# is easy to learn and works well with AI coding tools.
- The data model in `DESIGN.md` maps well to ScriptableObjects (forms, skins, skills).
- Addressables allow new forms and skins to ship as downloadable content.
- The asset store helps a small team move fast on placeholder art.

Choose **Unreal** if the goal is high-end, realistic 3D and the team has C++ or Blueprint skill.
Choose **Godot** if you want zero licensing cost and a stylized look, and you accept fewer ready-made tools.

Next step: build a one-day test in the top choice (one character, the morph effect, one Steam login) before you commit.

## 3. Steam integration plan

### Setup (one time)
1. Create a Steamworks partner account.
2. Pay the per-game app fee (Steam Direct, currently about USD 100 per game, check current terms).
3. Complete the tax and bank forms. Create the store page.
4. Steam takes a share of sales (commonly 30%). Plan the price model with that in mind.

### Game features to build
| Feature | Steam tool | Phase |
|---|---|---|
| Login and player identity | Steamworks SDK | M1 |
| Achievements and stats | Steam Achievements and Stats | M2 |
| Save sync | Steam Cloud | M2 |
| Paid forms and skins | Steam in-game purchases (microtransactions) or DLC | M3 |
| Item ownership | Steam Inventory Service (optional) | M3 |
| Seasonal pass | DLC or a pass item | M3 |

Design rule: the game checks "does this player own form X?" through ONE ownership interface.
Steam is one back end behind it. This keeps a later move to another store easy.

### Release path
1. **Playtest**: use Steam Playtest or a beta branch for early testers.
2. **Store page early**: publish the "Coming soon" page as soon as there is art and a trailer. Wishlists drive launch sales.
3. **Build upload**: use SteamPipe to upload builds. Keep a default branch and a beta branch.
4. **Steam Next Fest** or a demo: a free demo build helps wishlists.
5. **Launch**: free-to-play on Steam is allowed. Store rules for in-game purchases apply.
6. **After launch**: ship new forms as DLC or in-game store items on a fixed schedule.

### Risks
- Free-to-play games with purchases need clear price display and refund handling.
- 3D art cost per form is the main budget risk (see `DESIGN.md` section 7).
- Do not use real money flows outside Steam's system for Steam builds.

## 4. Decision needed from Ziyue
1. Which engine: Unity (recommended), Unreal, or Godot?
2. Free-to-play on Steam, or a paid base game with paid cosmetics?
3. Is a one-day engine test before the final choice acceptable?
