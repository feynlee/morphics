"""Build the base Hawk (base.flyer.flier.medium): mesh, painted textures, rig, animations, previews.

Run:  python3 art/hawk/build_hawk.py [--render] [--sheet] [--fbx] [--out DIR]
Needs the `bpy` Python module. Units are meters. The hawk faces +Y, Z is up. Rest pose: wings spread (T-pose).
Rig id: rig.flyer.flier. Mesh id: mesh.flyer.flier. Style: flat saturated colors, chunky shapes (matches the test map).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))
import bpy
from mathutils import Vector
import morph_lib as L
from morph_lib import lin, smooth, mix, rx, ry, rz, curve

OUT = "art/hawk/out"
TARGET_TRIS = int(os.environ.get("TARGET_TRIS", "6200"))   # body skin; feathers and toes add about 3,500
TEX = int(os.environ.get("TEX", "2048"))
for i, a in enumerate(sys.argv):
    if a == "--out":
        OUT = sys.argv[i + 1]
os.makedirs(OUT, exist_ok=True)
scene = L.reset()

# ---------------------------------------------------------------- palette (flat, saturated)
RUSSET, DARK, CREAM, GOLD, CAP = (lin((0.82, 0.46, 0.22)), lin((0.36, 0.22, 0.16)), lin((1.0, 0.93, 0.74)),
                                  lin((1.0, 0.80, 0.22)), lin((0.52, 0.30, 0.18)))
RUST = lin((0.90, 0.40, 0.18))

# ---------------------------------------------------------------- body graph
P = {
    "pelvis": (0, -0.14, 0.34, 0.100, 0.100),
    "spine": (0, -0.02, 0.40, 0.125, 0.125),
    "chest": (0, 0.08, 0.46, 0.135, 0.135),
    "neck": (0, 0.13, 0.56, 0.085, 0.085),
    "head": (0, 0.16, 0.665, 0.115, 0.115),
    "crown": (0, 0.155, 0.745, 0.080, 0.080),
    "tail_1": (0, -0.24, 0.34, 0.055, 0.035),
    "tail_2": (0, -0.34, 0.32, 0.035, 0.022),
}
SIDE = {
    "shoulder": (0.10, 0.06, 0.50, 0.050, 0.045),
    "elbow": (0.28, 0.00, 0.50, 0.036, 0.030),
    "wrist": (0.46, 0.08, 0.50, 0.030, 0.026),
    "wtip": (0.60, 0.05, 0.50, 0.016, 0.014),
    "hip": (0.065, -0.02, 0.32, 0.055, 0.055),
    "knee": (0.075, 0.01, 0.22, 0.042, 0.042),
    "ankle": (0.070, -0.02, 0.12, 0.032, 0.032),
    "foot": (0.070, 0.04, 0.035, 0.036, 0.055),
}
for k, v in SIDE.items():
    P["L_" + k] = v
    P["R_" + k] = (-v[0], v[1], v[2], v[3], v[4])
E = [("pelvis", "spine"), ("spine", "chest"), ("chest", "neck"), ("neck", "head"), ("head", "crown"),
     ("pelvis", "tail_1"), ("tail_1", "tail_2")]
for s in "LR":
    E += [("chest", f"{s}_shoulder"), (f"{s}_shoulder", f"{s}_elbow"), (f"{s}_elbow", f"{s}_wrist"),
          (f"{s}_wrist", f"{s}_wtip"), ("pelvis", f"{s}_hip"), (f"{s}_hip", f"{s}_knee"),
          (f"{s}_knee", f"{s}_ankle"), (f"{s}_ankle", f"{s}_foot")]
body = L.skin_mesh(P, E, "pelvis", "Hawk_Body", levels=3)
L.clean_and_decimate(body, TARGET_TRIS)
BODY_TRIS = L.tri_count(body)

# face points on the real surface
eye = L.surface(body, 0.078, 0.685)
cheek = L.surface(body, 0.085, 0.64)
assert eye and cheek

# ---------------------------------------------------------------- parts: beak, toes, feathers
parts = []
BEAK_Y = 0.245


def aim_cone(name, base, direction, length, r1, r2, verts=8, scale=(1, 1, 1)):
    d = Vector(direction).normalized()
    c = Vector(base) + d * length / 2
    rot = Vector((0, 0, 1)).rotation_difference(d).to_euler()
    o = L.cone(name, tuple(c), r1, r2, length, rot=tuple(rot), verts=verts)
    return o


beak = aim_cone("Beak", (0, BEAK_Y - 0.03, 0.655), (0, 0.9, -0.32), 0.115, 0.050, 0.008, verts=10)
parts.append(beak)
for sd, s in (("L", 1), ("R", -1)):
    fx = s * 0.070
    for k, (dx, dy) in enumerate(((0.0, 1.0), (0.45, 0.85), (-0.45, 0.85), (0.0, -0.8))):
        t = aim_cone(f"Toe_{sd}{k}", (fx + s * dx * 0.005, 0.04, 0.02), (s * dx, dy, -0.15), 0.075, 0.016, 0.006, verts=6)
        parts.append(t)


def feather(name, base, d, length, width, color_fn, s, curve_=0.0, lift=0.0, segs=5):
    """Feather on the left side (s=1) or right (s=-1, mirrored). color_fn(u) gives color along the length."""
    b = (s * base[0], base[1], base[2])
    dd = (s * d[0], d[1], d[2])
    o = L.leaf(name, b, dd, length, width, curve=curve_, segs=segs, lift=lift)
    bv, dv = Vector(b), Vector(dd).normalized()
    L.paint(o, lambda x, y, z: color_fn(max(0.0, min(1.0, (Vector((x, y, z)) - bv).dot(dv) / length))))
    return o


def prim_color(u):
    return mix(RUSSET, DARK, smooth(u, 0.45, 0.60))


def sec_color(u):
    c = mix(RUSSET, RUST, smooth(u, 0.2, 0.5))
    return mix(c, CREAM, smooth(u, 0.78, 0.86))


def cov_color(u):
    return mix(RUSSET, RUST, 0.3)


def tail_color(u):
    c = mix(RUST, DARK, smooth(u, 0.50, 0.58) * (1 - smooth(u, 0.70, 0.78)))
    return mix(c, CREAM, smooth(u, 0.86, 0.93))


WRIST, TIP, ELB, SHO = Vector((0.46, 0.08, 0.50)), Vector((0.60, 0.05, 0.50)), Vector((0.28, 0.0, 0.50)), Vector((0.10, 0.06, 0.50))
for sd, s in (("L", 1), ("R", -1)):
    for i in range(8):                                     # primaries on the hand
        u = i / 7
        base = WRIST + (TIP - WRIST) * u * 0.9
        phi = math.radians(22 + u * 62)
        d = (math.sin(phi), -math.cos(phi), 0)
        parts.append(feather(f"Prim_{sd}{i}", tuple(base), d, 0.25 + 0.04 * math.sin(math.pi * u * 0.9), 0.052, prim_color, s))
    for i in range(7):                                     # secondaries on the forearm
        u = i / 6
        base = ELB + (WRIST - ELB) * u
        phi = math.radians(4 + 14 * u)
        d = (math.sin(phi), -math.cos(phi), 0)
        parts.append(feather(f"Sec_{sd}{i}", tuple(base), d, 0.215 - 0.03 * u, 0.058, sec_color, s, lift=0.004))
    for i in range(4):                                     # inner feathers on the upper arm
        u = i / 3
        base = SHO + (ELB - SHO) * u
        d = (math.sin(math.radians(2)), -math.cos(math.radians(2)), 0)
        parts.append(feather(f"Ter_{sd}{i}", tuple(base), d, 0.17, 0.058, sec_color, s, lift=0.008))
    for i in range(9):                                     # coverts on top
        u = i / 8
        base = SHO + (WRIST - SHO) * u
        phi = math.radians(8 + 20 * u)
        d = (math.sin(phi), -math.cos(phi), 0)
        parts.append(feather(f"Cov_{sd}{i}", tuple(base), d, 0.10, 0.05, cov_color, s, lift=0.012, segs=4))
for i in range(7):                                         # tail fan
    phi = (i - 3) * 0.17
    d = (math.sin(phi), -math.cos(phi), -0.10)
    parts.append(feather(f"Tail_{i}", (0, -0.23, 0.335), d, 0.25, 0.062, tail_color, 1, lift=0.0))

# body base colors (vertex), then zones in the shader
L.paint(body, lambda x, y, z: RUSSET)
for o in parts[:9]:
    L.paint(o, (lambda x, y, z: GOLD) if o.name.startswith("Toe") else (lambda x, y, z: mix(GOLD, DARK, smooth(y, 0.31, 0.325))))
L.join(parts, body)
bpy.ops.object.shade_smooth()
TRIS = L.tri_count(body)
print("TRIANGLES", TRIS)

features = [
    (eye, 0.036, 0.0335, lin((0.18, 0.10, 0.06)), True),                                  # dark outline
    (eye, 0.032, 0.028, lin((1.0, 0.82, 0.25)), True),                                    # gold iris
    ((eye[0], eye[1], eye[2] - 0.001), 0.019, 0.016, lin((0.04, 0.03, 0.04)), True),      # pupil
    ((eye[0] + 0.007, eye[1] + 0.002, eye[2] + 0.010), 0.0095, 0.0075, (1, 1, 1), True),  # highlight
]
zones = [
    (CREAM, [("z", 0.46, 0.42), ("z", 0.26, 0.30), ("y", -0.18, -0.14), ("ax", 0.16, 0.14)]),   # belly and thighs
    (CAP, [("z", 0.70, 0.715), ("y", -0.0, 0.03), ("ax", 0.14, 0.12)]),                   # head cap
    (GOLD, [("z", 0.28, 0.26), ("ax", 0.12, 0.11)]),                                      # lower legs
]
paint_mat = L.paint_material("HawkPaint", features, zones=zones)
L.bake_and_finish(body, paint_mat, OUT, "hawk", size=TEX)

# ---------------------------------------------------------------- armature (rig.flyer.flier)
bones = [
    ("root", (0, 0, 0), (0, 0.15, 0), None),
    ("pelvis", (0, -0.14, 0.34), (0, -0.02, 0.40), "root"),
    ("spine", (0, -0.02, 0.40), (0, 0.08, 0.46), "pelvis"),
    ("neck", (0, 0.08, 0.46), (0, 0.13, 0.57), "spine"),
    ("head", (0, 0.13, 0.57), (0, 0.16, 0.74), "neck"),
    ("tail_1", (0, -0.14, 0.34), (0, -0.30, 0.32), "pelvis"),
    ("tail_2", (0, -0.30, 0.32), (0, -0.48, 0.28), "tail_1"),
]
for s, sd in ((1, "L"), (-1, "R")):
    bones += [
        (f"{sd}_wing_1", (s * 0.10, 0.06, 0.50), (s * 0.28, 0.0, 0.50), "spine"),
        (f"{sd}_wing_2", (s * 0.28, 0.0, 0.50), (s * 0.46, 0.08, 0.50), f"{sd}_wing_1"),
        (f"{sd}_wing_3", (s * 0.46, 0.08, 0.50), (s * 0.62, 0.05, 0.50), f"{sd}_wing_2"),
        (f"{sd}_thigh", (s * 0.065, -0.02, 0.33), (s * 0.075, 0.01, 0.22), "pelvis"),
        (f"{sd}_shin", (s * 0.075, 0.01, 0.22), (s * 0.070, -0.02, 0.12), f"{sd}_thigh"),
        (f"{sd}_foot", (s * 0.070, -0.02, 0.12), (s * 0.070, 0.05, 0.02), f"{sd}_shin"),
    ]
arm_obj = L.build_armature("Hawk_Armature", bones)
L.bind(body, arm_obj)
PO = L.Poser(arm_obj)

# ---------------------------------------------------------------- animation
FOLD = {  # folded wing directions (left side; x is mirrored for the right), and roll
    1: ((0.30, -0.80, -0.52), -1.3),
    2: ((0.08, 0.95, -0.10), -1.3),
    3: ((-0.05, -0.95, -0.15), -1.3),
}


def wing(P, sd, s, f=0.0, a=0.0, sweep=0.0, a2=0.0, a3=0.0):
    """f: fold 0..1. a, a2, a3: raise (+) of each segment about the forward axis. sweep: swept back."""
    for i in (1, 2, 3):
        n = f"{sd}_wing_{i}"
        if f > 0.001:
            d, roll = FOLD[i]
            P.aim(n, (s * d[0], d[1], d[2]), amount=f, roll=s * roll)
        else:
            ang = (a, a2, a3)[i - 1]
            sw = sweep if i == 1 else sweep * 0.25
            P.relm(n, rz(-s * sw) @ ry(-s * ang))


def pose(P, root=(0, 0, 0), root_rot=(0, 0, 0), pitch=0.0, roll=0.0, yaw=0.0, dz=0.0, head=(0, 0, 0), tail=(0, 0),
         wL=None, wR=None, legL=(0, 0, 0), legR=(0, 0, 0), tuck=0.0):
    """pitch: nose up is +. legs: (thigh swing, knee, foot) with + forward. tuck 0..1 pulls legs back for flight."""
    P.move("root", *root)
    P.rel("root", *root_rot)
    P.move("pelvis", 0, 0, dz)
    P.rel("pelvis", pitch, roll, yaw)
    P.rel("spine", 0.1 * pitch * 0, 0, 0)
    P.rel("neck", head[0] * 0.4, head[1] * 0.4, head[2] * 0.4)
    P.rel("head", head[0] * 0.6, head[1] * 0.6, head[2] * 0.6)
    P.rel("tail_1", tail[0], 0, tail[1])
    P.rel("tail_2", tail[0] * 0.5, 0, tail[1] * 0.5)
    for sd, s, w, (th, kn, ft) in (("L", 1, wL, legL), ("R", -1, wR, legR)):
        wing(P, sd, s, **(w or {"f": 1.0}))
        P.rel(f"{sd}_thigh", -pitch * (1 - tuck) + th - 1.0 * tuck, 0, 0)
        P.rel(f"{sd}_shin", kn - 0.2 * (1 - tuck) + (0.9 * tuck), 0, 0)
        P.rel(f"{sd}_foot", ft + (0.2 + 0.3 * pitch) * (1 - tuck) - 0.5 * tuck, 0, 0)


PERCH = 0.5


def idle(t, P):
    two = 2 * math.pi
    br = math.sin(two * t)
    pose(P, pitch=PERCH + 0.015 * br, dz=0.003 * br, head=(-PERCH + 0.04 * br, 0.1 * math.sin(two * t), 0.45 * math.sin(two * t + 0.4)),
         tail=(-0.1 + 0.03 * br, 0.08 * math.sin(two * 2 * t)),
         wL={"f": 1.0}, wR={"f": 1.0})


def walk(t, P):
    two = 2 * math.pi
    ph = two * t
    a = math.sin(ph)
    lift = lambda o: max(0.0, math.cos(ph + o)) ** 1.5
    pose(P, root=(0, 0, 0), pitch=PERCH - 0.05 + 0.03 * abs(math.cos(ph)), roll=0.07 * a, yaw=-0.05 * a, dz=-0.012 * abs(math.sin(ph)),
         head=(-PERCH + 0.15 * math.sin(2 * ph) * 0.5, 0.0, 0.1 * a), tail=(-0.12 + 0.06 * math.sin(2 * ph), 0.1 * a),
         legL=(0.55 * a, -0.7 * lift(0), 0.3 * lift(0)), legR=(-0.55 * a, -0.7 * lift(math.pi), 0.3 * lift(math.pi)))


def run(t, P):
    two = 2 * math.pi
    ph = two * t
    a = math.sin(ph)
    lift = lambda o: max(0.0, math.cos(ph + o)) ** 1.5
    fl = 0.25 * math.sin(ph * 2)
    pose(P, pitch=0.15 + 0.04 * math.sin(2 * ph), roll=0.08 * a, dz=-0.02 * abs(math.sin(ph)),
         head=(-0.1 + 0.1 * math.sin(2 * ph), 0, 0.1 * a), tail=(0.12, 0.1 * a),
         wL={"f": 0.55, "a": 0}, wR={"f": 0.55, "a": 0},
         legL=(0.9 * a, -1.0 * lift(0), 0.5 * lift(0)), legR=(-0.9 * a, -1.0 * lift(math.pi), 0.5 * lift(math.pi)))


FLY_Z = 0.8


def fly(t, P):
    two = 2 * math.pi
    ph = two * t
    a = 0.85 * math.sin(ph)
    a2 = 0.55 * math.sin(ph - 0.9)
    a3 = 0.75 * math.sin(ph - 1.7)
    wd = {"f": 0, "a": a, "a2": a2, "a3": a3, "sweep": 0.12 + 0.08 * math.cos(ph)}
    pose(P, root=(0, 0, FLY_Z + 0.06 * math.sin(ph - 0.3)), pitch=-0.12 + 0.07 * math.cos(ph), head=(0.1 - 0.05 * math.cos(ph), 0, 0),
         tail=(-0.15 + 0.1 * math.cos(ph), 0), wL=wd, wR=dict(wd), tuck=1.0)


def glide(t, P):
    two = 2 * math.pi
    sw = math.sin(two * t)
    wd = {"f": 0, "a": 0.16 + 0.03 * sw, "a2": 0.12 + 0.03 * sw, "a3": 0.02 + 0.05 * sw, "sweep": 0.30}
    wd2 = dict(wd, a=0.16 - 0.03 * sw, a2=0.12 - 0.03 * sw, a3=0.02 - 0.05 * sw)
    pose(P, root=(0, 0, FLY_Z + 0.03 * math.sin(two * t)), pitch=-0.10, roll=0.06 * sw, yaw=0.04 * math.sin(two * t + 1),
         head=(0.1, 0, 0.05 * sw), tail=(-0.05, 0.05 * sw), wL=wd, wR=wd2, tuck=1.0)


def jump(t, P):
    crouch = curve(t, [(0, 0), (0.2, 1), (0.28, 0.2), (0.8, 0.0), (0.9, 0.5), (1, 0)])
    air = curve(t, [(0, 0), (0.24, 0), (0.36, 1), (0.66, 1), (0.82, 0), (1, 0)])
    h = 0.45 * 4 * ((t - 0.26) / 0.52) * (1 - (t - 0.26) / 0.52) if 0.26 <= t <= 0.78 else 0.0
    flap = curve(t, [(0.26, 0.0), (0.34, -0.5), (0.48, 0.9), (0.62, 0.1), (0.78, 0.5), (0.9, 0)])
    wd = {"f": 1 - air, "a": flap * air + 0.0, "a2": flap * 0.6 * air, "a3": flap * 0.8 * air, "sweep": 0.1 * air}
    pose(P, root=(0, 0, h), pitch=PERCH + 0.35 * crouch - 0.5 * air, dz=-0.05 * crouch,
         head=(-PERCH + 0.2 * air, 0, 0), tail=(-0.1, 0), wL=wd, wR=dict(wd),
         legL=(0.5 * crouch, -0.5 * crouch, 0), legR=(0.5 * crouch, -0.5 * crouch, 0), tuck=0.8 * air)


def attack(t, P):
    c = curve(t, [(0, 0), (0.30, -1), (0.46, 1), (0.62, 1), (1, 0)])
    f = max(c, 0.0)
    w = max(-c, 0.0)
    wd = {"f": 1 - max(f, w), "a": 0.7 * w + 0.3 * f, "a2": 0.5 * w, "a3": 0.5 * w, "sweep": 0.1 * f}
    pose(P, root=(0, 0.20 * f, 0.08 * w + 0.05 * f), pitch=PERCH + 0.4 * w - 1.1 * f, dz=0,
         head=(-PERCH + 0.3 * w + 0.5 * f, 0, 0), tail=(-0.1 + 0.3 * f, 0), wL=wd, wR=dict(wd),
         legL=(1.5 * f - 0.3 * w, -0.4 * f, 0.4 * f), legR=(1.5 * f - 0.3 * w, -0.4 * f, 0.4 * f))


def hit(t, P):
    k = curve(t, [(0, 0), (0.22, 1), (0.55, 0.4), (1, 0)])
    wd = {"f": 1 - 0.8 * k, "a": 0.5 * k, "a2": 0.4 * k, "a3": 0.5 * k, "sweep": 0.0}
    pose(P, root=(0, -0.10 * k, 0.04 * k), pitch=PERCH + 0.5 * k, roll=0.15 * k, head=(-PERCH + 0.35 * k, 0, 0.3 * k),
         tail=(-0.1 + 0.4 * k, 0), wL=wd, wR=dict(wd), legL=(0.3 * k, 0, 0), legR=(0.3 * k, 0, 0))


def death(t, P):
    fall = curve(t, [(0.05, 0), (0.45, 1), (0.52, 0.94), (0.60, 1)])
    stagger = curve(t, [(0, 0), (0.15, 1), (0.45, 0)])
    wd = {"f": 1 - fall * 0.9, "a": -0.35 * fall, "a2": -0.2 * fall, "a3": -0.3 * fall, "sweep": 0.1 * fall}
    pose(P, root=(0, -0.05 * fall, 0.15 * fall), root_rot=(0, 1.35 * fall, 0), pitch=PERCH + 0.4 * stagger - 0.3 * fall,
         head=(-PERCH + 0.4 * stagger, 0, 0.5 * fall), tail=(-0.1, 0.2 * fall), wL=wd, wR=dict(wd, a=-0.5 * fall),
         legL=(0.9 * fall + 0.3 * stagger, -0.3 * fall, 0), legR=(1.0 * fall + 0.3 * stagger, -0.1 * fall, 0))


ACTIONS = [("idle", 90, idle, True), ("walk", 36, walk, True), ("run", 20, run, True), ("fly", 24, fly, True),
           ("glide", 60, glide, True), ("jump", 30, jump, False), ("attack_basic", 24, attack, False),
           ("hit", 18, hit, False), ("death", 60, death, False)]
acts = {n: L.make_action(PO, n, ln, fn, loop) for n, ln, fn, loop in ACTIONS}
arm_obj.animation_data.action = acts["idle"]
scene.frame_start, scene.frame_end = 1, 91
scene.render.fps = L.FPS

# ---------------------------------------------------------------- previews and export
if "--render" in sys.argv or "--sheet" in sys.argv:
    L.build_stage()
if "--render" in sys.argv:
    # rest pose (wings spread) for the mesh views
    arm_obj.animation_data.action = None
    for b in arm_obj.pose.bones:
        b.rotation_euler = (0, 0, 0)
        b.location = (0, 0, 0)
    views = {"front34": ((1.9, 2.6, 1.1), (0, 0, 0.45), 50), "top": ((0.0, 0.01, 3.6), (0, 0, 0.4), 45),
             "back34": ((-1.9, -2.6, 1.1), (0, 0, 0.45), 50), "head": ((0.5, 0.9, 0.85), (0, 0.16, 0.65), 90)}
    for name, (loc, tgt, lens) in views.items():
        L.render_still(os.path.join(OUT, f"hawk_{name}.png"), L.camera(loc, tgt, name, lens), samples=int(os.environ.get("SAMPLES", "32")))
        print("rendered", name)
    arm_obj.animation_data.action = acts["idle"]
    scene.frame_set(1)
    for name, loc in (("perch_front", (1.3, 1.9, 0.8)), ("perch_back", (-1.3, -1.9, 0.9))):
        L.render_still(os.path.join(OUT, f"hawk_{name}.png"), L.camera(loc, (0, 0, 0.38), name, 50), samples=int(os.environ.get("SAMPLES", "32")))
if "--sheet" in sys.argv:
    cam = L.camera((2.2, 2.2, 0.9), (0, 0, 0.55), "sheet", 40)
    L.contact_sheet(arm_obj, [a[0] for a in ACTIONS], cam, os.path.join(OUT, "hawk_anim_sheet.png"))
    arm_obj.animation_data.action = acts["idle"]

if "--fbx" in sys.argv:
    arm_obj.animation_data.action = acts["idle"]
    L.export_fbx(os.path.join(OUT, "SK_Hawk.fbx"), [body, arm_obj])
    print("exported fbx")
L.write_report(os.path.join(OUT, "hawk_report.json"), {
    "form": "Hawk", "base": "base.flyer.flier.medium", "rig": "rig.flyer.flier", "mesh": "mesh.flyer.flier",
    "triangles": TRIS, "body_triangles": BODY_TRIS, "bones": len(arm_obj.data.bones), "texture": TEX, "animations": L.ANIMS})
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hawk.blend"))
print("saved", "TRIANGLES", TRIS)
