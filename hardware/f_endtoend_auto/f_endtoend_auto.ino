// ============================================================
//  Glicovia - Firmware end-to-end (mode ukur + OLED + WiFi/MQTT)
//  ESP32 + ADS1115 (0x48) + OLED SH1106 1,3" (0x3C) + TIA Rf 100k
//  Kanal ADS: A0 = fruktosa, A1 = glukosa, A2 = pH, A3 = VMID
//  Varian AUTO dari f_endtoend.ino: mode siaga. Setelah daya masuk alat mengulang
//  baseline -> tunggu lonjakan arus sendiri; lonjakan = mulai hitung & kirim. Tanpa lonjakan
//  tidak ada yang direkam/dikirim. Ketik 'm' / tekan BOOT tetap bisa (manual, juga memotong jeda hasil).
//  Mulai ukur: ketik 'm' + Enter (Serial) ATAU tekan tombol BOOT.
//  Payload ke cloud SUDAH satuan riil (pH, mg/dL, umol/L) memakai kalibrasi SEMENTARA;
//  volt mentah ikut dikirim di "raw". Prediksi dari cloud tampil di OLED.
//  Library: adafruit/Adafruit ADS1X15, Adafruit GFX Library, Adafruit SH110X, PubSubClient`1
// ============================================================
#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_ADS1X15.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
#include <esp_system.h>
#include "secrets.h"

// ================= KONFIGURASI =================
#define USE_A3_VMID 1        // 1 = VMID sudah dijumper ke A3 (diferensial A1-A3)
                             // 0 = belum dijumper, pakai VMID_NOMINAL
#define I2C_SDA   21
#define I2C_SCL   22
#define ADS_ADDR  0x48
#define OLED_ADDR 0x3C
#define BTN_PIN   0          // tombol BOOT = mulai ukur

// Pemetaan kanal ADS1115
#define CH_FRU    0          // A0 fruktosa
#define CH_GLU    1          // A1 glukosa
#define CH_PH     2          // A2 pH
#define CH_VMID   3          // A3 VMID

const float    RF            = 100e3;  // ohm, resistor feedback TIA
const float    VMID_NOMINAL  = 1.65;   // isi hasil ukur multimeter jika USE_A3_VMID = 0
const float    TRIG_NA       = 5.0;    // ambang deteksi sampel masuk (n A)
const uint32_t DELAY_MS      = 10000;   // tunggu setelah trigger (lewati arus charging)
const int      N_SAMPLES     = 40;
const float    LOD_NA        = 1.0;    // di bawah ini dianggap "tidak ada arus"
#define AUTO_START 1                           // 1 = mode siaga otomatis, 0 = hanya manual
const uint32_t AUTO_BOOT_MS  = 4000;           // stabilkan TIA/potensiostat setelah daya masuk
const uint32_t HOLD_MS       = 60000;          // layar hasil ditahan sebelum siaga lagi (BOOT = lewati)

// Cloud (topik sama dengan firmware/firmware.ino)
#define DEVICE_CODE "GLICO-01"
#define FW_VERSION  "0.5.0-auto"
const char*    TOPIC_READ    = "glicovia/devices/" DEVICE_CODE "/readings";
const char*    TOPIC_PRED    = "glicovia/devices/" DEVICE_CODE "/predictions";
const uint32_t PRED_WAIT_MS  = 12000;
// ===============================================

// Harus di atas fungsi pertama: Arduino IDE menaruh prototype otomatis di sana.
struct Reading {
  bool    ok;
  int16_t raw;    // raw yang dipakai untuk hitung arus glukosa
  float   vFru;   // tegangan fruktosa (A0, single-ended)
  float   vOut;   // tegangan output TIA glukosa (A1, single-ended)
  float   vPh;    // tegangan pH (A2, single-ended)
  float   vMid;   // VMID (A3 atau nominal)
  float   iNA;    // arus sensor glukosa (nA)
  bool    sat;    // output jenuh / ADC mentok
};

// >>> CALC  (tanpa API Arduino selain snprintf/strstr; diuji di PC, jangan diubah sembarangan)
// Kalibrasi SEMENTARA, BUKAN hasil fit buffer/larutan standar. Harus sama dengan CAL di
// ml_pipeline/src/convert_data_log.py dan PROVISIONAL_CAL di
// app/backend/src/modules/inference/inference.service.ts (model dilatih dari fitur ini).
//   pH          : V = PH_M * pH + PH_C
//   glukosa     : I(nA) = GLU_A * mg/dL + GLU_B       (kanal jenuh, tidak informatif)
//   fruktosamin : I(nA) = FRU_A * umol/L + FRU_B,  I = (VMID - Vfru) / RF
// Hasil dipotong ke rentang model (pH 4-9, glukosa 0,1-10, fruktosamin 150-500).
#define CAL_VERSION "provisional-2026-10-22"
const float PH_M  = -0.05916f, PH_C  = 0.3226f;
const float GLU_A = 1000.0f,   GLU_B = 0.0f;
const float FRU_A = 35.0f,     FRU_B = -4000.0f;

static float clampf(float v, float lo, float hi, bool* clipped) {
  if (v < lo) { *clipped = true; return lo; }
  if (v > hi) { *clipped = true; return hi; }
  return v;
}
static float phFromV(float v, bool* c)    { return clampf((v - PH_C) / PH_M, 4.0f, 9.0f, c); }
static float gluFromI(float iNA, bool* c) { return clampf((iNA - GLU_B) / GLU_A, 0.1f, 10.0f, c); }
static float fruFromV(float vMid, float vFru, bool* c) {
  float iNA = (vMid - vFru) / RF * 1e9f;
  return clampf((iNA - FRU_B) / FRU_A, 150.0f, 500.0f, c);
}

// Angka untuk JSON; "null" bila NaN/Inf supaya JSON tetap valid.
static const char* num(char* b, size_t sz, float v, int dec) {
  if (!isfinite(v)) snprintf(b, sz, "null");
  else              snprintf(b, sz, "%.*f", dec, v);
  return b;
}

// Satu ringkasan pengukuran: ph/fructosamine/salivary_glucose = satuan riil, "raw" = volt mentah.
static int buildPayload(char* out, size_t sz, float ph, float fru, float glu,
                        float vPh, float vFru, float vGlu, float vMid, float iNA, float cv,
                        int n, int nSat, bool clipped) {
  char sPh[16], sFru[16], sGlu[16], sVph[16], sVfru[16], sVglu[16], sMid[16], sI[16], sCv[16];
  return snprintf(out, sz,
    "{\"device_code\":\"%s\",\"ph\":%s,\"fructosamine\":%s,\"salivary_glucose\":%s,"
    "\"units\":{\"ph\":\"pH\",\"fructosamine\":\"umol/L\",\"salivary_glucose\":\"mg/dL\"},"
    "\"raw\":{\"v_ph\":%s,\"v_fru\":%s,\"v_glu\":%s,\"v_mid\":%s,\"i_glu_nA\":%s},"
    "\"quality\":{\"n\":%d,\"n_sat\":%d,\"saturated\":%s,\"cv_pct\":%s,\"clipped\":%s},"
    "\"fw_version\":\"%s\",\"cal_version\":\"%s\"}",
    DEVICE_CODE,
    num(sPh, sizeof sPh, ph, 2), num(sFru, sizeof sFru, fru, 2), num(sGlu, sizeof sGlu, glu, 2),
    num(sVph, sizeof sVph, vPh, 4), num(sVfru, sizeof sVfru, vFru, 4), num(sVglu, sizeof sVglu, vGlu, 4),
    num(sMid, sizeof sMid, vMid, 4), num(sI, sizeof sI, iNA, 2),
    n, nSat, nSat > n / 2 ? "true" : "false", num(sCv, sizeof sCv, cv, 2), clipped ? "true" : "false",
    FW_VERSION, CAL_VERSION);
}

// Ambil nilai dari JSON datar balasan cloud, tanpa library JSON. false bila kunci tidak ada.
static bool jsonNum(const char* js, const char* key, float* out) {
  char pat[40]; snprintf(pat, sizeof pat, "\"%s\":", key);
  const char* p = strstr(js, pat);
  if (!p) return false;
  *out = (float)atof(p + strlen(pat));
  return true;
}
static bool jsonStr(const char* js, const char* key, char* out, size_t sz) {
  char pat[40]; snprintf(pat, sizeof pat, "\"%s\":\"", key);
  const char* p = strstr(js, pat);
  if (!p) return false;
  p += strlen(pat);
  size_t i = 0;
  while (*p && *p != '"' && i + 1 < sz) out[i++] = *p++;
  out[i] = 0;
  return true;
}
// <<< CALC

Adafruit_ADS1115 ads;
Adafruit_SH1106G oled(128, 64, &Wire, -1);
WiFiClient wifi;
PubSubClient mqtt(wifi);
uint32_t i2cErrCount = 0;
bool oledOk = false;
bool predGot = false;
float predEst = 0, predConf = 0;
char  predCat[24] = "";

// ---------------- OLED ----------------
// Layar teks: judul + sampai 4 baris (21 karakter per baris pada ukuran 1).
void oledLines(const char* l1, const char* l2 = "", const char* l3 = "", const char* l4 = "") {
  if (!oledOk) return;
  oled.clearDisplay();
  oled.setTextSize(1);
  oled.setTextColor(SH110X_WHITE);
  oled.setCursor(0, 12);  oled.print("GLICOVIA  PROTOTIPE");
  oled.drawLine(0, 22, 127, 22, SH110X_WHITE);
  const char* l[4] = {l1, l2, l3, l4};
  for (int i = 0; i < 4; i++) { oled.setCursor(0, 28 + i * 12); oled.print(l[i]); }
  oled.display();
}

// Layar hasil; ditahan sampai pengukuran berikutnya (loop() tidak menggambar ulang).
void oledResult(bool saturated, float ph, float fru) {
  if (!oledOk) return;
  char b[24];
  oled.clearDisplay();
  oled.setTextColor(SH110X_WHITE);
  oled.setTextSize(1);
  oled.setCursor(0, 12);  oled.print("Klasifikasi glukosa");
  oled.setTextSize(2);
  oled.setCursor(0, 23);
  if (predGot) { oled.print(strcmp(predCat, "Pre-Diabetes") == 0 ? "Prediabet" : predCat); }
  else         { oled.setTextSize(1); oled.setCursor(0, 27); oled.print("belum ada prediksi"); }
  oled.setTextSize(1);
  oled.setCursor(0, 43);

  oled.setCursor(0, 54);

  oled.setCursor( 0, 66);
  oled.print(saturated ? "PROTOTIPE  " : "PROTOTIPE (sementara)");
  oled.display();
}

// ---------------- sensor ----------------
bool i2cOk() {
  Wire.beginTransmission(ADS_ADDR);
  return Wire.endTransmission() == 0;
}

  Reading readOnce() {
  Reading r = {false, 0, 0, 0, 0, 0, 0, false};
  if (!i2cOk()) { i2cErrCount++; return r; }

  ads.setGain(GAIN_ONE);                       // +/-4.096 V
  r.vFru = ads.computeVolts(ads.readADC_SingleEnded(CH_FRU));
  int16_t rawGlu = ads.readADC_SingleEnded(CH_GLU);
  r.vOut = ads.computeVolts(rawGlu);
  r.vPh  = ads.computeVolts(ads.readADC_SingleEnded(CH_PH));

#if USE_A3_VMID
  r.vMid = ads.computeVolts(ads.readADC_SingleEnded(CH_VMID));
  ads.setGain(GAIN_FOUR);                      // +/-1.024 V, 1 LSB ~ 0.31 nA
  r.raw = ads.readADC_Differential_1_3();      // A1 - A3
  float vDiff = ads.computeVolts(r.raw);
  r.sat = (abs(r.raw) > 32000);
#else
  r.vMid = VMID_NOMINAL;
  r.raw  = rawGlu;
  float vDiff = r.vOut - r.vMid;
#endif

  r.sat = r.sat || (r.vOut < 0.05f) || (r.vOut > 3.25f);
  r.iNA = -vDiff / RF * 1e9f;                  // Vout = VMID - I*Rf
  r.ok  = true;
  return r;
}

const char* label(const Reading& r) {
  if (!r.ok)                 return "I2C GAGAL -> cek SDA/SCL/VDD ADS1115";
  if (r.sat)                 return "JENUH -> arus > rentang / short / lonjakan awal";
  if (fabs(r.iNA) < LOD_NA)  return "ARUS ~0 -> kontak strip putus / belum ada sampel";
  return "OK";
}

void sortf(float* a, int n) {
  for (int i = 1; i < n; i++) {
    float k = a[i]; int j = i - 1;
    while (j >= 0 && a[j] > k) { a[j + 1] = a[j]; j--; }
    a[j + 1] = k;
  }
}

// ---------------- jaringan ----------------
void onMsg(char*, byte* p, unsigned int len) {
  static char buf[512];
  unsigned int n = len < sizeof buf - 1 ? len : sizeof buf - 1;
  memcpy(buf, p, n);
  buf[n] = 0;
  Serial.print("Balasan cloud: ");
  Serial.println(buf);
  if (predGot) return;                          // pakai balasan pertama saja
  if (jsonNum(buf, "glucose_estimate", &predEst) && jsonStr(buf, "clinical_category", predCat, sizeof predCat)) {
    if (!jsonNum(buf, "confidence_score", &predConf)) predConf = 0;
    predGot = true;
  }
}

bool netUp() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  uint32_t t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 15000) delay(250);
  if (WiFi.status() != WL_CONNECTED) return false;
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(1024);                    // default 256 B, JSON lebih panjang
  mqtt.setCallback(onMsg);
  t0 = millis();
  while (!mqtt.connected() && millis() - t0 < 10000) {
    if (!mqtt.connect(DEVICE_CODE "-fw")) delay(500);
  }
  if (!mqtt.connected()) return false;
  mqtt.subscribe(TOPIC_PRED);
  return true;
}

void netDown() {
  mqtt.disconnect();
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);                         // radio mati lagi supaya ADC tidak terganggu
}

// Kirim satu ringkasan pengukuran, tunggu prediksi, tampilkan di OLED.
void sendReading(float vPh, float vFru, float vGlu, float vMid, float iNA, float cv,
                 int n, int nSat, float ph, float fru, float glu, bool clipped) {
  static char json[768];
  int len = buildPayload(json, sizeof json, ph, fru, glu, vPh, vFru, vGlu, vMid, iNA, cv, n, nSat, clipped);
  Serial.println(json);
  if (len < 0 || len >= (int)sizeof json) {
    Serial.println("GAGAL: payload terpotong, tidak dikirim.");
    oledLines("ERROR", "Payload terlalu", "panjang");
    return;
  }

  predGot = false;
  oledLines("Mengirim ke cloud...", "(WiFi + MQTT)");
  if (!netUp()) {
    netDown();
    Serial.println("GAGAL: WiFi/MQTT tidak tersambung, data tidak terkirim.");
    oledLines("ERROR", "WiFi/MQTT putus", "data tidak terkirim");
    return;
  }
  Serial.println(mqtt.publish(TOPIC_READ, json) ? "Publish OK" : "Publish GAGAL");
  oledLines("Terkirim.", "Menunggu prediksi...");
  uint32_t t0 = millis();
  while (!predGot && millis() - t0 < PRED_WAIT_MS) { mqtt.loop(); delay(20); }
  if (!predGot) Serial.println("Belum ada prediksi (cek website).");
  netDown();
  oledResult(nSat > n / 2, ph, fru);
}

// ---------------- mode ukur ----------------
void oledSiaga() {
  oledLines("Siaga", "Strip kering terpasang", "Teteskan sampel");
}

// quiet = mode siaga: tidak menggambar baseline/menunggu, "tidak ada trigger" tanpa layar error.
// Return true bila ada layar hasil/error yang perlu dibaca (ditahan HOLD_MS), false bila tidak ada trigger.
bool measure(bool quiet = false) {
  Serial.println(quiet ? "\n[siaga] baseline..." : "\n===== MODE UKUR: teteskan sampel dalam 30 detik =====");
  if (!quiet) oledLines("Mengukur baseline...", "Jangan teteskan dulu");

  // 1. Baseline tanpa sampel
  float base = 0; int nb = 0;
  for (int i = 0; i < 10; i++) {
    Reading r = readOnce();
    if (r.ok) { base += r.iNA; nb++; }
    delay(30);
  }
  if (nb == 0) {
    Serial.println("GAGAL: ADS1115 tidak merespons (cek SDA/SCL/VDD)");
    oledLines("ERROR", "ADS1115 tidak", "merespons");
    return true;
  }
  base /= nb;
  Serial.printf("Baseline: %.2f nA\n", base);

  // 2. Tunggu trigger (perubahan arus saat sampel masuk)
  if (!quiet) oledLines("Teteskan sampel", "(maks 30 detik)");
  uint32_t t0 = millis(); bool trig = false;
  while (millis() - t0 < 30000) {
    Reading r = readOnce();
    if (r.ok && fabs(r.iNA - base) > TRIG_NA) { trig = true; break; }
    delay(20);
  }
  if (!trig) {
    Serial.println("TIDAK ADA TRIGGER: arus tidak berubah.");
    if (quiet) return false;                   // siaga: ulang diam-diam, tidak ada yang dikirim
    Serial.println(" -> cek kontak konektor strip, sampel menutupi 3 elektroda, bias WE-RE (VSET).");
    oledLines("TIDAK ADA TRIGGER", "Cek kontak strip &", "sampel 3 elektroda");
    return true;
  }
  Serial.printf("Sampel terdeteksi. Tunggu %lu ms...\n", DELAY_MS);
  for (uint32_t left = DELAY_MS / 1000; left > 0; left--) {   // OLED hanya diperbarui saat tidak sampling
    char b[22]; snprintf(b, sizeof b, "Tunggu stabil %us", (unsigned)left);
    oledLines("Sampel terdeteksi", b);
    delay(1000);
  }

  // 3. Ambil sampel di jendela waktu tetap
  oledLines("Mengambil sampel", "Jangan disentuh");
  float buf[N_SAMPLES]; int n = 0, nSat = 0, nFail = 0;
  float sumFru = 0, sumPh = 0, sumGlu = 0, sumMid = 0;
  while (n < N_SAMPLES && nFail < 20) {
    Reading r = readOnce();
    if (!r.ok) { nFail++; continue; }
    if (r.sat) nSat++;
    sumFru += r.vFru;
    sumPh  += r.vPh;
    sumGlu += r.vOut;
    sumMid += r.vMid;
    buf[n++] = r.iNA;
  }
  if (n < 10) {
    Serial.println("GAGAL: terlalu banyak error I2C saat sampling.");
    oledLines("ERROR", "Terlalu banyak", "error I2C");
    return true;
  }

  // 4. Statistik
  float mean = 0;
  for (int i = 0; i < n; i++) mean += buf[i];
  mean /= n;
  float sd = 0;
  for (int i = 0; i < n; i++) sd += (buf[i] - mean) * (buf[i] - mean);
  sd = sqrtf(sd / (n - 1));

  sortf(buf, n);
  int lo = n / 4, hi = n - n / 4;              // trimmed mean (50% tengah)
  float tmean = 0;
  for (int i = lo; i < hi; i++) tmean += buf[i];
  tmean /= (hi - lo);
  float cv = (fabs(tmean) > 1e-6f) ? sd / fabs(tmean) * 100.0f : 0;

  // 5. Volt -> satuan riil (kalibrasi SEMENTARA)
  bool clipped = false;
  float ph  = phFromV(sumPh / n, &clipped);
  float fru = fruFromV(sumMid / n, sumFru / n, &clipped);
  float glu = gluFromI(tmean, &clipped);

  Serial.println("----- HASIL -----");
  Serial.printf("N=%d  jenuh=%d  gagal_I2C=%d\n", n, nSat, nFail);
  Serial.printf("I min/median/max : %.2f / %.2f / %.2f nA\n", buf[0], buf[n / 2], buf[n - 1]);
  Serial.printf("I trimmed mean   : %.2f nA (delta baseline %.2f nA)\n", tmean, tmean - base);
  Serial.printf("SD = %.2f nA   CV = %.1f %%\n", sd, cv);
  Serial.printf("Fruktosa (A0) rata-rata: %.4f V   pH (A2) rata-rata: %.4f V\n", sumFru / n, sumPh / n);
  Serial.printf("Terkonversi (SEMENTARA): pH=%.2f  glukosa=%.2f mg/dL  fruktosamin=%.1f umol/L%s\n",
                ph, glu, fru, clipped ? "  [ada nilai dipotong ke batas model]" : "");
  if (fabs(tmean) < LOD_NA) Serial.println("Glukosa: < batas deteksi (arus ~0)");

  if (nSat > 0)  Serial.println("PERINGATAN: ada sampel jenuh -> naikkan DELAY_MS atau turunkan gain/Rf.");
  if (cv > 10)   Serial.println("PERINGATAN: CV > 10% -> noise tinggi (cek Cf, kabel, WiFi, daya).");
  Serial.println("=================\n");

  // Siaga: lonjakan awal bisa saja pasang strip, bukan sampel. Arus akhir ~baseline/~0 = tidak kirim.
  //if (quiet && (fabs(tmean) < LOD_NA || fabs(tmean - base) < TRIG_NA)) {
  //  Serial.println("DIBATALKAN: arus akhir tidak beda dari baseline (bukan sampel?), tidak dikirim.");
  //  oledLines("Tidak ada sampel", "Data tidak dikirim", "Ulangi dgn strip", "kering + sampel");
  //  return true;
  //}

  sendReading(sumPh / n, sumFru / n, sumGlu / n, sumMid / n, tmean, cv, n, nSat, ph, fru, glu, clipped);
  return true;
}

void setup() {
  Serial.begin(115200);
  delay(500);
  WiFi.mode(WIFI_OFF);                         // matikan radio selama diagnostik
  pinMode(BTN_PIN, INPUT_PULLUP);

  esp_reset_reason_t rr = esp_reset_reason();
  Serial.printf("\nReset reason: %d %s\n", rr,
                rr == ESP_RST_BROWNOUT ? "(BROWNOUT! cek MT3608 / baterai)" : "");

  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(100000);

  delay(250);
  oledOk = oled.begin(OLED_ADDR, true);
  if (!oledOk) Serial.println("OLED SH1106 TIDAK DITEMUKAN di 0x3C (lanjut tanpa layar). Cek kabel / ganti driver SSD1306.");
  oledLines("Sistem Glicovia", "Memulai...");

  if (!ads.begin(ADS_ADDR, &Wire)) {
    Serial.println("ADS1115 TIDAK DITEMUKAN di 0x48. Cek kabel I2C & ADDR=GND.");
    oledLines("ERROR", "ADS1115 tidak", "ditemukan di 0x48");
  } else {
    Serial.println("ADS1115 OK");
    oledLines("Siap.", AUTO_START ? "Mode siaga otomatis" : "Tekan BOOT atau", AUTO_START ? "BOOT/m = manual" : "ketik m untuk ukur");
  }
  ads.setDataRate(RATE_ADS1115_32SPS);

  Serial.println("Kanal: A0=fruktosa  A1=glukosa  A2=pH  A3=VMID");
  Serial.printf("Mode: %s\n", USE_A3_VMID ? "diferensial A1-A3" : "single-ended A1 vs VMID_NOMINAL");
  Serial.println("Ketik 'm' + Enter atau tekan BOOT untuk mode ukur.\n");
#if AUTO_START
  delay(AUTO_BOOT_MS);
  oledSiaga();
#endif
}

uint32_t holdUntil = 0;                         // selama sekarang < holdUntil: layar hasil ditahan, siaga jeda

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'm' || c == 'M') { if (measure()) holdUntil = millis() + HOLD_MS; }
    while (Serial.available()) Serial.read();
  }
  if (digitalRead(BTN_PIN) == LOW) {            // BOOT ditekan (debounce 50 ms)
    delay(50);
    if (digitalRead(BTN_PIN) == LOW) {
      bool holding = (int32_t)(holdUntil - millis()) > 0;
      if (holding) { holdUntil = 0; oledSiaga(); }   // BOOT saat layar hasil = siaga lagi sekarang
      else if (measure()) holdUntil = millis() + HOLD_MS;
      while (digitalRead(BTN_PIN) == LOW) delay(10);
    }
  }

#if AUTO_START
  if ((int32_t)(holdUntil - millis()) <= 0) {
    bool wasHolding = holdUntil != 0;
    if (wasHolding) { holdUntil = 0; oledSiaga(); }    // jeda hasil habis
    if (measure(true)) holdUntil = millis() + HOLD_MS;
    return;                                            // measure sudah memakan waktu; lewati cetak diagnostik
  }
#endif

  Reading r = readOnce();
  Serial.printf("raw=%6d  Vfru=%.4f V  Vglu=%.4f V  VpH=%.4f V  Vmid=%.4f V  I=%8.2f nA  errI2C=%lu  | %s\n",
                r.raw, r.vFru, r.vOut, r.vPh, r.vMid, r.iNA, i2cErrCount, label(r));
  delay(250);
}
