# Bank Pertanyaan dan Jawaban Monev Glicovia

Dokumen ini disusun untuk latihan sesi tanya jawab monitoring dan evaluasi PKM-KC Glicovia. Jawaban dibuat dengan posisi yang aman: menekankan bahwa Glicovia saat ini adalah prototipe deteksi dini/screening, bukan alat diagnosis final.

## Jawaban Pembuka Singkat

**Pertanyaan: Jelaskan Glicovia dalam 1 menit.**

Glicovia adalah prototipe alat deteksi dini prediabetes secara non-invasif menggunakan sampel saliva. Biomarker yang digunakan adalah glukosa saliva, pH, dan fructosamine. Sinyal dari cartridge biosensor dibaca oleh rangkaian elektronik, kemudian data diproses oleh model machine learning dan hasilnya ditampilkan di dashboard berbasis web. Target utamanya adalah membuat proses screening lebih nyaman, mudah dipantau, dan berpotensi digunakan untuk deteksi awal, bukan menggantikan diagnosis klinis dokter.

**Pertanyaan: Apa kontribusi utama proyek ini?**

Kontribusi utamanya adalah integrasi end-to-end dari pengambilan biomarker saliva, pembacaan sensor, pengolahan data dengan machine learning, sampai penyimpanan dan visualisasi hasil melalui dashboard. Jadi proyek ini tidak hanya berhenti di ide alat atau model ML, tetapi sudah diarahkan menjadi sistem yang bisa digunakan dalam alur monitoring.

## A. Latar Belakang dan Urgensi

**1. Kenapa diabetes menjadi masalah yang perlu disasar?**

Diabetes memiliki prevalensi tinggi dan banyak kasus tidak terdiagnosis. Dampaknya bukan hanya kadar gula darah tinggi, tetapi juga komplikasi jangka panjang pada jantung, ginjal, mata, saraf, dan kulit. Karena prediabetes sering tidak bergejala, deteksi dini menjadi penting agar intervensi gaya hidup atau pemeriksaan lanjutan bisa dilakukan lebih cepat.

**2. Kenapa fokus pada prediabetes, bukan diabetes saja?**

Prediabetes adalah fase yang masih bisa dicegah agar tidak berkembang menjadi diabetes tipe 2. Kalau alat screening mampu membantu menemukan individu berisiko lebih awal, manfaat preventifnya lebih besar dibanding hanya mendeteksi saat kondisi sudah menjadi diabetes.

**3. Apa masalah dari metode cek gula darah saat ini?**

Metode umum masih banyak yang invasif, membutuhkan tusukan jarum, menghasilkan limbah medis, dan dapat menurunkan kepatuhan pemeriksaan rutin. Untuk sebagian masyarakat, rasa takut jarum dan ketidaknyamanan menjadi hambatan untuk melakukan screening berkala.

**4. Apakah Glicovia menggantikan glucometer darah?**

Tidak. Pada tahap ini Glicovia diposisikan sebagai alat screening atau deteksi dini berbasis saliva. Hasilnya tetap perlu dibandingkan dengan gold standard seperti pemeriksaan glukosa darah untuk validasi klinis.

**5. Apa novelty Glicovia?**

Novelty Glicovia ada pada kombinasi biomarker saliva, cartridge biosensor, model machine learning, dan dashboard IoT dalam satu alur prototipe. Nilai kebaruannya bukan hanya pada sensor, tetapi pada integrasi alat, model prediksi, dan sistem monitoring.

## B. Saliva dan Biomarker

**6. Kenapa memilih saliva?**

Saliva mudah diambil, tidak membutuhkan jarum, lebih nyaman bagi pengguna, dan mengandung biomarker yang dapat merefleksikan kondisi metabolik tertentu. Untuk screening berulang, saliva lebih ramah pengguna dibanding sampel darah kapiler.

**7. Apakah glukosa saliva berkorelasi dengan glukosa darah?**

Literatur menunjukkan adanya potensi korelasi, tetapi korelasinya tidak selalu sesederhana hubungan satu-ke-satu. Karena itu Glicovia tidak hanya memakai glukosa saliva, tetapi juga pH dan fructosamine sebagai fitur tambahan untuk membantu model menangkap pola yang lebih stabil.

**8. Kenapa memakai tiga biomarker: glukosa saliva, pH, dan fructosamine?**

Glukosa saliva memberi sinyal langsung terkait metabolisme glukosa. pH dapat menggambarkan kondisi lingkungan saliva yang memengaruhi pembacaan dan kondisi oral. Fructosamine memberi gambaran glikasi protein dalam rentang waktu lebih panjang. Kombinasi ketiganya diharapkan lebih informatif dibanding satu biomarker saja.

**9. Apa fungsi fructosamine dalam sistem ini?**

Fructosamine digunakan sebagai biomarker pendukung karena berkaitan dengan paparan glukosa terhadap protein dalam periode tertentu. Dalam model ML, fructosamine menjadi fitur yang membantu membedakan kondisi normal, prediabetes, dan diabetes.

**10. Apa faktor yang bisa mengganggu sampel saliva?**

Faktor seperti makanan, minuman, hidrasi, waktu pengambilan, kebersihan mulut, penyakit mulut, obat-obatan, dan volume saliva dapat memengaruhi hasil. Karena itu pengambilan sampel perlu protokol, misalnya kondisi puasa atau pembatasan makan-minum sebelum pengambilan.

**11. Apakah saliva cukup akurat untuk diagnosis?**

Pada tahap ini belum diklaim sebagai diagnosis final. Saliva digunakan sebagai pendekatan non-invasif untuk screening awal. Akurasi klinis harus dibuktikan melalui validasi dengan sampel manusia dan pembanding gold standard.

**12. Bagaimana menjawab jika reviewer meragukan saliva?**

Jawaban aman: keraguan itu valid, sehingga Glicovia tidak mengklaim menggantikan pemeriksaan darah. Fokus kami adalah membangun prototipe screening non-invasif dan menguji apakah kombinasi biomarker saliva plus machine learning dapat mendekati kategori klinis secara konsisten.

## C. Machine Learning dan Data

**13. Apa input dan output model?**

Input model adalah tiga fitur: `glucose_saliva`, `ph_value`, dan `fructosamine_umol_l`. Output model adalah estimasi kadar glukosa darah referensi dalam mg/dL, kemudian hasil estimasi itu dipetakan menjadi kategori Normal, Pre-Diabetes, atau Diabetes.

**14. Kenapa menggunakan SVM/SVR?**

SVR dipilih karena cocok untuk dataset kecil sampai menengah, dapat menangani pola non-linear dengan kernel RBF, dan cukup robust jika fitur sudah diskalakan. Untuk tahap prototipe, SVR adalah baseline yang masuk akal karena tidak membutuhkan data sangat besar seperti deep learning.

**15. Kenapa kernel RBF dipakai?**

Kernel RBF dipakai karena hubungan biomarker saliva dan estimasi glukosa darah kemungkinan tidak sepenuhnya linear. RBF membantu model menangkap pola non-linear antar fitur.

**16. Kenapa fitur perlu discaling dengan StandardScaler?**

SVR sensitif terhadap skala fitur. Glukosa saliva, pH, dan fructosamine memiliki rentang angka yang berbeda, sehingga scaling diperlukan agar model tidak terlalu didominasi oleh fitur dengan skala numerik lebih besar.

**17. Bagaimana preprocessing dilakukan?**

Pipeline melakukan validasi data, imputasi median untuk missing value, deteksi outlier dengan metode IQR, pembagian train-test secara stratified, lalu normalisasi menggunakan StandardScaler yang fitted hanya pada data training.

**18. Kenapa outlier dihapus?**

Outlier dapat berasal dari noise sensor, kesalahan pencatatan, atau sampel yang tidak sesuai protokol. Pada tahap awal, outlier dihapus agar model belajar dari pola yang lebih stabil. Namun pada tahap validasi lanjutan, strategi outlier bisa dibandingkan antara remove, cap, atau flag.

**19. Apakah data saat ini real atau synthetic?**

Pipeline saat ini sudah mendukung data real CSV, tetapi pengembangan awal banyak memakai synthetic data yang dibuat untuk mensimulasikan tiga kategori klinis, outlier, dan class imbalance. Ini berguna untuk validasi alur sistem, bukan untuk klaim akurasi klinis final.

**20. Kalau data masih synthetic, apa arti akurasinya?**

Akurasi pada synthetic data menunjukkan bahwa pipeline, preprocessing, training, evaluasi, dan inferensi sudah berjalan secara teknis. Namun akurasi tersebut belum boleh dianggap sebagai performa klinis final. Performa klinis harus dihitung ulang setelah data manusia terkumpul.

**21. Bagaimana rencana migrasi ke data manusia?**

Data manusia akan dikumpulkan dengan protokol pengambilan saliva dan pemeriksaan pembanding. Setelah data terkumpul, pipeline yang sama dapat digunakan untuk preprocessing, training ulang, cross-validation, evaluasi, dan pemilihan model terbaik.

**22. Apa metrik evaluasi yang digunakan?**

Untuk regresi digunakan R2, RMSE, dan MAE. Untuk kategori klinis digunakan accuracy dan F1 macro setelah estimasi mg/dL dipetakan ke kategori Normal, Pre-Diabetes, dan Diabetes. F1 macro penting karena kelas bisa tidak seimbang.

**23. Apa batas kategori klinis yang digunakan?**

Secara implementasi, estimasi di bawah 100 mg/dL dikategorikan Normal, 100 sampai di bawah 126 mg/dL sebagai Pre-Diabetes, dan 126 mg/dL ke atas sebagai Diabetes. Batas ini dipakai untuk pemetaan awal dan perlu disesuaikan dengan protokol klinis yang digunakan.

**24. Bagaimana mencegah overfitting?**

Pipeline memakai train-test split, cross-validation, pemantauan gap performa train-test, dan model comparison. Untuk SVR, hyperparameter dipilih melalui GridSearchCV. Pada data real nanti, validasi perlu diperluas dengan jumlah sampel lebih besar.

**25. Apakah sudah ada cross-validation?**

Ya. Pipeline memiliki evaluasi cross-validation, termasuk 5-fold validation dan pencatatan hasil fold. Untuk model SVR yang dituning, GridSearchCV juga digunakan untuk mencari parameter terbaik.

**26. Apa parameter SVR terbaik saat ini?**

Pada laporan model comparison, Tuned SVR RBF memiliki parameter terbaik `C=1000.0`, `epsilon=0.01`, dan `gamma=0.03` pada data yang digunakan saat pengujian tersebut.

**27. Kenapa hasil model comparison menunjukkan Ridge lebih baik dari Tuned SVR?**

Pada data synthetic saat ini, hubungan antar fitur kemungkinan cukup linear, sehingga Ridge bisa tampil lebih baik. Itu tidak berarti SVR salah, tetapi menunjukkan bahwa pipeline kami objektif membandingkan beberapa model. Model final akan dipilih setelah data manusia tersedia.

**28. Kalau Ridge lebih baik, kenapa slide masih menyebut SVM?**

SVM/SVR adalah rancangan awal dan baseline utama karena cocok untuk dataset kecil-menengah dan pola non-linear. Namun dalam pengembangan, kami juga menambahkan model comparison untuk memastikan pilihan model berbasis data. Jika data validasi manusia menunjukkan Ridge atau model lain lebih baik, sistem dapat mengadopsinya tanpa mengubah arsitektur besar.

**29. Apakah confidence score adalah probabilitas klinis?**

Belum. Confidence saat ini adalah estimasi teknis berbasis variasi prediksi melalui bootstrap perturbation, bukan probabilitas klinis terkalibrasi. Untuk penggunaan klinis, confidence perlu dikalibrasi dan divalidasi dengan data manusia.

**30. Apakah model bisa berjalan real-time?**

Ya, secara arsitektur bisa. Model disimpan sebagai artifact, lalu dipanggil oleh FastAPI endpoint `/predict`. Backend aplikasi dapat mengirim data sensor ke service ML dan menyimpan hasil prediksi ke database.

## D. Hardware dan Sensor

**31. Bagaimana prinsip kerja hardware Glicovia?**

Sampel saliva bereaksi pada cartridge biosensor. SPCE membaca respon elektrokimia, sinyal kemudian diperkuat atau dikondisikan oleh rangkaian analog, dikonversi oleh ADC, lalu diproses oleh ESP32 sebelum dikirim ke sistem.

**32. Apa fungsi SPCE?**

SPCE atau Screen Printed Carbon Electrode berfungsi sebagai elektroda pada cartridge biosensor untuk membaca reaksi elektrokimia dari sampel.

**33. Apa fungsi OPA2333?**

OPA2333 digunakan sebagai komponen penguat atau pengkondisi sinyal analog agar sinyal dari sensor lebih siap dibaca oleh ADC.

**34. Apa fungsi ADS1115?**

ADS1115 adalah ADC 16-bit yang mengubah sinyal analog menjadi data digital agar dapat diproses oleh mikrokontroler.

**35. Kenapa LMP91000 diganti OPA2333 dan ADS1115?**

Karena LMP91000 sulit didapat, tim memilih kombinasi OPA2333 dan ADS1115 sebagai alternatif yang lebih tersedia. Risiko dari perubahan ini adalah perlu redesain dan kalibrasi ulang, tetapi secara fungsi tetap mendukung pembacaan dan konversi sinyal.

**36. Apakah penggantian komponen memengaruhi akurasi?**

Berpotensi iya, karena karakteristik rangkaian analog memengaruhi kualitas sinyal. Karena itu perlu kalibrasi dan pengujian sensor sebelum klaim performa alat dibuat.

**37. Bagaimana kalibrasi sensor dilakukan?**

Kalibrasi idealnya dilakukan dengan larutan standar atau sampel dengan konsentrasi biomarker yang diketahui, lalu dibandingkan antara nilai sensor dan nilai referensi. Hasil kalibrasi digunakan untuk mengoreksi pembacaan sebelum masuk ke model.

**38. Apakah cartridge sekali pakai?**

Untuk keamanan dan menghindari kontaminasi silang, cartridge sebaiknya dirancang sekali pakai atau memiliki komponen kontak sampel yang disposable. Ini juga perlu dipertimbangkan dalam biaya operasional dan limbah.

**39. Apa risiko terbesar di hardware?**

Risiko terbesar adalah stabilitas sinyal, reproducibility antar cartridge, noise, ketersediaan komponen, dan kalibrasi terhadap nilai referensi. Ini adalah alasan pengujian sensor menjadi tahap krusial berikutnya.

**40. Bagaimana jika saliva terlalu sedikit atau kualitas sampel buruk?**

Sistem perlu quality flag. Pada backend sudah ada konsep `quality_flag` seperti valid, suspect, dan incomplete. Jika sampel incomplete, data tidak dikirim ke inferensi agar hasil tidak misleading.

## E. IoT, Backend, dan Dashboard

**41. Bagaimana data dari alat masuk ke sistem?**

Data sensor dari alat dikirim sebagai payload berisi nilai biomarker. Backend menyimpan data tersebut sebagai sensor reading, lalu dapat memicu inferensi ke ML service.

**42. Apa endpoint ML yang digunakan?**

ML service menyediakan endpoint `/predict` untuk prediksi satu sampel, `/predict-batch` untuk batch, `/model-info` untuk metadata model, dan `/health` untuk status service.

**43. Bagaimana backend menyimpan hasil prediksi?**

Backend menyimpan sensor reading, model version, dan prediction result. Hasil prediksi menyimpan estimasi glukosa, kategori klinis, confidence score, status inferensi, dan waktu prediksi.

**44. Kenapa perlu menyimpan versi model?**

Versi model penting untuk traceability. Jika hasil prediksi di masa lalu dievaluasi ulang, kita bisa tahu model mana yang menghasilkan prediksi tersebut.

**45. Bagaimana sistem pairing device dan user?**

Skema backend memiliki User, Subject, Device, PairingToken, dan DeviceAssignment. Pairing token digunakan untuk menghubungkan device tertentu dengan subject tertentu secara terkontrol.

**46. Apa yang terjadi jika ML service gagal?**

Backend menandai prediksi sebagai failed dan mencatat kegagalan. Ini lebih aman dibanding diam-diam menganggap hasil sukses. Sistem juga memiliki fallback metadata model jika `/model-info` tidak tersedia.

**47. Apakah ada autentikasi?**

Ya, backend memiliki modul auth dan middleware autentikasi. User juga memiliki role seperti subject dan admin, sehingga akses dapat dibedakan berdasarkan peran.

**48. Bagaimana keamanan data pasien?**

Data pasien perlu dijaga melalui autentikasi, pembatasan akses, penyimpanan terstruktur, dan audit log. Pada tahap prototipe, fondasi backend sudah mendukung user, subject, device, dan prediksi terpisah, tetapi hardening keamanan perlu dilakukan sebelum produksi.

**49. Apa manfaat dashboard?**

Dashboard membuat hasil tidak hanya muncul sekali di alat, tetapi bisa dipantau sebagai riwayat. Operator dapat melihat tren, reading terbaru, hasil prediksi, perangkat, dan status sistem.

**50. Apakah sistem tetap berjalan jika internet putus?**

Untuk rancangan ideal, alat dapat menyimpan sementara data secara lokal lalu sinkronisasi saat koneksi kembali. Pada tahap prototipe, fokus utamanya adalah integrasi online antara alat, backend, ML service, dan dashboard.

## F. Validasi, Etik, dan Uji Manusia

**51. Ethical clearance sudah untuk apa?**

Ethical clearance menunjukkan bahwa rencana pengambilan data manusia telah melalui peninjauan etik. Namun approval etik bukan bukti bahwa alat sudah valid, melainkan izin untuk menjalankan pengujian sesuai protokol.

**52. Apa pembanding gold standard?**

Pembanding yang ideal adalah pemeriksaan glukosa darah menggunakan metode klinis yang diakui, misalnya gula darah puasa atau pemeriksaan laboratorium sesuai protokol penelitian.

**53. Apa kriteria keberhasilan validasi?**

Keberhasilan validasi dapat dilihat dari korelasi dengan nilai referensi, error regresi seperti MAE/RMSE, sensitivitas dan spesifisitas kategori klinis, serta kemampuan mendeteksi prediabetes tanpa terlalu banyak false negative.

**54. Kenapa false negative penting?**

False negative berarti orang yang sebenarnya berisiko dianggap normal. Untuk alat screening, false negative berbahaya karena pengguna bisa merasa aman padahal perlu pemeriksaan lanjutan.

**55. Kenapa false positive juga perlu diperhatikan?**

False positive dapat menimbulkan kecemasan dan pemeriksaan lanjutan yang tidak perlu. Karena itu keseimbangan sensitivitas dan spesifisitas penting, terutama jika alat ditujukan untuk screening masyarakat.

**56. Bagaimana protokol pengambilan saliva?**

Subjek perlu mengikuti protokol sebelum pengambilan sampel, misalnya tidak makan atau minum dalam periode tertentu, menjaga kebersihan mulut, dan membiarkan saliva terkumpul secara alami. Detail protokol harus konsisten agar data tidak bias.

**57. Berapa jumlah subjek yang dibutuhkan?**

Semakin besar dan seimbang antar kategori, semakin baik. Untuk tahap awal, jumlah subjek bisa digunakan untuk proof-of-concept, tetapi klaim klinis kuat membutuhkan sampel lebih besar dan representatif.

**58. Bagaimana mengatasi bias usia, jenis kelamin, atau kondisi mulut?**

Bias dikendalikan melalui pencatatan metadata subjek, kriteria inklusi-eksklusi, protokol sampling, dan analisis subkelompok. Jika data cukup besar, variabel tambahan bisa dipertimbangkan dalam model.

**59. Apakah ada risiko biologis dari saliva?**

Ada risiko kontaminasi biologis karena saliva adalah sampel tubuh. Karena itu perlu APD, cartridge sekali pakai, prosedur pembuangan limbah, dan protokol kebersihan.

**60. Apakah alat ini sudah siap digunakan publik?**

Belum untuk penggunaan publik sebagai alat klinis. Saat ini statusnya prototipe yang perlu menyelesaikan pengujian sensor, validasi alat, dan validasi dengan sampel manusia.

## G. Luaran, Progres, dan Manajemen Proyek

**61. Progres 70 persen itu terdiri dari apa saja?**

Tahap yang sudah selesai meliputi studi literatur, desain hardware, pengadaan komponen, model SVM/pipeline ML, ethical clearance, dan perakitan alat. Website masih dalam proses, sedangkan pengujian sensor dan validasi alat belum selesai.

**62. Apa bagian yang paling belum selesai?**

Bagian paling kritis yang belum selesai adalah pengujian sensor dan validasi alat dengan sampel manusia. Tahap ini menentukan apakah alat tidak hanya berjalan secara teknis, tetapi juga valid secara pengukuran.

**63. Kenapa pengujian sensor belum selesai?**

Ada kendala komponen seperti LMP91000 yang sulit didapat, sehingga tim perlu mengganti rancangan dengan OPA2333 dan ADS1115. Perubahan ini membutuhkan redesain, perakitan ulang, dan kalibrasi.

**64. Apa risiko terbesar sampai akhir program?**

Risiko terbesar adalah keterbatasan waktu untuk kalibrasi, pengujian sensor, integrasi alat-web, dan pengumpulan data manusia. Karena itu prioritas berikutnya adalah memastikan demo end-to-end dan validasi minimal berjalan.

**65. Apa rencana selanjutnya?**

Rencana selanjutnya adalah pengujian alat dengan sampel manusia, 3D printing hardware, integrasi alat-web-uji sistem, evaluasi akhir, dan penyusunan luaran PKM.

**66. Apa luaran utama Glicovia?**

Luaran utama adalah prototipe alat, website/dashboard, laporan kemajuan, laporan akhir, dokumentasi, media sosial, publikasi, dan ethical clearance.

**67. Bagaimana membuktikan website sudah bukan sekadar mockup?**

Backend sudah memiliki skema database, modul auth, device, pairing, readings, predictions, model version, dan inference. Ini menunjukkan arsitektur sistem sudah mendukung alur data dari sensor reading sampai hasil prediksi.

**68. Apa pembagian kerja tim?**

Jawaban bisa disesuaikan dengan pembagian internal. Secara umum, anggota dapat dibagi pada literatur dan protokol medis, pengembangan hardware, model ML, website/backend, dokumentasi, dan koordinasi PKM.

## H. Pertanyaan Kritis dan Jawaban Aman

**69. Kalau belum uji manusia, kenapa berani klaim deteksi prediabetes?**

Kami tidak mengklaim alat ini sudah menjadi alat diagnosis final. Klaim kami adalah pengembangan prototipe deteksi dini prediabetes berbasis saliva yang sedang menuju validasi. Saat ini fokusnya adalah membuktikan integrasi alat, pipeline ML, dan dashboard, lalu tahap berikutnya adalah validasi manusia.

**70. Data ML synthetic, jadi apa gunanya model?**

Synthetic data digunakan untuk membangun dan menguji pipeline secara end-to-end: preprocessing, training, evaluasi, inferensi, API, dan integrasi dashboard. Dengan begitu, saat data manusia tersedia, sistem sudah siap menerima data real tanpa membangun ulang dari awal.

**71. Apakah hasil akurasi dari synthetic data boleh ditampilkan?**

Boleh ditampilkan sebagai hasil teknis pipeline, tetapi harus diberi konteks bahwa itu bukan performa klinis final. Untuk monev, lebih aman mengatakan metrik tersebut adalah indikator kesiapan sistem, bukan bukti alat sudah valid secara klinis.

**72. Apakah SVM masih relevan jika model lain lebih baik?**

Ya, SVM tetap relevan sebagai baseline yang kuat untuk dataset kecil-menengah. Namun kami juga menerapkan model comparison agar keputusan final berbasis hasil evaluasi. Jika data real menunjukkan model lain lebih baik, arsitektur sistem tetap bisa mengakomodasi penggantian model.

**73. Apakah Glicovia bisa menyebabkan misdiagnosis?**

Risiko itu ada jika alat digunakan sebagai diagnosis final. Karena itu posisi kami adalah screening awal dan decision support. Hasil abnormal harus diarahkan ke pemeriksaan lanjutan dengan metode klinis standar.

**74. Bagaimana jika sensor menghasilkan noise?**

Noise ditangani melalui kalibrasi hardware, validasi rentang input, quality flag, preprocessing, dan evaluasi model. Jika data tidak lengkap atau kualitasnya buruk, sistem sebaiknya tidak memaksakan prediksi.

**75. Apa yang paling membedakan Glicovia dari penelitian sebelumnya?**

Glicovia mengintegrasikan biosensor saliva, machine learning, IoT, dan dashboard monitoring dalam satu prototipe. Banyak penelitian berhenti pada biomarker atau model, sedangkan Glicovia diarahkan menjadi sistem penggunaan nyata.

**76. Mengapa tidak memakai deep learning?**

Deep learning biasanya membutuhkan data besar. Untuk tahap awal dengan jumlah data terbatas, model seperti SVR, Ridge, Random Forest, atau Gradient Boosting lebih realistis, lebih mudah divalidasi, dan lebih ringan untuk deployment.

**77. Apakah model interpretabel?**

SVR dengan RBF tidak seinterpretabel model linear. Karena itu model comparison juga menyertakan model linear seperti Ridge. Untuk tahap berikutnya, interpretabilitas dapat ditambah dengan analisis feature importance atau SHAP.

**78. Apakah alat bisa dipakai di puskesmas?**

Target jangka panjangnya iya, karena alat non-invasif dan dashboard monitoring cocok untuk screening. Namun sebelum implementasi di puskesmas, perlu validasi klinis, uji usability, estimasi biaya, dan prosedur operasional yang jelas.

**79. Apakah alat bisa dipakai mandiri di rumah?**

Secara konsep bisa diarahkan ke penggunaan mandiri, tetapi tahap awal lebih aman digunakan dengan pendampingan operator atau tenaga kesehatan agar protokol sampel dan interpretasi hasil tetap benar.

**80. Apa indikator keberhasilan monev kali ini?**

Indikator keberhasilan monev adalah prototipe memiliki rancangan yang jelas, progres teknis terukur, ML pipeline berjalan, dashboard terintegrasi secara arsitektur, ethical clearance tersedia, dan rencana validasi alat realistis untuk diselesaikan.

## I. Jawaban Cepat Per Komponen

**81. Apa itu ESP32?**

ESP32 adalah mikrokontroler yang membaca data dari rangkaian sensor dan mendukung konektivitas untuk pengiriman data ke sistem.

**82. Apa itu ADC?**

ADC adalah Analog-to-Digital Converter, komponen yang mengubah sinyal analog dari sensor menjadi angka digital.

**83. Apa itu SPCE?**

SPCE adalah elektroda cetak berbasis karbon yang digunakan sebagai area reaksi dan pembacaan sinyal elektrokimia.

**84. Apa itu SVR?**

SVR adalah Support Vector Regression, versi regresi dari Support Vector Machine untuk memprediksi nilai kontinu, dalam proyek ini estimasi glukosa darah mg/dL.

**85. Apa itu GridSearchCV?**

GridSearchCV adalah metode pencarian kombinasi hyperparameter terbaik menggunakan cross-validation.

**86. Apa itu RMSE?**

RMSE adalah rata-rata akar kuadrat error prediksi. Makin kecil nilainya, makin dekat prediksi ke nilai referensi.

**87. Apa itu MAE?**

MAE adalah rata-rata selisih absolut antara prediksi dan nilai referensi. Nilainya mudah dibaca karena satuannya sama dengan target, yaitu mg/dL.

**88. Apa itu R2?**

R2 menunjukkan seberapa besar variasi target yang bisa dijelaskan model. Nilai mendekati 1 berarti model menjelaskan data dengan baik, tetapi tetap harus divalidasi pada data real.

**89. Apa itu F1 macro?**

F1 macro adalah rata-rata F1 tiap kelas tanpa terlalu dipengaruhi kelas mayoritas. Ini penting saat data Normal, Pre-Diabetes, dan Diabetes tidak seimbang.

**90. Apa itu IoT dalam Glicovia?**

IoT berarti alat tidak berdiri sendiri, tetapi dapat mengirim data ke sistem digital untuk dipantau, disimpan, dan dianalisis melalui dashboard.

## J. Closing Statement

**Pertanyaan: Apa kesimpulan utama yang ingin disampaikan ke evaluator?**

Glicovia adalah prototipe sistem deteksi dini prediabetes berbasis saliva yang menggabungkan biosensor, machine learning, IoT, dan dashboard monitoring. Kami memahami bahwa klaim klinis membutuhkan validasi manusia, sehingga tahap berikutnya difokuskan pada pengujian sensor, kalibrasi, integrasi alat-web, dan validasi terhadap pemeriksaan standar. Nilai utama proyek ini adalah membangun fondasi teknologi yang siap diuji secara klinis dan berpotensi meningkatkan kepatuhan screening karena metode pengambilannya non-invasif.

