import bpy
import bmesh
import math
import mathutils
import os

scene = bpy.context.scene

# 1. Reset / Prepare Electronics Collection
col_name = "PKM_Electronics_Assembly"
col = bpy.data.collections.get(col_name)
if not col:
    col = bpy.data.collections.new(col_name)
    scene.collection.children.link(col)

# Clear existing objects in collection
for obj in list(col.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# 2. Materials Helper
def get_or_create_mat(name, color, roughness=0.3, metallic=0.0, transmission=0.0, ior=1.45):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = transmission
        if 'IOR' in bsdf.inputs:
            bsdf.inputs['IOR'].default_value = ior
    return mat

get_or_create_mat("Mat_FR4_Green", (0.015, 0.28, 0.08, 1.0), roughness=0.25)
get_or_create_mat("Mat_PCB_Blue", (0.01, 0.08, 0.45, 1.0), roughness=0.22)
get_or_create_mat("Mat_PCB_Black", (0.03, 0.03, 0.035, 1.0), roughness=0.35)
get_or_create_mat("Mat_IC_Molded", (0.02, 0.02, 0.02, 1.0), roughness=0.6)
get_or_create_mat("Mat_Metal_Silver", (0.85, 0.86, 0.88, 1.0), roughness=0.2, metallic=0.95)
get_or_create_mat("Mat_Brass_Gold", (0.95, 0.72, 0.15, 1.0), roughness=0.25, metallic=0.92)
get_or_create_mat("Mat_Solder_Tin", (0.75, 0.78, 0.82, 1.0), roughness=0.18, metallic=0.9)
get_or_create_mat("Mat_Rubber_Black", (0.025, 0.025, 0.028, 1.0), roughness=0.55)
get_or_create_mat("Mat_Battery_Silver", (0.75, 0.77, 0.8, 1.0), roughness=0.35, metallic=0.85)
get_or_create_mat("Mat_Kapton_Amber", (0.78, 0.45, 0.02, 0.85), roughness=0.18, transmission=0.45)
get_or_create_mat("Mat_Switch_Red", (0.85, 0.05, 0.04, 1.0), roughness=0.3)
get_or_create_mat("Mat_Plastic_Black", (0.02, 0.02, 0.02, 1.0), roughness=0.4)
get_or_create_mat("Mat_JST_White", (0.92, 0.92, 0.9, 1.0), roughness=0.35)
get_or_create_mat("Mat_Adapter_Blue", (0.02, 0.18, 0.75, 1.0), roughness=0.45)
get_or_create_mat("Mat_Glass_OLED", (0.02, 0.025, 0.035, 1.0), roughness=0.05, ior=1.52)
get_or_create_mat("Mat_SPE_White", (0.95, 0.96, 0.95, 1.0), roughness=0.3)
get_or_create_mat("Mat_SPE_Green", (0.1, 0.55, 0.35, 1.0), roughness=0.28)
get_or_create_mat("Mat_SPE_Carbon", (0.015, 0.015, 0.018, 1.0), roughness=0.7)
get_or_create_mat("Mat_Wire_Red", (0.85, 0.03, 0.02, 1.0), roughness=0.35)
get_or_create_mat("Mat_Wire_Black", (0.02, 0.02, 0.02, 1.0), roughness=0.35)
get_or_create_mat("Mat_Wire_Yellow", (0.9, 0.75, 0.02, 1.0), roughness=0.35)
get_or_create_mat("Mat_Wire_White", (0.92, 0.92, 0.92, 1.0), roughness=0.35)
get_or_create_mat("Mat_Wire_Blue", (0.02, 0.15, 0.85, 1.0), roughness=0.35)

# 3. Geometry Helpers
def add_box(name, size, loc, rot=(0,0,0), mat_name=None, bevel=0.0):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj.location = loc
    obj.rotation_euler = rot
    if mat_name:
        mat = bpy.data.materials.get(mat_name)
        if mat:
            obj.data.materials.append(mat)
    if bevel > 0.0:
        bev = obj.modifiers.new(name="Bevel", type='BEVEL')
        bev.width = bevel
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        bev.angle_limit = math.radians(35)
    return obj

def add_cyl(name, r1, r2, depth, loc, rot=(0,0,0), mat_name=None, segs=24):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r1, radius2=r2, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    obj.location = loc
    obj.rotation_euler = rot
    if mat_name:
        mat = bpy.data.materials.get(mat_name)
        if mat:
            obj.data.materials.append(mat)
    return obj

def add_ic_sop(name, body_size, loc, num_pins, mat_ic="Mat_IC_Molded", mat_pin="Mat_Solder_Tin"):
    ic_body = add_box(f"{name}_Body", body_size, (loc[0], loc[1], loc[2] + body_size[2]/2), mat_name=mat_ic, bevel=0.15)
    add_cyl(f"{name}_Dot", 0.35, 0.35, 0.1, (loc[0] - body_size[0]/2 + 0.6, loc[1] + body_size[1]/2 - 0.6, loc[2] + body_size[2] + 0.05), mat_name=mat_ic, segs=12)
    pins_per_side = num_pins // 2
    pitch = (body_size[1] - 0.8) / (pins_per_side - 1) if pins_per_side > 1 else 1.0
    for side in [-1, 1]:
        for p in range(pins_per_side):
            py = loc[1] + (body_size[1]/2 - 0.4) - p * pitch
            px = loc[0] + side * (body_size[0]/2 + 0.45)
            add_box(f"{name}_Pin_{side}_{p}", (0.9, 0.35, 0.2), (px, py, loc[2] + 0.1), mat_name=mat_pin)
    return ic_body

def add_pin_header(name, num_pins, pitch, loc, rot=(0,0,0), pin_len=8.5, is_gold=True):
    total_len = num_pins * pitch
    add_box(f"{name}_Plastic", (2.5, total_len, 2.5), (loc[0], loc[1], loc[2] + 1.25), rot=rot, mat_name="Mat_Plastic_Black", bevel=0.15)
    mat_pin = "Mat_Brass_Gold" if is_gold else "Mat_Solder_Tin"
    for p in range(num_pins):
        py = loc[1] - total_len/2 + pitch * (p + 0.5)
        add_box(f"{name}_Pin_{p+1}", (0.64, 0.64, pin_len), (loc[0], py, loc[2] + pin_len/2 - 2.5), rot=rot, mat_name=mat_pin)

def add_smd_passive(name, size, loc, rot=(0,0,0), mat_body="Mat_IC_Molded"):
    add_box(f"{name}_Body", (size[0]*0.6, size[1], size[2]), loc, rot=rot, mat_name=mat_body)
    cap_w = size[0]*0.2
    add_box(f"{name}_Cap1", (cap_w, size[1], size[2]), (loc[0] - size[0]/2 + cap_w/2, loc[1], loc[2]), rot=rot, mat_name="Mat_Solder_Tin")
    add_box(f"{name}_Cap2", (cap_w, size[1], size[2]), (loc[0] + size[0]/2 - cap_w/2, loc[1], loc[2]), rot=rot, mat_name="Mat_Solder_Tin")

def add_curve_wire(name, points, radius, mat_name):
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.fill_mode = 'FULL'
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = 4
    polyline = curve_data.splines.new('BEZIER')
    polyline.bezier_points.add(len(points) - 1)
    for i, pt in enumerate(points):
        bp = polyline.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, curve_data)
    col.objects.link(obj)
    if mat_name:
        mat = bpy.data.materials.get(mat_name)
        if mat:
            obj.data.materials.append(mat)
    return obj

# ==========================================
# 4. BUILD COMPONENTS
# ==========================================

# 1. Main Perfboard
pcb_main = add_box("Main_Perfboard", (50.0, 70.0, 1.6), (0.0, 0.0, 0.8), mat_name="Mat_FR4_Green", bevel=0.3)
for cx, cy in [(-22.0, -32.0), (22.0, -32.0), (-22.0, 32.0), (22.0, 32.0)]:
    add_cyl(f"Pad_M3_{cx}_{cy}", 2.5, 2.5, 0.1, (cx, cy, 1.65), mat_name="Mat_Solder_Tin", segs=16)
for gx in range(-8, 9, 2):
    for gy in range(-12, 13, 3):
        add_cyl(f"Via_{gx}_{gy}", 0.7, 0.7, 0.05, (gx * 2.54, gy * 2.54, 1.62), mat_name="Mat_Solder_Tin", segs=8)
add_box("Rail_L", (1.2, 64.0, 0.05), (-23.5, 0.0, 1.62), mat_name="Mat_Solder_Tin")
add_box("Rail_R", (1.2, 64.0, 0.05), (23.5, 0.0, 1.62), mat_name="Mat_Solder_Tin")

# 2. ESP32 DevKit V1
esp_x, esp_y = 4.0, -8.0
esp_pcb = add_box("ESP32_PCB", (28.0, 51.5, 1.6), (esp_x, esp_y, 1.6 + 0.8), mat_name="Mat_PCB_Black", bevel=0.25)
add_box("ESP32_Ant_Trace_Area", (18.0, 7.0, 0.05), (esp_x, esp_y + 22.0, 3.22), mat_name="Mat_Brass_Gold")
add_box("ESP32_Shield_Rim", (18.0, 18.0, 2.8), (esp_x, esp_y + 7.5, 3.2 + 1.4), mat_name="Mat_Metal_Silver", bevel=0.3)
add_box("ESP32_Shield_Label", (15.0, 15.0, 0.05), (esp_x, esp_y + 7.5, 3.2 + 2.82), mat_name="Mat_Metal_Silver")
add_cyl("ESP32_IPEX_Base", 1.3, 1.3, 1.4, (esp_x + 6.5, esp_y + 14.5, 3.2 + 0.7), mat_name="Mat_Brass_Gold", segs=16)
add_cyl("ESP32_IPEX_Pin", 0.35, 0.35, 0.8, (esp_x + 6.5, esp_y + 14.5, 3.2 + 1.4 + 0.4), mat_name="Mat_Brass_Gold", segs=8)
add_box("ESP32_USB_Shell", (7.5, 5.8, 3.0), (esp_x, esp_y - 23.5, 3.2 + 1.5), mat_name="Mat_Metal_Silver", bevel=0.2)
add_box("ESP32_USB_Hole", (5.5, 1.5, 1.6), (esp_x, esp_y - 26.0, 3.2 + 1.5), mat_name="Mat_Plastic_Black")
add_box("AMS1117_Body", (6.5, 3.5, 1.6), (esp_x - 3.5, esp_y - 12.0, 3.2 + 0.8), mat_name="Mat_IC_Molded")
add_box("AMS1117_Tab", (3.0, 1.5, 0.2), (esp_x - 3.5, esp_y - 10.0, 3.2 + 0.2), mat_name="Mat_Solder_Tin")
for p in range(3):
    add_box(f"AMS1117_Lead_{p}", (0.8, 1.5, 0.2), (esp_x - 5.5 + p * 2.0, esp_y - 14.2, 3.2 + 0.2), mat_name="Mat_Solder_Tin")
add_box("CP2102_IC", (5.0, 5.0, 0.9), (esp_x, esp_y - 15.0, 3.2 + 0.45), mat_name="Mat_IC_Molded", bevel=0.1)
for bname, bx in [("EN", esp_x - 7.5), ("BOOT", esp_x + 7.5)]:
    add_box(f"ESP32_Btn_{bname}_Base", (3.5, 3.5, 1.5), (bx, esp_y - 22.0, 3.2 + 0.75), mat_name="Mat_Metal_Silver")
    add_cyl(f"ESP32_Btn_{bname}_Actuator", 0.9, 0.9, 0.8, (bx, esp_y - 22.0, 3.2 + 1.5 + 0.4), mat_name="Mat_Plastic_Black", segs=12)
add_pin_header("ESP32_Pins_L", 15, 2.54, (esp_x - 12.7, esp_y, 1.6), pin_len=8.5, is_gold=True)
add_pin_header("ESP32_Pins_R", 15, 2.54, (esp_x + 12.7, esp_y, 1.6), pin_len=8.5, is_gold=True)
add_smd_passive("ESP32_LED_PWR", (1.6, 0.8, 0.6), (esp_x - 4.5, esp_y - 18.0, 3.2 + 0.3), mat_body="Mat_Wire_Red")
add_smd_passive("ESP32_LED_IO2", (1.6, 0.8, 0.6), (esp_x + 4.5, esp_y - 18.0, 3.2 + 0.3), mat_body="Mat_Wire_Blue")
add_smd_passive("ESP32_Res_1", (1.6, 0.8, 0.6), (esp_x - 2.0, esp_y - 18.0, 3.2 + 0.3))
add_smd_passive("ESP32_Res_2", (1.6, 0.8, 0.6), (esp_x + 2.0, esp_y - 18.0, 3.2 + 0.3))

# 3. ADS1115 Breakout Module
ads_x, ads_y = -15.5, 14.0
add_box("ADS1115_PCB", (17.0, 28.0, 1.6), (ads_x, ads_y, 1.6 + 0.8), mat_name="Mat_PCB_Blue", bevel=0.3)
add_ic_sop("ADS1115_IC", (3.0, 4.8, 1.1), (ads_x, ads_y + 4.0, 3.2), num_pins=10)
add_pin_header("ADS1115_Pins", 10, 2.54, (ads_x - 6.5, ads_y, 1.6), pin_len=8.0, is_gold=True)
for rp in [-2.0, 0.0, 2.0]:
    add_smd_passive(f"ADS_Res_{rp}", (1.6, 0.8, 0.5), (ads_x + 3.0, ads_y + rp, 3.2 + 0.25))

# 4. 3x OPA Breakouts
for i, y_pos in enumerate([25.0, 11.0, -3.0]):
    add_box(f"OPA_Adapter_{i+1}", (10.0, 10.0, 1.6), (18.5, y_pos, 1.6 + 0.8), mat_name="Mat_FR4_Green", bevel=0.2)
    add_ic_sop(f"OPA_IC_{i+1}", (4.0, 5.0, 1.4), (18.5, y_pos, 3.2), num_pins=8)
    for p in range(4):
        add_box(f"OPA_PinL_{i+1}_{p}", (0.64, 0.64, 5.0), (14.5, y_pos - 3.81 + p * 2.54, 1.6 + 2.5), mat_name="Mat_Brass_Gold")
        add_box(f"OPA_PinR_{i+1}_{p}", (0.64, 0.64, 5.0), (22.5, y_pos - 3.81 + p * 2.54, 1.6 + 2.5), mat_name="Mat_Brass_Gold")
    add_cyl(f"OPA_Cap_Blue_{i+1}", 1.4, 1.4, 3.2, (12.5, y_pos - 3.0, 3.2 + 1.6), mat_name="Mat_Wire_Blue")
    add_cyl(f"OPA_Cap_Disc_{i+1}", 1.8, 1.8, 1.0, (12.5, y_pos + 3.0, 3.2 + 1.6), rot=(0, math.radians(90), 0), mat_name="Mat_Kapton_Amber")

# 5. TP4056 USB-C Charger Module
tp_x, tp_y = -52.0, 32.0
add_box("TP4056_PCB", (17.3, 28.0, 1.6), (tp_x, tp_y, 0.8), mat_name="Mat_PCB_Blue", bevel=0.3)
add_box("TP4056_TypeC_Shell", (8.9, 7.3, 3.2), (tp_x, tp_y + 12.0, 1.6 + 1.6), mat_name="Mat_Metal_Silver", bevel=0.3)
add_box("TP4056_TypeC_Hole", (6.5, 1.5, 1.8), (tp_x, tp_y + 15.2, 1.6 + 1.6), mat_name="Mat_Plastic_Black")
add_box("TP4056_TypeC_Tongue", (5.0, 1.2, 0.5), (tp_x, tp_y + 14.8, 1.6 + 1.6), mat_name="Mat_Plastic_Black")
add_ic_sop("TP4056_IC_Chg", (4.0, 5.0, 1.4), (tp_x, tp_y + 3.0, 1.6), num_pins=8)
add_ic_sop("TP4056_IC_Prot", (2.8, 3.0, 1.2), (tp_x - 3.5, tp_y - 6.0, 1.6), num_pins=6)
add_ic_sop("TP4056_IC_Mosfet", (4.0, 5.0, 1.2), (tp_x + 3.5, tp_y - 6.0, 1.6), num_pins=8)
add_smd_passive("TP4056_LED_Red", (1.6, 0.8, 0.6), (tp_x - 5.5, tp_y + 6.0, 1.6 + 0.3), mat_body="Mat_Wire_Red")
add_smd_passive("TP4056_LED_Blue", (1.6, 0.8, 0.6), (tp_x - 5.5, tp_y + 3.0, 1.6 + 0.3), mat_body="Mat_Wire_Blue")
for px, py in [(tp_x - 6.5, tp_y - 12.0), (tp_x - 2.5, tp_y - 12.0), (tp_x + 2.5, tp_y - 12.0), (tp_x + 6.5, tp_y - 12.0)]:
    add_cyl(f"TP_Pad_{px}_{py}", 1.2, 1.2, 0.1, (px, py, 1.65), mat_name="Mat_Solder_Tin", segs=12)

# 6. LiPo Pouch Battery (with crimp edges & Kapton tape)
bat_x, bat_y = -52.0, -10.0
add_box("LiPo_Core", (32.0, 46.0, 6.8), (bat_x, bat_y, 3.4), mat_name="Mat_Battery_Silver", bevel=1.2)
add_box("LiPo_Crimp_L", (1.2, 46.0, 0.8), (bat_x - 16.6, bat_y, 3.4), mat_name="Mat_Battery_Silver")
add_box("LiPo_Crimp_R", (1.2, 46.0, 0.8), (bat_x + 16.6, bat_y, 3.4), mat_name="Mat_Battery_Silver")
add_box("LiPo_Crimp_B", (34.0, 1.5, 0.8), (bat_x, bat_y - 23.5, 3.4), mat_name="Mat_Battery_Silver")
add_box("LiPo_Kapton_Tape", (32.4, 9.0, 7.1), (bat_x, bat_y + 12.5, 3.55), mat_name="Mat_Kapton_Amber", bevel=0.2)
add_box("LiPo_PCM_Board", (28.0, 4.0, 1.2), (bat_x, bat_y + 15.0, 3.5), mat_name="Mat_PCB_Black")
add_box("LiPo_Label_Text", (20.0, 24.0, 0.05), (bat_x, bat_y - 3.0, 6.83), mat_name="Mat_Plastic_Black")

# 7. Mini Rocker Switch (KCD11)
sw_x, sw_y = -42.0, 62.0
add_box("Switch_Bezel_Base", (15.0, 10.5, 10.0), (sw_x, sw_y, 5.0), mat_name="Mat_Plastic_Black", bevel=0.4)
add_box("Switch_Flange", (16.5, 12.0, 1.2), (sw_x, sw_y, 10.0 - 0.6), mat_name="Mat_Plastic_Black", bevel=0.2)
add_box("Switch_Rocker_Btn", (12.0, 8.0, 4.0), (sw_x, sw_y, 10.0 + 1.5), rot=(math.radians(12), 0, 0), mat_name="Mat_Switch_Red", bevel=0.3)
add_cyl("Switch_Mark_O", 0.9, 0.9, 0.1, (sw_x, sw_y + 2.0, 12.8), rot=(math.radians(12), 0, 0), mat_name="Mat_JST_White", segs=16)
add_box("Switch_Mark_I", (0.3, 1.8, 0.1), (sw_x, sw_y - 2.0, 12.2), rot=(math.radians(12), 0, 0), mat_name="Mat_JST_White")
add_box("Switch_Lug_1", (4.8, 0.8, 6.0), (sw_x - 3.5, sw_y, -3.0), mat_name="Mat_Brass_Gold")
add_box("Switch_Lug_2", (4.8, 0.8, 6.0), (sw_x + 3.5, sw_y, -3.0), mat_name="Mat_Brass_Gold")

# 8. 0.96 inch I2C OLED Display (SSD1306)
oled_x, oled_y = 0.0, -75.0
add_box("OLED_PCB", (27.3, 27.8, 1.6), (oled_x, oled_y, 0.8), mat_name="Mat_PCB_Blue", bevel=0.3)
for ocx, ocy in [(-11.5, -11.5), (11.5, -11.5), (-11.5, 11.5), (11.5, 11.5)]:
    add_cyl(f"OLED_Hole_{ocx}_{ocy}", 1.4, 1.4, 1.8, (oled_x + ocx, oled_y + ocy, 0.8), mat_name="Mat_Solder_Tin", segs=16)
add_box("OLED_Glass_Substrate", (25.0, 15.0, 0.7), (oled_x, oled_y - 2.0, 1.6 + 0.35), mat_name="Mat_Glass_OLED", bevel=0.1)
add_box("OLED_Active_Panel", (21.7, 10.8, 0.2), (oled_x, oled_y - 2.0, 1.6 + 0.7 + 0.1), mat_name="Mat_PCB_Black")
add_box("OLED_FFC_Ribbon", (12.0, 8.0, 0.2), (oled_x, oled_y + 7.0, 1.7), mat_name="Mat_Kapton_Amber")
add_pin_header("OLED_Header", 4, 2.54, (oled_x, oled_y + 11.5, 1.6), rot=(0, 0, math.radians(90)), pin_len=8.0, is_gold=False)

# 9. 2.4 GHz Antenna & RP-SMA Bulkhead
ant_x, ant_y = 52.0, -15.0
add_cyl("Ant_Nut_Hex", 4.8, 4.8, 4.0, (ant_x, ant_y + 40.0, 5.0), rot=(math.radians(90), 0, 0), mat_name="Mat_Brass_Gold", segs=6)
add_cyl("Ant_Washer", 5.2, 5.2, 0.6, (ant_x, ant_y + 38.0, 5.0), rot=(math.radians(90), 0, 0), mat_name="Mat_Brass_Gold", segs=24)
add_cyl("Ant_Threaded_Barrel", 3.2, 3.2, 12.0, (ant_x, ant_y + 33.0, 5.0), rot=(math.radians(90), 0, 0), mat_name="Mat_Brass_Gold", segs=32)
add_cyl("Ant_Swivel_Knuckle", 4.8, 4.8, 14.0, (ant_x, ant_y + 20.0, 5.0), rot=(math.radians(90), 0, 0), mat_name="Mat_Rubber_Black", segs=32)
add_cyl("Ant_Hinge_Pin", 2.0, 2.0, 9.8, (ant_x, ant_y + 20.0, 5.0), rot=(0, math.radians(90), 0), mat_name="Mat_Metal_Silver", segs=16)
add_cyl("Ant_Rubber_Body", 4.6, 3.8, 92.0, (ant_x, ant_y - 33.0, 5.0), rot=(math.radians(90), 0, 0), mat_name="Mat_Rubber_Black", segs=32)
add_cyl("Ant_Tip_Dome", 3.8, 2.0, 5.0, (ant_x, ant_y - 81.5, 5.0), rot=(math.radians(90), 0, 0), mat_name="Mat_Rubber_Black", segs=24)

# 10. 3x SPE Adapters & Exact Screen-Printed Electrodes (34 x 10 mm)
for i in range(3):
    ad_x = -52.0 + (i * 15.0)
    ad_y = 115.0
    add_box(f"SPE_Adapter_Case_{i+1}", (11.0, 28.0, 5.5), (ad_x, ad_y, 2.75), mat_name="Mat_Adapter_Blue", bevel=0.8)
    add_box(f"SPE_JST_Housing_{i+1}", (9.0, 6.0, 4.5), (ad_x, ad_y - 15.0, 2.5), mat_name="Mat_JST_White", bevel=0.2)
    for pin_i in [-2.5, 0.0, 2.5]:
        add_box(f"SPE_JST_Terminal_{i+1}_{pin_i}", (0.8, 2.0, 0.8), (ad_x + pin_i, ad_y - 17.5, 2.5), mat_name="Mat_Solder_Tin")
    
    # Accurate SPE Sensor Strip (34.0 x 10.0 x 0.4 mm)
    sp_y = ad_y + 22.0
    add_box(f"SPE_Substrate_{i+1}", (10.0, 34.0, 0.4), (ad_x, sp_y, 2.75), mat_name="Mat_SPE_White", bevel=0.1)
    add_box(f"SPE_Dielectric_Green_{i+1}", (9.2, 22.0, 0.45), (ad_x, sp_y + 5.0, 2.8), mat_name="Mat_SPE_Green")
    
    # 3 Conductive Tracks
    for trk_i in [-2.5, 0.0, 2.5]:
        add_box(f"SPE_Track_{i+1}_{trk_i}", (0.8, 26.0, 0.42), (ad_x + trk_i, sp_y - 2.0, 2.8), mat_name="Mat_Solder_Tin")
    
    # 3-Electrode Electrochemical Cell:
    # 1. Central Carbon Working Electrode (WE)
    add_cyl(f"SPE_WE_Center_{i+1}", 1.5, 1.5, 0.1, (ad_x, sp_y + 11.5, 2.85), mat_name="Mat_SPE_Carbon", segs=24)
    # 2. Reference Electrode Arc (RE)
    add_cyl(f"SPE_RE_Arc_{i+1}", 2.2, 2.2, 0.08, (ad_x, sp_y + 11.5, 2.84), mat_name="Mat_Solder_Tin", segs=24)
    # 3. Counter Electrode Outer Horseshoe Ring (CE)
    add_cyl(f"SPE_CE_Ring_{i+1}", 2.9, 2.9, 0.06, (ad_x, sp_y + 11.5, 2.83), mat_name="Mat_SPE_Carbon", segs=24)

# 11. Realistic Wire Routing
add_curve_wire("Wire_Bat_Pos", [(-50.0, 16.0, 5.0), (-55.0, 21.0, 7.5), (-56.0, 24.0, 2.0)], 0.65, "Mat_Wire_Red")
add_curve_wire("Wire_Bat_Neg", [(-54.0, 16.0, 5.0), (-58.0, 21.0, 7.0), (-57.5, 24.0, 2.0)], 0.65, "Mat_Wire_Black")

add_curve_wire("Wire_Pwr_GND", [(-46.0, 24.0, 2.0), (-35.0, 20.0, 10.0), (-20.0, 10.0, 2.5)], 0.7, "Mat_Wire_Black")
add_curve_wire("Wire_Pwr_SW1", [(-44.0, 24.0, 2.0), (-40.0, 48.0, 8.0), (-42.0, 58.0, -1.0)], 0.7, "Mat_Wire_White")
add_curve_wire("Wire_Pwr_SW2", [(-42.0, 66.0, -1.0), (-32.0, 55.0, 12.0), (-18.0, 30.0, 2.5)], 0.7, "Mat_Wire_Red")

add_curve_wire("Coax_Antenna", [
    (esp_x + 6.5, esp_y + 14.5, 5.5),
    (24.0, 18.0, 12.0),
    (40.0, 24.0, 10.0),
    (ant_x, ant_y + 40.0, 5.0)
], 0.65, "Mat_Wire_Black")

colors = ["Mat_Wire_Yellow", "Mat_Wire_Red", "Mat_Wire_Black", "Mat_Wire_White"]
for idx, cmat in enumerate(colors):
    offset_x = -3.81 + (idx * 2.54)
    add_curve_wire(f"Wire_OLED_{idx+1}", [
        (esp_x + 12.7, -18.0 + idx*2.54, 7.0),
        (26.0, -38.0 + idx*2.0, 14.0),
        (18.0, -58.0 + idx*1.5, 10.0),
        (oled_x + offset_x, oled_y + 11.5, 3.5)
    ], 0.55, cmat)

for i in range(3):
    ad_x = -52.0 + (i * 15.0)
    y_target = 25.0 - (i * 14.0)
    add_curve_wire(f"Wire_SPE_Red_{i+1}", [(ad_x - 2.5, 96.0, 2.5), (ad_x - 6.0, 72.0, 18.0 + i*3.5), (18.5, y_target + 2.5, 4.0)], 0.45, "Mat_Wire_Red")
    add_curve_wire(f"Wire_SPE_Yel_{i+1}", [(ad_x, 96.0, 2.5), (ad_x, 72.0, 16.0 + i*3.5), (18.5, y_target, 4.0)], 0.45, "Mat_Wire_Yellow")
    add_curve_wire(f"Wire_SPE_Blk_{i+1}", [(ad_x + 2.5, 96.0, 2.5), (ad_x + 6.0, 72.0, 14.0 + i*3.5), (18.5, y_target - 2.5, 4.0)], 0.45, "Mat_Wire_Black")

# ==========================================
# 5. STUDIO ENVIRONMENT & LIGHTING
# ==========================================
floor_name = "Lab_Workstation_Table"
floor = bpy.data.objects.get(floor_name)
if not floor:
    fmesh = bpy.data.meshes.new(floor_name)
    floor = bpy.data.objects.new(floor_name, fmesh)
    scene.collection.objects.link(floor)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=2, y_segments=2, size=400.0)
    bm.to_mesh(fmesh)
    bm.free()
    floor.location = (0.0, 15.0, 0.0)
    mat_table = get_or_create_mat("Mat_Lab_Table", (0.88, 0.89, 0.92, 1.0), roughness=0.32, metallic=0.35)
    floor.data.materials.append(mat_table)

for l in [o for o in scene.objects if o.type == 'LIGHT']:
    bpy.data.objects.remove(l, do_unlink=True)

def add_area_light(name, power, size_x, size_y, loc, rot):
    ldata = bpy.data.lights.new(name, 'AREA')
    ldata.energy = power
    ldata.shape = 'RECTANGLE'
    ldata.size = size_x
    ldata.size_y = size_y
    lobj = bpy.data.objects.new(name, ldata)
    scene.collection.objects.link(lobj)
    lobj.location = loc
    lobj.rotation_euler = rot
    return lobj

add_area_light("Key_Softbox", 1400000, 180.0, 180.0, (120.0, -120.0, 250.0), (math.radians(45), 0, math.radians(35)))
add_area_light("Fill_Softbox", 550000, 220.0, 220.0, (-140.0, -80.0, 180.0), (math.radians(50), 0, math.radians(-40)))
add_area_light("Rim_Highlight", 900000, 120.0, 60.0, (0.0, 180.0, 160.0), (math.radians(-50), 0, math.radians(180)))

# Camera
cam = scene.camera
if not cam:
    cdata = bpy.data.cameras.new("Main_Camera")
    cam = bpy.data.objects.new("Main_Camera", cdata)
    scene.collection.objects.link(cam)
    scene.camera = cam

center = mathutils.Vector((-2.0, 20.0, 6.0))
cam.location = mathutils.Vector((center.x - 145.0, center.y - 225.0, center.z + 225.0))
cam.rotation_euler = mathutils.Euler((math.radians(58), 0, math.radians(-35)))

scene.render.engine = 'BLENDER_EEVEE'
if hasattr(scene, 'eevee'):
    scene.eevee.use_raytracing = True
    scene.eevee.use_fast_gi = True
    scene.eevee.fast_gi_quality = 1.0
    scene.eevee.use_shadows = True

scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - High Contrast'

# Save file
out_dir = "/home/hendra/project/PKM-Glicovia-/3dDesign"
blend_path = os.path.join(out_dir, "rangkaian_elektronika_pkm.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print("Complete master electronic circuit built and saved to:", blend_path)
