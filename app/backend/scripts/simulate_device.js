#!/usr/bin/env node

/**
 * Simulator Hardware GLICOVIA (ESP32 Virtual)
 * Mensimulasikan:
 * 1. Koneksi ke broker MQTT HiveMQ
 * 2. Mengirimkan data telemetri biomarker saliva ke backend
 * 3. Menerima hasil estimasi & diagnosis AI dari cloud
 * 4. Merender visualisasi layar OLED di terminal
 */

const mqtt = require('mqtt');

// Konfigurasi
const BROKER_URL   = process.env.MQTT_URL || 'mqtt://broker.hivemq.com:1883';
const DEVICE_CODE  = process.argv[2] || 'GLICO-01';
const TOPIC_PREFIX = 'glicovia';

const READINGS_TOPIC    = `${TOPIC_PREFIX}/devices/${DEVICE_CODE}/readings`;
const PREDICTIONS_TOPIC = `${TOPIC_PREFIX}/devices/${DEVICE_CODE}/predictions`;

// Parse argument atau gunakan nilai default realistis
function parseArgs() {
  const args = process.argv.slice(2);
  let ph = 6.95;
  let fructosamine = 210.0;
  let salivary_glucose = 2.15;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--ph' && args[i + 1]) ph = parseFloat(args[i + 1]);
    if (args[i] === '--fructo' && args[i + 1]) fructosamine = parseFloat(args[i + 1]);
    if (args[i] === '--glucose' && args[i + 1]) salivary_glucose = parseFloat(args[i + 1]);
  }
  return { ph, fructosamine, salivary_glucose };
}

const sampleData = parseArgs();

console.log('====================================================');
console.log(`🤖 SIMULATOR PERANGKAT GLICOVIA (${DEVICE_CODE})`);
console.log('====================================================');
console.log(`🌐 Broker      : ${BROKER_URL}`);
console.log(`📤 Topik Kirim : ${READINGS_TOPIC}`);
console.log(`📥 Topik Terima: ${PREDICTIONS_TOPIC}`);
console.log('📊 Nilai Sensor:');
console.log(`   - pH Saliva          : ${sampleData.ph}`);
console.log(`   - Fruktosamin        : ${sampleData.fructosamine} µmol/L`);
console.log(`   - Glukosa Saliva     : ${sampleData.salivary_glucose} mg/dL`);
console.log('----------------------------------------------------');

const client = mqtt.connect(BROKER_URL, {
  clientId: `simulator_${DEVICE_CODE}_${Math.random().toString(16).slice(2, 8)}`,
  clean: true,
  connectTimeout: 8000
});

client.on('connect', () => {
  console.log('✅ Terhubung ke Broker MQTT!');

  // 1. Subscribe ke topik hasil prediksi
  client.subscribe(PREDICTIONS_TOPIC, (err) => {
    if (err) {
      console.error('❌ Gagal subscribe ke topik prediksi:', err);
      process.exit(1);
    }
    console.log(`📡 Berhasil subscribe ke: ${PREDICTIONS_TOPIC}`);

    // 2. Publish data sensor
    const payload = JSON.stringify({
      device_code: DEVICE_CODE,
      ph: sampleData.ph,
      fructosamine: sampleData.fructosamine,
      salivary_glucose: sampleData.salivary_glucose,
      timestamp: new Date().toISOString()
    });

    console.log('\n🚀 Mengirimkan data pembacaan sensor ke Cloud...');
    client.publish(READINGS_TOPIC, payload, { qos: 0 }, (pubErr) => {
      if (pubErr) {
        console.error('❌ Gagal publish data:', pubErr);
        client.end();
        process.exit(1);
      }
      console.log('✅ Data berhasil dipublish!');
      console.log('⏳ Menunggu hasil inferensi AI dari Cloud...\n');
    });
  });
});

// 3. Tangkap hasil prediksi yang dipublish oleh backend
client.on('message', (topic, message) => {
  if (topic === PREDICTIONS_TOPIC) {
    try {
      const pred = JSON.parse(message.toString());
      console.log('====================================================');
      console.log('🎉 HASIL PREDIKSI AI DITERIMA DARI CLOUD!');
      console.log('====================================================');
      
      const glucose = Number(pred.glucose_estimate).toFixed(1);
      const category = pred.clinical_category || 'Unknown';
      const confidence = (Number(pred.confidence_score) * 100).toFixed(0);

      // Visualisasi Layar OLED SH1106 (128x64)
      console.log('\n┌────────────────────────────────────────┐');
      console.log('│         GLICOVIA OLED DISPLAY          │');
      console.log('├────────────────────────────────────────┤');
      console.log(`│  Glukosa Darah : ${glucose.padEnd(6)} mg/dL        │`);
      console.log(`│  Status        : ${category.padEnd(14)}        │`);
      console.log(`│  Tingkat Akurasi: ${confidence}%                │`);
      console.log('│                                        │');
      console.log('│  [ Hasil tersinkronisasi ke Web ]     │');
      console.log('└────────────────────────────────────────┘\n');

      console.log('Payload Mentah:', JSON.stringify(pred, null, 2));
      console.log('\n✅ Alur end-to-end berhasil selesai!');
      client.end();
      process.exit(0);
    } catch (e) {
      console.error('Gagal parsing payload prediksi:', e);
    }
  }
});

// Timeout jika cloud tidak merespon dalam 15 detik
setTimeout(() => {
  console.error('\n⏱️ Timeout: Tidak menerima respon prediksi dari cloud dalam 15 detik.');
  client.end();
  process.exit(1);
}, 15000);
