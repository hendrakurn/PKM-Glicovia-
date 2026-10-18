"""
PKM-GLICOVIA - Setup studio + render 4 sudut rangkaian elektronika (2560 x 1440, EEVEE raytracing).

Jalankan di Blender setelah build_rangkaian_detail_v2.py:
    setup_studio(); render_all()          # render 4 view ke folder 3dDesign
Kompilasi 4-in-1 dibuat terpisah (make_multiview) memakai PIL di Python sistem.
"""
import bpy
import math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

D = bpy.data
OUT_DIR = "/home/hendra/project/PKM-Glicovia-/3dDesign"
ROOT = "PKM_Electronics_Assembly"

VIEWS = {
    # name: (arah dari target ke kamera, lensa mm atau None=ortho, file)
    "isometric": (Vector((-0.55, -0.85, 0.80)), 55.0, "render_rangkaian_isometric.png"),
    "top":       (Vector((0.0, 0.0, 1.0)), None, "render_rangkaian_top.png"),
    "front":     (Vector((0.0, -1.0, 0.16)), 105.0, "render_rangkaian_front.png"),
    "side":      (Vector((1.0, -0.06, 0.16)), 105.0, "render_rangkaian_side.png"),
}


def scene_bbox():
    root = D.collections[ROOT]
    pts = []
    for ob in root.all_objects:
        if ob.type not in {'MESH', 'CURVE'} or ob.hide_render:
            continue
        for c in ob.bound_box:
            pts.append(ob.matrix_world @ Vector(c))
    return pts


def area_light(name, power, size, size_y, loc, target, color=(1, 1, 1)):
    ob = D.objects.get(name)
    if ob is None or ob.type != 'LIGHT':
        if ob:
            D.objects.remove(ob, do_unlink=True)
        ld = D.lights.new(name, 'AREA')
        ob = D.objects.new(name, ld)
        bpy.context.scene.collection.objects.link(ob)
    ld = ob.data
    ld.type = 'AREA'
    ld.shape = 'RECTANGLE'
    ld.size, ld.size_y = size, size_y
    ld.energy = power
    ld.color = color
    try:
        ld.use_shadow = True
        ld.shadow_soft_size = max(size, size_y) * 0.5
    except Exception:
        pass
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob


def setup_studio():
    sc = bpy.context.scene
    # meja lab netral (abu terang, semi-matte) - sudah ada sebagai Lab_Workstation_Table
    table = D.objects.get("Lab_Workstation_Table")
    if table:
        table.location = (0.0, 0.0, 0.0)
        table.scale = (1.6, 1.6, 1.0)
    # world: ambient studio lembut
    w = sc.world
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (0.62, 0.64, 0.68, 1.0)
    bg.inputs[1].default_value = 0.35
    # studio 3-point: key softbox, fill, rim (unit mm -> daya besar)
    area_light("Key_Softbox", 2.6e6, 260.0, 200.0, (-260.0, -300.0, 420.0), (0, -5, 0), (1.0, 0.97, 0.93))
    area_light("Fill_Softbox", 0.9e6, 320.0, 260.0, (330.0, -160.0, 300.0), (0, 0, 0), (0.93, 0.96, 1.0))
    area_light("Rim_Highlight", 1.6e6, 300.0, 90.0, (40.0, 360.0, 260.0), (0, 0, 0), (1.0, 1.0, 1.0))
    area_light("Top_Bounce", 0.7e6, 420.0, 420.0, (0.0, 0.0, 620.0), (0, 0, 0), (1.0, 1.0, 1.0))
    # render settings
    r = sc.render
    r.engine = 'BLENDER_EEVEE'
    r.resolution_x, r.resolution_y, r.resolution_percentage = 2560, 1440, 100
    r.film_transparent = False
    r.image_settings.file_format = 'PNG'
    r.image_settings.color_depth = '8'
    r.image_settings.compression = 15
    ee = sc.eevee
    ee.taa_render_samples = 128
    ee.use_raytracing = True
    ee.use_shadows = True
    ee.shadow_ray_count = 3
    ee.shadow_step_count = 12
    ee.use_fast_gi = True
    ee.fast_gi_quality = 1.0
    ee.fast_gi_distance = 30.0
    try:
        ee.ray_tracing_method = 'SCREEN'
        ee.ray_tracing_options.resolution_scale = '1'
        ee.ray_tracing_options.use_denoise = True
    except Exception as e:
        print("raytrace option:", e)
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - High Contrast'
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    sc.display_settings.display_device = 'sRGB'
    return sc


def get_cam(name):
    ob = D.objects.get(name)
    if ob is None:
        cd = D.cameras.new(name)
        ob = D.objects.new(name, cd)
        bpy.context.scene.collection.objects.link(ob)
    return ob


def frame_camera(cam, direction, lens, pts, margin=0.06):
    sc = bpy.context.scene
    center = sum(pts, Vector()) / len(pts)
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center = (lo + hi) / 2
    d = direction.normalized()
    cd = cam.data
    cd.clip_start, cd.clip_end = 1.0, 5000.0
    cd.sensor_fit = 'HORIZONTAL'
    cd.sensor_width = 36.0
    up = 'Y' if abs(d.z) < 0.99 else 'Y'
    if lens is None:
        cd.type = 'ORTHO'
        cam.location = center + d * 900.0
        cam.rotation_euler = (0, 0, 0) if d.z > 0.99 else (-d).to_track_quat('-Z', 'Y').to_euler()
        cd.ortho_scale = 300.0
    else:
        cd.type = 'PERSP'
        cd.lens = lens
        cam.location = center + d * 400.0
        cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    # iterasi: sesuaikan jarak/skala sampai semua titik masuk frame dengan margin
    for _ in range(40):
        bpy.context.view_layer.update()
        co = [world_to_camera_view(sc, cam, p) for p in pts]
        xs = [c.x for c in co]; ys = [c.y for c in co]
        ext = max(max(xs) - 0.5, 0.5 - min(xs), max(ys) - 0.5, 0.5 - min(ys))
        cx = (max(xs) + min(xs)) / 2 - 0.5
        cy = (max(ys) + min(ys)) / 2 - 0.5
        target = 0.5 - margin
        f = ext / target
        # geser pusat
        mw = cam.matrix_world.to_3x3()
        if cd.type == 'ORTHO':
            w = cd.ortho_scale
            h = w * sc.render.resolution_y / sc.render.resolution_x
            cam.location += mw @ Vector((cx * w, cy * h, 0))
            cd.ortho_scale *= f
        else:
            dist = (cam.location - center).length
            fov_w = 2 * math.atan(cd.sensor_width / (2 * cd.lens))
            w = 2 * dist * math.tan(fov_w / 2)
            h = w * sc.render.resolution_y / sc.render.resolution_x
            cam.location += mw @ Vector((cx * w, cy * h, 0)) * 0.9
            cam.location = center + (cam.location - center) * (1 + (f - 1) * 0.9)
        if abs(f - 1) < 0.004 and abs(cx) < 0.003 and abs(cy) < 0.003:
            break
    return cam


def setup_view(name):
    direction, lens, fname = VIEWS[name]
    pts = scene_bbox()
    cam = get_cam(f"Cam_{name.capitalize()}")
    frame_camera(cam, direction, lens, pts, margin=0.045 if name != 'top' else 0.035)
    return cam, fname


def render_view(name):
    cam, fname = setup_view(name)
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.filepath = f"{OUT_DIR}/{fname}"
    bpy.ops.render.render(write_still=True)
    return sc.render.filepath


def render_all():
    out = []
    for n in VIEWS:
        out.append(render_view(n))
    return out
