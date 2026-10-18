# PROMPT MASTER: EKSEKUSI ASSEMBLY FINAL & MULTI-VIEW RENDERING PKM-GLICOVIA
> **Target Model / Agent**: Claude Code (Opus 5.5) / Antigravity Agent  
> **Environment**: Ubuntu 24.04 LTS, Blender 5.2.2 LTS (`/snap/bin/blender`), Blender Python API (`bpy`)  
> **Output Utama**:
> 1. File Blender Assembly Baru: `/home/hendra/project/PKM-Glicovia-/3dDesign/pkm_glicovia_final_assembly.blend`
> 2. Hasil Render Foto Multi-Sudut: Disimpan di folder `/home/hendra/project/PKM-Glicovia-/3dDesign/finalImage/`

---

## SALIN & TEMPELKAN PROMPT BERIKUT KE CLAUDE CODE OPUS 5.5:

```markdown
Anda adalah Senior 3D CAD & Mechatronics Visualization Engineer yang sangat teliti. Tugas Anda adalah melakukan integrasi fisik (*assembly final*), merapikan wiring sirkuit, dan merender foto produk 3D kualitas tinggi untuk alat biosensor elektrokimia portabel **PKM-Glicovia (Pimnas)**.

### 1. FILE & DIREKTORI SUMBER
- Master Panduan Teknis: `/home/hendra/project/PKM-Glicovia-/3dDesign/PANDUAN_REKONSTRUKSI_ELEKTRONIKA_DAN_CASING.md`
- File Casing CAD Master: `/home/hendra/project/PKM-Glicovia-/3dDesign/pkm_casing_final_Pimnas.blend`
- File Elektronika Rangkaian: `/home/hendra/project/PKM-Glicovia-/3dDesign/rangkaian_elektronika_pkm.blend`
- Folder Foto Prototipe Fisik: `/home/hendra/project/PKM-Glicovia-/3dDesign/komponen/`
- Target File Blender Baru: `/home/hendra/project/PKM-Glicovia-/3dDesign/pkm_glicovia_final_assembly.blend`
- Target Folder Output Render: `/home/hendra/project/PKM-Glicovia-/3dDesign/finalImage/`

---

### 2. TUJUAN & SPESIFIKASI ASSEMBLY

Buat file Blender baru bernama `pkm_glicovia_final_assembly.blend` dengan menggabungkan casing dari `pkm_casing_final_Pimnas.blend` dan sirkuit elektronika dari `rangkaian_elektronika_pkm.blend`. Seluruh komponen elektronika yang sebelumnya tersebar mendatar di meja harus ditata rapi ke dalam rongga dalam casing bodi utama (`PKM_Casing_Main`).

#### Batasan Koordinat & Dimensi:
- **Dimensi Luar Casing**: $90.0 \times 130.0 \times 50.0\text{ mm}$ (Sumbu $X \in [-45, 45]$, $Y \in [-65, 65]$, $Z \in [0, 50]$).
- **Rongga Dalam Efektif**: $X \in [-40, 40]$, $Y \in [-60, 60]$, $Z \in [2, 46]$.

#### Peta Penataan Komponen (Layout Matrix):
1. **Layar OLED 0.96"**: Kunci tepat pada dudukan bracket di balik atap casing pada koordinat patokan `(X=0.0, Y=15.2, Z=43.93)` sehingga kaca layar sejajar pas di bawah jendela display casing.
2. **3x Adapter SPE & Sensor Strip**: Kunci presisi pada 3 slot lubang dinding depan ($Y = -65.0$, $Z \approx 11\text{--}15\text{ mm}$), mengarah keluar ke sumbu $-Y$, dengan 3 strip sensor SPE tertancap horizontal (elektroda menghadap atas).
3. **Main Perfboard ($50 \times 70\text{ mm}$)**: Dudukkan di lantai dasar sebelah kanan ($X \in [-10, 38]$, $Y \in [-25, 45]$, $Z \approx 4\text{ mm}$), bertumpu pada tiang stand-off. Memuat ESP32 DevKit, ADS1115, dan 3x modul OPA2333.
4. **Baterai Li-Po 1200mAh ($32 \times 48 \times 6.8\text{ mm}$)**: Diletakkan mendatar di lantai sebelah kiri perfboard ($X \in [-38, -10]$, $Y \in [-20, 28]$, $Z \approx 3\text{ mm}$).
5. **Modul Charger TP4056 & Saklar KCD11**: Posisikan di dinding samping/belakang dengan mulut port USB Type-C rata dengan lubang dinding casing, dan saklar terpasang pada bezel cutout panel.
6. **Antena 2.4 GHz RP-SMA**: Bulkhead kuningan menembus lubang dinding belakang ($Y = +65.0$), mur heksagonal mengunci dari luar, antena ditekuk 90° ke atas atau berdiri tegak.

#### Penataan Ulang Kabel (Cable Re-Routing):
- Modifikasi titik kontrol (*Bézier curve handles*) seluruh kabel:
  - 4 kabel OLED melengkung halus dari pin header naik ke jendela atap.
  - 9 kabel sensor SPE melengkung pendek dari soket adapter depan ke 3 modul OPA.
  - Kabel daya baterai & saklar diselipkan rapi di tepi dinding.
  - Kabel koaksial pigtail RG1.13 meliuk dari konektor IPEX ESP32 ke konektor SMA belakang.
- **PENTING**: Tidak boleh ada kawat kabel yang melenceng atau menembus (*clipping*) dinding casing!

---

### 3. STRUKTUR SCENE & VISIBILITY CONTROL

Atur hierarki collection di dalam Blender:
- `PKM_Casing` (Berisi `PKM_Casing_Main`, `PKM_Casing_Lid`, dan baut pengunci)
- `PKM_Electronics` (Perfboard, ESP32, ADS1115, OPA, Baterai, TP4056, Switch, Antena, SPE)
- `PKM_Wiring` (Seluruh kurva Bézier kabel jumper)
- `Studio_Lighting` (Kamera & 3-point studio lighting)

Siapkan 2 kondisi tampilan:
1. **Assembled (Closed Casing)**: `PKM_Casing_Lid` menutup rapat di bawah ($Z = 0$).
2. **Internal / Exploded (Open Casing)**: `PKM_Casing_Lid` digeser ke bawah ($Z = -35\text{ mm}$) atau di-hide, dan/atau casing bodi sedikit terangkat agar juri dapat melihat kerapian rangkaian sirkuit di dalam rongga casing.

---

### 4. PANDUAN RENDERING & KAMERA MULTI-SISI

Konfigurasikan render engine Blender:
- **Engine**: Cycles (Samples: 128 - 256, Denoise: OpenImageDenoise aktif) ATAU EEVEE Next (Raytracing & Fast GI on).
- **Resolusi**: $2560 \times 1440$ (2K QHD), format PNG 16-bit RGB.
- **Color Management**: View Transform `AgX` atau `Filmic`, Look `High Contrast`.
- **Lighting**: 3-point softbox studio (Key Light 400W, Fill Light 200W, Rim Light 600W di belakang untuk rim highlight elegan).

Ambil dan simpan gambar hasil render berikut ke dalam direktori `/home/hendra/project/PKM-Glicovia-/3dDesign/finalImage/`:

1. `finalImage/01_pkm_assembled_isometric.png`:
   - Sudut isometrik utama (3/4 angle), memperlihatkan casing tertutup, jendela OLED menyala, 3 strip SPE di depan, dan antena di belakang.
2. `finalImage/02_pkm_assembled_top_oled.png`:
   - Tampak atas tegak lurus (*Top View*), memperlihatkan proporsi casing, bezel jendela, tampilan layar OLED biosensor, dan strip sensor.
3. `finalImage/03_pkm_assembled_front_sensors.png`:
   - Tampak depan rendah (*Eye-level Front View*), fokus tajam (*close-up*) pada 3 adapter biru dan 3 strip sensor SPE berdetail elektroda.
4. `finalImage/04_pkm_assembled_side_ports.png`:
   - Tampak samping & belakang, memperlihatkan kepresisian port USB-C TP4056, saklar rocker KCD11, dan dudukan bulkhead antena RP-SMA.
5. `finalImage/05_pkm_internal_circuit_open_lid.png`:
   - Tutup bawah casing dilepas/dibalik, memperlihatkan penataan bersih sirkuit elektronika di dalam rongga bodi (menunjukkan kepatuhan engineering).
6. `finalImage/06_pkm_exploded_assembly_view.png`:
   - Tampilan *Exploded Assembly View* bertingkat (Atap casing, layar OLED, rangkaian board utama, kabel, dan tutup bawah terpisah melayang di sumbu Z).
7. `finalImage/07_pkm_multiview_grid_4in1.png`:
   - Gambar kompilasi 4 tampilan (Isometric, Top, Front, Internal) dalam satu kanvas gambar beresolusi $3840 \times 2160$ (4K UHD) siap pasang di slide presentasi PPT Pimnas.

---

### 5. VERIFIKASI & ACCEPTANCE CRITERIA
Setelah seluruh script eksekusi selesai:
- [ ] File `/home/hendra/project/PKM-Glicovia-/3dDesign/pkm_glicovia_final_assembly.blend` berhasil disimpan dan dapat dibuka tanpa missing data.
- [ ] Seluruh 7 file gambar render di atas telah ter-generate sempurna di folder `/home/hendra/project/PKM-Glicovia-/3dDesign/finalImage/`.
- [ ] Tidak ada mesh clipping antara kabel dan dinding casing.
- [ ] Tampilkan ringkasan status render dan konfirmasi dimensi akhir.
```
