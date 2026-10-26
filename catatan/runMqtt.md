```
```


Terminal 1 — pantau balasan:
mosquitto_sub -h broker.hivemq.com -t 'glicovia/devices/GLICO-01/predictions' -v

Terminal 2 — kirim pembacaan (pilih salah satu):

# A. Format firmware lama (satuan riil, tanpa units), nilai dalam rentang data latih → ≈ 88 Normal

```
mosquitto_pub -h broker.hivemq.com -t 'glicovia/devices/GLICO-01/readings'
  -m '{"device_code":"GLICO-01","ph":4.65,"fructosamine":220,"salivary_glucose":7.16}'
```

mosquitto_pub -h broker.hivemq.com -t 'glicovia/devices/GLICO-01/readings'
  -m '{"device_code":"GLICO-01","ph":4.65,"fructosamine":220,"salivary_glucose":7.16}'

# B. Format main.cpp (volt + units), sesi 88 → ≈ 89 Normal

mosquitto_pub -h broker.hivemq.com -t 'glicovia/devices/GLICO-01/readings' 
  -m '{"device_code":"GLICO-01","ph":null,"fructosamine":0.5262,"salivary_glucose":0.005,"units":{"ph":"none","fructosamine":"V","salivary_glucose":"V"},"raw":{"v_ph":0.0548,"v_fru":0.5262,"v_glu":0.005,"v_mid":0.913,"i_glu_nA":7158},"quality":{"saturated":true},"fw_version":"0.3.0"}'

# C. Sama dengan B, sesi 148 → ≈ 146 Diabetes

mosquitto_pub -h broker.hivemq.com -t 'glicovia/devices/GLICO-01/readings' 
  -m '{"device_code":"GLICO-01","ph":null,"fructosamine":0.0003,"salivary_glucose":0.0028,"units":{"ph":"none","fructosamine":"V","salivary_glucose":"V"},"raw":{"v_ph":0.0216,"v_fru":0.0003,"v_glu":0.0028,"v_mid":0.912,"i_glu_nA":7165},"quality":{"saturated":true},"fw_version":"0.3.0"}'

Pembuktiannya dari database (bukan dari terminal subscriber):
docker exec pkmglico-postgres psql -U postgres -d pkmglico -c "select r.received_at, r.ph, r.fructosamine, p.glucose_estimate, p.clinical_category, p.inference_status from sensor_readings r left join prediction_results p on p.sensor_reading_id=r.id order by r.received_at desc limit 5;"
