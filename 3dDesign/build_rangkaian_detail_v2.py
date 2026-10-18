"""
PKM-GLICOVIA - Rekonstruksi detail rangkaian elektronika (v2)
=============================================================
Script Blender (bpy/bmesh) yang membangun ulang seluruh collection
`PKM_Electronics_Assembly` di `rangkaian_elektronika_pkm.blend`.

Satuan: 1 BU = 1 mm (scene unit scale 0.001, length mm).
Sumbu: +X kanan, +Y atas (sama seperti foto komponen/rangkaianTotal.jpeg), +Z ke atas meja.

Dimensi diverifikasi dari foto komponen/ (skala dikalibrasi memakai strip SPE 34 mm
dan pitch lubang perfboard 2.54 mm) + datasheet:
  - Perfboard 70 x 90 x 1.6 mm, 24 x 30 lubang pitch 2.54 (foto: 24 slot tepi, 30 baris)
  - ESP32 DevKitC 38-pin (19 pin/sisi, label 3V3..5V / GND..CLK), modul ESP32-WROOM-32U
    (18 x 19.2 x 3.2 mm, konektor IPEX/u.FL, tanpa antena PCB), PCB 54.4 x 27.9 mm,
    jarak baris header 25.4 mm. Dipasang di female header 8.5 mm.
  - ADS1115 breakout 28 x 17.5 mm, header 10 pin (A3..VDD) di sisi kanan.
  - 3x adaptor SOP8->DIP8 10.2 x 10.2 mm, baris DIP 7.62 mm.
  - TP4056 Type-C 28 x 17.3 mm; USB-C 8.94 x 3.26 mm.
  - LiPo 1200 mAh ~52 x 33 x 6.5 mm (terukur dari foto).
  - KCD11 bezel 15 x 10.5 mm.
  - OLED 0.96" SSD1306: PCB 27.3 x 27.8, kaca 26.7 x 19.26, area aktif 21.74 x 10.86.
  - Antena 2.4 GHz 110 mm, RP-SMA 1/4"-36 UNS, mur hex 8 mm.
  - SPE 34 x 10 x 0.4 mm, WE karbon Ø3 mm, RE Ag/AgCl, CE karbon tapal kuda.
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

D = bpy.data
SCENE = bpy.context.scene
ROOT_NAME = "PKM_Electronics_Assembly"
RAD = math.radians


# ---------------------------------------------------------------------------
# Material library (Principled BSDF, nilai PBR)
# ---------------------------------------------------------------------------
MATS = {
    # name: (base color linear, roughness, metallic, extra dict)
    "Mat_FR4_Green":      ((0.018, 0.30, 0.10), 0.22, 0.0, {"Coat Weight": 0.35, "Coat Roughness": 0.08, "Subsurface Weight": 0.12, "Subsurface Scale": 0.6}),
    "Mat_FR4_Green_OPA":  ((0.020, 0.26, 0.06), 0.25, 0.0, {"Coat Weight": 0.3, "Coat Roughness": 0.1, "Subsurface Weight": 0.1, "Subsurface Scale": 0.4}),
    "Mat_PCB_Blue":       ((0.008, 0.07, 0.42), 0.22, 0.0, {"Coat Weight": 0.4, "Coat Roughness": 0.08, "Subsurface Weight": 0.08, "Subsurface Scale": 0.4}),
    "Mat_PCB_Black":      ((0.012, 0.012, 0.014), 0.28, 0.0, {"Coat Weight": 0.45, "Coat Roughness": 0.1}),
    "Mat_Module_Sub":     ((0.02, 0.02, 0.025), 0.4, 0.0, {}),
    "Mat_IC_Molded":      ((0.022, 0.022, 0.024), 0.55, 0.0, {}),
    "Mat_IC_Mark":        ((0.42, 0.42, 0.42), 0.6, 0.0, {}),
    "Mat_Metal_Silver":   ((0.86, 0.87, 0.89), 0.18, 0.95, {}),
    "Mat_Shield_Can":     ((0.80, 0.81, 0.82), 0.26, 0.95, {"Anisotropic": 0.4}),
    "Mat_Stainless":      ((0.78, 0.78, 0.80), 0.18, 0.95, {}),
    "Mat_Brass_Gold":     ((0.95, 0.72, 0.15), 0.20, 0.92, {}),
    "Mat_Gold_Pin":       ((1.00, 0.76, 0.33), 0.15, 1.0, {}),
    "Mat_Solder_Tin":     ((0.78, 0.79, 0.81), 0.22, 0.90, {}),
    "Mat_Pad_HASL":       ((0.80, 0.76, 0.62), 0.25, 0.90, {}),
    "Mat_Copper":         ((0.95, 0.52, 0.32), 0.25, 1.0, {}),
    "Mat_Rubber_Black":   ((0.020, 0.020, 0.022), 0.62, 0.0, {}),
    "Mat_Plastic_Black":  ((0.014, 0.014, 0.016), 0.35, 0.0, {}),
    "Mat_Plastic_Matte":  ((0.018, 0.018, 0.02), 0.6, 0.0, {}),
    "Mat_Hole_Dark":      ((0.002, 0.002, 0.002), 0.5, 0.0, {}),
    "Mat_Battery_Silver": ((0.78, 0.79, 0.81), 0.35, 0.85, {}),
    "Mat_Kapton_Amber":   ((0.80, 0.42, 0.03), 0.18, 0.0, {"Transmission Weight": 0.45, "Thin Wall": True, "Alpha": 0.72}),
    "Mat_FFC_Amber":      ((0.62, 0.32, 0.03), 0.25, 0.0, {"Transmission Weight": 0.25, "Thin Wall": True}),
    "Mat_Switch_Red":     ((0.80, 0.07, 0.03), 0.32, 0.0, {"Coat Weight": 0.2}),
    "Mat_Print_White":    ((0.88, 0.88, 0.86), 0.5, 0.0, {}),
    "Mat_Print_Dark":     ((0.05, 0.05, 0.05), 0.5, 0.0, {}),
    "Mat_JST_White":      ((0.90, 0.89, 0.84), 0.42, 0.0, {"Subsurface Weight": 0.15, "Subsurface Scale": 0.5}),
    "Mat_Adapter_Blue":   ((0.010, 0.10, 0.70), 0.38, 0.0, {"Coat Weight": 0.25, "Coat Roughness": 0.2}),
    "Mat_Clear_Tape":     ((0.95, 0.95, 0.95), 0.12, 0.0, {"Transmission Weight": 1.0, "Thin Wall": True, "Alpha": 0.35}),
    "Mat_Glass_OLED":     ((0.95, 0.97, 0.98), 0.05, 0.0, {"Transmission Weight": 1.0, "IOR": 1.52}),
    "Mat_OLED_Active":    ((0.004, 0.004, 0.006), 0.06, 0.0, {"Coat Weight": 1.0, "Coat Roughness": 0.03}),
    "Mat_OLED_Film":      ((0.25, 0.55, 0.95), 0.15, 0.0, {"Transmission Weight": 0.7, "Thin Wall": True, "Alpha": 0.8}),
    "Mat_SPE_White":      ((0.90, 0.91, 0.90), 0.35, 0.0, {}),
    "Mat_SPE_Green":      ((0.17, 0.55, 0.40), 0.30, 0.0, {"Coat Weight": 0.2}),
    "Mat_SPE_Carbon":     ((0.012, 0.012, 0.014), 0.75, 0.0, {}),
    "Mat_SPE_Silver":     ((0.62, 0.63, 0.62), 0.42, 0.6, {}),
    "Mat_Cap_Blue":       ((0.10, 0.34, 0.85), 0.22, 0.0, {"Coat Weight": 0.5, "Coat Roughness": 0.05}),
    "Mat_Cap_Disc":       ((0.55, 0.24, 0.05), 0.32, 0.0, {"Coat Weight": 0.3}),
    "Mat_MLCC_Tan":       ((0.45, 0.33, 0.20), 0.45, 0.0, {}),
    "Mat_LED_Red":        ((0.95, 0.04, 0.02), 0.1, 0.0, {"Transmission Weight": 0.5}),
    "Mat_LED_Blue":       ((0.02, 0.15, 0.95), 0.1, 0.0, {"Transmission Weight": 0.5}),
    "Mat_LED_Body":       ((0.92, 0.92, 0.90), 0.3, 0.0, {}),
    "Mat_Wire_Red":       ((0.72, 0.02, 0.015), 0.35, 0.0, {"Coat Weight": 0.25}),
    "Mat_Wire_Black":     ((0.012, 0.012, 0.013), 0.35, 0.0, {"Coat Weight": 0.25}),
    "Mat_Wire_Yellow":    ((0.85, 0.58, 0.01), 0.35, 0.0, {"Coat Weight": 0.25}),
    "Mat_Wire_Orange":    ((0.90, 0.20, 0.01), 0.35, 0.0, {"Coat Weight": 0.25}),
    "Mat_Wire_Brown":     ((0.10, 0.035, 0.015), 0.35, 0.0, {"Coat Weight": 0.25}),
    "Mat_Wire_White":     ((0.82, 0.82, 0.80), 0.35, 0.0, {"Coat Weight": 0.25}),
    "Mat_Wire_Blue":      ((0.008, 0.05, 0.55), 0.35, 0.0, {"Coat Weight": 0.25}),
    "Mat_Wire_Green":     ((0.01, 0.30, 0.04), 0.35, 0.0, {"Coat Weight": 0.25}),
    "Mat_Lab_Table":      ((0.55, 0.56, 0.57), 0.42, 0.0, {}),
}


def get_mat(name):
    spec = MATS[name]
    mat = D.materials.get(name) or D.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
        nt.links.new(bsdf.outputs[0], out.inputs[0])
    col, rough, metal, extra = spec
    bsdf.inputs['Base Color'].default_value = (*col, 1.0)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    for k, v in extra.items():
        if k in bsdf.inputs:
            bsdf.inputs[k].default_value = v
    mat.diffuse_color = (*col, 1.0)
    if extra.get("Alpha", 1.0) < 1.0 or extra.get("Transmission Weight", 0) > 0:
        try:
            mat.surface_render_method = 'BLENDED' if extra.get("Alpha", 1.0) < 1.0 else 'DITHERED'
        except Exception:
            pass
        try:
            mat.use_raytrace_refraction = True
        except Exception:
            pass
    return mat


def add_micro_bump(mat_name, scale=1.2, strength=0.06, kind='NOISE'):
    """Tekstur mikro (foil baterai / meja) memakai Noise -> Bump."""
    mat = D.materials[mat_name]
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    for n in list(nt.nodes):
        if n.name.startswith("MB_"):
            nt.nodes.remove(n)
    tc = nt.nodes.new('ShaderNodeTexCoord'); tc.name = "MB_tc"
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.name = "MB_noise"
    noise.inputs['Scale'].default_value = scale
    noise.inputs['Detail'].default_value = 6.0
    bump = nt.nodes.new('ShaderNodeBump'); bump.name = "MB_bump"
    bump.inputs['Strength'].default_value = strength
    nt.links.new(tc.outputs['Object'], noise.inputs['Vector'])
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def TM(loc=(0, 0, 0), rot=(0, 0, 0)):
    """Matrix dari lokasi (mm) dan rotasi Euler XYZ (derajat)."""
    return Matrix.Translation(Vector(loc)) @ Euler([RAD(a) for a in rot], 'XYZ').to_matrix().to_4x4()


def rounded_rect(w, h, r, n=4):
    """Poligon persegi panjang bersudut bulat (CCW), center di origin."""
    r = min(r, w / 2 - 1e-4, h / 2 - 1e-4)
    if r <= 1e-4:
        return [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    pts = []
    corners = [(w / 2 - r, -h / 2 + r, -90), (w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180)]
    for cx, cy, a0 in corners:
        for i in range(n + 1):
            a = RAD(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def stadium(w, h, n=8):
    """Bentuk stadion (oval kapsul) lebar w, tinggi h."""
    return rounded_rect(w, h, min(w, h) / 2 - 1e-3, n)


def circle_pts(r, n=24, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


class Part:
    """Kumpulan geometri (bmesh) yang di-bake menjadi 1 object dengan beberapa material."""

    def __init__(self, name, col, parent=None):
        self.name, self.col, self.parent = name, col, parent
        self.bm = bmesh.new()
        self.mats = []
        self.texts = []

    def mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def _tag(self, faces, m):
        idx = self.mi(m)
        for f in faces:
            f.material_index = idx

    @staticmethod
    def _faces_of(verts):
        return list({f for v in verts for f in v.link_faces})

    # -- primitives ---------------------------------------------------------
    def box(self, size, loc, rot=(0, 0, 0), m="Mat_Plastic_Black", bevel=0.0, seg=2):
        M = TM(loc, rot) @ Matrix.Diagonal((size[0], size[1], size[2], 1.0))
        verts = bmesh.ops.create_cube(self.bm, size=1.0, matrix=M)['verts']
        faces = self._faces_of(verts)
        self._tag(faces, m)
        if bevel > 0:
            b = min(bevel, min(size) * 0.49)
            edges = list({e for v in verts for e in v.link_edges})
            res = bmesh.ops.bevel(self.bm, geom=edges, offset=b, segments=seg, profile=0.5,
                                  affect='EDGES', clamp_overlap=True)
            self._tag(res['faces'], m)
        return verts

    def cyl(self, r1, r2, h, loc, rot=(0, 0, 0), m="Mat_Solder_Tin", segs=24):
        verts = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=segs,
                                      radius1=r1, radius2=r2, depth=h, matrix=TM(loc, rot))['verts']
        self._tag(self._faces_of(verts), m)
        return verts

    def sphere(self, r, loc, scale=(1, 1, 1), rot=(0, 0, 0), m="Mat_Solder_Tin", seg=16):
        M = TM(loc, rot) @ Matrix.Diagonal((scale[0], scale[1], scale[2], 1.0))
        verts = bmesh.ops.create_uvsphere(self.bm, u_segments=seg, v_segments=max(6, seg // 2), radius=r, matrix=M)['verts']
        self._tag(self._faces_of(verts), m)
        return verts

    def geom(self, verts, faces, M, m):
        bv = [self.bm.verts.new(M @ Vector(v)) for v in verts]
        out = []
        for f in faces:
            try:
                out.append(self.bm.faces.new([bv[i] for i in f]))
            except ValueError:
                pass
        self._tag(out, m)
        return out

    def prism(self, poly, z0, z1, loc=(0, 0, 0), rot=(0, 0, 0), m="Mat_Plastic_Black", caps=True):
        """Poligon 2D (bidang XY lokal) diekstrusi dari z0 ke z1."""
        n = len(poly)
        verts = [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
        faces = []
        if caps:
            faces.append(list(range(n))[::-1])
            faces.append(list(range(n, 2 * n)))
        for i in range(n):
            j = (i + 1) % n
            faces.append([i, j, n + j, n + i])
        return self.geom(verts, faces, TM(loc, rot), m)

    def frame(self, outer, inner, z0, z1, loc=(0, 0, 0), rot=(0, 0, 0), m="Mat_Plastic_Black"):
        """Bingkai berlubang: loop luar & dalam (jumlah titik sama)."""
        n = len(outer)
        assert n == len(inner)
        V = ([(x, y, z0) for x, y in outer] + [(x, y, z1) for x, y in outer] +
             [(x, y, z0) for x, y in inner] + [(x, y, z1) for x, y in inner])
        F = []
        for i in range(n):
            j = (i + 1) % n
            F.append([i, j, n + j, n + i])                      # sisi luar
            F.append([3 * n + i, 3 * n + j, 2 * n + j, 2 * n + i])  # sisi dalam
            F.append([n + i, n + j, 3 * n + j, 3 * n + i])      # atas
            F.append([2 * n + i, 2 * n + j, j, i])              # bawah
        return self.geom(V, F, TM(loc, rot), m)

    def tube(self, r_in, r_out, z0, z1, loc=(0, 0, 0), rot=(0, 0, 0), m="Mat_Pad_HASL", segs=16):
        return self.frame(circle_pts(r_out, segs), circle_pts(r_in, segs), z0, z1, loc, rot, m)

    def lathe(self, profile, loc=(0, 0, 0), rot=(0, 0, 0), m="Mat_Rubber_Black", segs=32, rfunc=None):
        """Profil (r, z) diputar mengelilingi sumbu Z lokal. rfunc(r, z, theta) opsional (knurl/ulir)."""
        V, F = [], []
        rows = len(profile)
        for (r, z) in profile:
            for s in range(segs):
                t = 2 * math.pi * s / segs
                rr = rfunc(r, z, t) if (rfunc and r > 1e-6) else r
                V.append((rr * math.cos(t), rr * math.sin(t), z))
        for a in range(rows - 1):
            for s in range(segs):
                s2 = (s + 1) % segs
                F.append([a * segs + s, a * segs + s2, (a + 1) * segs + s2, (a + 1) * segs + s])
        # tutup ujung
        if profile[0][0] > 1e-6:
            F.append(list(range(segs))[::-1])
        if profile[-1][0] > 1e-6:
            F.append([(rows - 1) * segs + s for s in range(segs)])
        return self.geom(V, F, TM(loc, rot), m)

    def loft_x(self, sections, loc=(0, 0, 0), rot=(0, 0, 0), m="Mat_Adapter_Blue", n=6):
        """Loft sepanjang X dari penampang persegi bulat: (x, w, h, zc, r)."""
        V, F = [], []
        k = None
        for (x, w, h, zc, r) in sections:
            pts = rounded_rect(w, h, r, n)
            k = len(pts)
            for (py, pz) in pts:
                V.append((x, py, zc + pz))
        S = len(sections)
        for a in range(S - 1):
            for s in range(k):
                s2 = (s + 1) % k
                F.append([a * k + s, a * k + s2, (a + 1) * k + s2, (a + 1) * k + s])
        F.append(list(range(k)))
        F.append([(S - 1) * k + s for s in range(k)][::-1])
        return self.geom(V, F, TM(loc, rot), m)

    def sweep_rect(self, path, width, thick, loc=(0, 0, 0), rot=(0, 0, 0), m="Mat_FFC_Amber", axis_w=(1, 0, 0)):
        """Pita datar (FFC) mengikuti path 3D; lebar sepanjang axis_w."""
        W = Vector(axis_w).normalized()
        V, F = [], []
        P = [Vector(p) for p in path]
        for i, p in enumerate(P):
            t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
            nrm = W.cross(t).normalized()
            for sw, sn in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                V.append(tuple(p + W * (sw * width / 2) + nrm * (sn * thick / 2)))
        for i in range(len(P) - 1):
            for s in range(4):
                s2 = (s + 1) % 4
                F.append([i * 4 + s, i * 4 + s2, (i + 1) * 4 + s2, (i + 1) * 4 + s])
        F.append([0, 1, 2, 3][::-1])
        L = len(P) - 1
        F.append([L * 4 + s for s in range(4)])
        return self.geom(V, F, TM(loc, rot), m)

    def mesh_data(self, me, M, m=None, keep_mats=None):
        """Salin mesh data ke part (dengan transform)."""
        base = len(self.bm.verts)
        bv = [self.bm.verts.new(M @ v.co) for v in me.vertices]
        out = []
        for p in me.polygons:
            try:
                f = self.bm.faces.new([bv[i] for i in p.vertices])
            except ValueError:
                continue
            if keep_mats:
                f.material_index = self.mi(keep_mats[min(p.material_index, len(keep_mats) - 1)])
            else:
                f.material_index = self.mi(m)
            out.append(f)
        return out

    def text(self, s, size, loc, rot_z=0.0, m="Mat_Print_White", align='CENTER', rot=None, thick=0.0):
        self.texts.append((s, size, loc, rot if rot else (0, 0, rot_z), m, align, thick))

    # -- smd helpers -------------------------------------------------------------
    def gullwing_leg(self, base_z, top_z, out_x, loc, rot, m="Mat_Solder_Tin", width=0.3, t=0.15, foot=0.55):
        """Kaki gull-wing di bidang XZ lokal, keluar ke arah +X dari x=0."""
        zm = base_z + (top_z - base_z) * 0.5
        c = [(-0.2, zm), (0.25, zm), (out_x - foot, base_z + t / 2), (out_x, base_z + t / 2)]
        up, dn = [], []
        for i, (x, z) in enumerate(c):
            a = c[max(i - 1, 0)]; b = c[min(i + 1, len(c) - 1)]
            tx, tz = b[0] - a[0], b[1] - a[1]
            L = math.hypot(tx, tz) or 1
            nx, nz = -tz / L, tx / L
            up.append((x + nx * t / 2, z + nz * t / 2))
            dn.append((x - nx * t / 2, z - nz * t / 2))
        poly = up + dn[::-1]
        # poly di (x,z) -> prism pada sumbu Y
        n = len(poly)
        V = [(x, -width / 2, z) for x, z in poly] + [(x, width / 2, z) for x, z in poly]
        F = [list(range(n)), list(range(n, 2 * n))[::-1]]
        for i in range(n):
            j = (i + 1) % n
            F.append([i, n + i, n + j, j])
        return self.geom(V, F, TM(loc, rot), m)

    def ic_gullwing(self, body, loc, pins_per_side, pitch, lead_span, m_body="Mat_IC_Molded",
                    rot_z=0.0, mark=None, mark_size=0.6, dot=True, standoff=0.1, lead_w=0.32):
        """IC SMD gull-wing: kaki di sisi ±X lokal (setelah rot_z), body (lx, ly, lz)."""
        lx, ly, lz = body
        R = TM(loc, (0, 0, rot_z))
        z0 = standoff
        self.box((lx, ly, lz), (R @ Vector((0, 0, z0 + lz / 2)))[:], (0, 0, rot_z), m_body, bevel=min(0.12, lz * 0.2))
        out = (lead_span - lx) / 2 + 0.05
        for side in (-1, 1):
            for p in range(pins_per_side):
                y = (p - (pins_per_side - 1) / 2) * pitch
                lp = R @ Vector((side * (lx / 2 - 0.05), y, 0))
                self.gullwing_leg(0.0, z0 + lz * 0.55, out, lp[:], (0, 0, rot_z + (0 if side > 0 else 180)), width=lead_w)
                pad = R @ Vector((side * (lx / 2 + out - 0.3), y, -0.02))
                self.box((0.9, lead_w + 0.25, 0.04), pad[:], (0, 0, rot_z), "Mat_Solder_Tin")
        top = z0 + lz
        if dot:
            dp = R @ Vector((-lx / 2 + min(0.6, lx * 0.18), ly / 2 - min(0.6, ly * 0.18), top + 0.005))
            self.cyl(min(0.28, lx * 0.08), min(0.28, lx * 0.08), 0.02, dp[:], (0, 0, 0), "Mat_Plastic_Black", 12)
        if mark:
            lines = mark if isinstance(mark, (list, tuple)) else [mark]
            for i, s in enumerate(lines):
                yy = (len(lines) - 1) / 2 * mark_size * 1.3 - i * mark_size * 1.3
                tp = R @ Vector((0, yy, top + 0.012))
                self.text(s, mark_size, tp[:], rot_z + 90 if ly > lx * 1.15 else rot_z, "Mat_IC_Mark")
        return top

    def chip(self, kind, loc, rot_z=0.0, body_mat=None, mark=None, size=None):
        """Komponen chip 0402/0603/0805: kind 'R','C','LED'."""
        L, W, H = size or (1.6, 0.8, 0.45)
        R = TM(loc, (0, 0, rot_z))
        cap = L * 0.2
        if kind == 'LED':
            self.box((L, W, H * 0.55), (R @ Vector((0, 0, H * 0.275)))[:], (0, 0, rot_z), "Mat_LED_Body", bevel=0.04)
            self.box((L * 0.62, W * 0.8, H * 0.5), (R @ Vector((0, 0, H * 0.55 + H * 0.25)))[:], (0, 0, rot_z), body_mat, bevel=0.08)
            for s in (-1, 1):
                self.box((cap, W, 0.12), (R @ Vector((s * (L / 2 - cap / 2), 0, 0.06)))[:], (0, 0, rot_z), "Mat_Solder_Tin")
            return
        bm_ = body_mat or ("Mat_IC_Molded" if kind == 'R' else "Mat_MLCC_Tan")
        self.box((L - 2 * cap + 0.02, W * 0.98, H), (R @ Vector((0, 0, H / 2)))[:], (0, 0, rot_z), bm_, bevel=0.03)
        for s in (-1, 1):
            self.box((cap, W, H + 0.02), (R @ Vector((s * (L / 2 - cap / 2), 0, H / 2 + 0.01)))[:], (0, 0, rot_z), "Mat_Solder_Tin", bevel=0.04)
            self.sphere(0.35, (R @ Vector((s * (L / 2 + 0.05), 0, 0.05)))[:], (W * 1.2, W * 1.5, 0.35), (0, 0, rot_z), "Mat_Solder_Tin", 10)
        if mark and kind == 'R':
            self.text(mark, W * 0.55, (R @ Vector((0, 0, H + 0.01)))[:], rot_z, "Mat_Print_White")

    def sot23(self, loc, rot_z=0.0, n6=False, mark=None):
        R = TM(loc, (0, 0, rot_z))
        lx, ly, lz = 2.9, 1.6, 1.0
        self.box((lx, ly, lz), (R @ Vector((0, 0, 0.1 + lz / 2)))[:], (0, 0, rot_z), "Mat_IC_Molded", bevel=0.1)
        xs_bottom = (-0.95, 0.0, 0.95) if n6 else (-0.95, 0.95)
        xs_top = (-0.95, 0.0, 0.95) if n6 else (0.0,)
        for xs, side in ((xs_bottom, -1), (xs_top, 1)):
            for x in xs:
                lp = R @ Vector((x, side * (ly / 2 - 0.05), 0))
                self.gullwing_leg(0.0, 0.6, 0.65, lp[:], (0, 0, rot_z + (90 if side > 0 else -90)), width=0.38)
        if mark:
            self.text(mark, 0.5, (R @ Vector((0, 0, 1.11 + 0.01)))[:], rot_z, "Mat_IC_Mark")

    # -- bake ----------------------------------------------------------------------
    def bake(self, smooth_angle=32.0):
        bm = self.bm
        for f in bm.faces:
            f.smooth = True
        lim = RAD(smooth_angle)
        for e in bm.edges:
            if len(e.link_faces) == 2:
                try:
                    e.smooth = e.calc_face_angle() < lim
                except ValueError:
                    e.smooth = False
            else:
                e.smooth = False
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        me = D.meshes.new(self.name)
        bm.to_mesh(me)
        bm.free()
        for m in self.mats:
            me.materials.append(get_mat(m))
        ob = D.objects.new(self.name, me)
        self.col.objects.link(ob)
        if self.parent:
            ob.parent = self.parent
        return ob


# ---------------------------------------------------------------------------
# Text batching (FONT -> mesh) supaya depsgraph dievaluasi sekali saja
# ---------------------------------------------------------------------------
def bake_texts(parts):
    tmp = []
    for p in parts:
        for (s, size, loc, rot, m, align, thick) in p.texts:
            cu = D.curves.new("tmp_txt", 'FONT')
            cu.body = s
            cu.size = size
            cu.align_x = align
            cu.align_y = 'CENTER'
            cu.resolution_u = 2
            cu.extrude = thick
            ob = D.objects.new("tmp_txt", cu)
            SCENE.collection.objects.link(ob)
            tmp.append((p, ob, cu, loc, rot, m))
    if not tmp:
        return
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    for (p, ob, cu, loc, rot, m) in tmp:
        me = D.meshes.new_from_object(ob.evaluated_get(dg))
        p.mesh_data(me, TM(loc, rot), m)
        D.meshes.remove(me)
        D.objects.remove(ob, do_unlink=True)
        D.curves.remove(cu)
    for p in parts:
        p.texts = []


# ---------------------------------------------------------------------------
# Boolean: lubang PCB (solver MANIFOLD, hasil di-bake jadi mesh biasa)
# ---------------------------------------------------------------------------
def pcb_with_holes(name, w, h, t, holes, corner_r=0.6, segs=14):
    bmb = bmesh.new()
    poly = rounded_rect(w, h, corner_r, 3)
    n = len(poly)
    vb = [bmb.verts.new((x, y, 0)) for x, y in poly]
    vt = [bmb.verts.new((x, y, t)) for x, y in poly]
    bmb.faces.new(vb[::-1]); bmb.faces.new(vt)
    for i in range(n):
        j = (i + 1) % n
        bmb.faces.new([vb[i], vb[j], vt[j], vt[i]])
    base_me = D.meshes.new(name + "_base")
    bmb.to_mesh(base_me); bmb.free()
    if not holes:
        return base_me
    bmc = bmesh.new()
    for (x, y, r) in holes:
        bmesh.ops.create_cone(bmc, cap_ends=True, cap_tris=False, segments=segs, radius1=r, radius2=r,
                              depth=t + 2.0, matrix=Matrix.Translation((x, y, t / 2)))
    cut_me = D.meshes.new(name + "_cut")
    bmc.to_mesh(cut_me); bmc.free()
    ob_b = D.objects.new(name + "_tmpb", base_me)
    ob_c = D.objects.new(name + "_tmpc", cut_me)
    SCENE.collection.objects.link(ob_b); SCENE.collection.objects.link(ob_c)
    mod = ob_b.modifiers.new("holes", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = ob_c
    mod.solver = 'MANIFOLD'
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    res = D.meshes.new_from_object(ob_b.evaluated_get(dg))
    D.objects.remove(ob_b, do_unlink=True); D.objects.remove(ob_c, do_unlink=True)
    D.meshes.remove(base_me); D.meshes.remove(cut_me)
    return res


# ---------------------------------------------------------------------------
# Scene structure
# ---------------------------------------------------------------------------
def reset_root():
    root = D.collections.get(ROOT_NAME)
    if root is None:
        root = D.collections.new(ROOT_NAME)
        SCENE.collection.children.link(root)

    def purge(col):
        for ch in list(col.children):
            purge(ch)
            D.collections.remove(ch)
        for o in list(col.objects):
            D.objects.remove(o, do_unlink=True)
    purge(root)
    for coll in (D.meshes, D.curves):
        for blk in list(coll):
            if blk.users == 0:
                coll.remove(blk)
    return root


def sub_col(root, name):
    c = D.collections.new(name)
    root.children.link(c)
    return c


def empty(name, col, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, size=5.0):
    e = D.objects.new(name, None)
    e.empty_display_type = 'PLAIN_AXES'
    e.empty_display_size = size
    e.location = loc
    e.rotation_euler = [RAD(a) for a in rot]
    col.objects.link(e)
    if parent:
        e.parent = parent
    return e


def mat_of(*chain):
    """Matrix dunia dari rantai (loc, rot)."""
    M = Matrix.Identity(4)
    for loc, rot in chain:
        M = M @ TM(loc, rot)
    return M


# ---------------------------------------------------------------------------
# Global layout (koordinat dunia, mm) - diukur dari rangkaianTotal.jpeg
# ---------------------------------------------------------------------------
PITCH = 2.54
BOARD_W, BOARD_H, BOARD_T = 70.0, 90.0, 1.6
NCOL, NROW = 24, 30
PERF_Z = 2.2                      # bawah perfboard (bertumpu pada ujung pin/solder)
T = BOARD_T                       # top perfboard (lokal)


def HX(i):
    return (i - (NCOL - 1) / 2) * PITCH


def HY(j):
    return (j - (NROW - 1) / 2) * PITCH


PERF_T = ((0.0, 0.0, PERF_Z), (0, 0, 0))
ESP_T = ((6.35, -13.97, T + 8.5 + 2.5), (0, 0, 0))        # lokal perfboard
ADS_T = ((-25.85, -10.16, T + 2.5), (0, 0, 0))            # lokal perfboard
OPA_X = (-22.86, 0.0, 22.86)
OPA_Y = 27.94
OLED_HDR = (29.21, 7.62)                                  # header 4-pin di tepi kanan perfboard
TP_T = ((-71.1, 38.6, 0.0), (0, 0, 18.0))
BAT_T = ((-65.5, -22.3, 0.0), (0, 0, 90.0))
SW_LOC = (-69.5, 64.6, 5.25)
ADAPTER_T = [((-80.5, 107.0, 0.0), (0, 0, -9.0)),
             ((-80.0, 94.5, 0.0), (0, 0, -6.0)),
             ((-76.5, 81.6, 0.0), (0, 0, -5.0))]
ANT_ROOT = (67.7, -9.9, 4.8)
ANT_DIR_DEG = -170.3
OLED_XY = (-14.0, -104.0)
SPE_LOOSE = [((-63.2, -65.9, 0.0), (0, 0, 2.0)), ((-1.1, -60.7, 0.0), (0, 0, 181.0))]

# Pin label ESP32 DevKitC (atas -> bawah)
ESP_LEFT = ["3V3", "EN", "VP", "VN", "34", "35", "32", "33", "25", "26", "27", "14", "12", "GND", "13", "D2", "D3", "CMD", "5V"]
ESP_RIGHT = ["GND", "23", "22", "TX", "RX", "21", "GND", "19", "18", "5", "17", "16", "4", "0", "2", "15", "D1", "D0", "CLK"]


def esp_pin_local(side, label):
    lst = ESP_LEFT if side < 0 else ESP_RIGHT
    k = lst.index(label)
    return (side * 12.7, (9 - k) * PITCH)


def esp_pin_perf(side, label):
    x, y = esp_pin_local(side, label)
    return (ESP_T[0][0] + x, ESP_T[0][1] + y)


ADS_LABELS = ["A3", "A2", "A1", "A0", "ALRT", "ADDR", "SDA", "SCL", "GND", "VDD"]


def ads_pin_perf(label):
    k = ADS_LABELS.index(label)
    return (ADS_T[0][0] + 6.8, ADS_T[0][1] + 11.43 - k * PITCH)


# ---------------------------------------------------------------------------
# 1. MAIN PERFBOARD 70 x 90 (24 x 30 lubang)
# ---------------------------------------------------------------------------
USED_HOLES = set()      # lubang (perf lokal) yang diisi pin/kawat -> solder di bawah


def mark_hole(x, y):
    USED_HOLES.add((round(x, 2), round(y, 2)))


def build_perfboard(col, root):
    holes = [(HX(i), HY(j), 0.52) for i in range(NCOL) for j in range(NROW)]
    corner = [(sx * 32.0, sy * 42.0, 1.55) for sx in (-1, 1) for sy in (-1, 1)]
    me = pcb_with_holes("Main_Perfboard", BOARD_W, BOARD_H, BOARD_T, holes + corner, corner_r=0.8, segs=12)
    board = Part("Main_Perfboard", col, root)
    board.mesh_data(me, Matrix.Identity(4), "Mat_FR4_Green")
    D.meshes.remove(me)

    pads = Part("Perfboard_Pads", col, root)
    for (x, y, _) in holes:
        pads.tube(0.48, 0.88, -0.035, T + 0.035, (x, y, 0), m="Mat_Pad_HASL", segs=14)
    for (x, y, _) in corner:
        pads.tube(1.5, 2.25, -0.035, T + 0.035, (x, y, 0), m="Mat_Pad_HASL", segs=24)
    slot = stadium(1.45, 3.5, 5)
    for i in range(NCOL):
        for sy in (-1, 1):
            for z0, z1 in ((T, T + 0.035), (-0.035, 0.0)):
                pads.prism(slot, z0, z1, (HX(i), sy * 40.65, 0), m="Mat_Pad_HASL")

    silk = Part("Perfboard_Silkscreen", col, root)
    letters = "ABCDEFGHIJKLMNOPQRSTUVWX"
    for i in range(NCOL):
        silk.text(letters[i], 0.85, (HX(i), 38.32, T + 0.04))
    for j in range(NROW):
        silk.text(str(j + 1), 0.8, (32.35, HY(j), T + 0.04), rot_z=90)
    return [board, pads, silk]


# ---------------------------------------------------------------------------
# Header & pin helpers (koordinat lokal perfboard)
# ---------------------------------------------------------------------------
def male_pin_column(part, xy_list, z_bottom, z_top, plastic_z0, plastic_z1, plastic=True, solder_top=None):
    for (x, y) in xy_list:
        part.box((0.64, 0.64, z_top - z_bottom), (x, y, (z_top + z_bottom) / 2), m="Mat_Gold_Pin", bevel=0.08)
        if plastic:
            part.box((2.5, 2.5, plastic_z1 - plastic_z0), (x, y, (plastic_z0 + plastic_z1) / 2), m="Mat_Plastic_Black", bevel=0.18)
        if solder_top is not None:
            part.cyl(0.95, 0.42, 0.75, (x, y, solder_top + 0.375), m="Mat_Solder_Tin", segs=16)


def bottom_solder(part, x, y, stub=2.0):
    part.cyl(0.42, 0.95, 0.85, (x, y, -0.425), m="Mat_Solder_Tin", segs=16)
    part.box((0.64, 0.64, stub), (x, y, -stub / 2), m="Mat_Solder_Tin", bevel=0.1)


# ---------------------------------------------------------------------------
# 2. ESP32 DevKitC-32U (38 pin) + female header
# ---------------------------------------------------------------------------
def build_esp32(col, perf_root):
    root = empty("ESP32_DevKit_Root", col, ESP_T[0], ESP_T[1], perf_root)
    # Female header 2x19 di perfboard (lokal perfboard)
    fh = Part("ESP32_Female_Headers", col, perf_root)
    for side in (-1, 1):
        for k in range(19):
            x = ESP_T[0][0] + side * 12.7
            y = ESP_T[0][1] + (9 - k) * PITCH
            fh.box((2.54, 2.54, 8.5), (x, y, T + 4.25), m="Mat_Plastic_Black", bevel=0.14)
            fh.box((1.0, 1.0, 0.06), (x, y, T + 8.5 + 0.005), m="Mat_Hole_Dark")
            fh.box((0.5, 0.5, 3.6), (x, y, T - 1.6), m="Mat_Solder_Tin")
            mark_hole(x, y)

    pcb = Part("ESP32_PCB", col, root)
    pcb.box((27.9, 54.4, 1.6), (0, 0, 0.8), m="Mat_PCB_Black", bevel=0.25)
    pins = Part("ESP32_Header_Pins", col, root)
    silk = Part("ESP32_Silkscreen", col, root)
    for side in (-1, 1):
        lst = ESP_LEFT if side < 0 else ESP_RIGHT
        for k, lab in enumerate(lst):
            x, y = side * 12.7, (9 - k) * PITCH
            pins.tube(0.5, 0.95, 1.6, 1.64, (x, y, 0), m="Mat_Gold_Pin", segs=16)
            silk.text(lab, 0.95, (side * 10.35, y, 1.64), rot_z=-90 if side < 0 else -90)
        male_pin_column(pins, [(side * 12.7, (9 - k) * PITCH) for k in range(19)], -8.5, 2.55, -2.5, 0.0, True, 1.62)
    silk.text("EN", 1.1, (-8.0, -19.9, 1.64))
    silk.text("Boot", 1.1, (7.9, -19.7, 1.64))

    # ---- Modul ESP32-WROOM-32U (18 x 19.2 x 3.2) ----
    mod = Part("ESP32_WROOM32U_Module", col, root)
    my = 27.2 - 9.6
    mod.box((18.0, 19.2, 0.8), (0, my, 1.6 + 0.4), m="Mat_Module_Sub", bevel=0.1)
    for side in (-1, 1):
        for p in range(14):
            yy = my - 9.6 + 1.6 + p * 1.27
            mod.box((0.9, 0.85, 0.82), (side * 8.6, yy, 2.0), m="Mat_Gold_Pin")
    for p in range(10):
        mod.box((0.85, 0.9, 0.82), ((p - 4.5) * 1.27, my - 9.6 + 0.35, 2.0), m="Mat_Gold_Pin")
    can = Part("ESP32_Shield_Can", col, root)
    sz0, sh = 2.4, 2.35
    # kaleng RF berbentuk L (coakan di kanan atas untuk konektor IPEX)
    Lpoly = [(-7.9, my - 8.5), (7.9, my - 8.5), (7.9, my + 4.5), (2.7, my + 4.5), (2.7, my + 8.1), (-7.9, my + 8.1)]
    can.prism(Lpoly, sz0, sz0 + sh - 0.3, m="Mat_Shield_Can")
    inset = [(-7.6, my - 8.2), (7.6, my - 8.2), (7.6, my + 4.2), (2.4, my + 4.2), (2.4, my + 7.8), (-7.6, my + 7.8)]
    can.geom([(x, y, sz0 + sh - 0.3) for x, y in Lpoly] + [(x, y, sz0 + sh) for x, y in inset],
             [[i, (i + 1) % 6, 6 + (i + 1) % 6, 6 + i] for i in range(6)] + [list(range(6, 12))],
             Matrix.Identity(4), "Mat_Shield_Can")
    top = sz0 + sh + 0.01
    silk.text("ESP-32U", 1.75, (-0.6, my + 2.2, top), m="Mat_Print_Dark")
    silk.text("espressif", 1.0, (-2.4, my + 5.6, top), m="Mat_Print_Dark")
    silk.text("ESP32-WROOM-32U", 0.9, (0, my - 0.4, top), m="Mat_Print_Dark")
    silk.text("FCC ID: 2AC7Z-ESP32WROOM32U", 0.5, (0, my - 2.2, top), m="Mat_Print_Dark")
    silk.text("CE", 1.2, (-4.5, my - 4.6, top), m="Mat_Print_Dark")
    silk.text("R 205-000519", 0.55, (2.2, my - 4.6, top), m="Mat_Print_Dark")
    # konektor IPEX u.FL (receptacle + plug)
    ipex = Part("ESP32_IPEX_UFL", col, root)
    ix, iy = 5.4, 25.5
    ipex.box((2.6, 2.6, 0.35), (ix, iy, 2.4 + 0.175), m="Mat_Gold_Pin", bevel=0.05)
    ipex.box((1.6, 1.6, 0.08), (ix, iy, 2.79), m="Mat_LED_Body")
    ipex.cyl(1.0, 1.0, 1.25, (ix, iy, 2.75 + 0.625), m="Mat_Gold_Pin", segs=24)
    ipex.cyl(0.55, 0.55, 0.2, (ix, iy, 4.1), m="Mat_Gold_Pin", segs=16)
    ipex.box((1.2, 2.6, 0.75), (ix + 0.9, iy + 0.9, 3.4), (0, 0, 45), m="Mat_Gold_Pin", bevel=0.1)
    # area bawah modul: 6 pad timah besar
    for side in (-1, 1):
        for p in range(3):
            pcb.box((2.4, 1.15, 0.05), (side * 9.0, 6.6 - p * 1.9, 1.62), m="Mat_Solder_Tin", bevel=0.02)

    smd = Part("ESP32_SMD", col, root)
    # AMS1117-3.3 (SOT-223), kaki 3 ke -X, tab ke +X
    smd.box((3.5, 6.5, 1.6), (0.2, -5.0, 0.1 + 1.6 + 0.8), m="Mat_IC_Molded", bevel=0.12)
    for p in range(3):
        smd.gullwing_leg(1.6, 1.6 + 0.9, 1.2, (-1.5, -5.0 + (p - 1) * 2.3, 0), (0, 0, 180), width=0.7)
        smd.box((1.4, 1.1, 0.05), (-2.85, -5.0 + (p - 1) * 2.3, 1.62), m="Mat_Solder_Tin")
    smd.gullwing_leg(1.6, 1.6 + 0.9, 1.4, (1.9, -5.0, 0), (0, 0, 0), width=3.0)
    smd.box((2.2, 3.4, 0.05), (3.0, -5.0, 1.62), m="Mat_Solder_Tin")
    silk.text("AMS1117", 0.55, (0.2, -4.2, 3.32), rot_z=90, m="Mat_IC_Mark")
    silk.text("3.3", 0.55, (-0.7, -5.0, 3.32), rot_z=90, m="Mat_IC_Mark")
    # CP2102 QFN-28 5x5
    smd.box((5.0, 5.0, 0.9), (0, -13.0, 1.6 + 0.45), m="Mat_IC_Molded", bevel=0.06)
    for s in range(4):
        for p in range(7):
            a = RAD(90 * s)
            u = (p - 3) * 0.5
            px, py = 2.45 * math.cos(a) - u * math.sin(a), 2.45 * math.sin(a) + u * math.cos(a)
            smd.box((0.3 if s % 2 == 0 else 0.22, 0.22 if s % 2 == 0 else 0.3, 0.2), (px, -13.0 + py, 1.7), m="Mat_Solder_Tin")
    silk.text("CP2102", 0.6, (0, -12.6, 2.52), m="Mat_IC_Mark")
    silk.text("DCL00X", 0.5, (0, -13.6, 2.52), m="Mat_IC_Mark")
    smd.cyl(0.25, 0.25, 0.02, (-1.9, -11.1, 2.51), m="Mat_Plastic_Black", segs=10)
    # transistor & ESD
    smd.sot23((7.6, -5.3, 1.6), 0)
    smd.sot23((7.6, -13.6, 1.6), 0)
    smd.sot23((-5.0, -17.4, 1.6), 0)
    smd.sot23((0.0, -18.2, 1.6), 0, n6=True)
    # pasif & LED
    for (x, y, rz, k) in [(-7.8, -2.8, 90, 'C'), (-5.5, -2.8, 90, 'C'), (-7.8, -6.7, 90, 'R'), (-5.5, -6.7, 90, 'C'),
                          (4.1, -10.9, 0, 'R'), (4.1, -15.6, 0, 'C'), (-5.2, -10.2, 90, 'R'), (-5.2, -13.0, 90, 'R'),
                          (-5.2, -15.3, 90, 'C'), (4.9, -19.0, 90, 'R'), (-3.6, -20.6, 0, 'R'), (3.6, -20.6, 0, 'R')]:
        smd.chip(k, (x, y, 1.6), rz, mark="103" if k == 'R' else None)
    smd.chip('LED', (-7.8, -11.9, 1.6), 90, body_mat="Mat_LED_Red")
    smd.chip('LED', (-7.8, -15.3, 1.6), 90, body_mat="Mat_LED_Blue")
    # tombol EN & BOOT (SMD tact switch)
    for (bx, by) in ((-8.2, -23.3), (8.2, -22.6)):
        smd.box((3.0, 4.0, 1.0), (bx, by, 1.6 + 0.5), m="Mat_Plastic_Black", bevel=0.1)
        smd.box((3.0, 4.0, 0.18), (bx, by, 2.69), m="Mat_Metal_Silver", bevel=0.05)
        smd.cyl(0.8, 0.75, 0.55, (bx, by, 2.78 + 0.27), m="Mat_Plastic_Matte", segs=20)
        for s in (-1, 1):
            smd.box((1.0, 0.8, 0.2), (bx, by + s * 2.35, 1.7), m="Mat_Solder_Tin", bevel=0.05)
    # Micro-USB B (rongga trapesium + lidah)
    usb = Part("ESP32_MicroUSB", col, root)
    oy0, depth = -28.7, 5.0
    outer = [(-3.75, 0.0), (3.75, 0.0), (3.75, 1.95), (3.35, 2.55), (-3.35, 2.55), (-3.75, 1.95)]
    inner = [(-3.45, 0.3), (3.45, 0.3), (3.45, 1.75), (3.1, 2.25), (-3.1, 2.25), (-3.45, 1.75)]
    usb.frame(outer, inner, 0.0, depth, (0, oy0 + depth, 1.62), (90, 0, 0), m="Mat_Stainless")
    usb.prism(outer, 0.0, 0.4, (0, oy0 + depth, 1.62), (90, 0, 0), m="Mat_Stainless")
    usb.box((6.8, 0.2, 2.0), (0, oy0 + depth - 0.6, 1.62 + 1.25), m="Mat_Hole_Dark")
    usb.box((3.6, 3.6, 0.6), (0, oy0 + 2.4, 1.62 + 1.05), m="Mat_Plastic_Black")
    for p in range(5):
        usb.box((0.3, 2.2, 0.05), ((p - 2) * 0.65, oy0 + 2.6, 1.62 + 0.72), m="Mat_Gold_Pin")
        usb.box((0.35, 1.2, 0.12), ((p - 2) * 0.65, oy0 + depth + 0.4, 1.68), m="Mat_Gold_Pin")
    for s in (-1, 1):
        usb.box((1.2, 1.6, 0.25), (s * 4.25, oy0 + 2.2, 1.75), m="Mat_Stainless")
        usb.sphere(0.6, (s * 4.3, oy0 + 2.2, 1.85), (1.4, 1.6, 0.6), m="Mat_Solder_Tin", seg=12)
    return [fh, pcb, pins, silk, mod, can, ipex, smd, usb], root


# ---------------------------------------------------------------------------
# 3. ADS1115 breakout
# ---------------------------------------------------------------------------
def build_ads1115(col, perf_root):
    root = empty("ADS1115_Root", col, ADS_T[0], ADS_T[1], perf_root)
    holes = [(-6.2, 11.6, 1.25), (-6.2, -11.6, 1.25)]
    me = pcb_with_holes("ADS1115_PCB", 17.5, 28.0, 1.6, holes, corner_r=0.8)
    pcb = Part("ADS1115_PCB", col, root)
    pcb.mesh_data(me, Matrix.Identity(4), "Mat_PCB_Blue"); D.meshes.remove(me)
    for (x, y, r) in holes:
        pcb.tube(r, r + 0.75, -0.03, 1.63, (x, y, 0), m="Mat_Gold_Pin", segs=24)
    pins = Part("ADS1115_Header", col, root)
    silk = Part("ADS1115_Silkscreen", col, root)
    for k, lab in enumerate(ADS_LABELS):
        y = 11.43 - k * PITCH
        pins.tube(0.5, 0.9, 1.6, 1.64, (6.8, y, 0), m="Mat_Gold_Pin", segs=16)
        silk.text(lab, 0.95, (5.55, y, 1.64), align='RIGHT')
        px, py = ads_pin_perf(lab)
        mark_hole(px, py)
    male_pin_column(pins, [(6.8, 11.43 - k * PITCH) for k in range(10)], -6.1, 2.6, -2.5, 0.0, True, 1.62)
    silk.text("V280", 1.2, (-1.6, 12.6, 1.64))
    silk.text("16Bit I2C ADC+PGA", 1.15, (-7.1, -0.6, 1.64), rot_z=90)
    silk.text("ADS1115.", 1.15, (-5.45, -2.4, 1.64), rot_z=90)
    smd = Part("ADS1115_SMD", col, root)
    smd.ic_gullwing((3.0, 3.0, 0.95), (1.8, 9.4, 1.6), 5, 0.5, 4.9, rot_z=90, mark=["BOGI"], mark_size=0.6, lead_w=0.23)
    smd.chip('C', (-1.5, 7.2, 1.6), 90, size=(2.0, 1.25, 0.6))
    for i, y in enumerate((-1.0, -3.0, -5.0, -7.1, -9.1, -11.1)):
        smd.chip('R' if i < 4 else 'C', (-1.6, y, 1.6), 0, mark="103" if i < 4 else None)
        for s in (-1, 1):
            silk.box((2.6, 0.12, 0.02), (-1.6, y + s * 0.7, 1.61), m="Mat_Print_White")
    smd.chip('C', (0.6, -9.7, 1.6), 90, size=(2.0, 1.25, 0.6))
    return [pcb, pins, silk, smd], root


# ---------------------------------------------------------------------------
# 4. 3x OPA breakout SOP8->DIP8 + kapasitor
# ---------------------------------------------------------------------------
def build_opa(col, perf_root):
    parts = []
    roots = []
    for n, cx in enumerate(OPA_X):
        root = empty(f"OPA_Module_{n + 1}_Root", col, (cx, OPA_Y, T + 2.5), (0, 0, 0), perf_root)
        roots.append(root)
        p = Part(f"OPA_Module_{n + 1}", col, root)
        p.box((10.2, 10.2, 1.0), (0, 0, 0.5), m="Mat_FR4_Green_OPA", bevel=0.15)
        dips = [(sx * 3.81, (k - 1.5) * PITCH) for sx in (-1, 1) for k in range(4)]
        for (x, y) in dips:
            p.tube(0.45, 0.85, 1.0, 1.04, (x, y, 0), m="Mat_Pad_HASL", segs=14)
            mark_hole(cx + x, OPA_Y + y)
        male_pin_column(p, dips, -6.1, 2.0, -2.5, 0.0, True, 1.02)
        # SOIC-8: kaki ke ±Y (body memanjang X)
        p.ic_gullwing((3.9, 4.9, 1.45), (0, 0, 1.0), 4, 1.27, 6.0, rot_z=90, lead_w=0.42)
        # jalur tembaga adaptor dari pad SOIC ke lubang DIP
        for k in range(4):
            for sy in (-1, 1):
                x0, y0 = (k - 1.5) * 1.27, sy * 3.2
                x1, y1 = (-3.81 if k < 2 else 3.81), sy * (3.81 if k in (0, 3) else 1.27)
                L = math.hypot(x1 - x0, y1 - y0)
                p.box((L, 0.3, 0.03), ((x0 + x1) / 2, (y0 + y1) / 2, 1.015), (0, 0, math.degrees(math.atan2(y1 - y0, x1 - x0))), m="Mat_Pad_HASL")
        p.text("SOP8", 0.7, (0, -4.6, 1.02))
        parts.append(p)

    caps = Part("OPA_Capacitors", col, perf_root)

    def disc_cap(x, yc):
        prof = [(0.0, -1.15), (2.2, -1.15), (2.95, -0.8), (3.15, 0.0), (2.95, 0.8), (2.2, 1.15), (0.0, 1.15)]
        zc = T + 3.4 + 3.1
        caps.lathe(prof, (x, yc, zc), (0, 90, 0), m="Mat_Cap_Disc", segs=32)
        for s in (-1, 1):
            caps.box((0.45, 0.45, zc - 1.5 - T + 2.0), (x, yc + s * 2.54, (zc - 1.5 + T - 2.0) / 2), m="Mat_Solder_Tin")
            mark_hole(x, yc + s * 2.54)

    def blue_cap(x, yc, lean=10.0):
        zc = T + 3.6 + 2.0
        prof = [(0.0, -1.9), (0.9, -1.85), (1.55, -1.3), (1.75, 0.0), (1.55, 1.25), (0.95, 1.85), (0.0, 1.95)]
        dx = math.sin(RAD(lean)) * 3.6
        caps.lathe(prof, (x + dx, yc, zc), (0, lean, 0), m="Mat_Cap_Blue", segs=24)
        # skala pipih: tambahkan badan oval dengan box bevel
        for s in (-1, 1):
            caps.box((0.45, 0.45, zc - 1.6 - T + 2.0), (x, yc + s * 1.27, (zc - 1.6 + T - 2.0) / 2), m="Mat_Solder_Tin")
            mark_hole(x, yc + s * 1.27)

    disc_cap(6.35, 26.67)
    blue_cap(8.89, 20.32, 8)
    blue_cap(8.89, 25.4, 12)
    disc_cap(29.21, 26.67)
    blue_cap(29.21, 20.32, 18)
    blue_cap(29.21, 33.02, 18)
    parts.append(caps)
    return parts, roots


# ---------------------------------------------------------------------------
# 5. Header OLED (4 pin + female dupont vertikal) di tepi kanan perfboard
# ---------------------------------------------------------------------------
def build_oled_header(col, perf_root):
    p = Part("OLED_Board_Header", col, perf_root)
    x0, yc = OLED_HDR
    ys = [yc + (k - 1.5) * PITCH for k in range(4)]
    male_pin_column(p, [(x0, y) for y in ys], -2.0, T + 2.5 + 6.0, T, T + 2.5, True, None)
    for y in ys:
        mark_hole(x0, y)
    p.box((2.54, 10.16, 14.0), (x0, yc, T + 2.5 + 7.0), m="Mat_Plastic_Black", bevel=0.2)
    for y in ys:
        p.box((1.2, 1.2, 1.2), (x0, y, T + 2.5 + 14.0 - 0.5), m="Mat_Hole_Dark")
        p.box((1.6, 0.9, 3.0), (x0 + 1.05, y, T + 2.5 + 9.0), m="Mat_Plastic_Black")
    return [p]


# ---------------------------------------------------------------------------
# 6. TP4056 Type-C charger
# ---------------------------------------------------------------------------
TP_PADS = {"OUT+": (6.6, -12.7), "B+": (2.5, -11.6), "B-": (-2.5, -11.6), "OUT-": (-6.6, -12.7)}


def build_tp4056(col, parent_col_root):
    root = empty("TP4056_Root", col, TP_T[0], TP_T[1])
    holes = [(x, y, 0.5) for (x, y) in TP_PADS.values()] + [(7.2, 12.7, 0.45), (-7.2, 12.7, 0.45)]
    me = pcb_with_holes("TP4056_PCB", 17.3, 28.0, 1.2, holes, corner_r=0.5)
    pcb = Part("TP4056_PCB", col, root)
    pcb.mesh_data(me, Matrix.Identity(4), "Mat_PCB_Blue"); D.meshes.remove(me)
    silk = Part("TP4056_Silkscreen", col, root)
    for lab, (x, y) in TP_PADS.items():
        pcb.box((2.2, 2.2, 0.04), (x, y, 1.22), m="Mat_Solder_Tin", bevel=0.3)
        pcb.box((2.2, 2.2, 0.04), (x, y, -0.02), m="Mat_Solder_Tin", bevel=0.3)
        pcb.tube(0.48, 0.6, 0.0, 1.2, (x, y, 0), m="Mat_Solder_Tin", segs=12)
        silk.text(lab, 0.85, (x * 0.62, y + 2.15, 1.23), rot_z=0)
    for s, lab in ((1, "+"), (-1, "-")):
        pcb.tube(0.45, 0.85, -0.02, 1.22, (s * 7.2, 12.7, 0), m="Mat_Solder_Tin", segs=16)
        silk.text(lab, 1.1, (s * 7.2, 10.6, 1.23))
    silk.text("4056", 1.0, (4.6, -3.0, 1.23), rot_z=90)
    for (x, y, lab) in ((2.6, 3.4, "R1"), (-3.6, 0.6, "C1"), (4.6, 6.6, "R3"), (-4.3, 7.6, "R4"), (-1.0, -3.3, "C2"), (3.6, -8.0, "U2")):
        silk.text(lab, 0.7, (x, y, 1.23))
    smd = Part("TP4056_SMD", col, root)
    smd.ic_gullwing((3.9, 4.9, 1.45), (0.4, 2.3, 1.2), 4, 1.27, 6.0, rot_z=0, mark=["TP4056", "2341"], mark_size=0.55)
    smd.box((2.4, 3.0, 0.04), (0.4, 2.3, 1.21), m="Mat_Solder_Tin")
    smd.ic_gullwing((3.0, 4.4, 1.0), (2.6, -6.4, 1.2), 4, 0.65, 6.4, rot_z=90, mark=["8205A"], mark_size=0.5, lead_w=0.25)
    smd.sot23((-2.9, -7.0, 1.2), 0, n6=True, mark="DW01")
    for (x, y, rz, k) in ((2.6, 4.9, 0, 'R'), (-3.6, 2.0, 90, 'C'), (4.6, 8.2, 90, 'R'), (-4.3, 9.2, 90, 'R'),
                          (-1.0, -2.0, 0, 'C'), (5.8, -1.5, 90, 'R'), (-5.8, -3.5, 90, 'C')):
        smd.chip(k, (x, y, 1.2), rz, mark="122" if k == 'R' else None)
    smd.chip('LED', (-6.3, 5.0, 1.2), 90, body_mat="Mat_LED_Red")
    smd.chip('LED', (-6.3, 8.0, 1.2), 90, body_mat="Mat_LED_Blue")
    # USB Type-C (stadion berongga + lidah + kontak)
    usb = Part("TP4056_TypeC", col, root)
    depth = 7.35
    outer = stadium(8.94, 3.26, 8)
    inner = stadium(8.34, 2.56, 8)
    y_front = 14.0 + 0.6
    usb.frame(outer, inner, 0.0, depth - 0.5, (0, y_front, 1.2 + 1.63), (90, 0, 0), m="Mat_Stainless")
    usb.prism(outer, depth - 0.5, depth, (0, y_front, 1.2 + 1.63), (90, 0, 0), m="Mat_Stainless")
    usb.box((6.69, 3.9, 0.7), (0, y_front - 1.0 - 1.95, 2.83), m="Mat_Plastic_Black", bevel=0.1)
    usb.box((7.9, 0.3, 2.3), (0, y_front - 6.6, 2.83), m="Mat_Hole_Dark")
    for p in range(12):
        x = (p - 5.5) * 0.5
        for sz in (-1, 1):
            usb.box((0.25, 3.0, 0.03), (x, y_front - 2.6, 2.83 + sz * 0.36), m="Mat_Gold_Pin")
    for s in (-1, 1):
        for yy in (y_front - 1.5, y_front - 5.6):
            usb.box((0.6, 1.0, 2.6), (s * 4.32, yy, 1.2 + 0.1), m="Mat_Stainless")
            usb.sphere(0.8, (s * 4.32, yy, 1.3), (1.1, 1.3, 0.5), m="Mat_Solder_Tin", seg=12)
    for p in range(8):
        usb.box((0.28, 1.1, 0.12), ((p - 3.5) * 0.6, y_front - depth - 0.45, 1.26), m="Mat_Solder_Tin")
    return [pcb, silk, smd, usb], root


# ---------------------------------------------------------------------------
# 7. Baterai LiPo pouch 3.7V 1200mAh
# ---------------------------------------------------------------------------
BAT_WIRE_Y = {"red": 22.9, "black": 24.3}


def build_battery(col):
    root = empty("LiPo_Battery_Root", col, BAT_T[0], BAT_T[1])
    p = Part("LiPo_Pouch", col, root)
    # badan pouch (pillow)
    p.box((31.0, 43.0, 6.3), (0, -3.0, 3.15), m="Mat_Battery_Silver", bevel=1.6, seg=5)
    # bibir kelim segel bawah 1.5 mm + crimp
    p.box((31.0, 1.6, 0.32), (0, -25.3, 3.15), m="Mat_Battery_Silver", bevel=0.1)
    for i in range(36):
        p.box((0.32, 1.5, 0.06), (-14.9 + i * 0.85, -25.3, 3.15 + 0.18), m="Mat_Battery_Silver")
    # sirip samping dilipat ke atas (crimped edge seal)
    for s in (-1, 1):
        p.box((0.32, 43.0, 4.6), (s * 16.0, -3.0, 3.3), (0, s * -14, 0), m="Mat_Battery_Silver", bevel=0.1)
        for i in range(48):
            p.box((0.07, 0.3, 4.2), (s * (16.0 + 0.2), -24.0 + i * 0.88, 3.3), (0, s * -14, 0), m="Mat_Battery_Silver")
    # kepala: segel atas, tab nikel, PCM
    head = Part("LiPo_PCM_Board", col, root)
    head.box((30.0, 3.0, 1.0), (0, 20.0, 4.6), m="Mat_Battery_Silver", bevel=0.2)
    for s in (-1, 1):
        head.box((3.0, 4.0, 0.12), (s * 7.5, 21.5, 4.0), m="Mat_Metal_Silver")
    head.box((28.0, 4.0, 0.8), (0, 23.6, 3.2), m="Mat_PCB_Blue", bevel=0.1)
    head.sot23((-3.0, 23.6, 3.6), 0, n6=True)
    head.sot23((3.0, 23.6, 3.6), 0, n6=True)
    head.chip('R', (8.5, 23.6, 3.6), 0)
    head.chip('C', (-8.5, 23.6, 3.6), 0)
    for y in BAT_WIRE_Y.values():
        head.sphere(0.9, (12.6, y, 3.75), (1.3, 1.0, 0.6), m="Mat_Solder_Tin", seg=12)
    kap = Part("LiPo_Kapton_Tape", col, root)
    # selongsong kapton tipis (0.12 mm) membungkus kepala PCM, ujung terbuka
    kap.frame(rounded_rect(33.0, 6.75, 0.8, 4), rounded_rect(32.76, 6.51, 0.7, 4), -4.1, 4.1, (0, 22.1, 3.37), (90, 0, 0), m="Mat_Kapton_Amber")
    kap.box((32.9, 0.12, 6.6), (0, 26.15, 3.35), m="Mat_Kapton_Amber", bevel=0.05)
    # pita kapton tepi samping menutup sirip kelim (terlihat 2 mm dari atas)
    for s in (-1, 1):
        kap.box((0.12, 43.0, 6.2), (s * 16.62, -3.0, 3.2), m="Mat_Kapton_Amber")
        kap.box((2.0, 43.0, 0.08), (s * 15.6, -3.0, 6.34), m="Mat_Kapton_Amber")
    kap.box((32.4, 0.12, 5.6), (0, -26.25, 3.0), m="Mat_Kapton_Amber")
    lab = Part("LiPo_Label_Text", col, root)
    lab.text("3.7V 1200mAh", 2.6, (0, -1.0, 6.31), rot_z=90, m="Mat_Print_Dark")
    lab.text("4.44Wh  Li-Polymer", 1.8, (3.6, -1.0, 6.31), rot_z=90, m="Mat_Print_Dark")
    return [p, head, kap, lab], root


# ---------------------------------------------------------------------------
# 8. Saklar rocker KCD11 (rebah menyamping seperti di foto)
# ---------------------------------------------------------------------------
def switch_matrix():
    # lokal X(15mm) -> dunia +Y ; lokal Y(10.5) -> dunia -Z ; lokal Z(normal panel) -> dunia -X
    R = Matrix(((0, 0, -1), (1, 0, 0), (0, -1, 0)))
    return R


def build_switch(col):
    R = switch_matrix()
    eul = R.to_euler('XYZ')
    root = empty("Switch_KCD11_Root", col, SW_LOC, tuple(math.degrees(a) for a in eul))
    p = Part("Switch_KCD11", col, root)
    # bezel/flange: bingkai 15 x 10.5, bukaan 12.4 x 8.2
    p.frame(rounded_rect(15.0, 10.5, 0.9, 3), rounded_rect(12.4, 8.2, 0.5, 3), 0.0, 1.6, m="Mat_Plastic_Black")
    p.box((15.0, 10.5, 0.2), (0, 0, 0.1), m="Mat_Plastic_Black")
    # badan bawah panel + klip snap-in
    p.box((13.4, 8.6, 10.2), (0, 0, -5.1), m="Mat_Plastic_Matte", bevel=0.3)
    for s in (-1, 1):
        p.geom([(-3.0, 0, 0), (3.0, 0, 0), (3.0, 0, -4.5), (-3.0, 0, -4.5), (-3.0, 0.9, -1.0), (3.0, 0.9, -1.0)],
               [[0, 1, 2, 3], [0, 4, 5, 1], [4, 3, 2, 5], [0, 3, 4], [1, 5, 2]],
               TM((0, s * 4.3, -1.2), (0, 0, 0 if s > 0 else 180)), "Mat_Plastic_Matte")
    # rocker cekung (profil XZ diekstrusi sepanjang Y)
    xs = [(-5.8 + 11.6 * i / 20) for i in range(21)]
    top = [(x, 2.6 + 0.12 * x + 0.62 * (x / 5.8) ** 2) for x in xs]
    poly = [(-5.8, 0.4), (5.8, 0.4)] + top[::-1]
    n = len(poly)
    V = [(x, -3.8, z) for x, z in poly] + [(x, 3.8, z) for x, z in poly]
    F = [list(range(n)), list(range(n, 2 * n))[::-1]]
    for i in range(n):
        j = (i + 1) % n
        F.append([i, n + i, n + j, j])
    p.geom(V, F, Matrix.Identity(4), "Mat_Switch_Red")
    # simbol I dan O (cetak putih mengikuti lereng)
    def ztop(x):
        return 2.6 + 0.12 * x + 0.62 * (x / 5.8) ** 2

    def slope(x):
        return math.degrees(math.atan(0.12 + 2 * 0.62 * x / 5.8 ** 2))
    p.box((2.4, 0.5, 0.05), (3.2, 0, ztop(3.2) + 0.02), (0, -slope(3.2), 0), m="Mat_Print_White")
    ring_o = circle_pts(1.25, 24)
    ring_i = circle_pts(0.85, 24)
    p.frame(ring_o, ring_i, -0.025, 0.025, (-3.2, 0, ztop(-3.2) + 0.02), (0, -slope(-3.2), 0), m="Mat_Print_White")
    # lug terminal (kuningan berlapis timah) dengan lubang solder Ø1.5
    # pelat di bidang XZ lokal (rebah horizontal di dunia), lubang di z = -15.2
    hw, hr, zc = 1.8, 0.75, -15.2
    outer_pts, inner_pts = [], []
    for k in range(24):
        a = 2 * math.pi * k / 24
        c, sn = math.cos(a), math.sin(a)
        tmax = min(abs(hw / c) if abs(c) > 1e-6 else 1e9, abs(hw / sn) if abs(sn) > 1e-6 else 1e9)
        outer_pts.append((c * tmax, sn * tmax))
        inner_pts.append((c * hr, sn * hr))
    for s in (-1, 1):
        L = (s * 2.5, 0, zc)
        p.frame(outer_pts, inner_pts, -0.25, 0.25, L, (90, 0, 0), m="Mat_Solder_Tin")
        p.prism([(-hw, hw), (hw, hw), (hw, -10.2 - zc), (-hw, -10.2 - zc)], -0.25, 0.25, L, (90, 0, 0), m="Mat_Solder_Tin")
        p.prism([(-hw, -hw - 0.25), (hw, -hw - 0.25), (hw, -hw), (-hw, -hw)], -0.25, 0.25, L, (90, 0, 0), m="Mat_Solder_Tin")
    return [p], root


SW_LUG_LOCAL = [(2.5, 0.0, -15.2), (-2.5, 0.0, -15.2)]


# ---------------------------------------------------------------------------
# 9. OLED 0.96" SSD1306 I2C
# ---------------------------------------------------------------------------
def oled_local_parts(col, root):
    holes = [(sx * 11.65, sy * 11.9, 1.05) for sx in (-1, 1) for sy in (-1, 1)]
    me = pcb_with_holes("OLED_PCB", 27.3, 27.8, 1.2, holes, corner_r=0.6)
    pcb = Part("OLED_PCB", col, root)
    pcb.mesh_data(me, Matrix.Identity(4), "Mat_PCB_Blue"); D.meshes.remove(me)
    for (x, y, r) in holes:
        pcb.tube(r, r + 0.7, -0.03, 1.23, (x, y, 0), m="Mat_Pad_HASL", segs=24)
    silk = Part("OLED_Silkscreen", col, root)
    hy = 12.2
    labels = ["VCC", "GND", "SCL", "SDA"]
    hdr = Part("OLED_Header_Pin_1", col, root)
    xs = [(k - 1.5) * PITCH for k in range(4)]
    for k, x in enumerate(xs):
        pcb.tube(0.5, 0.9, 1.2, 1.24, (x, hy, 0), m="Mat_Pad_HASL", segs=16)
        silk.text(labels[k], 0.8, (x, hy - 1.75, 1.24), rot_z=90 if False else 0)
    silk.text("1", 0.9, (xs[0] - 1.9, hy, 1.24))
    silk.text("4", 0.9, (xs[-1] + 1.9, hy, 1.24))
    # header lurus menghadap belakang + female dupont 4-pin
    male_pin_column(hdr, [(x, hy) for x in xs], -9.0, 1.9, -2.5, 0.0, True, 1.22)
    hdr.box((10.16, 2.54, 14.0), (0, hy, -2.5 - 7.0), m="Mat_Plastic_Black", bevel=0.2)
    for x in xs:
        hdr.box((0.9, 1.6, 3.0), (x, hy - 1.05, -2.5 - 5.0), m="Mat_Plastic_Black")
    # panel kaca ganda + area aktif + FFC
    glass_y = -2.57
    gl = Part("OLED_Glass_Substrate", col, root)
    gl.box((26.7, 19.26, 0.55), (0, glass_y, 1.2 + 0.25 + 0.275), m="Mat_Glass_OLED", bevel=0.05)
    gl.box((26.7, 16.4, 0.55), (0, glass_y + 1.43, 1.2 + 0.25 + 0.55 + 0.275), m="Mat_Glass_OLED", bevel=0.05)
    gl.box((26.0, 18.6, 0.25), (0, glass_y, 1.2 + 0.125), m="Mat_Plastic_Black")
    act = Part("OLED_Active_Panel", col, root)
    act.box((24.7, 15.8, 0.04), (0, glass_y + 1.43, 1.2 + 0.25 + 0.55 + 0.02), m="Mat_OLED_Active")
    act.box((21.74, 10.86, 0.02), (0, glass_y + 2.0, 1.2 + 0.25 + 1.1 + 0.012), m="Mat_OLED_Active")
    film = Part("OLED_Protect_Film", col, root)
    film.box((26.4, 16.2, 0.05), (0, glass_y + 1.43, 2.33), m="Mat_OLED_Film")
    film.box((8.0, 6.0, 0.05), (13.2 + 4.0, glass_y + 1.0, 2.33), m="Mat_OLED_Film")
    ffc = Part("OLED_FFC_Ribbon", col, root)
    # FFC: menempel di ledge kaca bawah, keluar tepi kaca, melengkung mengelilingi tepi PCB ke sisi bawah
    path = [(0, -9.6, 2.06), (0, -12.2, 2.06), (0, -13.3, 1.95)]
    cy_, cz_, rr = -13.9, 0.6, 1.4
    for k in range(1, 12):
        a = RAD(90 + 180 * k / 12)
        path.append((0, cy_ + rr * math.cos(a), cz_ + rr * math.sin(a)))
    path += [(0, -13.9, -0.8), (0, -12.0, -0.76), (0, -7.0, -0.76)]
    ffc.sweep_rect(path, 12.0, 0.12, m="Mat_FFC_Amber")
    ffc.box((12.4, 2.6, 0.2), (0, -11.2, -0.75), m="Mat_Plastic_Black")
    return [pcb, silk, hdr, gl, act, film, ffc]


def build_oled(col):
    root = empty("OLED_096_Root", col, (0, 0, 0), (0, 0, 0))
    parts = oled_local_parts(col, root)
    # Hitung kemiringan agar tepi depan menyentuh meja & housing dupont 3 mm di atas meja
    front = [Vector((x, -13.9, z)) for x in (-13.65, 13.65) for z in (-0.4, 0.0)]
    front += [Vector((x, y, z)) for x in (-6.0, 6.0) for (y, z) in ((-15.3, 0.6), (-13.9, -0.86), (-14.9, -0.4))]
    housing = [Vector((x, y, -16.5)) for x in (-5.08, 5.08) for y in (12.2 - 1.27, 12.2 + 1.27)]
    best = None
    for i in range(0, 90):
        a = RAD(i * 0.5 + 5)
        Rx = Matrix.Rotation(a, 4, 'X')
        zf = min((Rx @ v).z for v in front)
        zh = min((Rx @ v).z for v in housing)
        d = (zh - zf) - 4.0
        if best is None or abs(d) < abs(best[1]):
            best = (a, d, zf)
    a, d, zf = best
    root.rotation_euler = (a, 0, RAD(-90))
    root.location = (OLED_XY[0], OLED_XY[1], -zf)
    return parts, root


# ---------------------------------------------------------------------------
# 10. Antena 2.4 GHz + RP-SMA bulkhead
# ---------------------------------------------------------------------------
def build_antenna(col):
    root = empty("Antenna_RPSMA_Root", col, ANT_ROOT, (-90, 0, ANT_DIR_DEG))
    sma = Part("Ant_RPSMA_Brass", col, root)
    # badan belakang + mur hex 8mm AF + washer + ulir 1/4"-36
    sma.lathe([(0.0, -2.6), (2.0, -2.6), (2.75, -2.2), (2.75, 0.0), (0.0, 0.0)], m="Mat_Brass_Gold", segs=32)
    hexr = 4.0 / math.cos(RAD(30))
    sma.lathe([(0.0, 0.0), (hexr - 0.35, 0.0), (hexr, 0.3), (hexr, 2.2), (hexr - 0.35, 2.5), (0.0, 2.5)], m="Mat_Brass_Gold", segs=6)
    sma.lathe([(3.2, 2.5), (4.5, 2.5), (4.5, 3.0), (3.2, 3.0)], m="Mat_Metal_Silver", segs=40)
    pitch = 25.4 / 36
    prof = [(3.0, 2.95 + i * 0.05) for i in range(0, int((9.2 - 2.95) / 0.05))]

    def thread(r, z, t):
        ph = ((z - (t / (2 * math.pi)) * pitch) / pitch) % 1.0
        return 2.85 + 0.33 * (1 - abs(2 * ph - 1))
    sma.lathe([(0.0, 2.95)] + prof + [(0.0, prof[-1][1])], m="Mat_Brass_Gold", segs=40, rfunc=thread)
    rub = Part("Ant_Rubber_Body", col, root)

    def knurl(r, z, t):
        return r + 0.18 * abs(math.sin(15 * t)) if 9.6 < z < 19.4 else r
    rub.lathe([(0.0, 9.0), (4.2, 9.0), (4.75, 9.6), (4.75, 19.4), (4.6, 20.0), (0.0, 20.0)], m="Mat_Rubber_Black", segs=60, rfunc=knurl)
    # engsel (knuckle) + celah + pin poros metal
    rub.lathe([(0.0, 20.2), (4.6, 20.2), (4.7, 22.6), (0.0, 22.6)], m="Mat_Rubber_Black", segs=40)
    rub.lathe([(0.0, 23.0), (4.7, 23.0), (4.65, 27.0), (0.0, 27.0)], m="Mat_Rubber_Black", segs=40)
    rub.box((3.2, 9.6, 0.5), (0, 0, 22.8), m="Mat_Rubber_Black")
    rub.cyl(0.85, 0.85, 9.7, (0, 0, 21.4), (0, 90, 0), m="Mat_Metal_Silver", segs=16)
    for s in (-1, 1):
        rub.cyl(1.1, 1.1, 0.12, (s * 4.83, 0, 21.4), (0, 90, 0), m="Mat_Metal_Silver", segs=16)
    # badan meruncing + alur grip + kubah ujung
    def base_r(z):
        return 4.6 - (z - 28.0) * (4.6 - 3.95) / 74.0
    grooves = ((45.7, 46.3), (97.2, 97.8), (99.2, 99.8))
    zs = sorted(set([28.0 + 2 * i for i in range(37)] + [g for pair in grooves for g in pair] +
                    [pair[0] - 0.2 for pair in grooves] + [pair[1] + 0.2 for pair in grooves] + [102.0]))
    body = [(0.0, 27.2), (4.45, 27.2)]
    for z in zs:
        if z > 102.0:
            continue
        inside = any(g0 <= z <= g1 for g0, g1 in grooves)
        body.append((base_r(z) - (0.22 if inside else 0.0), z))
    for k in range(1, 10):
        a = RAD(90 * k / 9)
        body.append((max(0.0, 3.95 * math.cos(a)), 102.0 + 7.8 * math.sin(a)))
    rub.lathe(body, m="Mat_Rubber_Black", segs=40)
    # sleeve heatshrink coax di belakang SMA
    hs = Part("Ant_Coax_Heatshrink", col, root)
    hs.lathe([(0.0, -16.0), (1.1, -16.0), (1.8, -14.0), (1.85, -2.4), (1.6, -2.4), (0.0, -2.4)], m="Mat_Rubber_Black", segs=24)
    return [sma, rub, hs], root


# ---------------------------------------------------------------------------
# 11. Adapter SPE (heat-shrink biru + JST-XH 3 pin)
# ---------------------------------------------------------------------------
def build_adapters(col):
    parts, roots = [], []
    for n, (loc, rot) in enumerate(ADAPTER_T):
        root = empty(f"SPE_Adapter_{n + 1}_Root", col, loc, rot)
        roots.append(root)
        p = Part(f"SPE_Adapter_{n + 1}", col, root)
        secs = [(-21.0, 10.0, 6.0, 3.0, 1.6), (-19.5, 10.4, 6.3, 3.15, 1.8), (-9.0, 9.4, 6.0, 3.0, 1.8),
                (-6.5, 6.4, 4.7, 2.35, 1.9), (-4.0, 6.0, 4.5, 2.25, 1.9), (10.0, 6.1, 4.5, 2.25, 1.9),
                (13.0, 8.6, 5.6, 2.8, 1.8), (19.0, 9.3, 5.9, 2.95, 1.6), (19.6, 9.0, 5.6, 2.95, 1.4)]
        p.loft_x(secs, m="Mat_Adapter_Blue", n=5)
        # mulut konektor hitam + slot strip
        p.box((1.2, 9.2, 5.2), (-21.2, 0, 3.0), m="Mat_Plastic_Matte", bevel=0.3)
        p.box((0.3, 7.6, 0.7), (-21.85, 0, 3.0), m="Mat_Hole_Dark")
        # isolasi bening di kepala
        p.loft_x([(-20.5, 10.9, 6.9, 3.25, 2.0), (-12.0, 10.5, 6.8, 3.2, 2.0)], m="Mat_Clear_Tape", n=5)
        # PCB hijau + JST-XH
        p.box((2.4, 10.8, 1.6), (20.4, 0, 2.0), m="Mat_FR4_Green_OPA", bevel=0.1)
        p.box((4.0, 9.9, 6.0), (23.4, 0, 3.0), m="Mat_JST_White", bevel=0.25)
        p.box((6.4, 9.0, 5.2), (28.6, 0, 3.1), m="Mat_JST_White", bevel=0.35)
        p.box((3.0, 3.0, 0.6), (27.6, 0, 5.9), m="Mat_JST_White", bevel=0.15)
        for k in range(3):
            y = (k - 1) * 2.5
            p.box((0.9, 1.4, 1.4), (31.8, y, 3.6), m="Mat_Hole_Dark")
            p.box((0.64, 0.64, 2.0), (21.5, y, 0.9), m="Mat_Solder_Tin")
        p.text(f"0{n + 2}0-1-50", 0.95, (2.0, 0.0, 4.52), m="Mat_Print_Dark")
        parts.append(p)
    return parts, roots


ADAPTER_WIRE_EXIT = [((32.2, (k - 1) * 2.5, 3.6)) for k in range(3)]


# ---------------------------------------------------------------------------
# 12. Strip SPE 34 x 10 x 0.4 mm
# ---------------------------------------------------------------------------
def build_spe_strip(col, name, loc, rot):
    root = empty(name + "_Root", col, loc, rot)
    p = Part(name, col, root)
    L, W, ts = 34.0, 10.0, 0.30
    p.box((L, W, ts), (0, 0, ts / 2), m="Mat_SPE_White", bevel=0.04)
    zc, zg, zt = ts + 0.012, ts + 0.04, ts + 0.06
    # pad kontak perak
    for y in (-2.9, 0.0, 2.9):
        p.box((6.6, 1.5, 0.024), (13.3, y, zc), m="Mat_SPE_Silver")
    cxw = -12.2
    R_win = 4.2
    # dielektrik hijau dengan jendela melingkar
    x_split = cxw + 4.5
    p.box((9.6 - x_split, W - 0.6, 0.05), ((9.6 + x_split) / 2, 0, zg), m="Mat_SPE_Green")
    rect = (-16.7, x_split, -4.7, 4.7)
    angs = sorted(set([2 * math.pi * i / 72 for i in range(72)] +
                      [math.atan2(yy, xx) % (2 * math.pi) for xx in (rect[0] - cxw, rect[1] - cxw) for yy in (rect[2], rect[3])]))
    outer, inner = [], []
    for a in angs:
        c, s = math.cos(a), math.sin(a)
        tx = ((rect[1] - cxw) / c) if c > 1e-9 else ((rect[0] - cxw) / c if c < -1e-9 else 1e9)
        ty = (rect[3] / s) if s > 1e-9 else ((rect[2] / s) if s < -1e-9 else 1e9)
        t = min(tx, ty)
        outer.append((cxw + c * t, s * t))
        inner.append((cxw + c * R_win, s * R_win))
    p.frame(outer, inner, zg - 0.025, zg + 0.025, m="Mat_SPE_Green")
    # elektroda: WE (cakram karbon Ø3), RE (busur Ag/AgCl), CE (tapal kuda karbon)
    p.cyl(1.5, 1.5, 0.03, (cxw, 0, zc + 0.003), m="Mat_SPE_Carbon", segs=40)
    p.box((x_split - (cxw + 1.2), 0.9, 0.03), ((x_split + cxw + 1.2) / 2, 0, zc + 0.003), m="Mat_SPE_Carbon")

    def arc(r0, r1, a0, a1, m, z):
        n = 40
        o = [(cxw + r1 * math.cos(RAD(a0 + (a1 - a0) * i / n)), r1 * math.sin(RAD(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
        ii = [(cxw + r0 * math.cos(RAD(a0 + (a1 - a0) * i / n)), r0 * math.sin(RAD(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
        p.prism(o + ii[::-1], z - 0.015, z + 0.015, m=m)
    arc(2.1, 2.65, 55, 305, "Mat_SPE_Silver", zc)
    arc(3.05, 3.75, 47, 313, "Mat_SPE_Carbon", zc)
    p.box((x_split - (cxw + 1.45), 0.5, 0.03), ((x_split + cxw + 1.45) / 2, 1.8, zc), m="Mat_SPE_Silver")
    p.box((x_split - (cxw + 2.3), 0.5, 0.03), ((x_split + cxw + 2.3) / 2, -2.45, zc), m="Mat_SPE_Carbon")
    # jalur konduktor di atas dielektrik (terlihat gelap)
    for (y0, y1) in ((1.8, 2.9), (0.0, 0.0), (-2.45, -2.9)):
        pts = [(x_split, y0), (x_split + 3.0, y0), (x_split + 5.0, y1), (10.0, y1)]
        for a, b in zip(pts[:-1], pts[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            Lg = math.hypot(dx, dy)
            p.box((Lg + 0.35, 0.35, 0.02), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, zt), (0, 0, math.degrees(math.atan2(dy, dx))), m="Mat_Print_Dark")
    # label putih
    for sy in (-1, 1):
        p.box((5.0, 1.5, 0.02), (4.8, sy * 3.9, zt), m="Mat_SPE_White")
    p.text("ZP-01", 0.8, (4.8, 3.9, zt + 0.012), m="Mat_Print_Dark")
    return [p], root


# ---------------------------------------------------------------------------
# 13. Kabel (Bezier 3D, bevel bulat)
# ---------------------------------------------------------------------------
def wire(col, name, pts, radius, mat, res=20):
    cu = D.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    cu.resolution_u = res
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, pt in zip(sp.bezier_points, pts):
        bp.co = Vector(pt)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    for bp in sp.bezier_points:
        if bp.co.z < radius + 0.03:
            bp.co.z = radius + 0.03
    ob = D.objects.new(name, cu)
    ob.data.materials.append(get_mat(mat))
    col.objects.link(ob)
    return ob


def catmull(points, step=1.5):
    """Sampling Catmull-Rom untuk jalur bundel kabel."""
    P = [Vector(p) for p in points]
    P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        n = max(2, int((p2 - p1).length / step))
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2])
    return out


def bundle_paths(center_pts, offsets, step=2.0):
    """Jalur paralel (pita/bundel) di sekitar garis tengah, offset horizontal."""
    C = catmull(center_pts, step)
    res = [[] for _ in offsets]
    for i, c in enumerate(C):
        t = (C[min(i + 1, len(C) - 1)] - C[max(i - 1, 0)])
        t.z = 0
        if t.length < 1e-6:
            t = Vector((1, 0, 0))
        side = Vector((-t.y, t.x, 0)).normalized()
        for k, o in enumerate(offsets):
            res[k].append(c + side * o)
    return res


def thin(pts, every=3):
    return [pts[0]] + pts[1:-1:every] + [pts[-1]]


def lead_into_hole(wparts, perf_xy, color_mat, col_solder, wire_r=0.55):
    """Ujung kawat (timah) masuk lubang perfboard + solder di bawah."""
    x, y = perf_xy
    wparts.cyl(0.32, 0.32, T + 2.6, (x, y, PERF_Z + (T + 0.8) / 2 - 0.5), m="Mat_Solder_Tin", segs=10)
    mark_hole(x, y)


def W(chain, local):
    return (mat_of(*chain) @ Vector(local))


def build_wiring(col):
    leads = Part("Wire_Leads_Solder", col, None)
    objs = []
    PZ = PERF_Z
    top = PZ + T

    def hole_top(x, y, h=0.9):
        return Vector((x, y, top + h))

    def into(x, y, hops=3.5):
        return [Vector((x, y, top + hops)), Vector((x, y, top + 0.9))]

    # ---- Baterai -> TP4056 (merah B+, hitam B-) ----
    bat_ex = {k: W([BAT_T], (13.6, y, 3.75)) for k, y in BAT_WIRE_Y.items()}
    tp_pad = {k: W([TP_T], (x, y, 1.3)) for k, (x, y) in TP_PADS.items()}
    for key, mat, pad in (("red", "Mat_Wire_Red", "B+"), ("black", "Mat_Wire_Black", "B-")):
        a = bat_ex[key]
        b = tp_pad[pad]
        off = 0.0 if key == "red" else -1.5
        pts = [a, a + Vector((0, 3.5, -1.0)), Vector((a.x + 4 + off, a.y + 12, 0.6)), Vector((b.x - 7 + off, b.y - 14, 0.6)),
               b + Vector((-0.6, -4.5, 0.0)), b + Vector((0, -0.8, 0.7)), b + Vector((0, 0, 0.5))]
        objs.append(wire(col, f"Wire_Bat_{'Pos' if key == 'red' else 'Neg'}", pts, 0.55, mat))
        leads.sphere(0.95, b[:], (1.2, 1.2, 0.55), m="Mat_Solder_Tin", seg=12)

    # ---- TP4056 OUT- (hitam) -> GND perfboard (melintas di atas kabel baterai) ----
    gnd_xy = (HX(0), HY(27))
    a = tp_pad["OUT-"]
    pts = [a + Vector((0, 0, 0.5)), a + Vector((-0.5, -3.0, 1.8)), Vector((-70.5, 17.5, 3.0)), Vector((-63.0, 14.5, 0.6)),
           Vector((-50.0, 19.0, 0.6)), Vector((-41.0, 26.0, 2.1)), Vector((-36.0, 30.5, 3.8)),
           Vector((gnd_xy[0] - 3.5, gnd_xy[1] + 0.5, top + 4.0))] + into(*gnd_xy)
    objs.append(wire(col, "Wire_TP_OUTneg_GND", pts, 0.6, "Mat_Wire_Black"))
    leads.sphere(0.95, a[:], (1.2, 1.2, 0.55), m="Mat_Solder_Tin", seg=12)
    lead_into_hole(leads, gnd_xy, None, None)

    # ---- TP4056 OUT+ (putih) -> saklar lug 1 ----
    SWM = Matrix.Translation(SW_LOC) @ switch_matrix().to_4x4()
    lug1 = SWM @ Vector(SW_LUG_LOCAL[0])
    lug2 = SWM @ Vector(SW_LUG_LOCAL[1])
    a = tp_pad["OUT+"]
    pts = [a + Vector((0, 0, 0.5)), a + Vector((1.5, -2.5, 0.6)), Vector((-56.5, 31.0, 0.6)), Vector((-55.0, 44.0, 0.6)),
           Vector((-53.6, 56.0, 0.6)), Vector((lug2.x + 1.3, lug2.y - 2.6, 1.6)), Vector((lug2.x + 0.6, lug2.y - 0.9, lug2.z - 0.7)),
           lug2 + Vector((0.0, 0, 0.3))]
    objs.append(wire(col, "Wire_TP_OUTpos_Switch", pts, 0.6, "Mat_Wire_White"))
    leads.sphere(0.95, a[:], (1.2, 1.2, 0.55), m="Mat_Solder_Tin", seg=12)
    leads.sphere(0.9, lug2[:], (1.3, 1.0, 0.8), m="Mat_Solder_Tin", seg=12)

    # ---- Saklar lug 1 (merah) -> ESP32 VIN/5V (lewat celah baterai-perfboard) ----
    vx, vy = esp_pin_perf(-1, "5V")
    v5 = (vx - PITCH, vy)
    pts = [lug1 + Vector((0.0, 0, 0.3)), Vector((lug1.x + 2.0, lug1.y + 0.5, lug1.z - 0.8)), Vector((-48.5, 66.0, 0.6)),
           Vector((-46.0, 50.0, 0.6)), Vector((-44.5, 38.0, 0.6)), Vector((-37.3, 20.0, 0.6)), Vector((-37.3, -20.0, 0.6)),
           Vector((-36.8, -42.0, 0.6)), Vector((-28.0, -47.8, 0.6)), Vector((v5[0] - 4.0, v5[1] - 5.5, top + 2.6))] + into(*v5, 3.0)
    objs.append(wire(col, "Wire_Switch_ESP32_VIN", pts, 0.6, "Mat_Wire_Red"))
    leads.sphere(0.9, lug1[:], (1.3, 1.0, 0.8), m="Mat_Solder_Tin", seg=12)
    lead_into_hole(leads, v5, None, None)

    # ---- ADS1115 A0..A2 -> output OPA (kawat biru di atas board, lewat kiri ESP32) ----
    for k, (lab, n) in enumerate((("A0", 0), ("A1", 1), ("A2", 2))):
        ax, ay = ads_pin_perf(lab)
        s = (ax + PITCH, ay)
        e = (OPA_X[n] - 3.81, HY(23))
        lane_y = 15.0 + k * 1.2
        xl = -12.6 + (2 - k) * 1.15
        zl = top + 1.6 if e[0] > xl else top + 3.9      # kawat ke kiri melintas di atas kawat lain
        pts = [hole_top(*s, 0.9), Vector((s[0] + 0.6, s[1] + 0.6, top + 2.4)), Vector((xl, ay + 3.0, top + 1.6)),
               Vector((xl, lane_y - 3.0, top + 1.5)), Vector((xl + (1.5 if e[0] > xl else -1.5), lane_y, zl))]
        pts += [Vector((e[0] + (-2.0 if e[0] > xl else 2.0), lane_y + 0.6, zl + 0.2)), Vector((e[0], e[1] - 1.2, top + 2.6)), hole_top(*e, 0.9)]
        objs.append(wire(col, f"Wire_ADS_{lab}_OPA{n + 1}", pts, 0.5, "Mat_Wire_Blue"))
        lead_into_hole(leads, s, None, None)
        lead_into_hole(leads, e, None, None)

    # ---- Jumper putih (3V3 rail) ----
    a3 = esp_pin_perf(-1, "3V3")
    s = (HX(0), HY(22))
    e = (a3[0] - PITCH, a3[1])
    pts = [hole_top(*s), Vector((s[0] - 1.2, s[1] - 2.0, top + 3.0)), Vector((-31.0, 14.0, top + 3.5)), Vector((-27.0, 9.5, top + 3.2)),
           Vector((-15.0, 11.5, top + 3.0)), Vector((e[0] - 1.5, e[1] + 0.8, top + 2.0)), hole_top(*e)]
    objs.append(wire(col, "Wire_Jumper_3V3_A", pts, 0.55, "Mat_Wire_White"))
    lead_into_hole(leads, s, None, None); lead_into_hole(leads, e, None, None)
    s2, e2 = (HX(10), HY(23)), (HX(19), HY(23))
    pts = [hole_top(*s2), Vector((s2[0] + 0.5, s2[1] - 3.0, top + 4.0)), Vector((4.0, 15.5, top + 4.8)),
           Vector((13.0, 16.5, top + 4.5)), Vector((e2[0] - 0.8, e2[1] - 2.5, top + 3.2)), hole_top(*e2)]
    objs.append(wire(col, "Wire_Jumper_3V3_B", pts, 0.55, "Mat_Wire_White"))
    lead_into_hole(leads, s2, None, None); lead_into_hole(leads, e2, None, None)

    # ---- Jumper hitam GND (OPA -> ESP GND kanan atas) ----
    g = esp_pin_perf(1, "GND")
    e = (g[0] + PITCH, g[1])
    s = (HX(22), HY(22))
    pts = [hole_top(*s), Vector((s[0] - 0.8, s[1] - 2.5, top + 3.0)), Vector((24.0, 13.5, top + 3.2)),
           Vector((e[0] + 0.6, e[1] + 1.6, top + 2.4)), hole_top(*e)]
    objs.append(wire(col, "Wire_Jumper_GND", pts, 0.55, "Mat_Wire_Black"))
    lead_into_hole(leads, s, None, None); lead_into_hole(leads, e, None, None)

    # ---- 3 bundel kabel adapter SPE (kuning/hitam/merah) -> modul OPA ----
    # adapter 1 -> OPA3 (lintasan terluar), adapter 2 -> OPA2, adapter 3 -> OPA1
    mats = ["Mat_Wire_Yellow", "Mat_Wire_Black", "Mat_Wire_Red"]
    plan = {0: 2, 1: 1, 2: 0}
    lanes = {0: (58.0, 108.0), 1: (44.0, 96.0), 2: (30.0, 84.0)}
    for a_i, opa_i in plan.items():
        chain = [ADAPTER_T[a_i]]
        exits = [W(chain, ADAPTER_WIRE_EXIT[k]) for k in range(3)]
        start = (exits[0] + exits[1] + exits[2]) / 3
        cx = OPA_X[opa_i]
        lx, ly = lanes[a_i]
        targets = [(cx - 3.81, HY(28)), (cx - 1.27, HY(28)), (cx + 1.27, HY(28))]
        tgt_c = Vector((cx - 1.27, HY(28), 0))
        center = [start, start + Vector((8, -0.5, -2.6)), Vector((start.x + 30, ly + 1.0, 0.55)),
                  Vector((lx - 6, ly - 1.0, 0.55)), Vector((lx + 4, ly - 14.0, 0.55)), Vector((lx - 2, 52.0, 0.55)),
                  Vector((tgt_c.x + 6, 46.5, top + 4.0)), Vector((tgt_c.x + 1.5, 39.5, top + 5.5))]
        paths = bundle_paths(center, [1.25, 0.0, -1.25], step=2.5)
        for k in range(3):
            p = thin(paths[k], 2)
            p[0] = exits[k]
            tx, ty = targets[k]
            p += [Vector((tx, ty + 1.2, top + 3.2)), Vector((tx, ty, top + 0.9))]
            objs.append(wire(col, f"Wire_SPE{a_i + 1}_{['Y', 'K', 'R'][k]}_OPA{opa_i + 1}", p, 0.5, mats[k]))
            lead_into_hole(leads, targets[k], None, None)

    # ---- Pita 4 kabel ESP32 -> OLED (merah VCC, hitam GND, kuning SCL, oranye SDA) ----
    hx, hy = OLED_HDR
    hdr_top = [Vector((hx, hy + (k - 1.5) * PITCH, PZ + T + 2.5 + 14.0)) for k in range(4)]
    oled_root = D.objects["OLED_096_Root"]
    Mo = Matrix.Translation(oled_root.location) @ oled_root.rotation_euler.to_matrix().to_4x4()
    oled_end = [Mo @ Vector(((k - 1.5) * PITCH, 12.2, -16.5)) for k in range(4)]
    down = (Mo.to_3x3() @ Vector((0, 0, -1))).normalized()
    ribbon_mats = ["Mat_Wire_Red", "Mat_Wire_Black", "Mat_Wire_Yellow", "Mat_Wire_Orange"]
    oc = sum(oled_end, Vector()) / 4
    center = [Vector((hx, hy, PZ + T + 2.5 + 14.0)) + Vector((0, 0, 4.0)), Vector((hx + 6, hy, PZ + T + 22.0)),
              Vector((hx + 16, hy - 4, 9.0)), Vector((52.0, -12.0, 0.6)), Vector((55.0, -45.0, 0.6)),
              Vector((40.0, -80.0, 0.6)), Vector((oc.x + 22.0, oc.y + 6.0, 0.6)), Vector((oc.x + 11.0, oc.y, 0.6))]
    paths = bundle_paths(center, [-1.9, -0.63, 0.63, 1.9], step=2.5)
    for k in range(4):
        p = thin(paths[k], 2)
        p[0] = hdr_top[k] + Vector((0, 0, 1.5))
        p.insert(0, hdr_top[k] - Vector((0, 0, 0.5)))
        p += [oled_end[k] + down * 2.6, oled_end[k] + down * 0.2]
        objs.append(wire(col, f"Wire_OLED_{['VCC', 'GND', 'SCL', 'SDA'][k]}", p, 0.55, ribbon_mats[k]))
    # ---- Koaksial RF: IPEX ESP32 -> RP-SMA ----
    ipex = Vector((ESP_T[0][0] + 5.4 + 1.6, ESP_T[0][1] + 25.5 + 1.6, PZ + ESP_T[0][2] + 3.4))
    d = Vector((math.cos(RAD(ANT_DIR_DEG + 90)), math.sin(RAD(ANT_DIR_DEG + 90)), 0))
    sma_back = Vector(ANT_ROOT) - d * 16.0
    pts = [ipex, ipex + Vector((2.5, 2.5, 0.3)), Vector((24.0, 22.0, 17.0)), Vector((36.0, 30.0, 9.0)),
           Vector((48.0, 38.0, 0.7)), Vector((70.0, 40.0, 0.7)), Vector((78.0, 22.0, 0.9)),
           sma_back - d * 6.0 + Vector((0, 0, -1.8)), sma_back - d * 0.5]
    objs.append(wire(col, "Coax_RG113_IPEX_SMA", pts, 0.6, "Mat_Wire_Black", res=24))

    # ---- Bawah perfboard: jumper berisolasi (sesuai koneksi.jpeg) ----
    bot = PZ - 0.9
    under = [("SDA", (1, "21"), "Mat_Wire_Blue"), ("SCL", (1, "22"), "Mat_Wire_Green"),
             ("GND", (-1, "GND"), "Mat_Wire_Black"), ("VDD", (-1, "3V3"), "Mat_Wire_White")]
    for k, (alab, (side, elab), m) in enumerate(under):
        ax, ay = ads_pin_perf(alab)
        s = (ax + PITCH, ay)
        ex, ey = esp_pin_perf(side, elab)
        e = (ex + side * PITCH, ey)
        mid_x = -2.0 + k * 1.6
        pts = [Vector((s[0], s[1], PZ + 0.3)), Vector((s[0] + 0.4, s[1], bot - 0.6)), Vector((s[0] + 6, s[1] + 3 + k, bot)),
               Vector((mid_x, (s[1] + e[1]) / 2 + k * 2.0, bot)), Vector((e[0] - side * 3.0, e[1] - 2.0, bot)),
               Vector((e[0], e[1], bot - 0.6)), Vector((e[0], e[1], PZ + 0.3))]
        objs.append(wire(col, f"Wire_Under_{alab}_ESP{elab}", pts, 0.55, m))
        mark_hole(*s); mark_hole(*e)
    return objs, leads


def build_bottom_solder(col, perf_root):
    p = Part("Perfboard_Bottom_Solder", col, perf_root)
    for (x, y) in sorted(USED_HOLES):
        p.cyl(0.42, 0.95, 0.75, (x, y, -0.375), m="Mat_Solder_Tin", segs=14)
    # jalur timah manual (solder trail) antara pin & lubang tetangga
    trails = []
    for lab in ADS_LABELS:
        ax, ay = ads_pin_perf(lab)
        trails.append(((ax, ay), (ax + PITCH, ay)))
    for side, lst in ((-1, ESP_LEFT), (1, ESP_RIGHT)):
        for lab in ("3V3", "5V", "GND", "21", "22"):
            if lab in lst:
                x, y = esp_pin_perf(side, lab)
                trails.append(((x, y), (x + side * PITCH, y)))
    for cx in OPA_X:
        trails.append(((cx - 3.81, HY(28)), (cx - 3.81, HY(27))))
        trails.append(((cx + 1.27, HY(28)), (cx + 3.81, HY(28))))
        trails.append(((cx + 3.81, HY(28)), (cx + 3.81, HY(27))))
        trails.append(((cx - 3.81, HY(23)), (cx - 3.81, HY(24))))
    for (a, b) in trails:
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        Lg = math.hypot(b[0] - a[0], b[1] - a[1])
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        p.box((Lg + 1.2, 1.25, 0.6), (mx, my, -0.3), (0, 0, ang), m="Mat_Solder_Tin", bevel=0.28, seg=3)
    return [p]


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    USED_HOLES.clear()
    root_col = reset_root()
    for k in MATS:
        get_mat(k)
    add_micro_bump("Mat_Battery_Silver", scale=0.35, strength=0.08)
    add_micro_bump("Mat_Shield_Can", scale=2.5, strength=0.02)

    c_perf = sub_col(root_col, "EL_Perfboard")
    c_esp = sub_col(root_col, "EL_ESP32")
    c_ads = sub_col(root_col, "EL_ADS1115")
    c_opa = sub_col(root_col, "EL_OPA_Modules")
    c_tp = sub_col(root_col, "EL_TP4056")
    c_bat = sub_col(root_col, "EL_Battery")
    c_sw = sub_col(root_col, "EL_Switch")
    c_oled = sub_col(root_col, "EL_OLED")
    c_ant = sub_col(root_col, "EL_Antenna")
    c_ad = sub_col(root_col, "EL_SPE_Adapters")
    c_spe = sub_col(root_col, "EL_SPE_Strips")
    c_w = sub_col(root_col, "EL_Wiring")

    perf_root = empty("Perfboard_Root", c_perf, PERF_T[0], PERF_T[1], size=10)
    parts = []
    parts += build_perfboard(c_perf, perf_root)
    esp_parts, _ = build_esp32(c_esp, perf_root); parts += esp_parts
    ads_parts, _ = build_ads1115(c_ads, perf_root); parts += ads_parts
    opa_parts, _ = build_opa(c_opa, perf_root); parts += opa_parts
    parts += build_oled_header(c_perf, perf_root)
    tp_parts, _ = build_tp4056(c_tp, None); parts += tp_parts
    bat_parts, _ = build_battery(c_bat); parts += bat_parts
    sw_parts, _ = build_switch(c_sw); parts += sw_parts
    oled_parts, _ = build_oled(c_oled); parts += oled_parts
    ant_parts, _ = build_antenna(c_ant); parts += ant_parts
    ad_parts, _ = build_adapters(c_ad); parts += ad_parts
    for i, (loc, rot) in enumerate(SPE_LOOSE):
        sp, _ = build_spe_strip(c_spe, f"SPE_Strip_{i + 1}", loc, rot); parts += sp
    bpy.context.view_layer.update()
    wobjs, leads = build_wiring(c_w)
    parts.append(leads)
    parts += build_bottom_solder(c_perf, perf_root)

    bake_texts(parts)
    for p in parts:
        p.bake()
    bpy.context.view_layer.update()
    n_obj = len([o for o in root_col.all_objects])
    print("built objects:", n_obj, "holes used:", len(USED_HOLES))


if __name__ == "__main__":
    main()
