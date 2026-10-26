#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h> 

// Konfigurasi Layar OLED
#define i2c_Address 0x3C 
Adafruit_SH1106G display = Adafruit_SH1106G(128, 64, &Wire, -1);

// Konfigurasi ADC
Adafruit_ADS1115 ads;

void setup() {
  Serial.begin(115200);

  // Inisialisasi OLED
  display.begin(i2c_Address, true);
  display.clearDisplay();
  display.setTextColor(SH110X_WHITE);
  display.setTextSize(1);
  display.setCursor(10, 25);
  display.print("Sistem Standby...");
  display.display();

  // Inisialisasi ADS1115
  // Gunakan GAIN_ONE (+/- 4.096V) untuk tes Power Supply
  // Gunakan GAIN_SIXTEEN (+/- 0.256V) untuk tes Saliva asli
  ads.setGain(GAIN_ONE); 
  
  if (!ads.begin()) {
    Serial.println("Error: ADS1115 tidak terdeteksi!");
    while (1); 
  }
}

void loop() {
  // 1. Ambil data mentah (ADC) dan konversi ke Voltase
  float v_glukosa  = ads.computeVolts(ads.readADC_SingleEnded(0)); // Pin A0
  float v_fruktosa = ads.computeVolts(ads.readADC_SingleEnded(1)); // Pin A1
  float v_ph       = ads.computeVolts(ads.readADC_SingleEnded(2)); // Pin A2

  // 2. Tampilkan ke Serial Monitor (Untuk plot grafik di PC)
  Serial.print("Glu:"); Serial.print(v_glukosa, 5); Serial.print("\t");
  Serial.print("Fru:"); Serial.print(v_fruktosa, 5);Serial.print("\t");
  Serial.print("pH:");  Serial.println(v_ph, 5);      

  // 3. Tampilkan ke Layar OLED
  display.clearDisplay();
  display.setCursor(0, 0);  display.print("--- BACAAN SENSOR ---");
  
  display.setCursor(0, 20); display.print("Glu: "); display.print(v_glukosa, 5); display.print(" V");
  display.setCursor(0, 35); display.print("Fru: "); display.print(v_fruktosa, 5);display.print(" V");
  display.setCursor(0, 50); display.print("pH : "); display.print(v_ph, 5);      display.print(" V");
  
  display.display();
}