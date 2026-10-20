#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>

// ================= KONFIGURASI HARDWARE ====================
#define OLED_ADDR 0x3C 
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1   

Adafruit_SH1106G display = Adafruit_SH1106G(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
Adafruit_ADS1115 ads;

// Periode sampling data (misal tiap 250 ms = 4 kali per detik)
const unsigned long sampleInterval = 250;
unsigned long lastSampleTime = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000); // Tunggu Serial siap maks 3 detik

  Serial.println("\n--- Glicovia Data Logger Mode (Tanpa WiFi) ---");

  // Inisialisasi OLED (tetap aktif jika terpasang, opsional jika tidak ada)
  if (!display.begin(OLED_ADDR, true)) {
    Serial.println("Peringatan: Layar OLED tidak terdeteksi. Melanjutkan mode Serial...");
  } else {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SH110X_WHITE);
    display.setCursor(10, 20);
    display.println("Glicovia Logger");
    display.setCursor(10, 35);
    display.println("Mode: USB Serial");
    display.display();
  }

  // Inisialisasi ADS1115
  ads.setGain(GAIN_ONE); // Jangkauan +/- 4.096V (1 bit = 0.125 mV)
  if (!ads.begin()) {
    Serial.println("ERROR: ADS1115 tidak ditemukan! Periksa koneksi SDA (21) / SCL (22).");
    while (1) {
      delay(1000);
    }
  }

  Serial.println("ADS1115 Siap!");
  
  // Header kolom CSV untuk pencatatan data ke Excel / Spreadsheet
  Serial.println("timestamp_ms,Glukosa_Raw,Glukosa_Volt,pH_Raw,pH_Volt,Fruktosamin_Raw,Fruktosamin_Volt");
}

void loop() {
  unsigned long now = millis();

  if (now - lastSampleTime >= sampleInterval) {
    lastSampleTime = now;

    // 1. Baca nilai mentah 16-bit dan voltase
    // A0 = Glukosa, A1 = Fruktosamin, A2 = pH (jalur aktif yang terhubung ke adapter SPCE)
    int16_t adc0 = ads.readADC_SingleEnded(0);
    int16_t adc1 = ads.readADC_SingleEnded(1);
    int16_t adc2 = ads.readADC_SingleEnded(2);

    float volt0 = ads.computeVolts(adc0);
    float volt1 = ads.computeVolts(adc1);
    float volt2 = ads.computeVolts(adc2);

    // 2. Format CSV untuk Serial Stream
    // Urutan: timestamp_ms, Glukosa (A0), pH (A2), Fruktosamin (A1)
    Serial.print(now);
    Serial.print(",");
    Serial.print(adc0);
    Serial.print(",");
    Serial.print(volt0, 4);
    Serial.print(",");
    Serial.print(adc2);
    Serial.print(",");
    Serial.print(volt2, 4);
    Serial.print(",");
    Serial.print(adc1);
    Serial.print(",");
    Serial.println(volt1, 4);

    // 3. Update OLED (jika aktif)
    display.clearDisplay();
    display.setCursor(5, 0);
    display.println("LOGGING REAL-TIME");
    display.drawLine(0, 10, 128, 10, SH110X_WHITE);

    display.setCursor(0, 16);
    display.print("Glukosa : "); display.print(volt0, 3); display.println(" V");
    
    display.setCursor(0, 32);
    display.print("Nilai pH: "); display.print(volt2, 3); display.println(" V");
    
    display.setCursor(0, 48);
    display.print("Fruktosa: "); display.print(volt1, 3); display.println(" V");
    
    display.display();
  }
}
