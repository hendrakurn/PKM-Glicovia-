"""
PKM-GLICOVIA - Kompilasi 4 tampilan (Isometrik, Atas, Depan, Internal) 3840x2160 (4K UHD) untuk slide Pimnas.
Jalankan: python3 make_final_grid.py   (Pillow, Python sistem)
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DIR = Path(__file__).resolve().parent / "finalImage"
OUT = DIR / "07_pkm_multiview_grid_4in1.png"
W, H = 3840, 2160
GUTTER = 8
TILES = [
    ("01_pkm_assembled_isometric.png", "ISOMETRIK", "Rakitan tertutup"),
    ("02_pkm_assembled_top_oled.png", "TAMPAK ATAS", "Layar OLED biosensor"),
    ("03_pkm_assembled_front_sensors.png", "TAMPAK DEPAN", "3 adapter + strip SPE"),
    ("05_pkm_internal_circuit_open_lid.png", "INTERNAL", "Casing dibuka (cutaway)"),
]
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def main():
    canvas = Image.new("RGB", (W, H), (245, 246, 248))
    tw, th = (W - GUTTER) // 2, (H - GUTTER) // 2
    fb = ImageFont.truetype(FONT_B, 44)
    fr = ImageFont.truetype(FONT_R, 34)
    for i, (fname, title, sub) in enumerate(TILES):
        im = Image.open(DIR / fname).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = (i % 2) * (tw + GUTTER)
        y = (i // 2) * (th + GUTTER)
        canvas.paste(im, (x, y))
        # label: pita gelap semi-transparan di kiri bawah
        ov = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        bw = max(d.textlength(title, font=fb), d.textlength(sub, font=fr)) + 72
        d.rounded_rectangle((36, th - 176, 36 + bw, th - 36), radius=18, fill=(16, 22, 28, 190))
        d.rectangle((36, th - 176, 46, th - 36), fill=(46, 204, 113, 255))
        d.text((72, th - 162), title, font=fb, fill=(255, 255, 255, 255))
        d.text((72, th - 102), sub, font=fr, fill=(210, 222, 230, 255))
        canvas.paste(ov, (x, y), ov)
    canvas.save(OUT, optimize=True)
    print("saved", OUT, canvas.size)


if __name__ == "__main__":
    main()
