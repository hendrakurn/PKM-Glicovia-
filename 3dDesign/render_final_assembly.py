"""
PKM-GLICOVIA - Studio 3-point, kamera multi-sisi, dan render final assembly (2560x1440, PNG 16-bit).

Pakai di Blender setelah build_final_assembly.py:
    exec(open(".../render_final_assembly.py").read(), ns); ns['setup_studio'](); ns['render_view']('01')
Kondisi tampilan memakai set_state() dari build_final_assembly.py (frame 1/2/3 di timeline).
Kompilasi 4-in-1 (07) dibuat oleh make_grid() di Python sistem (Pillow).
"""
import math
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

D = bpy.data
DIR = "/home/hendra/project/PKM-Glicovia-/3dDesign"
OUT = DIR + "/finalImage"
LIGHT_K = 4800.0                  # skala W -> unit mm (rasio Key 400 : Fill 200 : Rim 600 dipertahankan)
FLOOR_Z = -4.8

# nama: (state, arah target->kamera, lensa mm (None = ortho), file, kelompok framing, margin)
VIEWS = {
    "01": ("ASSEMBLED", (0.58, -1.0, 0.78), 60.0, "01_pkm_assembled_isometric.png", "all", 0.05),
    "02": ("ASSEMBLED", (0.0, 0.0, 1.0), None, "02_pkm_assembled_top_oled.png", "all", 0.04),
    "03": ("ASSEMBLED", (0.25, -0.85, 1.0), 105.0, "03_pkm_assembled_front_sensors.png", "front", 0.05),
    "04": ("ASSEMBLED", (0.8, 1.0, 0.36), 70.0, "04_pkm_assembled_side_ports.png", "ports", 0.05),
    "05": ("OPEN_CUTAWAY", (-0.5, 0.72, 1.1), 50.0, "05_pkm_internal_circuit_open_lid.png", "casing", 0.035),
    "06": ("EXPLODED", (0.95, -1.0, 0.36), 55.0, "06_pkm_exploded_assembly_view.png", "all", 0.04),
}


def get_col(name):
    c = D.collections.get(name) or D.collections.new(name)
    sc = bpy.context.scene
    if c.name not in [x.name for x in sc.collection.children]:
        sc.collection.children.link(c)
    return c


def link_only(ob, col):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)


def area_light(name, watts, size, size_y, loc, target, color, col):
    ob = D.objects.get(name)
    if ob is None:
        ob = D.objects.new(name, D.lights.new(name, 'AREA'))
        col.objects.link(ob)
    ld = ob.data
    ld.type = 'AREA'
    ld.shape = 'RECTANGLE'
    ld.size, ld.size_y = size, size_y
    ld.energy = watts * LIGHT_K
    ld.color = color
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    ob["rated_watt"] = watts
    return ob


def setup_studio():
    sc = bpy.context.scene
    col = get_col("Studio_Lighting")
    # lantai studio (abu netral semi-matte) yang memudar mulus ke latar (studio tanpa batas)
    BG_CAM = (0.74, 0.76, 0.8)
    fl = D.objects.get("Studio_Floor")
    if fl is None:
        me = D.meshes.new("Studio_Floor")
        r = 4000.0
        me.from_pydata([(-r, -r, 0), (r, -r, 0), (r, r, 0), (-r, r, 0)], [], [(0, 1, 2, 3)])
        fl = D.objects.new("Studio_Floor", me)
        col.objects.link(fl)
    m = D.materials.get("Mat_Studio_Floor") or D.materials.new("Mat_Studio_Floor")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    outp = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs['Base Color'].default_value = (0.42, 0.44, 0.47, 1)
    bsdf.inputs['Roughness'].default_value = 0.6
    bsdf.inputs['Specular IOR Level'].default_value = 0.12
    emi = nt.nodes.new("ShaderNodeEmission")
    emi.inputs['Color'].default_value = (*BG_CAM, 1)
    emi.inputs['Strength'].default_value = 1.0
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = 'LENGTH'
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.interpolation_type = 'SMOOTHSTEP'
    mr.inputs['From Min'].default_value = 450.0
    mr.inputs['From Max'].default_value = 1600.0
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(geo.outputs['Position'], ln.inputs[0])
    nt.links.new(ln.outputs['Value'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], mix.inputs['Fac'])
    nt.links.new(bsdf.outputs[0], mix.inputs[1])
    nt.links.new(emi.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], outp.inputs['Surface'])
    fl.data.materials.clear()
    fl.data.materials.append(m)
    fl.location = (0, 0, FLOOR_Z)
    # world: latar terang untuk kamera, ambient redup untuk pencahayaan
    w = sc.world or D.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    wn = w.node_tree
    wn.nodes.clear()
    wo = wn.nodes.new("ShaderNodeOutputWorld")
    b_amb = wn.nodes.new("ShaderNodeBackground")
    b_amb.inputs[0].default_value = (0.6, 0.62, 0.66, 1)
    b_amb.inputs[1].default_value = 0.32
    b_cam = wn.nodes.new("ShaderNodeBackground")
    b_cam.inputs[0].default_value = (*BG_CAM, 1)
    b_cam.inputs[1].default_value = 1.0
    lp = wn.nodes.new("ShaderNodeLightPath")
    wm = wn.nodes.new("ShaderNodeMixShader")
    wn.links.new(lp.outputs['Is Camera Ray'], wm.inputs['Fac'])
    wn.links.new(b_amb.outputs[0], wm.inputs[1])
    wn.links.new(b_cam.outputs[0], wm.inputs[2])
    wn.links.new(wm.outputs[0], wo.inputs['Surface'])
    # 3-point softbox: Key 400 W, Fill 200 W, Rim 600 W (+ top bounce lembut)
    area_light("Key_Light_400W", 400, 300, 220, (-270, -330, 400), (0, -15, 20), (1.0, 0.96, 0.92), col)
    area_light("Fill_Light_200W", 200, 380, 300, (360, -220, 260), (0, -10, 15), (0.92, 0.96, 1.0), col)
    area_light("Rim_Light_600W", 600, 360, 110, (40, 420, 330), (0, 20, 30), (1.0, 1.0, 1.0), col)
    area_light("Top_Bounce_100W", 100, 520, 520, (0, 0, 700), (0, 0, 0), (1.0, 1.0, 1.0), col)
    # render
    r = sc.render
    try:
        r.engine = 'BLENDER_EEVEE'
    except TypeError:
        r.engine = 'BLENDER_EEVEE_NEXT'
    r.resolution_x, r.resolution_y, r.resolution_percentage = 2560, 1440, 100
    r.film_transparent = False
    r.image_settings.file_format = 'PNG'
    r.image_settings.color_mode = 'RGB'
    r.image_settings.color_depth = '16'
    r.image_settings.compression = 15
    ee = sc.eevee
    ee.taa_render_samples = 128
    ee.use_raytracing = True
    ee.use_shadows = True
    ee.shadow_ray_count = 3
    ee.shadow_step_count = 12
    ee.use_fast_gi = True
    ee.fast_gi_quality = 1.0
    ee.fast_gi_distance = 40.0
    try:
        ee.ray_tracing_method = 'SCREEN'
        ee.ray_tracing_options.resolution_scale = '1'
        ee.ray_tracing_options.use_denoise = True
    except Exception as e:
        print("raytrace option:", e)
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - High Contrast'
    sc.view_settings.exposure = 0.0
    sc.display_settings.display_device = 'sRGB'
    return sc


def visible_points(group):
    names_front = ("SPE_Strip", "Adapter_V1")       # bagian sensor di luar dinding depan
    pts = []
    if group == "front":       # dinding depan bagian bawah sebagai konteks
        pts += [Vector((x, -65.0, z)) for x in (-33.0, 33.0) for z in (0.0, 24.0)]
    for ob in bpy.context.scene.objects:
        if ob.type not in {'MESH', 'CURVE'} or ob.hide_render or ob.name.startswith(("Studio_", "Cut_")):
            continue
        if group == "front" and not (ob.name.startswith(names_front) or ob.name == "PKM_Casing_Main"):
            continue
        if group == "ports" and ob.name.startswith(("SPE_",)):
            continue
        if group == "casing" and not ob.name.startswith(("PKM_Casing_Main", "OLED_", "Ant_RPSMA", "Switch_")):
            continue
        for c in ob.bound_box:
            p = ob.matrix_world @ Vector(c)
            if group == "front" and ob.name == "PKM_Casing_Main":
                continue
            pts.append(p)
    return pts


def frame_camera(cam, direction, lens, pts, margin):
    sc = bpy.context.scene
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    center = (lo + hi) / 2
    d = Vector(direction).normalized()
    cd = cam.data
    cd.clip_start, cd.clip_end = 1.0, 6000.0
    cd.sensor_fit = 'HORIZONTAL'
    cd.sensor_width = 36.0
    if lens is None:
        cd.type = 'ORTHO'
        cam.location = center + d * 900.0
        cam.rotation_euler = (0, 0, 0)
        cd.ortho_scale = 300.0
    else:
        cd.type = 'PERSP'
        cd.lens = lens
        cam.location = center + d * 500.0
        cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    for _ in range(60):
        bpy.context.view_layer.update()
        co = [world_to_camera_view(sc, cam, p) for p in pts]
        xs = [c.x for c in co]
        ys = [c.y for c in co]
        ext = max(max(xs) - 0.5, 0.5 - min(xs), max(ys) - 0.5, 0.5 - min(ys))
        cx = (max(xs) + min(xs)) / 2 - 0.5
        cy = (max(ys) + min(ys)) / 2 - 0.5
        f = ext / (0.5 - margin)
        mw = cam.matrix_world.to_3x3()
        if cd.type == 'ORTHO':
            w = cd.ortho_scale
            h = w * sc.render.resolution_y / sc.render.resolution_x
            cam.location += mw @ Vector((cx * w, cy * h, 0))
            cd.ortho_scale *= f
        else:
            dist = (cam.location - center).length
            w = 2 * dist * math.tan(math.atan(cd.sensor_width / (2 * cd.lens)))
            h = w * sc.render.resolution_y / sc.render.resolution_x
            cam.location += mw @ Vector((cx * w, cy * h, 0)) * 0.9
            cam.location = center + (cam.location - center) * (1 + (f - 1) * 0.9)
        if abs(f - 1) < 0.003 and abs(cx) < 0.002 and abs(cy) < 0.002:
            break
    return cam


def get_cam(name):
    col = get_col("Studio_Lighting")
    ob = D.objects.get(name)
    if ob is None:
        ob = D.objects.new(name, D.cameras.new(name))
        col.objects.link(ob)
    return ob


def setup_view(key, ns):
    state, direction, lens, fname, group, margin = VIEWS[key]
    ns['set_state'](state)
    bpy.context.scene.frame_set(ns['STATE_FRAMES'][state])     # keyframe kondisi ikut dievaluasi
    cam = get_cam(f"Cam_{key}_" + fname.split("_pkm_")[1].replace(".png", ""))
    frame_camera(cam, direction, lens, visible_points(group), margin)
    cd = cam.data
    cd.dof.use_dof = key == "03"
    if key == "03":
        cd.dof.focus_distance = (cam.location - Vector((0, -82.0, 14.0))).length    # lubang sumur sampel
        cd.dof.aperture_fstop = 8.0
    return cam, fname


def render_view(key, ns):
    cam, fname = setup_view(key, ns)
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.filepath = f"{OUT}/{fname}"
    bpy.ops.render.render(write_still=True)
    return sc.render.filepath
