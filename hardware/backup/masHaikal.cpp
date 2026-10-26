// ============================================================
//  Glicovia - Firmware DIAGNOSTIK kanal glukosa (CH1, A0)
//  ESP32 + ADS1115 (0x48) + TIA Rf 100k
//  Serial 115200. Ketik 'm' + Enter untuk mode ukur.
//  Tanpa input -> monitor kontinu tiap 250 ms.
//  Library: adafruit/Adafruit ADS1X15
// ============================================================
#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <Adafruit_ADS1X15.h>
#include <esp_system.h>

// ================= KONFIGURASI =================
#define USE_A3_VMID 1        // 1 = VMID sudah dijumper ke A3 (diferensial A0-A3)
                             // 0 = belum dijumper, pakai VMID_NOMINAL
#define I2C_SDA   21
#define I2C_SCL   22
#define ADS_ADDR  0x48

const float    RF            = 100e3;  // ohm, resistor feedback TIA
const float    VMID_NOMINAL  = 1.65;   // isi hasil ukur multimeter jika USE_A3_VMID = 0
const float    TRIG_NA       = 5.0;    // ambang deteksi sampel masuk (nA)
const uint32_t DELAY_MS      = 3000;   // tunggu setelah trigger (lewati arus charging)
const int      N_SAMPLES     = 40;
const float    LOD_NA        = 1.0;    // di bawah ini dianggap "tidak ada arus"

// Kalibrasi linear: I(nA) = CAL_SLOPE * glukosa(mg/dL) + CAL_INTERCEPT
// Isi dari hasil regresi larutan standar.
float CAL_SLOPE     = 1.0;
float CAL_INTERCEPT = 0.0;
// ===============================================

Adafruit_ADS1115 ads;
uint32_t i2cErrCount = 0;

struct Reading {
  bool    ok;
  int16_t raw;    // raw yang dipakai untuk hitung arus
  float   vOut;   // tegangan output TIA (A0, single-ended)
  float   vMid;   // VMID (A3 atau nominal)
  float   iNA;    // arus sensor (nA)
  bool    sat;    // output jenuh / ADC mentok
};

bool i2cOk() {
  Wire.beginTransmission(ADS_ADDR);
  return Wire.endTransmission() == 0;
}

Reading readOnce() {
  Reading r = {false, 0, 0, 0, 0, false};
  if (!i2cOk()) { i2cErrCount++; return r; }

  ads.setGain(GAIN_ONE);                       // +/-4.096 V
  int16_t rawA0 = ads.readADC_SingleEnded(0);
  r.vOut = ads.computeVolts(rawA0);

#if USE_A3_VMID
  r.vMid = ads.computeVolts(ads.readADC_SingleEnded(3));
  ads.setGain(GAIN_FOUR);                      // +/-1.024 V, 1 LSB ~ 0.31 nA
  r.raw = ads.readADC_Differential_0_3();
  float vDiff = ads.computeVolts(r.raw);
  r.sat = (abs(r.raw) > 32000);
#else
  r.vMid = VMID_NOMINAL;
  r.raw  = rawA0;
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
  while (n < N_SAMPLES && nFail < 20) {
    Reading r = readOnce();
    if (!r.ok) { nFail++; continue; }
    if (r.sat) nSat++;
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

  float glu = (tmean - CAL_INTERCEPT) / CAL_SLOPE;   // TANPA clamp ke 0
  if (fabs(tmean) < LOD_NA) Serial.println("Glukosa: < batas deteksi (arus ~0)");
  else                      Serial.printf("Glukosa: %.2f mg/dL %s\n", glu, glu < 0 ? "(NEGATIF -> kalibrasi/intercept salah)" : "");

  if (nSat > 0)  Serial.println("PERINGATAN: ada sampel jenuh -> naikkan DELAY_MS atau turunkan gain/Rf.");
  if (cv > 10)   Serial.println("PERINGATAN: CV > 10% -> noise tinggi (cek Cf, kabel, WiFi, daya).");
  Serial.println("=================\n");
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

  Serial.printf("Mode: %s\n", USE_A3_VMID ? "diferensial A0-A3" : "single-ended A0 vs VMID_NOMINAL");
  Serial.println("Ketik 'm' + Enter untuk mode ukur.\n");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'm' || c == 'M') measure();
    while (Serial.available()) Serial.read();
  }

  Reading r = readOnce();
  Serial.printf("raw=%6d  Vout=%.4f V  Vmid=%.4f V  I=%8.2f nA  errI2C=%lu  | %s\n",
                r.raw, r.vOut, r.vMid, r.iNA, i2cErrCount, label(r));
  delay(250);
}