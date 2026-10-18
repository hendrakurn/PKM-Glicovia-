#!/usr/bin/env python3
"""
Generator skematik KiCad 8 untuk PKM-Glicovia Handheld Biosensor - versi TANPA TP4056.
Baterai Li-Po (dengan PCM internal) langsung ke saklar lalu MT3608; pengisian di luar alat.

Jalankan:  python3 generate_schematic.py
Hasil:     PKM_Glicovia.kicad_sch, Glicovia.kicad_sym, sym-lib-table

Semua posisi ditulis dalam satuan grid (1 g = 2.54 mm). Simbol standar diambil
dari library KiCad yang terpasang (/usr/share/kicad/symbols); simbol modul
(ESP32 DevKitC, ADS1115, MT3608, OLED) dibuat di library proyek
Glicovia.kicad_sym. EXPECTED_NETS di bawah dipakai verify_netlist.py untuk
memastikan netlist hasil KiCad sama dengan rancangan.
"""
import copy
import math
import os
import re
import uuid as _uuid

HERE = os.path.dirname(os.path.abspath(__file__))
KICAD_SYM = "/usr/share/kicad/symbols"
KICAD_FP = "/usr/share/kicad/footprints"
PROJECT = "PKM_Glicovia_TanpaTP4056"
G = 2.54
ROOT_UUID = "3b8e5d10-2c47-4f9a-b6d3-8a1e7c2f9b05"
_uid_ns = _uuid.UUID(ROOT_UUID)
_uid_n = 0


def uid():
    # UUID deterministik supaya file stabil di git setiap kali digenerate ulang
    global _uid_n
    _uid_n += 1
    return Q(str(_uuid.uuid5(_uid_ns, str(_uid_n))))


# ---------------------------------------------------------------------------
# S-expression kecil
# ---------------------------------------------------------------------------
class Q(str):
    """String yang harus ditulis dengan tanda kutip."""


def tokenize(s):
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in " \t\r\n":
            i += 1
        elif c in "()":
            yield c
            i += 1
        elif c == '"':
            j, buf = i + 1, []
            while s[j] != '"':
                if s[j] == "\\":
                    nxt = s[j + 1]
                    buf.append("\n" if nxt == "n" else nxt)
                    j += 2
                else:
                    buf.append(s[j])
                    j += 1
            yield Q("".join(buf))
            i = j + 1
        else:
            j = i
            while j < n and s[j] not in " \t\r\n()":
                j += 1
            yield s[i:j]
            i = j


def parse(s):
    stack = [[]]
    for t in tokenize(s):
        if t == "(" and not isinstance(t, Q):
            stack.append([])
        elif t == ")" and not isinstance(t, Q):
            x = stack.pop()
            stack[-1].append(x)
        else:
            stack[-1].append(t)
    return stack[0][0]


def num(v):
    if isinstance(v, (int,)) and not isinstance(v, bool):
        return str(v)
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def atom(x):
    if isinstance(x, Q):
        return '"' + x.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if isinstance(x, float):
        return num(x)
    return str(x)


def fmt(x, ind=0):
    if not isinstance(x, list):
        return atom(x)
    if not any(isinstance(e, list) for e in x):
        return "(" + " ".join(atom(e) for e in x) + ")"
    i, head = 0, []
    while i < len(x) and not isinstance(x[i], list):
        head.append(atom(x[i]))
        i += 1
    out = "(" + " ".join(head)
    for e in x[i:]:
        out += "\n" + "\t" * (ind + 1) + fmt(e, ind + 1)
    return out + "\n" + "\t" * ind + ")"


def find(lst, key):
    for e in lst:
        if isinstance(e, list) and e and e[0] == key:
            return e
    return None


def font(size=1.27):
    return ["font", ["size", size, size]]


def effects(justify=None, hide=False, size=1.27, bold=False):
    e = ["effects", font(size)]
    if bold:
        e[1].append(["bold", "yes"])
    if justify:
        e.append(["justify"] + justify.split())
    if hide:
        e.append(["hide", "yes"])
    return e


# ---------------------------------------------------------------------------
# Library KiCad bawaan
# ---------------------------------------------------------------------------
_libcache = {}


def lib_syms(lib):
    if lib not in _libcache:
        tree = parse(open(f"{KICAD_SYM}/{lib}.kicad_sym", encoding="utf-8").read())
        _libcache[lib] = {e[1]: e for e in tree if isinstance(e, list) and e[0] == "symbol"}
    return _libcache[lib]


def flatten(lib, name):
    """Gabungkan simbol turunan (extends) dengan simbol dasarnya."""
    syms = lib_syms(lib)
    s = copy.deepcopy(syms[name])
    ext = find(s, "extends")
    if not ext:
        return s
    base = flatten(lib, ext[1])
    own = {e[1]: e for e in s if isinstance(e, list) and e[0] == "property"}
    base_props = [e for e in base if isinstance(e, list) and e[0] == "property"]
    # properti turunan menimpa properti dasar; properti dasar lain (mis. ki_locked) tetap dipakai
    props = [own.pop(p[1], p) for p in base_props] + list(own.values())
    out = ["symbol", Q(name)]
    for e in base[2:]:
        if isinstance(e, list) and e[0] == "property":
            continue
        if isinstance(e, list) and e[0] == "symbol":
            e = copy.deepcopy(e)
            e[1] = Q(name + e[1][len(base[1]):])
        out.append(e)
    idx = next(i for i, e in enumerate(out) if isinstance(e, list) and e[0] == "symbol")
    out[idx:idx] = props
    return out


# ---------------------------------------------------------------------------
# Library proyek: modul-modul prototipe
# ---------------------------------------------------------------------------
def mk_pin(num_, name, typ, x, y, ang, length=2.54):
    return ["pin", typ, "line", ["at", float(x), float(y), ang], ["length", float(length)],
            ["name", Q(name), effects()], ["number", Q(num_), effects()]]


def mk_symbol(name, ref, value, box, pins, desc, keywords=""):
    x1, y1, x2, y2 = box
    return ["symbol", Q(name),
            ["pin_names", ["offset", 1.016]],
            ["exclude_from_sim", "no"], ["in_bom", "yes"], ["on_board", "yes"],
            ["property", Q("Reference"), Q(ref), ["at", float(x1), float(y1) + 1.27, 0], effects("left bottom")],
            ["property", Q("Value"), Q(value), ["at", float(x1), float(y2) - 1.27, 0], effects("left top")],
            ["property", Q("Footprint"), Q(""), ["at", 0.0, 0.0, 0], effects(hide=True)],
            ["property", Q("Datasheet"), Q(""), ["at", 0.0, 0.0, 0], effects(hide=True)],
            ["property", Q("Description"), Q(desc), ["at", 0.0, 0.0, 0], effects(hide=True)],
            ["property", Q("ki_keywords"), Q(keywords), ["at", 0.0, 0.0, 0], effects(hide=True)],
            ["symbol", Q(name + "_0_1"),
             ["rectangle", ["start", float(x1), float(y1)], ["end", float(x2), float(y2)],
              ["stroke", ["width", 0.254], ["type", "default"]], ["fill", ["type", "background"]]]],
            ["symbol", Q(name + "_1_1")] + pins]


ESP_LEFT = [("3V3", "power_out"), ("EN", "input"), ("SENSOR_VP", "input"), ("SENSOR_VN", "input"),
            ("IO34", "input"), ("IO35", "input"), ("IO32", "bidirectional"), ("IO33", "bidirectional"),
            ("IO25", "bidirectional"), ("IO26", "bidirectional"), ("IO27", "bidirectional"),
            ("IO14", "bidirectional"), ("IO12", "bidirectional"), ("GND", "power_in"),
            ("IO13", "bidirectional"), ("SD2", "bidirectional"), ("SD3", "bidirectional"),
            ("CMD", "bidirectional"), ("5V", "power_in")]
ESP_RIGHT = [("GND", "power_in"), ("IO23", "bidirectional"), ("IO22/SCL", "bidirectional"),
             ("TXD0", "output"), ("RXD0", "input"), ("IO21/SDA", "bidirectional"), ("GND", "power_in"),
             ("IO19", "bidirectional"), ("IO18", "bidirectional"), ("IO5", "bidirectional"),
             ("IO17", "bidirectional"), ("IO16", "bidirectional"), ("IO4", "bidirectional"),
             ("IO0", "bidirectional"), ("IO2", "bidirectional"), ("IO15", "bidirectional"),
             ("SD1", "bidirectional"), ("SD0", "bidirectional"), ("CLK", "bidirectional")]


def custom_symbols():
    syms = {}
    # ESP32-DevKitC 38 pin. Nomor pin berlawanan arah jarum jam seperti DIP:
    # kiri 1..19 (atas->bawah), kanan 20..38 (bawah->atas). Pin 39 = IPEX/u.FL.
    pins = []
    for k, (nm, typ) in enumerate(ESP_LEFT):
        pins.append(mk_pin(str(k + 1), nm, typ, -15.24, 22.86 - k * G, 0))
    for k, (nm, typ) in enumerate(ESP_RIGHT):
        pins.append(mk_pin(str(38 - k), nm, typ, 15.24, 22.86 - k * G, 180))
    pins.append(mk_pin("39", "IPEX (u.FL) ANT", "passive", 0, -27.94, 90))
    syms["ESP32_DevKitC_38P"] = mk_symbol(
        "ESP32_DevKitC_38P", "U", "ESP32-DevKitC-32U", (-12.7, 25.4, 12.7, -25.4), pins,
        "ESP32-DevKitC V4, modul ESP32-WROOM-32U (konektor antena IPEX), header 2x19", "esp32 devkitc wroom")

    pins = [mk_pin("1", "VDD", "power_in", 0, 11.43, 270),
            mk_pin("2", "GND", "power_in", 0, -11.43, 90),
            mk_pin("3", "SCL", "input", -12.7, 3.81, 0),
            mk_pin("4", "SDA", "bidirectional", -12.7, 1.27, 0),
            mk_pin("5", "ADDR", "input", -5.08, -11.43, 90),
            mk_pin("6", "ALRT", "open_collector", -12.7, -1.27, 0),
            mk_pin("7", "A0", "input", 12.7, 3.81, 180),
            mk_pin("8", "A1", "input", 12.7, 1.27, 180),
            mk_pin("9", "A2", "input", 12.7, -1.27, 180),
            mk_pin("10", "A3", "input", 5.08, -11.43, 90)]
    syms["ADS1115_Module"] = mk_symbol(
        "ADS1115_Module", "U", "ADS1115_Module", (-10.16, 8.89, 10.16, -8.89), pins,
        "Modul ADC 16-bit ADS1115 (header 10 pin: VDD GND SCL SDA ADDR ALRT A0 A1 A2 A3), pull-up I2C 10k onboard",
        "adc ads1115 i2c")

    pins = [mk_pin("1", "IN+", "passive", -2.54, 10.16, 270),
            mk_pin("2", "IN-", "passive", 2.54, 10.16, 270),
            mk_pin("3", "B+", "passive", -12.7, 2.54, 0),
            mk_pin("4", "B-", "passive", -12.7, -2.54, 0),
            mk_pin("5", "OUT-", "passive", 12.7, -2.54, 180),
            mk_pin("6", "OUT+", "power_out", 12.7, 2.54, 180)]
    syms["TP4056_Module"] = mk_symbol(
        "TP4056_Module", "U", "TP4056_TypeC_Module", (-10.16, 7.62, 10.16, -7.62), pins,
        "Modul charger Li-Ion TP4056 USB Type-C + proteksi DW01A/FS8205A", "charger tp4056 lipo")

    pins = [mk_pin("1", "VIN+", "power_in", -12.7, 2.54, 0),
            mk_pin("2", "VIN-", "power_in", -12.7, -2.54, 0),
            mk_pin("3", "VOUT+", "power_out", 12.7, 2.54, 180),
            mk_pin("4", "VOUT-", "passive", 12.7, -2.54, 180)]
    syms["MT3608_Module"] = mk_symbol(
        "MT3608_Module", "U", "MT3608_StepUp_5V", (-10.16, 5.08, 10.16, -5.08), pins,
        "Modul step-up DC-DC MT3608 (trimpot diatur ke 5,0 V)", "boost mt3608 step-up")

    pins = [mk_pin("1", "GND", "power_in", 0, -8.89, 90),
            mk_pin("2", "VCC", "power_in", 0, 8.89, 270),
            mk_pin("3", "SCL", "input", -10.16, 1.27, 0),
            mk_pin("4", "SDA", "bidirectional", -10.16, -1.27, 0)]
    syms["OLED_SH1106_I2C"] = mk_symbol(
        "OLED_SH1106_I2C", "J", "OLED_0.96_SH1106", (-7.62, 6.35, 7.62, -6.35), pins,
        "Modul OLED 0.96in 128x64 I2C SH1106G/SSD1306, header GND-VCC-SCL-SDA", "oled display i2c")
    return syms


CUSTOM = custom_symbols()
CUSTOM.pop("TP4056_Module")  # versi ini tanpa modul charger


def get_symbol(lib_id):
    lib, name = lib_id.split(":")
    if lib == "Glicovia":
        return copy.deepcopy(CUSTOM[name])
    return flatten(lib, name)


# ---------------------------------------------------------------------------
# Geometri
# ---------------------------------------------------------------------------
def rot_lib(x, y, rot):
    """Koordinat library (Y ke atas) -> offset layar (Y ke bawah), rotasi CCW."""
    r = math.radians(rot)
    xr = x * math.cos(r) - y * math.sin(r)
    yr = x * math.sin(r) + y * math.cos(r)
    return xr, -yr


def snap(v):
    return round(v / 1.27) * 1.27 if abs(v / 1.27 - round(v / 1.27)) < 1e-6 else round(v, 4)


def mm(g):
    return round(g * G, 4)


def pins_of(sym, unit):
    res = {}
    for sub in sym:
        if isinstance(sub, list) and sub[0] == "symbol":
            m = re.match(r".*_(\d+)_(\d+)$", sub[1])
            u, st = int(m[1]), int(m[2])
            if (u == 0 or u == unit) and st in (0, 1):
                for e in sub:
                    if isinstance(e, list) and e[0] == "pin":
                        at = find(e, "at")
                        res[str(find(e, "number")[1])] = (float(at[1]), float(at[2]),
                                                          float(at[3]) if len(at) > 3 else 0.0, e[1])
    return res


def fp_ok(fp):
    if not fp:
        return ""
    lib, name = fp.split(":")
    return fp if os.path.exists(f"{KICAD_FP}/{lib}.pretty/{name}.kicad_mod") else ""


# ---------------------------------------------------------------------------
# Skematik
# ---------------------------------------------------------------------------
class Schematic:
    def __init__(self):
        self.items = []
        self.lib = {}
        self.comps = {}          # (ref, unit) -> dict
        self.pin_index = {}      # ref -> {pin: (x, y, dx, dy)}
        self.npwr = 0
        self.nflg = 0

    # -- simbol ----------------------------------------------------------
    def _embed(self, lib_id):
        if lib_id not in self.lib:
            s = get_symbol(lib_id)
            s[1] = Q(lib_id)
            self.lib[lib_id] = s
        return self.lib[lib_id]

    def place(self, lib_id, ref, value, gx, gy, rot=0, unit=1, fp="", ds="", desc="",
              ref_at=None, val_at=None, in_bom=True, hide_ref=False, hide_val=False, txt_just=None):
        sym = self._embed(lib_id)
        X, Y = mm(gx), mm(gy)
        pins = pins_of(sym, unit)
        idx = self.pin_index.setdefault(ref, {})
        for n, (px, py, pa, _t) in pins.items():
            ox, oy = rot_lib(px, py, rot)
            # arah pin di library menunjuk ke badan simbol; arah keluar = +180
            dx, dy = rot_lib(math.cos(math.radians(pa + 180)), math.sin(math.radians(pa + 180)), rot)
            idx[n] = (round(X + ox, 4), round(Y + oy, 4), round(dx), round(dy))

        def lib_prop_at(key):
            p = next(e for e in sym if isinstance(e, list) and e[0] == "property" and e[1] == key)
            at = find(p, "at")
            ox, oy = rot_lib(float(at[1]), float(at[2]), rot)
            just = find(find(p, "effects"), "justify")
            return (X + ox, Y + oy), (" ".join(just[1:]) if just else None)

        def prop(key, val, at=None, hide=False, just=None):
            if at is None:
                (x, y), j = lib_prop_at(key) if key in ("Reference", "Value") else ((X, Y), None)
                just = just or j
            else:
                x, y = at
            return ["property", Q(key), Q(val), ["at", round(x, 4), round(y, 4), rot % 180], effects(just, hide)]

        r_at = (mm(ref_at[0]), mm(ref_at[1])) if ref_at else None
        v_at = (mm(val_at[0]), mm(val_at[1])) if val_at else None
        inst = ["symbol", ["lib_id", Q(lib_id)], ["at", X, Y, rot], ["unit", unit],
                ["exclude_from_sim", "no"], ["in_bom", "yes" if in_bom else "no"],
                ["on_board", "yes" if in_bom else "no"], ["dnp", "no"], ["uuid", uid()],
                prop("Reference", ref, r_at, hide_ref, txt_just),
                prop("Value", value, v_at, hide_val, txt_just),
                prop("Footprint", fp_ok(fp), hide=True),
                prop("Datasheet", ds, hide=True),
                prop("Description", desc, hide=True)]
        for n in sorted(pins, key=lambda s: (len(s), s)):
            inst.append(["pin", Q(n), ["uuid", uid()]])
        inst.append(["instances", ["project", Q(PROJECT),
                                   ["path", Q("/" + ROOT_UUID), ["reference", Q(ref)], ["unit", unit]]]])
        self.items.append(inst)
        self.comps[(ref, unit)] = {"lib_id": lib_id, "value": value}
        return inst

    def two_pin(self, lib_id, ref, value, gx, gy, horizontal=False, fp=""):
        """R / C: label nilai di samping supaya tidak menabrak kabel."""
        if horizontal:
            return self.place(lib_id, ref, value, gx, gy, 90, fp=fp,
                              ref_at=(gx, gy - 1.2), val_at=(gx, gy + 1.3), txt_just=None)
        return self.place(lib_id, ref, value, gx, gy, 0, fp=fp,
                          ref_at=(gx + 0.9, gy - 0.5), val_at=(gx + 0.9, gy + 0.5), txt_just="left")

    def pin(self, ref, p):
        return self.pin_index[ref][str(p)]

    # -- primitif --------------------------------------------------------
    def wire(self, *pts):
        """pts dalam grid, bisa juga ('pin', ref, pin)."""
        P = [self._pt(p) for p in pts]
        for a, b in zip(P, P[1:]):
            self.items.append(["wire", ["pts", ["xy", a[0], a[1]], ["xy", b[0], b[1]]],
                               ["stroke", ["width", 0], ["type", "default"]], ["uuid", uid()]])

    def _pt(self, p):
        if isinstance(p, tuple) and len(p) == 3 and p[0] == "pin":
            x, y, _, _ = self.pin(p[1], p[2])
            return (x, y)
        return (mm(p[0]), mm(p[1]))

    def junction(self, gx, gy):
        self.items.append(["junction", ["at", mm(gx), mm(gy)], ["diameter", 0], ["color", 0, 0, 0, 0],
                           ["uuid", uid()]])

    def nc(self, ref, *pins):
        for p in pins:
            x, y, _, _ = self.pin(ref, p)
            self.items.append(["no_connect", ["at", x, y], ["uuid", uid()]])

    def _label(self, kind, name, x, y, ang, shape="passive"):
        if kind == "global":
            just = "left" if ang in (0, 90) else "right"
            self.items.append(["global_label", Q(name), ["shape", shape], ["at", x, y, ang],
                               ["fields_autoplaced", "yes"], effects(just), ["uuid", uid()],
                               ["property", Q("Intersheetrefs"), Q("${INTERSHEET_REFS}"), ["at", x, y, ang],
                                effects(just, hide=True)]])
        else:
            just = "left bottom" if ang in (0, 90) else "right bottom"
            self.items.append(["label", Q(name), ["at", x, y, ang], ["fields_autoplaced", "yes"],
                               effects(just), ["uuid", uid()]])

    def label_at(self, name, gx, gy, ang=0, kind="local", shape="passive"):
        self._label(kind, name, mm(gx), mm(gy), ang, shape)

    def pin_label(self, ref, p, name, kind="local", shape="passive", stub=1.0):
        x, y, dx, dy = self.pin(ref, p)
        ex, ey = round(x + dx * stub * G, 4), round(y + dy * stub * G, 4)
        self.items.append(["wire", ["pts", ["xy", x, y], ["xy", ex, ey]],
                           ["stroke", ["width", 0], ["type", "default"]], ["uuid", uid()]])
        ang = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}[(dx, dy)]
        self._label(kind, name, ex, ey, ang, shape)

    def power_at(self, net, x, y, rot=0):
        if net == "PWR_FLAG":
            self.nflg += 1
            ref = f"#FLG{self.nflg:02d}"
        else:
            self.npwr += 1
            ref = f"#PWR{self.npwr:02d}"
        gx, gy = x / G, y / G
        self.place(f"power:{net}", ref, net, gx, gy, rot, in_bom=False, hide_ref=True)

    def pin_power(self, ref, p, net, stub=0.0):
        """Simbol power di ujung pin. stub>0: tarik kabel keluar dulu lalu simbol tegak normal;
        stub=0: simbol diputar menghadap keluar dari pin."""
        x, y, dx, dy = self.pin(ref, p)
        natural = (0, 1) if net == "GND" else (0, -1)
        if stub:
            ex, ey = round(x + dx * stub * G, 4), round(y + dy * stub * G, 4)
            self.items.append(["wire", ["pts", ["xy", x, y], ["xy", ex, ey]],
                               ["stroke", ["width", 0], ["type", "default"]], ["uuid", uid()]])
            self.power_at(net, ex, ey, 0)
            return
        for rot in (0, 90, 180, 270):
            v = natural
            for _ in range(rot // 90):
                v = (v[1], -v[0])  # putar 90 derajat CCW di layar
            if v == (dx, dy):
                if dx:  # simbol menyamping: nilai ditaruh setelah ujung simbol
                    self.npwr += 1
                    self.place(f"power:{net}", f"#PWR{self.npwr:02d}", net, x / G, y / G, rot,
                               in_bom=False, hide_ref=True, val_at=(x / G + dx * 1.35, y / G),
                               txt_just="right")  # KiCad membalik rata teks pada rotasi 90
                else:
                    self.power_at(net, x, y, rot)
                return
        raise ValueError((ref, p, net))

    def text(self, s, gx, gy, size=1.27, bold=False, just="left top"):
        self.items.append(["text", Q(s), ["exclude_from_sim", "no"], ["at", mm(gx), mm(gy), 0],
                           effects(just, size=size, bold=bold), ["uuid", uid()]])

    def frame(self, title, gx1, gy1, gx2, gy2):
        self.items.append(["rectangle", ["start", mm(gx1), mm(gy1)], ["end", mm(gx2), mm(gy2)],
                           ["stroke", ["width", 0.254], ["type", "dash"]], ["fill", ["type", "none"]],
                           ["uuid", uid()]])
        self.text(title, gx1 + 0.5, gy1 + 0.4, size=2.0, bold=True)

    def write(self, path, title_block):
        lib_symbols = ["lib_symbols"] + [self.lib[k] for k in sorted(self.lib)]
        doc = ["kicad_sch", ["version", 20231120], ["generator", Q("eeschema")],
               ["generator_version", Q("8.0")], ["uuid", Q(ROOT_UUID)], ["paper", Q("A3")],
               title_block, lib_symbols] + self.items + [
            ["sheet_instances", ["path", Q("/"), ["page", Q("1")]]]]
        with open(path, "w", encoding="utf-8") as f:
            f.write(fmt(doc) + "\n")


# ---------------------------------------------------------------------------
# Footprint (opsional, untuk tahap PCB nanti)
# ---------------------------------------------------------------------------
FP_R = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"
FP_C = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"
FP_RV = "Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical"
FP_DIP8 = "Package_DIP:DIP-8_W7.62mm"
FP_JST3 = "Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical"


# ---------------------------------------------------------------------------
# Rangkaian
# ---------------------------------------------------------------------------
def build():
    S = Schematic()

    # ===================== BLOK A: DAYA =====================
    S.frame("A. SUPLAI DAYA (Li-Po -> Saklar -> MT3608 5V, tanpa charger)", 5, 6, 64, 25)
    S.place("Device:Battery_Cell", "BT1", "LiPo 3.7V 1200mAh", 14, 18,
            ref_at=(15, 17.6), val_at=(15, 18.6), txt_just="left")
    S.pin_power("BT1", 2, "GND")
    S.place("Switch:SW_SPST", "SW1", "KCD11 Rocker", 24, 17, ref_at=(24, 14.4), val_at=(24, 15.4))
    S.wire(("pin", "BT1", 1), (14, 14), (19, 14), (19, 17), ("pin", "SW1", 1))
    S.label_at("VBAT", 15, 14)
    S.place("Glicovia:MT3608_Module", "U7", "MT3608_StepUp_5V", 36, 18)
    S.wire(("pin", "SW1", 2), (29, 17))
    S.wire((29, 17), ("pin", "U7", 1))
    S.junction(29, 17)
    S.power_at("PWR_FLAG", mm(29), mm(17))
    S.label_at("VSYS", 26.5, 17)
    S.pin_power("U7", 2, "GND")
    S.pin_power("U7", 4, "GND")
    S.wire(("pin", "U7", 3), (45, 17))
    S.power_at("+5V", mm(45), mm(17))
    S.power_at("PWR_FLAG", mm(49), mm(21))
    S.power_at("GND", mm(49), mm(21))
    S.text("Tanpa modul charger: Li-Po dicas di luar alat\n"
           "(charger Li-Po 1S 4,2 V). Pakai baterai dengan PCM\n"
           "internal (proteksi over-discharge/short).", 6, 9.5)
    S.text("Atur trimpot MT3608 ke 5,0 V\nSEBELUM disambung ke ESP32.", 31, 22.2)
    S.text("Matikan SW1 saat ESP32\ndisambung ke USB (flashing).", 51, 9.5)

    # ===================== BLOK B: MCU & RF =====================
    S.frame("B. MIKROKONTROLER & RF", 5, 27, 46, 97)
    S.place("Glicovia:ESP32_DevKitC_38P", "U1", "ESP32-DevKitC-32U", 28, 50,
            ref_at=(23, 38.4), val_at=(23, 39.4), txt_just="left")
    S.pin_power("U1", 1, "+3V3", stub=3)
    S.pin_power("U1", 14, "GND", stub=3)
    S.pin_power("U1", 19, "+5V", stub=3)
    S.pin_power("U1", 38, "GND")
    S.wire(("pin", "U1", 32), (36, 47))
    S.power_at("GND", mm(36), mm(47))
    S.pin_label("U1", 36, "I2C_SCL", "global", "bidirectional", stub=3)
    S.pin_label("U1", 33, "I2C_SDA", "global", "bidirectional", stub=3)
    used = {1, 14, 19, 32, 33, 36, 38, 39}
    S.nc("U1", *[p for p in range(1, 39) if p not in used])
    S.place("Connector:Conn_Coaxial", "J5", "RP-SMA 2.4GHz", 20, 70, ref_at=(21.5, 68), val_at=(21.5, 69),
            txt_just="left")
    S.wire(("pin", "U1", 39), (28, 64), (16, 64), (16, 70), ("pin", "J5", 1))
    S.label_at("RF_2G4", 18, 64)
    S.pin_power("J5", 2, "GND")
    S.text("U1: ESP32-DevKitC V4 dengan ESP32-WROOM-32U.\n"
           "J5: soket RP-SMA bulkhead + antena 2.4 GHz,\n"
           "disambung ke IPEX/u.FL U1 lewat pigtail RG1.13.\n"
           "I2C: SDA = GPIO21, SCL = GPIO22 (main.cpp).", 6, 77)

    # ===================== BLOK C: ADC, DISPLAY, VMID =====================
    S.frame("C. ADC 16-BIT, OLED & REFERENSI VMID", 48, 27, 93, 97)
    S.place("Glicovia:ADS1115_Module", "U2", "ADS1115_Module", 75, 40, ref_at=(64, 33.6), val_at=(64, 34.6), txt_just="left")
    S.pin_power("U2", 1, "+3V3")
    S.pin_power("U2", 2, "GND")
    S.pin_power("U2", 5, "GND")   # ADDR -> GND : alamat 0x48
    S.pin_power("U2", 10, "GND")  # A3 tidak dipakai
    S.pin_label("U2", 3, "I2C_SCL", "global", "input", stub=2)
    S.pin_label("U2", 4, "I2C_SDA", "global", "bidirectional", stub=2)
    S.nc("U2", 6)
    for p, ch in ((7, 1), (8, 2), (9, 3)):
        S.pin_label("U2", p, f"AFE_CH{ch}_OUT", "global", "input", stub=1)
    S.text("ADDR=GND -> 0x48, GAIN_ONE (+/-4.096 V).\nA0 Glukosa, A1 pH, A2 Fruktosamin.", 50, 46.5)

    S.place("Glicovia:OLED_SH1106_I2C", "J1", "OLED_0.96_SH1106", 75, 58, ref_at=(78.5, 55.4), val_at=(78.5, 56.4),
            txt_just="left")
    S.pin_power("J1", 2, "+3V3")
    S.pin_power("J1", 1, "GND")
    S.pin_label("J1", 3, "I2C_SCL", "global", "input", stub=2)
    S.pin_label("J1", 4, "I2C_SDA", "global", "bidirectional", stub=2)
    S.text("OLED SH1106G 128x64, alamat 0x3C.\nCek urutan pin modul (ada varian VCC-GND).", 50, 65)

    S.two_pin("Device:R", "R1", "10k", 66, 72, fp=FP_R)
    S.two_pin("Device:R", "R2", "10k", 66, 77, fp=FP_R)
    S.two_pin("Device:C", "C7", "10uF", 70, 76, fp=FP_C)
    S.pin_power("R1", 1, "+3V3")
    S.pin_power("R2", 2, "GND")
    S.pin_power("C7", 2, "GND")
    S.wire(("pin", "R1", 2), (66, 74.5))
    S.wire((66, 74.5), ("pin", "R2", 1))
    S.wire((66, 74.5), ("pin", "C7", 1))
    S.wire(("pin", "C7", 1), (73, 74.5))
    S.junction(66, 74.5)
    S.junction(70, 74.5)
    S.label_at("VMID", 73, 74.5, kind="global", shape="output")
    S.text("VMID = 1.65 V: potensial WE (CH1, CH3)\ndan RE (CH2).", 50, 82)

    # ===================== BLOK D: AFE 3 CHANNEL =====================
    bx = 96
    amper = [  # (channel, opamp, nama, y, R3.., RV, Cf, Cvset, Cout, Cdec100n, Cdec10u, J)
        dict(ch=1, U="U3", name="GLUKOSA (GOx) - amperometrik", by=6, Rtop="R3", RV="RV1", Rbot="R4",
             Rf="R5", Rce="R6", Rout="R7", Cf="C8", Cvs="C9", Cout="C10", Cd1="C1", Cd2="C4", J="J2",
             jval="SPE_Glukosa"),
        dict(ch=3, U="U5", name="FRUKTOSAMIN (PBA) - amperometrik", by=66, Rtop="R9", RV="RV2", Rbot="R10",
             Rf="R11", Rce="R12", Rout="R13", Cf="C12", Cvs="C13", Cout="C14", Cd1="C3", Cd2="C6", J="J4",
             jval="SPE_Fruktosamin"),
    ]
    for c in amper:
        n, U, by = c["ch"], c["U"], c["by"]

        def P(x, y):
            return (bx + x, by + y)

        S.frame(f"D{n}. AFE CH{n}: {c['name']}", bx + 3, by, bx + 52, by + 29.5)
        # U?A: penguat kontrol (CE/RE)
        S.place("Amplifier_Operational:OPA2333xxD", U, "OPA2333", *P(14, 8), unit=1, fp=FP_DIP8,
                ds="https://www.ti.com/lit/ds/symlink/opa2333.pdf")
        S.pin_label(U, 3, f"CH{n}_VSET", stub=2)
        S.pin_label(U, 2, f"CH{n}_RE", stub=2)
        S.two_pin("Device:R", c["Rce"], "1k", *P(21, 8), horizontal=True, fp=FP_R)
        S.wire(("pin", U, 1), ("pin", c["Rce"], 1))
        S.pin_label(c["Rce"], 2, f"CH{n}_CE", stub=1.5)
        # U?B: TIA untuk WE
        S.place("Amplifier_Operational:OPA2333xxD", U, "OPA2333", *P(14, 20), unit=2, fp=FP_DIP8,
                ds="https://www.ti.com/lit/ds/symlink/opa2333.pdf")
        S.pin_label(U, 5, "VMID", "global", "input", stub=2)
        S.two_pin("Device:R", c["Rf"], "100k", *P(14, 24), horizontal=True, fp=FP_R)
        S.two_pin("Device:C", c["Cf"], "1.3nF", *P(14, 27.5), horizontal=True, fp=FP_C)
        S.wire(("pin", U, 6), P(9, 21))
        S.wire(P(9, 21), P(7, 21))
        S.label_at(f"CH{n}_WE", *P(7, 21), ang=180)
        S.wire(P(9, 21), P(9, 24))
        S.wire(P(9, 24), P(9, 27.5), ("pin", c["Cf"], 1))
        S.wire(P(9, 24), ("pin", c["Rf"], 1))
        S.junction(*P(9, 21))
        S.junction(*P(9, 24))
        S.two_pin("Device:R", c["Rout"], "1k", *P(22, 20), horizontal=True, fp=FP_R)
        S.wire(("pin", U, 7), P(19, 20))
        S.wire(P(19, 20), ("pin", c["Rout"], 1))
        S.wire(P(19, 20), P(19, 24))
        S.wire(P(19, 24), P(19, 27.5), ("pin", c["Cf"], 2))
        S.wire(P(19, 24), ("pin", c["Rf"], 2))
        S.junction(*P(19, 20))
        S.junction(*P(19, 24))
        S.two_pin("Device:C", c["Cout"], "100nF", *P(26, 22.5), fp=FP_C)
        S.wire(("pin", c["Rout"], 2), P(26, 20))
        S.wire(P(26, 20), ("pin", c["Cout"], 1))
        S.wire(P(26, 20), P(28, 20))
        S.junction(*P(26, 20))
        S.label_at(f"AFE_CH{n}_OUT", *P(28, 20), kind="global", shape="output")
        S.pin_power(c["Cout"], 2, "GND")
        # Daya U?C + dekopling
        S.place("Amplifier_Operational:OPA2333xxD", U, "OPA2333", *P(31, 6), unit=3, fp=FP_DIP8,
                ref_at=P(29.4, 6), hide_val=True, txt_just="right")
        S.pin_power(U, 8, "+3V3")
        S.pin_power(U, 4, "GND")
        S.two_pin("Device:C", c["Cd1"], "100nF", *P(35, 6), fp=FP_C)
        S.two_pin("Device:C", c["Cd2"], "10uF", *P(39, 6), fp=FP_C)
        for cc in (c["Cd1"], c["Cd2"]):
            S.pin_power(cc, 1, "+3V3")
            S.pin_power(cc, 2, "GND")
        # Pembagi bias VSET (trimpot)
        S.two_pin("Device:R", c["Rtop"], "10k", *P(36, 15), fp=FP_R)
        S.place("Device:R_Potentiometer_Trim", c["RV"], "20k", *P(36, 20), fp=FP_RV,
                ref_at=P(37.6, 18.7), val_at=P(37.6, 21.6), txt_just="left")
        S.two_pin("Device:R", c["Rbot"], "10k", *P(36, 25), fp=FP_R)
        S.pin_power(c["Rtop"], 1, "+3V3")
        S.pin_power(c["Rbot"], 2, "GND")
        S.wire(("pin", c["Rtop"], 2), ("pin", c["RV"], 1))
        S.wire(("pin", c["RV"], 3), ("pin", c["Rbot"], 1))
        S.two_pin("Device:C", c["Cvs"], "1uF", *P(41, 23), fp=FP_C)
        S.wire(("pin", c["RV"], 2), P(41, 20))
        S.wire(P(41, 20), ("pin", c["Cvs"], 1))
        S.wire(P(41, 20), P(43, 20))
        S.junction(*P(41, 20))
        S.label_at(f"CH{n}_VSET", *P(43, 20))
        S.pin_power(c["Cvs"], 2, "GND")
        # Konektor SPE
        S.place("Connector_Generic:Conn_01x03", c["J"], c["jval"], *P(46, 14), fp=FP_JST3,
                ref_at=P(45, 11.4), val_at=P(45, 16.6), txt_just="left")
        S.pin_label(c["J"], 1, f"CH{n}_WE", stub=2)
        S.pin_label(c["J"], 2, f"CH{n}_RE", stub=2)
        S.pin_label(c["J"], 3, f"CH{n}_CE", stub=2)
        S.text(f"E(WE-RE) = VMID - VSET, atur RV{n if n == 1 else 2}\n"
               "TIA: Vout = VMID - I x 100k (+/-16 uA)\n"
               "fc = 1/(2pi x 100k x 1.3nF) = 1.2 kHz", *P(20.5, 26.3), size=1.0)

    # ---- CH2 pH (IrOx): potensiometrik ----
    by = 36

    def P(x, y):
        return (bx + x, by + y)

    S.frame("D2. AFE CH2: pH (IrOx) - potensiometrik", bx + 3, by, bx + 52, by + 29.5)
    S.place("Amplifier_Operational:OPA2333xxD", "U4", "OPA2333", *P(14, 8), unit=1, fp=FP_DIP8,
            ds="https://www.ti.com/lit/ds/symlink/opa2333.pdf")
    S.pin_label("U4", 3, "CH2_WE", stub=2)
    S.wire(("pin", "U4", 2), P(10, 9), P(10, 11), P(19, 11))
    S.wire(("pin", "U4", 1), P(19, 8), P(19, 11))
    S.wire(P(19, 11), P(19, 14))
    S.junction(*P(19, 11))
    S.two_pin("Device:R", "R8", "1k", *P(22, 14), horizontal=True, fp=FP_R)
    S.wire(P(19, 14), ("pin", "R8", 1))
    S.two_pin("Device:C", "C11", "100nF", *P(26, 16.5), fp=FP_C)
    S.wire(("pin", "R8", 2), P(26, 14))
    S.wire(P(26, 14), ("pin", "C11", 1))
    S.wire(P(26, 14), P(28, 14))
    S.junction(*P(26, 14))
    S.label_at("AFE_CH2_OUT", *P(28, 14), kind="global", shape="output")
    S.pin_power("C11", 2, "GND")
    S.place("Amplifier_Operational:OPA2333xxD", "U4", "OPA2333", *P(14, 20), unit=2, fp=FP_DIP8,
            ds="https://www.ti.com/lit/ds/symlink/opa2333.pdf")
    S.pin_label("U4", 5, "VMID", "global", "input", stub=2)
    S.wire(("pin", "U4", 6), P(10, 21), P(10, 23), P(19, 23), P(19, 20))
    S.wire(("pin", "U4", 7), P(19, 20))
    S.wire(P(19, 20), P(21, 20))
    S.junction(*P(19, 20))
    S.label_at("CH2_RE", *P(21, 20))
    S.place("Amplifier_Operational:OPA2333xxD", "U4", "OPA2333", *P(31, 6), unit=3, fp=FP_DIP8,
            ref_at=P(29.4, 6), hide_val=True, txt_just="right")
    S.pin_power("U4", 8, "+3V3")
    S.pin_power("U4", 4, "GND")
    S.two_pin("Device:C", "C2", "100nF", *P(35, 6), fp=FP_C)
    S.two_pin("Device:C", "C5", "10uF", *P(39, 6), fp=FP_C)
    for cc in ("C2", "C5"):
        S.pin_power(cc, 1, "+3V3")
        S.pin_power(cc, 2, "GND")
    S.place("Connector_Generic:Conn_01x03", "J3", "SPE_pH", *P(46, 14), fp=FP_JST3,
            ref_at=P(45, 11.4), val_at=P(45, 16.6), txt_just="left")
    S.pin_label("J3", 1, "CH2_WE", stub=2)
    S.pin_label("J3", 2, "CH2_RE", stub=2)
    S.nc("J3", 3)
    S.text("U4A: buffer impedansi tinggi untuk WE.\n"
           "U4B: menahan RE di VMID.\n"
           "Vout = VMID + E(WE-RE); CE tidak dipakai.", *P(26, 21.5))

    # ===================== CATATAN =====================
    S.text("CATATAN DESAIN\n"
           "1. Topologi AFE dan nilai R/C adalah rancangan awal (repo belum punya data rangkaian AFE aktual). "
           "Wajib diverifikasi dengan uji bench dan kalibrasi.\n"
           "2. Rf 100k + Cf 1.3nF dipilih agar bandwidth TIA ~1.2 kHz sesuai simulasi di laporan PKM. "
           "Ganti Rf bila arus sensor > 16 uA.\n"
           "3. Modul ESP32, ADS1115, MT3608, OLED ada di library proyek Glicovia.kicad_sym. "
           "Pull-up I2C 10k sudah ada di modul ADS1115.\n"
           "4. Skematik ini digenerate oleh generate_schematic.py; edit skrip lalu jalankan ulang "
           "agar netlist tetap terverifikasi (verify_netlist.py).",
           5, 99, size=1.5)

    title = ["title_block", ["title", Q("PKM-Glicovia Handheld Biosensor - Tanpa TP4056")],
             ["date", Q("2026-10-18")], ["rev", Q("1.0")], ["company", Q("Tim PKM-KC Glicovia")],
             ["comment", 1, Q("ESP32-DevKitC + ADS1115 + 3x OPA2333 potensiostat + OLED SH1106")],
             ["comment", 2, Q("Daya: Li-Po 1S (PCM) -> KCD11 -> MT3608 5V, tanpa TP4056")],
             ["comment", 3, Q("AFE: rancangan awal, perlu verifikasi bench")]]
    return S, title


# ---------------------------------------------------------------------------
# Netlist yang diharapkan (dicek oleh verify_netlist.py)
# ---------------------------------------------------------------------------
def _amper_nets(ch, U, Rtop, RV, Rbot, Rf, Rce, Rout, Cf, Cvs, Cout, J, adc_pin):
    return {
        f"CH{ch}_VSET": [(RV, "2"), (Cvs, "1"), (U, "3")],
        f"CH{ch}_RE": [(U, "2"), (J, "2")],
        f"CH{ch}_CE": [(Rce, "2"), (J, "3")],
        f"CH{ch}_CEDRV": [(U, "1"), (Rce, "1")],
        f"CH{ch}_WE": [(U, "6"), (Rf, "1"), (Cf, "1"), (J, "1")],
        f"CH{ch}_TIA": [(U, "7"), (Rf, "2"), (Cf, "2"), (Rout, "1")],
        f"CH{ch}_VTOP": [(Rtop, "2"), (RV, "1")],
        f"CH{ch}_VBOT": [(RV, "3"), (Rbot, "1")],
        f"AFE_CH{ch}_OUT": [(Rout, "2"), (Cout, "1"), ("U2", adc_pin)],
    }


EXPECTED_NETS = {
    "GND": [("BT1", "2"), ("U7", "2"), ("U7", "4"), ("U1", "14"), ("U1", "32"), ("U1", "38"), ("J5", "2"),
            ("U2", "2"), ("U2", "5"), ("U2", "10"), ("J1", "1"), ("U3", "4"), ("U4", "4"), ("U5", "4"),
            ("C1", "2"), ("C2", "2"), ("C3", "2"), ("C4", "2"), ("C5", "2"), ("C6", "2"), ("C7", "2"),
            ("R2", "2"), ("R4", "2"), ("R10", "2"), ("C9", "2"), ("C13", "2"), ("C10", "2"), ("C11", "2"),
            ("C14", "2")],
    "+3V3": [("U1", "1"), ("U2", "1"), ("J1", "2"), ("U3", "8"), ("U4", "8"), ("U5", "8"),
             ("C1", "1"), ("C2", "1"), ("C3", "1"), ("C4", "1"), ("C5", "1"), ("C6", "1"),
             ("R1", "1"), ("R3", "1"), ("R9", "1")],
    "+5V": [("U7", "3"), ("U1", "19")],
    "VSYS": [("SW1", "2"), ("U7", "1")],
    "VBAT": [("BT1", "1"), ("SW1", "1")],
    "I2C_SDA": [("U1", "33"), ("U2", "4"), ("J1", "4")],
    "I2C_SCL": [("U1", "36"), ("U2", "3"), ("J1", "3")],
    "RF_2G4": [("U1", "39"), ("J5", "1")],
    "VMID": [("R1", "2"), ("R2", "1"), ("C7", "1"), ("U3", "5"), ("U4", "5"), ("U5", "5")],
    "CH2_WE": [("U4", "3"), ("J3", "1")],
    "CH2_BUF": [("U4", "1"), ("U4", "2"), ("R8", "1")],
    "CH2_RE": [("U4", "6"), ("U4", "7"), ("J3", "2")],
    "AFE_CH2_OUT": [("R8", "2"), ("C11", "1"), ("U2", "8")],
}
EXPECTED_NETS.update(_amper_nets(1, "U3", "R3", "RV1", "R4", "R5", "R6", "R7", "C8", "C9", "C10", "J2", "7"))
EXPECTED_NETS.update(_amper_nets(3, "U5", "R9", "RV2", "R10", "R11", "R12", "R13", "C12", "C13", "C14", "J4", "9"))


def write_project_lib():
    lib = ["kicad_symbol_lib", ["version", 20231120], ["generator", Q("kicad_symbol_editor")],
           ["generator_version", Q("8.0")]] + [CUSTOM[k] for k in sorted(CUSTOM)]
    with open(os.path.join(HERE, "Glicovia.kicad_sym"), "w", encoding="utf-8") as f:
        f.write(fmt(lib) + "\n")
    # Library standar ikut didaftarkan di tabel proyek supaya proyek tetap lengkap
    # walau tabel library global KiCad belum dikonfigurasi.
    std = sorted({k.split(":")[0] for k in USED_STD_LIBS})
    lines = ['  (lib (name "Glicovia")(type "KiCad")(uri "${KIPRJMOD}/Glicovia.kicad_sym")'
             '(options "")(descr "Modul prototipe PKM-Glicovia"))']
    lines += [f'  (lib (name "{lib}")(type "KiCad")(uri "${{KICAD8_SYMBOL_DIR}}/{lib}.kicad_sym")'
              f'(options "")(descr "Library standar KiCad"))' for lib in std]
    with open(os.path.join(HERE, "sym-lib-table"), "w", encoding="utf-8") as f:
        f.write("(sym_lib_table\n  (version 7)\n" + "\n".join(lines) + "\n)\n")


USED_STD_LIBS = set()

if __name__ == "__main__":
    sch, tb = build()
    USED_STD_LIBS.update(k for k in sch.lib if not k.startswith("Glicovia:"))
    write_project_lib()
    out = os.path.join(HERE, f"{PROJECT}.kicad_sch")
    sch.write(out, tb)
    print("ditulis:", out)
