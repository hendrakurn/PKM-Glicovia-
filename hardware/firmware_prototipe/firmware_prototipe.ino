// ============================================================
//  Glicovia - Firmware PROTOTIPE
//  Mode ukur (tombol BOOT atau 'm') + kalibrasi via Serial
//  + kirim JSON ke cloud + tampil hasil di OLED 1,3" (SH1106)
//
//  Pembacaan : sama dengan backup/masHaikalKeren.cpp
//              A0 = fruktosa, A1 = glukosa (TIA), A2 = pH, A3 = VMID
//  Jaringan  : topik MQTT sama dengan firmware/firmware.ino
//  Library   : Adafruit ADS1X15, Adafruit GFX, Adafruit SH110X, PubSubClient (>= 2.8)
//  Siapkan   : salin secrets.example.h -> secrets.h lalu isi
//
//  Perintah Serial (115200, akhiri Enter):
//    m                 mulai pengukuran (sama dengan tombol BOOT)
//    live              nyalakan/matikan monitor kontinu 250 ms
//    cal ph <pH>       catat titik kalibrasi pH (elektroda sudah stabil di buffer)
//    cal glu <mg/dL>   catat titik kalibrasi glukosa
//    fit ph|glu [force] hitung & simpan fungsi kalibrasi (butuh >= 3 titik)
//    set ph <m> <c>    masukkan koefisien hasil hitung luar (V = m*pH + c)
//    set glu <a> <b>   masukkan koefisien glukosa (I[nA] = a*C + b)
//    show              tampilkan kalibrasi tersimpan + titik
//    clear             hapus titik kalibrasi di RAM (kalibrasi tersimpan tetap)
// ============================================================
#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <Preferences.h>
#include <PubSubClient.h>
#include <Adafruit_ADS1X15.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
#include "logic.h"
#include "secrets.h"

// ================= KONFIGURASI =================
#define FW_VERSION   "0.2.0"
#define DEVICE_CODE  "GLICO-01"
#define BTN_PIN      0            // tombol BOOT di DevKitC (aktif LOW)
#define I2C_SDA      21
#define I2C_SCL      22
#define ADS_ADDR     0x48
#define OLED_ADDR    0x3C

#define CH_FRU 0
#define CH_GLU 1
#define CH_PH  2
#define CH_VMID 3

#define REQUIRE_PH_CAL     1      // 1 = jangan kirim ke cloud bila pH belum dikalibrasi
#define SEND_IF_SATURATED  1      // prototipe: kirim walau jenuh, ditandai saturated:true

const float    RF          = 100e3;   // ohm, feedback TIA
const uint32_t STABLE_MS   = 60000;   // tunggu setelah sampel menetes (lewati transien)
const int      N           = 40;      // jumlah pembacaan per pengukuran / titik kalibrasi
const uint32_t PRED_WAIT_MS = 12000;  // tunggu balasan prediksi

const char* TOPIC_READ = "glicovia/devices/" DEVICE_CODE "/readings";
const char* TOPIC_PRED = "glicovia/devices/" DEVICE_CODE "/predictions";
// ===============================================

Adafruit_ADS1115 ads;
Adafruit_SH1106G display(128, 64, &Wire, -1);
WiFiClient wifi;
PubSubClient mqtt(wifi);
Preferences prefs;

struct Cal { float phM, phC, gluA, gluB; uint32_t ver; } cal = {0, 0, 0, 0, 0};
Pt phPts[8], gluPts[8];
int nPh = 0, nGlu = 0;
bool liveMode = false;
uint32_t i2cErr = 0;

struct Pred { bool got; float glu; float conf; char cat[20]; } pred;

// ---------- pembacaan (sama dengan masHaikalKeren.cpp) ----------
struct Reading { bool ok; int16_t raw; float vFru, vOut, vPh, vMid, iNA; bool sat; };

bool i2cOk() {
  Wire.beginTransmission(ADS_ADDR);
  return Wire.endTransmission() == 0;
}

Reading readOnce() {
  Reading r = {false, 0, 0, 0, 0, 0, 0, false};
  if (!i2cOk()) { i2cErr++; return r; }
  ads.setGain(GAIN_ONE);
  r.vFru = ads.computeVolts(ads.readADC_SingleEnded(CH_FRU));
  r.vOut = ads.computeVolts(ads.readADC_SingleEnded(CH_GLU));
  r.vPh  = ads.computeVolts(ads.readADC_SingleEnded(CH_PH));
  r.vMid = ads.computeVolts(ads.readADC_SingleEnded(CH_VMID));
  ads.setGain(GAIN_FOUR);
  r.raw = ads.readADC_Differential_1_3();                  // A1 - A3
  float vDiff = ads.computeVolts(r.raw);
  r.sat = (abs(r.raw) > 32000) || (r.vOut < 0.05f) || (r.vOut > 3.25f);
  r.iNA = -vDiff / RF * 1e9f;                              // Vout = VMID - I*Rf
  r.ok = true;
  return r;
}

// Kumpulan N pembacaan -> rata-rata terpangkas per kanal
struct Agg { int n, nSat, nFail; float vPh, vFru, vGlu, vMid, iNA, sdPhMv, cvI; };

bool collect(Agg& g) {
  float ph[N], fru[N], glu[N], mid[N], cur[N];
  g = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
  while (g.n < N && g.nFail < 20) {
    Reading r = readOnce();
    if (!r.ok) { g.nFail++; continue; }
    if (r.sat) g.nSat++;
    ph[g.n] = r.vPh; fru[g.n] = r.vFru; glu[g.n] = r.vOut; mid[g.n] = r.vMid; cur[g.n] = r.iNA;
    g.n++;
  }
  if (g.n < 10) return false;
  g.sdPhMv = sdev(ph, g.n) * 1000.0f;
  float sdI = sdev(cur, g.n);
  g.vPh = trimMean(ph, g.n); g.vFru = trimMean(fru, g.n);
  g.vGlu = trimMean(glu, g.n); g.vMid = trimMean(mid, g.n); g.iNA = trimMean(cur, g.n);
  g.cvI = fabsf(g.iNA) > 1e-6f ? sdI / fabsf(g.iNA) * 100.0f : 0;
  return true;
}

// ---------- OLED ----------
void oled4(const char* a, const char* b = "", const char* c = "", const char* d = "") {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);
  const char* L[4] = {a, b, c, d};
  for (int i = 0; i < 4; i++) { display.setCursor(0, i * 16); display.print(L[i]); }
  display.display();
}

void oledProgress(const char* title, int pct, int sec) {
  char t[24];
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);
  display.setCursor(0, 0);  display.print(title);
  display.drawRect(0, 20, 128, 12, SH110X_WHITE);
  display.fillRect(0, 20, pct * 128 / 100, 12, SH110X_WHITE);
  snprintf(t, sizeof t, "%d detik lagi", sec);
  display.setCursor(0, 40); display.print(t);
  display.setCursor(0, 54); display.print("BOOT = batal");
  display.display();
}

void showIdle() { oled4("GLICOVIA  PROTOTIPE", "", "Teteskan sampel,", "lalu tekan BOOT"); }

// ---------- kalibrasi (NVS) ----------
void loadCal() {
  prefs.begin("glicovia", true);
  cal.phM = prefs.getFloat("phM", 0);  cal.phC = prefs.getFloat("phC", 0);
  cal.gluA = prefs.getFloat("gluA", 0); cal.gluB = prefs.getFloat("gluB", 0);
  cal.ver = prefs.getUInt("ver", 0);
  prefs.end();
}

void saveCal() {
  cal.ver++;
  prefs.begin("glicovia", false);
  prefs.putFloat("phM", cal.phM);   prefs.putFloat("phC", cal.phC);
  prefs.putFloat("gluA", cal.gluA); prefs.putFloat("gluB", cal.gluB);
  prefs.putUInt("ver", cal.ver);
  prefs.end();
}

void cmdCal(bool isPh, float x) {
  Pt* pts = isPh ? phPts : gluPts;
  int& n = isPh ? nPh : nGlu;
  if (n >= 8) { Serial.println("Titik penuh (8). Ketik 'clear'."); return; }
  Serial.printf("Mengambil %d pembacaan...\n", N);
  Agg g;
  if (!collect(g)) { Serial.println("GAGAL: terlalu banyak error I2C"); return; }
  if (!isPh && g.nSat > g.n / 10) {
    Serial.printf("DITOLAK: kanal glukosa jenuh (%d/%d). Perbaiki hardware dulu.\n", g.nSat, g.n);
    return;
  }
  float y = isPh ? g.vPh : g.iNA;
  pts[n++] = {x, y};
  Serial.printf("Titik %d: x=%.3f  y=%.4f %s  (SD pH=%.2f mV, jenuh=%d/%d)\n",
                n, x, y, isPh ? "V" : "nA", g.sdPhMv, g.nSat, g.n);
}

void cmdFit(bool isPh, bool force) {
  Pt* pts = isPh ? phPts : gluPts;
  int n = isPh ? nPh : nGlu;
  if (n < 3) { Serial.println("Butuh >= 3 titik."); return; }
  float s, c, r2;
  if (!fitLine(pts, n, &s, &c, &r2)) { Serial.println("Fit gagal (titik tidak bervariasi)."); return; }
  bool ok;
  if (isPh) {
    Serial.printf("pH : V = %.5f*pH + %.5f   R2=%.4f   kemiringan %.1f mV/pH (Nernst 59.2)\n",
                  s, c, r2, s * 1000.0f);
    ok = r2 >= 0.99f && fabsf(s) >= 0.040f;     // kriteria PRD §15
  } else {
    Serial.printf("Glukosa : I = %.3f*C + %.3f nA   R2=%.4f\n", s, c, r2);
    ok = r2 >= 0.98f && s > 0;
  }
  if (!ok && !force) { Serial.println("TIDAK DISIMPAN: di bawah kriteria. Tambah 'force' untuk memaksa."); return; }
  if (isPh) { cal.phM = s; cal.phC = c; } else { cal.gluA = s; cal.gluB = c; }
  saveCal();
  Serial.printf("TERSIMPAN. cal_version=c%lu%s\n", (unsigned long)cal.ver, ok ? "" : "  (FORCE)");
}

void cmdShow() {
  Serial.printf("pH   : m=%.5f c=%.5f %s\n", cal.phM, cal.phC, cal.phM != 0 ? "" : "(BELUM)");
  Serial.printf("Glu  : a=%.3f b=%.3f %s\n", cal.gluA, cal.gluB, cal.gluA != 0 ? "" : "(BELUM)");
  Serial.printf("cal_version=c%lu\n", (unsigned long)cal.ver);
  for (int i = 0; i < nPh; i++)  Serial.printf("  titik pH  %d: pH=%.2f V=%.4f\n", i + 1, phPts[i].x, phPts[i].y);
  for (int i = 0; i < nGlu; i++) Serial.printf("  titik glu %d: C=%.2f I=%.2f nA\n", i + 1, gluPts[i].x, gluPts[i].y);
}

// ---------- jaringan ----------
void onMsg(char*, byte* p, unsigned int len) {
  static char msg[512];
  unsigned n = len < sizeof(msg) - 1 ? len : sizeof(msg) - 1;
  memcpy(msg, p, n); msg[n] = 0;
  Serial.printf("Balasan cloud: %s\n", msg);
  float v;
  if (!jsonNum(msg, "glucose_estimate", &v)) return;
  pred.glu = v;
  pred.conf = jsonNum(msg, "confidence_score", &v) ? v : -1;
  if (!jsonStr(msg, "clinical_category", pred.cat, sizeof pred.cat)) strcpy(pred.cat, "-");
  pred.got = true;
}

bool netUp() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  uint32_t t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 15000) delay(250);
  if (WiFi.status() != WL_CONNECTED) return false;
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(1024);                        // default 256 B: JSON kita lebih panjang
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
  WiFi.mode(WIFI_OFF);                             // radio mati lagi supaya ADC tidak terganggu
}

// ---------- satu siklus pengukuran ----------
bool btnPressed() {
  if (digitalRead(BTN_PIN) != LOW) return false;
  delay(40);
  if (digitalRead(BTN_PIN) != LOW) return false;
  while (digitalRead(BTN_PIN) == LOW) delay(10);
  return true;
}

bool waitStable() {
  uint32_t t0 = millis();
  while (millis() - t0 < STABLE_MS) {
    uint32_t el = millis() - t0;
    oledProgress("Menunggu stabil", el * 100 / STABLE_MS, (STABLE_MS - el) / 1000);
    if (btnPressed()) return false;
    delay(250);
  }
  return true;
}

void measureCycle() {
  Serial.println("\n===== MODE UKUR =====");
  if (!i2cOk()) { oled4("GAGAL", "ADS1115 tidak", "merespons"); Serial.println("ADS1115 tidak merespons"); return; }
  if (!waitStable()) { Serial.println("Dibatalkan."); showIdle(); return; }

  oled4("Mengukur...");
  Agg g;
  if (!collect(g)) { oled4("GAGAL", "Error I2C", "terlalu banyak"); return; }

  bool sat = g.nSat > g.n / 2;
  bool phCal = cal.phM != 0, gluCal = cal.gluA != 0;
  float ph  = phCal ? phFromV(g.vPh, cal.phM, cal.phC) : NAN;
  float glu = gluCal ? gluFromI(g.iNA, cal.gluB, cal.gluA) : g.vGlu;

  char sPh[16], sFru[16], sGlu[16], sMid[16], sI[16], sVph[16], sVf[16], sVg[16], sCv[16], sSd[16];
  static char json[768];
  snprintf(json, sizeof json,
    "{\"device_code\":\"%s\",\"ph\":%s,\"fructosamine\":%s,\"salivary_glucose\":%s,"
    "\"units\":{\"ph\":\"%s\",\"fructosamine\":\"V\",\"salivary_glucose\":\"%s\"},"
    "\"raw\":{\"v_ph\":%s,\"v_fru\":%s,\"v_glu\":%s,\"v_mid\":%s,\"i_glu_nA\":%s},"
    "\"quality\":{\"n\":%d,\"n_sat\":%d,\"saturated\":%s,\"cv_pct\":%s,\"sd_ph_mv\":%s},"
    "\"fw_version\":\"%s\",\"cal_version\":\"c%lu\"}",
    DEVICE_CODE,
    fmtNum(sPh, sizeof sPh, ph, 2), fmtNum(sFru, sizeof sFru, g.vFru, 4), fmtNum(sGlu, sizeof sGlu, glu, gluCal ? 2 : 4),
    phCal ? "pH" : "none", gluCal ? "mg/dL" : "V",
    fmtNum(sVph, sizeof sVph, g.vPh, 4), fmtNum(sVf, sizeof sVf, g.vFru, 4), fmtNum(sVg, sizeof sVg, g.vGlu, 4),
    fmtNum(sMid, sizeof sMid, g.vMid, 4), fmtNum(sI, sizeof sI, g.iNA, 2),
    g.n, g.nSat, sat ? "true" : "false", fmtNum(sCv, sizeof sCv, g.cvI, 2), fmtNum(sSd, sizeof sSd, g.sdPhMv, 2),
    FW_VERSION, (unsigned long)cal.ver);
  Serial.println(json);

  const char* blocked = nullptr;
  if (REQUIRE_PH_CAL && !phCal) blocked = "pH belum kalibrasi";
  else if (!SEND_IF_SATURATED && sat) blocked = "Sensor jenuh";
  if (blocked) {
    oled4("TIDAK DIKIRIM", blocked, "(lihat Serial)");
    Serial.printf("Tidak dikirim: %s\n", blocked);
    return;
  }

  oled4("Mengirim ke cloud", "WiFi...");
  pred.got = false;
  if (!netUp()) { netDown(); oled4("GAGAL", "WiFi/MQTT putus", "data tidak terkirim"); return; }
  bool sent = mqtt.publish(TOPIC_READ, json);
  Serial.println(sent ? "Publish OK" : "Publish GAGAL");
  uint32_t t0 = millis();
  while (!pred.got && millis() - t0 < PRED_WAIT_MS) { mqtt.loop(); delay(20); }
  netDown();

  char l1[24], l2[24], l3[24];
  if (!sent) { oled4("GAGAL", "Publish ditolak"); return; }
  if (!pred.got) { oled4("Terkirim", "Belum ada prediksi", "cek website"); return; }
  snprintf(l1, sizeof l1, "Glukosa: %.0f mg/dL", pred.glu);
  snprintf(l2, sizeof l2, "Status : %s", pred.cat);
  if (phCal) snprintf(l3, sizeof l3, "pH     : %.2f", ph); else l3[0] = 0;
  oled4(l1, l2, l3, "PROTOTIPE");
}

// ---------- Serial ----------
void handleLine(String s) {
  s.trim();
  if (s.length() == 0) return;
  if (s == "m") { measureCycle(); return; }
  if (s == "live") { liveMode = !liveMode; return; }
  if (s == "show") { cmdShow(); return; }
  if (s == "clear") { nPh = nGlu = 0; Serial.println("Titik dihapus."); return; }
  if (s.startsWith("cal ph "))  { cmdCal(true,  s.substring(7).toFloat()); return; }
  if (s.startsWith("cal glu ")) { cmdCal(false, s.substring(8).toFloat()); return; }
  if (s.startsWith("fit ph"))   { cmdFit(true,  s.endsWith("force")); return; }
  if (s.startsWith("fit glu"))  { cmdFit(false, s.endsWith("force")); return; }
  float p, q;
  if (s.startsWith("set ph ") || s.startsWith("set glu ")) {
    bool isPh = s.startsWith("set ph ");
    if (sscanf(s.c_str() + (isPh ? 7 : 8), "%f %f", &p, &q) == 2 && p != 0) {
      if (isPh) { cal.phM = p; cal.phC = q; } else { cal.gluA = p; cal.gluB = q; }
      saveCal();
      Serial.printf("TERSIMPAN. cal_version=c%lu\n", (unsigned long)cal.ver);
    } else Serial.println("Format: set ph <m V/pH> <c V>  |  set glu <a nA per mg/dL> <b nA>");
    return;
  }
  Serial.println("Perintah: m | live | cal ph <pH> | cal glu <mg/dL> | fit ph|glu [force] | set ph|glu <k> <c> | show | clear");
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(100);
  delay(300);
  WiFi.mode(WIFI_OFF);
  pinMode(BTN_PIN, INPUT_PULLUP);
  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(100000);
  if (!display.begin(OLED_ADDR, true)) Serial.println("OLED SH1106 tidak ditemukan (cek SDA/SCL, alamat, jenis controller)");
  if (!ads.begin(ADS_ADDR, &Wire)) { Serial.println("ADS1115 TIDAK DITEMUKAN di 0x48"); oled4("ADS1115 tidak", "ditemukan"); }
  ads.setDataRate(RATE_ADS1115_32SPS);
  loadCal();
  Serial.printf("\nGlicovia prototipe fw %s  cal=c%lu  (ketik 'show')\n", FW_VERSION, (unsigned long)cal.ver);
  showIdle();
}

void loop() {
  if (Serial.available()) handleLine(Serial.readStringUntil('\n'));
  if (btnPressed()) measureCycle();          // layar hasil bertahan sampai pengukuran berikutnya
  if (liveMode) {
    Reading r = readOnce();
    Serial.printf("Vfru=%.4f  Vglu=%.4f  VpH=%.4f  Vmid=%.4f  I=%.2f nA  sat=%d\n",
                  r.vFru, r.vOut, r.vPh, r.vMid, r.iNA, r.sat);
    delay(250);
  } else {
    delay(20);
  }
}
