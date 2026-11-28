"""Make an image-to-3D character look more like its source picture (CoComelon-style clean surfaces).

    python cartoon3d/tools/retouch.py in.zip ref.jpg out.zip retouch.json

- colour transfer: each colour group of the texture (skin, shirt, hair...) is moved to the matching
  colour of the reference picture (pairs listed in retouch.json "colors": [[from_rgb, to_rgb], ...])
- hair: the fuzzy fur surface is smoothed (Taubin) and painted one clean colour; a roughness map
  makes it a little glossy
retouch.json: {"colors": [...], "hair": {"rgb": [r,g,b], "max_v": 70, "min_y": 0.5,
               "face_box": {"y_max": 0.86, "z_min": 0.08, "x_abs_max": 0.11}, "iters": 25}}
"""
import io, json, sys, zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

src, ref_path, out, cfg_path = sys.argv[1:5]
cfg = json.load(open(cfg_path))
z = zipfile.ZipFile(src)
name = [n for n in z.namelist() if n.endswith(".obj")][0][:-4]
lines = z.read(name + ".obj").decode().splitlines()
V = np.array([l.split()[1:4] for l in lines if l.startswith("v ")], float)
VT = np.array([l.split()[1:3] for l in lines if l.startswith("vt ")], float)
F = np.array([[int(p.split("/")[0]) - 1 for p in l.split()[1:4]] for l in lines if l.startswith("f ")])
img = Image.open(io.BytesIO(z.read(name + ".png"))).convert("RGB")
W, H = img.size
T = np.asarray(img, np.float32)

# ---------------- colour transfer (soft, per colour group)
pairs = np.array(cfg["colors"], np.float32)
src_c, dst_c = pairs[:, 0], pairs[:, 1]
flat = T.reshape(-1, 3)
d2 = ((flat[:, None, :] - src_c[None]) ** 2).sum(2)
sig = float(cfg.get("sigma", 28.0))
w = np.exp(-d2 / (2 * sig * sig))
near = w.sum(1, keepdims=True)
shift = (w @ (dst_c - src_c)) / np.maximum(near, 1e-6)
amt = np.clip(near / (near + 0.05), 0, 1)  # far-from-any-group pixels barely move
T2 = np.clip(flat + shift * amt, 0, 255).reshape(T.shape)

# ---------------- hair: pick vertices, smooth them, paint their triangles
hc = cfg["hair"]
cu = VT[F].mean(1)
px = np.clip((cu[:, 0] * (W - 1)).astype(int), 0, W - 1)
py = np.clip(((1 - cu[:, 1]) * (H - 1)).astype(int), 0, H - 1)
fdark = (T[py, px].max(1) < hc.get("max_v", 70)).astype(float)
cnt = np.zeros(len(V)); dk = np.zeros(len(V))
for k in range(3):
    np.add.at(cnt, F[:, k], 1); np.add.at(dk, F[:, k], fdark)
dark = dk / np.maximum(cnt, 1) > 0.5
fb = hc["face_box"]
face = (V[:, 1] < fb["y_max"]) & (V[:, 2] > fb["z_min"]) & (np.abs(V[:, 0]) < fb["x_abs_max"])
hair = dark & (V[:, 1] > hc.get("min_y", 0.5)) & ~face
# grow/clean the selection through welded neighbours: a vertex is hair if most neighbours are
key = np.round(V * 20000).astype(np.int64)
_, weld = np.unique(key, axis=0, return_inverse=True)
weld = weld.ravel()
nw = weld.max() + 1
WF = weld[F]
e = np.concatenate([WF[:, [0, 1]], WF[:, [1, 2]], WF[:, [2, 0]]])
e = np.concatenate([e, e[:, ::-1]])
from scipy.sparse import coo_matrix
A = coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(nw, nw)).tocsr()
A.data[:] = 1
deg = np.asarray(A.sum(1)).ravel()
hw = np.zeros(nw)
np.maximum.at(hw, weld, hair.astype(float))
for _ in range(3):
    frac = (A @ hw) / np.maximum(deg, 1)
    hw = ((hw > 0.5) & (frac > 0.25)) | (frac > 0.6)
    hw = hw.astype(float)
hair = hw[weld] > 0.5
# Taubin smoothing of the hair surface (welded), boundary with non-hair stays put
P = np.zeros((nw, 3))
P[weld] = V
ts = hc.get("tuft_scale")
if ts:
    ty = hc.get("tuft_y", 0.9)
    up = (P[:, 1] > ty) & (hw > 0.5)
    P[up, 1] = ty + (P[up, 1] - ty) * ts
    ctr = np.array(hc.get("tuft_center", [0.0, 0.0]))  # pull the tuft points in toward the head (x, z)
    P[up][:, [0, 2]]
    k = np.clip((P[up, 1] - ty) / 0.05, 0, 1)[:, None] * (1 - ts) * 0.5
    P[np.nonzero(up)[0][:, None], [0, 2]] = P[up][:, [0, 2]] * (1 - k) + ctr * k
move = hw > 0.5
top = float(hc.get("tuft_y", 0.92))
keepk = np.ones(nw)
keepk[weld] = 1 - float(hc.get("tuft_keep", 0.85)) * np.clip((V[:, 1] - (top - 0.04)) / 0.04, 0, 1)
lam, mu = 0.6, -0.63
for _ in range(int(hc.get("iters", 25))):
    for f in (lam, mu):
        avg = (A @ P) / np.maximum(deg, 1)[:, None]
        P[move] += (f * keepk[move])[:, None] * (avg[move] - P[move])
V2 = P[weld]
print("hair vertices", int(hair.sum()), "of", len(V))

# paint the hair triangles in texture space
mask = Image.new("L", (W, H), 0)
dr = ImageDraw.Draw(mask)
hf = hair[F].sum(1) >= 2
for tri in F[hf]:
    dr.polygon([(VT[i, 0] * (W - 1), (1 - VT[i, 1]) * (H - 1)) for i in tri], fill=255)
cover = Image.new("L", (W, H), 0)
dc = ImageDraw.Draw(cover)
for tri in F[~hf]:
    dc.polygon([(VT[i, 0] * (W - 1), (1 - VT[i, 1]) * (H - 1)) for i in tri], fill=255)
other = np.asarray(cover.filter(ImageFilter.MaxFilter(3)), np.float32) / 255.0
grown = np.asarray(mask.filter(ImageFilter.MaxFilter(5)), np.float32) / 255.0
core = np.asarray(mask, np.float32) / 255.0
m = np.maximum(core, grown * (1 - other))[..., None]
hair_rgb = np.array(hc["rgb"], np.float32)
T3 = T2 * (1 - m) + hair_rgb * m
# ---------------- projection paint: draw clean shapes onto the model as seen from the front
def raster_positions(sel):
    """texel -> 3D position / face normal for the selected triangles"""
    pos = np.zeros((H, W, 3), np.float32); nz = np.full((H, W), -1.0, np.float32); hit = np.zeros((H, W), bool)
    for f in np.nonzero(sel)[0]:
        tri = F[f]
        uv = np.stack([VT[tri, 0] * (W - 1), (1 - VT[tri, 1]) * (H - 1)], 1)
        x0, y0 = np.floor(uv.min(0)).astype(int); x1, y1 = np.ceil(uv.max(0)).astype(int)
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, W - 1), min(y1, H - 1)
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (ax, ay), (bx, by), (cx, cy) = uv
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9:
            continue
        l1 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
        l2 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
        l3 = 1 - l1 - l2
        ins = (l1 >= -0.02) & (l2 >= -0.02) & (l3 >= -0.02)
        if not ins.any():
            continue
        p = l1[..., None] * V2[tri[0]] + l2[..., None] * V2[tri[1]] + l3[..., None] * V2[tri[2]]
        nrm = np.cross(V2[tri[1]] - V2[tri[0]], V2[tri[2]] - V2[tri[0]]); nrm /= np.linalg.norm(nrm) + 1e-12
        sub = (slice(y0, y1 + 1), slice(x0, x1 + 1))
        pos[sub][ins] = p[ins]; nz[sub][ins] = nrm[2]; hit[sub][ins] = True
    return pos, nz, hit


def soft(d, edge):  # inside (d<0) -> 1, with an anti-aliased edge
    return np.clip(0.5 - d / edge, 0, 1)


def blend(img, a, rgb):
    a = a[..., None]
    return img * (1 - a) + np.array(rgb, np.float32) * a


paint = cfg.get("paint", [])
if paint:
    cen = V2[F].mean(1)
    fn = np.cross(V2[F[:, 1]] - V2[F[:, 0]], V2[F[:, 2]] - V2[F[:, 0]])
    fn /= np.linalg.norm(fn, axis=1, keepdims=True) + 1e-12
    sel = np.zeros(len(F), bool)
    for op in paint:
        bx = op["box"]  # [xmin, xmax, ymin, ymax]
        sel |= (cen[:, 0] > bx[0]) & (cen[:, 0] < bx[1]) & (cen[:, 1] > bx[2]) & (cen[:, 1] < bx[3]) & (fn[:, 2] > op.get("nz_min", -1)) & (cen[:, 2] > op.get("z_min", -9))
    pos, nz, hit = raster_positions(sel)
    X3, Y3, Z3 = pos[..., 0], pos[..., 1], pos[..., 2]
    for op in paint:
        bx = op["box"]
        zone = hit & (X3 > bx[0]) & (X3 < bx[1]) & (Y3 > bx[2]) & (Y3 < bx[3]) & (nz > op.get("nz_min", -1)) & (Z3 > op.get("z_min", -9))
        zf = zone.astype(np.float32)
        if op["type"] == "eyes":
            for (ex, ey) in op["centers"]:
                rx, ry = op["rx"], op["ry"]
                dx, dy = (X3 - ex), (Y3 - ey)
                e = np.sqrt((dx / rx) ** 2 + (dy / ry) ** 2) - 1
                ix, iy = ex + op.get("look", [0, 0])[0], ey + op.get("look", [0, 0])[1]
                r = np.sqrt((X3 - ix) ** 2 + (Y3 - iy) ** 2)
                # the model's own eye shape, cleaned up in front-projection space (holes filled, edge smoothed)
                from scipy import ndimage as ndi
                skin = np.array(op.get("skin", [208, 158, 132]), np.float32)
                notskin = np.sqrt(((T3 - skin) ** 2).sum(2)) > op.get("skin_dist", 55)
                G = 240
                gx = np.clip(((X3 - (ex - rx)) / (2 * rx) * G).astype(int), 0, G - 1)
                gy = np.clip(((Y3 - (ey - ry)) / (2 * ry) * G).astype(int), 0, G - 1)
                inz = zone & (e < 0)
                grid = np.zeros((G, G)); cnt = np.zeros((G, G))
                np.add.at(grid, (gy[inz], gx[inz]), notskin[inz].astype(float)); np.add.at(cnt, (gy[inz], gx[inz]), 1)
                gm = grid / np.maximum(cnt, 1) > 0.5
                gm = ndi.binary_closing(gm, iterations=6)
                gm = ndi.binary_fill_holes(gm)
                gm = ndi.binary_opening(gm, iterations=4)
                lab, nl = ndi.label(gm)
                if nl > 1:
                    gm = lab == (np.argmax(ndi.sum(gm, lab, range(1, nl + 1))) + 1)
                sm = ndi.gaussian_filter(gm.astype(float), 2.0)
                sdf_in = ndi.distance_transform_edt(gm) / G * 2 * rx   # distance to edge (model units)
                em = sm[gy, gx] * inz
                edge = sdf_in[gy, gx]
                T3 = blend(T3, em, op.get("white", [252, 252, 252]))
                inside_eye = em
                # lid line along the upper edge
                upper = (Y3 > ey - ry * 0.15).astype(np.float32)
                T3 = blend(T3, em * upper * np.clip(1 - (edge - op.get("lid_w", 0.0035)) / 0.0015, 0, 1), op.get("lid", [38, 26, 24]))
                g = np.clip((Y3 - (iy - op["iris_r"])) / (2 * op["iris_r"]), 0, 1)[..., None]
                iris_col = np.array(op["iris"], np.float32) * (1 - g) + np.array(op["iris2"], np.float32) * g
                a = inside_eye * soft(r - op["iris_r"], 0.0025)
                T3 = T3 * (1 - a[..., None]) + iris_col * a[..., None]
                T3 = blend(T3, inside_eye * soft(r - op["pupil_r"], 0.002), op["pupil"])
                for hx, hy, hr in op.get("highlights", []):
                    rr = np.sqrt((X3 - (ix + hx)) ** 2 + (Y3 - (iy + hy)) ** 2)
                    T3 = blend(T3, inside_eye * soft(rr - hr, 0.0015), [255, 255, 255])
        elif op["type"] == "rocket":
            cxr, cyr = op["center"]; sz = op["size"]; ang = np.radians(op.get("angle", 0))
            # clear the old blurry print back to shirt colour
            old = zf * (T3.min(2) > op.get("clear_min", 150))
            old = np.asarray(Image.fromarray((old * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)), np.float32) / 255 * zf
            T3 = blend(T3, old, op["shirt"])
            u = ((X3 - cxr) * np.sin(ang) + (Y3 - cyr) * np.cos(ang)) / sz   # along the rocket (nose = +u)
            v = ((X3 - cxr) * np.cos(ang) - (Y3 - cyr) * np.sin(ang)) / sz
            body = np.sqrt(((u - 0.05) / 0.42) ** 2 + (v / 0.16) ** 2) - 1
            fin = np.maximum(np.abs(v) - (0.16 + 0.55 * np.clip(-0.12 - u, 0, 0.25)), np.maximum(u - (-0.05), -0.4 - u))
            flame = np.sqrt(((u + 0.47) / 0.1) ** 2 + (v / 0.06) ** 2) - 1
            shape = np.minimum(np.minimum(body * 0.16, fin), flame * 0.06)
            T3 = blend(T3, zf * soft(shape * sz, 0.0025), op.get("rgb", [252, 252, 250]))
            win = np.sqrt((u - 0.13) ** 2 + v ** 2) - 0.065
            T3 = blend(T3, zf * soft(win * sz, 0.002), op["shirt"])
        elif op["type"] == "recolor":
            sel2 = zf * (T3.min(2) < op.get("keep_white_min", 170))
            if "only_dark" in op:
                sel2 = sel2 * (T3.max(2) < op["only_dark"])
            lum = T3.mean(2, keepdims=True); ref = float(op.get("ref_lum", 140))
            col = np.clip(np.array(op["rgb"], np.float32) * (lum / ref) ** 0.6, 0, 255)
            T3 = T3 * (1 - sel2[..., None]) + col * sel2[..., None]
    print("painted", len(paint), "ops on", int(hit.sum()), "texels")

# ---------------- pad UV islands: texels outside every triangle take their neighbours' colour,
# so bilinear filtering at seams never picks up old gutter colours (white/black cracks)
cov = Image.new("L", (W, H), 0)
dcv = ImageDraw.Draw(cov)
for tri in F:
    dcv.polygon([(VT[i, 0] * (W - 1), (1 - VT[i, 1]) * (H - 1)) for i in tri], fill=255)
cm = (np.asarray(cov, np.float32) > 127).astype(np.float32)
from scipy.ndimage import uniform_filter
acc = T3 * cm[..., None]; wsum = cm.copy()
filled = T3 * cm[..., None]; known = cm.copy()
for _ in range(6):
    num = np.stack([uniform_filter(filled[..., k] * known, 3) for k in range(3)], 2)
    den = uniform_filter(known, 3)
    new = (den > 1e-3) & (known < 0.5)
    filled[new] = num[new] / den[new][:, None]
    known = np.maximum(known, new.astype(np.float32))
T3 = np.where(known[..., None] > 0.5, filled, T3)
out_img = Image.fromarray(np.clip(T3 + 0.5, 0, 255).astype(np.uint8))
rough = Image.fromarray((np.clip(0.8 - float(hc.get("gloss", 0.3)) * m[..., 0], 0, 1) * 255).astype(np.uint8)).convert("RGB")

# ---------------- write the new zip (same layout as glb2js.py output)
ol = []
vi = 0
for l in lines:
    if l.startswith("v "):
        x, y, zz = V2[vi]
        ol.append(f"v {x:.5f} {y:.5f} {zz:.5f}")
        vi += 1
    else:
        ol.append(l)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
    zo.writestr(name + ".obj", "\n".join(ol) + "\n")
    zo.writestr(name + ".mtl", z.read(name + ".mtl"))
    b = io.BytesIO(); out_img.save(b, "PNG"); zo.writestr(name + ".png", b.getvalue())
    b = io.BytesIO(); rough.save(b, "PNG"); zo.writestr(name + "_rough.png", b.getvalue())
print("wrote", out)
