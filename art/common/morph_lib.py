"""Shared Blender helpers for Morphics base meshes (Human, Hawk, and Wolf extensions).

Needs the `bpy` Python module. Units are meters. Creatures face +Y, Z is up.
Pose rule: every pose is built with `Poser`, which works in world axes
(X side, Y forward, Z up) so authors do not need to know bone roll.
"""
import math
import os
import json

import bpy
import bmesh
from mathutils import Vector, Matrix, Euler, Quaternion

FPS = 30


# ------------------------------------------------------------------ small math
def smooth(x, a, b):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def lin(c):
    """sRGB tuple to linear tuple (approximate)."""
    return tuple(v ** 2.2 for v in c)


def mix(a, b, t):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def ease(t):
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ scene and objects
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_mod(obj, mod):
    activate(obj)
    bpy.ops.object.modifier_apply(modifier=mod.name)


def skin_mesh(P, E, root, name, levels=2, sub_smooth=0.8):
    """Make a smooth tube mesh from a graph. P: name -> (x, y, z, rx, ry). E: list of (a, b) (a tree)."""
    names = list(P.keys())
    idx = {n: i for i, n in enumerate(names)}
    me = bpy.data.meshes.new(name)
    me.from_pydata([P[n][:3] for n in names], [(idx[a], idx[b]) for a, b in E], [])
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    activate(obj)
    sk = obj.modifiers.new("Skin", "SKIN")
    sk.use_smooth_shade = True
    sk.branch_smoothing = sub_smooth
    for n in names:
        v = me.skin_vertices[0].data[idx[n]]
        v.radius = (P[n][3], P[n][4])
        v.use_root = n == root
    sub = obj.modifiers.new("Sub", "SUBSURF")
    sub.levels = levels
    apply_mod(obj, obj.modifiers["Skin"])
    apply_mod(obj, obj.modifiers["Sub"])
    return obj


def sphere(name, loc, scale, rot=(0, 0, 0), seg=12, rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=1.0, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o


def cone(name, loc, r1, r2, depth, rot=(0, 0, 0), scale=(1, 1, 1), verts=10):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o


def leaf(name, base, direction, length, width, normal=(0, 0, 1), thick=0.006, curve=0.0, segs=4, lift=0.0):
    """A flat tapered blade (feather, tail plume). Thin double layer. Returns an object."""
    d = Vector(direction).normalized()
    n = Vector(normal).normalized()
    side = d.cross(n).normalized()
    bm = bmesh.new()
    top, bot = [], []
    for k in range(segs + 1):
        s = k / segs
        c = Vector(base) + d * length * s + n * (curve * length * s * s + lift)
        w = width * 0.5 * (0.55 + 0.45 * smooth(s, 0.0, 0.3)) * max(0.0, 1 - s ** 2.5) ** 0.6
        for sg in (-1, 1):
            top.append(bm.verts.new(c + side * w * sg + n * thick / 2))
            bot.append(bm.verts.new(c + side * w * sg - n * thick / 2))
    for k in range(segs):
        a = k * 2
        t = [top[a], top[a + 1], top[a + 3], top[a + 2]]
        b = [bot[a], bot[a + 1], bot[a + 3], bot[a + 2]]
        bm.faces.new(t)
        bm.faces.new(b[::-1])
        bm.faces.new([top[a], bot[a], bot[a + 2], top[a + 2]][::-1])
        bm.faces.new([top[a + 1], bot[a + 1], bot[a + 3], top[a + 3]])
    bm.faces.new([top[0], top[1], bot[1], bot[0]][::-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0004)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o


def join(objs, active):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    active.select_set(True)
    bpy.context.view_layer.objects.active = active
    bpy.ops.object.join()
    return active


def clean_and_decimate(obj, target_tris):
    """Merge, smooth, triangulate, then decimate to about target_tris."""
    activate(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.002)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    m = obj.modifiers.new("Smooth", "CORRECTIVE_SMOOTH")
    m.iterations = 6
    m.factor = 0.6
    apply_mod(obj, m)
    t = obj.modifiers.new("Tri", "TRIANGULATE")
    apply_mod(obj, t)
    cur = len(obj.data.polygons)
    if target_tris and cur > target_tris:
        d = obj.modifiers.new("Decimate", "DECIMATE")
        d.ratio = target_tris / cur
        apply_mod(obj, d)
    bpy.ops.object.shade_smooth()


def tri_count(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def paint(obj, fn):
    """Vertex colors from a function (x, y, z) -> (r, g, b) linear."""
    me = obj.data
    if "Col" in me.color_attributes:
        me.color_attributes.remove(me.color_attributes["Col"])
    attr = me.color_attributes.new(name="Col", type="FLOAT_COLOR", domain="POINT")
    for v in me.vertices:
        attr.data[v.index].color = (*fn(*v.co), 1.0)


def surface(obj, x, z, y_from=3.0):
    """Point where a ray along -Y at (x, z) first hits obj. For placing face features."""
    hit, loc, nor, _ = obj.ray_cast(Vector((x, y_from, z)), Vector((0, -1, 0)))
    return tuple(loc) if hit else None


# ------------------------------------------------------------------ armature and weights
def build_armature(name, bones):
    """bones: list of (name, head, tail, parent or None). Parent-first order. Returns the object."""
    arm = bpy.data.armatures.new(name)
    obj = bpy.data.objects.new(name, arm)
    bpy.context.scene.collection.objects.link(obj)
    activate(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones
    for n, head, tail, parent in bones:
        b = eb.new(n)
        b.head = Vector(head)
        b.tail = Vector(tail)
        if parent:
            b.parent = eb[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    return obj


def _seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(1e-9, ab.dot(ab))))
    return (p - (a + ab * t)).length


def bind(mesh_obj, arm_obj, skip=("root",), power=4.0, topk=4):
    """Skin by distance to bone segments (no bone heat, so it never fails on joined parts)."""
    arm = arm_obj.data
    segs = {b.name: (Vector(b.head_local), Vector(b.tail_local)) for b in arm.bones if b.name not in skip}
    vgs = {n: mesh_obj.vertex_groups.new(name=n) for n in segs}
    for v in mesh_obj.data.vertices:
        ws = []
        for n, (a, b) in segs.items():
            d = _seg_dist(v.co, a, b)
            ws.append((1.0 / (d + 0.01) ** power, n))
        ws.sort(reverse=True)
        ws = ws[:topk]
        tot = sum(w for w, _ in ws)
        for w, n in ws:
            vgs[n].add([v.index], w / tot, "REPLACE")
    mesh_obj.parent = arm_obj
    mod = mesh_obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm_obj


class Poser:
    """Author poses in world axes. Call rel/abs/aim for the bones you move, then end(frame).

    rel(bone, x, y, z): rotate in the parent's posed frame, world axes (radians).
    abs(bone, x, y, z): absolute world rotation from the rest pose.
    aim(bone, direction, amount, roll): point the bone along a world direction (blend by amount).
    move(bone, x, y, z): world-space offset from the rest position (for root and pelvis).
    Bones you do not name follow their parent.
    """

    def __init__(self, arm_obj):
        self.arm = arm_obj
        self.pb = arm_obj.pose.bones
        self.names = [b.name for b in self.pb]
        self.R = {b.name: b.bone.matrix_local.to_3x3() for b in self.pb}
        self.par = {b.name: (b.parent.name if b.parent else None) for b in self.pb}
        self.rest_dir = {b.name: (Vector(b.bone.tail_local) - Vector(b.bone.head_local)).normalized() for b in self.pb}
        for b in self.pb:
            b.rotation_mode = "XYZ"
        self.spec, self.moves, self.prev = {}, {}, {}

    def begin(self):
        self.spec, self.moves = {}, {}

    def rel(self, n, x=0.0, y=0.0, z=0.0):
        self.spec[n] = ("rel", Euler((x, y, z), "XYZ").to_matrix())

    def abs(self, n, x=0.0, y=0.0, z=0.0):
        self.spec[n] = ("abs", Euler((x, y, z), "XYZ").to_matrix())

    def relm(self, n, M):
        """Like rel, with a 3x3 matrix (compose several axis turns in the order you want)."""
        self.spec[n] = ("rel", M)

    def aim(self, n, direction, amount=1.0, roll=0.0):
        d = Vector(direction).normalized()
        q = self.rest_dir[n].rotation_difference(d)
        q = Quaternion().slerp(q, amount)
        m = q.to_matrix()
        if roll:
            m = Matrix.Rotation(roll * amount, 3, d) @ m
        self.spec[n] = ("abs", m)

    def move(self, n, x=0.0, y=0.0, z=0.0):
        self.moves[n] = Vector((x, y, z))

    def end(self, frame):
        A = {}
        for n in self.names:
            p = self.par[n]
            Ap = A[p] if p else Matrix.Identity(3)
            kind, M = self.spec.get(n, ("rel", Matrix.Identity(3)))
            A[n] = Ap @ M if kind == "rel" else M
            R = self.R[n]
            basis = R.inverted() @ Ap.inverted() @ A[n] @ R
            e = basis.to_euler("XYZ", self.prev.get(n, Euler((0, 0, 0))))
            self.prev[n] = e
            b = self.pb[n]
            b.rotation_euler = e
            b.keyframe_insert("rotation_euler", frame=frame)
            if n in self.moves or n in ("root",):
                w = self.moves.get(n, Vector((0, 0, 0)))
                b.location = R.inverted() @ w
                b.keyframe_insert("location", frame=frame)


ANIMS = {}


def rx(a):
    return Matrix.Rotation(a, 3, "X")


def ry(a):
    return Matrix.Rotation(a, 3, "Y")


def rz(a):
    return Matrix.Rotation(a, 3, "Z")


def curve(t, knots):
    """Smooth path through (time, value) knots. Holds the end values."""
    if t <= knots[0][0]:
        return knots[0][1]
    for (t0, v0), (t1, v1) in zip(knots, knots[1:]):
        if t <= t1:
            u = ease((t - t0) / (t1 - t0))
            return v0 + (v1 - v0) * u
    return knots[-1][1]


def make_action(poser, name, length, fn, loop=True):
    """fn(t, P): t runs 0..1 over the clip; call P.rel/abs/aim/move. Keys every frame. Returns the action."""
    arm = poser.arm
    act = bpy.data.actions.new(name)
    arm.animation_data_create()
    arm.animation_data.action = act
    for b in poser.pb:
        b.rotation_euler = (0, 0, 0)
        b.location = (0, 0, 0)
    poser.prev = {}
    for f in range(0, length + 1):
        t = f / length
        poser.begin()
        fn(t, poser)
        poser.end(1 + f)
    act.use_fake_user = True
    ANIMS[name] = {"frames": length + 1, "fps": FPS, "loop": loop}
    return act


# ------------------------------------------------------------------ paint material and bake
def _maprange(nt, value_out, lo, hi):
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.clamp = True
    mr.inputs["From Min"].default_value = lo
    mr.inputs["From Max"].default_value = hi
    nt.links.new(value_out, mr.inputs["Value"])
    return mr.outputs[0]


def _dist(nt, xyz_out, center):
    sub = nt.nodes.new("ShaderNodeVectorMath")
    sub.operation = "SUBTRACT"
    nt.links.new(xyz_out, sub.inputs[0])
    sub.inputs[1].default_value = center
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    nt.links.new(sub.outputs[0], ln.inputs[0])
    return ln.outputs["Value"]


def _stroke(nt, pos_out, scale, detail=5):
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale
    nt.links.new(pos_out, mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Detail"].default_value = detail
    nz.inputs["Roughness"].default_value = 0.6
    nt.links.new(mp.outputs[0], nz.inputs["Vector"])
    return nz.outputs["Fac"]


def paint_material(name, features, stroke_scale=(30, 30, 30), stroke_range=(1.0, 1.0), zones=()):
    """Emission material: vertex color x brush-stroke shading, plus face features.
    features: list of (center, r_out, r_in, color_linear, mirror_x).
    zones: list of (color_linear, terms). A term is (axis, a, b), axis in x, y, z, ax (=|x|). It ramps 0 at a to 1 at b
    (a > b gives a descending ramp). Terms multiply. Zones are evaluated per texel, so edges stay sharp."""
    m = bpy.data.materials.new(name)
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
    k = _maprange(nt, _stroke(nt, geo.outputs["Position"], stroke_scale), 0.3, 0.7)
    shade = nt.nodes.new("ShaderNodeMapRange")
    nt.links.new(k, shade.inputs["Value"])
    shade.inputs["To Min"].default_value = stroke_range[0]
    shade.inputs["To Max"].default_value = stroke_range[1]
    gray = nt.nodes.new("ShaderNodeCombineColor")
    for i in range(3):
        nt.links.new(shade.outputs[0], gray.inputs[i])
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.blend_type = "MULTIPLY"
    mx.inputs["Factor"].default_value = 1.0
    nt.links.new(col.outputs["Color"], mx.inputs["A"])
    nt.links.new(gray.outputs[0], mx.inputs["B"])
    cur = mx.outputs[2]
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    ab = nt.nodes.new("ShaderNodeMath")
    ab.operation = "ABSOLUTE"
    nt.links.new(sep.outputs["X"], ab.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(ab.outputs[0], comb.inputs["X"])
    nt.links.new(sep.outputs["Y"], comb.inputs["Y"])
    nt.links.new(sep.outputs["Z"], comb.inputs["Z"])
    axes = {"x": sep.outputs["X"], "y": sep.outputs["Y"], "z": sep.outputs["Z"], "ax": ab.outputs[0]}
    for color, terms in zones:
        mask = None
        for axis, a, b in terms:
            t = _maprange(nt, axes[axis], a, b)
            if mask is None:
                mask = t
            else:
                mm = nt.nodes.new("ShaderNodeMath")
                mm.operation = "MULTIPLY"
                nt.links.new(mask, mm.inputs[0])
                nt.links.new(t, mm.inputs[1])
                mask = mm.outputs[0]
        zmix = nt.nodes.new("ShaderNodeMix")
        zmix.data_type = "RGBA"
        nt.links.new(mask, zmix.inputs["Factor"])
        nt.links.new(cur, zmix.inputs["A"])
        zmix.inputs["B"].default_value = (*color, 1)
        cur = zmix.outputs[2]
    for center, r_out, r_in, color, mirror in features:
        src = comb.outputs[0] if mirror else geo.outputs["Position"]
        c = (abs(center[0]) if mirror else center[0], center[1], center[2])
        d = _dist(nt, src, c)
        f = _maprange(nt, d, r_out, r_in)
        mix_n = nt.nodes.new("ShaderNodeMix")
        mix_n.data_type = "RGBA"
        nt.links.new(f, mix_n.inputs["Factor"])
        nt.links.new(cur, mix_n.inputs["A"])
        mix_n.inputs["B"].default_value = (*color, 1)
        cur = mix_n.outputs[2]
    nt.links.new(cur, em.inputs["Color"])
    return m


def bake_and_finish(obj, paint_mat, out_dir, prefix, size=2048, normal_scale=(46, 11, 46), rough=0.9, strength=0.7, normal=False):
    """UV unwrap, bake base color and normal map, set one final material. Returns file paths."""
    scene = bpy.context.scene
    activate(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.006)
    bpy.ops.object.mode_set(mode="OBJECT")

    def bake(mat, kind, sz, path):
        img = bpy.data.images.new(os.path.basename(path), sz, sz, alpha=False)
        img.colorspace_settings.name = "sRGB" if kind == "DIFFUSE" else "Non-Color"
        tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = img
        mat.node_tree.nodes.active = tex
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        scene.render.engine = "CYCLES"
        scene.cycles.device = "CPU"
        scene.cycles.samples = 4
        scene.render.bake.margin = 8
        scene.render.bake.use_selected_to_active = False
        activate(obj)
        if kind == "DIFFUSE":
            scene.cycles.bake_type = "EMIT"
            bpy.ops.object.bake(type="EMIT")
        else:
            bpy.ops.object.bake(type="NORMAL")
        img.filepath_raw = path
        img.file_format = "PNG"
        img.save()
        return img

    base_path = os.path.join(out_dir, f"{prefix}_basecolor.png")
    norm_path = os.path.join(out_dir, f"{prefix}_normal.png")
    base_img = bake(paint_mat, "DIFFUSE", size, base_path)
    norm_path = None
    if not normal:
        _finish(obj, prefix, base_img, None, rough)
        _cleanup_col(obj)
        return base_path, None
    nm = bpy.data.materials.new("NormalBake")
    nm.use_nodes = True
    nt = nm.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    st = _stroke(nt, geo.outputs["Position"], normal_scale, 6)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = 0.01
    nt.links.new(st, bump.inputs["Height"])
    nt.links.new(bump.outputs[0], bsdf.inputs["Normal"])
    norm_img = bake(nm, "NORMAL", size // 2, norm_path)

    _finish(obj, prefix, base_img, norm_img, rough)
    _cleanup_col(obj)
    return base_path, norm_path


def _cleanup_col(obj):
    if "Col" in obj.data.color_attributes:
        obj.data.color_attributes.remove(obj.data.color_attributes["Col"])


def _finish(obj, prefix, base_img, norm_img, rough):
    final = bpy.data.materials.new(prefix.capitalize() + "Mat")
    final.use_nodes = True
    nt = final.node_tree
    bs = nt.nodes["Principled BSDF"]
    bs.inputs["Roughness"].default_value = rough
    ti = nt.nodes.new("ShaderNodeTexImage")
    ti.image = base_img
    nt.links.new(ti.outputs["Color"], bs.inputs["Base Color"])
    if norm_img is not None:
        tn = nt.nodes.new("ShaderNodeTexImage")
        tn.image = norm_img
        nmn = nt.nodes.new("ShaderNodeNormalMap")
        nmn.inputs["Strength"].default_value = 0.8
        nt.links.new(tn.outputs["Color"], nmn.inputs["Color"])
        nt.links.new(nmn.outputs[0], bs.inputs["Normal"])
    final.use_backface_culling = False
    obj.data.materials.clear()
    obj.data.materials.append(final)
    return final


# ------------------------------------------------------------------ stage, previews, export
def build_stage():
    scene = bpy.context.scene
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    g = bpy.context.active_object
    gm = bpy.data.materials.new("Ground")
    gm.use_nodes = True
    gb = gm.node_tree.nodes["Principled BSDF"]
    gb.inputs["Base Color"].default_value = (0.45, 0.85, 0.22, 1)
    gb.inputs["Roughness"].default_value = 1
    g.data.materials.append(gm)
    sun = bpy.data.lights.new("Sun", "SUN")
    sun.energy = 3.4
    sun.color = (1.0, 0.95, 0.85)
    sun.angle = math.radians(3)
    so = bpy.data.objects.new("Sun", sun)
    scene.collection.objects.link(so)
    so.rotation_euler = (math.radians(55), math.radians(10), math.radians(-35))
    fill = bpy.data.lights.new("Fill", "AREA")
    fill.energy = 40
    fill.color = (0.55, 0.65, 1.0)
    fill.size = 6
    fo = bpy.data.objects.new("Fill", fill)
    scene.collection.objects.link(fo)
    fo.location = (-4, 4, 3)
    fo.rotation_euler = (math.radians(60), 0, math.radians(-140))
    w = bpy.data.worlds.new("W")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.30, 0.55, 0.90, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    scene.view_settings.view_transform = "Standard"
    scene.world = w
    return g


def camera(loc, target, name, lens=70):
    c = bpy.data.cameras.new(name)
    c.lens = lens
    co = bpy.data.objects.new(name, c)
    bpy.context.scene.collection.objects.link(co)
    co.location = loc
    co.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return co


def render_still(path, cam, size=(960, 600), samples=24):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = False
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.camera = cam
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def contact_sheet(arm_obj, actions, cam, out_path, tiles=5, size=(300, 260), samples=10, exclude=()):
    """One row per action, `tiles` frames each, rendered through `cam`. Needs build_stage() first."""
    from PIL import Image, ImageDraw
    import tempfile
    scene = bpy.context.scene
    rows = [a for a in actions if a not in exclude]
    sheet = Image.new("RGB", (size[0] * tiles, size[1] * len(rows)), (30, 30, 30))
    tmp = tempfile.mkdtemp()
    for r, name in enumerate(rows):
        arm_obj.animation_data.action = bpy.data.actions[name]
        n = ANIMS.get(name, {"frames": 30})["frames"]
        for c in range(tiles):
            fr = 1 + round((n - 1) * c / (tiles - 1))
            scene.frame_set(fr)
            p = os.path.join(tmp, f"{name}_{c}.png")
            render_still(p, cam, size, samples)
            im = Image.open(p).convert("RGB")
            sheet.paste(im, (c * size[0], r * size[1]))
        ImageDraw.Draw(sheet).text((6, r * size[1] + 4), name, fill=(255, 255, 255))
    sheet.save(out_path)


def export_fbx(path, objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"ARMATURE", "MESH"},
                             add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=True,
                             bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True,
                             axis_forward="Y", axis_up="Z", apply_scale_options="FBX_SCALE_ALL",
                             mesh_smooth_type="FACE", use_armature_deform_only=True, global_scale=100.0)


def write_report(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
