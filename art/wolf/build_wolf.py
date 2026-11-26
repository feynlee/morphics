"""Build the stylized low-poly Wolf (form.wolf): mesh, painted textures, rig, animations, preview render.

Run:  python3 art/wolf/build_wolf.py [--render] [--strip] [--fbx] [--out DIR]
Needs the `bpy` Python module (pip install bpy). Units are meters. The wolf faces +Y, Z is up.
Style: Palworld-like, low poly (about 10,000 triangles), detail painted into textures.
See docs/art/WOLF_BRIEF.md. The earlier realistic version is in build_wolf_realistic.py.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

OUT = "art/wolf/out"
TARGET_TRIS = int(os.environ.get("TARGET_TRIS", "10000"))
TEX = int(os.environ.get("TEX", "2048"))
for i, a in enumerate(sys.argv):
    if a == "--out":
        OUT = sys.argv[i + 1]
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- body graph (skin modifier)
# name: (x, y, z, radius_x, radius_y). Friendly proportions: big head, chunky body, thick legs, big tail.
CENTER = {
    "tail_tip": (0, -0.76, 0.52, 0.060, 0.070),
    "tail_4": (0, -0.69, 0.60, 0.100, 0.110),
    "tail_3": (0, -0.59, 0.64, 0.130, 0.130),
    "tail_2": (0, -0.49, 0.64, 0.120, 0.120),
    "tail_1": (0, -0.40, 0.63, 0.090, 0.100),
    "pelvis": (0, -0.24, 0.58, 0.180, 0.200),
    "spine_2": (0, -0.01, 0.58, 0.180, 0.200),
    "chest": (0, 0.17, 0.60, 0.190, 0.220),
    "withers": (0, 0.32, 0.66, 0.170, 0.180),
    "neck_1": (0, 0.42, 0.74, 0.150, 0.150),
    "neck_2": (0, 0.50, 0.82, 0.140, 0.140),
    "skull": (0, 0.58, 0.88, 0.190, 0.170),
    "muzzle_1": (0, 0.76, 0.82, 0.095, 0.100),
    "muzzle_2": (0, 0.85, 0.80, 0.075, 0.070),
    "nose": (0, 0.90, 0.80, 0.045, 0.040),
}
LEG_L = {
    "f_shoulder": (0.110, 0.20, 0.52, 0.100, 0.110),
    "f_elbow": (0.110, 0.20, 0.34, 0.085, 0.090),
    "f_wrist": (0.115, 0.22, 0.17, 0.075, 0.080),
    "f_paw": (0.115, 0.27, 0.05, 0.085, 0.110),
    "h_hip": (0.135, -0.26, 0.50, 0.140, 0.150),
    "h_thigh": (0.145, -0.22, 0.40, 0.125, 0.135),
    "h_knee": (0.145, -0.15, 0.30, 0.095, 0.105),
    "h_hock": (0.125, -0.33, 0.20, 0.075, 0.080),
    "h_paw": (0.125, -0.29, 0.05, 0.085, 0.110),
}
EDGES = [
    ("nose", "muzzle_2"), ("muzzle_2", "muzzle_1"), ("muzzle_1", "skull"), ("skull", "neck_2"),
    ("neck_2", "neck_1"), ("neck_1", "withers"), ("withers", "chest"), ("chest", "spine_2"),
    ("spine_2", "pelvis"), ("pelvis", "tail_1"), ("tail_1", "tail_2"), ("tail_2", "tail_3"),
    ("tail_3", "tail_4"), ("tail_4", "tail_tip"),
    ("f_shoulder", "f_elbow"), ("f_elbow", "f_wrist"), ("f_wrist", "f_paw"),
    ("h_hip", "h_thigh"), ("h_thigh", "h_knee"), ("h_knee", "h_hock"), ("h_hock", "h_paw"),
]
P = dict(CENTER)
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
sk.branch_smoothing = 0.8
for n in names:
    v = me.skin_vertices[0].data[idx[n]]
    v.radius = (P[n][3], P[n][4])
    v.use_root = n == "pelvis"
sub = body.modifiers.new("Sub", "SUBSURF")
sub.levels = 3
bpy.ops.object.modifier_apply(modifier="Skin")
bpy.ops.object.modifier_apply(modifier="Sub")

# ---------------------------------------------------------------- ears (joined into the body mesh)
def add_ear(side, s):
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=0.10, radius2=0.02, depth=0.23,
                                    location=(s * 0.12, 0.56, 1.06), rotation=(math.radians(-6), math.radians(s * 16), 0))
    ear = bpy.context.active_object
    ear.name = f"Ear_{side}"
    ear.scale = (1, 0.5, 1)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return ear

ears = [add_ear("L", 1), add_ear("R", -1)]
bpy.ops.object.select_all(action="DESELECT")
for e in ears:
    e.select_set(True)
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()

# ---------------------------------------------------------------- clean mesh to the triangle budget
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.002)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT")
sm = body.modifiers.new("Smooth", "CORRECTIVE_SMOOTH")
sm.iterations = 6
sm.factor = 0.6
bpy.ops.object.modifier_apply(modifier="Smooth")
tri = body.modifiers.new("Tri", "TRIANGULATE")
bpy.ops.object.modifier_apply(modifier="Tri")
cur = len(body.data.polygons)
dec = body.modifiers.new("Decimate", "DECIMATE")
dec.ratio = min(1.0, TARGET_TRIS / max(1, cur))
bpy.ops.object.modifier_apply(modifier="Decimate")
bpy.ops.object.shade_smooth()
TRIS = len(body.data.polygons)
print("TRIANGLES", TRIS)

# ---------------------------------------------------------------- vertex-color zones (smooth painted regions)
def smooth(x, a, b):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)

def lin(c):
    return tuple(v ** 2.2 for v in c)


COAT, DARK, LIGHT, GREY = lin((0.55, 0.47, 0.40)), lin((0.27, 0.22, 0.19)), lin((0.93, 0.87, 0.76)), lin((0.65, 0.60, 0.55))
PINK = lin((0.70, 0.52, 0.50))


def mix(a, b, t):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))

attr = body.data.color_attributes.new(name="Col", type="FLOAT_COLOR", domain="POINT")
for v in body.data.vertices:
    x, y, z = v.co
    c = COAT
    c = mix(c, GREY, smooth(0.5 - abs(x) * 2.0, 0, 0.5) * 0.35)                 # lighter flanks
    saddle = smooth(z, 0.62, 0.76) * smooth(0.40 - y, -0.1, 0.35) * smooth(y, -0.55, -0.35)
    c = mix(c, DARK, saddle * 0.9)
    c = mix(c, DARK, smooth(z, 0.93, 1.02) * 0.8)                                 # top of head and ears
    ear = smooth(z, 0.97, 1.0)
    belly = (1 - smooth(z, 0.42, 0.55)) * smooth(0.30 - abs(x), 0.02, 0.2)
    c = mix(c, LIGHT, belly * smooth(y, -0.3, -0.1) * smooth(0.45 - y, -0.05, 0.2) * 0.9)
    chest = smooth(y, 0.12, 0.3) * (1 - smooth(z, 0.55, 0.74)) * smooth(0.2 - abs(x), 0.0, 0.14)
    c = mix(c, LIGHT, chest)
    muzzle = smooth(y, 0.70, 0.78) * (1 - smooth(z, 0.80, 0.88))
    c = mix(c, LIGHT, muzzle)
    cheek = smooth(y, 0.50, 0.62) * smooth(abs(x), 0.06, 0.14) * (1 - smooth(z, 0.82, 0.9))
    c = mix(c, LIGHT, cheek * 0.8)
    c = mix(c, LIGHT, (1 - smooth(z, 0.07, 0.14)) * 0.9)                          # light paws
    c = mix(c, DARK, smooth(-0.70 - y, 0.0, 0.08))                                # dark tail tip
    if ear > 0.0 and y > 0.552:
        c = mix(c, PINK, ear)                                                       # inner ear
    attr.data[v.index].color = (*c, 1.0)

def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m


# ---------------------------------------------------------------- UV unwrap
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.006)
bpy.ops.object.mode_set(mode="OBJECT")

# ---------------------------------------------------------------- materials and baking
def stroke_noise(nt, pos_out, scale=(34, 9, 34), detail=5):
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale
    nt.links.new(pos_out, mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.0
    nz.inputs["Detail"].default_value = detail
    nz.inputs["Roughness"].default_value = 0.6
    nt.links.new(mp.outputs[0], nz.inputs["Vector"])
    return nz.outputs["Fac"]

def maprange(nt, value_out, lo, hi, clamp=True):
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.clamp = clamp
    mr.inputs["From Min"].default_value = lo
    mr.inputs["From Max"].default_value = hi
    nt.links.new(value_out, mr.inputs["Value"])
    return mr.outputs[0]

def dist_to(nt, xyz_out, center):
    sub = nt.nodes.new("ShaderNodeVectorMath")
    sub.operation = "SUBTRACT"
    nt.links.new(xyz_out, sub.inputs[0])
    sub.inputs[1].default_value = center
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    nt.links.new(sub.outputs[0], ln.inputs[0])
    return ln.outputs["Value"]

def paint_material():
    m = bpy.data.materials.new("WolfPaint")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(em.outputs[0], out.inputs[0])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    col = nt.nodes.new("ShaderNodeVertexColor")
    col.layer_name = "Col"
    # fur strokes darken and lighten the base color
    st = stroke_noise(nt, geo.outputs["Position"])
    k = maprange(nt, st, 0.3, 0.7)
    mixn = nt.nodes.new("ShaderNodeMix"); mixn.data_type = "RGBA"
    mixn.blend_type = "MULTIPLY"
    mixn.inputs["Factor"].default_value = 1.0
    nt.links.new(col.outputs["Color"], mixn.inputs["A"])
    shade = nt.nodes.new("ShaderNodeMapRange")
    nt.links.new(k, shade.inputs["Value"])
    shade.inputs["To Min"].default_value = 0.78
    shade.inputs["To Max"].default_value = 1.12
    gray = nt.nodes.new("ShaderNodeCombineColor")
    for i in range(3):
        nt.links.new(shade.outputs[0], gray.inputs[i])
    nt.links.new(gray.outputs[0], mixn.inputs["B"])
    cur_col = mixn.outputs[2]
    # facial features by distance from object-space points
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    absx = nt.nodes.new("ShaderNodeMath"); absx.operation = "ABSOLUTE"
    nt.links.new(sep.outputs["X"], absx.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(absx.outputs[0], comb.inputs["X"])
    nt.links.new(sep.outputs["Y"], comb.inputs["Y"])
    nt.links.new(sep.outputs["Z"], comb.inputs["Z"])
    def layer(prev, mask, color):
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
        nt.links.new(mask, mx.inputs["Factor"])
        nt.links.new(prev, mx.inputs["A"])
        mx.inputs["B"].default_value = (*color, 1)
        return mx.outputs[2]
    EYE = (0.105, 0.735, 0.925)
    d_eye = dist_to(nt, comb.outputs[0], EYE)
    cur_col = layer(cur_col, maprange(nt, d_eye, 0.056, 0.048), lin((0.12, 0.09, 0.07)))      # dark outline
    cur_col = layer(cur_col, maprange(nt, d_eye, 0.046, 0.038), lin((0.98, 0.70, 0.22)))       # amber iris
    cur_col = layer(cur_col, maprange(nt, d_eye, 0.027, 0.022), lin((0.04, 0.03, 0.025)))     # pupil
    d_hi = dist_to(nt, comb.outputs[0], (0.098, 0.742, 0.948))
    cur_col = layer(cur_col, maprange(nt, d_hi, 0.012, 0.008), (1, 1, 1))                 # highlight
    d_nose = dist_to(nt, comb.outputs[0], (0.0, 0.91, 0.81))
    cur_col = layer(cur_col, maprange(nt, d_nose, 0.036, 0.030), lin((0.10, 0.08, 0.075)))
    # inner ears: pink-grey in a band near the front of the ear
    nt.links.new(cur_col, em.inputs["Color"])
    return m

def bake(mat, kind, size, path, setup=None):
    img = bpy.data.images.new(os.path.basename(path), size, size, alpha=False, float_buffer=False)
    img.colorspace_settings.name = "sRGB" if kind == "DIFFUSE" else "Non-Color"
    nt = mat.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    nt.nodes.active = tex
    body.data.materials.clear()
    body.data.materials.append(mat)
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 4
    scene.render.bake.margin = 8
    scene.render.bake.use_selected_to_active = False
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    if kind == "DIFFUSE":
        scene.cycles.bake_type = "EMIT"
        bpy.ops.object.bake(type="EMIT")
    else:
        bpy.ops.object.bake(type="NORMAL")
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    return img

paint = paint_material()
base_path = os.path.join(OUT, "wolf_basecolor.png")
base_img = bake(paint, "DIFFUSE", TEX, base_path)

# normal map: bump from the fur stroke noise
nm = bpy.data.materials.new("WolfNormalBake")
nm.use_nodes = True
nt = nm.node_tree
bsdf = nt.nodes["Principled BSDF"]
geo = nt.nodes.new("ShaderNodeNewGeometry")
st = stroke_noise(nt, geo.outputs["Position"], scale=(46, 11, 46), detail=6)
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.7
bump.inputs["Distance"].default_value = 0.01
nt.links.new(st, bump.inputs["Height"])
nt.links.new(bump.outputs[0], bsdf.inputs["Normal"])
normal_path = os.path.join(OUT, "wolf_normal.png")
normal_img = bake(nm, "NORMAL", TEX // 2, normal_path)

# final single material: base color + normal map
final = bpy.data.materials.new("WolfMat")
final.use_nodes = True
nt = final.node_tree
bs = nt.nodes["Principled BSDF"]
bs.inputs["Roughness"].default_value = 0.85
ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = base_img
nt.links.new(ti.outputs["Color"], bs.inputs["Base Color"])
tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = normal_img
nmn = nt.nodes.new("ShaderNodeNormalMap"); nmn.inputs["Strength"].default_value = 0.8
nt.links.new(tn.outputs["Color"], nmn.inputs["Color"])
nt.links.new(nmn.outputs[0], bs.inputs["Normal"])
body.data.materials.clear()
body.data.materials.append(final)

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

bone("root", (0, -0.2, 0.0), (0, 0.0, 0.0))
bone("pelvis", p("pelvis"), p("spine_2"), "root")
bone("spine_1", p("spine_2"), p("chest"), "pelvis", True)
bone("spine_2", p("chest"), p("withers"), "spine_1", True)
bone("neck_1", p("withers"), p("neck_2"), "spine_2", True)
bone("neck_2", p("neck_2"), p("skull"), "neck_1", True)
bone("head", p("skull"), p("muzzle_2"), "neck_2", True)
bone("jaw", (0, 0.80, 0.77), (0, 0.88, 0.76), "head")
for s, side in ((1, "L"), (-1, "R")):
    bone(f"ear_{side}", (s * 0.115, 0.56, 1.0), (s * 0.13, 0.55, 1.13), "head")
tail_pts = [(0, -0.38, 0.60), p("tail_1"), p("tail_2"), p("tail_3"), p("tail_4"), p("tail_tip")]
prev = "pelvis"
for i in range(len(tail_pts) - 1):
    nm_ = f"tail_{i + 1}"
    bone(nm_, tail_pts[i], tail_pts[i + 1], prev)
    prev = nm_
for s, side in ((1, "L"), (-1, "R")):
    pre = side + "_"
    bone(f"{side}_f_upper", P[pre + "f_shoulder"][:3], P[pre + "f_elbow"][:3], "spine_2")
    bone(f"{side}_f_lower", P[pre + "f_elbow"][:3], P[pre + "f_wrist"][:3], f"{side}_f_upper", True)
    bone(f"{side}_f_paw", P[pre + "f_wrist"][:3], P[pre + "f_paw"][:3], f"{side}_f_lower", True)
    bone(f"{side}_h_upper", P[pre + "h_hip"][:3], P[pre + "h_knee"][:3], "pelvis")
    bone(f"{side}_h_lower", P[pre + "h_knee"][:3], P[pre + "h_hock"][:3], f"{side}_h_upper", True)
    bone(f"{side}_h_paw", P[pre + "h_hock"][:3], P[pre + "h_paw"][:3], f"{side}_h_lower", True)
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
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
        "side": ((5.6, 0.1, 0.75), (0, 0.05, 0.55)),
        "front34": ((3.2, 4.0, 1.3), (0, 0.1, 0.52)),
        "back34": ((-2.6, -4.2, 1.5), (0, -0.05, 0.55)),
        "head": ((1.2, 2.5, 1.2), (0, 0.65, 0.85)),
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
    co = cam((5.6, 0.1, 0.75), (0, 0.05, 0.55), "strip", lens=85)
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
print("saved", "TRIANGLES", TRIS)
