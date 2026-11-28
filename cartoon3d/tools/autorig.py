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

# Bone heat fails on raw image-to-3D meshes (many loose, overlapping pieces), so skin a clean
# voxel-remeshed proxy and copy its weights onto the real mesh.
proxy = body.copy(); proxy.data = body.data.copy(); proxy.name = "proxy"
bpy.context.scene.collection.objects.link(proxy)
rm = proxy.modifiers.new("remesh", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = float(os.environ.get("VOXEL", "0.01")) * SC
bpy.ops.object.select_all(action="DESELECT")
proxy.select_set(True); bpy.context.view_layer.objects.active = proxy
bpy.ops.object.modifier_apply(modifier="remesh")
print("RIG: proxy verts", len(proxy.data.vertices))
bpy.ops.object.select_all(action="DESELECT")
proxy.select_set(True); rig.select_set(True); bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type="ARMATURE_AUTO")
pw = sum(1 for v in proxy.data.vertices if any(g.weight > 0.01 for g in v.groups))
print("RIG: proxy weighted", pw, "of", len(proxy.data.vertices))
for g in proxy.vertex_groups:
    body.vertex_groups.new(name=g.name)
dt = body.modifiers.new("dt", "DATA_TRANSFER")
dt.object = proxy; dt.use_vert_data = True; dt.data_types_verts = {"VGROUP_WEIGHTS"}
dt.vert_mapping = "POLYINTERP_NEAREST"; dt.layers_vgroup_select_src = "ALL"; dt.layers_vgroup_select_dst = "NAME"
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True); bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier="dt")
bpy.ops.object.vertex_group_normalize_all(lock_active=False)
am = body.modifiers.new("Armature", "ARMATURE"); am.object = rig
body.parent = rig
bpy.data.objects.remove(proxy, do_unlink=True)
groups = {g.index: g.name for g in body.vertex_groups}
unweighted = sum(1 for v in body.data.vertices if not any(g.weight > 0.01 for g in v.groups))
print("RIG: vertices", len(body.data.vertices), "unweighted", unweighted, "groups", len(groups))

bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_skins=True, export_animations=False,
                          export_yup=True, export_apply=False, export_materials="NONE")
print("RIG: wrote", out)
