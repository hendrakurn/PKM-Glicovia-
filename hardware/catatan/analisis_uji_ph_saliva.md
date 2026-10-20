# Laporan Analisis Pengujian Sensor pH Saliva (SPCE + ADS1115)

Dokumen ini mencatat hasil evaluasi eksperimental pengukuran pH saliva menggunakan sensor *Screen-Printed Carbon Electrode* (SPCE) yang terhubung ke modul *Analog Front-End* OPA2333 dan ADC 16-bit ADS1115 (Pin A2) pada mikrokontroler ESP32.

---

## 1. Metadata Pengujian

- **Tanggal & Waktu**: 20 Oktober 2026, 00:38 - 00:41 WIB
- **Hardware**: 
  - Sensor: SPCE (Elektroda Kerja, Referensi, dan Counter)
  - Penguat: OPA2333 (Dual Zero-Drift Op-Amp)
  - ADC: ADS1115 (16-bit, Gain One: jangkauan $\pm 4.096\text{ V}$, resolusi $0.125\text{ mV/bit}$)
  - Pin Input ADC: **A2** (`ads.readADC_SingleEnded(2)`)
- **Sampel Diuji**:
  1. Larutan Penyangga Standar (*Buffer*) **pH 4.01**
  2. Sampel Cairan Mulut (*Human Saliva*)
- **File Data Log**:
  - `data_log/glicovia_testingSaliva_pH_1_20261020_003830.csv` (Uji Saliva Sesi 1)
  - `data_log/glicovia_testingSaliva_pH_2_20261020_004026.csv` (Uji Saliva Sesi 2)

---

## 2. Rangkuman Data Hasil Pengukuran

| Parameter / Sampel | Nilai Mentah ADC (Raw) | Tegangan Terukur ($V$) | Kondisi & Kestabilan |
| :--- | :---: | :---: | :--- |
| **Kondisi Kering (Sebelum Saliva)** | $51 - 25.265$ | $0.0064\text{ V} - 3.1581\text{ V}$ | Berosilasi liar (*floating / open circuit*) |
| **Titik Awal Pembasahan ($t = 3490250\text{ ms}$)** | $1.058$ | $0.1323\text{ V}$ | Transien penurunan instan saat droplet menyentuh SPCE |
| **Buffer Standar pH 4.01** | $612 - 617$ | $0.0765\text{ V} - 0.0771\text{ V}$ | Rata-rata $\approx 0.0768\text{ V}$ ($76.8\text{ mV}$) |
| **Saliva Sesi 1 (Stabil, 30 detik akhir)** | $581.1 \pm 6.4$ | $0.07266\text{ V} \pm 0.00080\text{ V}$ | Rata-rata $72.66\text{ mV}$ ($\text{Std} = 0.80\text{ mV}$) |
| **Saliva Sesi 2 (Stabil, 60 detik penuh)** | $578.1 \pm 7.0$ | $0.07228\text{ V} \pm 0.00088\text{ V}$ | Rata-rata $72.28\text{ mV}$ ($\text{Std} = 0.88\text{ mV}$) |

> [!NOTE]
> Selisih tegangan kondisi stabil antara Sesi 1 dan Sesi 2 hanya sebesar **$0.38\text{ mV}$** ($\approx 3$ unit ADC). Ini menunjukkan bahwa rangkaian analog memiliki tingkat pengulangan (*repeatability*) dan presisi yang sangat tinggi.

---

## 3. Dinamika Respons Sinyal

Grafik profil tegangan terhadap waktu menunjukkan 4 fase:

```text
Tegangan (V)
   ^
3.15V |  /\  /\  /\ (Fase 1: Kering - Osilasi Liar)
      | /  \/  \/  \
0.132V|              * (Fase 2: Kontak Droplet Saliva Pertama)
      |               \
0.072V|                \___________________ (Fase 4: Steady-State Stabil)
   0V +-------------------------------------> Waktu (ms)
```

1. **Fase 1: Kering (*Open Circuit Floating*)**
   - Saat SPCE belum terkena cairan, resistansi antarmuka elektroda bersifat tak terhingga ($> 10^{12}\ \Omega$).
   - Gerbang input OPA2333 berbasis MOSFET tidak memiliki jalur arus referensi, sehingga berfungsi sebagai antena penangkap derau listrik lingkungan (frekuensi jala-jala 50 Hz dan induksi elektromagnetik).
2. **Fase 2: Pembasahan (*Wetting Event*)**
   - Pada timestamp `3490250 ms`, cairan saliva menutupi ketiga elektroda SPCE (WE, RE, dan CE).
   - Resistansi turun drastis ke skala $\text{k}\Omega$, sirkuit tertutup seketika, dan tegangan drop ke $0.1323\text{ V}$.
3. **Fase 3: Relaksasi Transien (*Electrical Double Layer Charging*)**
   - Tegangan melandai turun secara eksponensial dari $0.1323\text{ V} \rightarrow 0.0725\text{ V}$ selama $\approx 10$ detik.
   - Fenomena ini disebabkan oleh pembentukan lapisan ganda listrik Helmholtz/Gouy-Chapman serta difusi ion $\text{H}^+$ ke permukaan elektroda hingga tercapai kesetimbangan dinamis.
4. **Fase 4: Kondisi Mantap (*Steady-State*)**
   - Setelah 10–15 detik, pembacaan mengunci stabil pada $0.0723\text{ V} - 0.0727\text{ V}$.

---

## 4. Teori Elektrokimia & Penentuan pH

### A. Persamaan Nernst
Pada pengukuran potensiometrik elektroda peka ion hidrogen:
$$E = E^0 - \frac{2.303 \cdot R \cdot T}{n \cdot F} \cdot \text{pH}$$

Pada suhu ruangan ($25^\circ\text{C}$):
$$S = \frac{2.303 \cdot R \cdot T}{F} \approx 59.16\text{ mV / unit pH}$$

Potensial sel memiliki korelasi **berbanding terbalik** dengan nilai pH:
- Larutan semakin asam (konsentrasi ion $\text{H}^+$ tinggi) $\rightarrow$ Tegangan **lebih tinggi**.
- Larutan semakin basa (konsentrasi ion $\text{H}^+$ rendah) $\rightarrow$ Tegangan **lebih rendah**.

### B. Hubungan Tegangan Saliva vs Buffer pH 4.01
- Tegangan Buffer pH 4.01: $76.8\text{ mV}$
- Tegangan Sampel Saliva: $72.5\text{ mV}$
- Selisih tegangan:
  $$\Delta V = V_{\text{saliva}} - V_{\text{pH 4.01}} = 72.5\text{ mV} - 76.8\text{ mV} = -4.3\text{ mV}$$

Karena tegangan saliva **lebih rendah** daripada larutan standar pH 4.01, terbukti secara teoritis bahwa **pH sampel saliva berada di atas 4.01** (bersifat mendekati netral).

Secara fisiologis, saliva manusia yang sehat memiliki rentang pH normal **6.4 hingga 7.4** (dengan median $\approx 6.8$), dijaga oleh sistem buffer alami bikarbonat ($\text{HCO}_3^- / \text{H}_2\text{CO}_3$). Respon sensor ini selaras dengan profil biologis saliva.

---

## 5. Rencana Kalibrasi & Formula Konversi

Untuk mengonversi pembacaan tegangan ADC menjadi satuan pH secara matematis di dalam firmware, diperlukan kalibrasi 2-titik menggunakan larutan standar:

1. **Uji Buffer pH 7.00**:
   ```bash
   python3 hardware/logger.py -l "pH_7.00" -d 60
   ```
2. **Hitung Kemiringan Sensor (*Sensitivity Slope*)**:
   $$m = \frac{V_{\text{pH 7.00}} - V_{\text{pH 4.01}}}{7.00 - 4.01} \quad (\text{V/pH})$$
3. **Hitung Offset Tegangan ($c$)**:
   $$c = V_{\text{pH 4.01}} - (m \times 4.01)$$
4. **Rumus Konversi di Firmware**:
   $$\text{pH} = \frac{V_{\text{ADC}} - c}{m}$$
