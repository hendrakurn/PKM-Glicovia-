# Panduan Testing MQTT Hardware GLICOVIA

Dokumen ini menjelaskan apa yang perlu dilakukan oleh backend developer dan firmware/hardware developer untuk testing pengiriman data sensor dari device GLICOVIA ke backend melalui MQTT.

## Tujuan Testing

Tujuan testing ini:

```text
Hardware/device publish data sensor lewat MQTT
-> MQTT broker menerima message
-> backend lokal subscribe ke broker yang sama
-> backend resolve device
-> backend simpan data ke sensor_readings
-> data bisa dicek lewat API readings
```

Backend tidak harus dideploy cloud untuk testing MQTT. Yang penting adalah backend dan hardware sama-sama connect ke MQTT broker yang sama.

## Konsep Singkat

MQTT punya 3 komponen utama:

- Publisher: hardware/device GLICOVIA.
- Broker: server MQTT, misalnya HiveMQ, EMQX, Mosquitto.
- Subscriber: backend GLICOVIA.

Flow-nya:

```text
Device
-> publish ke topic MQTT
-> broker MQTT
-> backend subscribe topic
-> backend simpan ke database
```

Device tidak mengirim data sensor ke HTTP API backend. Device mengirim data ke MQTT broker.

## Kesepakatan Konfigurasi

Untuk testing awal, sepakati nilai berikut:

```text
MQTT broker host : broker.hivemq.com
MQTT broker port : 1883
MQTT topic prefix: glicovia
Device code      : GLICO-01
MQTT topic       : glicovia/devices/GLICO-01/readings
```

Payload JSON yang dikirim device:

```json
{
  "device_code": "GLICO-01",
  "ph": 7.12,
  "fructosamine": 285.4,
  "salivary_glucose": 9.8
}
```

Payload dengan timestamp device:

```json
{
  "device_code": "GLICO-01",
  "recorded_at": "2026-07-19T10:00:00Z",
  "ph": 7.12,
  "fructosamine": 285.4,
  "salivary_glucose": 9.8
}
```

Jika `recorded_at` tidak dikirim, backend akan memakai waktu saat message diterima.

## Yang Harus Dilakukan Backend Developer

### 1. Siapkan MQTT Broker

Untuk testing awal, bisa pakai broker publik:

```text
broker.hivemq.com:1883
```

Untuk testing yang lebih rapi, gunakan broker dengan username/password, misalnya HiveMQ Cloud atau EMQX Cloud.

### 2. Set Environment Backend

Isi `.env` backend:

```env
MQTT_URL=mqtt://broker.hivemq.com:1883
MQTT_TOPIC_PREFIX=glicovia
```

Jika pakai broker dengan auth:

```env
MQTT_URL=mqtts://<broker-host>:8883
MQTT_USERNAME=<username>
MQTT_PASSWORD=<password>
MQTT_TOPIC_PREFIX=glicovia
```

Backend akan subscribe ke:

```text
glicovia/#
```

Artinya backend menerima semua message di bawah topic `glicovia`.

### 3. Jalankan Database dan Migration

Pastikan PostgreSQL aktif, lalu jalankan:

```bash
npm run migrate
```

### 4. Jalankan Backend

```bash
npm run dev
```

Cek log backend. Jika MQTT aktif, backend akan subscribe ke topic:

```text
glicovia/#
```

Jika `MQTT_URL` kosong, backend akan menampilkan info bahwa MQTT disabled.

### 5. Register/Login User untuk Mendapatkan Token

Register:

```http
POST /api/auth/register
Content-Type: application/json
```

Body:

```json
{
  "email": "subject@example.com",
  "password": "StrongPass123!",
  "fullName": "Subject One"
}
```

Simpan `accessToken` dari response.

### 6. Daftarkan Device ke Backend

Device harus terdaftar dulu agar message MQTT tidak diabaikan.

```http
POST /api/devices
Authorization: Bearer <accessToken>
Content-Type: application/json
```

Body:

```json
{
  "deviceCode": "GLICO-01",
  "name": "Prototype Device 1",
  "mqttTopic": "glicovia/devices/GLICO-01/readings",
  "status": "unpaired",
  "firmwareVersion": "0.1.0"
}
```

Simpan `id` device dari response. ID ini dibutuhkan jika ingin pairing.

### 7. Test Publish Manual dari Laptop Backend

Sebelum hardware mengirim data, test jalur MQTT secara manual.

```bash
mosquitto_pub \
  -h broker.hivemq.com \
  -p 1883 \
  -t 'glicovia/devices/GLICO-01/readings' \
  -m '{"device_code":"GLICO-01","ph":7.12,"fructosamine":285.4,"salivary_glucose":9.8}'
```

Jika berhasil, backend log akan menunjukkan message seperti:

```text
MQTT reading stored
```

Jika device belum paired, data tetap bisa masuk ke database, tetapi `subject_id` akan `null`.

### 8. Pairing Device ke Subject

Agar data MQTT muncul di API readings milik user, device harus dipairing ke subject.

Generate token pairing:

```http
POST /api/pairing/tokens
Authorization: Bearer <accessToken>
Content-Type: application/json
```

Body:

```json
{
  "deviceId": "<device-id-dari-create-device>",
  "expiresInMinutes": 15
}
```

Ambil `pairingToken.token` dari response, lalu scan token:

```http
POST /api/pairing/scan
Authorization: Bearer <accessToken>
Content-Type: application/json
```

Body:

```json
{
  "token": "<pairing-token>"
}
```

Setelah pairing sukses:

```text
Device GLICO-01 -> subject user login
```

Message MQTT berikutnya dari `GLICO-01` akan tersimpan dengan `subject_id` user tersebut.

### 9. Cek Data Masuk Lewat API

Cek reading terbaru:

```http
GET /api/readings/me/readings/latest
Authorization: Bearer <accessToken>
```

Cek semua readings:

```http
GET /api/readings/me/readings
Authorization: Bearer <accessToken>
```

Cek trend:

```http
GET /api/readings/me/readings/trends?bucket=hour&limit=24
Authorization: Bearer <accessToken>
```

## Yang Harus Dilakukan Firmware/Hardware Developer

### 1. Pakai Konfigurasi MQTT yang Sama

Konfigurasi firmware:

```env
MQTT_HOST=broker.hivemq.com
MQTT_PORT=1883
MQTT_TOPIC=glicovia/devices/GLICO-01/readings
DEVICE_CODE=GLICO-01
```

Jika broker memakai auth:

```env
MQTT_HOST=<broker-host>
MQTT_PORT=8883
MQTT_USERNAME=<username>
MQTT_PASSWORD=<password>
MQTT_TOPIC=glicovia/devices/GLICO-01/readings
DEVICE_CODE=GLICO-01
```

### 2. Connect ke MQTT Broker

Firmware harus connect ke broker yang sama dengan backend.

Untuk testing publik:

```text
broker.hivemq.com:1883
```

Untuk broker TLS/auth:

```text
<broker-host>:8883
```

### 3. Publish ke Topic yang Disepakati

Topic wajib sama dengan yang didaftarkan di backend:

```text
glicovia/devices/GLICO-01/readings
```

### 4. Kirim Payload JSON

Payload minimal:

```json
{
  "device_code": "GLICO-01",
  "ph": 7.12,
  "fructosamine": 285.4,
  "salivary_glucose": 9.8
}
```

Payload lengkap dengan timestamp:

```json
{
  "device_code": "GLICO-01",
  "recorded_at": "2026-07-19T10:00:00Z",
  "ph": 7.12,
  "fructosamine": 285.4,
  "salivary_glucose": 9.8
}
```

Field yang dibaca backend:

- `device_code` atau `deviceCode`
- `recorded_at`, `recordedAt`, `timestamp`, `time`, atau `received_at`
- `ph`
- `fructosamine`
- `salivary_glucose` atau `salivaryGlucose`

### 5. Publish Berkala atau Saat Pembacaan Selesai

Untuk testing, firmware bisa publish setiap beberapa detik:

```text
setiap 5 detik / 10 detik
```

Untuk flow real, publish saat sensor selesai melakukan pembacaan.

## Checklist Bersama

Pastikan nilai ini sama di backend, database, dan firmware:

```text
MQTT broker      : broker.hivemq.com
MQTT port        : 1883
MQTT prefix      : glicovia
Device code      : GLICO-01
MQTT topic       : glicovia/devices/GLICO-01/readings
Payload field    : device_code = GLICO-01
```

Di backend `.env`:

```env
MQTT_URL=mqtt://broker.hivemq.com:1883
MQTT_TOPIC_PREFIX=glicovia
```

Di database backend, device harus terdaftar sebagai:

```json
{
  "deviceCode": "GLICO-01",
  "mqttTopic": "glicovia/devices/GLICO-01/readings"
}
```

Di firmware:

```env
MQTT_TOPIC=glicovia/devices/GLICO-01/readings
DEVICE_CODE=GLICO-01
```

## Urutan Testing yang Direkomendasikan

1. Backend developer set `.env` MQTT.
2. Backend developer jalankan database dan migration.
3. Backend developer jalankan backend.
4. Backend developer register/login user.
5. Backend developer daftarkan device `GLICO-01`.
6. Backend developer test `mosquitto_pub` manual.
7. Jika manual publish berhasil, firmware developer connect device ke broker.
8. Firmware developer publish payload JSON ke topic yang sama.
9. Backend developer cek log `MQTT reading stored`.
10. Backend developer pairing device ke subject jika ingin cek data lewat API user.
11. Backend developer cek `/api/readings/me/readings/latest`.

## Troubleshooting

### Backend tidak menerima message

Cek:

- `MQTT_URL` sudah diisi.
- Backend sudah restart setelah `.env` diubah.
- Firmware publish ke broker yang sama.
- Topic firmware berada di bawah prefix backend, misalnya `glicovia/...`.
- Broker/port bisa diakses dari laptop backend.

### Backend menerima message tapi mengabaikan device

Kemungkinan device belum terdaftar di database.

Pastikan sudah create device:

```json
{
  "deviceCode": "GLICO-01",
  "mqttTopic": "glicovia/devices/GLICO-01/readings"
}
```

### Data masuk database tapi tidak muncul di API readings user

Kemungkinan device belum paired ke subject.

Solusi:

1. Generate pairing token.
2. Scan pairing token dengan user yang sama.
3. Publish ulang data MQTT.
4. Cek `/api/readings/me/readings/latest`.

### Payload tersimpan sebagai incomplete

Kemungkinan payload kosong, bukan JSON valid, atau tidak punya measurement.

Payload harus JSON valid dan punya minimal salah satu field:

- `ph`
- `fructosamine`
- `salivary_glucose`
- `salivaryGlucose`

### Topic benar tapi device tetap tidak terdeteksi

Pastikan `device_code` di payload juga dikirim:

```json
{
  "device_code": "GLICO-01"
}
```

Ini membantu backend resolve device selain dari topic.

## Catatan Keamanan

Broker publik seperti `broker.hivemq.com` cocok untuk testing cepat, tetapi tidak cocok untuk data sensitif atau production.

Untuk demo yang lebih aman, gunakan broker dengan:

- username/password
- TLS port `8883`
- ACL topic per device

Untuk production, jangan kirim data kesehatan lewat broker publik tanpa auth dan TLS.
