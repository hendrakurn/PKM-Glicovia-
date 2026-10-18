"""
PKM-GLICOVIA - Tekstur layar OLED SSD1306 128x64 (UI biosensor) untuk render assembly.

Output:
  textures/oled_screen_glicovia_128x64.png   (1 bit, resolusi asli panel)
  textures/oled_screen_glicovia_px.png       (upscale x8 dengan celah antar-piksel, dipakai di Blender)
Jalankan dengan python3 sistem (Pillow).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "textures"
W, H = 128, 64
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def draw_ui():
    img = Image.new("1", (W, H), 0)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"                       # tanpa anti-alias (piksel OLED murni)
    small = font(FONT_MONO, 8)
    label = font(FONT_BOLD, 8)
    big = font(FONT_BOLD, 24)

    # --- status bar ---
    d.text((1, 0), "GLICOVIA", font=label, fill=1)
    # ikon WiFi (3 busur sederhana)
    cx, cy = 92, 9
    for r in (2, 4, 6):
        d.arc((cx - r, cy - r, cx + r, cy + r), 225, 315, fill=1)
    d.point((cx, cy), fill=1)
    # ikon baterai 82%
    d.rectangle((104, 2, 122, 9), outline=1)
    d.rectangle((123, 4, 124, 7), fill=1)
    d.rectangle((106, 4, 106 + 13, 7), fill=1)
    d.line((0, 12, 127, 12), fill=1)

    # --- nilai utama ---
    d.text((1, 15), "GLUKOSA", font=small, fill=1)
    d.text((0, 23), "112", font=big, fill=1)
    d.text((56, 26), "mg/dL", font=small, fill=1)
    d.text((56, 37), "NORMAL", font=small, fill=1)

    # --- mini voltammogram (DPV) di kanan ---
    x0, y0, x1, y1 = 92, 15, 127, 47
    d.rectangle((x0, y0, x1, y1), outline=1)
    import math
    prev = None
    for i in range(x1 - x0 - 3):
        t = i / (x1 - x0 - 4)
        val = 0.12 + 0.78 * math.exp(-((t - 0.52) / 0.13) ** 2) + 0.06 * t
        px = x0 + 2 + i
        py = int(y1 - 2 - val * (y1 - y0 - 5))
        if prev:
            d.line((prev[0], prev[1], px, py), fill=1)
        prev = (px, py)

    # --- baris bawah: status 3 kanal SPE ---
    d.line((0, 51, 127, 51), fill=1)
    for k, xs in enumerate((1, 44, 87)):
        d.text((xs, 53), f"S{k + 1}", font=small, fill=1)
        d.rectangle((xs + 13, 55, xs + 37, 61), outline=1)
        fill_w = (22, 19, 21)[k]
        d.rectangle((xs + 15, 57, xs + 13 + fill_w, 59), fill=1)
    return img


def pixel_grid(img, scale=8, gap=1):
    """Upscale dengan celah gelap antar-piksel (struktur subpiksel OLED)."""
    w, h = img.size
    out = Image.new("L", (w * scale, h * scale), 0)
    px = img.load()
    d = ImageDraw.Draw(out)
    for y in range(h):
        for x in range(w):
            if px[x, y]:
                d.rectangle((x * scale, y * scale, x * scale + scale - 1 - gap, y * scale + scale - 1 - gap), fill=255)
    return out


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    ui = draw_ui()
    ui.save(OUT / "oled_screen_glicovia_128x64.png")
    pixel_grid(ui).save(OUT / "oled_screen_glicovia_px.png")
    print("saved", OUT)
