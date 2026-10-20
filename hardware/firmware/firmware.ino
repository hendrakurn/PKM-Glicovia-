#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h> 
#include <WiFi.h>
#include <PubSubClient.h>

// ================= KONFIGURASI WIFI & MQTT =================
// Sesuaikan dengan Hotspot/WiFi Anda
const char* ssid        = "12345678";
const char* password    = "admin1234";

const char* mqtt_server     = "broker.hivemq.com";
const int   mqtt_port       = 1883;
const char* mqtt_topic      = "glicovia/devices/GLICO-01/readings";
const char* mqtt_pred_topic = "glicovia/devices/GLICO-01/predictions";
const char* device_code     = "GLICO-01";

WiFiClient espClient;
PubSubClient client(espClient);

// Variabel Penampung Hasil Prediksi AI dari Cloud
float latest_glucose_est = -1.0;
String latest_category = "";
int latest_confidence = 0;
unsigned long lastPredReceivedTime = 0;

// ================= KONFIGURASI HARDWARE ====================
#define i2c_Address 0x3C 
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1   

Adafruit_SH1106G display = Adafruit_SH1106G(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
Adafruit_ADS1115 ads;

// Variabel Timer non-blocking untuk MQTT
unsigned long lastPublishTime = 0;
const long publishInterval = 5000; // Publish setiap 5 detik (5000 ms)

// ================= CALLBACK PREDIKSI MQTT ===================
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Hasil Prediksi Diterima [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);

  int gluIdx = message.indexOf("\"glucose_estimate\":");
  if (gluIdx != -1) {
    int start = gluIdx + 19;
    int end = message.indexOf(",", start);
    if (end != -1) {
      latest_glucose_est = message.substring(start, end).toFloat();
    }
  }
  int catIdx = message.indexOf("\"clinical_category\":\"");
  if (catIdx != -1) {
    int start = catIdx + 21;
    int end = message.indexOf("\"", start);
    if (end != -1) {
      latest_category = message.substring(start, end);
    }
  }
  int confIdx = message.indexOf("\"confidence_score\":");
  if (confIdx != -1) {
    int start = confIdx + 19;
    int end = message.indexOf(",", start);
    if (end == -1) end = message.indexOf("}", start);
    if (end != -1) {
      latest_confidence = (int)(message.substring(start, end).toFloat() * 100);
    }
  }
  lastPredReceivedTime = millis();
}

// ================= FUNGSI RECONNECT MQTT ===================
void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Menghubungkan ke MQTT Broker...");
    // Gunakan Device Code sebagai Client ID
    if (client.connect(device_code)) {
      Serial.println(" BERHASIL!");
      client.subscribe(mqtt_pred_topic);
      Serial.println("Subscribed ke topik prediksi cloud!");
    } else {
      Serial.print(" GAGAL, rc=");
      Serial.print(client.state());
      Serial.println(" Coba lagi dalam 5 detik...");
      delay(5000);
    }
  }
}

// ================= SETUP SYSTEM ============================
void setup(void) {
  Serial.begin(115200);
  Serial.println("\nMemulai Inisialisasi Sistem Glicovia...");

  // 1. Inisialisasi Layar OLED
  delay(250); 
  if(!display.begin(i2c_Address, true)) {
    Serial.println("Gagal menemukan layar OLED SH1106! Periksa kabel I2C.");
    while (1);
  }
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);
  display.setCursor(15, 20);
  display.println("Sistem Glicovia");
  display.setCursor(15, 35);
  display.println("Connecting WiFi...");
  display.display();

  // 2. Koneksi WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Terhubung!");
  
  display.clearDisplay();
  display.setCursor(15, 20);
  display.println("WiFi Terhubung!");
  display.display();
  delay(1000);

  // 3. Konfigurasi MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);

  // 4. Inisialisasi ADS1115
  ads.setGain(GAIN_ONE); 
  if (!ads.begin()) {
    Serial.println("Gagal menemukan ADS1115! Cek kabel SDA/SCL.");
    while (1); 
  }
  
  Serial.println("Sensor, Layar, dan Jaringan Siap!");
}

// ================= MAIN LOOP ===============================
void loop(void) {
  // Jaga koneksi MQTT tetap hidup
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();

  int16_t adc0, adc1, adc2;
  float volts0, volts1, volts2;

  // Membaca Channel ADS1115
  adc0 = ads.readADC_SingleEnded(0); volts0 = ads.computeVolts(adc0);
  adc1 = ads.readADC_SingleEnded(1); volts1 = ads.computeVolts(adc1);
  adc2 = ads.readADC_SingleEnded(2); volts2 = ads.computeVolts(adc2);

  // Mengubah tegangan menjadi nilai analit (Ganti dengan rumus regresi kalibrasi Anda)
  // Format desimal dipertahankan agar tingkat presisi tetap tinggi
  float current_glucose = volts0 * 200.0; // Konstanta dummy
  float current_ph      = 7.0 + (volts1 * -5.0); // Konstanta dummy
  float current_fructo  = volts2 * 500.0; // Konstanta dummy

  // Menampilkan Data ke Layar OLED (Pembaruan cepat setiap 500ms)
  display.clearDisplay();
  display.setTextSize(1);

  // Jika ada hasil prediksi baru dari Cloud dalam 15 detik terakhir, tampilkan hasil AI!
  if (latest_glucose_est > 0 && (millis() - lastPredReceivedTime < 15000)) {
    display.setCursor(10, 0);
    display.println("HASIL PREDIKSI AI");
    display.drawLine(0, 10, 128, 10, SH110X_WHITE);

    display.setCursor(0, 18);
    display.print("Glukosa : ");
    display.print(latest_glucose_est, 1);
    display.println(" mg/dL");

    display.setCursor(0, 32);
    display.print("Status  : ");
    display.println(latest_category);

    display.setCursor(0, 46);
    display.print("Akurasi : ");
    display.print(latest_confidence);
    display.println(" %");
  } else {
    // Tampilan default: Pembacaan sensor analog real-time
    display.setCursor(5, 0);
    display.println("Data Sensor Real-Time");
    display.drawLine(0, 10, 128, 10, SH110X_WHITE);

    display.setCursor(0, 18);
    display.print("Glukosa : "); display.print(volts0, 4); display.println(" V");
    display.setCursor(0, 32);
    display.print("Nilai pH: "); display.print(volts1, 4); display.println(" V");
    display.setCursor(0, 46);
    display.print("Fruktosa: "); display.print(volts2, 4); display.println(" V");
  }
  display.display();

  // ================= PENGIRIMAN PAYLOAD JSON =================
  // Menggunakan fungsi millis() agar tidak mengganggu kecepatan pergerakan layar OLED
  unsigned long currentTime = millis();
  if (currentTime - lastPublishTime >= publishInterval) {
    lastPublishTime = currentTime;

    // Konstruksi JSON String dengan nilai riil (bukan bulat)
    String payload = "{";
    payload += "\"device_code\":\"" + String(device_code) + "\",";
    payload += "\"ph\":" + String(current_ph, 2) + ",";
    payload += "\"fructosamine\":" + String(current_fructo, 2) + ",";
    payload += "\"salivary_glucose\":" + String(current_glucose, 2);
    payload += "}";

    // Debugging di Serial Monitor
    Serial.print("Mem-publish ke topik: ");
    Serial.println(mqtt_topic);
    Serial.print("Payload: ");
    Serial.println(payload);

    // Kirim data ke HiveMQ
    if(client.publish(mqtt_topic, payload.c_str())) {
      Serial.println("-> Publish Berhasil!");
    } else {
      Serial.println("-> Publish Gagal!");
    }
    Serial.println("-----------------------------------");
  }

  // Delay kecil untuk stabilitas siklus I2C (OLED & ADS)
  delay(500); 
}
