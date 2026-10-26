### Tambahan untuk Metode: Pengumpulan dan Pengolahan Data

Data diperoleh dari sembilan sesi pengukuran saliva, yaitu empat sesi kelas normal (glukosa darah 88 mg/dL) dan lima sesi kelas diabetes (148 mg/dL), dengan label berasal dari nilai glukosa darah referensi pada nama berkas rekaman. Tegangan kanal fruktosamin, glukosa, dan pH dicatat melalui port serial sekitar 2,4 kali per detik. Fase transien 30 detik pertama dibuang dan sisanya dirata-ratakan per jendela 5 detik. Klasifikasi dievaluasi dengan *leave-one-session-out* agar pengambilan data dari sesi yang sama tidak muncul pada data latih dan data uji sekaligus. Konversi tegangan ke satuan riil memakai kalibrasi sementara (V = −0,05916·pH + 0,3226 untuk pH, serta arus penguat transimpedansi dengan Rf 100 kΩ untuk fruktosamin dan glukosa) karena kurva standar belum diselesaikan; karena itu analisis klasifikasi memakai tegangan, bukan nilai satuan riil.

### Pengganti kalimat pada Abstrak (setelah kalimat "Prototipe portabel ...")

Pada sembilan sesi saliva dua kelas (normal dan diabetes), tegangan kanal fruktosamin memisahkan kedua kelas dengan akurasi 100% pada evaluasi *leave-one-session-out*, sedangkan kanal glukosa masih jenuh dan kanal pH memerlukan koreksi offset.

### Pengganti Kesimpulan (tambahan di akhir paragraf)

Pengujian awal pada sembilan sesi saliva menunjukkan bahwa kanal fruktosamin mampu membedakan kelas normal dan diabetes, sedangkan kanal glukosa masih jenuh dan kanal pH memerlukan koreksi offset. Hasil ini bersifat awal karena kalibrasi masih sementara, jumlah sesi terbatas, dan kelas prediabetes belum teruji.

### Catatan konsistensi

Ganti penyebutan "tiga kategori (normal, prediabetes, diabetes)" pada Abstrak dan Metode dengan dua kelas yang diuji, dan sebut klasifikasi tiga kelas serta waktu inferensi 42 ms (data imitasi) sebagai tahap pengembangan terpisah bila tetap dipertahankan.
