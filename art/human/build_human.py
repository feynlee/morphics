"""Build the base Human (base.walker.humanoid.medium): mesh, painted textures, rig, animations, previews.

Run:  python3 art/human/build_human.py [--render] [--sheet] [--fbx] [--out DIR]
Needs the `bpy` Python module (pip install bpy). Units are meters. The human faces +Y, Z is up.
Rig id: rig.walker.humanoid. Mesh id: mesh.walker.humanoid. Style: stylized, painted textures.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))
import bpy
import morph_lib as L
from morph_lib import lin, smooth, mix, rx, ry, rz, curve

OUT = "art/human/out"
TARGET_TRIS = int(os.environ.get("TARGET_TRIS", "8200"))   # body; parts add about 900
TEX = int(os.environ.get("TEX", "2048"))
for i, a in enumerate(sys.argv):
    if a == "--out":
        OUT = sys.argv[i + 1]
os.makedirs(OUT, exist_ok=True)
scene = L.reset()

# Chibi proportions: legs are 75% as long as in the first draft and everything above the hip drops to match.
def Z(z):
    return z * 0.7527 if z <= 0.93 else z - 0.23


LEG = 0.84 * 0.7527   # thigh + shin length, used by the crouch math


def zt(pt):
    return (pt[0], pt[1], Z(pt[2]))


# ---------------------------------------------------------------- body graph
CENTER = {
    "pelvis": (0, 0, 0.97, 0.185, 0.130),
    "waist": (0, 0, 1.12, 0.165, 0.120),
    "chest": (0, 0, 1.30, 0.205, 0.140),
    "neck": (0, 0.01, 1.48, 0.070, 0.070),
    "chin": (0, 0.03, 1.57, 0.120, 0.120),
    "head": (0, 0.02, 1.69, 0.170, 0.165),
    "crown": (0, 0.01, 1.80, 0.125, 0.125),
}
SIDE = {
    "shoulder": (0.20, 0.0, 1.38, 0.080, 0.080),
    "elbow": (0.40, 0.0, 1.20, 0.063, 0.063),
    "wrist": (0.55, 0.02, 1.03, 0.055, 0.055),
    "hand": (0.61, 0.04, 0.95, 0.075, 0.060),
    "hip": (0.12, 0.0, 0.93, 0.105, 0.105),
    "knee": (0.12, 0.02, 0.52, 0.088, 0.088),
    "ankle": (0.12, -0.01, 0.12, 0.072, 0.072),
    "foot": (0.12, 0.06, 0.06, 0.078, 0.10),
    "toe": (0.12, 0.16, 0.05, 0.072, 0.055),
}
P = {k: (v[0], v[1], Z(v[2]), v[3], v[4]) for k, v in CENTER.items()}
for k, v in SIDE.items():
    P["L_" + k] = (v[0], v[1], Z(v[2]), v[3], v[4])
    P["R_" + k] = (-v[0], v[1], Z(v[2]), v[3], v[4])
E = [("pelvis", "waist"), ("waist", "chest"), ("chest", "neck"), ("neck", "chin"), ("chin", "head"), ("head", "crown")]
for s in "LR":
    E += [("chest", f"{s}_shoulder"), (f"{s}_shoulder", f"{s}_elbow"), (f"{s}_elbow", f"{s}_wrist"),
          (f"{s}_wrist", f"{s}_hand"), ("pelvis", f"{s}_hip"), (f"{s}_hip", f"{s}_knee"),
          (f"{s}_knee", f"{s}_ankle"), (f"{s}_ankle", f"{s}_foot"), (f"{s}_foot", f"{s}_toe")]

body = L.skin_mesh(P, E, "pelvis", "Human_Body", levels=3)
L.clean_and_decimate(body, TARGET_TRIS)
BODY_TRIS = L.tri_count(body)

# ---------------------------------------------------------------- face features placed on the real surface
EYE_X, EYE_Z = 0.072, Z(1.71)
eye = L.surface(body, EYE_X, EYE_Z)
nose_pt = L.surface(body, 0.0, Z(1.655))
mouth = L.surface(body, 0.0, Z(1.60))
cheek = L.surface(body, 0.105, Z(1.65))
assert eye and nose_pt and mouth and cheek, "face surface not found"

# ---------------------------------------------------------------- parts (nose, ears, hair)
parts = [
    L.sphere("Nose", (0, nose_pt[1] - 0.004, nose_pt[2]), (0.030, 0.032, 0.030), seg=10, rings=6),
    L.sphere("Ear_L", (0.165, 0.02, Z(1.69)), (0.030, 0.042, 0.056), seg=10, rings=6),
    L.sphere("Ear_R", (-0.165, 0.02, Z(1.69)), (0.030, 0.042, 0.056), seg=10, rings=6),
    L.sphere("Hair", (0, -0.015, Z(1.785)), (0.182, 0.190, 0.140), seg=18, rings=10),
    L.sphere("Hair_Back", (0, -0.10, Z(1.71)), (0.150, 0.100, 0.125), seg=14, rings=8),
]
SKIN = lin((1.0, 0.78, 0.62))
HAIR = lin((0.58, 0.34, 0.20))
SKIN_SH = lin((0.94, 0.66, 0.52))
for o in parts:
    L.paint(o, (lambda x, y, z: HAIR) if o.name.startswith("Hair") else (lambda x, y, z: SKIN_SH if o.name.startswith("Ear") else SKIN))

# ---------------------------------------------------------------- default (plain) paint: traveler clothes
TUNIC, SASH, TROUSER, BOOT = lin((0.96, 0.40, 0.34)), lin((1.0, 0.92, 0.62)), lin((0.84, 0.66, 0.42)), lin((0.52, 0.34, 0.22))
TUNIC_SH = lin((0.86, 0.30, 0.28))


def body_color(x, y, z):
    return SKIN

L.paint(body, body_color)

# ---------------------------------------------------------------- join and finish
all_objs = [body] + parts
L.join(parts, body)
bpy.ops.object.shade_smooth()
TRIS = L.tri_count(body)
print("TRIANGLES", TRIS)

features = [
    (eye, 0.0420, 0.0385, lin((1.0, 1.0, 0.98)), True),                                      # eye white
    ((eye[0], eye[1], eye[2] - 0.002), 0.0320, 0.0290, lin((0.25, 0.60, 0.35)), True),        # iris
    ((eye[0], eye[1], eye[2] - 0.003), 0.0180, 0.0160, lin((0.05, 0.05, 0.08)), True),        # pupil
    ((eye[0] + 0.009, eye[1] + 0.002, eye[2] + 0.011), 0.0105, 0.0085, (1, 1, 1), True),      # highlight
    ((cheek[0], cheek[1], cheek[2]), 0.040, 0.030, lin((1.0, 0.60, 0.52)), True),             # blush
    ((0.010, mouth[1], mouth[2]), 0.0120, 0.0090, lin((0.70, 0.20, 0.18)), True),             # mouth
    ((0.028, mouth[1], mouth[2] + 0.005), 0.0100, 0.0075, lin((0.70, 0.20, 0.18)), True),
]
W = 0.006
zones = [
    (TROUSER, [("z", Z(0.84), Z(0.80)), ("ax", 0.26, 0.25)]),
    (BOOT, [("z", Z(0.24), Z(0.20)), ("ax", 0.26, 0.25)]),
    (TUNIC, [("z", Z(0.80), Z(0.84)), ("z", Z(1.47), Z(1.46)), ("ax", 0.25, 0.24)]),
    (TUNIC, [("z", Z(1.13), Z(1.14)), ("z", Z(1.47), Z(1.46)), ("ax", 0.45, 0.44)]),
    (SASH, [("z", Z(0.895), Z(0.90)), ("z", Z(0.97), Z(0.965)), ("ax", 0.26, 0.25)]),
    (SASH, [("z", Z(1.45), Z(1.455)), ("z", Z(1.53), Z(1.525)), ("ax", 0.15, 0.14)]),
]
paint_mat = L.paint_material("HumanPaint", features, zones=zones)
base_path, norm_path = L.bake_and_finish(body, paint_mat, OUT, "human", size=TEX)

# ---------------------------------------------------------------- armature (rig.walker.humanoid)
bones = [
    ("root", (0, 0, 0), (0, 0.15, 0), None),
    ("pelvis", (0, 0, 0.95), (0, 0, 1.10), "root"),
    ("spine_1", (0, 0, 1.10), (0, 0, 1.27), "pelvis"),
    ("spine_2", (0, 0, 1.27), (0, 0, 1.45), "spine_1"),
    ("neck", (0, 0.005, 1.45), (0, 0.02, 1.54), "spine_2"),
    ("head", (0, 0.02, 1.54), (0, 0.02, 1.86), "neck"),
]
for s, sd in ((1, "L"), (-1, "R")):
    bones += [
        (f"{sd}_clavicle", (s * 0.04, 0, 1.40), (s * 0.19, 0, 1.40), "spine_2"),
        (f"{sd}_upper_arm", (s * 0.19, 0, 1.40), (s * 0.40, 0, 1.20), f"{sd}_clavicle"),
        (f"{sd}_forearm", (s * 0.40, 0, 1.20), (s * 0.55, 0.02, 1.03), f"{sd}_upper_arm"),
        (f"{sd}_hand", (s * 0.55, 0.02, 1.03), (s * 0.62, 0.04, 0.94), f"{sd}_forearm"),
        (f"{sd}_thigh", (s * 0.12, 0, 0.93), (s * 0.12, 0.02, 0.50), "pelvis"),
        (f"{sd}_shin", (s * 0.12, 0.02, 0.50), (s * 0.12, -0.01, 0.09), f"{sd}_thigh"),
        (f"{sd}_foot", (s * 0.12, -0.01, 0.09), (s * 0.12, 0.12, 0.04), f"{sd}_shin"),
        (f"{sd}_toe", (s * 0.12, 0.12, 0.04), (s * 0.12, 0.19, 0.03), f"{sd}_foot"),
    ]
bones = [(n, zt(h), zt(t), par) for n, h, t, par in bones]
arm_obj = L.build_armature("Human_Armature", bones)
L.bind(body, arm_obj)
P_ = L.Poser(arm_obj)

# ---------------------------------------------------------------- animation
def pose(P, root=(0, 0, 0), root_rot=(0, 0, 0), pelvis=(0, 0, 0), pelvis_dz=0.0, spine=(0, 0, 0), head=(0, 0, 0),
         legL=(0, 0), legR=(0, 0), armL=(0, 0, 0.5, 0), armR=(0, 0, 0.5, 0)):
    """World-axis pose. legs: (thigh swing, knee bend as negative). arms: (swing, elbow, adduct, spread)."""
    P.move("root", *root)
    P.rel("root", *root_rot)
    P.rel("pelvis", *pelvis)
    P.move("pelvis", 0, 0, pelvis_dz)
    P.rel("spine_1", spine[0] * 0.5, spine[1] * 0.5, spine[2] * 0.5)
    P.rel("spine_2", spine[0] * 0.5, spine[1] * 0.5, spine[2] * 0.5)
    P.rel("neck", head[0] * 0.35, head[1] * 0.35, head[2] * 0.35)
    P.rel("head", head[0] * 0.65, head[1] * 0.65, head[2] * 0.65)
    for sd, (th, kn) in (("L", legL), ("R", legR)):
        P.rel(f"{sd}_thigh", th, 0, 0)
        P.rel(f"{sd}_shin", kn, 0, 0)
        P.rel(f"{sd}_foot", -0.8 * (th + kn), 0, 0)
    for sd, s, (sw, el, ad, sp) in (("L", 1, armL), ("R", -1, armR)):
        P.relm(f"{sd}_upper_arm", rx(sw) @ ry(s * ad) @ rz(-s * sp))
        P.rel(f"{sd}_forearm", el, 0, 0)


def crouch(a):
    """Thigh, knee and foot angles that keep the feet planted, and the hip drop."""
    return (a, -2 * a), LEG * (math.cos(a) - 1)


def idle(t, P):
    two = 2 * math.pi
    br = math.sin(two * t)
    sway = math.sin(two * t)
    pose(P, pelvis=(0, 0, 0.02 * sway), pelvis_dz=0.004 * br, spine=(0.012 * br, 0, -0.02 * sway),
         head=(0.02 * br, 0, 0.12 * math.sin(two * t + 1.0)),
         armL=(0.03 * br, 0.12 + 0.03 * br, 0.5 + 0.02 * br, 0), armR=(-0.03 * br, 0.12 - 0.03 * br, 0.5 - 0.02 * br, 0))


def gait(P, t, amp, knee, lean, elbow, arm_amp, bob, twist):
    two = 2 * math.pi
    ph = two * t
    def leg(off):
        a = math.sin(ph + off)
        swing = max(0.0, math.cos(ph + off)) ** 1.5
        return (amp * a, -knee * swing - 0.05)
    lL, lR = leg(0.0), leg(math.pi)
    sL, sR = math.sin(ph), -math.sin(ph)
    pose(P, root=(0, 0, 0), pelvis=(0, 0, twist * sL), pelvis_dz=-bob * abs(math.cos(ph)) + bob * 0.5,
         spine=(-lean, 0, -twist * 1.6 * sL), head=(lean * 0.6, 0, twist * 0.5 * sL), legL=lL, legR=lR,
         armL=(-arm_amp * sL, elbow + 0.2 * max(0, -sL) * 0 + 0.15 * abs(sL), 0.35, 0),
         armR=(-arm_amp * sR, elbow + 0.15 * abs(sR), 0.35, 0))


def walk(t, P):
    gait(P, t, 0.50, 0.95, 0.04, 0.25, 0.38, 0.018, 0.10)


def run(t, P):
    gait(P, t, 0.95, 1.55, 0.22, 1.35, 0.85, 0.04, 0.16)


def jump(t, P):
    c = curve(t, [(0, 0), (0.22, 1), (0.30, 0.3), (0.62, 0.45), (0.80, 1.0), (0.95, 0.0), (1, 0)])
    air = curve(t, [(0, 0), (0.28, 0), (0.45, 1), (0.62, 0), (1, 0)])
    height = 0.55 * 4 * ((t - 0.28) / 0.34) * (1 - (t - 0.28) / 0.34) if 0.28 <= t <= 0.62 else 0.0
    a = 0.75 * c
    a = a * (1 - air) + 0.5 * air          # tucked in the air
    kn = -2 * a * (1 - air) - 0.9 * air
    arms_up = air * 1.9 - c * 0.9 * (1 - air)
    pose(P, root=(0, 0, height), pelvis_dz=-LEG * (1 - math.cos(a)) * (1 - air), spine=(-0.25 * c * (1 - air) + 0.05 * air, 0, 0),
         head=(-0.1 * air, 0, 0), legL=(a, kn), legR=(a * 0.9, kn * 0.9),
         armL=(arms_up, 0.3 + 0.4 * air, 0.5 - 0.3 * air, 0.2 * air), armR=(arms_up, 0.3 + 0.4 * air, 0.5 - 0.3 * air, 0.2 * air))


def attack(t, P):
    c = curve(t, [(0, 0), (0.30, -1), (0.42, 1), (0.60, 1), (1, 0)])
    f = max(c, 0.0)
    pose(P, root=(0, 0.16 * f, 0), pelvis=(0, 0, 0.35 * -c * 0.6), pelvis_dz=-0.04 * f,
         spine=(-0.25 * f, 0, -0.55 * c), head=(0.15 * f, 0, 0.25 * c),
         legL=(0.55 * f, -0.6 * f - 0.05), legR=(-0.35 * f, -0.3 * f - 0.05),
         armR=((1.5 * c if c > 0 else 1.0 * c), 1.5 * (1 - f) + 0.15, 0.35, 0.1 * f),
         armL=(-0.6 * c, 1.1, 0.35, 0))


def hit(t, P):
    k = curve(t, [(0, 0), (0.22, 1), (0.55, 0.45), (1, 0)])
    pose(P, root=(0, -0.12 * k, 0), pelvis_dz=-0.03 * k, spine=(0.38 * k, 0, 0.08 * k), head=(0.35 * k, 0, 0.15 * k),
         legL=(0.25 * k, -0.4 * k), legR=(-0.15 * k, -0.2 * k),
         armL=(0.5 * k, 0.5 * k, 0.5 - 0.5 * k, 0.4 * k), armR=(0.3 * k, 0.4 * k, 0.5 - 0.5 * k, 0.5 * k))


def death(t, P):
    col = curve(t, [(0, 0), (0.28, 1)])
    fall = curve(t, [(0.22, 0), (0.62, 1), (0.72, 0.96), (0.82, 1)])
    a = 1.05 * col * (1 - fall) + 0.2 * fall
    pose(P, root=(0, -0.1 * fall, 0.13 * fall), root_rot=(1.5 * fall, 0, 0.12 * fall),
         pelvis_dz=-LEG * (1 - math.cos(a)) * (1 - fall), spine=(0.2 * col - 0.25 * (1 - fall) * col, 0, 0),
         head=(0.1 + 0.25 * fall, 0, -0.2 * fall), legL=(a, -2 * a * (1 - fall) - 0.15 * fall), legR=(a * 0.8 - 0.2 * fall, -1.6 * a * (1 - fall) - 0.1 * fall),
         armL=(0.6 * col, 0.8 * col, 0.5 + 0.8 * fall, 0.5 * fall), armR=(0.3 * col, 0.6 * col, 0.5 + 0.9 * fall, 0.6 * fall))


ACTIONS = [("idle", 90, idle, True), ("walk", 32, walk, True), ("run", 20, run, True),
           ("jump", 36, jump, False), ("attack_basic", 24, attack, False), ("hit", 18, hit, False),
           ("death", 48, death, False)]
acts = {n: L.make_action(P_, n, ln, fn, loop) for n, ln, fn, loop in ACTIONS}
arm_obj.animation_data.action = acts["idle"]
scene.frame_start, scene.frame_end = 1, 91
scene.render.fps = L.FPS
bpy.ops.object.mode_set(mode="OBJECT") if bpy.context.mode != "OBJECT" else None

# ---------------------------------------------------------------- previews and export
if "--render" in sys.argv or "--sheet" in sys.argv:
    L.build_stage()
    arm_obj.animation_data.action = acts["idle"]
    scene.frame_set(1)
if "--render" in sys.argv:
    views = {"front34": ((3.0, 4.0, 1.2), (0, 0, 0.8), 70), "side": ((5.0, 0.1, 0.9), (0, 0, 0.8), 70),
             "back34": ((-2.6, -3.6, 1.3), (0, 0, 0.8), 70), "head": ((0.9, 1.7, Z(1.8)), (0, 0.02, Z(1.69)), 100)}
    for name, (loc, tgt, lens) in views.items():
        L.render_still(os.path.join(OUT, f"human_{name}.png"), L.camera(loc, tgt, name, lens), samples=int(os.environ.get("SAMPLES", "32")))
        print("rendered", name)
if "--sideattack" in sys.argv:
    L.build_stage()
    L.contact_sheet(arm_obj, ["attack_basic", "jump"], L.camera((5.5, 0.1, 0.9), (0, 0, 0.8), "side", 60), os.path.join(OUT, "human_side_check.png"), tiles=6)
if "--sheet" in sys.argv:
    cam = L.camera((4.4, 3.4, 1.2), (0, 0, 0.8), "sheet", 55)
    L.contact_sheet(arm_obj, [a[0] for a in ACTIONS], cam, os.path.join(OUT, "human_anim_sheet.png"))
    arm_obj.animation_data.action = acts["idle"]

if "--fbx" in sys.argv:
    L.export_fbx(os.path.join(OUT, "SK_Human.fbx"), [body, arm_obj])
    print("exported fbx")
L.write_report(os.path.join(OUT, "human_report.json"), {
    "form": "Human", "base": "base.walker.humanoid.medium", "rig": "rig.walker.humanoid", "mesh": "mesh.walker.humanoid",
    "triangles": TRIS, "body_triangles": BODY_TRIS, "bones": len(arm_obj.data.bones), "texture": TEX, "animations": L.ANIMS})
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "human.blend"))
print("saved", "TRIANGLES", TRIS)
