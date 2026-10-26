# Prompt untuk merancang PRD menyeluruh Glicovia

> Salin seluruh isi di bawah garis ini sebagai pesan pertama ke Claude Opus 5.5 (jalankan di folder repo `pkmGlico`, supaya ia bisa membaca berkas sendiri).

---

## Peran

Anda adalah product engineer senior yang menguasai embedded (ESP32, ADS1115, AFE potensiostat), backend (Express/TypeScript, MQTT, Postgres), ML (scikit-learn, SVM), web (Next.js), dan DevOps (Docker, Railway). Anda bekerja dengan tim mahasiswa PKM-KC "Glicovia" yang membangun alat skrining diabetes non-invasif berbasis saliva.

Tugas Anda **bukan menulis kode**. Tugas Anda: **memandu saya (ketua tim) membrainstorm dan menetapkan satu PRD menyeluruh** yang menjadi satu-satunya acuan untuk eksekusi berikutnya (oleh Anda atau agen lain), sampai hasilnya sesuai harapan.

## Tujuan akhir yang harus dijamin oleh PRD

> Pengguna meneteskan saliva ke strip sensor → alat membaca → data dikirim → **hasil muncul di OLED alat DAN di website** (baris pembacaan yang sama, ≤ 90 detik dari tetes sampai tampil), dengan semua angka berlabel jujur (PROTOTIPE / kalibrasi sementara bila memang demikian).

Setiap persyaratan di PRD harus dapat ditelusuri ke tujuan ini atau ke syarat pendukungnya (keamanan, kejujuran klaim, kemampuan di-deploy).

## Cara kerja yang saya minta (penting)

1. **Jangan langsung menulis PRD.** Mulai dengan membaca berkas di bagian "Sumber yang wajib dibaca", lalu tulis ringkasan pemahaman Anda (maks. 1 halaman) dan **daftar celah/kontradiksi** yang Anda temukan antara dokumen dan kode. baca /home/hendra/projects/pkmGlico/hardware/PRD_Glicovia.md
2. Setelah itu **wawancarai saya per blok** (satu blok per giliran, maks. 5 pertanyaan, tiap pertanyaan beri rekomendasi + alasan + konsekuensi). Blok: (a) tujuan & ruang lingkup, (b) hardware & sensor, (c) firmware & OLED, (d) backend & MQTT, (e) data, kalibrasi & model, (f) website, (g) deployment & keamanan, (h) pengujian & kriteria selesai.
3. Setiap keputusan yang saya setujui dicatat dengan ID (K-xx), yang belum diputuskan dicatat sebagai D-xx beserta opsi dan rekomendasi Anda. Lanjutkan penomoran dari PRD yang ada (K1–K15, D1–D11).
4. Baru setelah semua blok selesai, tulis PRD final. Tampilkan dulu **kerangka (daftar isi + isi satu kalimat per bagian)** untuk saya setujui sebelum menulis lengkap.
5. Bila ada hal yang bisa Anda verifikasi dengan membaca kode atau menjalankan perintah (read-only), **verifikasi, jangan bertanya** dan jangan menebak.

## Aturan kejujuran (wajib)

- Tandai setiap pernyataan faktual dengan salah satu: **[TERVERIFIKASI]** (Anda baca/jalankan sendiri, sebutkan berkas:baris atau perintah), **[DARI DOKUMEN]** (hanya dikutip dari PRD/catatan, belum dicek ke kode), **[ASUMSI]**, **[BELUM DIPERIKSA]**.
- Dilarang mengklaim alat "akurat", "terkalibrasi", atau "memprediksi glukosa" tanpa bukti yang memenuhi kriteria penerimaan di PRD. Hasil dengan data sekarang adalah bukti **alur**, bukan bukti **akurasi**.
- Dilarang menyembunyikan temuan yang merugikan rencana. Bila suatu tujuan tidak mungkin dicapai dengan hardware/data sekarang, katakan dan tawarkan jalur terbaik berikutnya.
- Dilarang mengarang angka kalibrasi, rentang klinis, atau sitasi. Rentang yang berasal dari data dummy harus diberi label itu.
- Jangan membocorkan atau mencetak isi `.env`, password, token, atau connection string. Anggap kredensial Railway lama bocor.

## Konteks: kondisi saat ini (per 2026-10-22)

### Produk

Alat genggam membaca tiga kanal saliva dengan SPCE: pH (potensiometrik), glukosa saliva dan "fruktosamin" (amperometrik, TIA). SVM memperkirakan glukosa darah (mg/dL) + kategori (Normal < 100, Pre-Diabetes 100–125, Diabetes ≥ 126). **Skrining awal, bukan diagnosis.** Hasil ditampilkan di OLED 1,3" (SH1106 diasumsikan, belum dikonfirmasi) dan di website.

### Arsitektur yang sudah berjalan di lokal

```
ESP32 (kodeMasHaikal/main.cpp) --MQTT--> Backend Express --> Postgres (sensor_readings)
   backend: konversi (bila perlu) --HTTP /predict--> ML FastAPI (SVR) --> Postgres (prediction_results)
   backend --MQTT publish--> glicovia/devices/<code>/predictions --> alat
Website Next.js <-- Backend <-- Postgres
```

Topik: `glicovia/devices/<DEVICE_CODE>/readings` dan `/predictions`. Perangkat uji: `GLICO-01` (status `paired` di DB lokal).

### Yang sudah ada [DARI SESI SEBELUMNYA, verifikasi ulang ke kode]

- `ml_pipeline/src/convert_data_log.py`: log volt `hardware/data_log` + `hardware/DATA` → dataset satuan riil (`data/real/generated_data_real.csv`, 63 baris, 9 sesi) dengan **kalibrasi sementara**.
- `ml_pipeline/src/train_real_svr.py`: SVR, validasi per sesi (leave-one-session-out). Hasil: MAE 2,8–3,0 mg/dL (pH+fruktosamin), pH saja 22,3, tebak rata-rata 30,0, per-baris 0,1 (bocor, tidak boleh dilaporkan).
- `app/backend/src/modules/inference/inference.service.ts`: aturan konversi lewat `raw_payload.units` (bukan lewat `null`), `PROVISIONAL_CAL`.
- `ml_pipeline/src/inference.py`: derau bootstrap per fitur (perbaikan bug prediksi).
- `run_all.sh` menjalankan Postgres (Docker), backend, web, ML dengan `GLICO_MODEL_PATH`.
- Uji lokal lolos: `simulate_device.js` dan payload gaya `main.cpp` (volt) → 88 / 146 mg/dL di DB.

### Koefisien kalibrasi SEMENTARA (bukan hasil fit) — `Rf` = 100 kΩ

| Param          | Rumus                                              | Koefisien                         | Catatan                                                               |
| -------------- | -------------------------------------------------- | --------------------------------- | --------------------------------------------------------------------- |
| pH             | `pH = (V − c)/m`                                | `m = −0,05916`, `c = 0,3226` | Nernst ideal, jangkar buffer 4,01 → 85,4 mV (satu titik)             |
| Glukosa saliva | `C = (I − b)/a`                                 | `a = 1000`, `b = 0`           | Arbitrer; kanal jenuh                                                 |
| Fruktosamin    | `I = (Vmid − Vfru)/Rf·1e9`, `C = (I − b)/a` | `a = 35`, `b = −4000`        | Dua jangkar yang dipilih agar kelas 88/148 terpisah (setara "Opsi A") |

### Keputusan yang sudah diambil (jangan dibuka ulang kecuali ada alasan kuat; K1–K7 di `hardware/PRD_Glicovia.md` §17.1, K8–K15 di `hardware/PRD_Glicovia_prototipe.md` §2)

Opsi B (latih dari data alat nyata, jujur soal batas); model tidak menimpa `best_model.pkl` (pilih lewat `GLICO_MODEL_PATH`); firmware selalu kirim volt di `raw`; backend putuskan konversi lewat `units`; validasi per sesi; glukosa saliva tidak dipakai model (jenuh); label 88/148 dari nama file, sesi tanpa angka diasumsikan 148 (`label_source=assumed`); koefisien kalibrasi ada di dua tempat dan harus identik.

## Celah yang sudah diketahui (PRD harus menutup tiap baris ini)

| #   | Celah                                                                                                                                                                                                                                                                                                                                                                                             | Dampak ke tujuan akhir                                                     |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| G1  | **OLED belum ada di /home/hendra/projects/pkmGlico/hardware/kodeMasHaikal/main.cpp **: balasan prediksi hanya dicetak ke Serial. Layar hasil (kategori, angka, pH, PROTOTIPE) dan layar error belum ada.                                                                                                                                                                                         | Tujuan akhir "hasil muncul di OLED" belum tercapai                         |
| G2  | **`main.cpp` belum pernah dikompilasi/diuji di alat.** Ada 3–4 varian firmware dengan peta kanal ADS berbeda (`firmware/`, `firmware_offline/`, `firmware_prototipe/`, `kodeMasHaikal/`) dan berbeda dari catatan skematik.                                                                                                                                                      | Risiko data salah label kanal                                              |
| G3  | **Hardware**: VMID terukur 0,91 V (rancangan 1,65 V); kanal glukosa menempel ≈ 0 V / jenuh (≈ 7160 nA konstan); 97% baris data berstatus `JENUH`; kanal ke-3 memakai enzim glukosa, bukan fruktosamin (hanya 2 strip enzim tersisa).                                                                                                                                                    | Sinyal sampel nyata mungkin tidak terbaca; hasil bisa hanya cermin artefak |
| G4  | **Konversi terjadi saat inferensi, bukan saat penyimpanan**: DB dan website berisi volt di kolom `fructosamine`/`salivary_glucose`, `ph` kosong. `qualityFlag` selalu `valid` walau `quality.saturated=true`.                                                                                                                                                                   | Website menampilkan volt sebagai satuan riil                               |
| G5  | **Broker HiveMQ publik dipakai bersama**: satu pembacaan mendapat dua balasan (model dummy 176 mg/dL vs lokal 88). Data kesehatan lewat broker publik tanpa auth/TLS.                                                                                                                                                                                                                       | OLED/simulator bisa menampilkan angka salah; privasi                       |
| G6  | **Website**: badge PROTOTIPE, `model_version`, penanganan baris provisional belum ada. Kode `app/web` belum pernah diaudit di PRD.                                                                                                                                                                                                                                                      | Hasil bisa disalahartikan                                                  |
| G7  | **Deployment**: hanya `ml_pipeline` yang punya Dockerfile; backend dan web belum; compose hanya `db`. `requirements.txt` mengunci scikit-learn 1.7.0, `venv` memakai 1.9.0 → pickle model bisa tidak cocok dengan image. Railway sedang insiden (build ditunda, token API dicabut, "pre-deploy command" tersendat); kredensial Postgres Railway pernah ada di berkas terlacak git. | Tidak bisa deploy; kredensial dianggap bocor                               |
| G8  | **Data & model**: ~2 orang, 2 nilai label (88, 148), 9 sesi, label sebagian asumsi, tanpa glukometer terkontrol; kalibrasi pH lama tidak bisa di-fit; hanya 22 strip polos + 2 strip enzim tersisa (anggaran PRD §16).                                                                                                                                                                     | Model tidak bermakna secara ilmiah; klaim harus dibatasi                   |
| G9  | **Etika/regulasi**: uji pada manusia butuh informed consent / ethical clearance; data subjek hanya kode.                                                                                                                                                                                                                                                                                    | Syarat sebelum uji ke relawan                                              |
| G10 | Pertanyaan terbuka D1–D11 (kanal ke-3, satuan glukosa saliva, status puasa, peta kanal final, arus sampel, HTTPS vs MQTT, sensor suhu, broker, label `DIABETES_1`, tampilan website untuk baris volt).                                                                                                                                                                                         | Menentukan arsitektur akhir                                                |

## Sumber yang wajib dibaca (cari lokasi sendiri bila path berbeda)

- `hardware/PRD_Glicovia.md` (§5 temuan kritis, §14–17), `hardware/PRD_Glicovia_prototipe.md`
- Firmware: `hardware/kodeMasHaikal/main.cpp`, `hardware/firmware/firmware.ino`, `hardware/firmware_offline/`, `hardware/firmware_prototipe/` (perintah kalibrasi serial), `hardware/pHBisa/`
- Hardware: `hardware/kicad_tanpa_tp4056/` (skematik, `generate_schematic.py`, `verify_netlist.py`), `hardware/catatan/*` (Nernst, kalibrasi, analisis uji pH)
- Data: `hardware/data_log/`, `hardware/DATA/`, `ml_pipeline/data/real/`
- ML: `ml_pipeline/src/` (`api_connector.py`, `inference.py`, `train_real_svr.py`, `convert_data_log.py`, `preprocessing.py`, `train_svm.py`), `ml_pipeline/Dockerfile`, `requirements.txt`
- Backend: `app/backend/src/` (`mqtt/`, `modules/readings`, `modules/inference`, `modules/devices`, `modules/predictions`), `prisma/`, `docker-compose.yml`
- Web: `app/web/src/` (halaman `overview`, `readings`, `predictions`, `devices`, `operator`)
- `scripts/simulate_device.js`, `run_all.sh`, dokumen panduan simulasi end-to-end (berisi kredensial lama, **jangan dicetak**)

## Isi yang harus ada di PRD final

1. **Ringkasan, tujuan terukur, non-tujuan, persona, skenario pakai** (satu alur utama + alur gagal: strip kering, sampel kurang, jenuh, WiFi putus, backend/ML down, model belum siap).
2. **Arsitektur & batas tanggung jawab** per komponen: apa yang dilakukan alat, backend, ML, DB, website. Tentukan **satu** tempat konversi volt → satuan riil (saat penyimpanan atau inferensi), dan nasib data volt/raw.
3. **Kontrak data**: payload alat → backend, DB (skema + migrasi yang dibutuhkan, mis. tanda `provisional`, `cal_version`, `strip_type`, `fw_version`), respons ML, pesan balik ke alat. Aturan versi dan kompatibilitas mundur.
4. **Firmware**: mesin status pengukuran (siap → deteksi sampel → tunggu stabil → sampling → kirim → tunggu balasan → tampil), peta kanal ADS **tunggal** untuk semua firmware dan skematik, aturan tolak/tandai hasil (jenuh, CV, error I2C), konfigurasi tanpa rahasia di repo, mode kalibrasi.
5. **OLED**: spesifikasi tiap layar (ukur, tunggu stabil + hitung mundur, hasil, error, kalibrasi) dengan tata letak 128×64, teks persis, durasi tampil (hasil ditahan sampai pengukuran berikutnya), penanda PROTOTIPE, konfirmasi driver SH1106 vs SSD1306.
6. **Website**: halaman dan data yang ditampilkan, hubungan baris pembacaan ↔ prediksi, badge PROTOTIPE/`model_version`/`provisional`, perilaku untuk data jenuh/suspect, alur pairing perangkat ke akun.
7. **Data, kalibrasi, dan model**: prosedur kalibrasi pH/glukosa (tautkan §15 PRD induk, sesuaikan dengan anggaran strip §16), cara koefisien sampai ke firmware/backend tanpa dua salinan yang bisa berbeda, siklus latih ulang (versi data, versi model, versi sklearn), aturan label dan status puasa, validasi per subjek, kriteria "model layak dilaporkan", dan **batas klaim**.
8. **Deployment & operasi**: Dockerfile ketiga service, compose lokal (termasuk broker MQTT pilihan), jalur Railway setelah pulih (service per Dockerfile, Postgres Railway, migrasi, variabel lingkungan, jaringan internal, broker privat + TLS + auth), pengelolaan rahasia dan rotasi kredensial, log dan cara melihat kegagalan (satu pembacaan → satu prediksi).
9. **Keamanan, privasi, etika**: broker, token per perangkat, data subjek berkode, informed consent/ethical clearance, pernyataan "bukan alat diagnosis".
10. **Rencana pengujian**: matriks uji per lapisan (unit, integrasi, simulator, perangkat nyata, e2e ≤ 90 s) dengan kriteria lulus/gagal yang bisa dicek mesin. Sertakan uji "tepat satu balasan per pembacaan" dan uji kegagalan di G-list.
11. **Rencana kerja bertahap** (P0 wajib demo, P1, P2) dengan urutan dan ketergantungan; tahap pertama harus menutup G1–G5 supaya tujuan akhir tercapai dengan label jujur, tahap berikutnya memperbaiki hardware/kalibrasi/data.
12. **Register risiko**, **keputusan (K-xx) dan pertanyaan terbuka (D-xx)** lengkap dengan rekomendasi, serta **definisi selesai** per tahap.

## Format keluaran

- Bahasa Indonesia, istilah teknis dan nama berkas/kode apa adanya. Gaya ringkas: tabel untuk persyaratan, kalimat pendek.
- Setiap persyaratan: ID (mis. FW-OLED-03), prioritas P0/P1/P2, kriteria penerimaan yang dapat diuji, dan tautan ke celah (G-xx) atau tujuan yang dipenuhi.
- Simpan PRD final di `hardware/PRD_Glicovia_v2.md` setelah kerangkanya saya setujui. Jangan menimpa PRD yang ada.
- Di akhir, berikan **daftar tugas eksekusi berurutan** yang masing-masing cukup kecil untuk dikerjakan dan diuji sendiri (judul, berkas yang disentuh, cara verifikasi).

## Yang tidak boleh Anda lakukan

- Menulis atau mengubah kode, menjalankan perintah yang menulis ke DB/Docker/broker, atau mem-publish MQTT pada tahap PRD ini (hanya baca berkas dan jalankan perintah read-only).
- Menghubungi Railway atau layanan eksternal lain.
- Memperluas ruang lingkup (aplikasi mobile, multi-akun, pengisian baterai) tanpa persetujuan saya.

Mulai sekarang dengan langkah 1: baca sumber, lalu berikan ringkasan pemahaman dan daftar celah/kontradiksi.
