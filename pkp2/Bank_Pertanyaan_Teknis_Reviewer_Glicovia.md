# Bank Pertanyaan Teknis Reviewer PKP/Monev Glicovia

Tanggal telaah: 14 September 2026. Isi: 75 pertanyaan dalam lima kategori, 10 pertanyaan paling berbahaya, dan red flag jawaban. Ditulis untuk latihan lisan berbasis bukti, bukan materi promosi.

## Cara Membaca Status Bukti

- **Ada di kode/artefak:** ditemukan pada workspace; belum berarti pernah diuji pada alat fisik, server aktif, atau manusia.
- **Klaim dokumen:** tertulis pada laporan/Google Doc; perlu data mentah dan catatan pengujian sebelum dinyatakan sebagai capaian terverifikasi.
- **Rencana:** mitigasi atau pengujian yang masih harus dilakukan. Jangan dibacakan sebagai pekerjaan yang sudah selesai.
- **Belum terverifikasi:** tidak dibuktikan oleh sumber yang ditelaah. Ini tidak memastikan artefaknya tidak ada di tempat lain.

Jawaban aman berarti jujur tentang batas bukti. Jika reviewer meminta hasil yang belum tersedia, nyatakan belum tersedia dan jelaskan cara membuktikannya. Jangan mengarang jumlah peserta, izin etik, hasil kalibrasi, atau performa klinis.

## Temuan yang Harus Diselaraskan Sebelum Presentasi

1. Jalur `ml_pipeline` memakai SVR untuk target `bg_mgdl_reference`, lalu menerjemahkan prediksi ke kategori. Narasi SVM klasifikasi langsung perlu diperjelas. Folder `ml_pipeline_git` masih memiliki generator berbasis viskositas; jangan mencampur versinya. [K1](#k1-ml-aktif), [K3](#k3-versi-dan-biomarker)
2. Fitur aktif adalah `glucose_saliva`, `ph_value`, dan `fructosamine_umol_l`. Fructosamine dan viskositas adalah besaran berbeda; penggantian nama kolom tidak membuat keduanya setara. [K1](#k1-ml-aktif), [K3](#k3-versi-dan-biomarker)
3. Metadata data dummy mencatat 150 baris: 60 normal, 52 prediabetes, 38 diabetes. Laporan preprocessing terbaru menyisakan 98 train dan 25 test; distribusi kelas berubah. Baris sintetis bukan peserta manusia. [K2](#k2-artefak-evaluasi)
4. Evaluasi bertanggal 12 September 2026 melaporkan R2 0,9718, RMSE 9,1546 mg/dL, MAE 6,9112 mg/dL; `classification_metrics` kosong. `clinical_status: PASS` merupakan keputusan ambang perangkat lunak, bukan kelulusan klinis. Angka ini dibaca dari artefak, tidak direproduksi pada telaah ini. [K2](#k2-artefak-evaluasi)
5. Laporan perbandingan delapan model bertanggal 18 Agustus 2026 menempatkan Ridge pada peringkat pertama berdasarkan test R2. Ini eksperimen berbeda dari evaluasi September; jangan membandingkan angka lintas run sebagai head-to-head. [K2](#k2-artefak-evaluasi)
6. Imputasi, pemeriksaan varians, dan penghapusan outlier dilakukan sebelum train/test split. Scaler di-fit pada train, tetapi data yang sudah diskalakan masuk ke pencarian CV. Ada risiko informasi holdout/fold memengaruhi preprocessing; evaluasi perlu diulang dengan pemisahan yang benar. [K1](#k1-ml-aktif), [S5](#s5-preprocessing)
7. `confidence` pada inference dihitung dari variasi prediksi setelah jitter input, dengan batas bawah `confidence_level - 0.2`. Pada default 0,95, nilainya minimal 0,75. Ini bukan probabilitas diagnosis benar. [K1](#k1-ml-aktif)
8. Firmware memakai konversi `glucose = volts0 * 200`, `pH = 7 + volts1 * -5`, dan `fructo = volts2 * 500`. Konstanta ini belum disertai bukti kalibrasi eksperimental dalam sumber yang ditelaah. [K4](#k4-hardware)
9. Rute prediksi global `/api/predictions` dan `/api/predictions/latest` tidak dipasangi `authMiddleware` pada router; middleware dipasang pada `/me`. Tidak terlihat autentikasi global pada `app.ts`. Ini temuan kode; keterpaparan deployment belum diuji. [K6](#k6-api-dan-akses)
10. Website memiliki klien API serta sumber data statis `app/web/src/lib/data.ts`. Angka contoh, status koneksi, dan metrik di sumber statis tidak membuktikan keadaan alat. [K7](#k7-website)
11. Laporan PKP menyebut fabrikasi dan integrasi penuh masih tertunda, pengujian komponen, mock hardware, serta data sintetis. Angka seperti inferensi 42 ms atau waktu pemeriksaan <=5 menit perlu log/protokol; jangan disamakan dengan hasil uji sistem penuh. [K8](#k8-dokumen-proyek)
12. Google Doc menyebut OGTT sebagai glukometer. Koreksi: OGTT adalah prosedur uji toleransi glukosa; hasil plasma dua jam dan konteks pengujiannya berbeda dari pembacaan glukometer biasa. Acuan mutu laboratorium dan studi IVD juga tidak otomatis memberikan sertifikasi produk. [D1](#d1-google-doc), [S1](#s1-kriteria-klinis), [S2](#s2-pembanding), [S3](#s3-iso-15189), [S4](#s4-iso-20916)

## 1. Machine Learning

### ML-01. Model kalian sebenarnya SVM klasifikasi atau SVR regresi?

- **Maksud reviewer:** menguji kesesuaian presentasi dengan estimator dan target yang benar-benar dipakai.
- **Jawaban singkat aman:** Jalur aktif memakai SVR untuk estimasi nilai referensi glukosa darah, kemudian menerapkan aturan kategori.
- **Jawaban teknis:** `train_svm.py` membangun `sklearn.svm.SVR`; nama file tidak menentukan jenis model. Target preprocessing adalah `bg_mgdl_reference`. Kategori keluaran merupakan turunan regresi, sehingga evaluasi harus mencakup galat numerik dan kesalahan kategori. Dokumentasi klasifikasi langsung perlu diselaraskan.
- **Bukti:** Ada: [K1](#k1-ml-aktif), konfigurasi target dan fungsi `_build_svr`/`_mgdl_to_class`. Siapkan: identitas artefak yang benar-benar dimuat saat demo.
- **Risiko salah jawab:** reviewer menemukan narasi algoritma yang tidak cocok dengan implementasi.
- **Follow-up:** Mengapa memilih regresi jika tujuan utamanya kategori risiko?

### ML-02. Data latih berasal dari pasien atau hasil generator?

- **Maksud reviewer:** memeriksa apakah angka performa memiliki dasar biologis atau hanya simulasi.
- **Jawaban singkat aman:** Artefak yang ditelaah menggunakan data sintetis untuk pengembangan pipeline; performa pada manusia belum terbukti dari artefak ini.
- **Jawaban teknis:** Metadata mencatat 150 baris hasil generator beserta seed dan distribusi kelas. Relasi fitur-target dalam generator adalah asumsi pemodelan, sehingga keberhasilan mempelajarinya tidak memvalidasi hubungan saliva-darah. Rencana berikutnya memerlukan pasangan saliva dan pemeriksaan referensi dengan provenance per subjek.
- **Bukti:** Ada: [K2](#k2-artefak-evaluasi), `metadata.json`; [K1](#k1-ml-aktif), generator. Siapkan: manifest data nyata jika sudah ada, terpisah dari dummy.
- **Risiko salah jawab:** 150 baris diklaim sebagai 150 responden dan merusak kredibilitas hasil.
- **Follow-up:** Berapa peserta unik dengan data darah-saliva berpasangan yang dapat diaudit?

### ML-03. Apa arti R2 0,9718? Apakah akurasi alat 97,18%?

- **Maksud reviewer:** menguji pemahaman metrik dan batas generalisasi.
- **Jawaban singkat aman:** R2 adalah metrik regresi pada set uji artefak tersebut; bukan persentase diagnosis benar.
- **Jawaban teknis:** Laporan September mencatat RMSE sekitar 9,15 dan MAE 6,91 mg/dL terhadap target dataset. Nilai itu harus dibaca bersama asal data sintetis, ukuran test 25 baris, dan risiko preprocessing. `classification_metrics` kosong pada laporan evaluasi tersebut; sensitivitas prediabetes tidak dapat disimpulkan dari R2.
- **Bukti:** Ada: [K2](#k2-artefak-evaluasi), `evaluation_report.json` dan laporan preprocessing. Siapkan: pasangan prediksi-target dan analisis per kelas.
- **Risiko salah jawab:** angka statistik berubah menjadi klaim medis yang tidak didukung.
- **Follow-up:** Berapa false negative prediabetes pada subjek independen?

### ML-04. Mengapa SVR dipilih jika Ridge lebih baik dalam laporan kalian?

- **Maksud reviewer:** menguji apakah pemilihan model berbasis bukti atau mengikuti judul proposal.
- **Jawaban singkat aman:** SVR masih kandidat prototipe. Laporan perbandingan memang menempatkan Ridge lebih tinggi pada test set eksperimen itu.
- **Jawaban teknis:** Laporan Agustus membandingkan delapan model dan memberi peringkat berdasarkan test R2. Jangan mengklaim SVR paling unggul atau membandingkannya langsung dengan run September. Rencana pemilihan final menggunakan validasi pengembangan yang konsisten, biaya kesalahan screening, serta test akhir yang tidak dipakai memilih model.
- **Bukti:** Ada: [K2](#k2-artefak-evaluasi), `comparison_report.json`, aturan ranking, parameter, dan hasil tiap model.
- **Risiko salah jawab:** reviewer menunjukkan baseline sederhana yang mengalahkan klaim keunggulan AI.
- **Follow-up:** Apakah tim bersedia mengganti model jika baseline lebih andal?

### ML-05. Apakah preprocessing kalian bocor ke data test?

- **Maksud reviewer:** memeriksa validitas estimasi performa.
- **Jawaban singkat aman:** Ada risiko leakage: pembersihan data dilakukan sebelum split. Evaluasi perlu diulang sebelum menjadi dasar klaim kuat.
- **Jawaban teknis:** Imputasi dan batas IQR yang dihitung dari seluruh data dapat membawa informasi holdout. Scaler memang di-fit pada train, tetapi di luar fold CV. Mitigasi: split lebih dahulu, fit transformasi hanya pada bagian training setiap fold, dan evaluasi test yang dikunci. Ini rekomendasi perbaikan, belum perubahan yang dilakukan pada telaah ini. [S5](#s5-preprocessing)
- **Bukti:** Ada: [K1](#k1-ml-aktif), urutan `preprocess` dan input `GridSearchCV`. Siapkan: evaluasi ulang dengan pipeline per fold.
- **Risiko salah jawab:** menyatakan bebas leakage padahal kode menunjukkan jalur informasi yang bermasalah.
- **Follow-up:** Seberapa berubah performa setelah leakage ditangani?

### ML-06. Bagaimana mencegah sampel satu orang masuk train dan test?

- **Maksud reviewer:** mencari kebocoran identitas dan pengulangan biologis.
- **Jawaban singkat aman:** Pemisahan per subjek wajib direncanakan untuk data manusia; split baris sintetis belum membuktikan hal itu.
- **Jawaban teknis:** Beberapa pembacaan dari orang atau kunjungan yang sama dapat sangat mirip. Rencana: simpan ID subjek dan kunjungan, kelompokkan pembagian berdasarkan subjek, lalu pertimbangkan holdout waktu atau lokasi. Jumlah pembacaan tidak boleh dipakai sebagai jumlah peserta independen. Bukti grouping harus terlihat pada manifest split, bukan hanya seed.
- **Bukti:** Ada: [K1](#k1-ml-aktif), konfigurasi split. Siapkan: manifest subject-wise split dan pemeriksaan irisan ID kosong.
- **Risiko salah jawab:** model mengenali pola peserta lama tetapi dilaporkan mampu menghadapi peserta baru.
- **Follow-up:** Apa unit analisis kalian: orang, kunjungan, sampel, atau paket MQTT?

### ML-07. Mengapa membuang outlier? Apakah kasus diabetes justru terbuang?

- **Maksud reviewer:** menguji selection bias dan hilangnya kasus sulit.
- **Jawaban singkat aman:** Penghapusan IQR sekarang merupakan aturan komputasi; belum membuktikan setiap nilai yang dibuang adalah kesalahan sensor.
- **Jawaban teknis:** Dari 150 baris tersisa 123, dan proporsi kelas diabetes turun dibanding metadata awal. Ini alasan untuk audit, bukan bukti sebab klinis. Rencana: bedakan kegagalan pengukuran dari nilai biologis ekstrem, laporkan eksklusi per kelas, dan bandingkan analisis dengan serta tanpa eksklusi.
- **Bukti:** Ada: [K2](#k2-artefak-evaluasi), jumlah outlier dan rasio kelas. Siapkan: daftar baris dikeluarkan beserta alasan yang ditetapkan sebelum evaluasi.
- **Risiko salah jawab:** performa tampak baik karena kasus paling relevan dihilangkan.
- **Follow-up:** Berapa kasus diabetes tersisa pada test, dan cukupkah untuk menilai sensitivitas?

### ML-08. Apa kontribusi pH dan fructosamine dibanding glukosa saja?

- **Maksud reviewer:** menguji manfaat nyata multimarker.
- **Jawaban singkat aman:** Tiga fitur sudah digunakan dalam kode; peningkatan manfaat tiap biomarker belum dapat disimpulkan dari keberadaan fitur.
- **Jawaban teknis:** Rencana pembuktian menggunakan ablation: glukosa saja, kombinasi dua fitur, lalu tiga fitur pada split yang sama. Bandingkan galat dan sensitivitas pada target screening, dengan ketidakpastian. Hubungan yang sengaja dibuat generator dapat membuat tambahan fitur tampak membantu; hasil tersebut masih perlu diuji pada data nyata.
- **Bukti:** Ada: [K1](#k1-ml-aktif), `FEATURE_COLUMNS`. Siapkan: laporan ablation dan data pasangan biomarker-referensi.
- **Risiko salah jawab:** klaim tiga biomarker pasti lebih akurat tanpa pembanding terkendali.
- **Follow-up:** Jika fructosamine tidak menambah manfaat, apakah sensor itu tetap diperlukan?

### ML-09. Apakah scaling saat inferensi sama dengan training?

- **Maksud reviewer:** mencari train-serving skew dan pertukaran urutan fitur.
- **Jawaban singkat aman:** Kode memiliki urutan fitur dan parameter scaler; konsistensinya harus dibuktikan untuk pasangan model-scaler yang dideploy.
- **Jawaban teknis:** Urutan aktif adalah glukosa saliva, pH, lalu fructosamine. Inference mendukung parameter scaler dan scaler dari objek model. Rencana uji kontrak harus mencakup skala, satuan, urutan, fitur hilang, serta pencegahan transformasi ganda bila model sudah membungkus preprocessing. Jangan refit scaler dari satu sampel baru.
- **Bukti:** Ada: [K1](#k1-ml-aktif), `FEATURE_ORDER`, `preprocess_sample`; [K2](#k2-artefak-evaluasi), `scaler_params.json`.
- **Risiko salah jawab:** input valid secara JSON menghasilkan prediksi salah karena representasi berbeda.
- **Follow-up:** Dapatkah satu sampel memberi hasil identik lewat CLI dan API?

### ML-10. Apakah confidence 95% berarti prediksi benar dengan peluang 95%?

- **Maksud reviewer:** menguji apakah ketidakpastian model diklaim secara sah.
- **Jawaban singkat aman:** Tidak. Skor sekarang mengukur kestabilan terhadap perturbasi input, bukan peluang diagnosis benar.
- **Jawaban teknis:** `_bootstrap_confidence` menambahkan jitter ke satu input dan mengukur variasi output model yang sama. Tidak ada resampling peserta atau pelatihan ulang model dalam fungsi tersebut. Skor juga memiliki floor 0,75 pada default. Rencana: definisikan ketidakpastian sesuai target, uji coverage/kalibrasi pada data independen, dan ubah label UI agar tidak menyesatkan.
- **Bukti:** Ada: [K1](#k1-ml-aktif), `_bootstrap_confidence`; [K7](#k7-website), tampilan prediksi.
- **Risiko salah jawab:** stabil terhadap noise disamakan dengan benar secara klinis.
- **Follow-up:** Bisakah model yang selalu salah tetap mempunyai confidence tinggi?

### ML-11. Apa yang terjadi pada sampel di luar distribusi training?

- **Maksud reviewer:** menguji perilaku di luar cakupan data.
- **Jawaban singkat aman:** Kemampuan mendeteksi semua sampel di luar distribusi belum terverifikasi. Nilai numerik saja tidak cukup untuk menyatakan input layak.
- **Jawaban teknis:** Rentang generator bukan rentang ukur sensor yang tervalidasi. Rencana: gunakan batas analitik sensor, pemeriksaan nilai non-finite, status kualitas, serta pengujian OOD pada kombinasi fitur yang tidak dikenal. Kasus gagal kualitas harus menghasilkan status tidak dapat dinilai atau permintaan ulang, bukan dipaksa menjadi normal.
- **Bukti:** Ada: [K1](#k1-ml-aktif), validasi inference; [K5](#k5-ingestion-dan-inference), quality flag. Siapkan: matriks kasus invalid/OOD.
- **Risiko salah jawab:** ekstrapolasi model menghasilkan rasa aman palsu.
- **Follow-up:** Siapa menetapkan batas valid, dan dari eksperimen apa?

### ML-12. Apakah lima fold sudah cukup membuktikan model tidak overfit?

- **Maksud reviewer:** memeriksa salah tafsir cross-validation.
- **Jawaban singkat aman:** Lima fold adalah metode evaluasi pengembangan, bukan jaminan bebas overfit atau validitas eksternal.
- **Jawaban teknis:** Pencarian `C`, `gamma`, dan `epsilon` menggunakan CV. Pemilihan parameter, penggunaan preprocessing, dan pemilihan model dapat menimbulkan optimism jika evaluasinya dipakai ulang. Rencana: pemisahan tuning dan evaluasi akhir, preprocessing per fold, serta validasi eksternal setelah model dikunci. Gap train-test kecil sendiri tidak membuktikan generalisasi klinis.
- **Bukti:** Ada: [K1](#k1-ml-aktif), `DEFAULT_CONFIG` dan `GridSearchCV`; [K2](#k2-artefak-evaluasi), hasil fold.
- **Risiko salah jawab:** menganggap nama metode statistik sebagai sertifikat keandalan.
- **Follow-up:** Apakah test pernah digunakan memilih model, parameter, atau batas kategori?

### ML-13. Mengapa batas kategori 100 dan 126 mg/dL?

- **Maksud reviewer:** menguji apakah target dan protokol darah sesuai aturan kategorisasi.
- **Jawaban singkat aman:** Kode memakai batas yang menyerupai konteks glukosa plasma puasa; penggunaannya harus sesuai definisi target dan belum memvalidasi diagnosis dari saliva.
- **Jawaban teknis:** Fungsi kategori memakai `<100`, `<126`, dan selebihnya. Protokol OGTT memiliki kriteria berbeda; nilai acak juga tidak boleh diperlakukan sebagai puasa. Rencana: tetapkan jenis referensi, kondisi puasa, rentang keluaran valid, serta penanganan nilai rendah atau tidak masuk akal sebelum pemetaan kategori. [S1](#s1-kriteria-klinis)
- **Bukti:** Ada: [K1](#k1-ml-aktif), `_mgdl_to_class` dan `_category_from_mgdl`. Siapkan: data dictionary target dan aturan kategori yang disetujui klinisi.
- **Risiko salah jawab:** salah label karena ambang tepat diterapkan pada konteks pemeriksaan yang salah.
- **Follow-up:** Bagaimana menangani prediksi sangat rendah yang sekarang masuk kelas normal?

### ML-14. Metrik apa yang paling penting untuk deteksi prediabetes?

- **Maksud reviewer:** melihat apakah tujuan klinis mengarahkan evaluasi model.
- **Jawaban singkat aman:** Evaluasi harus menilai kasus prediabetes yang terlewat, false positive, dan ketidakpastiannya; R2 saja tidak cukup.
- **Jawaban teknis:** Rencana: definisikan endpoint, misalnya prediabetes versus non-prediabetes atau kebutuhan rujukan versus tidak, sebelum menghitung confusion matrix. Laporkan sensitivitas, spesifisitas, PPV/NPV pada populasi relevan, serta interval kepercayaan. Untuk output regresi, tetap laporkan MAE/RMSE dan galat dekat batas keputusan. Target ambang ditetapkan bersama pembimbing klinis.
- **Bukti:** Ada: [K2](#k2-artefak-evaluasi), keterbatasan laporan metrik saat ini. Siapkan: rencana analisis dan matriks prediksi-label independen.
- **Risiko salah jawab:** akurasi agregat menutupi kegagalan pada kelas sasaran.
- **Follow-up:** Bagaimana diabetes diperlakukan ketika endpoint utama adalah prediabetes?

### ML-15. Dapatkah reviewer mereproduksi hasil model kalian?

- **Maksud reviewer:** menguji ketertelusuran eksperimen dan model yang ditampilkan.
- **Jawaban singkat aman:** Kode dan artefak tersedia; reproduksi penuh perlu mengunci data, konfigurasi, environment, model, dan scaler dari run yang sama.
- **Jawaban teknis:** Seed membantu, tetapi tidak menjamin semua run identik jika dataset atau dependensi berubah. Ada beberapa folder/run ML, serta laporan yang berubah di worktree. Rencana paket bukti: hash dataset dan model, commit, versi dependensi, manifest split, parameter, log, dan perintah reproduksi tanpa menimpa artefak acuan.
- **Bukti:** Ada: [K1](#k1-ml-aktif), pipeline; [K2](#k2-artefak-evaluasi), log eksperimen dan laporan. Siapkan: manifest rilis demo.
- **Risiko salah jawab:** model demo, tabel laporan, dan file training ternyata berasal dari versi berbeda.
- **Follow-up:** Hash model mana yang menghasilkan prediksi yang sedang ditunjukkan?

## 2. Website/Backend/IoT

### WEB-01. Jelaskan perjalanan satu sampel sampai muncul di dashboard.

- **Maksud reviewer:** menguji pemahaman integrasi lintas anggota tim.
- **Jawaban singkat aman:** Firmware mengirim MQTT, backend menyimpan reading, memicu inference Python, menyimpan prediksi, lalu website mengambil hasil melalui API.
- **Jawaban teknis:** Handler memetakan perangkat dan assignment aktif, menyimpan biomarker serta payload, kemudian memicu inference asinkron. Service memetakan nama fitur ke kontrak ML. Kode menunjukkan jalur integrasi; keberhasilan eksperimen fisik harus dibuktikan dengan ID reading yang sama pada payload, database, inference, dan UI.
- **Bukti:** Ada: [K4](#k4-hardware), [K5](#k5-ingestion-dan-inference), [K7](#k7-website). Siapkan: log end-to-end satu sampel.
- **Risiko salah jawab:** demo komponen diklaim sebagai keberhasilan sistem terintegrasi.
- **Follow-up:** Tunjukkan ID sampel yang sama pada empat lapisan tersebut.

### WEB-02. Apakah semua halaman memakai data alat sungguhan?

- **Maksud reviewer:** memisahkan demo visual dari telemetry nyata.
- **Jawaban singkat aman:** Workspace memiliki klien API dan data statis. Sumber data harus diperiksa per halaman.
- **Jawaban teknis:** `lib/data.ts` memuat contoh readings, subjek, metrik, dan status perangkat. Komponen lain memiliki pemanggilan API. Rencana pembuktian: tandai sumber mock/manual/MQTT, cocokkan respons jaringan dengan database. Data statis tidak membuktikan semua halaman mock, tetapi angka contoh juga tidak membuktikan keadaan alat.
- **Bukti:** Ada: [K7](#k7-website), data statis dan API client. Siapkan: rekaman Network dan asal setiap angka demo.
- **Risiko salah jawab:** contoh UI dipresentasikan sebagai hasil pengukuran manusia.
- **Follow-up:** Halaman mana tetap menampilkan angka saat backend dimatikan?

### WEB-03. Apakah pengguna lain bisa melihat prediksi milik saya?

- **Maksud reviewer:** menguji kerahasiaan dan otorisasi objek.
- **Jawaban singkat aman:** Rute `/me` memiliki autentikasi, tetapi rute prediksi global yang ditelaah belum memiliki middleware tersebut.
- **Jawaban teknis:** Router melindungi `/me`, sementara `/` dan `/latest` dipasang tanpa `authMiddleware`; `app.ts` tidak menambah autentikasi global. Keterpaparan deployment belum diuji. Mitigasi sebelum penggunaan data manusia: tetapkan hak operator/admin, scope query berdasarkan hak subjek, dan uji akses tanpa token serta akses silang akun.
- **Bukti:** Ada: [K6](#k6-api-dan-akses), router dan app. Siapkan: matriks role-endpoint dan hasil uji otorisasi.
- **Risiko salah jawab:** menyebut seluruh API aman karena halaman login tersedia.
- **Follow-up:** Apa respons endpoint global ketika dipanggil tanpa token?

### WEB-04. Apa yang mencegah orang mengirim nilai palsu ke MQTT?

- **Maksud reviewer:** memeriksa autentisitas sumber data.
- **Jawaban singkat aman:** Firmware demo memakai broker publik dan identitas perangkat dalam pesan; itu belum cukup membuktikan pengirim sah.
- **Jawaban teknis:** `device_code` dan topic bisa ditiru. Rencana: broker terkelola, TLS, kredensial per perangkat, ACL topic, rotasi kredensial, serta uji publisher tidak sah. Validasi JSON tidak menggantikan autentikasi perangkat. Kontrol ini belum boleh disebut aktif tanpa konfigurasi dan log pembuktian.
- **Bukti:** Ada: [K4](#k4-hardware), broker/publish; [K5](#k5-ingestion-dan-inference), resolusi device. Siapkan: hasil uji spoofing pada lingkungan sendiri.
- **Risiko salah jawab:** data palsu diterima sebagai pengukuran sah.
- **Follow-up:** Bisakah laptop lain mem-publish sebagai `GLICO-01`?

### WEB-05. Bagaimana jika pesan MQTT masuk dua kali?

- **Maksud reviewer:** menguji idempotensi dan integritas jumlah pemeriksaan.
- **Jawaban singkat aman:** Deduplikasi end-to-end belum terbukti dari jalur yang ditelaah; pengiriman ulang perlu diuji.
- **Jawaban teknis:** Pencegahan prediksi ganda untuk reading-model berbeda dari pencegahan dua reading dari satu pengukuran. Rencana: ID pengukuran dari perangkat, sequence number, dan constraint unik yang sesuai. Uji replay setelah reconnect dan pastikan tidak menambah jumlah pemeriksaan atau mengubah statistik subjek.
- **Bukti:** Ada: [K5](#k5-ingestion-dan-inference), handler dan repository. Siapkan: skema ID dan uji publish ganda.
- **Risiko salah jawab:** satu sampel dihitung sebagai banyak pengamatan independen.
- **Follow-up:** Apa pembeda pengukuran baru dengan pengiriman ulang?

### WEB-06. Apa yang terjadi jika ML mati setelah reading tersimpan?

- **Maksud reviewer:** menilai konsistensi dan pemulihan kegagalan.
- **Jawaban singkat aman:** Reading disimpan sebelum inference asinkron. Reading tersimpan tidak berarti prediksi berhasil.
- **Jawaban teknis:** Recovery perlu dibuktikan. Rencana: status pending/failed/succeeded, retry terbatas, dan rekonsiliasi reading tanpa prediksi. UI harus menampilkan status proses/gagal, bukan prediksi lama seolah milik reading baru. Durable queue belum terverifikasi dari sumber yang ditelaah.
- **Bukti:** Ada: [K5](#k5-ingestion-dan-inference), trigger asinkron. Siapkan: log mematikan ML dan menjalankan pemulihan.
- **Risiko salah jawab:** hasil lama menempel pada pemeriksaan baru atau kegagalan hilang diam-diam.
- **Follow-up:** Setelah server restart, siapa memproses reading yang tertinggal?

### WEB-07. Apa yang terjadi saat Wi-Fi atau broker terputus?

- **Maksud reviewer:** menguji kesiapan lapangan.
- **Jawaban singkat aman:** Firmware memiliki reconnect, tetapi reconnect MQTT bersifat blocking; layanan offline penuh belum terbukti.
- **Jawaban teknis:** `reconnectMQTT()` menunggu dalam `while` dengan `delay(5000)` sebelum pembacaan berikutnya. Ini dapat menahan pembacaan dan pembaruan layar. Rencana: state machine nonblocking, indikator koneksi, timeout, dan buffering jika dibutuhkan. Ukur kehilangan paket, jangan menganggap reconnect menjamin pemulihan seluruh data.
- **Bukti:** Ada: [K4](#k4-hardware), reconnect dan loop. Siapkan: uji putus jaringan saat pemeriksaan.
- **Risiko salah jawab:** menjanjikan alat tetap bekerja ketika loop tertahan broker.
- **Follow-up:** Berapa sampel hilang selama putus satu menit?

### WEB-08. Bagaimana memastikan data masuk ke subjek yang benar?

- **Maksud reviewer:** mencari salah atribusi akibat pairing dan pesan terlambat.
- **Jawaban singkat aman:** Backend memakai assignment perangkat; ketepatan saat pergantian subjek perlu diuji.
- **Jawaban teknis:** Assignment aktif saat pesan diterima dapat berbeda dari assignment saat pengambilan sampel. Rencana: ikat pengukuran ke sesi dan subjek yang diverifikasi, catat waktu pengambilan, serta uji paket lama setelah unpair/pair. Operator harus memverifikasi identitas sebelum akuisisi tanpa menaruh nama subjek di topic publik.
- **Bukti:** Ada: [K5](#k5-ingestion-dan-inference), resolver assignment; [K6](#k6-api-dan-akses), pairing. Siapkan: uji pergantian dua subjek.
- **Risiko salah jawab:** hasil seseorang tampil pada akun orang lain.
- **Follow-up:** Ke siapa paket tertunda dikaitkan setelah perangkat dipindahkan?

### WEB-09. Mengapa nama fitur berbeda pada firmware, DB, dan ML?

- **Maksud reviewer:** menguji kontrak data dan satuan.
- **Jawaban singkat aman:** Backend melakukan mapping eksplisit; kesetaraan makna dan satuannya tetap harus dijaga.
- **Jawaban teknis:** `salivary_glucose` menjadi `glucose_saliva`, `ph` menjadi `ph_value`, dan `fructosamine` menjadi `fructosamine_umol_l`. Mapping nama tidak memverifikasi dimensi fisik. Rencana: schema version, data dictionary, rentang valid, dan uji kontrak dari firmware sampai inference; data viskositas tidak boleh sekadar diberi nama fructosamine.
- **Bukti:** Ada: [K5](#k5-ingestion-dan-inference), fungsi mapping; [K1](#k1-ml-aktif), urutan fitur.
- **Risiko salah jawab:** JSON valid membawa angka dengan unit yang salah.
- **Follow-up:** Di mana unit diperiksa, bukan sekadar dituliskan?

### WEB-10. Apakah quality flag lengkap berarti hasil berkualitas?

- **Maksud reviewer:** memisahkan kelengkapan data dari validitas pengukuran.
- **Jawaban singkat aman:** Flag kelengkapan membantu gating inference, tetapi belum membuktikan kalibrasi atau kelayakan sampel.
- **Jawaban teknis:** Service menolak reading berstatus `incomplete`. Rencana perlu memisahkan field hilang, nilai non-finite, saturasi ADC, drift, volume kurang, serta penyimpangan SOP. Simpan alasan terstruktur agar operator mengetahui kapan mengulang. Field hilang tidak boleh otomatis diganti nol dan dianggap pengukuran sah.
- **Bukti:** Ada: [K5](#k5-ingestion-dan-inference), quality flag dan pemeriksaan payload. Siapkan: matriks kasus gagal kualitas.
- **Risiko salah jawab:** kelengkapan tiga angka disamakan dengan kelayakan analitik.
- **Follow-up:** Apakah pH ekstrem tetapi numerik tetap memperoleh prediksi?

### WEB-11. Bagaimana melacak model yang menghasilkan prediksi lama?

- **Maksud reviewer:** menguji audit trail saat model diperbarui.
- **Jawaban singkat aman:** Ada penyimpanan versi model, tetapi identitas itu harus cocok dengan artefak yang benar-benar dipakai service.
- **Jawaban teknis:** Backend memiliki fallback metadata ketika informasi model tidak tersedia. Fallback tidak membuktikan provenance. Rencana: hash model dan scaler dari service, simpan bersama prediksi, tandai metadata tidak terverifikasi, dan pertahankan hasil historis saat inference ulang. Versi nominal saja tidak cukup.
- **Bukti:** Ada: [K5](#k5-ingestion-dan-inference), service inference dan repository model. Siapkan: jejak reading-prediction-model hash.
- **Risiko salah jawab:** dua artefak berbeda tercatat sebagai versi sama.
- **Follow-up:** Apa yang dicatat jika `/model-info` gagal tetapi `/predict` berhasil?

### WEB-12. Publish lima detik berarti hasil muncul dalam lima detik?

- **Maksud reviewer:** menguji definisi latensi.
- **Jawaban singkat aman:** Interval publish bukan jaminan latensi end-to-end atau waktu reaksi sensor.
- **Jawaban teknis:** Latensi mencakup akuisisi, reaksi, jaringan, penyimpanan, inference, dan refresh UI. Rencana: timestamp tiap tahap lalu ukur p50/p95 pada kondisi yang dinyatakan. Angka inferensi 42 ms dalam laporan perlu log; sekalipun terbukti, angka itu tidak mewakili waktu pemeriksaan lengkap.
- **Bukti:** Ada: [K4](#k4-hardware), timer; [K8](#k8-dokumen-proyek), target waktu. Siapkan: trace waktu pemeriksaan.
- **Risiko salah jawab:** hasil stopwatch reviewer bertentangan dengan klaim real-time.
- **Follow-up:** Waktu dihitung sejak saliva diteteskan atau JSON dikirim?

### WEB-13. Berapa perangkat yang mampu dilayani bersamaan?

- **Maksud reviewer:** meminta kapasitas terukur.
- **Jawaban singkat aman:** Kapasitas produksi belum terukur; penggunaan cloud dan PostgreSQL bukan bukti skalabilitas.
- **Jawaban teknis:** Beban mengikuti jumlah perangkat, interval publish, biaya inference, dan query UI. Seratus perangkat dengan interval lima detik memberi perkiraan 20 pesan/detik, bukan kapasitas teruji. Rencana: load test terisolasi, batas concurrency, backpressure, serta ukur latensi dan error sebelum menyatakan kapasitas.
- **Bukti:** Ada: [K5](#k5-ingestion-dan-inference), ingestion; [K6](#k6-api-dan-akses), repository. Siapkan: laporan load test.
- **Risiko salah jawab:** angka kapasitas dibuat tanpa pengujian.
- **Follow-up:** Apa bottleneck pertama saat beban dinaikkan?

### WEB-14. Bagaimana membuktikan histori tidak berubah diam-diam?

- **Maksud reviewer:** menguji integritas, koreksi, dan pemulihan data.
- **Jawaban singkat aman:** Reading dan raw payload membantu penelusuran; audit perubahan dan restore masih memerlukan bukti uji.
- **Jawaban teknis:** Rencana: provenance MQTT/manual/import, operator, alasan koreksi, waktu kejadian/penerimaan, dan versi hasil. Hindari overwrite tanpa jejak. Backup perlu diuji restore. Retensi dan minimisasi data pribadi harus tercantum dalam protokol; jangan menyebut tulisan pengaturan UI sebagai bukti mekanisme retensi aktif.
- **Bukti:** Ada: [K5](#k5-ingestion-dan-inference), penyimpanan payload; [K6](#k6-api-dan-akses), schema. Siapkan: audit koreksi dan hasil restore.
- **Risiko salah jawab:** hasil laporan tidak dapat direkonstruksi.
- **Follow-up:** Bisakah operator mengubah nilai tanpa jejak siapa dan kapan?

### WEB-15. Pengujian apa yang membuktikan workflow website benar?

- **Maksud reviewer:** membedakan aplikasi dapat dibuka dari alur pemeriksaan yang andal.
- **Jawaban singkat aman:** Bukti harus mencakup workflow dan kegagalan, bukan hanya screenshot.
- **Jawaban teknis:** Rencana prioritas: akses silang akun, pairing dua subjek, payload invalid, replay, ML timeout, data stale, serta kecocokan satuan/kategori. Uji mobile dan keterbacaan status gagal. Telaah ini membaca implementasi; acceptance test dan server deployment tidak dijalankan.
- **Bukti:** Ada: [K7](#k7-website), komponen dan API client. Siapkan: matriks test serta hasil untuk versi demo terkunci.
- **Risiko salah jawab:** demo lancar dianggap membuktikan seluruh workflow manusia aman.
- **Follow-up:** Tunjukkan satu negative test yang pernah gagal lalu diperbaiki.

## 3. Hardware/Sensor

### HW-01. Bagian mana sudah fisik, mana masih simulasi?

- **Maksud reviewer:** memeriksa realisasi terhadap klaim kemajuan.
- **Jawaban singkat aman:** Kode reader tersedia; laporan menyebut fabrikasi dan integrasi penuh masih tertunda. Status fisik harus ditunjukkan per subsistem.
- **Jawaban teknis:** Laporan memisahkan pengujian komponen, simulasi elektronik, dan platform dengan mock hardware. Firmware tidak membuktikan cartridge menghasilkan sinyal biomarker valid. Rencana bukti: daftar komponen terpasang, hasil uji, dependensi pengadaan, serta kriteria penerimaan sebelum menyebut system-level testing selesai.
- **Bukti:** Ada: [K4](#k4-hardware), firmware; [K8](#k8-dokumen-proyek), laporan. Siapkan: foto berlabel, BOM aktual, dan bench log.
- **Risiko salah jawab:** desain disebut alat terkalibrasi yang sudah bekerja penuh.
- **Follow-up:** Bisakah alat membaca larutan kontrol tanpa input angka manual?

### HW-02. Mengapa memakai ADS1115, bukan ADC internal ESP32?

- **Maksud reviewer:** menguji alasan pemilihan komponen.
- **Jawaban singkat aman:** ADS1115 menyediakan ADC eksternal dengan PGA; manfaatnya perlu ditunjukkan pada rangkaian aktual.
- **Jawaban teknis:** Resolusi nominalnya 16 bit dengan kanal multiplexed. Resolusi tidak sama dengan akurasi sistem; noise, gain, impedansi sumber, dan front-end tetap menentukan hasil. Rencana: ukur rentang sinyal dan baseline noise pada konfigurasi yang digunakan. Pemilihan ADC tidak membuktikan ketepatan klinis. [S6](#s6-adc)
- **Bukti:** Ada: [K4](#k4-hardware), inisialisasi ADC dan `GAIN_ONE`. Siapkan: pengukuran sinyal/noise.
- **Risiko salah jawab:** jumlah bit dipakai sebagai bukti akurasi konsentrasi.
- **Follow-up:** Berapa noise efektif pada pembacaan kontrol?

### HW-03. Dari mana konstanta pengali 200, -5, dan 500 berasal?

- **Maksud reviewer:** menguji konversi tegangan ke besaran biologis.
- **Jawaban singkat aman:** Konstanta ada pada firmware demo; bukti fitting kalibrasi eksperimentalnya belum terverifikasi.
- **Jawaban teknis:** Firmware menggunakan rumus linear sederhana. Untuk mengklaim satuan konsentrasi, rencana uji memerlukan larutan standar, blank, replikasi, rentang kerja, fitting, residual, dan verifikasi independen. Kalibrasi harus terkait batch cartridge serta versi firmware, bukan dipilih agar angka tampak masuk akal.
- **Bukti:** Ada: [K4](#k4-hardware), rumus konversi. Siapkan: data mentah tegangan-konsentrasi dan kurva kalibrasi bertanggal.
- **Risiko salah jawab:** angka OLED tidak memiliki ketertelusuran pengukuran.
- **Follow-up:** Tunjukkan titik kalibrasi yang menghasilkan slope 200.

### HW-04. Di mana potensiostat atau pengubah arus menjadi tegangan?

- **Maksud reviewer:** menguji kelengkapan rantai elektrokimia.
- **Jawaban singkat aman:** Firmware membaca tegangan ADC; pembacaan SPCE memerlukan front-end yang sesuai dan teruji.
- **Jawaban teknis:** Pada metode amperometrik, rangkaian harus mengendalikan kondisi elektroda dan mengubah arus ke sinyal ADC. Laporan menyebut OPA2333 dan di bagian lain LMP91000; BOM terpasang perlu diselaraskan. Simulasi settling time belum membuktikan stabilitas pada elektroda nyata. Rencana: uji dummy cell, gain, offset, dan respons kontrol.
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), narasi front-end; [K4](#k4-hardware), akuisisi. Siapkan: skematik aktual dan hasil uji.
- **Risiko salah jawab:** ADS1115 dianggap sendirian sudah menjadi pembaca biosensor lengkap.
- **Follow-up:** Berapa tegangan kerja elektroda dan bagaimana kestabilannya diuji?

### HW-05. Mengapa fructosamine dan viskositas disebut bergantian?

- **Maksud reviewer:** mencari inkonsistensi biomarker.
- **Jawaban singkat aman:** Keduanya berbeda. Jalur aktif memakai fructosamine; versi lain masih memuat viskositas dan perlu diselaraskan.
- **Jawaban teknis:** Fructosamine adalah analit kimia, sedangkan viskositas sifat aliran dengan unit dan metode ukur berbeda. Tidak ada konversi umum yang membenarkan penggantian label. Jika alat mengukur viskositas, model harus memakai fitur sesuai atau hubungan proksi yang dibuktikan khusus. Pilihan fitur mengikuti kemampuan cartridge aktual.
- **Bukti:** Ada: [K3](#k3-versi-dan-biomarker), versi generator/UI; [K1](#k1-ml-aktif), fitur aktif.
- **Risiko salah jawab:** model menerima biomarker yang sebenarnya tidak diukur.
- **Follow-up:** Tunjukkan prinsip ukur dan unit kanal ketiga.

### HW-06. Apa bukti kanal fructosamine selektif terhadap target?

- **Maksud reviewer:** menguji dasar kimia analitik.
- **Jawaban singkat aman:** Laporan mengusulkan PBA; selektivitas terhadap target saliva masih perlu eksperimen khusus.
- **Jawaban teknis:** Referensi pada analit atau matriks berbeda tidak otomatis membuktikan respons fructosamine saliva. Rencana: tetapkan analit operasional, metode referensi, kontrol positif/negatif, interferen, dan recovery dalam saliva. Bedakan sinyal pengikatan, respons elektrokimia, dan konsentrasi yang dilaporkan. Kelayakan kanal ini membutuhkan bukti analitik sendiri.
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), rancangan cartridge. Siapkan: protokol kimia dan hasil selektivitas/recovery.
- **Risiko salah jawab:** sinyal nonspesifik diklaim sebagai konsentrasi biomarker tertentu.
- **Follow-up:** Jika pengganggu memberi sinyal sama, bagaimana membedakannya?

### HW-07. Apakah pH memengaruhi sensor glukosa, bukan hanya kondisi subjek?

- **Maksud reviewer:** memisahkan efek biologis dari efek alat.
- **Jawaban singkat aman:** Pengaruh pH terhadap respons cartridge perlu dikarakterisasi terpisah dari penggunaannya sebagai fitur ML.
- **Jawaban teknis:** Respons reaksi/sensor dapat berubah bersama kondisi sampel. Model tidak otomatis mengoreksinya. Rencana: glukosa tetap pada beberapa kondisi pH dan suhu, kemudian tentukan kompensasi atau batas penggunaan. Interpretasi mengikuti kimia dan sensor aktual, bukan asumsi bahwa semua perubahan pH mencerminkan glukosa darah.
- **Bukti:** Ada: [K1](#k1-ml-aktif), fitur pH; [K8](#k8-dokumen-proyek), rancangan sensor. Siapkan: matriks uji pH-glukosa-suhu.
- **Risiko salah jawab:** artefak sensor dianggap hubungan klinis.
- **Follow-up:** Apakah model belajar kondisi subjek atau perubahan sensitivitas sensor?

### HW-08. Apakah tiga kanal dibaca secara bersamaan?

- **Maksud reviewer:** menguji timing dan cross-talk.
- **Jawaban singkat aman:** Kanal ADS1115 multiplexed dan dibaca bergiliran, bukan simultan. [S6](#s6-adc)
- **Jawaban teknis:** Saat respons berubah, selisih waktu kanal dapat memengaruhi kombinasi fitur. Rencana: catat timestamp akuisisi, tentukan settling setelah pemilihan kanal, lalu uji cross-talk dengan mengubah sinyal satu kanal. Interval sampling mengikuti dinamika reaksi dan konfigurasi ADC, bukan sekadar interval publish.
- **Bukti:** Ada: [K4](#k4-hardware), urutan pembacaan. Siapkan: trace akuisisi dan uji satu kanal.
- **Risiko salah jawab:** tiga angka dianggap mewakili keadaan sampel pada waktu identik.
- **Follow-up:** Berapa selisih waktu kanal pertama dan terakhir?

### HW-09. Bagaimana mendeteksi saturasi dan input di luar rentang ADC?

- **Maksud reviewer:** menguji penolakan kegagalan ukur.
- **Jawaban singkat aman:** Gain dikonfigurasi, tetapi deteksi saturasi perlu dibuktikan pada rangkaian aktual.
- **Jawaban teknis:** Full-scale PGA tidak menghapus batas tegangan pin terhadap catu. Rencana: periksa datasheet varian yang dipakai, gain front-end, dan level I2C; uji input kontrol dalam kondisi aman. Simpan raw ADC dan flag clipping/overrange, jangan langsung mengubahnya menjadi konsentrasi ekstrem. [S6](#s6-adc)
- **Bukti:** Ada: [K4](#k4-hardware), gain. Siapkan: skematik proteksi/catu dan uji rentang input.
- **Risiko salah jawab:** clipping menjadi hasil klinis atau input merusak komponen.
- **Follow-up:** Apakah full-scale besar membolehkan input melewati tegangan catu?

### HW-10. Apakah paket setiap lima detik berarti sampel baru?

- **Maksud reviewer:** mencari pseudoreplikasi.
- **Jawaban singkat aman:** Tidak. Beberapa paket bisa berasal dari saliva dan cartridge yang sama.
- **Jawaban teknis:** Timer mengatur pengiriman, bukan identitas biologis. Rencana: definisikan awal sesi, fase reaksi, kriteria stabil, pembacaan final, dan pergantian cartridge. Repeated measures disimpan sebagai turunan satu pemeriksaan. Jumlah paket tidak boleh menggantikan jumlah sampel atau peserta independen dalam evaluasi.
- **Bukti:** Ada: [K4](#k4-hardware), timer publish. Siapkan: SOP sesi dan relasi ID sampel-cartridge-paket.
- **Risiko salah jawab:** N penelitian diperbesar oleh pengulangan satu saliva.
- **Follow-up:** Apa yang menandai pembacaan final siap untuk inference?

### HW-11. Berapa volume saliva dan kondisi pengambilannya?

- **Maksud reviewer:** memeriksa repeatability pra-analitik.
- **Jawaban singkat aman:** Volume dan SOP mengikuti kebutuhan cartridge yang diuji; firmware tidak menentukan angka finalnya.
- **Jawaban teknis:** Rencana SOP mencakup jenis saliva, waktu, kondisi makan/minum, penanganan, dan jeda sampai pembacaan. Uji volume minimum, pembasahan, gelembung, serta variasi operator. Catat penyimpangan sebagai metadata atau alasan penolakan. Parameter final ditetapkan dari feasibility bersama tim klinis.
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), rancangan pengujian. Siapkan: SOP dan hasil uji volume/operator.
- **Risiko salah jawab:** variasi pengambilan mendominasi perubahan biomarker.
- **Follow-up:** Bagaimana mendeteksi volume kurang atau elektroda belum terbasahi?

### HW-12. Berapa LoD dan LoQ sensor kalian?

- **Maksud reviewer:** menguji kemampuan ukur pada kadar rendah.
- **Jawaban singkat aman:** LoD/LoQ belum dapat diklaim dari resolusi ADC atau konstanta firmware.
- **Jawaban teknis:** Rencana: blank dan seri konsentrasi rendah dengan replikasi serta kriteria yang ditetapkan sebelumnya. LoD menilai pembedaan dari blank; LoQ menuntut ketelitian kuantifikasi yang memadai. Laporkan unit, matriks, metode estimasi, dan variasi batch. Nilai literatur tidak otomatis berlaku pada cartridge sendiri.
- **Bukti:** Ada: [K4](#k4-hardware), akuisisi; [K8](#k8-dokumen-proyek), rencana analitik. Siapkan: data blank dan seri kadar rendah.
- **Risiko salah jawab:** banyak desimal dianggap bukti kemampuan mengukur kadar rendah.
- **Follow-up:** Apa keluaran sistem saat sinyal di bawah LoQ?

### HW-13. Apakah cartridge stabil antarbatch dan selama penyimpanan?

- **Maksud reviewer:** menguji konsistensi di luar satu eksperimen berhasil.
- **Jawaban singkat aman:** Stabilitas dan variasi batch membutuhkan uji khusus; satu kalibrasi belum cukup.
- **Jawaban teknis:** Rencana: batch berbeda, replikasi lintas hari/operator, kondisi penyimpanan, dan pengujian berkala. Catat lot, tanggal fabrikasi, kalibrasi, serta kemasan. Tentukan apakah kalibrasi berlaku per lot atau sensor. Umur simpan tidak boleh dinyatakan sebelum data tersedia.
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), rancangan cartridge. Siapkan: log lot dan hasil kontrol selama penyimpanan.
- **Risiko salah jawab:** drift sensor ditafsirkan sebagai perubahan kondisi subjek.
- **Follow-up:** Kapan batch ditolak atau dikalibrasi ulang?

### HW-14. Apa bukti bebas kontaminasi silang dan aman digunakan?

- **Maksud reviewer:** menguji keselamatan proses pengambilan dan penanganan saliva.
- **Jawaban singkat aman:** Risiko mengikuti jenis kontak dan SOP; non-invasif tidak berarti tanpa risiko.
- **Jawaban teknis:** Rencana: cartridge sekali pakai atau reuse yang tervalidasi, pengelolaan limbah, pencegahan kebocoran, dan pembersihan reader. Kebutuhan evaluasi biokompatibilitas bergantung jenis/durasi kontak, bukan hanya material casing. Studi manusia mengikuti kajian etik dan SOP penggunaan aktual.
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), desain. Siapkan: peta kontak material, SOP biosafety, dan penilaian risiko.
- **Risiko salah jawab:** kenyamanan dijadikan jaminan keselamatan universal.
- **Follow-up:** Bagian mana menyentuh peserta, saliva, dan operator?

### HW-15. Bagaimana catu daya dan noise Wi-Fi memengaruhi hasil?

- **Maksud reviewer:** menguji ketelitian reader dalam kondisi operasional.
- **Jawaban singkat aman:** Pengaruh catu dan transmisi perlu diukur; firmware berjalan tidak membuktikan sinyal analog bebas gangguan.
- **Jawaban teknis:** Rencana: bandingkan kontrol saat radio aktif/nonaktif, catu berbeda, dan baterai pada rentang kerja. Uji grounding, decoupling, brownout, serta recovery restart. Jika mengklaim portabel, laporkan durasi operasi dari konsumsi dan duty cycle terukur, bukan kapasitas baterai saja.
- **Bukti:** Ada: [K4](#k4-hardware), akuisisi/transmisi. Siapkan: trace noise, pengukuran arus, dan log uji catu.
- **Risiko salah jawab:** lonjakan radio atau catu dianggap perubahan biomarker.
- **Follow-up:** Apakah hasil kontrol berubah ketika MQTT sedang mem-publish?

## 4. Validasi Klinis dan Etik

### KLIN-01. Apa yang sebenarnya ingin dibuktikan pada manusia?

- **Maksud reviewer:** menguji definisi intended use dan endpoint.
- **Jawaban singkat aman:** Tujuannya menilai kelayakan prototipe sebagai kandidat screening risiko, dengan status referensi ditentukan pemeriksaan klinis yang sesuai.
- **Jawaban teknis:** Rencana protokol harus menentukan populasi, setting, pengguna, keputusan yang dibantu, dan konsekuensi hasil. Estimasi glukosa, klasifikasi prediabetes, dan rekomendasi rujukan merupakan endpoint berbeda. Tentukan endpoint primer sebelum rekrutmen agar ukuran sampel, analisis, dan klaim mengikuti pertanyaan penelitian yang sama.
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), tujuan; [D1](#d1-google-doc), batas klaim. Siapkan: protokol intended use dan rencana analisis.
- **Risiko salah jawab:** keberhasilan satu endpoint dipakai untuk mengklaim endpoint lain.
- **Follow-up:** Keputusan apa yang boleh berubah setelah melihat hasil Glicovia?

### KLIN-02. Apakah glukometer sama dengan OGTT?

- **Maksud reviewer:** menguji validitas pembanding dan ketepatan istilah.
- **Jawaban singkat aman:** Tidak. OGTT adalah prosedur uji toleransi glukosa; pembacaan glukometer biasa tidak identik dengan hasil plasma sesuai protokol OGTT.
- **Jawaban teknis:** Google Doc memuat penyamaan yang perlu dikoreksi. Rencana studi harus menyebut jenis spesimen, metode laboratorium, waktu pengambilan, dan kondisi pemeriksaan. Glukometer dapat menjadi pembanding eksploratif dengan keterbatasan yang dicatat; jangan menjadikannya satu-satunya dasar label diagnosis definitif. [S2](#s2-pembanding)
- **Bukti:** Ada: [D1](#d1-google-doc), bagian standar. Siapkan: protokol pembanding yang disepakati klinisi dan laboratorium.
- **Risiko salah jawab:** seluruh label training dan validasi memakai reference standard yang salah definisi.
- **Follow-up:** Apakah label kalian berasal dari plasma laboratorium atau darah kapiler alat portabel?

### KLIN-03. Ambang prediabetes mana yang kalian gunakan?

- **Maksud reviewer:** mencari pencampuran puasa, OGTT, dan HbA1c.
- **Jawaban singkat aman:** Ambang mengikuti jenis pemeriksaan referensi, bukan satu angka universal untuk semua kondisi.
- **Jawaban teknis:** Acuan ADA untuk prediabetes mencakup FPG 100-125 mg/dL, plasma dua jam pada OGTT 75 g 140-199 mg/dL, atau HbA1c 5,7-6,4%. Ini kriteria pemeriksaan referensi, bukan cut-off saliva. Model dan UI harus menyimpan konteks target serta menghindari kategori yang bertentangan. [S1](#s1-kriteria-klinis)
- **Bukti:** Ada: [K1](#k1-ml-aktif), batas kategori; [K7](#k7-website), contoh UI. Siapkan: kamus target dan aturan kategori tunggal.
- **Risiko salah jawab:** nilai sama diberi label berbeda karena konteks pemeriksaan hilang.
- **Follow-up:** Bagaimana menangani dua pemeriksaan referensi yang hasil kategorinya berbeda?

### KLIN-04. Apa beda validasi analitik dan validasi klinis?

- **Maksud reviewer:** memeriksa urutan pembuktian.
- **Jawaban singkat aman:** Analitik menguji pengukuran biomarker; klinis menguji hubungan hasil sistem dengan kondisi sasaran pada populasi yang ditetapkan.
- **Jawaban teknis:** Rencana analitik meliputi presisi, bias terhadap metode analit, rentang, interferensi, LoD/LoQ, serta stabilitas. Setelah rantai ukur memadai, studi klinis menguji keputusan screening terhadap reference standard pada peserta. Pembandingan glukosa saliva dengan metode glukosa saliva tidak sama dengan pembandingan prediksi terhadap status prediabetes.
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), tahapan pengembangan; [D1](#d1-google-doc), rencana validasi. Siapkan: dua protokol dengan endpoint berbeda.
- **Risiko salah jawab:** sensor presisi diklaim otomatis mampu mendeteksi penyakit.
- **Follow-up:** Eksperimen mana membuktikan konsentrasi, dan mana membuktikan kemampuan screening?

### KLIN-05. Apakah sudah memenuhi ISO 15189:2022?

- **Maksud reviewer:** menguji penggunaan standar secara tepat.
- **Jawaban singkat aman:** Kami dapat merujuk prinsip mutu dan kompetensi yang relevan; pemenuhan atau akreditasi belum dibuktikan oleh sumber yang ditelaah.
- **Jawaban teknis:** ISO 15189 berfokus pada laboratorium medis dan mencakup POCT. Menuliskan rujukan ini tidak mensertifikasi produk Glicovia. Rencana: bersama laboratorium mitra, petakan persyaratan yang relevan ke SOP, kompetensi operator, dokumentasi, dan bukti pengendalian mutu. Telaah ini memeriksa ruang lingkup publik, bukan mengaudit seluruh klausul. [S3](#s3-iso-15189)
- **Bukti:** Ada: [D1](#d1-google-doc), penyebutan standar. Siapkan: matriks persyaratan-bukti serta dokumen resmi bila ada.
- **Risiko salah jawab:** mengaku tersertifikasi tanpa ruang lingkup atau dokumen yang sah.
- **Follow-up:** Siapa yang diakreditasi: laboratorium, penelitian, atau alat?

### KLIN-06. Apa relevansi ISO 20916:2019 untuk penelitian ini?

- **Maksud reviewer:** menguji pemahaman tata kelola studi IVD.
- **Jawaban singkat aman:** Standar itu membahas praktik studi kinerja klinis IVD menggunakan spesimen manusia; penerapannya perlu dipetakan sesuai tujuan studi.
- **Jawaban teknis:** Ruang lingkup publik mencakup perencanaan, pelaksanaan, pencatatan, dan pelaporan studi kinerja/safety untuk tujuan regulatori. Bukan angka kelulusan akurasi universal. Rencana Glicovia perlu protokol, penanggung jawab, pengendalian data, serta pelaporan penyimpangan. Klaim kepatuhan penuh memerlukan telaah standar dan bukti lengkap. [S4](#s4-iso-20916)
- **Bukti:** Ada: [D1](#d1-google-doc), rujukan standar. Siapkan: protokol studi dan matriks penerapan persyaratan.
- **Risiko salah jawab:** menyebut nomor ISO sebagai pengganti desain studi yang valid.
- **Follow-up:** Dokumen studi apa yang sudah selesai dan siapa menyetujuinya?

### KLIN-07. Apakah target 30 sampel cukup membuktikan akurasi?

- **Maksud reviewer:** memeriksa kecukupan ukuran studi.
- **Jawaban singkat aman:** Angka 30 dalam laporan adalah target awal; belum merupakan justifikasi ukuran studi validasi klinis.
- **Jawaban teknis:** Rencana perhitungan harus mengikuti endpoint, presisi interval kepercayaan, prevalensi/perbandingan kelompok, jumlah kasus positif, dan pengukuran berulang. Tiga puluh aliquot dari sedikit orang berbeda dari 30 peserta independen. Pilot dapat menguji feasibility dan memperkirakan variasi, tetapi tidak otomatis mendukung klaim performa populasi.
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), target sampel. Siapkan: perhitungan ukuran sampel dan definisi unit analisis.
- **Risiko salah jawab:** angka kebiasaan dipakai sebagai alasan statistik untuk klaim kuat.
- **Follow-up:** Berapa peserta prediabetes yang diperlukan agar sensitivitas cukup presisi?

### KLIN-08. Bagaimana peserta dipilih agar hasil tidak bias?

- **Maksud reviewer:** mencari spectrum bias dan populasi terlalu mudah.
- **Jawaban singkat aman:** Kriteria peserta harus mengikuti target penggunaan dan ditetapkan sebelum rekrutmen.
- **Jawaban teknis:** Rencana: definisikan setting, kriteria inklusi/eksklusi, alur rekrutmen, serta catatan peserta yang tidak masuk analisis. Membandingkan kontrol sangat sehat dengan diabetes berat dapat mempermudah pemisahan, tetapi belum menguji batas prediabetes. Laporkan karakteristik peserta dan cakupan generalisasi; jangan mengklaim semua umur dari satu kelompok terbatas.
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), sasaran umum. Siapkan: protokol rekrutmen dan diagram alur peserta.
- **Risiko salah jawab:** sensitivitas/spesifisitas studi tidak berlaku pada setting screening nyata.
- **Follow-up:** Apakah peserta dekat ambang prediabetes terwakili?

### KLIN-09. Bagaimana mengendalikan makanan, kesehatan mulut, obat, dan hidrasi?

- **Maksud reviewer:** menguji confounding serta kelayakan protokol saliva.
- **Jawaban singkat aman:** Faktor tersebut perlu dicatat dan dinilai; tiga biomarker tidak otomatis menghilangkan pengaruhnya.
- **Jawaban teknis:** Rencana: SOP pra-analitik bersama klinisi, metadata kondisi yang relevan, kriteria penundaan/penolakan sampel, dan analisis subgroup yang ditentukan sebelumnya. Kriteria terlalu ketat dapat mengurangi keterpakaian, sehingga dokumentasikan alasan serta batas populasi. Jangan menetapkan waktu puasa atau larangan obat sendiri tanpa protokol yang disetujui.
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), rencana sampel; [K7](#k7-website), contoh metadata. Siapkan: formulir dan analisis confounder.
- **Risiko salah jawab:** model belajar kebiasaan atau gangguan mulut sebagai pengganti status glikemik.
- **Follow-up:** Bagaimana membedakan sinyal karena penyakit mulut dari kondisi metabolik?

### KLIN-10. Seberapa dekat waktu pengambilan darah dan saliva?

- **Maksud reviewer:** menguji validitas pasangan reference dan index test.
- **Jawaban singkat aman:** Jendela waktu harus ditetapkan dalam protokol dan dicatat; kecocokan tanggal saja tidak cukup.
- **Jawaban teknis:** Rencana: pilih kondisi pemeriksaan, catat waktu kedua spesimen, serta aturan untuk pasangan di luar jendela. Bila memakai OGTT, fase pengambilan saliva harus jelas. Analisis mempertimbangkan pengukuran berulang dan kemungkinan perbedaan dinamika, tanpa mengarang nilai lag biologis yang belum diukur.
- **Bukti:** Ada: [K5](#k5-ingestion-dan-inference), field waktu ingestion. Siapkan: timestamp pengambilan biologis dan SOP pairing pemeriksaan.
- **Risiko salah jawab:** galat akibat waktu disalahartikan sebagai kegagalan atau keberhasilan model.
- **Follow-up:** Timestamp database menandai pengambilan sampel atau penerimaan pesan?

### KLIN-11. Bagaimana mencegah operator mengetahui jawaban saat membaca alat?

- **Maksud reviewer:** mencari bias pengukuran dan penyesuaian hasil.
- **Jawaban singkat aman:** Rencana validasi perlu blinding dan model terkunci sebelum membaca hasil reference test.
- **Jawaban teknis:** Operator index test sebaiknya tidak memakai label referensi untuk mengulang, memilih, atau menyesuaikan pembacaan. Rencana: kode sampel, akses terpisah, SOP repeat, serta log semua percobaan termasuk gagal. Model/threshold dikunci sebelum analisis evaluasi independen. Ini desain yang disarankan, belum bukti studi sudah dijalankan.
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), rencana pengujian. Siapkan: prosedur blinding dan log akses/pengukuran.
- **Risiko salah jawab:** performa terbentuk dari pemilihan hasil yang cocok dengan label.
- **Follow-up:** Berapa kali sampel boleh diulang dan hasil mana yang masuk analisis?

### KLIN-12. Bagaimana false negative dan false positive ditangani?

- **Maksud reviewer:** menilai konsekuensi keputusan screening.
- **Jawaban singkat aman:** Hasil prototipe tidak boleh menjadi dasar menghentikan pemeriksaan atau terapi; tindak lanjut mengikuti tenaga kesehatan dan protokol studi.
- **Jawaban teknis:** Rencana: hitung kedua jenis kesalahan terhadap endpoint yang jelas, tentukan proses rujukan, serta bahasa hasil yang tidak memberi kepastian palsu. Sampel invalid atau hasil dekat batas harus mengikuti aturan yang ditetapkan sebelumnya. Penilaian utilitas perlu mempertimbangkan beban konfirmasi dan kasus terlewat, bukan akurasi agregat saja.
- **Bukti:** Ada: [D1](#d1-google-doc), batas klaim. Siapkan: SOP komunikasi hasil/rujukan dan rencana analisis kesalahan.
- **Risiko salah jawab:** peserta merasa aman atau mengubah penanganan berdasarkan prediksi eksperimental.
- **Follow-up:** Apa tindakan jika Glicovia normal tetapi pemeriksaan referensi menunjukkan kelainan?

### KLIN-13. Sudah ada ethical clearance dan informed consent?

- **Maksud reviewer:** menguji apakah penelitian manusia memiliki tata kelola yang benar.
- **Jawaban singkat aman:** Bukti persetujuan etik belum terverifikasi dalam telaah ini. Status harus dijawab memakai dokumen aktual, bukan diasumsikan dari proposal.
- **Jawaban teknis:** Sebelum kegiatan studi manusia sesuai protokol, ajukan kajian KEPK dan ikuti keputusan serta persetujuan yang berlaku. Consent harus menjelaskan sifat eksperimen, prosedur, risiko, penggunaan data, dan hak peserta. Jangan menentukan pengecualian sendiri karena saliva non-invasif. Nomor, tanggal, serta versi protokol harus cocok. [S9](#s9-etik)
- **Bukti:** Ada: [D1](#d1-google-doc), narasi tahap pengembangan. Siapkan: surat KEPK, protokol disetujui, dan formulir consent yang relevan.
- **Risiko salah jawab:** mengaku memperoleh izin atau menganggap izin pembimbing menggantikan kajian etik.
- **Follow-up:** Apakah izin mencakup pengambilan darah, penyimpanan saliva, dan pelatihan ML?

### KLIN-14. Bagaimana privasi subjek dan penggunaan ulang data dijaga?

- **Maksud reviewer:** menilai kontrol data nyata, bukan sekadar penghilangan nama.
- **Jawaban singkat aman:** ID berkode membantu, tetapi masih dapat menjadi data yang bisa dikaitkan kembali; akses dan tujuan penggunaan perlu dibatasi.
- **Jawaban teknis:** Rencana: simpan kunci identitas terpisah, kontrol akses per peran/subjek, minimisasi log, retensi yang disetujui, dan prosedur penarikan diri sesuai consent/protokol. Penggunaan ulang untuk training atau berbagi dataset harus ditetapkan secara jelas. Temuan endpoint global dan broker publik harus ditangani sebelum data manusia mengalir.
- **Bukti:** Ada: [K6](#k6-api-dan-akses), kontrol akses; [K4](#k4-hardware), broker. Siapkan: rencana pengelolaan data dan consent terkait.
- **Risiko salah jawab:** ID subjek dianggap anonim mutlak sementara hasil bisa diakses atau dikaitkan ulang.
- **Follow-up:** Siapa memegang kunci penghubung ID dengan identitas?

### KLIN-15. Jika korelasi saliva-darah tetap rendah, apa keputusan tim?

- **Maksud reviewer:** menguji falsifiabilitas dan keberanian membatasi klaim.
- **Jawaban singkat aman:** Kami akan melaporkan hasil tersebut dan menilai apakah tujuan screening masih didukung; klaim dihentikan atau dipersempit bila tidak memenuhi kriteria.
- **Jawaban teknis:** Rencana investigasi memisahkan mutu analitik, masalah pra-analitik, kesesuaian target, serta kekuatan hubungan biologis. Korelasi saja tidak cukup: galat, agreement, dan keputusan screening juga perlu dinilai. Jangan terus mengganti model atau membuang data sampai hasil tampak baik. Perubahan hipotesis harus dinyatakan eksploratif dan diuji kembali.
- **Bukti:** Ada: [D1](#d1-google-doc), diskusi keterbatasan korelasi. Siapkan: kriteria go/no-go dan laporan semua eksperimen.
- **Risiko salah jawab:** proyek terlihat tidak memiliki kondisi gagal dan hanya mencari pembenaran.
- **Follow-up:** Kriteria terukur apa yang membuat tim menghentikan klaim screening?

## 5. Pertanyaan Menjebak Reviewer

Pertanyaan berikut sengaja menghubungkan kelemahan antarkomponen. Bagian maksud dan risiko menjelaskan mengapa pertanyaan berbahaya; jangan menjawab defensif dengan klaim baru yang belum dibuktikan.

### TRAP-01. Jadi sensitivitas Glicovia sudah 94,2%, sesuai slide kalian?

- **Maksud reviewer:** memancing pemindahan hasil publikasi menjadi hasil alat sendiri.
- **Jawaban singkat aman:** Angka itu berasal dari penelitian Fares dan kolega, bukan uji Glicovia.
- **Jawaban teknis:** Abstrak publikasi memang melaporkan sensitivitas 94,2% dan spesifisitas 62% untuk analisis salivary glucose pada studi mereka. Hasil tersebut mendukung alasan riset, tetapi tidak memvalidasi cartridge, model, protokol, atau populasi Glicovia. Rencana pembuktian tetap memerlukan studi sendiri. [S7](#s7-studi-saliva)
- **Bukti:** Ada: [D1](#d1-google-doc), kutipan studi; [K2](#k2-artefak-evaluasi), hasil lokal berbeda jenis. Siapkan: pemisahan tabel hasil literatur dan hasil tim.
- **Risiko salah jawab:** reviewer menilai tim mengatribusikan hasil penelitian orang lain sebagai capaian sendiri.
- **Follow-up:** Mana confusion matrix peserta Glicovia yang menghasilkan angka tersebut?

### TRAP-02. File kalian menulis clinical PASS. Mengapa mengaku belum tervalidasi?

- **Maksud reviewer:** mencari label perangkat lunak yang melebih-lebihkan bukti.
- **Jawaban singkat aman:** `clinical_status: PASS` adalah nama status dari aturan internal evaluasi; labelnya terlalu kuat untuk bukti yang tersedia.
- **Jawaban teknis:** Artefak menunjukkan kelulusan threshold R2/RMSE/MAE, sementara metrik klasifikasi pada file itu kosong. Asal data dan desain evaluasi belum mendukung kelulusan klinis. Rencana: ubah terminologi menjadi evaluasi teknis internal dan pisahkan dari hasil studi klinis. Mengakui masalah penamaan lebih dapat dipertahankan daripada menjadikan label sebagai sertifikasi.
- **Bukti:** Ada: [K2](#k2-artefak-evaluasi), `clinical_assessment`, `meets_thresholds`, dan `classification_metrics`.
- **Risiko salah jawab:** isi artefak membantah batas klaim yang diucapkan tim.
- **Follow-up:** Siapa menetapkan threshold internal itu dan apakah memiliki dasar klinis?

### TRAP-03. Confidence tidak bisa di bawah 75%; apakah kalian membuat model selalu yakin?

- **Maksud reviewer:** membongkar skor yang terlihat meyakinkan karena konstruksi rumus.
- **Jawaban singkat aman:** Default fungsi memang memberi floor 0,75. Skor ini belum layak ditafsirkan sebagai keyakinan klinis.
- **Jawaban teknis:** Floor berasal dari `max(confidence, confidence_level - 0.2)` dengan default 0,95. Menghapus floor saja juga tidak membuatnya probabilitas valid karena metode tetap jitter pada model yang sama. Rencana: ubah label, jelaskan metode secara terbuka, lalu uji pendekatan ketidakpastian yang sesuai pada data independen.
- **Bukti:** Ada: [K1](#k1-ml-aktif), `_bootstrap_confidence`. Siapkan: distribusi skor pada kasus valid, salah, dan OOD.
- **Risiko salah jawab:** reviewer menganggap angka confidence dibentuk untuk memperindah hasil.
- **Follow-up:** Berapa confidence ketika input sengaja salah tetapi tetap numerik?

### TRAP-04. Apakah kanal ketiga benar mengukur fructosamine atau hanya diganti namanya?

- **Maksud reviewer:** menyatukan inkonsistensi hardware, fitur ML, dan dokumen.
- **Jawaban singkat aman:** Schema aktif memakai fructosamine, tetapi klaim pengukuran membutuhkan bukti kanal fisik; viskositas tidak boleh diganti label begitu saja.
- **Jawaban teknis:** Ada jejak viskositas di versi lain dan UI statis. Rencana: tunjukkan transduser, prinsip ukur, standar kalibrasi, unit, mapping payload, dan dataset training untuk kanal yang sama. Bila salah satu belum tersedia, nyatakan jalur tersebut masih simulasi atau rencana integrasi.
- **Bukti:** Ada: [K3](#k3-versi-dan-biomarker), perbedaan versi; [K4](#k4-hardware), rumus; [K5](#k5-ingestion-dan-inference), mapping.
- **Risiko salah jawab:** keseluruhan prediksi bergantung pada fitur dengan makna fisik tidak jelas.
- **Follow-up:** Bisakah tim menunjukkan rantai bukti satu kanal dari kimia sampai model?

### TRAP-05. Kalau MQTT palsu saja menghasilkan prediksi, apa yang membuktikan biosensor bekerja?

- **Maksud reviewer:** memisahkan uji integrasi perangkat lunak dari validasi sensing.
- **Jawaban singkat aman:** Prediksi dari payload buatan hanya membuktikan jalur software menerima dan memproses data.
- **Jawaban teknis:** Bukti biosensor harus dimulai dari sampel kontrol berkadar diketahui, sinyal elektroda/front-end, raw ADC, konversi terkalibrasi, baru payload dan prediksi. Rencana demo membedakan mode simulasi dan mode fisik secara eksplisit serta memakai ID uji yang tertelusur. Sukses API tidak menguji selektivitas atau akurasi sensor.
- **Bukti:** Ada: [K5](#k5-ingestion-dan-inference), jalur data; [K8](#k8-dokumen-proyek), mock hardware. Siapkan: log kontrol fisik end-to-end.
- **Risiko salah jawab:** keberhasilan demo digital dipakai menutup belum selesainya cartridge.
- **Follow-up:** Apa yang berubah pada raw ADC ketika konsentrasi kontrol diganti?

### TRAP-06. Kalian menyebut pengembangan CGM. Di mana pengukuran kontinunya?

- **Maksud reviewer:** menguji ketepatan kategori perangkat.
- **Jawaban singkat aman:** Bukti saat ini lebih sesuai dengan prototipe pemeriksaan berbasis sampel saliva; pembaruan dashboard bukan bukti pengukuran biologis kontinu.
- **Jawaban teknis:** Dokumen lama memakai narasi CGM, sementara firmware mem-publish pembacaan berkala dari kanal analog. Rencana klaim harus mengikuti cara sampling dan masa pakai cartridge aktual. Untuk menyebut kontinu diperlukan bukti akuisisi biologis berkelanjutan, stabilitas, interval valid, serta pemeliharaan; hal itu belum terbukti dari timer MQTT.
- **Bukti:** Ada: [K3](#k3-versi-dan-biomarker), dokumen lama; [K4](#k4-hardware), timer. Siapkan: definisi mode pemeriksaan pada slide.
- **Risiko salah jawab:** reviewer menilai kelas teknologi dibesar-besarkan.
- **Follow-up:** Apakah ada sampel baru atau hanya pembacaan ulang saliva yang sama?

### TRAP-07. Target akurasi 85% sudah tercapai atau masih angka proposal?

- **Maksud reviewer:** memeriksa pemisahan target, simulasi, dan capaian.
- **Jawaban singkat aman:** Laporan memuat target tersebut; capaian harus disertai definisi metrik, dataset, dan protokol evaluasi yang sesuai.
- **Jawaban teknis:** R2 tidak bisa dipakai menggantikan accuracy. Accuracy dari data sintetis atau eksperimen model pembanding juga bukan akurasi klinis perangkat. Rencana slide memisahkan target proposal, hasil software per run, pengujian analitik, dan hasil klinis jika tersedia. Jangan memilih angka tertinggi dari laporan berbeda tanpa provenance.
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), target 85%; [K2](#k2-artefak-evaluasi), laporan aktual.
- **Risiko salah jawab:** target ditampilkan sebagai capaian tanpa eksperimen yang relevan.
- **Follow-up:** Delapan puluh lima persen dari berapa kasus, dengan endpoint apa?

### TRAP-08. Nilai glukosa saliva pada dokumen berbeda jauh dari rentang generator. Mengapa?

- **Maksud reviewer:** mencari mismatch literatur, satuan, dan distribusi training.
- **Jawaban singkat aman:** Rentang sintetis dan angka dokumen perlu diaudit; kami belum boleh menyatakan distribusi generator mewakili populasi target.
- **Jawaban teknis:** Metadata dummy mencatat rentang `glucose_saliva` 0,1-10, sedangkan Google Doc menyebut angka rerata yang lebih tinggi. Perbedaan itu perlu pemeriksaan sumber primer, unit, metode, matriks, dan aturan clipping. Jangan langsung mengubah unit atau memperluas rentang tanpa dasar. Rencana: data dictionary dan distribusi empiris dari protokol sendiri.
- **Bukti:** Ada: [K2](#k2-artefak-evaluasi), metadata; [D1](#d1-google-doc), bagian standar saliva. Siapkan: audit angka dan unit.
- **Risiko salah jawab:** data biologis aktual seluruhnya jatuh di luar distribusi latih.
- **Follow-up:** Apa yang terjadi jika glukosa saliva input berada jauh di atas maksimum training?

### TRAP-09. Kalau tetap harus tes darah, untuk apa alat ini?

- **Maksud reviewer:** menguji manfaat klinis di luar kenyamanan atau teknologi.
- **Jawaban singkat aman:** Manfaat screening tambahan masih hipotesis: perlu dibuktikan apakah meningkatkan jangkauan atau alur rujukan dengan kesalahan yang dapat diterima.
- **Jawaban teknis:** Konfirmasi klinis tidak otomatis meniadakan manfaat screening, tetapi manfaat juga tidak otomatis ada. Rencana studi utilitas membandingkan alur dengan/tanpa alat: partisipasi, hasil invalid, rujukan, kasus terlewat, biaya per pemeriksaan valid, serta beban konfirmasi. Pada tahap kini klaim dibatasi ke pengembangan prototipe.
- **Bukti:** Ada: [D1](#d1-google-doc), tujuan kenyamanan; [K8](#k8-dokumen-proyek), target penggunaan. Siapkan: rancangan pembanding workflow.
- **Risiko salah jawab:** kenyamanan dipakai untuk menghindari kebutuhan pembuktian manfaat.
- **Follow-up:** Hasil studi seperti apa menunjukkan alat justru menambah biaya tanpa manfaat?

### TRAP-10. ISO 15197 dipakai untuk saliva? Bukankah ruang lingkupnya berbeda?

- **Maksud reviewer:** menguji pemilihan standar dan pencampuran parameter performa.
- **Jawaban singkat aman:** ISO 15197 membahas sistem pemantauan glukosa darah kapiler untuk self-testing; penerapannya pada saliva tidak boleh diasumsikan langsung.
- **Jawaban teknis:** Laporan lokal mengaitkan klasifikasi dengan standar tersebut. Rencana: petakan standar sesuai intended use dan matriks, lalu jelaskan jika suatu kriteria hanya dipakai sebagai referensi eksploratif. Ketepatan analitik pengukuran glukosa dan sensitivitas klasifikasi adalah ukuran berbeda. Telaah ruang lingkup tidak setara audit kepatuhan penuh. [S8](#s8-iso-15197)
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), penyebutan ISO 15197. Siapkan: matriks relevansi standar yang ditelaah bersama ahli.
- **Risiko salah jawab:** nomor standar digunakan di luar konteks untuk memberi kesan tervalidasi.
- **Follow-up:** Kriteria mana relevan untuk analit saliva dan mana hanya untuk pembanding darah?

### TRAP-11. Sudah ada login dan CORS. Mengapa belum aman untuk data manusia?

- **Maksud reviewer:** menguji pemahaman batas kontrol keamanan.
- **Jawaban singkat aman:** Login dan CORS tidak membuktikan semua endpoint terotorisasi atau pengirim MQTT sah.
- **Jawaban teknis:** Pada kode, middleware autentikasi prediksi hanya dipasang untuk `/me`; rute global tetap perlu pengamanan. CORS mengatur akses lintas origin di browser, bukan autentikasi semua klien. Rencana: audit akses per route/objek, uji permintaan langsung, serta pisahkan pengamanan perangkat dari pengamanan akun website.
- **Bukti:** Ada: [K6](#k6-api-dan-akses), `app.ts` dan router; [K4](#k4-hardware), MQTT. Siapkan: negative test akses.
- **Risiko salah jawab:** kontrol antarmuka dianggap menutup semua jalur akses data.
- **Follow-up:** Apa yang mencegah klien non-browser memanggil rute global?

### TRAP-12. Kalau korelasi lemah, bukankah AI bisa memperbaikinya?

- **Maksud reviewer:** memancing klaim AI dapat menggantikan informasi biologis yang tidak tersedia.
- **Jawaban singkat aman:** Model hanya dapat memakai informasi yang ada pada input; peningkatan harus dibuktikan pada data independen.
- **Jawaban teknis:** Model fleksibel dapat mempelajari pola nonlinear, tetapi juga artefak, confounder, dan aturan generator. Rencana: baseline sederhana, ablation, audit leakage, serta evaluasi independen. Jika input tidak membawa sinyal yang cukup untuk endpoint, menambah kompleksitas tidak membenarkan klaim screening. Hasil negatif harus tetap dilaporkan.
- **Bukti:** Ada: [K1](#k1-ml-aktif), generator/training; [K2](#k2-artefak-evaluasi), baseline pembanding.
- **Risiko salah jawab:** AI dijadikan alasan mengabaikan mutu sensor dan dasar biologis.
- **Follow-up:** Apa bukti manfaat nonlinear dibanding Ridge pada data manusia?

### TRAP-13. Mengapa contoh UI memberi label yang berbeda dari aturan model?

- **Maksud reviewer:** menguji konsistensi makna hasil yang dilihat pengguna.
- **Jawaban singkat aman:** Ada contoh statis dengan aturan kategori berbeda; ini perlu diselaraskan dan tidak boleh dijadikan bukti klinis.
- **Jawaban teknis:** `data.ts` memuat contoh 142 mg/dL berlabel prediabetes dan pembangkitan histori memakai batas 126/180, sementara inference memakai 100/126. Tanpa konteks pemeriksaan yang jelas, perbedaan itu menyesatkan. Rencana: satu kontrak kategori per target, label data demo, dan uji nilai batas pada seluruh tampilan yang memakai sumber tersebut.
- **Bukti:** Ada: [K7](#k7-website), `dashboardMetrics`/histori statis; [K1](#k1-ml-aktif), kategori inference.
- **Risiko salah jawab:** hasil sama diberi arti berbeda oleh model dan website.
- **Follow-up:** Sumber kategori mana yang dipakai halaman yang sedang didemokan?

### TRAP-14. Apa bukti inovasi ini belum pernah dibuat siapa pun?

- **Maksud reviewer:** menguji kebaruan yang diklaim terlalu absolut.
- **Jawaban singkat aman:** Kebaruan yang diajukan berada pada rancangan integrasi tertentu; klaim pertama di dunia belum terbukti oleh telaah ini.
- **Jawaban teknis:** Komponen, model, dan protokol komunikasi telah dikenal. Rencana pembuktian kebaruan memerlukan pencarian literatur/paten yang terdokumentasi serta perbandingan fitur dan intended use dengan karya terdekat. Integrasi tiga biomarker bisa menjadi kontribusi yang diuji, tetapi belum otomatis berarti lebih akurat, unik, atau dapat dipatenkan.
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), klaim kebaruan. Siapkan: matriks prior art, tanggal pencarian, dan perbedaan yang terukur.
- **Risiko salah jawab:** satu publikasi pembanding langsung menggugurkan klaim absolut.
- **Follow-up:** Apa pembeda paling spesifik terhadap penelitian terdekat?

### TRAP-15. Bila cartridge belum selesai sampai penilaian, apa luaran yang jujur?

- **Maksud reviewer:** menguji manajemen risiko dan konsistensi pelaporan.
- **Jawaban singkat aman:** Laporkan subsistem yang sudah terbukti, bagian tertunda, serta milestone berikutnya dengan kriteria uji yang jelas.
- **Jawaban teknis:** Rencana prioritas: realisasi/karakterisasi cartridge, kalibrasi reader, integrasi kontrol fisik, kemudian studi yang disetujui. Jangan mengalihkan definisi sukses menjadi dashboard semata bila tujuan mencakup biosensor. Angka simulasi, biaya rancangan, dan target waktu tetap diberi statusnya; biaya per tes harus memasukkan cartridge gagal, kontrol, dan konfirmasi jika dianalisis.
- **Bukti:** Ada: [K8](#k8-dokumen-proyek), hambatan pengadaan dan realisasi. Siapkan: matriks progres, bukti pembelian/fabrikasi, serta jadwal realistis.
- **Risiko salah jawab:** tim dianggap menyembunyikan hambatan atau mengubah klaim capaian.
- **Follow-up:** Eksperimen apa yang paling menentukan kelayakan proyek pada tahap berikutnya?

## Indeks Bukti dan Sumber

Tautan lokal relatif terhadap file ini. Kode menunjukkan implementasi; JSON menunjukkan isi artefak tersimpan; laporan menunjukkan pernyataan penulis. Ketiganya tidak menggantikan catatan eksperimen fisik atau studi klinis. Hash yang mengikat seluruh artefak ke satu rilis belum diverifikasi. Perubahan lokal yang sudah ada tidak diubah dalam penyusunan dokumen ini.

### K1. ML Aktif

- [Generator data sintetis](../ml_pipeline/src/generate_dummy.py).
- [Preprocessing dan definisi fitur/target](../ml_pipeline/src/preprocessing.py): `FEATURE_COLUMNS`, `DEFAULT_CONFIG`, `preprocess`, `_fit_scaler`.
- [Training SVR dan kategorisasi](../ml_pipeline/src/train_svm.py): `_build_svr`, `_mgdl_to_class`, `GridSearchCV`.
- [Inference dan confidence](../ml_pipeline/src/inference.py): `FEATURE_ORDER`, `preprocess_sample`, `_bootstrap_confidence`, `_category_from_mgdl`.
- [Pipeline](../ml_pipeline/src/pipeline.py), [API Python](../ml_pipeline/src/api_connector.py), [evaluasi](../ml_pipeline/src/evaluate.py).

### K2. Artefak Evaluasi

- [Metadata dummy](../ml_pipeline/src/data/dummy/metadata.json): 150 baris, distribusi kelas, rentang fitur, dan seed.
- [Laporan preprocessing](../ml_pipeline/src/data/processed/preprocessing_report.json): 98 train, 25 test, eksklusi outlier, serta distribusi kelas setelah preprocessing.
- [Parameter scaler](../ml_pipeline/src/data/processed/scaler_params.json).
- [Laporan evaluasi September](../ml_pipeline/src/evaluation/evaluation_report.json): R2/RMSE/MAE, status internal PASS, serta `classification_metrics` kosong.
- [Log eksperimen](../ml_pipeline/src/models/experiment_log.json), [hasil fold](../ml_pipeline/src/models/fold_results/).
- [Perbandingan model Agustus](../ml_pipeline/src/models/model_comparison/comparison_report.json): delapan model, Ridge berperingkat pertama menurut test R2 dalam eksperimen itu.

Angka di atas merupakan snapshot pada waktu telaah. Generator dan metadata membuktikan adanya jalur sintetis; mengikat setiap laporan ke dataset tertentu tetap memerlukan manifest/hash. Jangan membawa angka lintas run tanpa identitas eksperimen.

### K3. Versi dan Biomarker

- [Generator pada folder ML lain](../ml_pipeline_git/src/generate_dummy.py): masih memuat viskositas.
- [Catatan arsitektur lama](../.hermes.md): narasi dan kolom versi awal.
- [Dokumen GLICOVIA](../resource/markdown/GLICOVIA.md): memuat narasi CGM dan viskositas.
- [Data contoh website](../app/web/src/lib/data.ts): viskositas, angka/statistik contoh, dan kategori statis.

Keberadaan folder berbeda tidak menetapkan folder yang aktif di deployment. Buktikan dengan konfigurasi startup, model yang dimuat, serta respons service pada versi demo.

### K4. Hardware

- [Firmware reader](../main.cpp): ESP32, ADS1115, OLED SH1106, koneksi MQTT, timer, rumus konversi, dan reconnect blocking.
- [Panduan pengujian MQTT-hardware](../app/backend/guide/mqtt-hardware-testing-guide.md): panduan pengujian integrasi, bukan sertifikat kalibrasi.

### K5. Ingestion dan Inference

- [MQTT handler](../app/backend/src/mqtt/mqtt-handler.ts): parsing, resolusi device/assignment, penyimpanan, dan trigger inference.
- [MQTT client](../app/backend/src/mqtt/mqtt-client.ts).
- [Inference service](../app/backend/src/modules/inference/inference.service.ts): `mapSensorReadingToMlPayload`, `runInferenceForSensorReading`, quality gating, serta metadata model.
- [Repository readings](../app/backend/src/modules/readings/readings.repository.ts).
- [Repository predictions](../app/backend/src/modules/predictions/predictions.repository.ts).
- [Repository model](../app/backend/src/modules/models/models.repository.ts).

### K6. API dan Akses

- [Express app](../app/backend/src/app.ts): pemasangan route dan CORS.
- [Router predictions](../app/backend/src/modules/predictions/predictions.routes.ts): autentikasi `/me` dan rute global.
- [Router readings](../app/backend/src/modules/readings/readings.routes.ts).
- [Router pairing](../app/backend/src/modules/pairing/pairing.routes.ts).
- [Schema Prisma](../app/backend/prisma/schema.prisma).

Temuan rute adalah hasil inspeksi kode, bukan hasil penetration test atau bukti bahwa deployment publik sedang mengekspos data nyata.

### K7. Website

- [API client](../app/web/src/lib/api/client.ts).
- [Klien readings](../app/web/src/components/readings-client.tsx), [klien predictions](../app/web/src/components/predictions-client.tsx).
- [Klien devices](../app/web/src/components/devices-client.tsx), [klien operator](../app/web/src/components/operator-client.tsx).
- [Data statis](../app/web/src/lib/data.ts): `dashboardMetrics`, histori contoh, `analyticsMetrics`, `modelInfo`, dan `settingsConfig`.

Isi contoh seperti online, retensi, latensi, atau kompensasi suhu bukan bukti fitur itu aktif pada perangkat. Periksa pemakai setiap sumber data dan perilaku runtime sebelum presentasi.

### K8. Dokumen Proyek

- [Laporan PKP lokal](Laporan_PKM-KC_Glicovia.md): target 85%, target 30 sampel, rancangan front-end/cartridge, hasil simulasi yang dilaporkan, dan integrasi yang masih tertunda.
- [Dokumen rancangan awal](../resource/markdown/GLICOVIA.md).
- [Panduan eksekusi backend](../app/backend/guide/hermes-backend-execution-guide.md).

Klaim numerik pada laporan, termasuk inferensi 42 ms, dimensi/toleransi casing, dan respons simulasi, belum direproduksi pada telaah ini. Minta data mentah, kondisi uji, dan versi artefak sebelum menjadikannya bukti capaian.

### D1. Google Doc

[Kumpulan pertanyaan Glicovia](https://docs.google.com/document/d/1YFi_cBWbTfi9SH18LIkgD9qtsxcrnj1q8UBJOe25woQ/edit?usp=sharing), dibaca melalui [ekspor teks](https://docs.google.com/document/d/1YFi_cBWbTfi9SH18LIkgD9qtsxcrnj1q8UBJOe25woQ/export?format=txt). Isinya memuat posisi prototipe screening, biomarker, angka literatur Fares, dan rencana validasi. Penyebutan OGTT sebagai glukometer serta narasi klasifikasi langsung perlu diselaraskan dengan protokol dan kode.

### S1. Kriteria Klinis

[ADA Standards of Care 2026: Diagnosis and Classification of Diabetes](https://doi.org/10.2337/dc26-s002). Kriteria prediabetes dibedakan menurut FPG, plasma dua jam OGTT 75 g, dan HbA1c. Digunakan untuk memeriksa konteks reference test, bukan untuk menetapkan cut-off saliva atau memvalidasi output Glicovia. Halaman langsung sempat gagal dibuka; informasi kriteria diperiksa dari hasil indeks sumber resmi dan ringkasan NIDDK pada S2.

### S2. Pembanding

[NIDDK: Diabetes Tests and Diagnosis](https://www.niddk.nih.gov/health-information/diabetes/overview/tests-diagnosis) dan [tes untuk mengidentifikasi prediabetes](https://www.niddk.nih.gov/health-information/professionals/clinical-tools-patient-management/diabetes/game-plan-preventing-type-2-diabetes/prediabetes-screening-how-why/recommended-tests-identifying-prediabetes). Sumber ini membedakan pemeriksaan diagnostik dan keterbatasan meter glukosa konsumen; mendukung pemilihan pembanding sesuai protokol klinis.

### S3. ISO 15189

[ISO 15189:2022, halaman resmi](https://www.iso.org/standard/76677.html). Ruang lingkup mutu/kompetensi laboratorium medis, termasuk POCT. Telaah memakai ringkasan ruang lingkup publik, bukan akses/audit penuh dokumen standar.

### S4. ISO 20916

[ISO 20916:2019, halaman resmi](https://www.iso.org/standard/69455.html). Praktik studi kinerja klinis IVD menggunakan spesimen manusia untuk tujuan regulatori; bukan ambang kelulusan akurasi universal. Pemetaan relevansi studi akademik perlu dinyatakan, bukan diasumsikan sebagai sertifikasi.

### S5. Preprocessing

[scikit-learn: Common Pitfalls and Recommended Practices](https://scikit-learn.org/1.8/common_pitfalls.html). Mendukung pemisahan train/test sebelum pembelajaran transformasi dan penggunaan pipeline untuk mengurangi leakage. Temuan urutan preprocessing Glicovia berasal dari kode lokal; besarnya dampak perlu evaluasi ulang.

### S6. ADC

[Texas Instruments: ADS1115](https://www.ti.com/product/ADS1115) dan [datasheet ADS111x](https://www.ti.com/lit/ds/symlink/ads1115.pdf). Mendukung spesifikasi ADC/PGA dan pemeriksaan batas listrik. Cocokkan nomor komponen terpasang; jangan mencampur spesifikasi ADS1115 dengan ADS1115L atau varian lain.

### S7. Studi Saliva

[Fares et al., 2019, PubMed](https://pubmed.ncbi.nlm.nih.gov/31336519/), DOI [10.1016/j.dsx.2019.03.010](https://doi.org/10.1016/j.dsx.2019.03.010). Abstrak memuat sensitivitas 94,2% dan spesifisitas 62% yang dikutip Google Doc. Itu hasil studi penulis tersebut; tidak boleh diatribusikan pada Glicovia. Rincian protokol/cut-off perlu diperiksa pada artikel lengkap sebelum diadopsi.

### S8. ISO 15197

[ISO 15197:2013, halaman resmi](https://www.iso.org/standard/54976.html). Ruang lingkupnya sistem pemantauan glukosa darah kapiler untuk self-testing dalam pengelolaan diabetes; tidak otomatis berlaku langsung pada sensor saliva. Dicantumkan karena laporan lokal menggunakannya, bukan sebagai pernyataan kepatuhan Glicovia.

### S9. Etik

[Kementerian Kesehatan: Pedoman dan Standar Etik Penelitian dan Pengembangan Kesehatan Nasional](https://repository.badankebijakan.kemkes.go.id/4214/1/Pedoman%20dan%20Standar%20Etik%20Penelitian%20dan%20Pengembangan%20Kesehatan%20Nasional.pdf). Rujukan untuk penyusunan kajian etik dan persetujuan setelah penjelasan. Persyaratan studi aktual serta keputusan peninjauan mengikuti KEPK yang berwenang; dokumen ini tidak menetapkan sendiri status persetujuan atau pengecualian Glicovia.

## 10 Pertanyaan Paling Berbahaya

Urutan berikut adalah prioritas latihan berdasarkan ketidaksesuaian bukti yang ditemukan, bukan prediksi statistik peluang pertanyaan keluar.

### BAHAYA-01. Berapa manusia yang sudah membuktikan alat kalian akurat?

**Jawaban paling aman:** "Artefak yang kami tunjukkan saat ini adalah evaluasi pipeline dengan data sintetis. Jumlah peserta dan performa manusia belum dapat kami klaim dari artefak ini. Bukti studi harus berupa protokol, persetujuan etik, pasangan data referensi, dan laporan hasilnya."

**Pegangan bukti:** ML-02, KLIN-07, KLIN-13; [K2](#k2-artefak-evaluasi), [K8](#k8-dokumen-proyek).

### BAHAYA-02. Mana data kalibrasi yang membenarkan angka konsentrasi di OLED?

**Jawaban paling aman:** "Rumus pada firmware demo belum kami nyatakan sebagai kalibrasi sensor tervalidasi. Angka konsentrasi baru dapat dipertahankan setelah ada pengukuran standar, kurva kalibrasi, dan verifikasi independen. Tanpa itu, yang terbukti baru pembacaan dan alur elektroniknya."

**Pegangan bukti:** HW-03, HW-04; [K4](#k4-hardware).

### BAHAYA-03. Apakah fructosamine sebenarnya hanya viskositas yang diganti nama?

**Jawaban paling aman:** "Keduanya tidak setara. Jalur aktif memakai fructosamine, tetapi versi lain masih memuat viskositas. Kami harus menunjukkan sensor, unit, kalibrasi, dan dataset yang konsisten; bagian yang belum terbukti tetap kami nyatakan sebagai simulasi atau rencana."

**Pegangan bukti:** HW-05, TRAP-04; [K3](#k3-versi-dan-biomarker).

### BAHAYA-04. Apakah confidence tinggi dan clinical PASS membuktikan aman dipakai?

**Jawaban paling aman:** "Tidak. Confidence sekarang berasal dari perturbasi input dengan floor internal; PASS berasal dari ambang metrik perangkat lunak. Keduanya belum membuktikan ketepatan maupun keselamatan klinis dan perlu diberi label yang sesuai."

**Pegangan bukti:** ML-10, TRAP-02, TRAP-03; [K1](#k1-ml-aktif), [K2](#k2-artefak-evaluasi).

### BAHAYA-05. Mengapa memakai SVR jika baseline Ridge menang dan evaluasinya berisiko leakage?

**Jawaban paling aman:** "SVR adalah kandidat yang sudah diimplementasikan. Laporan pembanding memang mengunggulkan Ridge pada eksperimen tersebut, dan urutan preprocessing perlu diperbaiki. Pemilihan final harus mengikuti evaluasi yang konsisten dan independen; kami belum mengklaim SVR paling unggul."

**Pegangan bukti:** ML-04, ML-05, ML-12; [K1](#k1-ml-aktif), [K2](#k2-artefak-evaluasi).

### BAHAYA-06. Mengapa menyebut glukometer sebagai OGTT dan memakai satu ambang untuk semua tes?

**Jawaban paling aman:** "Istilah pada dokumen itu perlu dikoreksi. Jenis spesimen, metode, waktu, dan kondisi pemeriksaan menentukan reference test serta kategorinya. Ambang yang digunakan model harus cocok dengan target yang dilatih; hasil saliva belum menjadi diagnosis klinis."

**Pegangan bukti:** KLIN-02, KLIN-03; [S1](#s1-kriteria-klinis), [S2](#s2-pembanding).

### BAHAYA-07. Bisakah orang membaca prediksi atau menyamar sebagai alat tanpa izin?

**Jawaban paling aman:** "Kode memiliki rute prediksi global tanpa middleware autentikasi yang terlihat, dan firmware demo memakai broker publik. Deployment belum kami audit pada telaah ini. Celah tersebut harus ditangani dan diuji sebelum data manusia digunakan."

**Pegangan bukti:** WEB-03, WEB-04, TRAP-11; [K4](#k4-hardware), [K6](#k6-api-dan-akses).

### BAHAYA-08. Apa demo ini menunjukkan biosensor bekerja atau hanya payload simulasi?

**Jawaban paling aman:** "Mode demo harus dinyatakan sesuai sumber datanya. Payload simulasi membuktikan alur software. Bukti biosensor harus menunjukkan sampel kontrol, sinyal mentah, konversi terkalibrasi, dan hasil yang tertelusur sampai dashboard."

**Pegangan bukti:** WEB-01, HW-01, TRAP-05; [K4](#k4-hardware), [K5](#k5-ingestion-dan-inference), [K8](#k8-dokumen-proyek).

### BAHAYA-09. Mana sertifikat ISO, izin etik, dan bukti sensitivitas 94,2% milik kalian?

**Jawaban paling aman:** "Angka 94,2% adalah hasil literatur, bukan Glicovia. Rujukan ISO bukan sertifikasi. Status etik dan kepatuhan hanya kami nyatakan berdasarkan dokumen resmi yang benar-benar ada dan sesuai protokol; bukti itu belum terverifikasi dalam telaah ini."

**Pegangan bukti:** KLIN-05, KLIN-06, KLIN-13, TRAP-01; [S3](#s3-iso-15189), [S4](#s4-iso-20916), [S7](#s7-studi-saliva), [S9](#s9-etik).

### BAHAYA-10. Jika performa pada manusia buruk, apakah kalian tetap menyebut detektor prediabetes?

**Jawaban paling aman:** "Tidak sebagai kemampuan yang sudah terbukti. Kami akan melaporkan hasil, menilai sumber kegagalan, dan membatasi atau menghentikan klaim sesuai kriteria yang ditetapkan. Kontribusi subsistem yang teruji tetap dilaporkan terpisah dari keberhasilan screening klinis."

**Pegangan bukti:** KLIN-15, TRAP-12, TRAP-15; [K8](#k8-dokumen-proyek), [D1](#d1-google-doc).

## Red Flag Jawaban yang Harus Dihindari

- "Akurasi Glicovia 94,2%." Itu angka literatur yang dikutip, bukan hasil alat sendiri.
- "R2 0,97 berarti 97% pasien terdiagnosis benar." Metrik regresi bukan accuracy klasifikasi.
- "Clinical PASS berarti sudah lolos uji klinis." Status berasal dari threshold internal software.
- "Confidence 95% berarti pasti benar 95%." Metode saat ini belum memberi probabilitas klinis terkalibrasi.
- "Data kami 150 pasien." Metadata yang ditelaah berisi 150 baris sintetis.
- "Tiga puluh sampel pasti cukup secara statistik." Kecukupan mengikuti endpoint, desain, dan presisi yang diinginkan.
- "Lima fold menjamin tidak overfit atau leakage." Urutan preprocessing dan pemisahan subjek tetap menentukan validitas.
- "SVR pasti paling akurat." Laporan pembanding lokal justru menempatkan Ridge lebih tinggi pada eksperimen tersebut.
- "Fructosamine dan viskositas sama." Analit kimia dan sifat fisik berbeda; tidak boleh menukar label fitur.
- "ADS1115 16 bit berarti konsentrasi sudah akurat." Resolusi ADC tidak membuktikan kalibrasi, selektivitas, atau akurasi sistem.
- "Sudah ada angka di OLED, berarti sensor valid." Perlu kontrol dan ketertelusuran konversi sinyal.
- "OGTT itu glukometer." Prosedur, spesimen, waktu, dan metode pembanding harus jelas.
- "Ambang darah boleh langsung dipakai pada saliva." Ambang pemeriksaan referensi tidak otomatis menjadi cut-off saliva.
- "Kami sudah tersertifikasi ISO karena mengikuti prinsipnya." Klaim resmi perlu bukti dan ruang lingkup yang tepat.
- "Saliva non-invasif, jadi bebas etik dan risiko." Kajian etik dan penilaian risiko mengikuti studi aktual.
- "ID subjek berarti anonim sepenuhnya." Data berkode bisa tetap dikaitkan ulang.
- "Ada login/CORS, jadi semua data aman." Otorisasi route/objek dan autentikasi perangkat perlu diuji.
- "Semua halaman sudah live." Workspace juga memuat data statis; buktikan sumber per halaman.
- "Publish lima detik berarti hasil pemeriksaan keluar lima detik." Interval kirim berbeda dari waktu analitik dan latensi total.
- "Reconnect berarti semua data pasti tersimpan." Buffer, replay, deduplikasi, dan recovery harus dibuktikan.
- "AI akan mengatasi sensor yang tidak selektif atau korelasi yang lemah." Informasi input dan validasi independen tetap diperlukan.
- "Hasil normal berarti peserta pasti sehat." Hasil prototipe tidak menghapus kebutuhan penilaian klinis sesuai protokol.
- "Prototipe sudah menggantikan glukometer/dokter." Bukti yang ditelaah belum mendukung penggunaan tersebut.
- "Belum pernah ada di dunia." Klaim absolut memerlukan penelusuran prior art yang memadai.
- "Nanti divalidasi" tanpa eksperimen atau kriteria lanjut. Sebutkan uji berikutnya, bukti yang dihasilkan, dan kondisi gagal secara konkret.
