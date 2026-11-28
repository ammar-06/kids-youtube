"""Rig an image-to-3D character (OBJ in a zip from glb2js.py) with a Mixamo-named skeleton, headless.

    blender -b -P cartoon3d/tools/autorig.py -- in.zip joints.json out.glb

joints.json: positions in OBJ space (x right = character's left, y up, z toward camera), 1 unit tall:
  {"hips":[x,y,z], "chest":..., "neck":..., "head":..., "headtop":..., "shoulder":..., "elbow":..., "wrist":...,
   "handtip":..., "hip":..., "knee":..., "ankle":..., "toe":...}   (limb joints given for the +x side, mirrored)
"""
import bpy, sys, json, os, zipfile, tempfile
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
src, jf, out = a[0], a[1], a[2]
J = json.load(open(jf))
tmp = tempfile.mkdtemp()
zipfile.ZipFile(src).extractall(tmp)
obj_path = [os.path.join(tmp, f) for f in os.listdir(tmp) if f.endswith(".obj")][0]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=obj_path)
body = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
# weld the UV-seam duplicates so skin weights don't tear along seams
bpy.context.view_layer.objects.active = body
body.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.0002)
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.shade_smooth()
SC = 10.0  # bone heat fails on tiny meshes, so work at 10 units tall
body.scale = (SC, SC, SC)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def P(p, mirror=False):  # OBJ (x,y,z) -> Blender (x,-z,y)
    x, y, z = p
    return Vector((-x if mirror else x, -z, y)) * SC


arm_data = bpy.data.armatures.new("Armature")
rig = bpy.data.objects.new("Armature", arm_data)
bpy.context.scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="EDIT")
E = arm_data.edit_bones


def bone(name, h, t, parent=None, connect=False):
    b = E.new(name)
    b.head, b.tail = h, t
    if parent:
        b.parent = E[parent]
        b.use_connect = connect
    return b


hips = P(J["hips"]); chest = P(J["chest"]); neck = P(J["neck"]); head = P(J["head"]); top = P(J["headtop"])
sp1 = hips.lerp(chest, 0.34); sp2 = hips.lerp(chest, 0.67)
bone("mixamorig:Hips", hips, sp1)
bone("mixamorig:Spine", sp1, sp2, "mixamorig:Hips", True)
bone("mixamorig:Spine1", sp2, chest, "mixamorig:Spine", True)
bone("mixamorig:Spine2", chest, neck, "mixamorig:Spine1", True)
bone("mixamorig:Neck", neck, head, "mixamorig:Spine2", True)
bone("mixamorig:Head", head, top, "mixamorig:Neck", True)
for side, m in (("Left", False), ("Right", True)):
    sh = P(J["shoulder"], m); el = P(J["elbow"], m); wr = P(J["wrist"], m); ht = P(J["handtip"], m)
    clav = chest.lerp(sh, 0.35) + Vector((0, 0, 0.0))
    bone(f"mixamorig:{side}Shoulder", clav, sh, "mixamorig:Spine2")
    bone(f"mixamorig:{side}Arm", sh, el, f"mixamorig:{side}Shoulder", True)
    bone(f"mixamorig:{side}ForeArm", el, wr, f"mixamorig:{side}Arm", True)
    bone(f"mixamorig:{side}Hand", wr, ht, f"mixamorig:{side}ForeArm", True)
    hp = P(J["hip"], m); kn = P(J["knee"], m); an = P(J["ankle"], m); to = P(J["toe"], m)
    bone(f"mixamorig:{side}UpLeg", hp, kn, "mixamorig:Hips")
    bone(f"mixamorig:{side}Leg", kn, an, f"mixamorig:{side}UpLeg", True)
    bone(f"mixamorig:{side}Foot", an, to, f"mixamorig:{side}Leg", True)
# bones roll: keep Blender defaults (z-up); fine for procedural local rotations
bpy.ops.object.mode_set(mode="OBJECT")

# Region-based skin weights (bone heat bleeds arm weights into the chin and shirt on these meshes):
# head above the neck, arms only outside the torso, legs only below the shorts, spine blended by height.
import numpy as np
mesh = body.data
Vb = np.array([v.co[:] for v in mesh.vertices]) / SC
X, Y, Z = Vb[:, 0], Vb[:, 2], -Vb[:, 1]          # back to OBJ space (x left, y up, z front)
Jv = {k: np.array(v, float) for k, v in J.items()}


def sstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def segd(p, a, b):
    ab = b - a
    t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1)
    return np.linalg.norm(p - (a + t[:, None] * ab), axis=1)


def chain(p, segs):
    d = np.stack([segd(p, a, b) for a, b in segs], 1)
    w = 1.0 / (d ** 4 + 1e-9)
    # keep the two nearest bones only
    idx = np.argsort(-w, 1)
    m = np.zeros_like(w)
    for k in range(2):
        m[np.arange(len(w)), idx[:, k]] = 1
    w = w * m
    return w / w.sum(1, keepdims=True)


n = len(Vb)
W = {}
def add(name, w):
    W[name] = W.get(name, 0) + w

hy, cy, ny, hdy = Jv["hips"][1], Jv["chest"][1], Jv["neck"][1], Jv["head"][1]
torso_hw = float(os.environ.get("TORSO_HW", "0.095"))
P3 = np.stack([X, Y, Z], 1)
ax = np.abs(X)
# arms: outside the torso and between hand tip and shoulder top
arm_f = sstep(torso_hw - 0.006, torso_hw + 0.022, ax) * (1 - sstep(Jv["shoulder"][1] + 0.02, Jv["shoulder"][1] + 0.06, Y)) * sstep(Jv["handtip"][1] - 0.05, Jv["handtip"][1] - 0.02, Y)
# legs: below the crotch
leg_f = (1 - sstep(Jv["hip"][1] - 0.035, Jv["hip"][1] + 0.01, Y)) * (1 - arm_f)
core = 1 - arm_f - leg_f
# spine by height
head_f = sstep(ny - 0.02, ny + 0.012, Y)
neck_f = sstep(cy + 0.04, ny - 0.01, Y) * (1 - head_f)
rest = 1 - head_f - neck_f
sp = [hy, hy + (cy - hy) * 0.34, hy + (cy - hy) * 0.67, cy]
names = ["Hips", "Spine", "Spine1", "Spine2"]
wsp = np.zeros((n, 4))
yy = np.clip(Y, sp[0], sp[3])
for i in range(4):
    lo = sp[i - 1] if i > 0 else sp[0] - 1
    hi = sp[i + 1] if i < 3 else sp[3] + 1
    wsp[:, i] = np.where(yy <= sp[i], sstep(lo, sp[i], yy) if i > 0 else 1, 1 - sstep(sp[i], hi, yy) if i < 3 else 1)
wsp /= wsp.sum(1, keepdims=True)
for i, nm in enumerate(names):
    add(nm, core * rest * wsp[:, i])
add("Neck", core * neck_f)
add("Head", core * head_f)
for side, sg in (("Left", 1), ("Right", -1)):
    on = (X * sg > 0).astype(float)
    mir = np.array([sg, 1, 1])
    sh, el, wr, tip = (Jv[k] * mir for k in ("shoulder", "elbow", "wrist", "handtip"))
    clav = Jv["chest"] + (sh - Jv["chest"]) * 0.35
    wa = chain(P3, [(clav, sh), (sh, el), (el, wr), (wr, tip)])
    for i, nm in enumerate(["Shoulder", "Arm", "ForeArm", "Hand"]):
        add(side + nm, arm_f * on * wa[:, i])
    hp, kn, an, to = (Jv[k] * mir for k in ("hip", "knee", "ankle", "toe"))
    wl = chain(P3, [(hp, kn), (kn, an), (an, to)])
    for i, nm in enumerate(["UpLeg", "Leg", "Foot"]):
        add(side + nm, leg_f * on * wl[:, i])
tot = sum(W.values())
for nm, w in W.items():
    g = body.vertex_groups.new(name="mixamorig:" + nm)
    w = w / np.maximum(tot, 1e-9)
    for i in np.nonzero(w > 0.002)[0]:
        g.add([int(i)], float(w[i]), "REPLACE")
am = body.modifiers.new("Armature", "ARMATURE"); am.object = rig
body.parent = rig
groups = {g.index: g.name for g in body.vertex_groups}
unweighted = sum(1 for v in body.data.vertices if not any(g.weight > 0.01 for g in v.groups))
print("RIG: vertices", len(body.data.vertices), "unweighted", unweighted, "groups", len(groups))

bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_skins=True, export_animations=False,
                          export_yup=True, export_apply=False, export_materials="NONE")
print("RIG: wrote", out)
