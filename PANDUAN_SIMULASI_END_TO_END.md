# Panduan Simulasi End-to-End GLICOVIA

Dokumen ini berisi panduan lengkap langkah demi langkah untuk menjalankan simulasi alur end-to-end: mulai dari **pengiriman data sensor oleh alat**, **ingesti & penyimpanan database**, **inferensi AI (SVR)**, hingga **hasil ditampilkan di Dashboard Web Vercel dan layar OLED alat**.

---

## 1. Arsitektur & Jalur Komunikasi Data

```text
[Alat ESP32 / Simulator] ────── 1. MQTT Publish (Data Sensor) ─────► [HiveMQ Cloud Broker]
         ▲                                                                   │
         │ 5. MQTT Subscribe (Hasil AI)                                      │ 2. Ingest
         │                                                                   ▼
[Layar OLED Tampil Hasil]                                            [Railway Backend Express]
                                                                             │
                                                                             ├─► 3. Simpan ke Postgres: sensor_readings
                                                                             │
                                                                             ├─► 4. HTTP POST /predict (Internal VPC)
                                                                             │         │
                                                                             │         ▼
                                                                             │   [Railway ML Service (SVR)]
                                                                             │         │
                                                                             │         ▼
                                                                             ├─◄ Hasil Prediksi (mg/dL + Kategori)
                                                                             │
                                                                             ├─► Simpan ke Postgres: prediction_results
                                                                             │
                                                                             └─► [Dashboard Web Vercel]
```

### Parameter Endpoint Produksi

- **Web Dashboard (Frontend)**: [https://pkm-glicovia-v8fo.vercel.app/](https://pkm-glicovia-v8fo.vercel.app/)
- **API Backend**: `https://backend-production-eac88.up.railway.app`
- **MQTT Broker**: `broker.hivemq.com` (Port: `1883`)
- **Topik Sensor (Kirim)**: `glicovia/devices/<device_code>/readings`
- **Topik Prediksi (Terima)**: `glicovia/devices/<device_code>/predictions`

---

## 2. Persiapan: Registrasi & Pairing Device

Sebelum data sensor diproses oleh AI dan dikaitkan ke pasien, alat (contoh: `GLICO-01`) harus terdaftar dan berstatus **paired** dengan akun pasien di database.

### Cara Cek / Daftarkan Device ke Akun Anda

Jalankan perintah berikut di terminal lokal untuk memastikan device `GLICO-01` terikat ke akun Anda:

```bash
cd /home/hendra/projects/pkmGlico/app/backend
node -e "
const { Client } = require('pg');
const crypto = require('crypto');

async function run() {
  const client = new Client({
    connectionString: 'postgresql://postgres:OODJCSRugoSLZphXWMInnvYLdMASdBuy@switchback.proxy.rlwy.net:51918/railway',
    ssl: false
  });
  await client.connect();

  // Ambil subject pertama (akun Anda)
  const subjRes = await client.query('SELECT id, display_name FROM subjects LIMIT 1');
  if (subjRes.rows.length === 0) {
    console.error('Belum ada akun subject! Silakan register di web terlebih dahulu.');
    process.exit(1);
  }
  const subjectId = subjRes.rows[0].id;

  // Insert atau pastikan device GLICO-01 ada
  await client.query(\`
    INSERT INTO devices (id, device_code, name, mqtt_topic, status, firmware_version, created_at, updated_at)
    VALUES (\$1, 'GLICO-01', 'Glicovia Biosensor 01', 'glicovia/devices/GLICO-01/readings', 'paired', 'v1.0.0', NOW(), NOW())
    ON CONFLICT (device_code) DO NOTHING
  \`, [crypto.randomUUID()]);

  const devRes = await client.query(\"SELECT id FROM devices WHERE device_code = 'GLICO-01'\");
  const actualDevId = devRes.rows[0].id;

  // Pastikan device ter-assign aktif ke subject
  await client.query(\`
    INSERT INTO device_assignments (id, device_id, subject_id, status, assigned_at, created_at)
    VALUES (\$1, \$2, \$3, 'active', NOW(), NOW())
    ON CONFLICT DO NOTHING
  \`, [crypto.randomUUID(), actualDevId, subjectId]);

  console.log('✅ Device GLICO-01 terhubung aktif dengan subjek:', subjRes.rows[0].display_name);
  await client.end();
}
run().catch(console.error);
"
```

---

## 3. Menjalankan Simulasi (Virtual Hardware Simulator)

Telah disediakan skrip simulasi hardware mandiri di `scripts/simulate_device.js` yang mensimulasikan kerja mikroprosesor ESP32 secara akurat:
1. Menghubungkan diri ke broker MQTT HiveMQ.
2. Melakukan *subscribe* ke topik prediksi alat (`glicovia/devices/GLICO-01/predictions`).
3. Mengirimkan payload pembacaan sensor ke topik ingesti (`glicovia/devices/GLICO-01/readings`).
4. Menangkap respon balik dari AI Cloud dan mencetak visualisasi layar OLED di terminal.

### Perintah Menjalankan Simulasi

Jalankan perintah berikut dari root project:

```bash
NODE_PATH=app/backend/node_modules node scripts/simulate_device.js
```

### Skenario Uji Klinis Berbeda

Anda bisa menambahkan parameter uji dengan flag `--ph`, `--fructo`, dan `--glucose`:

#### Skenario A: Kategori Normal (< 100 mg/dL)
```bash
NODE_PATH=app/backend/node_modules node scripts/simulate_device.js --ph 7.20 --fructo 180 --glucose 0.8
```
*Output yang diharapkan: Glukosa ~86 mg/dL, Status: **Normal**.*

#### Skenario B: Kategori Pre-Diabetes (100 - 125 mg/dL)
```bash
NODE_PATH=app/backend/node_modules node scripts/simulate_device.js --ph 7.00 --fructo 195 --glucose 1.4
```
*Output yang diharapkan: Glukosa ~110-120 mg/dL, Status: **Pre-Diabetes**.*

#### Skenario C: Kategori Diabetes (≥ 126 mg/dL)
```bash
NODE_PATH=app/backend/node_modules node scripts/simulate_device.js --ph 6.85 --fructo 215 --glucose 2.4
```
*Output yang diharapkan: Glukosa ~150-180 mg/dL, Status: **Diabetes**.*

---

## 4. Tampilan Hasil pada Masing-Masing Sisi

### A. Pada Terminal (Representasi Layar OLED Alat)
Ketika backend selesai melakukan inferensi, simulator langsung menerima payload balik dan menampilkan visualisasi layar OLED:

```text
====================================================
🎉 HASIL PREDIKSI AI DITERIMA DARI CLOUD!
====================================================

┌────────────────────────────────────────┐
│         GLICOVIA OLED DISPLAY          │
├────────────────────────────────────────┤
│  Glukosa Darah : 86.1   mg/dL          │
│  Status        : Normal                │
│  Tingkat Akurasi: 99%                  │
│                                        │
│  [ Hasil tersinkronisasi ke Web ]      │
└────────────────────────────────────────┘
```

### B. Pada Dashboard Web Vercel
1. Buka [https://pkm-glicovia-v8fo.vercel.app/](https://pkm-glicovia-v8fo.vercel.app/)
2. Login menggunakan akun Anda.
3. Masuk ke halaman **Readings** atau **Predictions**:
   - Angka estimasi glukosa darah terbaru langsung terupdate.
   - Grafik tren riwayat pembacaan otomatis menambahkan titik data baru.
   - Status badge kategori risiko (Normal / Pre-Diabetes / Diabetes) tertera lengkap beserta confidence score.

### C. Pada Database PostgreSQL (Verifikasi Data)
Untuk melihat data mentah yang tersimpan di PostgreSQL Railway:

```bash
cd /home/hendra/projects/pkmGlico/app/backend
node -e "
const { Client } = require('pg');
async function run() {
  const client = new Client({
    connectionString: 'postgresql://postgres:OODJCSRugoSLZphXWMInnvYLdMASdBuy@switchback.proxy.rlwy.net:51918/railway',
    ssl: false
  });
  await client.connect();
  const res = await client.query(\`
    SELECT 
      sr.recorded_at, sr.ph, sr.fructosamine, sr.salivary_glucose,
      pr.glucose_estimate, pr.clinical_category, pr.confidence_score, pr.inference_status
    FROM sensor_readings sr
    JOIN prediction_results pr ON pr.sensor_reading_id = sr.id
    ORDER BY sr.recorded_at DESC LIMIT 5
  \`);
  console.table(res.rows);
  await client.end();
}
run().catch(console.error);
"
```

---

## 5. Menjalankan Menggunakan Alat Fisik (ESP32)

Jika Anda ingin langsung mencoba pada hardware fisik:

1. Buka file `main.cpp` di **Arduino IDE** atau **VS Code (PlatformIO)**.
2. Pastikan library terinstall:
   - `Adafruit SH110X`
   - `Adafruit GFX Library`
   - `Adafruit ADS1X15`
   - `PubSubClient`
3. Sesuaikan konfigurasi WiFi pada baris 9-10:
   ```cpp
   const char* ssid     = "Nama_WiFi_Anda";
   const char* password = "Password_WiFi_Anda";
   ```
4. Hubungkan board ESP32 ke laptop dan klik **Upload**.
5. Buka Serial Monitor (`115200` baud):
   - ESP32 akan membaca sensor $\rightarrow$ mem-publish ke HiveMQ setiap 5 detik.
   - Ketika hasil AI diterima, ESP32 otomatis membunyikan/mengganti tampilan OLED ke menu **"HASIL PREDIKSI AI"**.

---

## 6. Ringkasan Format JSON Payload

### Topik Kirim: `glicovia/devices/<device_code>/readings`
```json
{
  "device_code": "GLICO-01",
  "ph": 6.85,
  "fructosamine": 215.50,
  "salivary_glucose": 2.45
}
```

### Topik Terima: `glicovia/devices/<device_code>/predictions`
```json
{
  "device_code": "GLICO-01",
  "glucose_estimate": 150.94,
  "clinical_category": "Diabetes",
  "confidence_score": 0.9938,
  "timestamp": "2026-10-15T07:58:57.000Z"
}
```
