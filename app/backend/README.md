# PKMGlico Backend

Backend service untuk GLICOVIA / PKM saliva glucose monitoring.

Stack:
- Express
- TypeScript
- PostgreSQL
- MQTT
- JWT auth

## Fitur yang sudah dibuat

- Health check service.
- Auth user: register, login, dan me.
- Subject profile otomatis dibuat saat register.
- Device management: create, list, detail, update, delete.
- QR pairing token flow untuk menghubungkan device ke subject.
- Device assignment: menyimpan relasi device aktif dengan subject.
- MQTT ingestion untuk menyimpan sensor reading dari hardware.
- API reading milik subject: device aktif, daftar reading, latest reading, dan trend.
- Metadata model AI/SVM.
- Read API untuk prediction result.

## Struktur folder

- `src/app.ts` - wiring Express routes dan middleware.
- `src/server.ts` - bootstrap HTTP server dan MQTT client.
- `src/config/` - environment config dan logger.
- `src/db/` - PostgreSQL pool dan migration SQL.
- `src/middleware/` - auth, error handler, request id, not found.
- `src/modules/auth/` - register, login, JWT profile.
- `src/modules/devices/` - CRUD device.
- `src/modules/pairing/` - generate QR token, scan token, unpair device.
- `src/modules/readings/` - read API untuk subject dan helper simpan MQTT reading.
- `src/modules/models/` - metadata versi model.
- `src/modules/predictions/` - query hasil prediksi.
- `src/mqtt/` - MQTT subscriber, parser topic, handler payload sensor.
- `src/lib/` - helper error, transaction, JWT.
- `src/utils/` - helper ID, crypto, date.

## Konsep flow aplikasi

Flow utama backend ini:

```text
subject register/login
-> device didaftarkan ke backend
-> backend generate QR pairing token untuk device
-> subject scan QR
-> backend membuat active device assignment
-> device publish data sensor lewat MQTT
-> backend resolve device dan subject
-> backend simpan sensor_readings
-> subject membaca readings/latest/trends
-> prediction_results dapat dibaca jika proses AI sudah mengisi tabel prediksi
```

Catatan role:
- Database sudah menyiapkan role `subject` dan `admin`.
- Register publik saat ini selalu membuat user role `subject`.
- Endpoint device dan pairing token secara konsep cocok untuk admin/operator, tetapi kode saat ini belum membatasi route tersebut khusus admin.

## Scripts

- `npm run dev` - jalankan server dalam watch mode.
- `npm run build` - compile TypeScript ke `dist/`.
- `npm start` - jalankan hasil build dari `dist/server.js`.
- `npm run migrate` - jalankan semua SQL migration via `psql`.

## Environment

Copy `.env.example` menjadi `.env`, lalu sesuaikan nilai berikut:

- `NODE_ENV` - default `development`.
- `PORT` - default `3000`.
- `HOST` - default `0.0.0.0`.
- `DATABASE_URL` - connection string PostgreSQL.
- `JWT_SECRET` - secret untuk signing token.
- `JWT_EXPIRES_IN` - durasi token JWT, default `7d`.
- `LOG_LEVEL` - default `info`.
- `MQTT_URL` - broker URL, contoh `mqtt://localhost:1883`. Jika kosong, MQTT client tidak dijalankan.
- `MQTT_CLIENT_ID` - client id MQTT. Jika kosong, dibuat otomatis.
- `MQTT_USERNAME` - username MQTT jika broker memerlukan auth.
- `MQTT_PASSWORD` - password MQTT jika broker memerlukan auth.
- `MQTT_TOPIC_PREFIX` - prefix topic, default `glicovia`.

## Migration

```bash
npm run migrate
```

Catatan:
- Script ini memakai `psql`, jadi PostgreSQL client harus tersedia.
- Semua file SQL di `src/db/migrations/` akan dieksekusi berurutan.

## Menjalankan server

Development:

```bash
npm run dev
```

Production-like:

```bash
npm run build
npm start
```

Base URL lokal default:

```text
http://localhost:3000
```

Untuk endpoint yang butuh login, pakai header:

```text
Authorization: Bearer <accessToken>
```

## Ringkasan API

| Method | Endpoint | Auth | Fungsi |
| --- | --- | --- | --- |
| GET | `/health` | Tidak | Cek service hidup. |
| POST | `/api/auth/register` | Tidak | Register user subject baru. |
| POST | `/api/auth/login` | Tidak | Login dan ambil JWT. |
| GET | `/api/auth/me` | Ya | Ambil profil user dan subject. |
| GET | `/api/devices` | Ya | List semua device. |
| POST | `/api/devices` | Ya | Daftarkan device baru. |
| GET | `/api/devices/:deviceId` | Ya | Detail device. |
| PATCH | `/api/devices/:deviceId` | Ya | Update device. |
| DELETE | `/api/devices/:deviceId` | Ya | Hapus device. |
| POST | `/api/pairing/tokens` | Ya | Generate token QR pairing. |
| POST | `/api/pairing/scan` | Ya, subject | Scan token dan pairing device. |
| POST | `/api/pairing/unpair` | Ya, subject | Unpair device dari subject. |
| GET | `/api/readings/me/devices` | Ya | Device aktif milik subject. |
| GET | `/api/readings/me/readings` | Ya | List sensor reading subject. |
| GET | `/api/readings/me/readings/latest` | Ya | Reading terbaru. |
| GET | `/api/readings/me/readings/trends` | Ya | Agregasi trend per jam/hari. |
| GET | `/api/models` | Tidak | List metadata model. |
| POST | `/api/models` | Tidak | Tambah metadata model. |
| GET | `/api/predictions` | Tidak | List hasil prediksi. |

## API Detail

### GET /health

Mengecek apakah backend hidup.

Input: tidak ada.

Contoh response:

```json
{
  "status": "ok",
  "timestamp": "2026-07-16T10:15:00.000Z"
}
```

### POST /api/auth/register

Membuat akun user dan subject profile. Password disimpan sebagai hash, bukan plaintext.

Body:

```json
{
  "email": "subject@example.com",
  "password": "StrongPass123!",
  "fullName": "Subject One"
}
```

Validasi:
- `email` wajib valid email.
- `password` minimal 8 karakter.
- `fullName` optional, maksimal 120 karakter.

Contoh response:

```json
{
  "user": {
    "id": "8c6d0c16-2ef5-4d2f-b5a7-3d588e6d0f36",
    "email": "subject@example.com",
    "full_name": "Subject One",
    "role": "subject",
    "is_active": true,
    "last_login_at": null,
    "created_at": "2026-07-16T10:15:00.000Z",
    "updated_at": "2026-07-16T10:15:00.000Z"
  },
  "subject": {
    "id": "d63820cb-0c53-43d9-bbcb-3522335d0d5f",
    "user_id": "8c6d0c16-2ef5-4d2f-b5a7-3d588e6d0f36",
    "subject_code": "SUB-8C6D0C162EF54D2FB5A73D588E6D0F36",
    "display_name": "Subject One",
    "age": null,
    "sex": null,
    "notes": null,
    "created_at": "2026-07-16T10:15:00.000Z",
    "updated_at": "2026-07-16T10:15:00.000Z"
  },
  "accessToken": "<jwt-token>",
  "tokenType": "Bearer"
}
```

Error umum:
- `409 Email already registered`
- `400` jika body tidak valid.

### POST /api/auth/login

Login user dan mendapatkan JWT token.

Body:

```json
{
  "email": "subject@example.com",
  "password": "StrongPass123!"
}
```

Contoh response: sama seperti register, tetapi `last_login_at` terisi waktu login terbaru.

Error umum:
- `401 Invalid email or password`
- `404 User profile not found`

### GET /api/auth/me

Mengambil profil user dan subject dari JWT.

Header:

```text
Authorization: Bearer <accessToken>
```

Contoh response: object `user` dan `subject`, tanpa `accessToken`.

### GET /api/devices

Mengambil semua device, termasuk active assignment jika ada.

Header auth wajib. Secara produk endpoint ini cocok untuk admin/operator, tetapi kode saat ini belum mengecek role admin.

Contoh response:

```json
{
  "data": [
    {
      "id": "4f21d6de-9fb1-4d2c-b3d7-9d1a261f3291",
      "device_code": "GLICO-01",
      "name": "Prototype Device 1",
      "mqtt_topic": "glicovia/devices/GLICO-01/readings",
      "status": "paired",
      "firmware_version": "0.1.0",
      "last_seen_at": "2026-07-16T10:30:00.000Z",
      "created_at": "2026-07-16T10:10:00.000Z",
      "updated_at": "2026-07-16T10:25:00.000Z",
      "active_assignment": {
        "id": "a9e904e5-c18e-4210-b8fc-26f865d592ab",
        "subject_id": "d63820cb-0c53-43d9-bbcb-3522335d0d5f",
        "assigned_at": "2026-07-16T10:25:00.000Z",
        "subject_code": "SUB-8C6D0C162EF54D2FB5A73D588E6D0F36",
        "subject_name": "Subject One"
      }
    }
  ]
}
```

### POST /api/devices

Mendaftarkan device fisik ke backend.

Body:

```json
{
  "deviceCode": "GLICO-01",
  "name": "Prototype Device 1",
  "mqttTopic": "glicovia/devices/GLICO-01/readings",
  "status": "unpaired",
  "firmwareVersion": "0.1.0",
  "lastSeenAt": null
}
```

Validasi:
- `deviceCode` wajib string non-empty.
- `mqttTopic` wajib string non-empty.
- `name` optional string atau `null`.
- `status` optional, salah satu: `unpaired`, `paired`, `offline`, `online`, `inactive`.
- `firmwareVersion` optional string atau `null`.
- `lastSeenAt` optional ISO date string atau `null`.

Contoh response:

```json
{
  "data": {
    "id": "4f21d6de-9fb1-4d2c-b3d7-9d1a261f3291",
    "device_code": "GLICO-01",
    "name": "Prototype Device 1",
    "mqtt_topic": "glicovia/devices/GLICO-01/readings",
    "status": "unpaired",
    "firmware_version": "0.1.0",
    "last_seen_at": null,
    "created_at": "2026-07-16T10:10:00.000Z",
    "updated_at": "2026-07-16T10:10:00.000Z",
    "active_assignment": null
  }
}
```

Error umum:
- `409 A device with the same unique field already exists`
- `400` jika body tidak valid.

### GET /api/devices/:deviceId

Mengambil detail satu device.

Path parameter:
- `deviceId` - UUID device.

Response sukses: sama seperti object `data` pada create/list device.

Error umum:
- `404 Device not found`

### PATCH /api/devices/:deviceId

Mengubah sebagian field device.

Body contoh:

```json
{
  "name": "Prototype Device 1 - Lab A",
  "status": "online",
  "firmwareVersion": "0.1.1",
  "lastSeenAt": "2026-07-16T10:30:00.000Z"
}
```

Field yang bisa diupdate:
- `deviceCode`
- `name`
- `mqttTopic`
- `status`
- `firmwareVersion`
- `lastSeenAt`

Minimal satu field harus dikirim.

### DELETE /api/devices/:deviceId

Menghapus device.

Response sukses:

```text
204 No Content
```

Error umum:
- `404 Device not found`
- `409 Device has dependent records and cannot be removed` jika device sudah punya relasi data lain.

### POST /api/pairing/tokens

Membuat token QR sementara untuk satu device. Token bersifat one-time-use dan punya expiry.

Body:

```json
{
  "deviceId": "4f21d6de-9fb1-4d2c-b3d7-9d1a261f3291",
  "expiresInMinutes": 15
}
```

Validasi:
- `deviceId` wajib string non-empty.
- `expiresInMinutes` optional positive integer, default `15`.

Contoh response:

```json
{
  "data": {
    "device": {
      "id": "4f21d6de-9fb1-4d2c-b3d7-9d1a261f3291",
      "device_code": "GLICO-01",
      "status": "unpaired"
    },
    "pairingToken": {
      "id": "0cf29c65-f422-4398-a797-d8ba96245c1e",
      "device_id": "4f21d6de-9fb1-4d2c-b3d7-9d1a261f3291",
      "token": "b84fd3c0b7a7b702d36b5eb53a87a9349c5d0dbb6c8fdd4bf4cf6308e54aa1aa",
      "qr_payload": "{...json payload for QR...}",
      "status": "pending",
      "expires_at": "2026-07-16T10:25:00.000Z",
      "used_at": null,
      "revoked_at": null,
      "created_at": "2026-07-16T10:10:00.000Z"
    }
  }
}
```

Detail penting:
- Saat token baru dibuat, token pending lama untuk device yang sama otomatis direvoke.
- `qr_payload` adalah string JSON yang bisa dijadikan QR.
- QR ini tidak permanen. Setelah token dipakai atau expired, perlu generate token baru.
- User tidak perlu scan QR terus-menerus; scan hanya membuat relasi awal di `device_assignments`.

### POST /api/pairing/scan

Dipakai oleh subject/user untuk menghubungkan akunnya ke device.

Body:

```json
{
  "token": "b84fd3c0b7a7b702d36b5eb53a87a9349c5d0dbb6c8fdd4bf4cf6308e54aa1aa"
}
```

Validasi logic:
- Token harus ada.
- Token belum expired.
- Token status harus `pending`.
- Device belum punya active assignment.
- Subject belum punya active device assignment.

Contoh response ringkas:

```json
{
  "data": {
    "device": {
      "id": "4f21d6de-9fb1-4d2c-b3d7-9d1a261f3291",
      "device_code": "GLICO-01",
      "status": "paired",
      "active_assignment": {
        "id": "a9e904e5-c18e-4210-b8fc-26f865d592ab",
        "subject_id": "d63820cb-0c53-43d9-bbcb-3522335d0d5f"
      }
    },
    "assignment": {
      "id": "a9e904e5-c18e-4210-b8fc-26f865d592ab",
      "device_id": "4f21d6de-9fb1-4d2c-b3d7-9d1a261f3291",
      "subject_id": "d63820cb-0c53-43d9-bbcb-3522335d0d5f",
      "status": "active"
    }
  }
}
```

Catatan: response `pairingToken` pada kode saat ini berisi data token sebelum update `used_at`, sedangkan assignment dan device sudah dibuat. Di database token sudah diubah menjadi `used`.

Error umum:
- `404 Pairing token not found`
- `410 Pairing token has expired`
- `409 Pairing token has already been used`
- `409 Pairing token was revoked`
- `409 Device already has an active assignment`
- `409 Subject already has an active device assignment`

### POST /api/pairing/unpair

Mengakhiri active assignment antara subject dan device.

Body:

```json
{
  "deviceId": "4f21d6de-9fb1-4d2c-b3d7-9d1a261f3291"
}
```

Contoh response ringkas: `{ "data": { "device": ..., "assignment": ... } }`.

Catatan: response `assignment` pada kode saat ini adalah data assignment sebelum update `ended`, tetapi di database assignment sudah diubah ke `ended` dan `unassigned_at` sudah diisi.

### GET /api/readings/me/devices

Mengambil device aktif yang sedang paired ke subject.

Contoh response: `{ "data": { "subject": ..., "devices": [...] } }`.

### GET /api/readings/me/readings

Mengambil daftar sensor reading milik subject.

Query optional:
- `device_id` - filter device.
- `from` - filter `recorded_at >= from`.
- `to` - filter `recorded_at <= to`.
- `limit` - default `100`.
- `offset` - default `0`.

Contoh response:

```json
{
  "data": {
    "subject": {
      "id": "d63820cb-0c53-43d9-bbcb-3522335d0d5f",
      "display_name": "Subject One"
    },
    "readings": [
      {
        "id": "51a4f4c5-95d9-40d4-85b0-977e2d48c64e",
        "device_id": "4f21d6de-9fb1-4d2c-b3d7-9d1a261f3291",
        "subject_id": "d63820cb-0c53-43d9-bbcb-3522335d0d5f",
        "device_assignment_id": "a9e904e5-c18e-4210-b8fc-26f865d592ab",
        "recorded_at": "2026-07-16T10:30:00.000Z",
        "received_at": "2026-07-16T10:30:03.000Z",
        "ph": "7.120",
        "fructosamine": "285.400",
        "salivary_glucose": "9.800",
        "raw_payload": {
          "device_code": "GLICO-01",
          "recorded_at": "2026-07-16T10:30:00.000Z",
          "ph": 7.12,
          "fructosamine": 285.4,
          "salivary_glucose": 9.8
        },
        "quality_flag": "valid",
        "created_at": "2026-07-16T10:30:03.000Z"
      }
    ]
  }
}
```

### GET /api/readings/me/readings/latest

Mengambil reading terbaru milik subject.

Query optional:
- `device_id` - filter device.

Response sukses: `{ "data": { "subject": ..., "reading": ... } }`.

Jika tidak ada reading, response `404`:

```json
{
  "message": "No readings found"
}
```

### GET /api/readings/me/readings/trends

Mengambil agregasi trend reading per jam atau per hari.

Query optional:
- `device_id` - filter device.
- `from` - filter `recorded_at >= from`.
- `to` - filter `recorded_at <= to`.
- `bucket` - `hour` atau `day`, default `hour`.
- `limit` - default `48`.

Contoh response:

```json
{
  "data": {
    "subject": {
      "id": "d63820cb-0c53-43d9-bbcb-3522335d0d5f",
      "display_name": "Subject One"
    },
    "trends": [
      {
        "bucket_start": "2026-07-16T10:00:00.000Z",
        "reading_count": "3",
        "ph_avg": "7.1100000000000000",
        "fructosamine_avg": "284.9000000000000000",
        "salivary_glucose_avg": "9.7333333333333333"
      }
    ]
  }
}
```

### GET /api/models

List metadata versi model AI/SVM. Endpoint ini belum memakai auth middleware.

Contoh response: `{ "data": { "models": [...] } }`.

### POST /api/models

Tambah metadata versi model AI/SVM.

Body:

```json
{
  "model_name": "saliva-glucose-svm",
  "version": "0.1.0",
  "status": "deployed",
  "artifact_url": "s3://models/saliva-glucose-svm/0.1.0.pkl",
  "trained_at": "2026-07-16T09:00:00.000Z",
  "deployed_at": "2026-07-16T10:00:00.000Z",
  "notes": "Initial deployed model"
}
```

Validasi:
- `model_name` wajib string.
- `version` wajib string.
- `status` hanya menerima `deployed` atau `archived`; selain itu akan dianggap `training`.
- Field lain optional string atau `null`.

Contoh response: `{ "data": { "model": ... } }`.

### GET /api/predictions

List hasil prediksi. Endpoint ini belum memakai auth middleware. Fungsi service untuk membuat prediction result sudah ada, tetapi belum diekspos sebagai route HTTP.

Query optional:
- `sensor_reading_id` - filter hasil prediksi untuk satu reading.
- `model_version_id` - filter hasil prediksi dari satu model version.
- `limit` - default `100`.
- `offset` - default `0`.

Contoh response:

```json
{
  "data": {
    "predictions": [
      {
        "id": "efb4f40e-1292-495a-bd7d-765cb8772953",
        "sensor_reading_id": "51a4f4c5-95d9-40d4-85b0-977e2d48c64e",
        "model_version_id": "4a42bdfb-678c-4500-b285-a07d076b2038",
        "glucose_estimate": "105.300",
        "clinical_category": "normal",
        "confidence_score": "0.9234",
        "inference_status": "success",
        "predicted_at": "2026-07-16T10:31:00.000Z",
        "created_at": "2026-07-16T10:31:00.000Z",
        "sensor_recorded_at": "2026-07-16T10:30:00.000Z",
        "model_name": "saliva-glucose-svm",
        "model_version": "0.1.0"
      }
    ]
  }
}
```

## MQTT Ingestion

MQTT dipakai agar hardware device bisa publish data sensor tanpa memanggil HTTP API. Backend subscribe ke topic:

```text
<MQTT_TOPIC_PREFIX>/#
```

Jika `MQTT_TOPIC_PREFIX=glicovia`, backend subscribe ke:

```text
glicovia/#
```

Rekomendasi topic per device:

```text
glicovia/devices/GLICO-01/readings
```

Contoh payload:

```json
{
  "device_code": "GLICO-01",
  "recorded_at": "2026-07-16T10:15:00Z",
  "ph": 7.12,
  "fructosamine": 285.4,
  "salivary_glucose": 9.8
}
```

Backend akan mencoba resolve device dari:
- topic MQTT lengkap.
- device code yang ada di topic.
- `device_id` di payload.
- `device_code` di payload.
- `deviceId` di payload.
- `deviceCode` di payload.
- `mqtt_topic` di payload.

Jika device ketemu:
- backend mencari active assignment untuk device tersebut.
- reading disimpan ke `sensor_readings`.
- jika device sedang paired, `subject_id` dan `device_assignment_id` ikut disimpan.
- jika device belum paired, reading tetap bisa disimpan dengan `subject_id = null`.

Quality flag:
- `valid` jika payload bisa diparse dan punya minimal satu measurement.
- `incomplete` jika payload kosong, malformed JSON, atau tidak ada measurement.

Contoh publish pakai `mosquitto_pub`:

```bash
mosquitto_pub \
  -h localhost \
  -t 'glicovia/devices/GLICO-01/readings' \
  -m '{"device_code":"GLICO-01","recorded_at":"2026-07-16T10:15:00Z","ph":7.12,"fructosamine":285.4,"salivary_glucose":9.8}'
```

## Database schema

Schema PostgreSQL ada di:

- `src/db/migrations/0001_glicovia_user_pairing.sql`

Tabel utama:
- `users` - akun login.
- `subjects` - profil subject/pemilik data.
- `devices` - hardware GLICOVIA yang terdaftar.
- `pairing_tokens` - token QR sementara untuk pairing.
- `device_assignments` - relasi aktif/ended antara device dan subject.
- `sensor_readings` - data sensor dari MQTT.
- `model_versions` - metadata versi model AI/SVM.
- `prediction_results` - hasil prediksi dari satu sensor reading dan satu model version.

Enum utama:
- `user_role`: `subject`, `admin`.
- `device_status`: `unpaired`, `paired`, `offline`, `online`, `inactive`.
- `assignment_status`: `active`, `ended`.
- `pairing_status`: `pending`, `used`, `expired`, `revoked`.
- `quality_flag`: `valid`, `suspect`, `incomplete`.
- `inference_status`: `pending`, `success`, `failed`.
- `model_status`: `training`, `deployed`, `archived`.

## Catatan implementasi

- Password tidak pernah direturn ke response.
- JWT diverifikasi lewat middleware `authMiddleware`.
- `requireSubjectMiddleware` memastikan route tertentu hanya bisa diakses identity subject.
- Pairing token bersifat one-time-use dan memiliki expiry.
- User tidak perlu scan QR terus-menerus. Scan hanya untuk membuat active assignment awal.
- MQTT topic menjadi jalur/channel data sensor dan membantu backend mengenali device.
- Identitas permanen device sebaiknya `device_code`, misalnya `GLICO-01`.
- QR pairing sebaiknya tidak permanen; yang permanen ditempel di device adalah `device_code` atau serial number.
- MQTT ingestion bisa menyimpan reading meski device belum memiliki assignment aktif.
- Prediksi AI otomatis belum diimplementasikan; yang tersedia baru metadata model dan query hasil prediksi.
- Endpoint `models` dan `predictions` belum dilindungi auth pada kode saat ini.


```
docker start mosquitto-test
```
```
mosquitto_sub -h localhost -t 'glicovia/#' -v
```
```
mosquitto_pub -h localhost -t 'glicovia/devices/GLICO-01/readings' \
  -m '{"device_code":"GLICO-01","recorded_at":"2026-07-23T09:00:00Z","ph":7.12,"fructosamine":285.4,"salivary_glucose":9.8}'
```
```
export ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJmNzQxYTI1Zi1mNTNiLTQ3ZDYtYmY4Mi03YmJkZjkwOWE4YmYiLCJlbWFpbCI6ImhlbmRyYWt1cm5pYW1hbGlxaUBtYWlsLnVnbS5hYy5pZCIsInJvbGUiOiJzdWJqZWN0IiwiaWF0IjoxNzg0NzkxNDYyLCJleHAiOjE3ODQ4Nzc4NjJ9.llgpCDj7IBwArgM5w49UHbWASw6pF7p0AwXti75O8kw"
```
```
echo "$ACCESS_TOKEN"
```
```
curl http://localhost:5000/api/readings/me/readings/latest \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

```
cd ml_pipeline
source venv/bin/activate
uvicorn src.api_connector:app --host 0.0.0.0 --port 8001 --reload
```