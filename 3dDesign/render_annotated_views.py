#!/usr/bin/env python3
"""
Script Blender (bpy) untuk:
1. Menambahkan label keterangan komponen 3D + leader line (Beveled Curve) pada hardware assembly.
2. Billboard effect (TRACK_TO constraint) agar teks selalu menghadap kamera aktif.
3. Multi-angle camera & batch render 3 sudut ke ./renders/ (1920x1080):
   - render_top_ortho.png   (Top-Down Orthographic)
   - render_isometric.png   (Isometric 45-degree Perspective)
   - render_front_angle.png (Front Low-Angle Perspective)
4. Menyimpan scene baru ke file .blend terpisah (<output>.blend).

Penggunaan Terminal CLI:
  blender input.blend --background --python render_annotated_views.py -- output.blend
"""

import bpy
import math
import os
import sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

# ==============================================================================
# 1. KONFIGURASI ANOTASI KOMPONEN (Dictionary Python)
#    - target: koordinat titik kontak pada fisik komponen (mm)
#    - label : koordinat posisi melayang teks keterangan 3D (mm)
#    - text  : teks label keterangan
# ==============================================================================
ANNOTATIONS_CONFIG = {
    "esp32": {
        "text": "ESP32 DevKit",
        "desc": "Microcontroller board hitam",
        "target": Vector((6.35, -14.0, 19.5)),
        "label": Vector((58.0, 2.0, 32.0)),
        "text_size": 4.5,
    },
    "oled": {
        "text": "OLED Display 0.96\"",
        "desc": "Layar atas / display",
        "target": Vector((-14.0, -104.0, 16.5)),
        "label": Vector((-14.0, -135.0, 22.0)),
        "text_size": 4.5,
    },
    "antenna": {
        "text": "2.4GHz Antenna + SMA Connector",
        "desc": "Antena batang dan konektor SMA",
        "target": Vector((72.0, -45.0, 8.5)),
        "label": Vector((96.0, -45.0, 26.0)),
        "text_size": 4.2,
    },
    "battery": {
        "text": "3.7V 1200mAh Li-Po Battery",
        "desc": "Baterai Li-Po",
        "target": Vector((-61.7, -22.3, 6.5)),
        "label": Vector((-108.0, -22.0, 20.0)),
        "text_size": 4.5,
    },
    "tp4056": {
        "text": "TP4056 Charger Module",
        "desc": "Modul charger USB Type-C",
        "target": Vector((-71.1, 38.6, 2.5)),
        "label": Vector((-108.0, 38.0, 24.0)),
        "text_size": 4.5,
    },
    "switch": {
        "text": "Power Switch (SPST)",
        "desc": "Saklar rocker hitam",
        "target": Vector((-62.8, 64.6, 10.5)),
        "label": Vector((-98.0, 68.0, 30.0)),
        "text_size": 4.5,
    },
    "fsr": {
        "text": "FSR Sensors (2x)",
        "desc": "Sensor strip elektrokimia / tekanan",
        "target": Vector((-32.0, -63.0, 1.5)),
        "label": Vector((-32.0, -82.0, 20.0)),
        "text_size": 4.5,
    },
    "opa": {
        "text": "Signal Conditioning / Op-Amps",
        "desc": "Modul pengkondisi sinyal OPA2333",
        "target": Vector((0.0, 28.0, 9.0)),
        "label": Vector((15.0, 62.0, 30.0)),
        "text_size": 4.2,
    },
    "probe": {
        "text": "Finger Probe Sensors (3x)",
        "desc": "Adapter sensor elektroda silinder",
        "target": Vector((-75.0, 94.5, 7.0)),
        "label": Vector((-115.0, 112.0, 36.0)),
        "text_size": 4.2,
    },
    "ads1115": {
        "text": "Sensor Breakout Board",
        "desc": "Board ADC ADS1115 di atas perfboard",
        "target": Vector((-25.85, -10.16, 8.5)),
        "label": Vector((-48.0, 8.0, 30.0)),
        "text_size": 4.5,
    },
}

# ==============================================================================
# 2. DEFINISI SUDUT KAMERA & RENDER
# ==============================================================================
VIEW_CAMERAS = {
    "render_top_ortho.png": {
        "name": "Cam_Top_Annotated",
        "type": "ORTHO",
        "direction": Vector((0.0, 0.0, 1.0)),
        "lens": None,
        "margin": 0.05,
        "desc": "Tampilan Top-Down Orthographic",
    },
    "render_isometric.png": {
        "name": "Cam_Isometric_Annotated",
        "type": "PERSP",
        "direction": Vector((-0.60, -0.80, 0.65)),
        "lens": 60.0,
        "margin": 0.06,
        "desc": "Sudut Isometrik 45 derajat (Perspective)",
    },
    "render_front_angle.png": {
        "name": "Cam_Front_Annotated",
        "type": "PERSP",
        "direction": Vector((-0.55, -0.80, 0.32)),
        "lens": 65.0,
        "margin": 0.06,
        "desc": "Sudut depan miring (Low-angle Perspective)",
    },
}


def get_or_create_collection(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def get_or_create_materials():
    """Membuat material Emissive White untuk teks dan Neon Cyan untuk leader line."""
    # 1. Text material (Emissive White)
    mat_text = bpy.data.materials.get("Mat_Annotation_Text_White")
    if not mat_text:
        mat_text = bpy.data.materials.new("Mat_Annotation_Text_White")
        mat_text.use_nodes = True
        nodes = mat_text.node_tree.nodes
        nodes.clear()
        out = nodes.new('ShaderNodeOutputMaterial')
        emi = nodes.new('ShaderNodeEmission')
        emi.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        emi.inputs['Strength'].default_value = 3.0
        mat_text.node_tree.links.new(emi.outputs['Emission'], out.inputs['Surface'])

    # 2. Leader Line material (High-Contrast Tech Cyan)
    mat_line = bpy.data.materials.get("Mat_Annotation_Line_Cyan")
    if not mat_line:
        mat_line = bpy.data.materials.new("Mat_Annotation_Line_Cyan")
        mat_line.use_nodes = True
        nodes = mat_line.node_tree.nodes
        nodes.clear()
        out = nodes.new('ShaderNodeOutputMaterial')
        emi = nodes.new('ShaderNodeEmission')
        emi.inputs['Color'].default_value = (0.05, 0.78, 1.0, 1.0)
        emi.inputs['Strength'].default_value = 2.2
        mat_line.node_tree.links.new(emi.outputs['Emission'], out.inputs['Surface'])

    return mat_text, mat_line


def setup_annotations(config, initial_target_cam=None):
    """
    Membuat collection 'Component_Annotations' beserta:
    - 3D Text (Emissive White)
    - Billboard tracking constraint (TRACK_TO)
    - Leader lines (Beveled Curves)
    - Terminal anchor spheres di titik komponen
    """
    col = get_or_create_collection("Component_Annotations")
    mat_text, mat_line = get_or_create_materials()

    # Bersihkan objek anotasi lama jika pernah dibuat
    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    text_objects = []

    for key, cfg in config.items():
        text_str = cfg["text"]
        target = Vector(cfg["target"])
        label = Vector(cfg["label"])
        size = cfg.get("text_size", 4.5)

        # A. 3D Text object
        font_curve = bpy.data.curves.new(name=f"Curve_Text_{key}", type='FONT')
        font_curve.body = text_str
        font_curve.size = size
        font_curve.extrude = 0.35
        font_curve.bevel_depth = 0.04
        font_curve.align_x = 'CENTER'
        font_curve.align_y = 'CENTER'
        font_curve.materials.append(mat_text)

        text_obj = bpy.data.objects.new(name=f"Text_{key}", object_data=font_curve)
        text_obj.location = label
        col.objects.link(text_obj)

        # Billboard TRACK_TO constraint
        con = text_obj.constraints.new(type='TRACK_TO')
        con.name = "Billboard_Track"
        con.track_axis = 'TRACK_Z'
        con.up_axis = 'UP_Y'
        if initial_target_cam:
            con.target = initial_target_cam

        # B. Leader Line (Beveled 3D Curve)
        curve_data = bpy.data.curves.new(name=f"Curve_Leader_{key}", type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.bevel_depth = 0.45
        curve_data.bevel_resolution = 3
        curve_data.materials.append(mat_line)

        spline = curve_data.splines.new('POLY')
        # Titik elbow peralihan ketinggian dan ujung bawah label
        z_mid = target.z + (label.z - target.z) * 0.45
        elbow = Vector((label.x, label.y, z_mid))
        end_pt = Vector((label.x, label.y, label.z - size * 0.70))

        spline.points.add(2)
        spline.points[0].co = (target.x, target.y, target.z, 1.0)
        spline.points[1].co = (elbow.x, elbow.y, elbow.z, 1.0)
        spline.points[2].co = (end_pt.x, end_pt.y, end_pt.z, 1.0)

        line_obj = bpy.data.objects.new(name=f"Leader_{key}", object_data=curve_data)
        col.objects.link(line_obj)

        # C. Anchor sphere di titik kontak komponen
        import bmesh
        mesh_dot = bpy.data.meshes.new(f"Mesh_Dot_{key}")
        dot_obj = bpy.data.objects.new(f"Dot_{key}", mesh_dot)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        bm.to_mesh(mesh_dot)
        bm.free()
        mesh_dot.materials.append(mat_line)
        dot_obj.location = target
        col.objects.link(dot_obj)

        text_objects.append(text_obj)

    print(f"[OK] {len(text_objects)} label komponen 3D berhasil ditambahkan ke collection 'Component_Annotations'.")
    return text_objects


def ensure_lighting():
    """Memastikan studio lighting / fill & sun light cukup terang."""
    sc = bpy.context.scene
    existing_lights = [o for o in bpy.data.objects if o.type == 'LIGHT']
    if not existing_lights:
        print("[INFO] Tidak ada lampu di scene. Menambahkan studio lights...")
        # Key Sun
        ld = bpy.data.lights.new("Sun_Main", 'SUN')
        ld.energy = 5.0
        ld.color = (1.0, 0.98, 0.95)
        ob = bpy.data.objects.new("Sun_Main", ld)
        sc.collection.objects.link(ob)
        ob.rotation_euler = (math.radians(50), math.radians(20), math.radians(45))

        # Fill Area
        ld_fill = bpy.data.lights.new("Fill_Area", 'AREA')
        ld_fill.energy = 2000.0
        ld_fill.size = 300.0
        ld_fill.color = (0.9, 0.95, 1.0)
        ob_fill = bpy.data.objects.new("Fill_Area", ld_fill)
        sc.collection.objects.link(ob_fill)
        ob_fill.location = (-200.0, -200.0, 300.0)
    else:
        # Naikkan energi jika lampu terlalu redup (scene skala mm membutuhkan energi tinggi)
        for ob in existing_lights:
            if ob.data.type == 'AREA' and ob.data.energy < 10000.0:
                ob.data.energy = max(ob.data.energy, 500000.0)


def get_all_scene_points():
    """Mengambil seluruh titik bounding box objek elektronik & anotasi untuk auto-framing."""
    pts = []
    target_collections = ["PKM_Electronics_Assembly", "Component_Annotations"]
    for col_name in target_collections:
        col = bpy.data.collections.get(col_name)
        if not col:
            continue
        for ob in col.all_objects:
            if ob.type not in {'MESH', 'CURVE', 'FONT'} or ob.hide_render:
                continue
            if ob.bound_box:
                for c in ob.bound_box:
                    pts.append(ob.matrix_world @ Vector(c))
    if not pts:
        pts = [Vector((-50, -50, 0)), Vector((50, 50, 30))]
    return pts


def get_or_create_camera(name):
    ob = bpy.data.objects.get(name)
    if not ob or ob.type != 'CAMERA':
        if ob:
            bpy.data.objects.remove(ob, do_unlink=True)
        cd = bpy.data.cameras.new(name)
        ob = bpy.data.objects.new(name, cd)
        bpy.context.scene.collection.objects.link(ob)
    return ob


def frame_camera(cam, direction, lens, pts, margin=0.06):
    """Secara otomatis menyesuaikan jarak, rotasi, dan framing kamera agar seluruh objek masuk kanvas."""
    sc = bpy.context.scene
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center = (lo + hi) * 0.5
    d = direction.normalized()
    cd = cam.data
    cd.clip_start, cd.clip_end = 1.0, 5000.0
    cd.sensor_fit = 'HORIZONTAL'
    cd.sensor_width = 36.0

    if lens is None:
        cd.type = 'ORTHO'
        cam.location = center + d * 900.0
        cam.rotation_euler = (0, 0, 0) if d.z > 0.99 else (-d).to_track_quat('-Z', 'Y').to_euler()
        cd.ortho_scale = max(hi.x - lo.x, hi.y - lo.y) * 1.35
    else:
        cd.type = 'PERSP'
        cd.lens = lens
        cam.location = center + d * 450.0
        cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()

    sc.camera = cam

    # Iteratif presisi framing
    for _ in range(30):
        bpy.context.view_layer.update()
        co = [world_to_camera_view(sc, cam, p) for p in pts]
        xs = [c.x for c in co]
        ys = [c.y for c in co]
        ext = max(max(xs) - 0.5, 0.5 - min(xs), max(ys) - 0.5, 0.5 - min(ys))
        cx = (max(xs) + min(xs)) / 2 - 0.5
        cy = (max(ys) + min(ys)) / 2 - 0.5
        target = 0.5 - margin
        f = ext / target
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
        if abs(f - 1) < 0.005 and abs(cx) < 0.005 and abs(cy) < 0.005:
            break
    return cam


def update_billboard_for_render(cam, is_ortho):
    """
    Menyelaraskan rotasi billboard teks 3D:
    - Pada kamera ORTHO (Top view): teks didatarkan (rot=0,0,0) agar 100% horizontal dan terbaca tegak lurus.
    - Pada kamera PERSP: billboard constraint aktif melacak posisi kamera.
    """
    col = bpy.data.collections.get("Component_Annotations")
    if not col:
        return
    for ob in col.objects:
        if ob.type == 'FONT':
            con = ob.constraints.get("Billboard_Track")
            if is_ortho:
                if con:
                    con.mute = True
                ob.rotation_euler = (0, 0, 0)
            else:
                if con:
                    con.mute = False
                    con.target = cam


def render_all_views(out_dir="./renders"):
    """
    Mengatur 3 kamera dan me-render 3 sudut pandang secara otomatis:
    1. render_top_ortho.png
    2. render_isometric.png
    3. render_front_angle.png
    """
    sc = bpy.context.scene
    os.makedirs(out_dir, exist_ok=True)

    # Render settings: 1920x1080 PNG RGBA
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.image_settings.color_depth = '8'

    # EEVEE optimization
    sc.eevee.taa_render_samples = 64
    sc.eevee.use_raytracing = True
    sc.eevee.use_fast_gi = True

    pts = get_all_scene_points()
    rendered_files = []

    for filename, cfg in VIEW_CAMERAS.items():
        cam = get_or_create_camera(cfg["name"])
        is_ortho = (cfg["type"] == "ORTHO")
        frame_camera(cam, cfg["direction"], cfg["lens"], pts, margin=cfg["margin"])
        update_billboard_for_render(cam, is_ortho)
        bpy.context.view_layer.update()

        sc.camera = cam
        out_filepath = os.path.abspath(os.path.join(out_dir, filename))
        sc.render.filepath = out_filepath

        print(f"[RENDER] Menghasilkan {filename} ({cfg['desc']})...")
        bpy.ops.render.render(write_still=True)
        rendered_files.append(out_filepath)
        print(f"[OK] Disimpan ke: {out_filepath}")

    return rendered_files


def save_annotated_blend(output_blend_path):
    """Menyimpan scene yang telah dianotasi ke file .blend baru tanpa mengubah file asli."""
    # Pastikan default camera adalah Isometric
    cam_iso = bpy.data.objects.get("Cam_Isometric_Annotated")
    if cam_iso:
        bpy.context.scene.camera = cam_iso
        update_billboard_for_render(cam_iso, is_ortho=False)
        bpy.context.view_layer.update()

    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(output_blend_path), copy=True)
    print(f"[OK] File Blender baru berhasil disimpan ke: {os.path.abspath(output_blend_path)}")


def parse_cli_args():
    """Membaca argumen terminal setelah pemisah '--'."""
    args = sys.argv
    output_blend = "output_annotated.blend"
    out_renders_dir = "./renders"

    if "--" in args:
        user_args = args[args.index("--") + 1:]
        if len(user_args) >= 1 and user_args[0].endswith(".blend"):
            output_blend = user_args[0]
        if len(user_args) >= 2:
            out_renders_dir = user_args[1]

    return output_blend, out_renders_dir


def main():
    print("=" * 70)
    print("PKM-GLICOVIA: 3D ANNOTATIONS & MULTI-VIEW BATCH RENDER")
    print("=" * 70)

    output_blend, out_renders_dir = parse_cli_args()

    # 1. Pastikan pencahayaan memadai
    ensure_lighting()

    # 2. Tambahkan anotasi 3D dan leader lines
    setup_annotations(ANNOTATIONS_CONFIG)

    # 3. Batch render 3 sudut pandang
    rendered = render_all_views(out_dir=out_renders_dir)

    # 4. Simpan ke file .blend baru
    save_annotated_blend(output_blend)

    print("=" * 70)
    print("EKSEKUSI SELESAI:")
    print(f"1. File Blend Baru : {os.path.abspath(output_blend)}")
    print(f"2. File Renders ({len(rendered)} file):")
    for r in rendered:
        print(f"   - {r}")
    print("=" * 70)


if __name__ == "__main__":
    main()
