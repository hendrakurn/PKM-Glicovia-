// ============================================================
//  Glicovia - Firmware DIAGNOSTIK kanal glukosa
//  ESP32 + ADS1115 (0x48) + TIA Rf 100k
//  Kanal ADS: A0 = fruktosa, A1 = glukosa, A2 = pH, A3 = VMID
//  Serial 115200. Ketik 'm' + Enter untuk mode ukur.
//  Tanpa input -> monitor kontinu tiap 250 ms.
//  Library: adafruit/Adafruit ADS1X15
// ============================================================
#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_ADS1X15.h>
#include <esp_system.h>
#include "secrets.h"

// ================= KONFIGURASI =================
#define USE_A3_VMID 1        // 1 = VMID sudah dijumper ke A3 (diferensial A1-A3)
                             // 0 = belum dijumper, pakai VMID_NOMINAL
#define I2C_SDA   21
#define I2C_SCL   22
#define ADS_ADDR  0x48

// Pemetaan kanal ADS1115
#define CH_FRU    0          // A0 fruktosa
#define CH_GLU    1          // A1 glukosa
#define CH_PH     2          // A2 pH
#define CH_VMID   3          // A3 VMID

const float    RF            = 100e3;  // ohm, resistor feedback TIA
const float    VMID_NOMINAL  = 1.65;   // isi hasil ukur multimeter jika USE_A3_VMID = 0
const float    TRIG_NA       = 5.0;    // ambang deteksi sampel masuk (nA)
const uint32_t DELAY_MS      = 60000;   // tunggu setelah trigger (lewati arus charging)
const int      N_SAMPLES     = 40;
const float    LOD_NA        = 1.0;    // di bawah ini dianggap "tidak ada arus"

// Kalibrasi linear: I(nA) = CAL_SLOPE * glukosa(mg/dL) + CAL_INTERCEPT
// Isi dari hasil regresi larutan standar.
float CAL_SLOPE     = 1.0;
float CAL_INTERCEPT = 0.0;

// Kalibrasi pH: V(pH) = PH_M * pH + PH_C  (hasil calibrate.py). PH_M = 0 -> belum dikalibrasi,
// pH dikirim null. Fruktosamin tidak punya kalibrasi: dikirim sebagai volt.
float PH_M = 0.0;
float PH_C = 0.0;

// Cloud (topik sama dengan firmware/firmware.ino)
#define DEVICE_CODE "GLICO-01"
#define FW_VERSION  "0.3.0"
const char*    TOPIC_READ    = "glicovia/devices/" DEVICE_CODE "/readings";
const char*    TOPIC_PRED    = "glicovia/devices/" DEVICE_CODE "/predictions";
const uint32_t PRED_WAIT_MS  = 12000;
// ===============================================

Adafruit_ADS1115 ads;
WiFiClient wifi;
PubSubClient mqtt(wifi);
uint32_t i2cErrCount = 0;
bool predGot = false;

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

void onMsg(char*, byte* p, unsigned int len) {
  Serial.print("Balasan cloud: ");
  Serial.write(p, len);
  Serial.println();
  predGot = true;
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

// Angka untuk JSON; "null" bila NaN/Inf supaya JSON tetap valid.
const char* num(char* b, size_t sz, float v, int dec) {
  if (!isfinite(v)) snprintf(b, sz, "null");
  else              snprintf(b, sz, "%.*f", dec, v);
  return b;
}

// Kirim satu ringkasan pengukuran. ph/glu sudah satuan riil bila terkalibrasi, selain itu null / volt.
void sendReading(float vPh, float vFru, float vGlu, float vMid, float iNA, float cv,
                 int n, int nSat, bool phCal, bool gluCal, float glu) {
  float ph = phCal ? (vPh - PH_C) / PH_M : NAN;
  char sPh[16], sFru[16], sGlu[16], sVph[16], sVfru[16], sVglu[16], sMid[16], sI[16], sCv[16];
  static char json[768];
  snprintf(json, sizeof json,
    "{\"device_code\":\"%s\",\"ph\":%s,\"fructosamine\":%s,\"salivary_glucose\":%s,"
    "\"units\":{\"ph\":\"%s\",\"fructosamine\":\"V\",\"salivary_glucose\":\"%s\"},"
    "\"raw\":{\"v_ph\":%s,\"v_fru\":%s,\"v_glu\":%s,\"v_mid\":%s,\"i_glu_nA\":%s},"
    "\"quality\":{\"n\":%d,\"n_sat\":%d,\"saturated\":%s,\"cv_pct\":%s},"
    "\"fw_version\":\"%s\"}",
    DEVICE_CODE,
    num(sPh, sizeof sPh, ph, 2), num(sFru, sizeof sFru, vFru, 4),
    num(sGlu, sizeof sGlu, gluCal ? glu : vGlu, gluCal ? 2 : 4),
    phCal ? "pH" : "none", gluCal ? "mg/dL" : "V",
    num(sVph, sizeof sVph, vPh, 4), num(sVfru, sizeof sVfru, vFru, 4), num(sVglu, sizeof sVglu, vGlu, 4),
    num(sMid, sizeof sMid, vMid, 4), num(sI, sizeof sI, iNA, 2),
    n, nSat, nSat > n / 2 ? "true" : "false", num(sCv, sizeof sCv, cv, 2),
    FW_VERSION);
  Serial.println(json);

  predGot = false;
  if (!netUp()) { netDown(); Serial.println("GAGAL: WiFi/MQTT tidak tersambung, data tidak terkirim."); return; }
  Serial.println(mqtt.publish(TOPIC_READ, json) ? "Publish OK" : "Publish GAGAL");
  uint32_t t0 = millis();
  while (!predGot && millis() - t0 < PRED_WAIT_MS) { mqtt.loop(); delay(20); }
  if (!predGot) Serial.println("Belum ada prediksi (cek website).");
  netDown();
}

void measure() {
  Serial.println("\n===== MODE UKUR: teteskan sampel dalam 30 detik =====");

  // 1. Baseline tanpa sampel
  float base = 0; int nb = 0;
  for (int i = 0; i < 10; i++) {
    Reading r = readOnce();
    if (r.ok) { base += r.iNA; nb++; }
    delay(30);
  }
  if (nb == 0) { Serial.println("GAGAL: ADS1115 tidak merespons (cek SDA/SCL/VDD)"); return; }
  base /= nb;
  Serial.printf("Baseline: %.2f nA\n", base);

  // 2. Tunggu trigger (perubahan arus saat sampel masuk)
  uint32_t t0 = millis(); bool trig = false;
  while (millis() - t0 < 30000) {
    Reading r = readOnce();
    if (r.ok && fabs(r.iNA - base) > TRIG_NA) { trig = true; break; }
    delay(20);
  }
  if (!trig) {
    Serial.println("TIDAK ADA TRIGGER: arus tidak berubah.");
    Serial.println(" -> cek kontak konektor strip, sampel menutupi 3 elektroda, bias WE-RE (VSET).");
    return;
  }
  Serial.printf("Sampel terdeteksi. Tunggu %lu ms...\n", DELAY_MS);
  delay(DELAY_MS);

  // 3. Ambil sampel di jendela waktu tetap
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
  if (n < 10) { Serial.println("GAGAL: terlalu banyak error I2C saat sampling."); return; }

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

  Serial.println("----- HASIL -----");
  Serial.printf("N=%d  jenuh=%d  gagal_I2C=%d\n", n, nSat, nFail);
  Serial.printf("I min/median/max : %.2f / %.2f / %.2f nA\n", buf[0], buf[n / 2], buf[n - 1]);
  Serial.printf("I trimmed mean   : %.2f nA (delta baseline %.2f nA)\n", tmean, tmean - base);
  Serial.printf("SD = %.2f nA   CV = %.1f %%\n", sd, cv);
  Serial.printf("Fruktosa (A0) rata-rata: %.4f V   pH (A2) rata-rata: %.4f V\n", sumFru / n, sumPh / n);

  float glu = (tmean - CAL_INTERCEPT) / CAL_SLOPE;   // TANPA clamp ke 0
  if (fabs(tmean) < LOD_NA) Serial.println("Glukosa: < batas deteksi (arus ~0)");
  else                      Serial.printf("Glukosa: %.2f mg/dL %s\n", glu, glu < 0 ? "(NEGATIF -> kalibrasi/intercept salah)" : "");

  if (nSat > 0)  Serial.println("PERINGATAN: ada sampel jenuh -> naikkan DELAY_MS atau turunkan gain/Rf.");
  if (cv > 10)   Serial.println("PERINGATAN: CV > 10% -> noise tinggi (cek Cf, kabel, WiFi, daya).");
  Serial.println("=================\n");

  bool gluCal = CAL_SLOPE != 1.0f || CAL_INTERCEPT != 0.0f;
  sendReading(sumPh / n, sumFru / n, sumGlu / n, sumMid / n, tmean, cv,
              n, nSat, PH_M != 0, gluCal, glu);
}

void setup() {
  Serial.begin(115200);
  delay(500);
  WiFi.mode(WIFI_OFF);                         // matikan radio selama diagnostik

  esp_reset_reason_t rr = esp_reset_reason();
  Serial.printf("\nReset reason: %d %s\n", rr,
                rr == ESP_RST_BROWNOUT ? "(BROWNOUT! cek MT3608 / baterai)" : "");

  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(100000);
  if (!ads.begin(ADS_ADDR, &Wire)) {
    Serial.println("ADS1115 TIDAK DITEMUKAN di 0x48. Cek kabel I2C & ADDR=GND.");
  } else {
    Serial.println("ADS1115 OK");
  }
  ads.setDataRate(RATE_ADS1115_32SPS);

  Serial.println("Kanal: A0=fruktosa  A1=glukosa  A2=pH  A3=VMID");
  Serial.printf("Mode: %s\n", USE_A3_VMID ? "diferensial A1-A3" : "single-ended A1 vs VMID_NOMINAL");
  Serial.println("Ketik 'm' + Enter untuk mode ukur.\n");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'm' || c == 'M') measure();
    while (Serial.available()) Serial.read();
  }

  Reading r = readOnce();
  Serial.printf("raw=%6d  Vfru=%.4f V  Vglu=%.4f V  VpH=%.4f V  Vmid=%.4f V  I=%8.2f nA  errI2C=%lu  | %s\n",
                r.raw, r.vFru, r.vOut, r.vPh, r.vMid, r.iNA, i2cErrCount, label(r));
  delay(250);
}
