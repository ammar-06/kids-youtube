"""Turn a GLB (one textured mesh) into a JS file + PNG texture that Three.js can build synchronously.

    python cartoon3d/tools/glb2js.py in.glb out_dir name
writes out_dir/<name>.js (window.MESHES[name] = {pos, nrm, uv, idx} as base64) and out_dir/<name>.png
"""
import base64, io, json, os, struct, sys
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from PIL import Image

src, out, name = sys.argv[1:4]
b = open(src, "rb").read()
n = struct.unpack("<I", b[12:16])[0]
j = json.loads(b[20:20 + n])
binstart = 20 + n + 8
blob = b[binstart:]


def view(i):
    bv = j["bufferViews"][i]
    o = bv.get("byteOffset", 0)
    return blob[o:o + bv["byteLength"]]


def acc(i):
    a = j["accessors"][i]
    bv = j["bufferViews"][a["bufferView"]]
    comps = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[a["type"]]
    size = {5126: 4, 5125: 4, 5123: 2, 5121: 1}[a["componentType"]]
    o = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", comps * size)
    if stride == comps * size:
        return blob[o:o + a["count"] * stride], a["componentType"]
    return b"".join(blob[o + k * stride:o + k * stride + comps * size] for k in range(a["count"])), a["componentType"]


prim = j["meshes"][0]["primitives"][0]
at = prim["attributes"]
d = {}
for key, attr in (("pos", "POSITION"), ("nrm", "NORMAL"), ("uv", "TEXCOORD_0")):
    if attr in at:
        d[key] = base64.b64encode(acc(at[attr])[0]).decode()
raw, ct = acc(prim["indices"])
I = np.frombuffer(raw, np.uint32 if ct == 5125 else np.uint16).reshape(-1, 3).astype(np.uint32)
P = np.frombuffer(acc(at["POSITION"])[0], np.float32).reshape(-1, 3)
# drop the floor / backdrop plates that image-to-3D builds from the photo background:
# weld vertices by position, find connected pieces, drop any piece much wider than the character
_, w = np.unique(np.round(P * 20000).astype(np.int64), axis=0, return_inverse=True)
w = w.ravel()
J = w[I]
nv = int(w.max()) + 1
e = np.concatenate([J[:, [0, 1]], J[:, [1, 2]]])
_, lab = connected_components(coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(nv, nv)), directed=False)
def pieces(mask):
    e = np.concatenate([J[mask][:, [0, 1]], J[mask][:, [1, 2]]])
    _, lab = connected_components(coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(nv, nv)), directed=False)
    fl = np.full(len(I), -1)
    fl[mask] = lab[J[mask][:, 0]]
    return fl


ally = P[I][:, :, 1]
floor = P[:, 1].min()
# 1) peel off the thin floor slab (every corner within 1.5% of the lowest point), wherever it is
mask = ~(ally.max(1) < floor + 0.015 * (P[:, 1].max() - floor))
fl = pieces(mask)
big = np.bincount(fl[mask]).argmax()
qb = P[I[fl == big].ravel()]
span = (qb.max(0) - qb.min(0))[[0, 2]].max()
# 2) drop any remaining piece much wider than the character (backdrop walls)
keep = np.zeros(len(I), bool)
for c in np.unique(fl[mask]):
    q = P[I[fl == c].ravel()]
    keep[fl == c] = (q.max(0) - q.min(0))[[0, 2]].max() < span * 1.15
# 3) put the shoe soles back: floor faces right under the character's footprint
lo, hi = qb.min(0), qb.max(0)
cx = P[I][:, :, [0, 2]].mean(1)
sole = (~mask) & (cx[:, 0] > lo[0]) & (cx[:, 0] < hi[0]) & (cx[:, 1] > lo[2]) & (cx[:, 1] < hi[2])
print("sole faces", int(sole.sum()))
print("faces kept", int(keep.sum()), "of", len(I))
d["idx"] = base64.b64encode(I[keep].astype(np.uint32).tobytes()).decode()
d["idx32"] = True
mat = j["materials"][prim.get("material", 0)]
tex = j["textures"][mat["pbrMetallicRoughness"]["baseColorTexture"]["index"]]
src_img = tex.get("source", tex.get("extensions", {}).get("EXT_texture_webp", {}).get("source"))
img = Image.open(io.BytesIO(view(j["images"][src_img]["bufferView"]))).convert("RGB")
# image-to-3D textures come out dark and over-saturated; a gamma lift brings them back to the source picture
GAMMA = float(os.environ.get("TEX_GAMMA", "1.6"))
SAT = float(os.environ.get("TEX_SAT", "0.8"))
a = np.asarray(img, np.float32) / 255.0
a = np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055) if GAMMA == 2.2 else np.power(a, 1 / GAMMA)
g = (a * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
a = g + (a - g) * SAT
img = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))
img.save(os.path.join(out, name + ".png"))
# node transform (TRELLIS puts a rotation on the node)
node = next(nd for nd in j["nodes"] if "mesh" in nd)
d["matrix"] = node.get("matrix")
d["rotation"] = node.get("rotation")
d["scale"] = node.get("scale")
d["translation"] = node.get("translation")
open(os.path.join(out, name + ".js"), "w").write(f"window.MESHES=window.MESHES||{{}};window.MESHES[{json.dumps(name)}]={json.dumps(d)};")
print("ok", img.size, {k: len(v) for k, v in d.items() if isinstance(v, str)}, d["rotation"], d["matrix"] is not None)

# ---- optional: OBJ + MTL + PNG zip for Mixamo upload (4th arg = zip path)
if len(sys.argv) > 4:
    import zipfile
    keepI = I[keep]
    used = np.unique(keepI)
    remap = np.full(len(P), -1, np.int64)
    remap[used] = np.arange(len(used))
    UV = np.frombuffer(acc(at["TEXCOORD_0"])[0], np.float32).reshape(-1, 2)
    Pk = P[used] - [0, P[used][:, 1].min(), 0]  # feet on the ground
    Pk = Pk * (1.0 / Pk[:, 1].max())  # 1 unit tall
    lines = [f"mtllib {name}.mtl", f"o {name}"]
    lines += [f"v {x:.5f} {y:.5f} {z:.5f}" for x, y, z in Pk]
    lines += [f"vt {u:.5f} {1 - v:.5f}" for u, v in UV[used]]
    lines += ["usemtl skin"]
    F = remap[keepI] + 1
    lines += [f"f {a}/{a} {b}/{b} {c}/{c}" for a, b, c in F]
    mtl = f"newmtl skin\nKd 1 1 1\nKa 0 0 0\nKs 0 0 0\nillum 1\nmap_Kd {name}.png\n"
    with zipfile.ZipFile(sys.argv[4], "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(name + ".obj", "\n".join(lines) + "\n")
        z.writestr(name + ".mtl", mtl)
        z.write(os.path.join(out, name + ".png"), name + ".png")
    print("mixamo zip", sys.argv[4], len(used), "verts", len(F), "faces")
