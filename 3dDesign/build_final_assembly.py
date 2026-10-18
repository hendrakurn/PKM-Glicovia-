"""
PKM-GLICOVIA (Pimnas) - Final assembly casing + elektronika + wiring.

Jalankan di Blender (MCP / Text Editor):
    exec(open(".../build_final_assembly.py").read()); build_all()
Hasil: pkm_glicovia_final_assembly.blend (pkm_casing_final_Pimnas.blend & rangkaian_elektronika_pkm.blend tidak diubah).

Konvensi: 1 BU = 1 mm. Casing bodi X[-45,45] Y[-65,65] Z[0,50]; permukaan atas tutup bawah = Z 0
(pelat tutup 2.2 mm berada di Z[-2.2,0], bibirnya masuk ke dalam dinding).

Layout (diturunkan dari pemindaian lubang casing + ukuran komponen hasil rekonstruksi foto):
  - Perfboard 70x90 (ukuran nyata di foto) di atas 4 standoff M3x5 kuningan, bawah papan Z=5.0.
  - TP4056 di atas 2 spacer nilon, USB-C sejajar lubang dinding belakang (X -12.5, Z 15).
  - Baterai berdiri di dinding kanan (ruang di samping papan 70 mm tidak cukup untuk baterai mendatar).
  - Saklar KCD11 pada insert bezel di lubang dinding kanan (lubang casing 13x19 dibuat untuk KCD1).
  - OLED disekrup M2 ke 4 tiang dudukan bawaan atap casing, pusat PCB (0, 15.2), atas PCB Z 45.5.
  - 3 adapter SPE biru di DALAM casing: mulut strip menempel di slot dinding depan (Y -63.45), badan
    berbaring di sleeve bawaan casing ke arah +Y; adapter 1/2/3 = slot kiri/tengah/kanan (X -20/0/+20).
  - Rumah sensor eksternal Adapter_V1_Base/Lid (asli dari file casing) di LUAR dinding depan; kantong
    Base dilebarkan ke 10.3 mm agar muat strip SPE 10 mm, pasak Lid di jalur strip dipangkas. Lubang
    sumur sampel Lid (Ø4.5, Y -85) sepusat dengan elektroda kerja tiap strip.
  - Antena RP-SMA seluruhnya di dalam casing: konektor tegak di klip cetak dinding belakang, whip
    ditekuk 90 deg dan berbaring di bawah atap ke arah -Y (dinding belakang tidak dilubangi).
"""
import bpy
import bmesh
import math
from collections import defaultdict
from mathutils import Vector, Matrix, Euler
from mathutils.bvhtree import BVHTree

D = bpy.data
DIR = "/home/hendra/project/PKM-Glicovia-/3dDesign"
CASING_BLEND = DIR + "/pkm_casing_final_Pimnas.blend"
EL_BLEND = DIR + "/rangkaian_elektronika_pkm.blend"
OUT_BLEND = DIR + "/pkm_glicovia_final_assembly.blend"
SCREEN_IMG = DIR + "/textures/oled_screen_glicovia_px.png"

# ---------------------------------------------------------------------------
# Layout (mm, koordinat dunia casing)
# ---------------------------------------------------------------------------
PERF_LOC = (-6.0, 4.0, 5.0)                    # Perfboard_Root = sisi bawah papan
TP_LOC = (-12.5, 48.4, 12.145)                 # USB-C center Z 14.975 = pusat lubang belakang
BAT_LOC, BAT_ROT = (33.76, -17.65, 17.0), (0, 90, 0)
SW_LOC, SW_ROT = (44.97, 14.975, 25.0), (0, 90, 0)
OLED_LOC = (0.0, 15.2, 44.26)                  # atas PCB OLED = 45.50 = ujung 4 tiang dudukan di atap
OLED_GLASS_SHIFT = 2.57                        # kaca dipusatkan di antara baris lubang PCB (sesuai foto)
OLED_HOLES = [(-11.85, -11.96), (11.85, -11.96), (-11.85, 11.96), (11.85, 11.96)]   # antara lubang PCB & tiang atap
ANT_LOC, ANT_ROT = (21.0, 52.0, 21.0), (0, 0, 0)    # konektor tegak; whip tertekuk berbaring ke -Y di Z 42.4
ANT_HINGE_Z = 21.4                             # pivot knuckle (lokal antena)
# Adapter biru (lokal +X = sumbu panjang, mulut strip di x=-22, ujung JST di x=+32.25)
ADAPTER_X = {"SPE_Adapter_1_Root": -20.0, "SPE_Adapter_2_Root": 0.0, "SPE_Adapter_3_Root": 20.0}
ADAPTER_MOUTH_X = -22.0                        # muka mulut adapter (lokal)
ADAPTER_MOUTH_Y = -61.95                       # muka mulut di belakang bibir slot dalam (Y -62.0, Z 11..12)
ADAPTER_Z = 11.2                               # duduk di rel sleeve (Z 10.9 di mulut), atas 17.5 < PCB ESP32 17.6
ADAPTER_YAW = {"SPE_Adapter_1_Root": 1.0, "SPE_Adapter_2_Root": 0.0, "SPE_Adapter_3_Root": 0.0}
STRIP_FOR_ADAPTER = {"SPE_Adapter_1_Root": "SPE_Strip_1_Root", "SPE_Adapter_2_Root": "SPE_Strip_2_Root",
                     "SPE_Adapter_3_Root": "SPE_Strip_3_Root"}
# Strip SPE di kantong Adapter_V1_Base; pusat elektroda kerja (WE) tepat di bawah lubang sumur Lid
WE_Y = -85.0
STRIP_Z = 12.69                                # lantai kantong Adapter_V1_Base
V1_POCKET_HALF_W = 5.15                        # kantong 10.3 mm untuk strip 10.0 mm
V1_POCKET_Y = (-93.5, -63.3)                   # ujung kantong (stopper Base di Y -93.5..-95)
LID_HOLES = [(-33.5, -54.22, -1.2), (33.5, -54.22, -1.2), (-33.5, 53.5, 0.0), (33.5, 53.5, 0.0)]
ROOF_IN = 48.03
LID_LOC = (0.0, 0.0, -2.2)
CUT_Z = 36.0                                   # tinggi potongan cutaway (render internal)

ON_BOARD_WIRES = ("Wire_ADS_", "Wire_Jumper_", "Wire_Under_")


def TM(loc=(0, 0, 0), rot=(0, 0, 0)):
    return Matrix.Translation(Vector(loc)) @ Euler([math.radians(a) for a in rot], 'XYZ').to_matrix().to_4x4()


# ---------------------------------------------------------------------------
# Material helpers
# ---------------------------------------------------------------------------
def principled(mat):
    return next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def new_mat(name, color, rough=0.5, metal=0.0, emission=None, estr=0.0, alpha=1.0, coat=0.0):
    m = D.materials.get(name) or D.materials.new(name)
    m.use_nodes = True
    b = principled(m)
    b.inputs['Base Color'].default_value = (*color, 1.0)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if coat:
        b.inputs['Coat Weight'].default_value = coat
    if emission:
        b.inputs['Emission Color'].default_value = (*emission, 1.0)
        b.inputs['Emission Strength'].default_value = estr
    if alpha < 1.0:
        b.inputs['Alpha'].default_value = alpha
    m.diffuse_color = (*color, alpha)
    return m


def mat(name):
    return D.materials[name]


# ---------------------------------------------------------------------------
# Mesh helpers (bmesh)
# ---------------------------------------------------------------------------
class Part:
    """Kumpulkan primitif ke satu mesh multi-material."""

    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.mats = []

    def _mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def _tag(self, geom, m):
        mi = self._mi(m)
        for f in [g for g in geom if isinstance(g, bmesh.types.BMFace)]:
            f.material_index = mi

    def box(self, size, loc, m, rot=(0, 0, 0)):
        r = bmesh.ops.create_cube(self.bm, size=1.0, matrix=TM(loc, rot) @ Matrix.Diagonal((*size, 1.0)))
        faces = list({f for v in r['verts'] for f in v.link_faces})
        self._tag(faces, m)

    def box_minmax(self, lo, hi, m):
        size = [hi[i] - lo[i] for i in range(3)]
        loc = [(hi[i] + lo[i]) / 2 for i in range(3)]
        self.box(size, loc, m)

    def cyl(self, r1, r2, depth, loc, m, rot=(0, 0, 0), segs=24):
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r1, radius2=r2,
                                    depth=depth, matrix=TM(loc, rot))
        faces = list({f for v in res['verts'] for f in v.link_faces})
        self._tag(faces, m)

    def tube(self, r_in, r_out, z0, z1, loc, m, rot=(0, 0, 0), segs=24):
        M = TM(loc, rot)
        bm = self.bm
        ring = []
        for z in (z0, z1):
            for r in (r_out, r_in):
                ring.append([bm.verts.new(M @ Vector((r * math.cos(2 * math.pi * i / segs),
                                                      r * math.sin(2 * math.pi * i / segs), z))) for i in range(segs)])
        o0, i0, o1, i1 = ring
        mi = self._mi(m)
        for i in range(segs):
            j = (i + 1) % segs
            for quad in ((o0[i], o0[j], o1[j], o1[i]), (i0[j], i0[i], i1[i], i1[j]),
                         (o0[j], o0[i], i0[i], i0[j]), (o1[i], o1[j], i1[j], i1[i])):
                bm.faces.new(quad).material_index = mi

    def prism(self, poly2d, z0, z1, M, m):
        """Prisma dari poligon 2D (xy) diekstrusi z0..z1, ditransformasi M."""
        bm = self.bm
        bot = [bm.verts.new(M @ Vector((x, y, z0))) for x, y in poly2d]
        top = [bm.verts.new(M @ Vector((x, y, z1))) for x, y in poly2d]
        mi = self._mi(m)
        bm.faces.new(list(reversed(bot))).material_index = mi
        bm.faces.new(top).material_index = mi
        n = len(poly2d)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((bot[i], bot[j], top[j], top[i])).material_index = mi

    def build(self, col, parent=None, smooth_angle=35.0, bevel=0.0):
        me = D.meshes.new(self.name)
        bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=1e-5)
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        for p in me.polygons:
            p.use_smooth = True
        ob = D.objects.new(self.name, me)
        col.objects.link(ob)
        set_sharp(me, smooth_angle)
        if bevel > 0:
            mod = ob.modifiers.new("Bevel", 'BEVEL')
            mod.width = bevel
            mod.segments = 2
            mod.limit_method = 'ANGLE'
            mod.harden_normals = True
        if parent:
            ob.parent = parent
            ob.matrix_parent_inverse = parent.matrix_world.inverted()
        return ob


def set_sharp(me, angle_deg):
    bm = bmesh.new()
    bm.from_mesh(me)
    lim = math.radians(angle_deg)
    for e in bm.edges:
        e.smooth = not (len(e.link_faces) == 2 and e.calc_face_angle(0.0) > lim) and len(e.link_faces) == 2
    bm.to_mesh(me)
    bm.free()


def world_bvh(ob, dg):
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    mw = ob.matrix_world
    verts = [mw @ v.co for v in me.vertices]
    polys = [tuple(p.vertices) for p in me.polygons]
    ev.to_mesh_clear()
    if not polys:
        return None, []
    return BVHTree.FromPolygons(verts, polys, epsilon=0.0), [sum((verts[i] for i in p), Vector()) / len(p) for p in polys]


def get_col(name, parent=None):
    c = D.collections.get(name)
    if c is None:
        c = D.collections.new(name)
    if parent is not None and c.name not in [x.name for x in parent.children]:
        parent.children.link(c)
    return c


def move_to_col(ob, col):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)


# ---------------------------------------------------------------------------
# 1. Buka casing, bersihkan, append elektronika
# ---------------------------------------------------------------------------
def load_sources():
    bpy.ops.wm.open_mainfile(filepath=CASING_BLEND)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 0.001
    sc.unit_settings.length_unit = 'MILLIMETERS'
    # rumah sensor eksternal asli dipertahankan (pindah ke PKM_Casing)
    ccol = D.collections["PKM_Casing"]
    for n in ("Adapter_V1_Base", "Adapter_V1_Lid"):
        move_to_col(D.objects[n], ccol)
        D.objects[n].location = (0.0, 0.0, 0.0)     # file casing menyimpan offset Z +2; spek: Base Z 11..13.2
    # modul OLED sederhana, kamera/sun lama -> diganti versi detail
    for cname in ("OLED_096_Module", "Sensor_Adapters", "Studio"):
        c = D.collections.get(cname)
        if c is None:
            continue
        for ob in list(c.all_objects):
            D.objects.remove(ob, do_unlink=True)
        for ch in list(c.children_recursive):
            D.collections.remove(ch)
        D.collections.remove(c)
    for ob in list(D.objects):
        if ob.name.startswith(("Header_Pin_", "Pin_Tip_", "Solder_Fillet_", "OLED_", "Tab_Anchor")):
            D.objects.remove(ob, do_unlink=True)
    with D.libraries.load(EL_BLEND, link=False) as (src, dst):
        dst.collections = ["PKM_Electronics_Assembly"]
    el = dst.collections[0]
    sc.collection.children.link(el)
    el.name = "PKM_Electronics"
    bpy.context.view_layer.update()          # matrix_world objek hasil append baru valid setelah update
    return el


# ---------------------------------------------------------------------------
# 2. Catat titik ujung kabel antar-komponen di frame lokal pemiliknya
# ---------------------------------------------------------------------------
def component_roots():
    return [o for o in D.objects if o.type == 'EMPTY' and o.name.endswith("_Root")]


def owner_of(p, roots, tol=1.5):
    best = None
    for r in roots:
        inv = r.matrix_world.inverted()
        lp = inv @ p
        for ob in r.children_recursive:
            if ob.type != 'MESH':
                continue
            bb = [inv @ ob.matrix_world @ Vector(c) for c in ob.bound_box]
            lo = [min(q[i] for q in bb) - tol for i in range(3)]
            hi = [max(q[i] for q in bb) + tol for i in range(3)]
            if all(lo[i] <= lp[i] <= hi[i] for i in range(3)):
                vol = (hi[0] - lo[0]) * (hi[1] - lo[1]) * (hi[2] - lo[2])
                # pilih komponen terkecil yang memuat titik (ujung pada modul, bukan papan)
                if best is None or vol < best[1]:
                    best = (r, vol)
    if best:
        return best[0]
    # cadangan: root dengan mesh terdekat (jarak ke kotak pembatas)
    near = None
    for r in roots:
        for ob in r.children_recursive:
            if ob.type != 'MESH':
                continue
            bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
            lo = Vector([min(q[i] for q in bb) for i in range(3)])
            hi = Vector([max(q[i] for q in bb) for i in range(3)])
            d = (Vector([min(max(p[i], lo[i]), hi[i]) for i in range(3)]) - p).length
            if near is None or d < near[1]:
                near = (r, d)
    return near[0] if near else None


WIRE_SPEC = {}      # nama -> dict(start=(root, lp, ldir), end=(...), radius, mat)


def record_harness(el):
    wcol = D.collections["EL_Wiring"]
    roots = component_roots()
    perf = D.objects["Perfboard_Root"]
    for ob in list(wcol.objects):
        if ob.type == 'CURVE' and ob.name.startswith(ON_BOARD_WIRES):
            ob.parent = perf
            ob.matrix_parent_inverse = perf.matrix_world.inverted()
            continue
        if ob.type != 'CURVE':
            continue
        sp = ob.data.splines[0]
        pts = [ob.matrix_world @ bp.co for bp in sp.bezier_points]
        name = ob.name
        if name.startswith("Wire_SPE"):
            # adapter k (slot kiri/tengah/kanan) -> modul OPA k di sisi yang sama (tanpa kabel menyilang)
            _w, spe, col, opa = name.split("_")
            src_opa = D.objects[opa.replace("OPA", "OPA_Module_") + "_Root"]
            name = "%s_%s_%s_OPA%s" % (_w, spe, col, spe[-1])
        ends = []
        for p, q in ((pts[0], pts[1]), (pts[-1], pts[-2])):
            r = owner_of(p, roots)
            if name.startswith("Wire_SPE") and p is pts[-1]:
                r = src_opa
            if name.startswith("Wire_SPE") and p is pts[0]:
                r = D.objects["SPE_Adapter_%s_Root" % spe[-1]]
            inv = r.matrix_world.inverted()
            d = (q - p).normalized()
            ends.append([r.name, inv @ p, (inv.to_3x3() @ d).normalized()])
        if name.startswith("Wire_SPE"):
            ends[1][0] = "OPA_Module_%s_Root" % spe[-1]       # titik lokal identik di tiap modul OPA
        WIRE_SPEC[name] = dict(start=tuple(ends[0]), end=tuple(ends[1]), radius=ob.data.bevel_depth,
                               mat=ob.data.materials[0].name)
        D.objects.remove(ob, do_unlink=True)


def split_leads_solder():
    """Pecah mesh Wire_Leads_Solder per pulau -> parent ke komponen pemiliknya."""
    ob = D.objects.get("Wire_Leads_Solder")
    if ob is None:
        return []
    roots = component_roots()
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    seen = set()
    groups = defaultdict(list)
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, isl = [v], []
        seen.add(v.index)
        while stack:
            a = stack.pop()
            isl.append(a.index)
            for e in a.link_edges:
                b = e.other_vert(a)
                if b.index not in seen:
                    seen.add(b.index)
                    stack.append(b)
        c = sum((ob.matrix_world @ bm.verts[i].co for i in isl), Vector()) / len(isl)
        r = owner_of(c, roots, tol=2.5) or D.objects["Perfboard_Root"]
        groups[r.name].extend(isl)
    bm.free()
    out = []
    for rname, idx in groups.items():
        keep = set(idx)
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.index not in keep], context='VERTS')
        nm = D.meshes.new("Leads_Solder_" + rname.replace("_Root", ""))
        bm.to_mesh(nm)
        bm.free()
        for m in me.materials:
            nm.materials.append(m)
        no = D.objects.new(nm.name, nm)
        no.matrix_world = ob.matrix_world
        root = D.objects[rname]
        D.collections[root.users_collection[0].name].objects.link(no)
        no.parent = root
        no.matrix_parent_inverse = root.matrix_world.inverted()
        out.append(no)
    D.objects.remove(ob, do_unlink=True)
    return out


# ---------------------------------------------------------------------------
# 3. Tempatkan komponen
# ---------------------------------------------------------------------------
def place(name, loc, rot=(0, 0, 0)):
    ob = D.objects[name]
    ob.parent = None
    ob.matrix_world = TM(loc, rot)
    return ob


def place_components():
    lid = D.objects["PKM_Casing_Lid"]
    lid.location = LID_LOC                              # pelat tutup Z[-2.2, 0], bibir masuk ke dalam dinding
    place("Perfboard_Root", PERF_LOC)
    place("TP4056_Root", TP_LOC)
    place("LiPo_Battery_Root", BAT_LOC, BAT_ROT)
    place("Switch_KCD11_Root", SW_LOC, SW_ROT)
    place("OLED_096_Root", OLED_LOC)
    place("Antenna_RPSMA_Root", ANT_LOC, ANT_ROT)
    # strip ke-3: duplikat strip 1
    if "SPE_Strip_3_Root" not in D.objects:
        r1 = D.objects["SPE_Strip_1_Root"]
        s1 = D.objects["SPE_Strip_1"]
        r3 = r1.copy()
        r3.name = "SPE_Strip_3_Root"
        D.collections["EL_SPE_Strips"].objects.link(r3)
        s3 = s1.copy()
        s3.name = "SPE_Strip_3"
        D.collections["EL_SPE_Strips"].objects.link(s3)
        s3.parent = r3
    wx, wy = strip_we_local()
    for rname, x in ADAPTER_X.items():
        place_adapter(rname, x, ADAPTER_Z, ADAPTER_YAW[rname])
        # strip rot 90: lokal (lx, ly) -> dunia (-ly, lx); WE dunia = (x, WE_Y), sisi terminal ke +Y
        place(STRIP_FOR_ADAPTER[rname], (x + wy, WE_Y - wx, STRIP_Z), (0, 0, 90))
    # film pelindung OLED dilepas pada produk jadi
    for n in ("OLED_Protect_Film",):
        if n in D.objects:
            D.objects.remove(D.objects[n], do_unlink=True)
    if "OLED_PCB.001" in D.objects and "OLED_PCB" not in D.objects:
        D.objects["OLED_PCB.001"].name = "OLED_PCB"
    bend_antenna()


def place_adapter(rname, x, z, yaw):
    """Muka mulut adapter di (x, ADAPTER_MOUTH_Y); yaw (deg) memutar ekor ke +X di sekitar mulut."""
    rz = math.radians(90.0 - yaw)
    d = Vector((math.cos(rz), math.sin(rz), 0.0))
    root = Vector((x, ADAPTER_MOUTH_Y, z)) - d * ADAPTER_MOUTH_X
    return place(rname, tuple(root), (0, 0, 90.0 - yaw))


def strip_we_local():
    """Pusat lingkaran elektroda kerja (karbon) di frame root strip."""
    r = D.objects["SPE_Strip_1_Root"]
    ob = D.objects["SPE_Strip_1"]
    me = ob.data
    to_root = r.matrix_world.inverted() @ ob.matrix_world
    ci = next(i for i, m in enumerate(me.materials) if m.name == "Mat_SPE_Carbon")
    vs = [to_root @ me.vertices[i].co for p in me.polygons if p.material_index == ci for i in p.vertices]
    c = Vector((sum(v.x for v in vs) / len(vs), sum(v.y for v in vs) / len(vs), 0))
    for _ in range(4):                       # disk WE: verteks karbon dalam radius 2.3 mm dari pusat
        disk = [v for v in vs if (Vector((v.x, v.y, 0)) - c).length < 2.3]
        lo = Vector((min(v.x for v in disk), min(v.y for v in disk), 0))
        hi = Vector((max(v.x for v in disk), max(v.y for v in disk), 0))
        c = (lo + hi) / 2
    return c.x, c.y


def bend_antenna():
    """Tekuk whip antena 90 deg ke atas pada knuckle (rotasi lokal +X di Z=ANT_HINGE_Z)."""
    ob = D.objects["Ant_Rubber_Body"]
    if ob.get("bent"):
        return
    to_root = ob.matrix_parent_inverse @ ob.matrix_basis      # mesh -> frame root (tanpa depender update)
    back = to_root.inverted()
    R = Matrix.Translation((0, 0, ANT_HINGE_Z)) @ Matrix.Rotation(math.radians(90), 4, 'X') @ \
        Matrix.Translation((0, 0, -ANT_HINGE_Z))
    me = ob.data
    for v in me.vertices:
        lp = to_root @ v.co
        if lp.z > ANT_HINGE_Z + 0.0:
            # transisi halus 1.2 mm agar barrel knuckle tidak sobek
            t = min(1.0, (lp.z - ANT_HINGE_Z) / 1.2)
            ang = math.radians(90) * t
            Rt = Matrix.Translation((0, 0, ANT_HINGE_Z)) @ Matrix.Rotation(ang, 4, 'X') @ \
                Matrix.Translation((0, 0, -ANT_HINGE_Z))
            v.co = back @ (Rt @ lp)
    me.update()
    ob["bent"] = True


# ---------------------------------------------------------------------------
# 4. Modifikasi casing (pada file assembly saja)
# ---------------------------------------------------------------------------
def apply_modifiers(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = D.meshes.new_from_object(ev)
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    me.name = old.name
    D.meshes.remove(old)


def boolean(ob, cutter, op='DIFFERENCE', transfer=False, hole_tolerant=False):
    mod = ob.modifiers.new("Bool", 'BOOLEAN')
    mod.operation = op
    mod.solver = 'EXACT'
    mod.object = cutter
    mod.material_mode = 'TRANSFER' if transfer else 'INDEX'
    mod.use_hole_tolerant = hole_tolerant            # mesh komponen non-manifold (shell terpisah)
    apply_modifiers(ob)


def make_cutter(name, size, loc, rot=(0, 0, 0), cyl=None, m=None):
    p = Part(name)
    mm = m or new_mat("Mat_Cutter", (1, 0, 1))
    if cyl:
        p.cyl(cyl[0], cyl[0], cyl[1], loc, mm, rot, segs=48)
    else:
        p.box(size, loc, mm, rot)
    ob = p.build(bpy.context.scene.collection, smooth_angle=20)
    return ob


def modify_casing():
    main = D.objects["PKM_Casing_Main"]
    if main.get("assembly_mod"):
        return
    apply_modifiers(main)                                   # bake bevel (antena di dalam: dinding belakang utuh)
    main["assembly_mod"] = True


def build_v1_housing():
    """Adapter_V1_Base/Lid asli: kantong strip 8.5 -> 10.3 mm, pasak Lid yang jatuh di jalur strip dipangkas."""
    base, lid = D.objects["Adapter_V1_Base"], D.objects["Adapter_V1_Lid"]
    if base.get("fitted"):
        return [base, lid]
    for ob in (base, lid):
        apply_modifiers(ob)
    vm = mat("PKM_Mat_Adapter_V1")
    y0, y1 = V1_POCKET_Y
    for x in ADAPTER_X.values():
        c = make_cutter("Cut_V1_Pocket", (2 * V1_POCKET_HALF_W, y1 - y0, 1.2), (x, (y0 + y1) / 2, STRIP_Z + 0.6), m=vm)
        boolean(base, c, transfer=True)
        D.objects.remove(c, do_unlink=True)
        c = make_cutter("Cut_V1_LidChannel", (2 * V1_POCKET_HALF_W, y1 - y0, 2.0), (x, (y0 + y1) / 2, 13.2 - 1.0), m=vm)
        boolean(lid, c, transfer=True)
        D.objects.remove(c, do_unlink=True)
    base["fitted"] = True
    return [base, lid]


def cut_adapter_sockets():
    """Celah mulut adapter biru tepat seukuran strip yang dicolokkan (strip + 0.08 mm)."""
    hole = mat("Mat_Hole_Dark")
    bpy.context.view_layer.update()
    for rname, sname in STRIP_FOR_ADAPTER.items():
        ad = next(o for o in D.objects[rname].children if o.type == 'MESH' and o.name.startswith("SPE_Adapter"))
        if ad.get("socket_cut"):
            continue
        if ad.data.users > 1:
            ad.data = ad.data.copy()
        strip = next(o for o in D.objects[sname].children if o.type == 'MESH')
        vs = [strip.matrix_world @ v.co for v in strip.data.vertices]
        lo = Vector([min(v[i] for v in vs) for i in range(3)]) - Vector((0.08, 0.0, 0.08))
        hi = Vector([max(v[i] for v in vs) for i in range(3)]) + Vector((0.08, 0.1, 0.08))
        lo.y = ADAPTER_MOUTH_Y - 1.0
        c = make_cutter("Cut_Adapter_Socket", tuple(hi - lo), tuple((hi + lo) / 2), m=hole)
        boolean(ad, c, transfer=True, hole_tolerant=True)
        D.objects.remove(c, do_unlink=True)
        ad["socket_cut"] = True


def build_casing_addons(ccol):
    green = mat("PKM_Mat_CasingGreen")
    # --- boss sekrup tutup (4x, menyatu ke atap) ---
    p = Part("Casing_Lid_Screw_Bosses")
    for (x, y, z0) in LID_HOLES:
        p.tube(1.25, 3.5, z0, ROOF_IN + 0.2, (x, y, 0), green, segs=32)
        p.cyl(3.5, 5.0, 2.0, (x, y, ROOF_IN - 0.8), green, segs=32)    # fillet ke atap
    bosses = p.build(ccol, smooth_angle=40)
    # --- insert bezel saklar (lubang 12.95x19.3 -> cutout KCD11 8.8x13.6) ---
    y0, y1, z0, z1 = 8.5, 21.45, 15.35, 34.65
    yc, zc = SW_LOC[1], SW_LOC[2]
    cy0, cy1, cz0, cz1 = yc - 4.4, yc + 4.4, zc - 6.8, zc + 6.8
    p = Part("Casing_Switch_Bezel_Insert")
    xo0, xo1 = 43.8, 44.95
    y0, y1, z0, z1 = y0 + 0.03, y1 - 0.03, z0 + 0.03, z1 - 0.03          # celah pas 0.03 mm ke dinding lubang
    for lo, hi in (((xo0, y0, z0), (xo1, y1, cz0)), ((xo0, y0, cz1), (xo1, y1, z1)),
                   ((xo0, y0, cz0), (xo1, cy0, cz1)), ((xo0, cy1, cz0), (xo1, y1, cz1))):
        p.box_minmax(lo, hi, green)
    # kerah 1 mm sepanjang dinding lubang + flens dalam
    for lo, hi in (((42.45, y0, z0), (43.8, y1, z0 + 1.0)), ((42.45, y0, z1 - 1.0), (43.8, y1, z1)),
                   ((42.45, y0, z0 + 1.0), (43.8, y0 + 1.0, z1 - 1.0)), ((42.45, y1 - 1.0, z0 + 1.0), (43.8, y1, z1 - 1.0)),
                   ((41.4, y0 - 2.5, z0 - 2.5), (42.45, y1 + 2.5, z0 + 1.0)),
                   ((41.4, y0 - 2.5, z1 - 1.0), (42.45, y1 + 2.5, z1 + 2.5)),
                   ((41.4, y0 - 2.5, z0 + 1.0), (42.45, y0 + 1.0, z1 - 1.0)),
                   ((41.4, y1 - 1.0, z0 + 1.0), (42.45, y1 + 2.5, z1 - 1.0))):
        p.box_minmax(lo, hi, green)
    insert = p.build(ccol, smooth_angle=40)
    # --- sekrup M3 pan-head + ring + kaki karet (di bawah tutup) ---
    steel = new_mat("Mat_Steel_Screw", (0.78, 0.79, 0.8), rough=0.22, metal=1.0)
    dark = new_mat("Mat_Screw_Recess", (0.04, 0.04, 0.045), rough=0.6, metal=0.8)
    rubber = new_mat("Mat_Rubber_Foot", (0.02, 0.02, 0.022), rough=0.75)
    p = Part("Casing_Lid_Screws_M3")
    for (x, y, _z) in LID_HOLES:
        zb = -2.2
        if y < 0:
            p.tube(1.7, 3.6, zb - 0.5, zb, (x, y, 0), steel, segs=32)          # ring plat
            zb -= 0.5
        p.cyl(2.75, 2.45, 1.9, (x, y, zb - 0.95), steel, segs=32)
        p.cyl(2.45, 1.4, 0.35, (x, y, zb - 2.02), steel, segs=32)
        for a in (0, 90):
            p.box((3.0, 0.62, 0.6), (x, y, zb - 2.05), dark, rot=(0, 0, a + 45))
        p.cyl(1.45, 1.45, 10.0, (x, y, zb + 5.0), steel, segs=16)              # batang di dalam boss
    screws = p.build(ccol, smooth_angle=30)
    p = Part("Casing_Rubber_Feet")
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.cyl(5.0, 4.4, 2.6, (sx * 34.0, sy * 38.0, -2.2 - 1.3), rubber, segs=40)
    feet = p.build(ccol, smooth_angle=40, bevel=0.3)
    # --- klip cetak konektor RP-SMA (menyatu ke dinding belakang dalam, Y 62.47) ---
    ax, ay = ANT_LOC[0], ANT_LOC[1]
    r_notch, half_w, depth = 4.75, 5.6, 62.6 - ANT_LOC[1]
    poly = [(half_w, 0.0), (half_w, depth), (-half_w, depth), (-half_w, 0.0)]
    poly += [(r_notch * math.cos(math.radians(a)), r_notch * math.sin(math.radians(a))) for a in range(180, -1, -10)]
    p = Part("Casing_Antenna_Clip")
    p.prism(poly, ANT_LOC[2] - 1.0, ANT_LOC[2] + 7.0, TM((ax, ay, 0)), green)
    clip = p.build(ccol, smooth_angle=40)
    return [bosses, insert, screws, feet, clip]


# ---------------------------------------------------------------------------
# 5. Mounting elektronika
# ---------------------------------------------------------------------------
def build_mounting(ecol):
    perf = D.objects["Perfboard_Root"]
    brass = mat("Mat_Brass_Gold") if "Mat_Brass_Gold" in D.materials else new_mat("Mat_Brass_Gold", (0.95, 0.72, 0.15), 0.18, 0.92)
    steel = D.materials.get("Mat_Steel_Screw")
    nylon = new_mat("Mat_Nylon_White", (0.86, 0.85, 0.8), rough=0.45)
    foam = new_mat("Mat_Foam_Tape_Grey", (0.12, 0.12, 0.13), rough=0.95)
    dark = D.materials.get("Mat_Screw_Recess")
    p = Part("Perf_Standoffs_M3x5")
    zb = PERF_LOC[2]
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = PERF_LOC[0] + sx * 32.0
            y = PERF_LOC[1] + sy * 42.0
            p.cyl(2.887, 2.887, zb, (x, y, zb / 2), brass, rot=(0, 0, 30), segs=6)  # hex 5 AF, flat menghadap X
            p.cyl(2.75, 2.45, 1.9, (x, y, zb + 1.6 + 0.95), steel, segs=32)  # kepala sekrup di atas papan
            p.cyl(2.45, 1.4, 0.35, (x, y, zb + 1.6 + 2.07), steel, segs=32)
            for a in (0, 90):
                p.box((3.0, 0.62, 0.6), (x, y, zb + 1.6 + 2.1), dark, rot=(0, 0, a + 45))
    so = p.build(ecol, smooth_angle=35)
    so.parent = perf
    so.matrix_parent_inverse = perf.matrix_world.inverted()
    # spacer nilon TP4056
    tp = D.objects["TP4056_Root"]
    p = Part("TP4056_Nylon_Spacers")
    top = PERF_LOC[2] + 1.6
    for sx in (-6.0, 6.0):
        w = tp.matrix_world @ Vector((sx, -1.4, 0))
        p.tube(1.2, 1.75, top, TP_LOC[2] - 0.04, (w.x, w.y, 0), nylon, segs=24)
    sp = p.build(ecol, smooth_angle=35)
    sp.parent = tp
    sp.matrix_parent_inverse = tp.matrix_world.inverted()
    # pita foam baterai ke dinding kanan
    bat = D.objects["LiPo_Battery_Root"]
    p = Part("LiPo_Foam_Mount")
    p.box_minmax((40.52, -38.0, 6.0), (42.45, 2.0, 28.0), foam)
    fo = p.build(ecol, smooth_angle=30)
    fo.parent = bat
    fo.matrix_parent_inverse = bat.matrix_world.inverted()
    return [so, sp, fo]


def fix_oled_glass():
    """Pusatkan kaca/panel OLED di antara baris lubang PCB; FFC diregangkan mengikuti."""
    root = D.objects["OLED_096_Root"]
    if root.get("glass_fixed"):
        return
    d = Matrix.Translation((0, OLED_GLASS_SHIFT, 0))
    for n in ("OLED_Glass_Substrate", "OLED_Active_Panel"):
        ob = D.objects[n]
        mpi = ob.matrix_parent_inverse
        ob.matrix_basis = mpi.inverted() @ d @ mpi @ ob.matrix_basis
    ffc = D.objects["OLED_FFC_Ribbon"]
    to_root = ffc.matrix_parent_inverse @ ffc.matrix_basis
    back = to_root.inverted()
    y0, y1 = -13.0, -7.0
    for v in ffc.data.vertices:
        lp = to_root @ v.co
        if lp.y > y0:
            t = min(1.0, (lp.y - y0) / (y1 - y0))
            lp.y += OLED_GLASS_SHIFT * t
            v.co = back @ lp
    ffc.data.update()
    root["glass_fixed"] = True


def build_oled_screws(ecol):
    root = D.objects["OLED_096_Root"]
    steel = D.materials.get("Mat_Steel_Screw")
    dark = D.materials.get("Mat_Screw_Recess")
    p = Part("OLED_M2_Screws")
    for (x, y) in OLED_HOLES:
        p.cyl(1.9, 1.75, 1.2, (x, y, -0.03 - 0.6), steel, segs=28)
        p.cyl(1.75, 1.0, 0.25, (x, y, -0.03 - 1.32), steel, segs=28)
        p.box((2.2, 0.45, 0.5), (x, y, -1.4), dark, rot=(0, 0, 45))
        p.box((2.2, 0.45, 0.5), (x, y, -1.4), dark, rot=(0, 0, -45))
        p.cyl(0.8, 0.8, 2.2, (x, y, 1.24 + 1.1), steel, segs=12)       # batang M2 masuk lubang tiang
    ob = p.build(ecol, smooth_angle=30)
    ob.parent = root
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.matrix_basis = Matrix.Identity(4)
    return ob


# ---------------------------------------------------------------------------
# 6. Layar OLED menyala
# ---------------------------------------------------------------------------
def build_oled_screen(ecol):
    root = D.objects["OLED_096_Root"]
    if "OLED_Display_Pixels" in D.objects:
        return D.objects["OLED_Display_Pixels"]
    img = D.images.load(SCREEN_IMG, check_existing=True)
    img.pack()
    m = D.materials.new("Mat_OLED_Pixels")
    m.use_nodes = True
    nt = m.node_tree
    b = principled(m)
    b.inputs['Base Color'].default_value = (0.004, 0.004, 0.006, 1)
    b.inputs['Roughness'].default_value = 0.08
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = 'Closest'
    tint = nt.nodes.new("ShaderNodeMix")
    tint.data_type = 'RGBA'
    tint.blend_type = 'MULTIPLY'
    tint.inputs['Factor'].default_value = 1.0
    tint.inputs[7].default_value = (0.82, 0.92, 1.0, 1.0)
    nt.links.new(tex.outputs['Color'], tint.inputs[6])
    nt.links.new(tint.outputs[2], b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value = 6.0
    me = D.meshes.new("OLED_Display_Pixels")
    w, h = 21.74, 10.86
    vs = [(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)]
    me.from_pydata(vs, [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, co in zip(range(4), ((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[li].uv = co
    me.materials.append(m)
    ob = D.objects.new("OLED_Display_Pixels", me)
    ecol.objects.link(ob)
    ob.parent = root
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.location = (0.0, -1.14 + OLED_GLASS_SHIFT, 2.585)
    return ob


# ---------------------------------------------------------------------------
# 7. Wiring (Bezier) dengan rute manual + offset pita
# ---------------------------------------------------------------------------
def endpoint(spec_end):
    rname, lp, ldir = spec_end
    r = D.objects[rname]
    return r.matrix_world @ lp, (r.matrix_world.to_3x3() @ ldir).normalized()


def catmull(pts, n=6):
    """Centripetal Catmull-Rom -> titik rapat."""
    P = [pts[0] + (pts[0] - pts[1])] + list(pts) + [pts[-1] + (pts[-1] - pts[-2])]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]

        def tj(ti, a, b):
            return ti + max((b - a).length, 1e-4) ** 0.5
        t0 = 0.0
        t1 = tj(t0, p0, p1)
        t2 = tj(t1, p1, p2)
        t3 = tj(t2, p2, p3)
        for k in range(n):
            t = t1 + (t2 - t1) * k / n
            a1 = p0 * ((t1 - t) / (t1 - t0)) + p1 * ((t - t0) / (t1 - t0))
            a2 = p1 * ((t2 - t) / (t2 - t1)) + p2 * ((t - t1) / (t2 - t1))
            a3 = p2 * ((t3 - t) / (t3 - t2)) + p3 * ((t - t2) / (t3 - t2))
            b1 = a1 * ((t2 - t) / (t2 - t0)) + a2 * ((t - t0) / (t2 - t0))
            b2 = a2 * ((t3 - t) / (t3 - t1)) + a3 * ((t - t1) / (t3 - t1))
            out.append(b1 * ((t2 - t) / (t2 - t1)) + b2 * ((t - t1) / (t2 - t1)))
    out.append(pts[-1])
    return out


def make_wire(name, ctrl, radius, mname, col, n=5):
    pts = catmull([Vector(p) for p in ctrl], n)
    cu = D.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 6
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    cu.materials.append(mat(mname))
    ob = D.objects.new(name, cu)
    col.objects.link(ob)
    return ob


def side_vec(t):
    s = t.cross(Vector((0, 0, 1)))
    if s.length < 1e-3:
        s = Vector((1, 0, 0))
    return s.normalized()


def ribbon(names, centre, spacing, col, lead=3.0, lead_end=3.0, order=None, n=5, lift=None):
    """Beberapa kabel mengikuti satu garis tengah sebagai pita datar."""
    centre = [Vector(c) for c in centre]
    k = len(names)
    sv = []
    for i, c in enumerate(centre):
        a = centre[max(i - 1, 0)]
        b = centre[min(i + 1, len(centre) - 1)]
        sv.append(side_vec((b - a).normalized()))
    starts = {nm: endpoint(WIRE_SPEC[nm]['start']) for nm in names}
    if order is None:
        order = sorted(names, key=lambda nm: (starts[nm][0] - centre[0]).dot(sv[0]))
    objs = []
    for j, nm in enumerate(order):
        off = (j - (k - 1) / 2) * spacing
        s, sd = starts[nm]
        e, ed = endpoint(WIRE_SPEC[nm]['end'])
        ctrl = [s, s + sd * lead]
        ctrl += [c + sv[i] * off for i, c in enumerate(centre)]
        ctrl += [e + ed * lead_end, e]
        spec = WIRE_SPEC[nm]
        objs.append(make_wire(nm, ctrl, spec['radius'], spec['mat'], col, n))
    return objs


def single(nm, vias, col, lead=3.0, lead_end=3.0, start=None, end=None, n=5):
    spec = WIRE_SPEC[nm]
    s, sd = start or endpoint(spec['start'])
    e, ed = end or endpoint(spec['end'])
    ctrl = [s, s + sd * lead] + [Vector(v) for v in vias] + [e + ed * lead_end, e]
    return make_wire(nm, ctrl, spec['radius'], spec['mat'], col, n)


def override_end(nm, which, root, lp, ldir):
    WIRE_SPEC[nm][which] = (root, Vector(lp), Vector(ldir).normalized())


def route_harness(wcol):
    objs = []
    # ---- endpoint yang perlu disesuaikan dengan pemasangan baru ----
    # saklar: kabel masuk lubang lug searah Y (lug pipih di bidang XZ)
    sw = D.objects["Switch_KCD11_Root"]
    swinv = sw.matrix_world.inverted()
    lug_lo = swinv @ Vector((29.4, 14.975, 22.5))
    lug_hi = swinv @ Vector((29.4, 14.975, 27.5))
    override_end("Wire_Switch_ESP32_VIN", 'start', sw.name, lug_lo, swinv.to_3x3() @ Vector((0, -1, 0)))
    override_end("Wire_TP_OUTpos_Switch", 'end', sw.name, lug_hi, swinv.to_3x3() @ Vector((0, 1, 0)))
    # baterai: kabel keluar dari ujung PCM, berdampingan searah lebar baterai
    override_end("Wire_Bat_Pos", 'start', "LiPo_Battery_Root", (12.6, 25.4, 1.95), (0, 1, 0))
    override_end("Wire_Bat_Neg", 'start', "LiPo_Battery_Root", (12.6, 25.4, 4.35), (0, 1, 0))
    # VIN: disolder di sisi bawah perfboard (lubang sebelah pin 5V ESP32)
    override_end("Wire_Switch_ESP32_VIN", 'end', "Perfboard_Root", (-8.89, -36.83, -0.35), (0, 0, -1))
    # TP pads / OPA / adapter: arah keluar tegak lurus permukaan
    for nm in ("Wire_Bat_Pos", "Wire_Bat_Neg", "Wire_TP_OUTneg_GND", "Wire_TP_OUTpos_Switch"):
        sp = WIRE_SPEC[nm]
        for which in ('start', 'end'):
            r, lp, ld = sp[which]
            if r == "TP4056_Root":
                sp[which] = (r, lp, Vector((0, 0, 1)))
            if r == "LiPo_Battery_Root":
                sp[which] = (r, lp, Vector((0, 1, 0)))
    for nm, sp in WIRE_SPEC.items():
        for which in ('start', 'end'):
            r, lp, ld = sp[which]
            if r.startswith("OPA_Module") or (r == "Perfboard_Root" and nm != "Wire_Switch_ESP32_VIN"
                                              and not nm.startswith("Coax")):
                sp[which] = (r, lp, Vector((0, 0, 1)))
            if r.startswith("SPE_Adapter"):
                sp[which] = (r, lp, Vector((1, 0, 0)))
            if r == "OLED_096_Root":
                sp[which] = (r, lp, Vector((0, 0, -1)))
            if r == "Antenna_RPSMA_Root":
                sp[which] = (r, lp, Vector((0, 0, -1)))

    # ---- 9 kabel sensor SPE: adapter -> modul OPA (pita 3 kabel, putar balik di belakang OPA
    #      supaya urutan Y/K/R di adapter cocok dengan urutan lubang di perfboard tanpa silang) ----
    zc = ADAPTER_Z + 3.6
    for k in (1, 2, 3):
        names = ["Wire_SPE%d_%s_OPA%d" % (k, c, k) for c in ("R", "K", "Y")]
        objs += ribbon(names, [(x, y, zc if z is None else z) for x, y, z in SPE_ROUTE_TAIL[k]],
                       1.25, wcol, lead=2.0, lead_end=2.6, order=names)

    # ---- 4 kabel OLED: header perfboard -> header OLED di atap (pita dupont) ----
    objs += ribbon(["Wire_OLED_VCC", "Wire_OLED_GND", "Wire_OLED_SCL", "Wire_OLED_SDA"],
                   [(23.2, 11.62, 26.6), (18.5, 12.0, 27.4), (11.0, 16.5, 26.8), (4.0, 21.0, 25.2),
                    (0.0, 23.8, 24.4)],
                   2.54, wcol, lead=2.5, lead_end=1.6, n=6,
                   order=["Wire_OLED_VCC", "Wire_OLED_GND", "Wire_OLED_SCL", "Wire_OLED_SDA"])

    # ---- daya: baterai -> TP4056 (merah/hitam), sepanjang dinding kanan & belakang ----
    objs += ribbon(["Wire_Bat_Pos", "Wire_Bat_Neg"],
                   [(36.9, 13.0, 4.2), (37.2, 24.0, 4.0), (37.6, 36.0, 3.8), (36.2, 44.5, 6.4), (31.0, 47.0, 10.8),
                    (12.0, 47.0, 11.2), (1.6, 46.8, 11.8), (-1.4, 42.4, 16.6), (-5.8, 38.8, 17.0)],
                   1.35, wcol, lead=2.0, lead_end=2.4, order=["Wire_Bat_Pos", "Wire_Bat_Neg"])
    # ---- TP OUT- -> GND perfboard ----
    objs.append(single("Wire_TP_OUTneg_GND", [(-21.0, 35.7, 17.4), (-28.0, 35.0, 16.4), (-34.0, 35.6, 14.0)],
                       wcol, lead=2.4, lead_end=3.0))
    # ---- TP OUT+ (putih) -> lug atas saklar ----
    objs.append(single("Wire_TP_OUTpos_Switch",
                       [(-4.6, 34.8, 19.6), (4.0, 34.6, 20.4), (16.0, 34.2, 21.0), (28.5, 31.0, 25.0),
                        (31.5, 23.5, 28.6)],
                       wcol, lead=2.6, lead_end=2.6))
    # ---- lug bawah saklar (merah) -> VIN ESP32 lewat bawah perfboard ----
    objs.append(single("Wire_Switch_ESP32_VIN",
                       [(30.6, 9.8, 20.0), (32.0, 4.0, 11.0), (32.0, -6.0, 3.4), (30.6, -24.0, 2.2),
                        (22.0, -31.6, 2.0), (0.0, -32.6, 2.0), (-11.5, -32.9, 2.0)],
                       wcol, lead=2.4, lead_end=1.8))
    # ---- koaksial RG1.13: IPEX ESP32 -> konektor RP-SMA (masuk dari bawah, lewat belakang tepi perfboard) ----
    objs.append(single("Coax_RG113_IPEX_SMA", COAX_ROUTE, wcol, lead=1.6, lead_end=2.4))
    return objs


# Garis tengah pita SPE: keluar ujung JST adapter (+Y), lewat sela ESP32/ADS1115, putar balik di belakang OPA.
# z None = ADAPTER_Z + 3.6 (tinggi pin JST)
SPE_ROUTE_TAIL = {
    1: [(-18.8, -2.0, None), (-18.9, 4.0, None), (-20.5, 9.5, 14.2), (-27.0, 13.0, 14.6), (-35.0, 15.5, 14.6),
        (-38.4, 20.0, 14.0), (-38.4, 26.0, 12.6), (-38.4, 33.0, 10.2), (-38.0, 39.0, 9.6),
        (-36.0, 42.6, 9.6), (-33.0, 43.5, 9.6), (-30.6, 42.2, 9.6), (-30.13, 40.8, 9.6)],
    2: [(0.0, -2.0, None), (0.0, 6.0, None), (0.6, 15.0, 13.8), (3.8, 20.5, 14.2), (8.6, 25.0, 14.2),
        (8.6, 31.0, 12.4), (8.4, 37.0, 10.4), (7.2, 40.8, 9.6), (4.4, 42.4, 9.6),
        (0.0, 42.6, 9.6), (-4.6, 42.0, 9.6), (-7.0, 40.6, 9.6)],
    3: [(20.0, -2.0, None), (23.0, 2.5, 13.2), (27.4, 6.0, 12.2), (28.4, 11.0, 11.8), (28.4, 24.0, 11.4),
        (28.2, 36.0, 10.2), (26.6, 41.8, 9.6), (22.8, 43.4, 9.6), (18.6, 43.2, 9.6), (16.2, 42.0, 9.6),
        (15.59, 40.6, 9.6)],
}
COAX_ROUTE = [(9.6, 26.5, 21.4), (12.0, 32.0, 23.6), (15.0, 37.5, 23.2), (19.0, 43.0, 19.6), (22.2, 47.6, 16.4),
              (23.8, 50.2, 12.0), (24.2, 51.4, 7.0), (23.9, 52.0, 3.4), (22.6, 52.2, 1.9)]


# ---------------------------------------------------------------------------
# 8. Cek tabrakan (kabel vs casing/komponen, kabel vs kabel)
# ---------------------------------------------------------------------------
def curve_ends(ob):
    sp = ob.data.splines[0]
    return [ob.matrix_world @ sp.bezier_points[0].co, ob.matrix_world @ sp.bezier_points[-1].co]


BOARD_PARTS = ("Main_Perfboard", "Perfboard_", "Leads_Solder_", "ESP32_Female_Headers")


def collision_report(wires, end_tol=3.2, verbose=True):
    """Kabel harness baru diuji terhadap SEMUA mesh + semua kabel; kabel on-board (tidak diubah dari
    model rangkaian) hanya diuji terhadap casing & part baru (kontak dengan pad/lubang papan memang disengaja)."""
    dg = bpy.context.evaluated_depsgraph_get()
    obst = []
    for ob in list(D.collections["PKM_Casing"].all_objects) + list(D.collections["PKM_Electronics"].all_objects):
        if ob.type != 'MESH' or ob.hide_render or ob.name.startswith("Cut_"):
            continue
        bvh, _ = world_bvh(ob, dg)
        if bvh:
            obst.append((ob.name, bvh, ob.users_collection[0].name))
    wb = {}
    for w in wires:
        bvh, cent = world_bvh(w, dg)
        wb[w.name] = (bvh, cent, curve_ends(w), w.name in WIRE_SPEC)
    report = defaultdict(list)
    for wn, (bvh, cent, ends, harness) in wb.items():
        def far(i):
            return all((cent[i] - e).length > end_tol for e in ends)
        for on, ob, oc in obst:
            if not harness and (on.startswith(BOARD_PARTS) or oc in ("EL_Perfboard", "EL_ESP32", "EL_ADS1115",
                                                                     "EL_OPA_Modules")):
                continue
            hits = [i for i, _j in bvh.overlap(ob) if far(i)]
            if hits:
                report[wn].append((on, len(hits), tuple(round(c, 1) for c in cent[hits[len(hits) // 2]])))
    names = list(wb)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = wb[names[i]], wb[names[j]]
            if not (a[3] or b[3]):
                continue
            hits = [p for p, q in a[0].overlap(b[0]) if all((a[1][p] - e).length > end_tol for e in a[2] + b[2])]
            if hits:
                report[names[i]].append((names[j], len(hits), tuple(round(c, 1) for c in a[1][hits[0]])))
    if verbose:
        for k, v in report.items():
            print("COLLIDE", k, v)
        print("collision groups:", len(report))
    return report


# ---------------------------------------------------------------------------
# 9. Struktur collection
# ---------------------------------------------------------------------------
def organize(el):
    sc = bpy.context.scene
    ccol = D.collections["PKM_Casing"]
    wcol = get_col("PKM_Wiring")
    if wcol.name not in [c.name for c in sc.collection.children]:
        sc.collection.children.link(wcol)
    old = D.collections.get("EL_Wiring")
    if old:
        for ob in list(old.objects):
            move_to_col(ob, wcol)
        D.collections.remove(old)
    for nm in ("Collection",):
        c = D.collections.get(nm)
        if c and not c.all_objects:
            D.collections.remove(c)
    return ccol, wcol


# ---------------------------------------------------------------------------
# 10. Cutaway + kondisi tampilan (frame 1 = rakitan tertutup, 2 = casing dibuka/cutaway, 3 = exploded)
# ---------------------------------------------------------------------------
SECTION_SOURCES = ("PKM_Casing_Main", "Casing_Lid_Screw_Bosses", "Casing_Switch_Bezel_Insert")
EXPLODE = {"lid": -30.0, "board": 0.0, "harness": 22.0, "oled": 35.0, "body": 110.0}
STATE_FRAMES = {"ASSEMBLED": 1, "OPEN_CUTAWAY": 2, "EXPLODED": 3}


def build_cutaway(ccol):
    sec = new_mat("Mat_Section_Cut", (0.86, 0.24, 0.06), rough=0.7)
    out = []
    for n in SECTION_SOURCES:
        src = D.objects[n]
        nm = n + "_Cutaway"
        if nm in D.objects:
            D.objects.remove(D.objects[nm], do_unlink=True)
        ob = src.copy()
        ob.data = src.data.copy()
        ob.name = ob.data.name = nm
        ccol.objects.link(ob)
        apply_modifiers(ob)
        c = make_cutter("Cut_Section", (400, 400, 100), (0, 0, CUT_Z + 50.0), m=sec)
        boolean(ob, c, transfer=True)
        D.objects.remove(c, do_unlink=True)
        out.append(ob)
    return out


def state_groups():
    harness = [D.objects[n] for n in WIRE_SPEC if n in D.objects]
    if not harness:
        harness = [o for o in D.collections["PKM_Wiring"].objects if o.parent is None]
    return {
        "lid": [D.objects[n] for n in ("PKM_Casing_Lid", "Casing_Lid_Screws_M3", "Casing_Rubber_Feet")],
        "board": [D.objects[n] for n in ("Perfboard_Root", "TP4056_Root", "LiPo_Battery_Root")],
        "harness": harness,
        "oled": [D.objects["OLED_096_Root"]],
        "body": [D.objects[n] for n in ("PKM_Casing_Main", "Casing_Lid_Screw_Bosses", "Casing_Switch_Bezel_Insert",
                                         "Switch_KCD11_Root", "Antenna_RPSMA_Root", "Casing_Antenna_Clip",
                                         "Adapter_V1_Base", "Adapter_V1_Lid")]
                + [D.objects[n] for n in ADAPTER_X] + [D.objects[n] for n in STRIP_FOR_ADAPTER.values()]
                + [D.objects[n + "_Cutaway"] for n in SECTION_SOURCES if n + "_Cutaway" in D.objects],
    }


def store_base():
    for g in state_groups().values():
        for ob in g:
            ob["base_loc"] = list(ob.location)


def set_state(state, key=False):
    """ASSEMBLED | OPEN_CUTAWAY | EXPLODED. key=True -> sisipkan keyframe di frame STATE_FRAMES[state]."""
    groups = state_groups()
    frame = STATE_FRAMES[state]
    for gname, obs in groups.items():
        dz = EXPLODE[gname] if state == "EXPLODED" else 0.0
        for ob in obs:
            b = ob.get("base_loc")
            if b is None:
                continue
            ob.location = (b[0], b[1], b[2] + dz)
            if key:
                ob.keyframe_insert("location", frame=frame)
    cut = state == "OPEN_CUTAWAY"
    for n in SECTION_SOURCES:
        for nm, vis in ((n, not cut), (n + "_Cutaway", cut)):
            ob = D.objects.get(nm)
            if ob is None:
                continue
            ob.hide_render = not vis
            ob.hide_viewport = not vis
            if key:
                ob.keyframe_insert("hide_render", frame=frame)
                ob.keyframe_insert("hide_viewport", frame=frame)
    floor = D.objects.get("Studio_Floor")
    if floor:
        floor.location.z = FLOOR_Z + (EXPLODE["lid"] if state == "EXPLODED" else 0.0)
        if key:
            floor.keyframe_insert("location", frame=frame)
    bpy.context.view_layer.update()


FLOOR_Z = -2.2 - 2.6          # bawah kaki karet


def key_states():
    for st in ("ASSEMBLED", "OPEN_CUTAWAY", "EXPLODED"):
        set_state(st, key=True)
    for ob in D.objects:
        ad = ob.animation_data
        if ad and ad.action:
            try:
                fcurves = ad.action.fcurves
            except AttributeError:
                fcurves = [fc for layer in ad.action.layers for strip in layer.strips
                           for cb in strip.channelbags for fc in cb.fcurves]
            for fc in fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = 'CONSTANT'
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, 3
    for st, f in STATE_FRAMES.items():
        m = sc.timeline_markers.get(st) or sc.timeline_markers.new(st, frame=f)
        m.frame = f
    sc.frame_set(1)
    set_state("ASSEMBLED")


def build_all(save=True, studio=None):
    el = load_sources()
    record_harness(el)
    split_leads_solder()
    place_components()
    modify_casing()
    build_v1_housing()
    cut_adapter_sockets()
    ccol, wcol = organize(el)
    build_casing_addons(ccol)
    mcol = get_col("EL_Mounting", el)
    build_mounting(mcol)
    fix_oled_glass()
    build_oled_screen(D.collections["EL_OLED"])
    build_oled_screws(D.collections["EL_OLED"])
    route_harness(wcol)
    bpy.context.view_layer.update()
    rep = collision_report(list(wcol.objects))
    build_cutaway(ccol)
    if studio:
        studio()
    store_base()
    key_states()
    if save:
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    return rep


def part_groups():
    g = {}
    for ob in D.collections["PKM_Casing"].all_objects:
        if ob.type == 'MESH':
            g[ob.name] = [ob]
    for r in component_roots():
        if r.parent is not None:
            continue
        g[r.name] = [o for o in r.children_recursive if o.type == 'MESH']
    for ob in D.collections["EL_Mounting"].objects:
        if ob.type == 'MESH':
            g[ob.name] = [ob]
    return g


def part_interference(verbose=True):
    """Uji tumpang-tindih antar kelompok part (komponen vs casing vs komponen)."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    g = part_groups()
    bvh = {}
    for k, obs in g.items():
        for ob in obs:
            if ob.hide_render:
                continue
            t, cent = world_bvh(ob, dg)
            if t:
                bvh.setdefault(k, []).append((ob.name, t, cent))
    keys = list(bvh)
    out = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            for an, at, ac in bvh[keys[i]]:
                for bn, bt, bc in bvh[keys[j]]:
                    pairs = at.overlap(bt)
                    if pairs:
                        p = ac[pairs[0][0]]
                        out.append((an, bn, len(pairs), tuple(round(c, 1) for c in p)))
    if verbose:
        for o in out:
            print("PART", o)
        print("part overlaps:", len(out))
    return out
