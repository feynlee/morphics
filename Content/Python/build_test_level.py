"""Build /Game/Maps/TestLevel: a small daytime forest playground with a centered third-person placeholder character.
Style: bright, saturated, rounded shapes (original art, built from engine basic shapes, low triangle count).
Terrain is faked with big uniform spheres half buried in the ground (hills). Spheres must be scaled uniformly:
a stretched sphere keeps a round collision shape and would not block the player. Watering holes are ponds ringed by raised mounds so they read as low spots.
Rerun: move Content/Maps/TestLevel.umap away first (new_level refuses to overwrite).
Run headless (use a -script path without spaces) or from the editor's Python console.
"""
import math
import random
import unreal

MAP = "/Game/Maps/TestLevel"
MAT_DIR = "/Game/Maps/Materials"
SHAPES = "/Engine/BasicShapes/"
HALF = 2000  # playground is about 40 m x 40 m

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level_ed = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
random.seed(11)

HILLS = []  # (x, y, sphere_radius, top_height)
PONDS = []  # (x, y, radius)


def flat_material(name, color, rough=0.85, glow=0.0):
    path = "%s/%s" % (MAT_DIR, name)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.load_asset(path)
    mat = tools.create_asset(name, MAT_DIR, unreal.Material, unreal.MaterialFactoryNew())
    c = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
    c.set_editor_property("constant", unreal.LinearColor(*color))
    mel.connect_material_property(c, "", unreal.MaterialProperty.MP_BASE_COLOR)
    r = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 200)
    r.set_editor_property("r", rough)
    mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
    if glow > 0:
        e = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 400)
        e.set_editor_property("constant", unreal.LinearColor(color[0] * glow, color[1] * glow, color[2] * glow))
        mel.connect_material_property(e, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat


def mesh(shape, loc, scale, mat, rot=(0, 0, 0), label=None, shadow=True, collide=True):
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), unreal.Rotator(*rot))
    comp = a.static_mesh_component
    comp.set_static_mesh(unreal.load_asset(SHAPES + shape))
    comp.set_material(0, mat)
    if not shadow:
        comp.set_editor_property("cast_shadow", False)
    if not collide:
        comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    a.set_actor_scale3d(unreal.Vector(*scale))
    if label:
        a.set_actor_label(label)
    return a


def height_at(x, y):
    """Ground height from the hill domes (0 on flat ground)."""
    best = 0.0
    for hx, hy, radius, top in HILLS:
        d = math.hypot(x - hx, y - hy)
        if d < radius:
            best = max(best, top - radius + math.sqrt(radius * radius - d * d))
    return max(best, 0.0)


def near_pond(x, y, pad=0):
    return any(math.hypot(x - px, y - py) < r + pad for px, py, r in PONDS)


def free_spot(min_spawn=450, pond_pad=150, tries=40):
    for _ in range(tries):
        x, y = random.uniform(-HALF, HALF), random.uniform(-HALF, HALF)
        if math.hypot(x, y) > min_spawn and not near_pond(x, y, pond_pad):
            return x, y
    return x, y


def main():
    grass = flat_material("M_Grass", (0.20, 0.55, 0.10))
    grass2 = flat_material("M_GrassLight", (0.38, 0.70, 0.14))
    bark = flat_material("M_Bark", (0.30, 0.17, 0.08))
    leaves = [flat_material("M_Leaf%d" % i, c) for i, c in
              enumerate([(0.10, 0.50, 0.12), (0.22, 0.62, 0.12), (0.45, 0.68, 0.10)])]
    rock = flat_material("M_Rock", (0.45, 0.45, 0.48))
    moss = flat_material("M_Moss", (0.25, 0.50, 0.15))
    water = flat_material("M_Water", (0.10, 0.55, 0.80), rough=0.15)
    sand = flat_material("M_Sand", (0.80, 0.70, 0.45))
    bush = flat_material("M_Bush", (0.08, 0.42, 0.14))
    berries = [flat_material("M_Berry%d" % i, c, rough=0.4) for i, c in
               enumerate([(0.85, 0.05, 0.12), (0.30, 0.10, 0.75), (0.95, 0.35, 0.05)])]
    cloud = flat_material("M_Cloud", (1.0, 1.0, 1.0), glow=0.6)
    flowers = [flat_material("M_Flower%d" % i, c) for i, c in
               enumerate([(0.95, 0.30, 0.45), (0.98, 0.85, 0.20), (0.95, 0.95, 0.95), (0.60, 0.40, 0.95)])]

    level_ed.new_level(MAP)

    # Big flat base so the horizon is green.
    mesh("Cube.Cube", (0, 0, -50), (400, 400, 1), grass, label="Ground")

    # Pond sites first, so hills and props avoid them.
    for px, py, pr in [(900, -700, 380), (-1300, 800, 320), (-200, 1500, 280)]:
        PONDS.append((px, py, pr))

    # Rolling hills: top heights 120 to 380 cm, wide and gentle.
    for i in range(11):
        for _ in range(40):
            x, y = random.uniform(-HALF, HALF), random.uniform(-HALF, HALF)
            if math.hypot(x, y) > 500 and not near_pond(x, y, 600):
                break
        base, top = random.uniform(380, 650), random.uniform(120, 340)
        radius = (base * base + top * top) / (2 * top)  # sphere whose cap is `top` high and `base` wide
        HILLS.append((x, y, radius, top))
        mesh("Sphere.Sphere", (x, y, top - radius), (radius / 50.0,) * 3, random.choice([grass, grass2]), label="Hill_%d" % i)

    # Watering holes: sandy bed and water at ground level, ringed by solid dome mounds so they sit in a low spot.
    for i, (px, py, pr) in enumerate(PONDS):
        mesh("Cylinder.Cylinder", (px, py, 1), (pr / 50.0 * 1.25, pr / 50.0 * 1.25, 0.02), sand, label="PondBed_%d" % i, collide=False)
        mesh("Cylinder.Cylinder", (px, py, 2), (pr / 50.0, pr / 50.0, 0.02), water, label="Pond_%d" % i, collide=False)
        n = 14
        for k in range(n):
            a = 2 * math.pi * k / n + random.uniform(-0.08, 0.08)
            rr = pr * 1.3
            r = random.uniform(150, 190)  # uniform sphere radius
            top = random.uniform(55, 75)
            mesh("Sphere.Sphere", (px + math.cos(a) * rr, py + math.sin(a) * rr, top - r),
                 (r / 50.0,) * 3, random.choice([grass, grass2]), label="PondRim_%d_%d" % (i, k))

    # Stylized trees on the terrain.
    placed = []
    for i in range(26):
        for _ in range(30):
            x, y = free_spot(pond_pad=500)
            if all(math.hypot(x - a, y - b) > 280 for a, b in placed):
                break
        placed.append((x, y))
        gz = height_at(x, y)
        h = random.uniform(2.6, 4.2)
        mesh("Cylinder.Cylinder", (x, y, gz + h * 50 - 50), (0.7, 0.7, h), bark, label="Trunk_%d" % i)
        lm = random.choice(leaves)
        top = gz + h * 100 - 20
        mesh("Sphere.Sphere", (x, y, top + 90), (3.0, 3.0, 2.6), lm, label="Crown_%d" % i, collide=False)
        for k in range(3):
            a = random.uniform(0, 2 * math.pi)
            mesh("Sphere.Sphere", (x + math.cos(a) * 110, y + math.sin(a) * 110, top + random.uniform(10, 70)),
                 (2.0, 2.0, 1.7), lm, label="CrownPuff_%d_%d" % (i, k), collide=False)

    # Berry bushes: soft overlapping blobs with berries. No collision, so the player walks straight through
    # and the camera never snags; keeping them low (under 1 m) hides the body clipping through the leaves.
    for i in range(16):
        x, y = free_spot(min_spawn=250, pond_pad=450)
        gz = height_at(x, y)
        for k in range(5):
            a = 2 * math.pi * k / 5 + random.uniform(-0.3, 0.3)
            d = random.uniform(30, 55)
            sc = random.uniform(1.1, 1.6)
            mesh("Sphere.Sphere", (x + math.cos(a) * d, y + math.sin(a) * d, gz + 15),
                 (sc, sc, sc * 0.7), bush, label="Bush_%d_%d" % (i, k), collide=False)
        mesh("Sphere.Sphere", (x, y, gz + 25), (1.9, 1.9, 1.2), bush, label="BushTop_%d" % i, collide=False)
        bm = random.choice(berries)
        for k in range(10):
            a = random.uniform(0, 2 * math.pi)
            d = random.uniform(10, 85)
            mesh("Sphere.Sphere", (x + math.cos(a) * d, y + math.sin(a) * d, gz + random.uniform(45, 80)),
                 (0.16, 0.16, 0.16), bm, label="Berry_%d_%d" % (i, k), collide=False)

    # Mossy rocks.
    for i in range(14):
        x, y = free_spot(min_spawn=350, pond_pad=300)
        gz = height_at(x, y)
        s = random.uniform(0.8, 2.4)
        rot = (random.uniform(-8, 8), random.uniform(0, 360), random.uniform(-8, 8))
        mesh("Sphere.Sphere", (x, y, gz + s * 15), (s * 1.2,) * 3, rock, rot=rot, label="Rock_%d" % i)
        mesh("Sphere.Sphere", (x, y, gz + s * 50), (s * 0.9, s * 0.7, s * 0.25), moss, rot=rot, label="RockMoss_%d" % i, collide=False)

    # Flowers and grass tufts for color.
    for i in range(70):
        x, y = free_spot(min_spawn=100, pond_pad=100)
        mesh("Sphere.Sphere", (x, y, height_at(x, y) - 35), (0.35, 0.35, 0.35), random.choice(flowers), label="Flower_%d" % i, collide=False)
    for i in range(40):
        x, y = free_spot(min_spawn=100, pond_pad=100)
        mesh("Sphere.Sphere", (x, y, height_at(x, y) - 40), (1.6, 1.6, 0.5), grass2, label="Tuft_%d" % i, collide=False)

    # Clouds: clusters of white puffs high above, no shadows.
    for i in range(9):
        cx, cy, cz = random.uniform(-3500, 3500), random.uniform(-3500, 3500), random.uniform(1800, 2800)
        for k in range(random.randint(4, 6)):
            s = random.uniform(5, 9)
            mesh("Sphere.Sphere", (cx + k * 260 - 650, cy + random.uniform(-120, 120), cz + random.uniform(-40, 60)),
                 (s, s * 0.8, s * 0.45), cloud, label="Cloud_%d_%d" % (i, k), shadow=False, collide=False)

    # Lighting: warm midday sun, bright sky, light haze.
    sun = eas.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1000), unreal.Rotator(0, -48, -30))
    sun.set_actor_label("Sun")
    sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
    sc.set_editor_property("atmosphere_sun_light", True)
    sc.set_editor_property("intensity", 9.0)
    sc.set_editor_property("light_color", unreal.Color(255, 244, 224, 255))
    eas.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0)).set_actor_label("SkyAtmosphere")
    sky = eas.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 500))
    sky.set_actor_label("SkyLight")
    sky.get_component_by_class(unreal.SkyLightComponent).set_editor_property("real_time_capture", True)
    fog = eas.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0))
    fog.set_actor_label("Haze")
    fog.get_component_by_class(unreal.ExponentialHeightFogComponent).set_editor_property("fog_density", 0.012)

    # Slightly boosted saturation for the stylized look.
    ppv = eas.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
    ppv.set_actor_label("StylizedLook")
    ppv.set_editor_property("unbound", True)
    s = ppv.get_editor_property("settings")
    s.set_editor_property("override_color_saturation", True)
    s.set_editor_property("color_saturation", unreal.Vector4(1.15, 1.15, 1.15, 1.0))
    ppv.set_editor_property("settings", s)

    eas.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, 0, 100 + height_at(0, 0))).set_actor_label("PlayerStart")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    world.get_world_settings().set_editor_property("default_game_mode", unreal.load_class(None, "/Script/Morphics.MorphTestGameMode"))

    level_ed.save_current_level()


main()
