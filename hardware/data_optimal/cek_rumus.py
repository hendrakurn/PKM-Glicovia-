"""Cek: konversi di ringkasan_sesi.csv == blok CALC asli main.cpp (dikompilasi g++).
    python3 cek_rumus.py
"""
import subprocess
import tempfile
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
src = (HERE.parent / "f_endtoend" / "main.cpp").read_text()
calc = src[src.index("// >>> CALC"):src.index("// <<< CALC")]
# Konstanta di luar blok CALC yang dipakai di dalamnya, diambil apa adanya dari main.cpp
deps = [l for l in src.splitlines()
        if l.startswith(("const float    RF", "#define DEVICE_CODE", "#define FW_VERSION"))]
prog = """#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
""" + "\n".join(deps) + "\n" + calc + """
int main() {
  float vph, vmid, vfru, i;
  while (scanf("%f %f %f %f", &vph, &vmid, &vfru, &i) == 4) {
    bool c = false;
    printf("%.4f %.4f %.4f\\n", phFromV(vph, &c), fruFromV(vmid, vfru, &c), gluFromI(i, &c));
  }
}
"""
ring = pd.read_csv(HERE / "ringkasan_sesi.csv")
with tempfile.TemporaryDirectory() as d:
    cpp, exe = Path(d) / "calc.cpp", Path(d) / "calc"
    cpp.write_text(prog)
    subprocess.run(["g++", "-O0", "-o", str(exe), str(cpp)], check=True)
    inp = "\n".join(f"{r.VpH_V} {r.Vmid_V} {r.Vfru_V} {r.I_trim_nA}" for r in ring.itertuples())
    out = subprocess.run([str(exe)], input=inp, capture_output=True, text=True, check=True).stdout.split("\n")

for r, line in zip(ring.itertuples(), out):
    ph, fru, glu = map(float, line.split())
    assert abs(ph - r.pH) < 0.01 and abs(fru - r.fructosamine_umol_L) < 0.1 \
        and abs(glu - r.salivary_glucose_mgdL) < 0.01, (r.sesi, r.versi, line)
print(f"OK: {len(ring)} baris ringkasan cocok dengan CALC main.cpp")
