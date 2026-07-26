# Hermes Execution Guide For GLICOVIA Backend

Panduan ini menjelaskan bagaimana Hermes harus mengeksekusi backend di:

`~/projects/pkmGlico/app/backend`

dengan mengacu pada master prompt di:

`~/projects/pkmGlico/app/web/diagrams/hermes-backend-master-prompt.md`

dan schema DBML di:

`~/projects/pkmGlico/app/web/diagrams/glicovia-user-pairing-fixed.dbml`

## Prinsip Kerja

- Hermes memegang tanggung jawab penuh atas hasil akhir.
- Codex boleh dipanggil untuk subtask coding yang konkret.
- Hermes tidak boleh berhenti di planning atau scaffold setengah jadi.
- Hasil akhir harus runnable, modular, dan sesuai DBML.
- Backend harus langsung siap untuk integrasi hardware via MQTT walaupun AI inference belum aktif.

## Arsitektur Yang Harus Dijaga

Backend harus dibangun sebagai service terpisah dari frontend:

- Frontend: `~/projects/pkmGlico/app/web`
- Backend: `~/projects/pkmGlico/app/backend`

Stack backend:
- Express
- TypeScript
- PostgreSQL
- MQTT
- JWT auth

Tujuan fitur:
- user/subject dapat register dan login
- hardware menampilkan QR pairing token
- subject scan QR saat login
- backend membuat assignment device ke subject
- hardware publish data via MQTT
- backend simpan `sensor_readings`
- frontend membaca data subject dari API backend

## Makna Domain Yang Wajib Dipertahankan

- `users` = akun login
- `subjects` = pemilik data kesehatan
- `devices` = hardware
- `pairing_tokens` = token QR sekali pakai
- `device_assignments` = relasi aktif device ke subject
- `sensor_readings` = data mentah dari MQTT
- `model_versions` = metadata model AI
- `prediction_results` = hasil inferensi model

Sensor yang dipakai:
- `ph`
- `fructosamine`
- `salivary_glucose`

Jangan gunakan `temperature`.

## Strategi Eksekusi Yang Disarankan

### Fase 1. Baca sumber kebenaran

Hermes harus membaca dulu:
- DBML schema
- master prompt

Hermes tidak boleh menebak schema sendiri bila sudah ada DBML.

### Fase 2. Scaffold backend dasar

Hermes membuat project backend TypeScript + Express yang modular, termasuk:
- `package.json`
- `tsconfig.json`
- `src/app.ts`
- `src/server.ts`
- env loader
- db pool
- middleware global
- folder modules
- folder mqtt

### Fase 3. Implement database

Hermes harus menerjemahkan DBML menjadi migration/schema PostgreSQL nyata.

Minimal harus ada:
- tabel
- foreign key
- unique constraint
- index yang relevan

Index penting:
- `users.email`
- `devices.device_code`
- `devices.mqtt_topic`
- `pairing_tokens.token`
- active assignment lookup
- subject readings by date
- device readings by date

### Fase 4. Implement auth

Minimal endpoint:
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

Register harus:
- membuat `users`
- membuat `subjects`

Auth harus:
- hash password
- issue JWT
- protect route via Bearer token

### Fase 5. Implement device management

Minimal endpoint:
- `POST /api/devices`
- `GET /api/devices`
- `GET /api/devices/:deviceId`
- `PATCH /api/devices/:deviceId`

Device harus punya status dan data identitas yang sesuai diagram.

### Fase 6. Implement pairing flow

Minimal endpoint:
- `POST /api/devices/:deviceId/pairing-token`
- `POST /api/pairing/scan`
- `POST /api/devices/:deviceId/unpair`

Aturan pairing:
- token unik
- token expired
- token one-time-use
- token pending lama untuk device yang sama harus di-revoke saat token baru dibuat
- scan token membuat `device_assignments`
- token ditandai `used`
- device status diupdate

### Fase 7. Implement MQTT ingestion

Hermes harus membuat subscriber MQTT yang membaca topic device dan menyimpan readings.

Kontrak default yang direkomendasikan:

Topic:
- `glicovia/devices/GLICO-01/readings`

Payload:

```json
{
  "device_code": "GLICO-01",
  "recorded_at": "2026-07-16T10:15:00Z",
  "ph": 7.12,
  "fructosamine": 285.4,
  "salivary_glucose": 9.8
}
```

Strategi resolusi device:
- topic dulu
- kalau perlu fallback ke payload

Saat message diterima:
- cari device
- cari assignment aktif
- isi `subject_id` kalau ada
- isi `device_assignment_id` kalau ada
- simpan `raw_payload`
- simpan `received_at`
- simpan `quality_flag`

Kalau device diketahui tetapi belum ada assignment aktif, reading tetap boleh disimpan dengan `subject_id` null. Ini harus didokumentasikan.

### Fase 8. Implement read API untuk frontend

Minimal endpoint:
- `GET /api/me/devices`
- `GET /api/me/readings`
- `GET /api/me/readings/latest`
- `GET /api/me/readings/trends`

Semua endpoint ini harus subject-scoped:
- hanya mengembalikan data milik subject yang sedang login

### Fase 9. Siapkan model dan prediction layer

Minimal endpoint:
- `GET /api/models`
- `POST /api/models`
- `GET /api/predictions`

Catatan penting:
- jangan memalsukan AI inference
- cukup siapkan schema, akses data, dan route supaya siap integrasi ke depan

### Fase 10. Dokumentasi dan verifikasi

Hermes wajib membuat:
- `.env.example`
- `README.md`

README minimal harus menjelaskan:
- setup
- env
- migration
- cara run dev
- cara register/login
- cara generate pairing token
- cara scan pairing
- contoh curl
- contoh publish MQTT

## Aturan Delegasi Ke Codex

Hermes boleh mendelegasikan subtask coding ke Codex, tetapi tidak boleh menyerahkan seluruh proyek mentah-mentah.

Subtask yang cocok untuk Codex:
- bootstrap backend TypeScript + Express
- generate migration SQL dari DBML
- implement module auth
- implement module devices
- implement module pairing
- implement MQTT client dan handler
- implement subject-scoped reading APIs
- implement model/prediction read layer
- draft `.env.example` dan README

Hermes tetap harus:
- memeriksa konsistensi nama file dan route
- memastikan semua route termount
- memastikan env vars konsisten
- memastikan arsitektur tetap modular
- memastikan hasil akhir benar-benar runnable

## Checklist Selesai

Hermes tidak boleh menyatakan pekerjaan selesai bila belum memenuhi semua poin ini.

### Scaffold
- backend project ada di `~/projects/pkmGlico/app/backend`
- TypeScript config ada
- package scripts ada
- struktur modular ada

### Database
- migration/schema ada
- schema mengikuti DBML
- foreign key dan index ada

### Auth
- register ada
- login ada
- me ada
- JWT protection ada

### Devices
- create/list/detail/update ada

### Pairing
- generate pairing token ada
- revoke token lama ada
- consume token sekali pakai ada
- assignment dibuat
- unpair ada

### MQTT
- config broker ada
- subscriber ada
- topic/payload contract terdokumentasi
- sensor reading insert flow ada

### Read APIs
- my devices ada
- my readings ada
- latest reading ada
- trends ada

### Predictions readiness
- models route ada
- predictions route ada
- schema siap untuk AI integration

### Quality
- modular
- tidak monolitik
- validation ada
- error middleware ada
- password hash tidak pernah direturn

### Docs
- `.env.example` ada
- README ada
- sample curl ada
- sample MQTT publish ada

## Instruksi Penutup

Hermes harus fokus pada hasil akhir yang bisa dipakai langsung untuk:
- backend modular
- database PostgreSQL siap
- hardware publish ke MQTT
- subject login dan pair device
- frontend consume API

Jika ada bagian yang memang belum bisa final, Hermes harus menyebutkannya secara eksplisit sebagai gap, bukan diam-diam meninggalkannya.
