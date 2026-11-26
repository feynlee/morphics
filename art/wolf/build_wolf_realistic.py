"""Build the Wolf (form.wolf) in Blender: mesh, fur, rig, and a preview render.

Run:  python3 art/wolf/build_wolf.py [--render] [--out DIR]
Needs the `bpy` Python module (pip install bpy). Units are meters. The wolf faces +Y, Z is up.
This is the first pass of the quality test. See docs/art/WOLF_BRIEF.md.
"""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Vector

OUT = "art/wolf/out"
for i, a in enumerate(sys.argv):
    if a == "--out":
        OUT = sys.argv[i + 1]
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- body graph (skin modifier)
# name: (x, y, z, radius_x, radius_y). Left side is +X. Mirror pairs are built from L entries.
CENTER = {
    "tail_tip": (0, -1.12, 0.50, 0.035, 0.05),
    "tail_4": (0, -1.03, 0.54, 0.080, 0.09),
    "tail_3": (0, -0.90, 0.62, 0.105, 0.10),
    "tail_2": (0, -0.77, 0.69, 0.085, 0.09),
    "tail_1": (0, -0.64, 0.76, 0.055, 0.07),
    "pelvis": (0, -0.50, 0.82, 0.160, 0.17),
    "spine_2": (0, -0.15, 0.82, 0.120, 0.17),
    "chest": (0, 0.20, 0.76, 0.150, 0.21),
    "withers": (0, 0.42, 0.88, 0.125, 0.16),
    "neck_1": (0, 0.58, 0.94, 0.100, 0.13),
    "neck_2": (0, 0.72, 0.99, 0.090, 0.11),
    "skull": (0, 0.88, 1.01, 0.118, 0.120),
    "muzzle_1": (0, 1.02, 0.965, 0.068, 0.070),
    "muzzle_2": (0, 1.10, 0.945, 0.050, 0.052),
    "nose": (0, 1.15, 0.940, 0.034, 0.034),
}
LEG_L = {
    "f_shoulder": (0.105, 0.30, 0.66, 0.095, 0.115),
    "f_elbow": (0.100, 0.26, 0.45, 0.062, 0.065),
    "f_wrist": (0.100, 0.31, 0.24, 0.038, 0.042),
    "f_paw": (0.100, 0.37, 0.045, 0.050, 0.070),
    "h_hip": (0.125, -0.47, 0.66, 0.130, 0.150),
    "h_thigh": (0.125, -0.40, 0.56, 0.105, 0.125),
    "h_knee": (0.125, -0.30, 0.44, 0.070, 0.080),
    "h_hock": (0.105, -0.56, 0.30, 0.042, 0.048),
    "h_paw": (0.105, -0.50, 0.045, 0.048, 0.068),
}
EDGES = [
    ("nose", "muzzle_2"), ("muzzle_2", "muzzle_1"), ("muzzle_1", "skull"), ("skull", "neck_2"),
    ("neck_2", "neck_1"), ("neck_1", "withers"), ("withers", "chest"), ("chest", "spine_2"),
    ("spine_2", "pelvis"), ("pelvis", "tail_1"), ("tail_1", "tail_2"), ("tail_2", "tail_3"),
    ("tail_3", "tail_4"), ("tail_4", "tail_tip"),
    ("f_shoulder", "f_elbow"), ("f_elbow", "f_wrist"), ("f_wrist", "f_paw"),
    ("h_hip", "h_thigh"), ("h_thigh", "h_knee"), ("h_knee", "h_hock"), ("h_hock", "h_paw"),
]
P = {}
for k, v in CENTER.items():
    P[k] = v
for k, v in LEG_L.items():
    P["L_" + k] = v
    P["R_" + k] = (-v[0], v[1], v[2], v[3], v[4])
E = []
for a, b in EDGES:
    if a in CENTER and b in CENTER:
        E.append((a, b))
    else:
        E.append(("L_" + a, "L_" + b))
        E.append(("R_" + a, "R_" + b))
E += [("L_f_shoulder", "chest"), ("R_f_shoulder", "chest"), ("L_h_hip", "pelvis"), ("R_h_hip", "pelvis")]
names = list(P.keys())
idx = {n: i for i, n in enumerate(names)}

me = bpy.data.meshes.new("WolfBase")
me.from_pydata([P[n][:3] for n in names], [(idx[a], idx[b]) for a, b in E], [])
body = bpy.data.objects.new("Wolf_Body", me)
scene.collection.objects.link(body)
bpy.context.view_layer.objects.active = body
body.select_set(True)
sk = body.modifiers.new("Skin", "SKIN")
sk.use_smooth_shade = True
sk.branch_smoothing = 0.6
for n in names:
    v = me.skin_vertices[0].data[idx[n]]
    v.radius = (P[n][3], P[n][4])
    v.use_root = n == "pelvis"
sub = body.modifiers.new("Sub", "SUBSURF")
sub.levels = 2
sub.render_levels = 2
bpy.ops.object.modifier_apply(modifier="Skin")
bpy.ops.object.modifier_apply(modifier="Sub")
bpy.ops.object.shade_smooth()

# Remesh to clean quad topology, then re-subdivide lightly for smoothness.
rm = body.modifiers.new("Remesh", "REMESH")
rm.mode = "VOXEL"
rm.voxel_size = 0.018
bpy.ops.object.modifier_apply(modifier="Remesh")
sm = body.modifiers.new("Smooth", "CORRECTIVE_SMOOTH")
sm.iterations = 12
sm.factor = 0.8
bpy.ops.object.modifier_apply(modifier="Smooth")
bpy.ops.object.shade_smooth()

# ---------------------------------------------------------------- extra parts
def add_part(name, prim, loc, scale, rot=(0, 0, 0)):
    getattr(bpy.ops.mesh, prim)()
    o = bpy.context.active_object
    o.name = name
    o.location = loc
    o.scale = scale
    o.rotation_euler = rot
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.shade_smooth()
    return o


parts = []
for s, side in ((1, "L"), (-1, "R")):
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.068, radius2=0.012, depth=0.18,
                                    location=(s * 0.090, 0.84, 1.13), rotation=(math.radians(-8), math.radians(s * 12), 0))
    ear = bpy.context.active_object
    ear.name = f"Ear_{side}"
    ear.scale = (1, 0.45, 1)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    sub_e = ear.modifiers.new("s", "SUBSURF"); sub_e.levels = 2
    bpy.ops.object.modifier_apply(modifier="s")
    bpy.ops.object.shade_smooth()
    parts.append(ear)
    eye = add_part(f"Eye_{side}", "primitive_uv_sphere_add", (s * 0.066, 0.97, 1.045), (0.019, 0.013, 0.015))
    parts.append(eye)
nose = add_part("Nose", "primitive_uv_sphere_add", (0, 1.172, 0.945), (0.032, 0.028, 0.024))
parts.append(nose)

# ---------------------------------------------------------------- materials
def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m


skin_mat = new_mat("WolfSkin")
nt = skin_mat.node_tree
bsdf = nt.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.30, 0.25, 0.21, 1)
bsdf.inputs["Roughness"].default_value = 0.8
body.data.materials.append(skin_mat)

fur_mat = new_mat("WolfFur")
nt = fur_mat.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
out = nt.nodes.new("ShaderNodeOutputMaterial")
hair = nt.nodes.new("ShaderNodeBsdfHairPrincipled")
hair.parametrization = "COLOR"
hair.inputs["Roughness"].default_value = 0.45
hair.inputs["Coat"].default_value = 0.1
hair.inputs["Random Roughness"].default_value = 0.2
nt.links.new(hair.outputs[0], out.inputs[0])
pos = nt.nodes.new("ShaderNodeNewGeometry")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(pos.outputs["Position"], sep.inputs[0])
# Coat zones in object space: z (height) and |x|, y.
def ramp(nodes, lo, hi, name):
    mr = nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = lo
    mr.inputs["From Max"].default_value = hi
    mr.clamp = True
    return mr


belly = ramp(nt.nodes, 0.50, 0.72, "belly")            # 0 at belly, 1 on back
nt.links.new(sep.outputs["Z"], belly.inputs["Value"])
spine = ramp(nt.nodes, 0.80, 1.00, "spine")            # darker toward the top line
nt.links.new(sep.outputs["Z"], spine.inputs["Value"])
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 28
noise.inputs["Detail"].default_value = 6
nt.links.new(pos.outputs["Position"], noise.inputs["Vector"])
hinfo = nt.nodes.new("ShaderNodeHairInfo")
cols = {
    "light": (0.72, 0.62, 0.48, 1),
    "coat": (0.17, 0.135, 0.105, 1),
    "dark": (0.045, 0.037, 0.032, 1),
    "grey": (0.30, 0.27, 0.24, 1),
}
def rgb(v):
    n = nt.nodes.new("ShaderNodeRGB")
    n.outputs[0].default_value = v
    return n
c_light, c_coat, c_dark, c_grey = (rgb(cols[k]) for k in ("light", "coat", "dark", "grey"))
mix1 = nt.nodes.new("ShaderNodeMix"); mix1.data_type = "RGBA"
nt.links.new(belly.outputs[0], mix1.inputs["Factor"])
nt.links.new(c_light.outputs[0], mix1.inputs["A"])
# coat vs grey salt-and-pepper by noise
mixg = nt.nodes.new("ShaderNodeMix"); mixg.data_type = "RGBA"
nt.links.new(noise.outputs["Fac"], mixg.inputs["Factor"])
nt.links.new(c_coat.outputs[0], mixg.inputs["A"])
nt.links.new(c_grey.outputs[0], mixg.inputs["B"])
nt.links.new(mixg.outputs[2], mix1.inputs["B"])
mix2 = nt.nodes.new("ShaderNodeMix"); mix2.data_type = "RGBA"
nt.links.new(spine.outputs[0], mix2.inputs["Factor"])
nt.links.new(mix1.outputs[2], mix2.inputs["A"])
nt.links.new(c_dark.outputs[0], mix2.inputs["B"])
# root darker than tip
mix3 = nt.nodes.new("ShaderNodeMix"); mix3.data_type = "RGBA"; mix3.inputs["Factor"].default_value = 0.0
nt.links.new(hinfo.outputs["Intercept"], mix3.inputs["Factor"])
nt.links.new(mix2.outputs[2], mix3.inputs["A"])
tip = rgb((0.30, 0.25, 0.20, 1))
nt.links.new(tip.outputs[0], mix3.inputs["B"])
mixt = nt.nodes.new("ShaderNodeMix"); mixt.data_type = "RGBA"; mixt.inputs["Factor"].default_value = 0.25
nt.links.new(mix2.outputs[2], mixt.inputs["A"]); nt.links.new(mix3.outputs[2], mixt.inputs["B"])
nt.links.new(mixt.outputs[2], hair.inputs["Color"])
# tail tip dark: y < -0.95
tailt = ramp(nt.nodes, -1.0, -0.88, "tailtip")
nt.links.new(sep.outputs["Y"], tailt.inputs["Value"])
mixtail = nt.nodes.new("ShaderNodeMix"); mixtail.data_type = "RGBA"
nt.links.new(tailt.outputs[0], mixtail.inputs["Factor"])
nt.links.new(c_dark.outputs[0], mixtail.inputs["A"])
nt.links.new(mixt.outputs[2], mixtail.inputs["B"])
nt.links.new(mixtail.outputs[2], hair.inputs["Color"])

for o, col, rough in ((parts[2], (0.03, 0.025, 0.02), 0.5),):
    pass
eye_mat = new_mat("WolfEye")
eb = eye_mat.node_tree.nodes["Principled BSDF"]
eb.inputs["Base Color"].default_value = (0.75, 0.48, 0.10, 1)
eb.inputs["Roughness"].default_value = 0.05
nose_mat = new_mat("WolfNose")
nb = nose_mat.node_tree.nodes["Principled BSDF"]
nb.inputs["Base Color"].default_value = (0.02, 0.018, 0.016, 1)
nb.inputs["Roughness"].default_value = 0.25
ear_mat = new_mat("WolfEarSkin")
ear_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.2, 0.15, 0.12, 1)
# Materials of the small parts are set first, then all parts are joined into the body mesh so that
# one weight pass rigs everything. Each part gets a "nofur" vertex group so fur skips eyes, nose, ears.
body.data.materials.append(fur_mat)
for o in parts:
    key_mat = eye_mat if o.name.startswith("Eye") else nose_mat if o.name == "Nose" else ear_mat
    o.data.materials.clear()
    o.data.materials.append(key_mat)
    g = o.vertex_groups.new(name="nofur")
    g.add([v.index for v in o.data.vertices], 1.0, "REPLACE")
    if o.name.startswith("Ear"):
        eg = o.vertex_groups.new(name="ear")
        eg.add([v.index for v in o.data.vertices], 1.0, "REPLACE")
bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()

# ---------------------------------------------------------------- fur (hair particles, preview only)
vg = body.vertex_groups.new(name="fur")
vg_ruff = body.vertex_groups.new(name="ruff")
vg_tail = body.vertex_groups.new(name="tail")
vg_short = body.vertex_groups.new(name="short")
ear_idx = body.vertex_groups["ear"].index
nofur_idx = body.vertex_groups["nofur"].index
for v in body.data.vertices:
    x, y, z = v.co
    w = 1.0
    if any(g.group == nofur_idx for g in v.groups):
        w = 0.0
    elif z < 0.16:
        w = 0.0                       # paws get short fur instead
    elif y > 0.98:
        w = 0.0                       # muzzle gets short fur instead
    vg.add([v.index], w, "REPLACE")
    is_ear = any(g.group == ear_idx for g in v.groups)
    is_part = any(g.group == nofur_idx for g in v.groups)
    short = 1.0 if (is_ear or (not is_part and (v.co[2] < 0.16 or v.co[1] > 0.98))) else 0.0
    vg_short.add([v.index], short, "REPLACE")
    ruff = max(0.0, 1 - abs(y - 0.55) / 0.28) if z > 0.7 else 0.0
    vg_ruff.add([v.index], ruff, "REPLACE")
    vg_tail.add([v.index], 1.0 if y < -0.55 else 0.0, "REPLACE")

def add_fur(name, count, length, vgroup, rough=0.01, children=8, spread=0.012):
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.particle_system_add()
    ps = body.particle_systems[-1]
    ps.name = name
    s = ps.settings
    s.type = "HAIR"
    s.count = count
    s.hair_length = length
    s.child_type = "INTERPOLATED"
    s.rendered_child_count = children
    s.child_percent = max(2, children // 3)
    s.child_radius = spread
    s.child_roundness = 1.0
    s.roughness_1 = rough
    s.roughness_endpoint = 0.04
    s.clump_factor = 0.3
    s.hair_step = 4
    s.material_slot = "WolfFur"
    s.root_radius = 0.10
    s.tip_radius = 0.02
    ps.vertex_group_density = vgroup
    s.use_advanced_hair = False
    return ps


add_fur("fur_body", 14000, 0.05, "fur", rough=0.012, children=10)
add_fur("fur_short", 26000, 0.018, "short", rough=0.01, children=6, spread=0.006)
add_fur("fur_ruff", 3500, 0.10, "ruff", rough=0.02, children=10, spread=0.02)
add_fur("fur_tail", 3500, 0.10, "tail", rough=0.015, children=10, spread=0.02)

# ---------------------------------------------------------------- armature
bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
arm_obj = bpy.context.active_object
arm_obj.name = "Wolf_Armature"
arm = arm_obj.data
arm.name = "WolfRig"
for b in list(arm.edit_bones):
    arm.edit_bones.remove(b)
eb = arm.edit_bones

def bone(name, head, tail, parent=None, connect=False):
    b = eb.new(name)
    b.head = Vector(head)
    b.tail = Vector(tail)
    if parent:
        b.parent = eb[parent]
        b.use_connect = connect
    return b

def p(n):
    return P[n][:3]

bone("root", (0, -0.5, 0.0), (0, -0.3, 0.0))
bone("pelvis", p("pelvis"), p("spine_2"), "root")
bone("spine_1", p("spine_2"), p("chest"), "pelvis", True)
bone("spine_2", p("chest"), p("withers"), "spine_1", True)
bone("neck_1", p("withers"), p("neck_2"), "spine_2", True)
bone("neck_2", p("neck_2"), p("skull"), "neck_1", True)
bone("head", p("skull"), p("muzzle_2"), "neck_2", True)
bone("jaw", (0, 1.00, 0.93), (0, 1.10, 0.915), "head")
for s, side in ((1, "L"), (-1, "R")):
    bone(f"ear_{side}", (s * 0.075, 0.82, 1.07), (s * 0.085, 0.80, 1.17), "head")
tail_pts = [(0, -0.58, 0.78)] + [p(n) for n in ("tail_2", "tail_3", "tail_4", "tail_tip")]
tail_pts.insert(1, p("tail_1"))
prev = "pelvis"
for i in range(len(tail_pts) - 1):
    nm = f"tail_{i + 1}"
    bone(nm, tail_pts[i], tail_pts[i + 1], prev)
    prev = nm
for s, side in ((1, "L"), (-1, "R")):
    pre = side + "_"
    bone(f"{side}_f_upper", P[pre + "f_shoulder"][:3], P[pre + "f_elbow"][:3], "spine_2")
    bone(f"{side}_f_lower", P[pre + "f_elbow"][:3], P[pre + "f_wrist"][:3], f"{side}_f_upper", True)
    bone(f"{side}_f_paw", P[pre + "f_wrist"][:3], P[pre + "f_paw"][:3], f"{side}_f_lower", True)
    bone(f"{side}_h_upper", P[pre + "h_hip"][:3], P[pre + "h_knee"][:3], "pelvis")
    bone(f"{side}_h_lower", P[pre + "h_knee"][:3], P[pre + "h_hock"][:3], f"{side}_h_upper", True)
    bone(f"{side}_h_paw", P[pre + "h_hock"][:3], P[pre + "h_paw"][:3], f"{side}_h_lower", True)
bpy.ops.object.mode_set(mode="OBJECT")

# parent meshes to the armature with automatic weights
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
# fur particle systems must be removed from weight calc: automatic weights uses the mesh only
bpy.ops.object.parent_set(type="ARMATURE_AUTO")

# ---------------------------------------------------------------- animation
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode="POSE")
pb = arm_obj.pose.bones
for b in pb:
    b.rotation_mode = "XYZ"

FPS = 30
scene.render.fps = FPS

def set_rot(name, frame, x=0.0, y=0.0, z=0.0):
    b = pb[name]
    b.rotation_euler = (x, y, z)
    b.keyframe_insert("rotation_euler", frame=frame)

def make_action(name, length, fn):
    act = bpy.data.actions.new(name)
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = act
    for b in pb:
        b.rotation_euler = (0, 0, 0)
        b.location = (0, 0, 0)
    for f in range(1, length + 2):
        t = (f - 1) / length
        fn(t, f)
    act.use_fake_user = True
    return act

def gait(t, f, amp, hock, spine_bob, tail_sw, lat=True):
    two = 2 * math.pi
    # lateral sequence: LH, LF, RH, RF phases
    ph = {"L_h": 0.0, "L_f": 0.25, "R_h": 0.5, "R_f": 0.75} if lat else {"L_h": 0.0, "R_h": 0.1, "L_f": 0.55, "R_f": 0.65}
    for key, off in ph.items():
        a = math.sin(two * (t - off))
        up = max(0.0, math.cos(two * (t - off)))
        sgn = 1 if key.endswith("h") else 1
        if key.endswith("f"):
            set_rot(f"{key[0]}_f_upper", f, x=a * amp)
            set_rot(f"{key[0]}_f_lower", f, x=-up * 0.7 * hock - 0.1)
            set_rot(f"{key[0]}_f_paw", f, x=up * 0.3 * hock)
        else:
            set_rot(f"{key[0]}_h_upper", f, x=-a * amp * 0.9)
            set_rot(f"{key[0]}_h_lower", f, x=up * 0.9 * hock + 0.1)
            set_rot(f"{key[0]}_h_paw", f, x=-up * 0.5 * hock)
    set_rot("pelvis", f, x=math.sin(two * (t * 2)) * spine_bob, z=math.sin(two * t) * 0.05)
    set_rot("spine_1", f, x=-math.sin(two * (t * 2)) * spine_bob * 0.6, z=-math.sin(two * t) * 0.05)
    set_rot("spine_2", f, x=math.sin(two * (t * 2)) * spine_bob * 0.4, z=-math.sin(two * t) * 0.03)
    set_rot("neck_1", f, x=-math.sin(two * (t * 2)) * spine_bob * 0.8)
    set_rot("head", f, x=math.sin(two * (t * 2) + 0.6) * spine_bob * 0.8)
    for i in range(1, 6):
        set_rot(f"tail_{i}", f, z=math.sin(two * t - i * 0.6) * tail_sw, x=0.05)

def idle(t, f):
    two = 2 * math.pi
    br = math.sin(two * t)
    set_rot("spine_1", f, x=br * 0.012)
    set_rot("spine_2", f, x=br * 0.018)
    set_rot("neck_1", f, x=-br * 0.012, z=math.sin(two * t * 0.5) * 0.04)
    set_rot("neck_2", f, z=math.sin(two * t * 0.5) * 0.05)
    set_rot("head", f, x=0.04 + br * 0.01, z=math.sin(two * t * 0.5) * 0.08)
    for i in range(1, 6):
        set_rot(f"tail_{i}", f, z=math.sin(two * t * 2 - i * 0.5) * 0.09, x=0.05)
    set_rot("ear_L", f, z=math.sin(two * t * 3) * 0.04 if int(t * 10) == 3 else 0.0)

acts = {
    "idle": make_action("idle", 90, idle),
    "walk": make_action("walk", 36, lambda t, f: gait(t, f, 0.45, 0.8, 0.02, 0.10)),
    "run": make_action("run", 20, lambda t, f: gait(t, f, 0.95, 1.3, 0.07, 0.14, lat=False)),
}
bpy.ops.object.mode_set(mode="OBJECT")
# Every motion is a sum of sines with whole periods, so the last key equals the first and the loop closes.
arm_obj.animation_data.action = acts["idle"]
bpy.ops.object.mode_set(mode="POSE")
for b in pb:
    b.rotation_euler = (0, 0, 0)
    b.location = (0, 0, 0)
bpy.ops.object.mode_set(mode="OBJECT")
scene.frame_start, scene.frame_end = 1, 91

# ---------------------------------------------------------------- scene + render
def build_stage():
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    g = bpy.context.active_object
    gm = new_mat("Ground")
    gb = gm.node_tree.nodes["Principled BSDF"]
    gb.inputs["Base Color"].default_value = (0.20, 0.24, 0.12, 1)
    gb.inputs["Roughness"].default_value = 1
    g.data.materials.append(gm)
    sun = bpy.data.lights.new("Sun", "SUN")
    sun.energy = 4.0
    sun.color = (1.0, 0.82, 0.62)
    sun.angle = math.radians(3)
    so = bpy.data.objects.new("Sun", sun)
    scene.collection.objects.link(so)
    so.rotation_euler = (math.radians(55), math.radians(10), math.radians(-35))
    fill = bpy.data.lights.new("Fill", "AREA")
    fill.energy = 120
    fill.color = (0.55, 0.65, 1.0)
    fill.size = 6
    fo = bpy.data.objects.new("Fill", fill)
    scene.collection.objects.link(fo)
    fo.location = (-4, 4, 3)
    fo.rotation_euler = (math.radians(60), 0, math.radians(-140))
    w = bpy.data.worlds.new("W")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.62, 0.78, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    scene.world = w

def cam(loc, target, name, lens=70):
    c = bpy.data.cameras.new(name)
    c.lens = lens
    co = bpy.data.objects.new(name, c)
    scene.collection.objects.link(co)
    co.location = loc
    d = Vector(target) - Vector(loc)
    co.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return co

if "--render" in sys.argv:
    build_stage()
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = int(os.environ.get("SAMPLES", "32"))
    scene.cycles.use_denoising = False
    scene.render.resolution_x, scene.render.resolution_y = 960, 600
    scene.render.film_transparent = False
    views = {
        "side": ((6.2, 0.1, 0.95), (0, 0.05, 0.62)),
        "front34": ((3.6, 4.4, 1.5), (0, 0.1, 0.65)),
        "back34": ((-2.8, -4.6, 1.8), (0, -0.1, 0.7)),
        "head": ((1.3, 2.7, 1.3), (0, 0.9, 0.97)),
    }
    only = os.environ.get("VIEWS")
    for name, (loc, tgt) in views.items():
        if only and name not in only.split(","):
            continue
        co = cam(loc, tgt, name, lens=85 if name != "head" else 100)
        scene.camera = co
        scene.render.filepath = os.path.join(OUT, f"wolf_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", name)

if "--strip" in sys.argv:
    # walk cycle contact sheet: 6 frames, side view
    if "--render" not in sys.argv:
        build_stage()
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 12
    scene.render.resolution_x, scene.render.resolution_y = 480, 300
    co = cam((6.2, 0.1, 0.95), (0, 0.05, 0.62), "strip", lens=85)
    scene.camera = co
    arm_obj.animation_data.action = acts["walk"]
    for i, fr in enumerate((1, 7, 13, 19, 25, 31)):
        scene.frame_set(fr)
        scene.render.filepath = os.path.join(OUT, f"walk_{i}.png")
        bpy.ops.render.render(write_still=True)
    arm_obj.animation_data.action = acts["idle"]
    scene.frame_set(1)

if "--fbx" in sys.argv:
    # Game export: mesh (without preview hair) and rig with all actions. Fur becomes cards in Unreal later.
    for ps in list(body.particle_systems):
        pass
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    arm_obj.select_set(True)
    for m in list(body.modifiers):
        if m.type == "PARTICLE_SYSTEM":
            m.show_viewport = False
            m.show_render = False
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, "SK_Wolf.fbx"), use_selection=True, object_types={"ARMATURE", "MESH"},
                             add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False,
                             bake_anim_force_startend_keying=True, axis_forward="Y", axis_up="Z", apply_scale_options="FBX_SCALE_ALL",
                             mesh_smooth_type="FACE", use_armature_deform_only=True, global_scale=100.0)
    print("exported fbx")

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "wolf.blend"))
print("saved")
