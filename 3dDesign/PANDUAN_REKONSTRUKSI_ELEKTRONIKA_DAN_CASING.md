# PANDUAN MASTER REKONSTRUKSI 3D RANGKAIAN ELEKTRONIKA & ASSEMBLY CASING PKM-GLICOVIA

> **Target Pembaca / Agent**: Claude Code (Opus 5.5) & Antigravity Agent  
> **Tujuan Utama**:  
> 1. Memperbaiki dan menyempurnakan model 3D `rangkaian_elektronika_pkm.blend` agar 100% akurat terhadap prototipe fisik pada `komponen/rangkaianTotal.jpeg` dan file detail di folder `komponen/`.  
> 2. Menggunakan **Playwright MCP** untuk mencari data teknis, part number LCSC, datasheet pinout, dan model 3D CAD pabrikan (`.STEP` / `.OBJ`).  
> 3. Menggabungkan (*merge / append*) rangkaian elektronika yang telah disempurnakan ke dalam casing bodi utama `PKM_Casing_Main` dari file `pkm_casing_final_Pimnas.blend` menjadi satu file assembly akhir (`pkm_glicovia_final_assembly.blend`).

---

## 1. STRUKTUR FILE & DIREKTORI PROYEK

```
/home/hendra/project/PKM-Glicovia-/3dDesign/
├── pkm_casing_final_Pimnas.blend     # File casing 3D utama (Casing Main, Lid, dudukan OLED & adapter)
├── rangkaian_elektronika_pkm.blend   # File model 3D rangkaian elektronika saat ini
├── build_detailed_electronics.py     # Script Python Blender pembuat komponen elektronika
├── render_multiview_rangkaian_all_sides.png # Render kompilasi 4 sudut elektronika saat ini
├── PANDUAN_REKONSTRUKSI_ELEKTRONIKA_DAN_CASING.md # (File ini - master instruction guide)
└── komponen/                         # Folder foto referensi prototipe fisik asli
    ├── rangkaianTotal.jpeg           # Foto prototipe lengkap (tampak atas dengan tangan memegang OLED)
    ├── rankaianTotal.jpeg            # Foto prototipe lengkap (tampak atas dalam baki aluminium)
    ├── boardutama.jpeg               # Foto close-up tampak atas main perfboard (ESP32, ADS1115, 3x OPA)
    ├── board.jpeg                    # Foto alternatif PCB utama dan wiring atas
    ├── koneksi.jpeg                  # Foto tampak bawah perfboard (jalur solder timah & jumper kawat)
    ├── esp32.jpeg                    # Modul ESP32 DevKit V1 (30-pin, IPEX connector, port micro-USB)
    ├── ADS1115.jpeg                  # Modul ADC 16-bit 4-channel (PCB biru, MSOP-10, header 10-pin)
    ├── IC_OPA.jpeg                   # 3x Modul SOP-8 to DIP-8 Op-Amp + kapasitor bypass biru & coklat
    ├── modulChargerTP4056.jpeg       # Modul charger Li-Ion TP4056 USB Type-C + saklar mini
    ├── baterai.jpeg                  # Baterai Li-Po pouch cell 3.7V dengan seal isolasi Kapton kuning
    ├── saklar.jpeg                   # Saklar rocker switch KCD11 merah-hitam (simbol I / O)
    ├── oled.jpeg                     # Layar OLED 0.96" I2C SSD1306 (kaca ganda, ribbon FFC, header 4-pin)
    ├── antena.jpeg                   # Antena 2.4 GHz Rubber Duck + mur heksagonal kuningan RP-SMA
    ├── adapter.jpeg                  # 3x Adapter SPE biru heatshrink + kabel konektor JST putih
    ├── spe.jpeg                      # Strip sensor SPE (Screen-Printed Electrode) 3-elektroda
    └── ukuranSPE.jpeg                # Foto strip SPE dengan penggaris milimeter (panjang 34mm, lebar 10mm)
```

---

## 2. DETAIL ANATOMI & DIMENSI KOMPONEN (BERDASARKAN FOTO `komponen/`)

| No | Komponen | File Foto Referensi | Dimensi Fisik (P × L × T) | Detail Geometri & Tekstur yang Wajib Akurat |
| :- | :--- | :--- | :--- | :--- |
| **1** | **Main Perfboard** | `boardutama.jpeg`<br>`koneksi.jpeg` | `50.0 × 70.0 × 1.6 mm` | Substrat FR4 hijau translusen. Grid matriks *through-hole* 2.54 mm (18×24 lubang) dengan cincin pad timah/emas. Rel tembaga daya samping. 4 lubang baut M3 sudut. Tampak bawah memiliki jalur solder timah manual (`koneksi.jpeg`). |
| **2** | **ESP32 DevKit V1** | `esp32.jpeg`<br>`boardutama.jpeg` | `51.5 × 28.5 × 7.0 mm` | PCB hitam matte, 2 baris 15-pin header emas (jarak antar baris 25.4 mm). Kaleng shield RF perak (`18×18 mm`) dengan bevel tepi. Area meander antena tembaga emas di ujung atas. **Konektor IPEX/u.FL emas** di sudut kanan atas shield. Port Micro-USB metal di ujung bawah. IC regulator AMS1117 (SOT-223), IC USB CP2102 (QFN-28), 2 tombol tactile EN & BOOT, serta LED SMD Merah/Biru. |
| **3** | **Modul ADS1115** | `ADS1115.jpeg`<br>`boardutama.jpeg` | `28.0 × 17.0 × 2.5 mm` | PCB biru tua glossy, 10-pin header emas di sisi kiri. IC ADC 16-bit MSOP-10 di tengah dengan 10 kaki *gull-wing* timah. 3 resistor pull-up array SMD (kode 103), kapasitor bypass, dan teks silkscreen putih (VDD, GND, SCL, SDA, ADDR, ALRT, A0–A3). |
| **4** | **3x OPA Breakouts** | `IC_OPA.jpeg`<br>`boardutama.jpeg` | Masing-masing `10.0 × 10.0 × 3.5 mm` | 3 papan adaptor SOP-8 ke DIP-8 hijau dipasang vertikal di sisi kanan perfboard. Masing-masing memiliki IC Op-Amp SOIC-8 dengan 8 kaki timah, 1 kapasitor keramik *dipped* biru (100nF), dan 1 kapasitor cakram coklat (*disc cap*). |
| **5** | **Modul TP4056** | `modulChargerTP4056.jpeg` | `28.0 × 17.3 × 4.2 mm` | PCB biru glossy. Soket **USB Type-C** metal stainless dengan mulut oval berongga dan 4 pin ground tab. IC Charger TP4056 (SOP-8), IC proteksi baterai DW01A (SOT-23-6), dan dual MOSFET FS8205A. Dua LED indikator SMD (Merah: Charging, Biru: Standby). 4 lubang pad sudut (IN+, IN-, B+, B-, OUT+, OUT-). |
| **6** | **Baterai Li-Po Pouch** | `baterai.jpeg` | `48.0 × 32.0 × 6.8 mm` | Kantung foil aluminium silver dengan **bibir kelim segel (*crimped edge seal*)** selebar 1.5 mm di ketiga sisinya. Bagian atas dilindungi balutan pita polimida Kapton amber transparan (`32 × 9 mm`). Terdapat papan proteksi PCM internal dan 2 kabel keluar (Merah: B+, Hitam: B-). Label teks hitam: *3.7V 1200mAh / 4.44Wh*. |
| **7** | **Saklar Rocker KCD11** | `saklar.jpeg` | `15.0 × 10.5 × 12.0 mm` | Bezel/frame luar plastik hitam dengan *snap-in retention ribs* (cutout panel `14 × 9 mm`). Tuas penekan cekung (*concave rocker*) warna merah cerah dengan ukiran simbol lingkaran putih **`O`** dan garis putih **`I`**. Di bawah terdapat 2 lug terminal sekop kuningan dengan lubang solder. |
| **8** | **Layar OLED 0.96"** | `oled.jpeg` | `27.3 × 27.8 × 3.5 mm` | PCB biru dengan 4 lubang baut sudut. Panel kaca ganda: substrat kaca bening + layar OLED aktif hitam gelap mengilap (`25 × 14.5 mm`). Pita kabel fleksibel oranye (*amber FFC ribbon*) terlipat di tepi bawah. Header 4-pin siku/lurus (VCC, GND, SCL, SDA). |
| **9** | **Antena 2.4 GHz + SMA** | `antena.jpeg` | Panjang `110 mm`, Ø `9.5 mm` | Konektor sekat (*bulkhead*) kuningan emas RP-SMA female dengan mur heksagonal 6 sisi (kunci 8mm) dan ring washer. Engsel tekuk (*swivel knuckle*) karet hitam dengan pin poros metal. Selongsong bodi karet elastis meruncing (*tapered rubber duck*) dengan cincin-cincin grip dan kubah ujung membulat. Kabel pigtail koaksial hitam RG1.13 menuju IPEX ESP32. |
| **10** | **3x Adapter SPE** | `adapter.jpeg` | Masing-masing `28.0 × 11.0 × 5.5 mm` | Bodi klip konektor terbungkus selongsong *heat-shrink tubing* biru dengan kontur mengecil ke belakang. Bagian belakang memiliki soket JST-XH 3-pin putih dengan terminal kancing. Bagian depan memiliki celah slot presisi untuk memasukkan strip elektroda SPE. |
| **11** | **Strip Elektroda SPE** | `ukuranSPE.jpeg`<br>`spe.jpeg` | `34.0 × 10.0 × 0.4 mm` (Exact) | Substrat plastik PET / keramik putih kaku. Memiliki 3 jalur konduktor perak/karbon paralel dari pin belakang ke sel elektrokimia. Dilapisi masker dielektrik hijau giok. Memiliki 3 elektroda: **Working Electrode (WE)** berupa cakram karbon hitam lingkaran pusat (Ø 3.0 mm), **Reference Electrode (RE)** berupa busur setengah lingkaran perak Ag/AgCl, dan **Counter Electrode (CE)** berupa cincin tapal kuda karbon hitam paling luar. |

---

## 3. PANDUAN PENGGUNAAN PLAYWRIGHT MCP

Agent Claude Code wajib menjalankan Playwright MCP untuk mengonfirmasi detail pabrikan jika memerlukan referensi visual tambahan atau file 3D CAD:

### Contoh Perintah & Query Pencarian:
1. **Mencari Model 3D STEP & Footprint Resmi di LCSC**:
   ```javascript
   // Buka LCSC dan cari part resmi ESP32 DevKit V1
   await page.goto("https://www.lcsc.com/search?q=ESP32-WROOM-32D");
   // Cari ADS1115
   await page.goto("https://www.lcsc.com/search?q=ADS1115IDGSR");
   // Cari TP4056 Type-C
   await page.goto("https://www.lcsc.com/search?q=TP4056");
   ```
2. **Mencari Diagram Dimensi Presisi**:
   ```javascript
   // Verifikasi dimensi DOIT ESP32 DevKit V1
   await page.goto("https://randomnerdtutorials.com/esp32-pinout-reference-gpios/");
   // Verifikasi datasheet SSD1306 OLED 0.96"
   await page.goto("https://www.adafruit.com/product/326");
   // Verifikasi dimensi saklar KCD11
   await page.goto("https://www.alldatasheet.com/view.jsp?Searchword=KCD11");
   ```
3. **Mencari Model CAD 3D Resmi**:
   - Cari di GrabCAD: `"ESP32 DevKit V1 STEP"`, `"TP4056 Type C CAD"`, `"0.96 OLED display STEP model"`.

---

## 4. SCHEMATIC & WIRING MATRIX (JARINGAN KABEL)

Semua kabel di Blender harus dimodelkan menggunakan kurva 3D (`CURVE` dengan `bevel_depth` dan resolusi halus), dengan warna insulasi yang persis seperti pada foto `rangkaianTotal.jpeg`:

```
[BATERAI LiPo 3.7V]
  ├── Merah (B+)  ──────> TP4056 [B+] pad
  └── Hitam (B-)  ──────> TP4056 [B-] pad

[TP4056 CHARGER]
  ├── Hitam (OUT-) ─────> Ground Bus Perfboard (GND)
  └── Putih (OUT+) ─────> Saklar KCD11 [Terminal 1]

[SAKLAR KCD11]
  └── Merah (Power Switched) ──> ESP32 [VIN / 5V] Pin Header

[I2C BUS (ESP32 ke Sensor & Layar)]
  ├── ESP32 3V3 (Pin 1) ───────> ADS1115 [VDD] & OLED [VCC] (Kabel Merah / Putih)
  ├── ESP32 GND (Pin 2) ───────> ADS1115 [GND] & OLED [GND] (Kabel Hitam)
  ├── ESP32 GPIO21 (SDA) ──────> ADS1115 [SDA] & OLED [SDA] (Kabel Kuning / Oranye)
  └── ESP32 GPIO22 (SCL) ──────> ADS1115 [SCL] & OLED [SCL] (Kabel Coklat / Biru)

[POTENSIOSTAT 3-CHANNEL OPA ke ADS1115]
  ├── Channel 1 OPA Output ────> ADS1115 Analog In [A0]
  ├── Channel 2 OPA Output ────> ADS1115 Analog In [A1]
  └── Channel 3 OPA Output ────> ADS1115 Analog In [A2]

[3x ADAPTER SPE ke 3x OPA BOARD]
  ├── Masing-masing Adapter memiliki 3 kabel (Merah: WE, Kuning: RE, Hitam: CE)
  └── Total 9 kabel melengkung dari adapter SPE depan menuju deretan 3 modul OPA di sisi kanan perfboard.

[RF ANTENNA]
  └── ESP32 IPEX Connector ───> Kabel koaksial hitam fleksibel ───> Soket RP-SMA Antena Kuningan
```

---

## 5. SPESIFIKASI ASSEMBLY & INTEGRASI KE CASING (`pkm_casing_final_Pimnas.blend`)

### 5.1 Koordinat & Dimensi Casing Eksisting
Dari inspeksi data Blender pada file `pkm_casing_final_Pimnas.blend`:
- **`PKM_Casing_Main`**:
  - Ukuran Luar: `90.0 mm` (Sumbu X) × `130.0 mm` (Sumbu Y) × `50.0 mm` (Sumbu Z).
  - Bounding Box: X `[-45.0, 45.0]`, Y `[-65.0, 65.0]`, Z `[0.0, 50.0]`.
- **`PKM_Casing_Lid`**:
  - Ukuran: `90.0 mm × 130.0 mm × 6.7 mm` (saat ini diletakkan terbuka di offset X = 105.0 mm).
- **Posisi Komponen Eksisting di dalam Casing**:
  - **Layar OLED sudah memiliki posisi patokan**: Objek `OLED_PCB` terletak pada koordinat `(X=0.0, Y=15.2, Z=43.93)`. Posisi ini tepat berada di bawah jendela lubang kaca pada permukaan atas casing (`Z=50.0`).

### 5.2 Tata Letak (Layout) Komponen di Dalam Casing:

```
+-------------------------------------------------------+  Y = +65 (Belakang)
|  [Antena SMA Bulkhead: Lubang Ø6.5mm di Dinding Belakang / Kanan] |
|                                                       |
|   +-------------------+       +-------------------+   |
|   |  TP4056 Charger   |       |  Saklar KCD11     |   |
|   |  (Port Type-C     |       |  (Rocker Switch)  |   |
|   |   menghadap sisi) |       |                   |   |
|   +-------------------+       +-------------------+   |
|                                                       |
|              +-----------------------------+          |
|              |      Jendela Layar OLED     |          |
|              |      (X=0, Y=15.2, Z=44)    |          |
|              +-----------------------------+          |
|                                                       |
|   +--------------------+   +----------------------+   |
|   |  Baterai Li-Po     |   |  Main Perfboard      |   |
|   |  3.7V 1200mAh      |   |  (ESP32 + ADS1115    |   |
|   |  (32 x 48 x 7 mm)  |   |   + 3x OPA Modules)  |   |
|   +--------------------+   +----------------------+   |
|                                                       |
|   [ Slot 3x Adapter SPE: 3 Lubang di Dinding Depan ]   |
+-------------------------------------------------------+  Y = -65 (Depan)
```

1. **Bagian Depan (Y = -65)**:
   - Dinding depan memiliki lubang slot untuk 3x adapter SPE (`Adapter_V1_Base` dan `Adapter_V1_Lid`).
   - Tiga adapter SPE terpasang mengarah keluar, memudahkan strip elektroda dimasukkan dari luar casing.
2. **Bagian Tengah Atas (Y = 15.2, Z = 44)**:
   - Modul Layar OLED `0.96"` dipasang tepat mengunci di bawah jendela kaca casing.
3. **Bagian Lantai Bawah (Z = 2 s/d Z = 25)**:
   - **Kanan**: Main Perfboard (`50 × 70 mm`) diletakkan di atas tiang *stand-off* bodi bawah. Port Micro-USB ESP32 bisa diakses untuk flashing firmware.
   - **Kiri Bawah**: Baterai Li-Po (`32 × 48 × 7 mm`) diletakkan di kompartemen samping perfboard.
4. **Dinding Samping / Belakang**:
   - **Modul TP4056**: Port USB Type-C menghadap lubang cutout samping casing agar bisa dicas dari luar.
   - **Saklar KCD11**: Masuk ke lubang kotak saklar di dinding atas/belakang.
   - **Antena RP-SMA**: Baut kuningan bulkhead dipasang menembus lubang melingkar Ø 6.5 mm di dinding bodi belakang/kanan, mur heksagonal mengunci dari luar, dan antena karet berdiri tegak / ditekuk 90°.

---

## 6. LANGKAH KERJA UNTUK CLAUDE CODE OPUS 5.5

Ikuti urutan langkah berikut secara terstruktur:

### Tahap 1: Verifikasi & Unduh Referensi Tambahan via Playwright MCP
1. Buka browser via Playwright untuk memvalidasi datasheet dan model 3D CAD:
   - Cari model 3D CAD ESP32 DevKit V1 dan SSD1306 OLED (format STEP).
   - Pastikan posisi pinout dan toleransi lubang konektor sesuai standar.

### Tahap 2: Sempurnakan File `rangkaian_elektronika_pkm.blend`
1. Buka file `rangkaian_elektronika_pkm.blend` via Blender MCP (`execute_blender_code`).
2. Tingkatkan detail visual pada komponen yang masih berupa balok sederhana:
   - Tambahkan lubang rongga port Micro-USB dan Type-C.
   - Berikan tekstur silkscreen tulisan pada bodi IC ESP32 (*Espressif ESP-WROOM-32*), ADS1115, dan Baterai.
   - Pastikan elektroda SPE memiliki 3 sel konsentris (Cakram tengah, busur referensi, cincin luar).
   - Pastikan warna insulasi kabel fleksibel melengkung secara natural (tidak kaku/tajam).

### Tahap 3: Pembuatan File Assembly Gabungan (`pkm_glicovia_final_assembly.blend`)
1. Buka file `pkm_casing_final_Pimnas.blend`.
2. Lakukan `bpy.ops.wm.append` untuk memuat seluruh collection `PKM_Electronics_Assembly` dari `rangkaian_elektronika_pkm.blend`.
3. Simpan file baru sebagai:
   `/home/hendra/project/PKM-Glicovia-/3dDesign/pkm_glicovia_final_assembly.blend`.

### Tahap 4: Penataan (*Fitting & Assembly*) di Dalam Casing
1. Posisikan `Main_Perfboard` ke dalam kompartemen bawah casing (pastikan tidak menabrak tiang baut lid).
2. Sejajarkan 3x Adapter SPE dengan lubang slot depan `PKM_Casing_Main`.
3. Sejajarkan modul OLED dengan jendela display atas (`X=0.0, Y=15.2, Z=43.93`).
4. Pasang modul TP4056 sejajar dengan lubang colokan charger Type-C di dinding casing.
5. Pasang mur heksagonal kuningan SMA antena menembus lubang antena casing.
6. Lakukan penyesuaian kurva kabel (*wire bezier handles*) agar seluruh kabel tertata rapi di dalam interior casing tanpa ada kabel yang menembus (*clipping*) dinding casing.

### Tahap 5: Setup Pencahayaan Studio & Render Akhir
1. Buat 2 mode tampilan kamera:
   - **Mode Exploded / Open View**: Tutup casing (`PKM_Casing_Lid`) dibuka ke samping agar juri/dosen dapat melihat kerapian rangkaian elektronik di dalam casing.
   - **Mode Assembled View**: Tutup casing terpasang rapat, memperlihatkan produk akhir yang siap pakai.
2. Gunakan render engine **EEVEE Next** (dengan Raytracing + Fast GI) atau **Cycles** (samples 256 + OpenImageDenoise).
3. Atur Color Management ke **AgX - High Contrast** dengan resolusi **2560 × 1440 (2K QHD)**.
4. Render 4 sudut pandang (Isometrik, Atas, Depan, Samping) dan simpan gambar hasil render.

---

## 7. KRITERIA PENERIMAAN (*ACCEPTANCE CRITERIA*)
- [ ] Tidak ada komponen yang melayang tanpa dudukan atau saling menembus (*mesh intersection/clipping*).
- [ ] Seluruh port eksternal (USB-C charger, slot strip SPE, tombol saklar, antena) sejajar sempurna dengan lubang cutout casing.
- [ ] Layar OLED pas di bawah lubang kaca penutup atas.
- [ ] Tampilan render tajam, memiliki bayangan kontak realistis (*contact shadow*), dan material terlihat nyata (plastik ABS casing, logam kuningan SMA, kaca OLED, silikon kabel).
- [ ] File project `pkm_glicovia_final_assembly.blend` tersimpan bersih dan siap dibuka di Blender versi 4.2+ / 5.x.
