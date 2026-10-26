# data_optimal — CONTOH data optimal (SIMULASI)

> **Bukan hasil pengukuran.** Isi folder ini adalah contoh volt yang *seharusnya* terbaca bila sensor
> sudah optimal, dibuat dari struktur sesi asli di `../data_log/`. Jangan dilaporkan sebagai data ukur;
> bila dipakai di laporan, beri label "simulasi/ilustrasi target".

## Isi
| File | Isi |
|---|---|
| `buat_data_optimal.py` | Pembuat data. `python3 buat_data_optimal.py` |
| `cek_rumus.py` | Kompilasi blok `CALC` asli `../f_endtoend/main.cpp` (g++) dan cocokkan dengan ringkasan |
| `sesi/*_optimal.csv` | Per baris: kolom sama dengan log asli + `pH`, `fructosamine_umol_L`, `salivary_glucose_mgdL` |
| `ringkasan_sesi.csv` | Per sesi, versi `asli` vs `optimal`, dihitung seperti `measure()` (40 sampel terakhir, trimmed mean arus) |
| `sesi/contoh_PRE-DIABETES_lengkap_optimal.csv` | Contoh sesi Pre-Diabetes lengkap (150 s, 355 baris), karena log asli hanya 5 baris |
| `perbandingan_optimal.png` | Grafik per kelas (titik = sesi, hanya sesi ≥ 40 sampel) |
| `analisis_korelasi.py` | Regresi volt→satuan, volt asli vs optimal, korelasi Spearman, pemisahan kelas |
| `korelasi_volt_satuan.png`, `volt_asli_vs_optimal.png`, `korelasi_matriks.png` | Keluaran `analisis_korelasi.py` |
| `hasil_pembahasan_optimal.md` | Draf Hasil dan Pembahasan dari data optimal |
| `deret_waktu_3kelas.png` | Deret waktu satu sesi per kelas; garis tebal = 40 sampel yang dipakai `measure()` |

## Cara dibuat
- Dari file asli dipakai: `waktu_iso`, `t_detik`, jumlah baris, `Vmid_V`.
- Target satuan riil per kelas = rerata data dummy tempat model SVM dilatih, ditambah variasi antar-sesi kecil:

| Kelas | pH | Fruktosamin (µmol/L) | Glukosa saliva (mg/dL) |
|---|---|---|---|
| Normal | 6,94 | 224 | 0,67 |
| Pre-Diabetes | 6,49 | 285 | 1,16 |
| Diabetes | 5,88 | 350* | 3,31 |

  \*Dummy = 386, diturunkan karena batas baca rumus (lihat bawah).
- Volt dihitung dari invers rumus `main.cpp`:
  - `VpH = -0,05916·pH + 0,3226`
  - `Vfru = Vmid − (35·fru − 4000)·1e-9·Rf`
  - `raw = −(1000·glu)·1e-9·Rf / (1,024/32768)` (GAIN_FOUR), `Vglu = Vmid + raw·LSB`
- Ditambah noise kecil dan lonjakan awal (tau 5 s). Status dihitung dengan logika `label()`.

## Batas fisik rumus sementara (perlu diperbaiki di alat sungguhan)
1. **pH**: `VpH = 0 V` ↔ pH 5,45. Semua pH saliva fisiologis (≈5,7–7,0) butuh **VpH negatif**, padahal ADS1115 single-ended tidak bisa membaca < 0 V. Elektroda pH perlu diukur relatif ke VMID (diferensial A2−A3) atau offset kalibrasi diganti.
2. **Fruktosamin**: dengan VMID terukur ≈ 0,913 V, nilai maksimum yang terbaca = 375 µmol/L (saat Vfru = 0). Data asli Diabetes menempel di batas ini, karena Vfru ≈ 0. VMID 1,65 V menaikkan batas ke ≈ 586.
3. **Glukosa**: batas jenuh `|raw| > 32000` ↔ 10 mg/dL. Log asli terkunci di ≈ 7160 nA (status JENUH semua).
4. **Pre-Diabetes** hanya punya 5 baris (≈ 2 s). Lonjakan awal belum turun, jadi glukosanya terbaca 1,83 (target 1,16). Sesi ini perlu diambil ulang ≥ 60 s + 40 sampel. Contoh bentuk yang benar ada di `contoh_PRE-DIABETES_lengkap`.
5. **Label 126 mg/dL** pada file Pre-Diabetes asli secara kriteria ADA/Perkeni termasuk **diabetes** (GDP ≥ 126); rentang prediabetes adalah 100–125 mg/dL. Contoh lengkap memakai referensi 112 mg/dL.

## Pelatihan AI pada data optimal (`ai/`)
- `ai/latih_ai_optimal.py`: SVR (tegangan -> pH, fruktosamin, glukosa saliva) dan SVM (kelas), LOSO. Menambah 3 sesi Pre-Diabetes simulasi (`ai/sesi_prediabetes_ekstra/`).
- `ai/hasil_pembahasan_ai_optimal.md`: draf Hasil dan Pembahasan; `ai/ai_gambar_*.png`: Gambar 9-12; `ai/tabel*_*.csv`, `ai/dataset_jendela.csv`: angka sumber.
- Semua SIMULASI; regresi linear sudah sempurna dan tiap kanal tunggal memisahkan kelas, jadi bukan bukti kinerja alat.
