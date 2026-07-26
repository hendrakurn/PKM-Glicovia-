## **AMPEROMETRI** 

**TESIS Karya tulis sebagai salah satu syarat untuk memperoleh gelar Magister dari Institut Teknologi Bandung Oleh** 

**(Program Studi Magister Teknik Elektro)** 

## 

**Agustus 2024** 

# **ABSTRAK** 

# **PERA�CA�GA� POTE�SIOSTAT MULTIKA�AL BERBASIS MIKROKO�TROLER U�TUK A�ALISIS KARAKTERISTIK ELEKTROKIMIA BERBASIS VOLTAMETRI DA� AMPEROMETRI** 

Oleh 

# **Theodore Maximillan Jonathan �IM: 23223024** 

**(Program Studi Magister Teknik Elektro)** Penelitian di bidang karakterisasi material dengan metode berbasis elektrokimia berkembang pesat, mengingat kegunaannya yang luas yang mencakup analisis kualitas material serta berbagai penerapan di dunia medis. Salah satu bukti dari kemajuan penelitian di bidang ini adalah berkembangnya potensiostat sebagai alat karakterisasi material berbasis elektrokimia. Potensiostat memberikan umpan tegangan listrik dengan bentuk tertentu pada analit kimia, sehingga diperoleh respons arus yang khas untuk analit yang berbeda. Alat karakterisasi material berbasis elektrokimia memiliki beberapa kelebihan, antara lain dari harga yang relatif lebih rendah, kecepatan analisis yang lebih cepat, serta prinsip kerja yang relatif lebih sederhana dibandingkan metode karakterisasi yang lain. Tesis ini membahas pengembangan potensiostat multikanal berbasis mikrokontroler yang mampu melakukan berbagai pengukuran berbasis voltametri dan _Cyclic Voltammetry_ (CV), _Differential Pulse Voltammetry_ (LSV), dan _Chronoamperometry_ potensiostat menggunakan larutan kalium ferisianat (K3[Fe(CN)63[Fe(CN)6[Fe(CN)66]) menunjukkan akurasi relatif untuk metode pengukuran CV, DPV, LSV, dan CA terhadap hasil pengukuran dengan potensiostat komersil PalmSens4 adalah 95.57%, 90.25%, 88.64%, dan 88.65% untuk pengukuran arus yang mengalir pada larutan. Didapat pula arus yang mengalir pada analit sebanding dengan konsentrasinya pada rentang uji konsentrasi 2.5 mM sampai 20 Kata kunci: amperometri, multikanal, potensiostat, voltametri 

Penelitian di bidang karakterisasi material dengan metode berbasis elektrokimia berkembang pesat, mengingat kegunaannya yang luas yang mencakup analisis kualitas material serta berbagai penerapan di dunia medis. Salah satu bukti dari kemajuan penelitian di bidang ini adalah berkembangnya potensiostat sebagai alat karakterisasi material berbasis elektrokimia. Potensiostat memberikan umpan tegangan listrik dengan bentuk tertentu pada analit kimia, sehingga diperoleh respons arus yang khas untuk analit yang berbeda. Alat karakterisasi material berbasis elektrokimia memiliki beberapa kelebihan, antara lain dari harga yang relatif lebih rendah, kecepatan analisis yang lebih cepat, serta prinsip kerja yang relatif lebih sederhana dibandingkan metode karakterisasi yang lain. Tesis ini membahas pengembangan potensiostat multikanal berbasis mikrokontroler yang mampu melakukan berbagai pengukuran berbasis voltametri dan amperometri, yaitu _Cyclic Voltammetry_ (CV), _Differential Pulse Voltammetry_ (DPV), _Linear Sweep Voltammetry_ (LSV), dan _Chronoamperometry_ (CA). Pengujian potensiostat menggunakan larutan kalium ferisianat (K3[Fe(CN)63[Fe(CN)6[Fe(CN)66]) menunjukkan akurasi relatif untuk metode pengukuran CV, DPV, LSV, dan CA terhadap hasil pengukuran dengan potensiostat komersil PalmSens4 adalah 95.57%, 90.25%, 88.64%, dan 88.65% untuk pengukuran arus yang mengalir pada larutan. Didapat pula arus yang mengalir pada analit sebanding dengan konsentrasinya pada rentang uji konsentrasi 2.5 mM sampai 20 mM untuk kedua kanal. 

Kata kunci: amperometri, multikanal, potensiostat, voltametri 

ii 

# _**ABSTRACT**_ 

# _**DEVELOPMENT OF MICROCONTROLLER-BASED MULTICHANNEL POTENTIOSTAT FOR ELECTROCHEMICAL ANALYSIS WITH VOLTAMMETRIC AND AMPEROMETRIC METHODS**_ 

# _By_ **Theodore Maximillan Jonathan �IM: 23223024** 

_**(Master’s Program in Electrical Engineering)** Research in the field of material characterization using electrochemical methods has been developing rapidly, given its wide range of applications, including material quality analysis and various medical applications. One of the evidence of progress in this field includes the development of potentiostat as a characterization tool with electrochemical methods. A potentiostat provides a specific voltage trigger to a chemical analyte, resulting in different current responses for different analytes. Electrochemical-based material characterization tools have several advantages, including lower costs, faster analysis speed, and simpler working principles compared to other characterization methods. This thesis discusses the development of a multichannel potentiostat based on a microcontroller capable of performing various voltammetry and amperometry measurements, including Cyclic Voltammetry (CV), Differential Pulse Voltammetry (DPV), Linear Sweep Voltammetry (LSV), and Chronoamperometry (CA). By testing the potentiostat using potassium ferricyanide solution (K[[3]] [Fe(CN)[[6]] relative accuracy for the CV, DPV, LSV, and CA measurement methods compared to measurements with the commercial potentiostat PalmSens4, which were 95.57%, 90.25%, 88.64%, and 88.65% respectively for the current measurements in the solution. It was also found that the current flowing in the analyte was proportional to its concentration in the test concentration range of 2.5 mM to 20 mM for both channels. Keywords: amperometry, multichannel, potentiostat, voltammetry._ 

_Research in the field of material characterization using electrochemical methods has been developing rapidly, given its wide range of applications, including material quality analysis and various medical applications. One of the evidence of progress in this field includes the development of potentiostat as a characterization tool with electrochemical methods. A potentiostat provides a specific voltage trigger to a chemical analyte, resulting in different current responses for different analytes. Electrochemical-based material characterization tools have several advantages, including lower costs, faster analysis speed, and simpler working principles compared to other characterization methods. This thesis discusses the development of a multichannel potentiostat based on a microcontroller capable of performing various voltammetry and amperometry measurements, including Cyclic Voltammetry (CV), Differential Pulse Voltammetry (DPV), Linear Sweep Voltammetry (LSV), and Chronoamperometry (CA). By testing the potentiostat using potassium ferricyanide solution (K[[3]] [Fe(CN)[[6]] ]), it shows that the relative accuracy for the CV, DPV, LSV, and CA measurement methods compared to measurements with the commercial potentiostat PalmSens4, which were 95.57%, 90.25%, 88.64%, and 88.65% respectively for the current measurements in the solution. It was also found that the current flowing in the analyte was proportional to its concentration in the test concentration range of 2.5 mM to 20 mM for both channels._ 

_Keywords: amperometry, multichannel, potentiostat, voltammetry._ 

iii 

## **AMPEROMETRI** 

Oleh **Theodore Maximillan Jonathan** 

**(Program Studi Magister Teknik Elektro)** 

Institut Teknologi Bandung Menyetujui Tim Pembimbing Tanggal 30 Juli 2024 Ketua Digitally signed by isa anshori Date: 2024.08.14 (he 16:12:47 +07'00' 

Institut Teknologi Bandung 

Isa Anshori, S.T., M.Eng., Ph.D. 

An **gg** ota Dr. Eng. Ir. Infall Syafalni, S.T., M.Sc. 

iv 

## **PEDOMA� PE�GGU�AA� TESIS** 

Tesis Magister yang tidak dipublikasikan terdaftar dan tersedia di Perpustakaan Institut Teknologi Bandung, dan terbuka untuk umum dengan ketentuan bahwa hak cipta ada pada penulis dengan mengikuti aturan HaKI yang berlaku di Institut Teknologi Bandung. Referensi kepustakaan diperkenankan dicatat, tetapi pengutipan atau peringkasan hanya dapat dilakukan seizin penulis dan harus disertai dengan kaidah ilmiah untuk menyebutkan sumbernya. 

- Sitasi hasil penelitian Tesis ini dapat di tulis dalam bahasa Indonesia sebagai berikut: _Perancangan potensiostat multikanal berbasis mikrokontroler_ 

- _untuk analisis karakteristik elektrokimia berbasis voltametri dan amperometri,_ Tesis Program Magister, Institut Teknologi Bandung. 

- dan dalam bahasa Inggris sebagai berikut: _Development of microcontroller-based multichannel potentiostat_ 

- _for electrochemical analysis with voltammetric and amperometric methods_ Master’s Thesis, Institut Teknologi Bandung. 

- Memperbanyak atau menerbitkan sebagian atau seluruh tesis haruslah seizin Dekan Sekolah Pascasarjana, Institut Teknologi Bandung. 

dan dalam bahasa Inggris sebagai berikut: 

**==> picture [429 x 40] intentionally omitted <==**

**----- Start of picture text -----**<br>
Jonathan, T.M. (2024):  Development of microcontroller-based multichannel potentiostat<br>for electrochemical analysis with voltammetric and amperometric methods ,<br>Master’s Thesis, Institut Teknologi Bandung.<br>**----- End of picture text -----**<br>


Memperbanyak atau menerbitkan sebagian atau seluruh tesis haruslah seizin Dekan Sekolah Pascasarjana, Institut Teknologi Bandung. 

Sitasi hasil penelitian Tesis ini dapat di tulis dalam bahasa Indonesia sebagai berikut: Jonathan, T.M. (2024): _Perancangan potensiostat multikanal berbasis mikrokontroler untuk analisis karakteristik elektrokimia berbasis voltametri dan amperometri,_ Tesis Program Magister, Institut Teknologi Bandung. 

v 

_“All my life, You have been faithful. All my life, You have been so, so good. With every breath that I am able, I will sing of the goodness of God.” – Goodness of God, Bethel Music_ 

_Untuk Amah_ 

vi 

## **KATA PE�GA�TAR** 

Puji syukur kepada Tuhan Yesus sehingga pada akhirnya, penulisan tesis ini dapat selesai walaupun telah melewati berbagai halangan. Satu tahun yang sulit, namun puji Tuhan lewat fase kehidupan ini, penulis mendapat berbagai pelajaran, baik dari segi ilmu pengetahuan maupun terkait kehidupan itu sendiri. Selama penyusunan tesis ini, penulis juga mendapat banyak sekali bimbingan dan bantuan, dan oleh karena itu penulis hendak mengucapkan terima kasihnya kepada: 

Bapak Isa Anshori, S.T., M.Eng., Ph.D. dan Bapak Dr.Eng. Ir. Infall Syafalni, S.T., M.Sc. selaku dosen pembimbing atas segala bantuan dan kesabarannya dalam membimbing penulis selama dua tahun terakhir di penelitian ini. Kedua orang tua saya, Bapak Lukas Jonathan, S.T. dan Ibu Suzanne Mondigir, S.E. atas dukungan yang tak hentinya diberikan selama penyusunan tesis ini. Saudara Christian Reivan, S.T. dan Gotawa Aryo Prakoso, S.T. atas seluruh bantuannya dalam perancangan dan pengujian potensiostat tesis ini. Bapak Sandra Irawan, A.Md. dan Bapak Aby Rahmat Fadhillah, S.Si. selaku teknisi di Laboratorium Dasar Teknik Elektro untuk fasilitas yang diberikan selama pengujian potensiostat dalam tesis ini. Rekan-rekan di ruang Laboratorium Sol-Gel PPNN: Kak Geolita, Kak Indah, Kak Nadia, dan Uperianti untuk bantuannya selama proses eksperimen berlangsung. Saudara Carlos Christopher Hutahean dan Saudari Retta Tampubolon atas dukungan moral yang diberikan selama masa-masa genting penyusunan tesis ini. Adik-adikku di Excelsis Learning Center yang telah memberikan warna pada kehidupan penulis selama menempuh pendidikan S2 di ITB. Rekan-rekan di Gereja Injili Indonesia (GII) Hok Im Tong Dago untuk doa yang tak henti-hentinya dipanjatkan selama penyusunan tesis ini. 

1. Bapak Isa Anshori, S.T., M.Eng., Ph.D. dan Bapak Dr.Eng. Ir. Infall Syafalni, 

- bantuannya dalam perancangan dan pengujian potensiostat tesis ini. 

- 4. Bapak Sandra Irawan, A.Md. dan Bapak Aby Rahmat Fadhillah, S.Si. selaku teknisi di Laboratorium Dasar Teknik Elektro untuk fasilitas yang diberikan selama pengujian potensiostat dalam tesis ini. 

- 5. Rekan-rekan di ruang Laboratorium Sol-Gel PPNN: Kak Geolita, Kak Indah, Kak Nadia, dan Uperianti untuk bantuannya selama proses eksperimen berlangsung. 

- 6. Saudara Carlos Christopher Hutahean dan Saudari Retta Tampubolon atas dukungan moral yang diberikan selama masa-masa genting penyusunan tesis ini. 

- 7. Adik-adikku di Excelsis Learning Center yang telah memberikan warna pada kehidupan penulis selama menempuh pendidikan S2 di ITB. 

8. Rekan-rekan di Gereja Injili Indonesia (GII) Hok Im Tong Dago untuk doa yang tak henti-hentinya dipanjatkan selama penyusunan tesis ini. 

9. dan pihak-pihak lain yang tidak bisa disebutkan satu per satu. 

Penulis berharap tesis ini bisa bermanfaat bagi orang-orang yang hendak menggunakannya dan dapat dikembangkan kembali di masa yang akan datang. 

Bandung, 30 Juli 2024 Theodore Maximillan Jonathan 

S.T., M.Sc. selaku dosen pembimbing atas segala bantuan dan kesabarannya dalam membimbing penulis selama dua tahun terakhir di penelitian ini. 2. Kedua orang tua saya, Bapak Lukas Jonathan, S.T. dan Ibu Suzanne Mondigir, S.E. atas dukungan yang tak hentinya diberikan selama penyusunan tesis ini. 3. Saudara Christian Reivan, S.T. dan Gotawa Aryo Prakoso, S.T. atas seluruh 

vii 

## **DAFTAR ISI** 

**==> picture [400 x 606] intentionally omitted <==**

**----- Start of picture text -----**<br>
||||
|---|---|---|
|ABSTRAK  ........................................................................................................... ii|
|ABSTRACT|..........................................................................................................iii|
|PEDOMAN PENGGUNAAN TESIS ..................................................................... v|
|HALAMAN PERUNTUKAN ................................................................................. v|
|KATA PENGANTAR ........................................................................................... vii|
|DAFTAR ISI  ........................................................................................................viii|
|DAFTAR LAMPIRAN ........................................................................................... x|
|DAFTAR GAMBAR DAN ILUSTRASI............................................................... xi|
|DAFTAR TABEL ................................................................................................. xii|
|DAFTAR SINGKATAN DAN LAMBANG .......................................................xiii|
|Bab I    Pendahuluan .............................................................................................. 14|
|I.1|Latar Belakang ............................................................................. 14|
|I.2|Rumusan Masalah ........................................................................ 16|
|I.3|Batasan Masalah .......................................................................... 16|
|I.4|Tujuan Penelitian ......................................................................... 16|
|I.5|Sistematika Penulisan .................................................................. 17|
|Bab II    Tinjauan Pustaka ..................................................................................... 19|
|II.1|Biosensor dan Sensor Kimia ........................................................ 19|
|II.2|Analisis Voltametri dan Amperometri ......................................... 21|
|II.3|Rangkaian Potensiostat Standar ................................................... 27|
|Bab III    Metode Penelitian dan Perancangan ...................................................... 30|
|III.1 Rancangan Skema Penelitian ....................................................... 30|
|III.1.1      Alur Kerja Penelitian .............................................................. 30|
|III.1.2      Konsep Interaksi Sistem.......................................................... 32|
|III.1.3      Rancangan Dasar Perangkat Keras ......................................... 33|
|III.1.4      Modul dan Komponen yang Digunakan ................................. 41|
|III.1.5      Rangkaian Dasar Perangkat Lunak ......................................... 45|
|III.2 Skema Perangkat Keras ............................................................... 47|
|III.2.1      Skematik Perangkat Keras ...................................................... 47|
|III.2.2      Skema Komunikasi dengan PC ............................................... 49|
|III.3 Skema Perangkat Lunak (|Firmware|) Potensiostat ....................... 50|
|III.3.1      Algoritma|Cyclic Voltammetry|(CV) ...................................... 50|
|III.3.2      Algoritma|Differential Pulse Voltammetry|(DPV) ................. 53|
|III.3.3      Algoritma|Linear Sweep Voltammetry|(LSV) ........................ 54|
|III.3.4      Algoritma|Chronoamperometry|(CA) .................................... 55|
|III.4 Rancangan PCB Potensiostat ....................................................... 56|
|III.4.1      Penempatan Komponen/|Layout|pada PCB ............................. 56|
|III.4.2      Rancangan Rangkaian Fisik PCB ........................................... 57|
|III.5 Perangkat Pembanding ................................................................. 58|
|III.6 Harga ............................................................................................ 58|
|Bab IV    Pengujian Sistem .................................................................................... 60|
|IV.1 Desain Skema Pengujian .............................................................. 60|
|IV.1.1     Skema Pengujian ..................................................................... 60|
|IV.1.2     Parameter Pengujian ............................................................... 60|

**----- End of picture text -----**<br>


viii 

|IV.2 Hasil Pengujian ............................................................................ 62|
|---|
|IV.2.1     Bentuk Tegangan Keluaran ..................................................... 62|
|IV.2.2     Pengujian Karakteristik Elektrokimia Senyawa K3[Fe(CN)6] 65|
|IV.3 Posisi Riset ................................................................................... 80|
|Bab V    Kesimpulan.............................................................................................. 83|
|V.1<br>Kesimpulan .................................................................................. 83|
|V.2<br>Saran............................................................................................. 84|
|DAFTAR PUSTAKA ............................................................................................ 86|
|LAMPIRAN  ......................................................................................................... 89|



## 

ix 

## **DAFTAR LAMPIRA�** 

Lampiran A: Prosedur Aktivasi Elektroda Karbon (SPCE) ............................................89 

## 

x 

## **DAFTAR GAMBAR DA� ILUSTRASI** 

|Gambar II.1 Komponen-komponen penyusun biosensor ...................................... 19|
|---|
|Gambar II.2 Tegangan input dan output berbagai pengukuran elektrokimia ........ 23|
|Gambar II.3 Parameter input dan contoh voltamogram hasil pengukuran DPV ... 24|
|Gambar II.4 Kurva input untuk LSV dan voltamogram hasil pengukuran LSV ... 26|
|Gambar II.5 Tegangan masukan dan arus keluaran pengukuran CA<br>27|
|Gambar II.6 Skema rangkaian potensiostat ........................................................... 28|
|Gambar II.7 Contoh implementasi sistem potensiostat ......................................... 28|
|Gambar III.1 Alur penelitian……………………………………………………..30|
|Dokumen Asli<br>Gambar III.2 Desain interaksi sistem potensiostat dengan pengguna ................... 32<br>Gambar III.3 Skema rangkaian_level shifter_.......................................................... 35<br>Gambar III.4 Rangkaian antarmuka dengan sel elektrokimia ............................... 36<br>Gambar III.5 Rangkaian penguat transimpedansi ................................................. 37<br>Gambar III.6 Rangkaian_Low-Pass-Filter_(LPF) Sallen-Key ............................... 38<br>Gambar III.7 Rangkaian penggeser tegangan keluaran ......................................... 40<br>Gambar III.8 Rangkaian RC sebagai filter antialiasing ......................................... 41<br>Gambar III.9 Susunan pin (_pinout_) dari multiplexer ADG409BRZ ...................... 44<br>Gambar III.10 Skema rangkaian pengolah data potensiostat ................................ 48<br>Gambar III.11 Skema komunikasi data potensiostat dengan PC........................... 49<br>Gambar III.12 Rangkaian komunikasi data antara potensiostat dengan PC .......... 50<br>Gambar III.13 Rencana_layout_komponen pada PCB............................................ 56<br>Gambar III.14 Hasil_layouting_pada perangkat lunak KiCad ................................ 57<br>Gambar III.15 Hasil 3D_Rendering_dari rangkaian potensiostat ........................... 58<br>Gambar IV.1 Contoh kurva voltamogram CV…………………………………...61<br>Gambar IV.2 Contoh kurva kalibrasi .................................................................... 61<br>Gambar IV.3 (a) Contoh kurva arus CA dan (b) Contoh kurva kalibrasi CA ....... 62<br>Gambar IV.4 Hasil tegangan keluaran CV ............................................................ 63<br>Gambar IV.5 Hasil tegangan keluaran LSV .......................................................... 64<br>Gambar IV.6 Hasil tegangan keluaran DPV ......................................................... 64<br>Gambar IV.7 Hasil tegangan keluaran CA ............................................................ 65<br>Gambar IV.8 Hasil pengujian CV larutan K3[Fe(CN)6] pada Channel 1 .............. 66<br>Gambar IV.9 Hasil pengujian CV larutan K3[Fe(CN)6] pada Channel 2 .............. 66<br>Gambar IV.10 Hasil kurva kalibrasi CV larutan K3[Fe(CN)6] .............................. 68<br>Gambar IV.11 Hasil pengujian LSV larutan K3[Fe(CN)6] pada Channel 1 .......... 71<br>Gambar IV.12 Hasil pengujian LSV larutan K3[Fe(CN)6] pada Channel 2 .......... 71|
|Gambar IV.13 Hasil kurva kalibrasi LSV larutan K3[Fe(CN)6] ............................ 73|
|Gambar IV.14 Hasil pengujian DPV larutan K3[Fe(CN)6] pada Channel 1 ......... 74|
|Gambar IV.15 Hasil pengujian DPV larutan K3[Fe(CN)6] pada Channel 2 ......... 75|
|Gambar IV.16 Hasil kurva kalibrasi DPV larutan K3[Fe(CN)6] ........................... 76|
|Gambar IV.17 Hasil pengujian CA larutan K3[Fe(CN)6] pada Channel 1 ............ 78|
|Gambar IV.18 Hasil pengujian CA larutan K3[Fe(CN)6] pada Channel 2 ............ 78|
|Gambar IV.19 Hasil kurva kalibrasi CA larutan K3[Fe(CN)6] .............................. 80|



xi 

## **DAFTAR TABEL** 

Tabel II.1 Biaya produksi potensiostat .................................................................. 59 Tabel IV.1 Data arus anodik CV larutan K3[Fe(CN)6] .......................................... 67 Tabel IV.2 Data arus katodik CV larutan K3[Fe(CN)6]......................................... 67 Tabel IV.3 Persamaan kurva kalibrasi CV larutan K3[Fe(CN)6] ........................... 70 Tabel IV.4 Rentang konsentrasi larutan K3[Fe(CN)6] metode CV ....................... 70 Tabel IV.5 Data arus LSV larutan K3[Fe(CN)6] .................................................... 72 Tabel IV.6 Persamaan kurva kalibrasi LSV larutan K3[Fe(CN)6]......................... 73 Tabel IV.7 Rentang konsentrasi terukur larutan K3[Fe(CN)6] metode LSV ......... 74 Tabel IV.8 Data arus DPV larutan K3[Fe(CN)6] ................................................... 75 Tabel IV.9 Persamaan kurva kalibrasi DPV larutan K3[Fe(CN)6] ........................ 76 Tabel IV.10 Rentang konsentrasi terukur larutan K3[Fe(CN)6] metode DPV ...... 77 Tabel IV.11 Data arus _steady-state_ CA larutan K3[Fe(CN)6] ............................... 79 Tabel IV.12 Persamaan kurva kalibrasi CA larutan K3[Fe(CN)6]......................... 80 Tabel IV.13 Persamaan kurva kalibrasi CA larutan K3[Fe(CN)6]......................... 81 

xii 

## **DAFTAR SI�GKATA� DA� LAMBA�G** 

|SINGKATAN|Nama|Pemakaian|
|---|---|---|
|||pertama kali|
|||pada halaman|
|CV|_Cyclic Voltammetry_|15|
|DPV|_Differential Pulse Voltammetry_|15|
|CA|_Chronoamperometry_|25|
|LSV|_Linear Sweep Voltammetry_|26|
|CE|_Counter Electrode_|27|
|WE|_Working Electrode_|28|
|Dokumen Asli<br>RE<br>_Reference Electrode_<br>28<br>LoD<br>_Limit of Detection_<br>15<br>SPCE<br>_Screen Printed Carbon Electrode_<br>27<br>PCB<br>_Printed Circuit Board_<br>16<br>TIA<br>_Transimpedance Amplifier_<br>28<br>ADC<br>_Analog to Digital Converter_<br>29<br>DAC<br>_Digital to Analog Converter_<br>29<br>LAMBANG<br>_A_<br>Luas elektroda<br>25<br>_C0 _<br>Konsentrasi awal analit pada permukaan<br>elektroda<br>25<br>�� <br>Konsentrasi akhir analit pada permukaan<br>elektroda<br>26<br>_D0 _<br>Koefisien difusi analit<br>25<br>_E_<br>Potensial reduksi/oksidasi sel di luar<br>konsentrasi standar<br>22<br>_E0 _<br>Potensial reduksi/oksidasi sel pada<br>konsentrasi standar (1 M)<br>22<br>_F_<br>Konstanta Faraday (96.485 C/mol)<br>22<br>_IWE_<br>Arus pada Working Electrode (WE), yang<br>bernilai sama dengan arus pada analit<br>37<br>_Ip _<br>Arus puncak pada analit<br>25<br>_n_<br>Jumlah mol elektron pada reaksi<br>stoikiometri redoks<br>22|||
|_R_|Konstanta gas ideal|22|
|_Rg _|Resistansi gain pada TIA|37|
|_t_|Waktu|26|
|_T_|Temperatur|22|
|_v_|Kecepatan pindai (_scan rate_)|25|
|_vin_|Tegangan keluaran ADC|34|
|_vsweep_|Tegangan yang dirasakan analit|35|
|_vTIA_|Tegangan keluaran TIA|37|



xiii 

## **Bab I    Pendahuluan** 

## **I.1 Latar Belakang** 

Karakterisasi material berbasis metode elektrokimia menjadi sorotan dalam bidang riset dewasa ini, mengingat kemudahan dan praktikalitasnya dibandingkan metode karakterisasi material yang lain. Beberapa kegunaan karakterisasi material berbasis elektrokimia antara lain untuk melakukan karakterisasi material dan menentukan 

kandungan suatu zat dalam sebuah sampel. Aplikasi dari karakterisasi berbasis elektrokimia mencakup pendeteksian bakteri atau virus tertentu dalam sebuah sampel organik dengan menggunakan bantuan biosensor, menentukan kualitas air melalui pendeteksian kandungan kontaminan, dan pendeteksian kontaminan anorganik seperti 2O2) pada sebuah sampel. O2) pada sebuah sampel. 2) pada sebuah sampel. ) pada sebuah sampel. Karakterisasi berbasis elektrokimia juga sangat dekat dengan kehidupan sehari-hari, contohnya adalah alat glukometer, yakni alat untuk mendeteksi kadar gula dalam darah. Dengan sedikit darah pasien yang diteteskan ke atas test strip yang kemudian dihubungkan dengan glukometer, pasien dapat mengetahui konsentrasi gula dalam darah. Salah satu alat yang dibutuhkan dalam karakterisasi material berbasis elektrokimia adalah potensiostat. Potensiostat menerima sinyal listrik dari tetesan analit yang diteteskan di atas lembaran biosensor, kemudian mengolah sinyal tersebut menjadi data profil elektrokimia dari analit yang dapat diinterpretasikan oleh operator atau analis yang menggunakan potensiostat tersebut. Penggunaan potensiostat sendiri memungkinkan analisis elektrokimia secara cepat dengan akurasi yang tinggi, serta dapat mendeteksi kandungan analit dalam konsentrasi yang sangat kecil. 

Karakterisasi berbasis elektrokimia juga sangat dekat dengan kehidupan sehari-hari, contohnya adalah alat glukometer, yakni alat untuk mendeteksi kadar gula dalam darah. Dengan sedikit darah pasien yang diteteskan ke atas test strip yang kemudian dihubungkan dengan glukometer, pasien dapat mengetahui konsentrasi gula dalam darah. Salah satu alat yang dibutuhkan dalam karakterisasi material berbasis elektrokimia adalah potensiostat. Potensiostat menerima sinyal listrik dari tetesan analit yang diteteskan di atas lembaran biosensor, kemudian mengolah sinyal tersebut menjadi data profil elektrokimia dari analit yang dapat diinterpretasikan oleh operator atau analis yang menggunakan potensiostat tersebut. Penggunaan potensiostat sendiri memungkinkan analisis elektrokimia secara cepat dengan akurasi yang tinggi, serta dapat mendeteksi kandungan analit dalam konsentrasi yang sangat kecil. 

Namun, salah satu keterbatasan dari perkembangan potensiostat sekarang ini adalah informasi terkait potensiostat yang masih terbatas pada kalangan tertentu, sehingga menyebabkan perkembangan potensiostat sekarang ini seringkali memiliki tujuan komersil, dan menyebabkan harga jualnya menjadi tidak terjangkau. Melihat keterbatasan ini, terdapat urgensi untuk mengembangkan potensiostat dengan keandalan yang baik, namun dengan harga yang terjangkau, mengingat potensiostat memiliki manfaat yang 

kandungan suatu zat dalam sebuah sampel. Aplikasi dari karakterisasi berbasis elektrokimia mencakup pendeteksian bakteri atau virus tertentu dalam sebuah sampel organik dengan menggunakan bantuan biosensor, menentukan kualitas air melalui pendeteksian kandungan kontaminan, dan pendeteksian kontaminan anorganik seperti hidrogen peroksida (H2O2) pada sebuah sampel. O2) pada sebuah sampel. 2) pada sebuah sampel. ) pada sebuah sampel. 

14 

luas, baik untuk analisis dan karakterisasi zat, sampai menjadi alat bantu dalam bidang pendidikan. 

Salah satu bidang riset baru yang dapat menjadi arah perkembangan potensiostat berikutnya adalah pendeteksian material dengan bantuan imobilisasi zat. Salah satunya adalah untuk pendeteksian bakteri E. coli yang membutuhkan biosensor berbasis emas (Au) yang telah diimobilisasi oleh 11-mercaptoundecanoic acid (MUA) sehingga dapat mengikat bakteri E. coli di atas permukaan elektroda ketika keberadaannya terdeteksi[1]. 

Potensiostat di masa kini juga dikembangkan supaya bersifat portabel dan dapat digunakan di luar lingkungan laboratorium. Pengembangan berikutnya juga dilakukan dalam realisasi algoritma pengolahan sinyal potensiostat, salah satunya yaitu penggunaan rangkaian filter untuk mengurangi pengaruh derau (noise) pada sinyal bacaan potensiostat sehingga hasil bacaan potensiostat menjadi lebih akurat. Pemilihan jenis metode analisis elektrokimia juga penting dilakukan supaya terpilih metode yang paling cocok dengan analit yang hendak diteliti, sehingga potensiostat harus mampu melakukan pengujian elektrokimia dengan berbagai metode. Metode Cyclic Voltammetry (CV) menganalisis profil elektrokimia pada sebuah analit yang mencakup tegangan redoks dan arus redoks analit. Metode CV dapat dilakukan untuk mendeteksi penyakit pada sampel dari pasien, contohnya pendeteksian keberadaan aseton pada tubuh pasien sebagai indikator penyakit diabetes[2]. Metode Differential Pulse Voltammetry (DPV) telah berhasil mendeteksi keberadaan beberapa sampel obat dalam urin manusia yang mencakup parasetamol, dipyrone, cefazolin, dan dexamethasone[3]. Metode Electrochemical Impedance Spectroscopy (EIS) yang berbasis impedimetri umumnya 

Pemilihan jenis metode analisis elektrokimia juga penting dilakukan supaya terpilih metode yang paling cocok dengan analit yang hendak diteliti, sehingga potensiostat harus mampu melakukan pengujian elektrokimia dengan berbagai metode. Metode Cyclic Voltammetry (CV) menganalisis profil elektrokimia pada sebuah analit yang mencakup tegangan redoks dan arus redoks analit. Metode CV dapat dilakukan untuk mendeteksi penyakit pada sampel dari pasien, contohnya pendeteksian keberadaan aseton pada tubuh pasien sebagai indikator penyakit diabetes[2]. Metode Differential Pulse Voltammetry (DPV) telah berhasil mendeteksi keberadaan beberapa sampel obat dalam urin manusia yang mencakup parasetamol, dipyrone, cefazolin, dan dexamethasone[3]. Metode Electrochemical Impedance Spectroscopy (EIS) yang berbasis impedimetri umumnya digunakan untuk mendeteksi keberadaan zat yang tidak bersifat elektroaktif dan telah berhasil mendeteksi keberadaan bakteri _E. coli_ dalam sampel analit[1]. 

Potensiostat juga dapat direalisasikan menggunakan mikrokontroler yang umum, seperti Raspberry Pi[5], Arduino[4], dan ESP32[6] dengan parameter performa yang cukup baik (seperti Limit of Detection (LoD) dan Linear Range) dibandingkan potensiostat yang dijual secara komersil. 

Potensiostat di masa kini juga dikembangkan supaya bersifat portabel dan dapat digunakan di luar lingkungan laboratorium. Pengembangan berikutnya juga dilakukan dalam realisasi algoritma pengolahan sinyal potensiostat, salah satunya yaitu penggunaan rangkaian filter untuk mengurangi pengaruh derau (noise) pada sinyal bacaan potensiostat sehingga hasil bacaan potensiostat menjadi lebih akurat. 

15 

## **I.2 Rumusan Masalah** 

Dari paparan latar belakang yang telah disampaikan, terdapat beberapa poin penting terkait pengembangan potensiostat, yakni isu harga potensiostat yang mahal, kebutuhan potensiostat untuk mudah digunakan, serta kemampuan potensiostat untuk melakukan beragam jenis analisis elektrokimia. Beberapa permasalahan yang hendak diangkat dalam penelitian ini antara lain: 

1. Apa saja bagian-bagian yang dibutuhkan dalam perancangan potensiostat yang low-cost namun memiliki keandalan yang baik? 

   - low-cost namun memiliki keandalan yang baik? Apa saja metode pengukuran yang dapat direalisasikan oleh potensiostat? Bagaimana performa potensiostat yang dirancang apabila dibandingkan dengan potensiostat komersil? **Batasan Masalah** 

   - Batasan masalah dari penelitian ini antara lain: Potensiostat yang dirancang harus _portable_ dan memiliki massa kurang dari 1 kg sehingga mudah dibawa apabila terdapat kebutuhan untuk melakukan percobaan di luar laboratorium. Potensiostat yang dirancang harus memiliki suplai tegangan maksimal 5 V untuk meminimalisasi kebutuhan daya dari potensiostat. Potensiostat harus menggunakan komponen yang relatif mudah dicari di pasaran sehingga dapat menekan total harga komponen yang diperlukan. Potensiostat harus mampu melakukan pengukuran elektrokimia berbasis voltametri dan amperometri. Desain potensiostat harus berbasis mikrokontroler dan dapat disusun dalam satu 

2. Apa saja metode pengukuran yang dapat direalisasikan oleh potensiostat? 

3. Bagaimana performa potensiostat yang dirancang apabila dibandingkan dengan potensiostat komersil? 

## **I.3 Batasan Masalah** 

- Batasan masalah dari penelitian ini antara lain: 1. Potensiostat yang dirancang harus _portable_ dan memiliki massa kurang dari 1 kg sehingga mudah dibawa apabila terdapat kebutuhan untuk melakukan percobaan di luar laboratorium. 

   2. Potensiostat yang dirancang harus memiliki suplai tegangan maksimal 5 V untuk meminimalisasi kebutuhan daya dari potensiostat. 

   3. Potensiostat harus menggunakan komponen yang relatif mudah dicari di pasaran sehingga dapat menekan total harga komponen yang diperlukan. 

   4. Potensiostat harus mampu melakukan pengukuran elektrokimia berbasis voltametri dan amperometri. 

   5. Desain potensiostat harus berbasis mikrokontroler dan dapat disusun dalam satu PCB untuk mendukung portabilitas potensiostat. 

   6. Data pengukuran harus dapat disimpan oleh pengguna sehingga dapat dianalisis kembali setelah percobaan dilakukan. 

## **I.4 Tujuan Penelitian** 

Tujuan penelitian ini antara lain: 

16 

1. Merancang potensiostat yang _low-cost_ (memiliki harga produksi di bawah Rp2.000.000,00) dan memiliki akurasi di atas 85% dibandingkan potensiostat komersil. 

2. Mengimplementasikan potensiostat yang mampu melakukan berbagai jenis pengukuran elektrokimia berbasis voltametri dan amperometri. 

3. Melakukan pengujian dari performa potensiostat yang dirancang dan membandingkan hasilnya dengan hasil pengukuran dari potensiostat komersil. 

   - **Sistematika Penulisan** 

   - Susunan penulisan tesis ini dirangkum dalam beberapa bab sebagai berikut: BAB 1 PENDAHULUAN Bab ini membahas terkait perkembangan dari potensiostat serta urgensi melakukan pengembangan potensiostat yang andal dan ekonomis. Dibahas juga terkait kebutuhan potensiostat yang mudah untuk dioperasikan dan mampu melakukan pengujian karakteristik elektrokimia dengan berbagai metode pengukuran. BAB 2 STUDI PUSTAKA Bab ini membahas terkait teori yang mendasari penelitian ini, mencakup prinsip kerja sensor elektrokimia dan biosensor, skema standar kerja potensiostat, serta teori terkait aplikasi mikrokontroler dan perangkat antarmuka pengguna ( _interface_ ) untuk merealisasikan potensiostat. BAB 3 DESAIN DAN PERANCANGAN SISTEM 

## **I.5 Sistematika Penulisan** 

**==> picture [394 x 95] intentionally omitted <==**

**----- Start of picture text -----**<br>
Bab ini membahas terkait perkembangan dari potensiostat serta urgensi<br>melakukan pengembangan potensiostat yang andal dan ekonomis. Dibahas juga<br>terkait kebutuhan potensiostat yang mudah untuk dioperasikan dan mampu<br>melakukan pengujian karakteristik elektrokimia dengan berbagai metode<br>pengukuran.<br>**----- End of picture text -----**<br>


## 2. BAB 2 STUDI PUSTAKA 

Bab ini membahas terkait teori yang mendasari penelitian ini, mencakup prinsip kerja sensor elektrokimia dan biosensor, skema standar kerja potensiostat, serta teori terkait aplikasi mikrokontroler dan perangkat antarmuka pengguna ( _user interface_ ) untuk merealisasikan potensiostat. 

## 3. BAB 3 DESAIN DAN PERANCANGAN SISTEM 

Bab ini membahas proses penentuan bagian-bagian penting dan komponenkomponen yang dibutuhkan dalam sistem potensiostat supaya dapat mengimplementasikan fungsionalitas yang diperlukan. Akan dibahas pula arsitektur dari potensiostat yang mencakup susunan perangkat keras maupun keterkaitan antarkomponen perangkat lunak yang digunakan, serta alasan pemilihan komponen-komponen tersebut. 

Susunan penulisan tesis ini dirangkum dalam beberapa bab sebagai berikut: 1. BAB 1 PENDAHULUAN 

17 

## 4. BAB 4 IMPLEMENTASI DAN PENGUJIAN 

Bab ini membahas pengujian potensiostat dalam melakukan pengukuran elektrokimia pada analit serta membandingkan hasilnya dengan pengukuran yang dilakukan oleh potensiostat komersial. Dibahas pula alasan di balik perbedaan pengukuran antara kedua potensiostat dan faktor-faktor yang dapat mempengaruhi kualitas hasil pengukuran dari potensiostat yang dirancang. 

## 5. BAB 5 KESIMPULAN 

- Bagian ini membahas hasil dari penelitian ini dan merangkum informasi penting yang didapat dari penelitian ini, seperti spesifikasi potensiostat yang hendak dirancang dan hasil pengujian potensiostat secara umum. 

Bagian ini membahas hasil dari penelitian ini dan merangkum informasi penting yang didapat dari penelitian ini, seperti spesifikasi potensiostat yang hendak dirancang dan hasil pengujian potensiostat secara umum. 

18 

## **Bab II    Tinjauan Pustaka** 

## **II.1 Biosensor dan Sensor Kimia** 

Biosensor adalah alat yang mampu mengukur keberadaan zat biologis atau reaksi kimia yang terdapat pada sebuah analit melalui pemberian sinyal listrik dan pengamatan respons sinyal dari analit. Terdapat beberapa bagian penting dalam biosensor yang diilustrasikan pada Gambar II.1. 

**==> picture [370 x 372] intentionally omitted <==**

**----- Start of picture text -----**<br>
Bioreceptor Transducer Electronics Display<br>S)<br>Enzyme<br>. Photo<br>vane i<br>Conversion | 22 |<br>¢ « Cells from<br>‘aa Heat | Thermistor Transducer analog to digital | [Processed]<br>e @> signal signal<br>a<br>oe ftamer |— —_— —<br>* H ch PpH<br>¢ e DNA iabeieiaee| electrode Signal “<br>conditioning ‘2 rp<br>Nanoparticles} Mass Quartz aa<br>change } electrode “ ‘ara<br>Bio-recognition Signalisation Quantification<br>Gambar II.1  Komponen-komponen penyusun biosensor[7]<br>Analit merupakan komponen yang hendak dideteksi keberadaannya. Misalnya, pada<br>glukometer untuk mendeteksi kadar gula dalam darah manusia, analitnya adalah glukosa.<br>Bioreseptor adalah molekul yang mampu mendeteksi keberadaan analit yang ditandai<br>dengan terjadinya reaksi tertentu ( biorecognition ). Pemilihan bioreseptor sangat<br>Dokumen Asli<br>**----- End of picture text -----**<br>


Analit merupakan komponen yang hendak dideteksi keberadaannya. Misalnya, pada glukometer untuk mendeteksi kadar gula dalam darah manusia, analitnya adalah glukosa. Bioreseptor adalah molekul yang mampu mendeteksi keberadaan analit yang ditandai dengan terjadinya reaksi tertentu ( _biorecognition_ ). Pemilihan bioreseptor sangat bergantung pada analit yang hendak dideteksi, karena umumnya bioreseptor memiliki sifat spesifik, yaitu hanya dapat mengenali satu jenis zat. Beberapa contoh bioreseptor antara lain nanopartikel, DNA, sel, aptamer, antibodi, dan enzim. Spesifisitas dari material bioreseptor tersebut dapat terlihat dari enzim yang memiliki _active/binding site_ yang spesifik hanya dapat berikatan dengan zat tertentu, serta antibodi yang memiliki sifat reaktif hanya ketika dipertemukan dengan antigen tertentu. 

19 

Contoh lain pemilihan biosensor adalah pemilihan nanopartikel seperti nanopartikel emas (AuNP). Nanopartikel emas memiliki sifat mudah mengikat gugus thiol, sehingga cocok digunakan sebagai pelapis elektroda apabila hendak mendeteksi analit biologis, atau bahkan mendeteksi kandungan bakteri pada analit seperti bakteri _E. coli_ . 

Transduser merupakan komponen yang berfungsi melakukan konversi bentuk energi menjadi bentuk yang lain yang lebih mudah diukur. Pada umumnya, sinyal yang 

diolah menjadi data yang dapat dikenali dan ditampilkan langsung pada pengguna ) melalui berbagai proses pengolahan sinyal seperti kuantifikasi, yaitu konversi sinyal analog ke sinyal digital yang lebih mudah diproses Perbedaan yang signifikan antara biosensor dan sensor kimia terletak pada analit yang ingin dideteksi. Biosensor mendeteksi zat biologis dan menggunakan bioreseptor berupa material biologis seperti DNA, protein, dan enzim, sedangkan sensor kimia hanya mendeteksi keberadaan zat non-biologis tertentu dalam sampel analit. Sensor kimia juga memiliki fungsi yang sangat berkaitan dalam kehidupan sehari-hari. Sensor kimia mampu mendeteksi kandungan pencemaran obat dalam air sungai, mendeteksi adanya korosi dalam sampel analit, serta mendeteksi keberadaan zat narkotika Tantangan dalam riset biosensor dan sensor kimia menyangkut performansi dari sensor yang sudah dibuat. Beberapa parameter di antaranya seperti spesifisitas dan linearitas. 

Sensor kimia juga memiliki fungsi yang sangat berkaitan dalam kehidupan sehari-hari. Sensor kimia mampu mendeteksi kandungan pencemaran obat dalam air sungai, mendeteksi adanya korosi dalam sampel analit, serta mendeteksi keberadaan zat narkotika dalam sebuah sampel. 

Tantangan dalam riset biosensor dan sensor kimia menyangkut performansi dari sensor yang sudah dibuat. Beberapa parameter di antaranya seperti spesifisitas dan linearitas. 

Spesifisitas mengacu pada kemampuan dari biosensor untuk mendeteksi tepat satu analit. Apabila terdapat kandungan zat lain (yang bukan zat yang ingin dideteksi keberadaannya) dalam analit, biosensor tidak boleh memberikan hasil _false negative_ . Apabila terjadi kesalahan, khususnya dalam bidang medis, hal ini dapat mengakibatkan konsekuensi yang tidak diinginkan, sehingga spesifisitas merupakan kriteria yang sangat penting dari sebuah biosensor. 

dihasilkan oleh komponen transduser merupakan sinyal listrik yang memiliki sifat mudah diolah menjadi data yang dapat dikenali dan ditampilkan langsung pada pengguna ( _display_ ) melalui berbagai proses pengolahan sinyal seperti kuantifikasi, yaitu konversi sinyal analog ke sinyal digital yang lebih mudah diproses 

Perbedaan yang signifikan antara biosensor dan sensor kimia terletak pada analit yang ingin dideteksi. Biosensor mendeteksi zat biologis dan menggunakan bioreseptor berupa material biologis seperti DNA, protein, dan enzim, sedangkan sensor kimia hanya mendeteksi keberadaan zat non-biologis tertentu dalam sampel analit. 

20 

Linearitas mengacu pada kemampuan biosensor untuk menghasilkan respons sinyal yang linear dengan konsentrasi analitnya. Salah satu parameter yang sering disorot adalah _Linear Range_ , yakni rentang konsentrasi di mana sinyal yang dihasilkan sebanding dengan konsentrasi analitnya. Hal ini penting mengingat di luar rentang linear, sulit untuk memprediksi konsentrasi dari analit apabila hanya diketahui kuat sinyal listrik yang dihasilkan. 

yang merupakan batas konsentrasi analit terkecil yang dapat dideteksi oleh biosensor. Nilai LoD dari sebuah biosensor umumnya bergantung dari besarnya _noise_ terdeteksi oleh sistem transduser, biasanya tiga kali dari besarnya sinyal noise.[17] **Analisis Voltametri dan Amperometri** Dua dari antara metode yang umum digunakan untuk melakukan analisis elektrokimia adalah voltametri dan amperometri. Teknik voltametri menganalisis tanggapan arus yang terbentuk pada analit (sebagai tanda terjadinya perpindahan elektron pada reaksi redoks) terhadap tegangan yang diberikan, sedangkan Teknik amperometri umumnya menganalisis respons arus yang terbentuk pada analit sebagai fungsi dari waktu untuk tegangan yang bernilai konstan. _Cyclic Voltammetry_ (CV) Analisis elektrokimia dengan teknik CV bertujuan mengetahui profil dari reaksi elektrokimia (redoks) yang terjadi pada analit, serta mengetahui reversibilitas dari reaksi reduksi atau oksidasi yang terjadi. Kegunaan lain dari CV adalah 

## **II.2 Analisis Voltametri dan Amperometri** 

Dua dari antara metode yang umum digunakan untuk melakukan analisis elektrokimia adalah voltametri dan amperometri. Teknik voltametri menganalisis tanggapan arus yang terbentuk pada analit (sebagai tanda terjadinya perpindahan elektron pada reaksi redoks) terhadap tegangan yang diberikan, sedangkan Teknik amperometri umumnya menganalisis respons arus yang terbentuk pada analit sebagai fungsi dari waktu untuk tegangan yang bernilai konstan. 

## 1. _Cyclic Voltammetry_ (CV) 

Analisis elektrokimia dengan teknik CV bertujuan mengetahui profil dari reaksi elektrokimia (redoks) yang terjadi pada analit, serta mengetahui reversibilitas dari reaksi reduksi atau oksidasi yang terjadi. Kegunaan lain dari CV adalah kemampuannya untuk melakukan pengujian terhadap elektroda, apakah sedang dalam kondisi yang baik atau tidak baik [8]. Analisis elektrokimia dengan CV menggunakan tiga buah elektroda yaitu Counter Electrode (CE), Working Electrode (WE), dan Reference Electrode (RE). Arus pada analit yang terukur merupakan arus dari CE menuju WE, sedangkan tegangan pada analit diukur oleh elektroda RE. 

Sensitivitas dari biosensor juga dapat diamati melalui parameter _Limit of Detection_ (LoD) yang merupakan batas konsentrasi analit terkecil yang dapat dideteksi oleh biosensor. Nilai LoD dari sebuah biosensor umumnya bergantung dari besarnya _noise_ yang terdeteksi oleh sistem transduser, biasanya tiga kali dari besarnya sinyal noise.[17] 

21 

Teknik CV memberikan sinyal input berupa sinyal _sweep_ dari tegangan terkecil Vmin sampai tegangan Vmax, kemudian kembali lagi menuju tegangan terkecil Vmin, dan berulang sebanyak beberapa siklus. Opsi lain adalah memulai dari tegangan terbesar Vmax kemudian melakukan siklus dengan arah yang berlawanan. 

Dari hasil analisis CV, dapat terlihat potensial reduksi dan oksidasi dari sebuah analit, yang dapat terlihat pada puncak katodik (ketika arus bernilai positif 

potensial ini bergantung pada Persamaan Nernst, yakni: �[[��]] ����� ��� �� Pada persamaan ini, � adalah potensial reduksi analit, �� adalah potensial reduksi dalam keadaan standar dan konsentrasi analit tepat 1 M, R merupakan tetapan gas ideal 8.314 J/mol K, T merupakan suhu tempat terjadinya reaksi, � merupakan jumlah mol elektron yang bereaksi, dan � merupakan konstanta Faraday 96500 C/mol yang menyatakan jumlah muatan yang terkandung dalam satu mol elektron. Besaran ��menyatakan perbandingan konsentrasi reaksi reaktan dan produk dipangkatkan koefisiennya masing-masing dalam reaksi kimia yang setara. 

maksimum) dan puncak anodic (ketika arus bernilai paling negatif). Besarnya potensial ini bergantung pada Persamaan Nernst, yakni: �[[��]] ����� ��� �� 

22 

**==> picture [399 x 372] intentionally omitted <==**

**----- Start of picture text -----**<br>
is 0<br>Time E/V<br>‘s<br>SWV 5<br>2 <<br>0 x<br>s i<br>| | —“‘CSsSCSC—szY aid<br>Time E/V<br>Gambar II.2  Ilustrasi tegangan masukan (kiri) dan keluaran (kanan) dari berbagai metode<br>pengukuran elektrokimia[9]<br>Besarnya arus puncak yang terjadi pada analisis CV berkaitan dengan konsentrasi<br>analit yang diuji, sedangkan bentuk kurva CV yang jauh dari bentuk tipikalnya<br>menandakan kemungkinan kualitas elektroda yang digunakan sudah tidak baik<br>lagi.<br>Beberapa faktor lain yang mempengaruhi hasil CV yaitu  scan rate  yaitu kecepatan<br>perubahan tegangan dari tegangan minimum ke maksimum (dan sebaliknya).<br>Dokumen AsliApabila  scan rate  dipilih terlalu cepat, reaksi redoks pada analit belum terjadi<br>**----- End of picture text -----**<br>


Beberapa faktor lain yang mempengaruhi hasil CV yaitu _scan rate_ yaitu kecepatan perubahan tegangan dari tegangan minimum ke maksimum (dan sebaliknya). Apabila _scan rate_ dipilih terlalu cepat, reaksi redoks pada analit belum terjadi secara sempurna ketika tegangan yang diberikan sudah berubah, sehingga dapat mempengaruhi kualitas dari bacaan CV. Selain itu, pemilihan rentang _sweep_ Vmin dan Vmax juga penting, mengingat apabila potensial reduksi dari analit tidak terdapat pada rentang tersebut, bentuk standar kurva CV tidak akan muncul. 

2. _Differential Pulse Voltammetry_ (DPV) 

23 

Perbedaan mendasar antara teknik DPV dengan CV adalah bentuk tegangan masukan yang diberikan. Analisis DPV memberikan tegangan berbentuk anak tangga seperti diilustrasikan pada Gambar 2.1., serta menganalisis besarnya selisih besarnya arus pada analit saat puncak dan dasar pulsa (pada Gambar 2.1., berarti nilai Vso — Vo4 ) terhadap tegangan analit.[10] Gambar II.3 menjelaskan beberapa parameter masukan pada pengukuran DPV, yakni periode pulsa, lebar pulsa, periode _sampling_ , dan tinggi/amplituda dari pulsa yang digunakan. Step Pulse width (A) E Sample period E Pulse snes Sample period Pulse period Quiet time t (B) ' H : an ‘ 5<= ates a: H LS:itey a neH ‘ 5'‘ 5i : ~0.0118 | RN 5 KS | aR Sateen ~200.0 -350.5 —501.0 -651.5 802.0 Potential (mV) **Gambar II.3** (A) Tegangan input dan parameter-parameter masukan pada pengukuran DPV, (B) contoh voltamogram hasil pengukuran DPV[18] 

Analisis DPV pada elektroda yang diam memiliki ciri khas yaitu arus yang mengalir setelah pemberian satu “langkah” kenaikan potensial dipengaruhi oleh langkah-langkah sebelumnya sejak analisis dimulai.[11] 

Kelebihan dari analisis DPV dibandingkan CV antara lain mengurangi efek dari _background current_ yang disebabkan oleh arus kapasitif pada analit melalui 

24 

bentuk tegangan yang menyerupai DC ramp dan melalui pengambilan selisih arus ketimbang nilai arus yang mengalir pada analit, sehingga memiliki hasil yang lebih sensitif. Bentuk pulsa dengan kenaikan yang kecil juga menyebabkan arus puncak yang semakin sempit, sehingga DPV mampu membedakan beberapa analit yang memiliki potensial oksidasi yang mirip. Namun, analisis DPV memiliki waktu pengujian yang relatif lama dibandingkan dengan teknik analisis yang lain. Salah satu penerapan dari uji DPV adalah pendeteksian obat pada sampel urin manusia[12]. 

_Linear Sweep Voltammetry_ (LSV) Studi LSV menganalisis arus yang terbentuk pada analit ketika diberikan input berupa tegangan _sweep_ satu arah. Bentuk tegangan input pada LSV menyerupai input tegangan pada CV, namun hanya dilakukan satu kali dan hanya satu arah. Kelebihan dari LSV sangat terlihat pada reaksi redoks pada sistem irreversibel, yakni ketika pemberian potensial _sweep_ ke arah yang berlawanan tidak menghasilkan keluaran yang signifikan. Arus puncak yang terbentuk pada analisis LSV dirumuskan melalui persamaan: ��� ���������[[�]] �������������������������������������������������������������������������������� Pada persamaan di atas, �� merupakan konsentrasi analit dalam mol/L, � merupakan konsentrasi analit dalam mol/L,  merupakan konsentrasi analit dalam mol/L, elektroda A, dan konstanta difusi ��. Parameter ��. Parameter �. Parameter . Parameter _scan rate_ tegangan pada saat sweeping) adalah �. Untuk sistem yang reversibel, nilai �. Untuk sistem yang reversibel, nilai . Untuk sistem yang reversibel, nilai �� 

## 3. _Linear Sweep Voltammetry_ (LSV) 

Studi LSV menganalisis arus yang terbentuk pada analit ketika diberikan input berupa tegangan _sweep_ satu arah. Bentuk tegangan input pada LSV menyerupai input tegangan pada CV, namun hanya dilakukan satu kali dan hanya satu arah. Kelebihan dari LSV sangat terlihat pada reaksi redoks pada sistem irreversibel, yakni ketika pemberian potensial _sweep_ ke arah yang berlawanan tidak menghasilkan keluaran yang signifikan. Arus puncak yang terbentuk pada analisis LSV dirumuskan melalui persamaan: ��� ���������[[�]] �������������������������������������������������������������������������������� **(II.1)** Pada persamaan di atas, �� merupakan konsentrasi analit dalam mol/L, � merupakan konsentrasi analit dalam mol/L,  merupakan konsentrasi analit dalam mol/L, � luas elektroda A, dan konstanta difusi ��. Parameter ��. Parameter �. Parameter . Parameter _scan rate_ (kecepatan perubahan tegangan pada saat sweeping) adalah �. Untuk sistem yang reversibel, nilai �. Untuk sistem yang reversibel, nilai . Untuk sistem yang reversibel, nilai �� �, sedangkan untuk sistem yang tidak reversibel, nilai ��������, di mana nilai � menentukan derajat reversibilitas dari reaksi yang berlangsung.[13,14] 

25 

Vif --------------- **Gambar II.4** Kurva input untuk LSV (kiri) dan voltamogram hasil pengukuran LSV (kanan) _Chronoamperometry_ (CA) Analisis CA menggunakan eksitasi gelombang step pada analit, kemudian melihat kuat arus listrik yang mengalir sebagai fungsi dari waktu. Umumnya, nilai potensial diubah dari nilai di mana tidak ada arus yang mengalir menjadi ada arus yang mengalir (reaksi redoks berjalan). Teknik CA dapat digunakan untuk menentukan koefisien difusi (dalam m/s[2] ) dari sebuah senyawa elektroaktif melalui persamaan Cottrell[8]: **(II.2)** 

4. _Chronoamperometry_ (CA) 

26 

**Gambar II.5** Tegangan masukan dan arus keluaran pengukuran CA[8] Gambar 2.4. menyajikan kurva input-output dari analisis CA. Umumnya, analisis CA juga mengamati respons arus ketika tegangan dinaikkan setelah nilai arus stabil, sehingga muncul bentuk arus yang terus menerus naik menyerupai pulsa anak tangga. **Rangkaian Potensiostat Standar** Rangkaian potensiostat adalah sistem yang menerima input berupa sinyal listrik dari reaksi reduksi/oksidasi yang terjadi pada analit, kemudian mentranslasikannya menjadi data voltammogram atau hasil pengukuran elektrokimia lain yang dapat diinterpretasikan oleh peneliti. Penggunaan umum potensiostat melibatkan sebuah (SPCE) sebagai elektroda yang dapat dimodifikasi dengan bioreseptor sesuai dengan kebutuhan. SPCE merupakan tempat terjadinya reaksi elektrokimia yang akan menghasilkan data untuk diolah oleh potensiostat. 

**II.3 Rangkaian Potensiostat Standar** 

Rangkaian potensiostat adalah sistem yang menerima input berupa sinyal listrik dari reaksi reduksi/oksidasi yang terjadi pada analit, kemudian mentranslasikannya menjadi data voltammogram atau hasil pengukuran elektrokimia lain yang dapat diinterpretasikan oleh peneliti. Penggunaan umum potensiostat melibatkan sebuah _Screen Printed Carbon Electrode_ (SPCE) sebagai elektroda yang dapat dimodifikasi dengan bioreseptor sesuai dengan kebutuhan. SPCE merupakan tempat terjadinya reaksi elektrokimia yang akan menghasilkan data untuk diolah oleh potensiostat. 

Potensiostat memberikan tegangan dengan pola tertentu bergantung pada metode pengukuran yang hendak diterapkan dengan cara memberikan beda potensial pada elektroda _Counter_ pada SPCE (CTR atau CE/ _Counter Electrode_ ). Rangkaian standar potensiostat ditunjukkan pada Gambar II.6 di bawah ini. 

Gambar 2.4. menyajikan kurva input-output dari analisis CA. Umumnya, analisis CA juga mengamati respons arus ketika tegangan dinaikkan setelah nilai arus stabil, sehingga muncul bentuk arus yang terus menerus naik menyerupai pulsa anak tangga. 

27 

**==> picture [429 x 372] intentionally omitted <==**

**----- Start of picture text -----**<br>
WRKsense WRKearive<br>- s @<br>Gambar II.6  Skema rangkaian potensiostat<br>Dalam  implementasinya,  dibutuhkan  komponen-komponen  tambahan  untuk<br>merealisasikan sistem potensiostat ini supaya dapat terhubung dengan baik dengan<br>prosesor yang hendak digunakan, dan komunikasi data dapat dilakukan dengan baik.<br>Gambar II.7 menunjukkan skema diagram rangkaian potensiostat[12].<br>Digital-to- Trans- Analog-to-<br>Analog Electro- : tah<br>Converter Level Shifter chemical impedance Level Shifter Digital<br>(DAC) Cell Amplifier(TIA) Converter(ADC)<br>Gambar II.7  Contoh implementasi sistem potensiostat[12]<br>Dokumen Asli<br>**----- End of picture text -----**<br>


Blok rangkaian yang umum ada pada potensiostat adalah _Digital to Analog Converter_ 

untuk memberikan tegangan _sweep_ pada rentang tertentu, kemudian rangkaian penggeser level tegangan ( _level shifter_ ) yang diimplementasikan melalui rangkaian _Summing Amplifier_ untuk memberikan offset pada tegangan keluaran DAC yang selalu positif, sehingga tegangan yang dirasakan analit bisa mencakup tegangan negatif juga. Kemudian, terdapat _Transimpedance Amplifier_ (TIA) yang bertugas mengkonversi data 

28 

tegangan atau arus yang diterima dari analit menjadi data yang dapat diinterpretasikan oleh sistem. Setelah itu, rangkaian potensiostat bisa mengolah data menjadi voltammogram dengan bantuan perangkat lunak lain. 

Potensiostat sendiri memiliki kelebihan dibandingkan alat uji karakterisasi material lainnya, di antaranya kebutuhan analit dalam jumlah yang sedikit, waktu pengujian yang relatif lebih cepat, dan hasil yang langsung dapat dilihat setelah pengujian. Beberapa 

perancangan potensiostat berukuran kecil yang mudah dibawa apabila hendak dilakukan pengujian di luar ruangan laboratorium.[15] Selain itu, perkembangan potensiostat juga sedang menuju ke arah resolusi yang lebih teliti, sehingga arus yang terukur oleh potensiostat menjadi lebih akurat dan presisi. Telah _chipset_ untuk merealisasikan sistem potensiostat yang menggunakan rangkaian konversi Analog ke Digital (atau sebaliknya) dengan resolusi yang lebih tinggi dan dengan ukuran yang lebih kecil, sehingga mampu menghasilkan performansi yang Perkembangan lain juga menuju ke arah antarmuka potensiostat dengan pengguna. Contohnya, penggunaan komunikasi nirkabel sehingga data hasil pengujian dapat diakses di perangkat masing-masing, serta pengembangan antarmuka pengguna ( pada berbagai perangkat, atau pengembangan potensiostat multikanal yang mampu menganalisis lebih dari satu analit dalam waktu yang bersamaan, sehingga menghemat waktu pengujian apabila hendak dilakukan pengujian terhadap analit yang beragam. 

Perkembangan lain juga menuju ke arah antarmuka potensiostat dengan pengguna. Contohnya, penggunaan komunikasi nirkabel sehingga data hasil pengujian dapat diakses di perangkat masing-masing, serta pengembangan antarmuka pengguna ( _user interface_ ) pada berbagai perangkat, atau pengembangan potensiostat multikanal yang mampu menganalisis lebih dari satu analit dalam waktu yang bersamaan, sehingga menghemat waktu pengujian apabila hendak dilakukan pengujian terhadap analit yang beragam. 

perkembangan dari riset potensiostat antara lain menyangkut isu portabilitas, yakni terkait perancangan potensiostat berukuran kecil yang mudah dibawa apabila hendak dilakukan pengujian di luar ruangan laboratorium.[15] 

Selain itu, perkembangan potensiostat juga sedang menuju ke arah resolusi yang lebih teliti, sehingga arus yang terukur oleh potensiostat menjadi lebih akurat dan presisi. Telah dirancang juga _chipset_ untuk merealisasikan sistem potensiostat yang menggunakan rangkaian konversi Analog ke Digital (atau sebaliknya) dengan resolusi yang lebih tinggi dan dengan ukuran yang lebih kecil, sehingga mampu menghasilkan performansi yang semakin baik.[16] 

29 

## **Bab III    Metode Penelitian dan Perancangan** 

## **III.1 Rancangan Skema Penelitian** 

**==> picture [382 x 449] intentionally omitted <==**

**----- Start of picture text -----**<br>
III.1.1 Alur Kerja Penelitian<br>Alur penelitian ini disajikan pada diagram alir pada Gambar III.1 di bawah ini.<br>Identifikasi Masalah<br>Studi Literatur<br>Perancangan Sistem<br>Belum berhasil<br>Implementasi Sistem (Iterasi)<br>Dokumen Asli<br>**----- End of picture text -----**<br>


**Gambar III.1** Alur penelitian 

30 

Beberapa tahapan yang dilakukan dalam penelitian ini antara lain: 

1. Identifikasi masalah 

Telah dilakukan proses identifikasi masalah, yaitu adanya kebutuhan untuk potensiostat sebagai alat analisis profil elektrokimia dari sebuah analit yang memiliki harga terjangkau dan performa yang setara dengan potensiostat yang dijual secara komersil. Identifikasi masalah dan batasan penelitian ini telah dibahas di Bab I Pendahuluan. 

2. Studi literatur Dilakukan studi dari penelitian-penelitian terkini terkait pengembangan potensiostat dengan beragam jenis seperti dalam bentuk _chip printed circuit board_ (PCB). Dilakukan pula pengamatan terhadap skema kerja potensiostat standar yang mencakup algoritma dari perangkat lunak/ _firmware_ yang digunakan dan blok-blok rangkaian dasar yang digunakan dalam potensiostat, sampai rangkaian/sistem pengolah data potensiostat sehingga dapat menghasilkan data yang dapat dianalisis oleh pengguna. Kajian terkait solusi-solusi yang telah diimplementasikan pada penelitian sebelumnya telah dibahas pada Bab II Studi Literatur. 3. Perancangan sistem Dilakukan perencanaan terhadap sistem yang hendak diimplementasikan dari segi perangkat keras (desain blok rangkaian dasar pada sistem, perancangan PCB, _layouting_ untuk PCB) maupun perangkat lunak (fungsifungsi dasar yang dibutuhkan pada _firmware_ , metode komunikasi data, dan fungsionalitas lain yang diperlukan pada perangkat lunak). Selain itu, 

Dilakukan studi dari penelitian-penelitian terkini terkait pengembangan potensiostat dengan beragam jenis seperti dalam bentuk _chip_ , dalam bentuk _printed circuit board_ (PCB). Dilakukan pula pengamatan terhadap skema kerja potensiostat standar yang mencakup algoritma dari perangkat lunak/ _firmware_ yang digunakan dan blok-blok rangkaian dasar yang digunakan dalam potensiostat, sampai rangkaian/sistem pengolah data potensiostat sehingga dapat menghasilkan data yang dapat dianalisis oleh pengguna. Kajian terkait solusi-solusi yang telah diimplementasikan pada penelitian sebelumnya telah dibahas pada Bab II Studi Literatur. 

Dilakukan perencanaan terhadap sistem yang hendak diimplementasikan dari segi perangkat keras (desain blok rangkaian dasar pada sistem, perancangan PCB, _layouting_ untuk PCB) maupun perangkat lunak (fungsifungsi dasar yang dibutuhkan pada _firmware_ , metode komunikasi data, dan fungsionalitas lain yang diperlukan pada perangkat lunak). Selain itu, dilakukan pula perancangan cara kerja sistem dari segi komunikasi data sehingga data dapat dilihat oleh pengguna. Detail perancangan sistem dibahas pada Bab III Metode Penelitian dan Perancangan. 

## 4. Implementasi sistem 

Pada tahapan ini, dilakukan implementasi sistem menjadi _printed circuit board_ (PCB). Dilakukan juga perancangan untuk _casing_ dari sistem. 

31 

Implementasi sistem ini dijabarkan pada Bab IV Implementasi dan Pengujian. 

5. Pengujian sistem 

Pada tahap ini, performa potensiostat yang dirancang pada penelitian ini dibandingkan dengan performa potensiostat yang dijual secara komersil. Beberapa parameter yang diuji mencakup rentang konsentrasi analit yang 

**==> picture [401 x 379] intentionally omitted <==**

**----- Start of picture text -----**<br>
dapat terdeteksi, linearitas arus yang terbentuk terhadap konsentrasi analit,<br>serta resolusi arus dan tegangan yang dapat terukur oleh potensiostat.<br>Pengujian sistem dijelaskan pada Bab IV Implementasi dan Pengujian.<br>III.1.2 Konsep Interaksi Sistem<br>Desain interaksi sistem dengan pengguna disajikan pada Gambar III.2. di bawah<br>ini.<br>Tegangan pemicu<br>le+| +€E‘lektroda + Analit<br>Tegangan<br>elektroda<br>Sistem Potensiostat<br>Mode dan parameter Pembacaan arus dan<br>pengukuran tegangan analit<br>Mode dan parameter<br>pengukuran<br>PC/Laptop User<br>Pembacaan arus dan<br>wsar tegangan analit<br>Dokumen Asli<br>**----- End of picture text -----**<br>


## **III.1.2 Konsep Interaksi Sistem** 

**Gambar III.2** Desain interaksi sistem potensiostat dengan pengguna 

Pada potensiostat yang dirancang, pengguna cukup memasukkan mode pengukuran dan parameter pengukuran yang hendak digunakan pada PC/Laptop pengguna, dengan contoh sebagai berikut: 

32 

1. Mode pengukuran: pada potensiostat yang dirancang hanya mencakup pengukuran _Cyclic Voltammetry_ (CV) dan _Differential Pulse Voltammetry_ (DPV). 

2. Parameter tegangan pemicu awal dan akhir, yaitu tegangan minimum dan maksimum yang diberikan pada analit. 

3. _Scan Rate_ , yaitu kecepatan perubahan tegangan yang dirasakan oleh analit (dalam mV/s) 

4. Jumlah siklus, yaitu banyaknya siklus yang digunakan pada CV. Umumnya, 

jumlah siklus dibuat lebih dari satu untuk pada akhirnya diambil data pada siklus terakhir, ketika reaksi elektrokimia pada analit sudah lebih stabil. 5. Jumlah kanal, yaitu banyaknya kanal yang digunakan. Jika jumlah kanal yang digunakan dalam sekali pengukuran lebih banyak, akan lebih banyak analit yang dapat diuji secara sekaligus. Kemudian, parameter-parameter yang dimasukkan oleh pengguna akan diteruskan dari PC/Laptop menuju sistem potensiostat. Potensiostat kemudian akan memberikan tegangan pada analit untuk memicu terjadinya redoks/elektrokimia sesuai dengan parameter yang dimasukkan, sambil melakukan pembacaan terhadap tegangan pada elektroda yang terhubung pada analit. Adapun arus dapat mengalir pada analit karena pada reaksi elektrokimia, terjadi perpindahan/aliran elektron. Pada reaksi oksidasi, terjadi pelepasan elektron, dan pada reaksi reduksi, elektron bergabung dengan suatu spesi. Kemudian, data tegangan elektroda dikonversi menjadi arus pada analit dengan menggunakan persamaan yang didapat dari analisis rangkaian potensiostat. Data ini 

Kemudian, parameter-parameter yang dimasukkan oleh pengguna akan diteruskan dari PC/Laptop menuju sistem potensiostat. Potensiostat kemudian akan memberikan tegangan pada analit untuk memicu terjadinya reaksi redoks/elektrokimia sesuai dengan parameter yang dimasukkan, sambil melakukan pembacaan terhadap tegangan pada elektroda yang terhubung pada analit. Adapun arus dapat mengalir pada analit karena pada reaksi elektrokimia, terjadi perpindahan/aliran elektron. Pada reaksi oksidasi, terjadi pelepasan elektron, dan pada reaksi reduksi, elektron bergabung dengan suatu spesi. 

Kemudian, data tegangan elektroda dikonversi menjadi arus pada analit dengan menggunakan persamaan yang didapat dari analisis rangkaian potensiostat. Data ini akan diteruskan ke pengguna sehingga terbentuk kurva arus terhadap tegangan analit yang nantinya dapat dianalisis oleh pengguna sesuai dengan kebutuhan. 

## **III.1.3 Rancangan Dasar Perangkat Keras** 

Perangkat keras yang dirancang perlu memenuhi spesifikasi berikut: 

- Mampu menghasilkan tegangan pada analit pada rentang -1 sampai 1 V. 

jumlah siklus dibuat lebih dari satu untuk pada akhirnya diambil data pada siklus terakhir, ketika reaksi elektrokimia pada analit sudah lebih stabil. 5. Jumlah kanal, yaitu banyaknya kanal yang digunakan. Jika jumlah kanal yang digunakan dalam sekali pengukuran lebih banyak, akan lebih banyak analit yang dapat diuji secara sekaligus. 

33 

- Memiliki resolusi arus minimal ���� dan rentang arus pengukuran maksimal ����. 

- Mampu melakukan pengukuran elektrokimia dengan teknik _Cyclic Voltammetry_ (CV), _Linear Sweep Voltammetry_ (LSV), _Differential Pulse Voltammetry_ (DPV), dan _Chronoamperometry_ (CA). 

- Membutuhkan tegangan catu daya rendah, yaitu dalam orde satuan Volt. 

- Memiliki ukuran yang portabel. 

Pemilihan rangkaian perangkat keras mengikuti yang sudah dijelaskan pada Bab II sebelumnya. Terdapat banyak kemungkinan rancangan sistem lain untuk mengimplementasikan sistem potensiostat ini, namun susunan ini dipilih karena relatif lebih mudah diimplementasikan karena menggunakan komponen diskrit. Adapun realisasi dengan fabrikasi chip/IC potensiostat khusus dinilai kurang memungkinkan karena keterbatasan sumber daya yang ada, dan bisa menjadi potensi pengembangan riset ini di masa mendatang. Terdapat beberapa blok rangkaian utama yang diperlukan pada potensiostat, yaitu penggeser level tegangan ( _level shifter_ ), antarmuka sel elektrokimia, penguat transimpedansi ( _transimpedance amplifier_ /TIA), filter analog Sallen-Key, serta _level shifter_ pada tahap output. Rincian dari kerja masing-masing blok rangkaian adalah sebagai berikut: 1. Generator sinyal Digunakan mikrokontroler STM32F4CE11U6 sebagai generator sinyal. Diperlukan sinyal berbentuk tangga untuk pengukuran CV dan LSV, sinyal berbentuk pulsa naik dan turun untuk pengukuran DPV, serta tegangan 

Terdapat beberapa blok rangkaian utama yang diperlukan pada potensiostat, yaitu penggeser level tegangan ( _level shifter_ ), antarmuka sel elektrokimia, penguat transimpedansi ( _transimpedance amplifier_ /TIA), filter analog Sallen-Key, serta _level shifter_ pada tahap output. Rincian dari kerja masing-masing blok rangkaian adalah sebagai berikut: 

Digunakan mikrokontroler STM32F4CE11U6 sebagai generator sinyal. Diperlukan sinyal berbentuk tangga untuk pengukuran CV dan LSV, sinyal berbentuk pulsa naik dan turun untuk pengukuran DPV, serta tegangan _step_ untuk CA. Bentuk tegangan ini dapat diimplementasikan menggunakan mikrokontroler STM32F4CE11U6. Mikrokontroler ini dibantu juga dengan DAC 16-bit, sehingga resolusi tegangan yang dapat dikeluarkan adalah: 

**==> picture [92 x 26] intentionally omitted <==**

Pemilihan rangkaian perangkat keras mengikuti yang sudah dijelaskan pada Bab II sebelumnya. Terdapat banyak kemungkinan rancangan sistem lain untuk mengimplementasikan sistem potensiostat ini, namun susunan ini dipilih karena relatif lebih mudah diimplementasikan karena menggunakan komponen diskrit. Adapun realisasi dengan fabrikasi chip/IC potensiostat khusus dinilai kurang memungkinkan karena keterbatasan sumber daya yang ada, dan bisa menjadi potensi pengembangan riset ini di masa mendatang. 

34 

2. Penggeser Level Tegangan ( _level shifter_ ) 

**Gambar III.3** Skema rangkaian _level shifter_ Mikrokontroler STM32 yang digunakan dapat memberikan suplai tegangan nominal sebesar 0 sampai 5 Volt. Namun, tegangan yang diperlukan pada analit mencakup tegangan negatif pula, umumnya -1 sampai 1 Volt. Strategi yang dilakukan adalah memetakan rentang tegangan yang mungkin disuplai oleh mikrokontroler menjadi tegangan yang dibutuhkan oleh analit. Adapun hubungan tegangan suplai dari mikrokontroler dengan tegangan yang diberikan pada analit dapat dicari melalui analisis rangkaian pada Gambar III.3. 

**(III.1)** Mengingat resistansi yang tersedia di pasaran hanyalah resistansi yang tercakup dalam daftar nilai EIA, maka melalui perhitungan, dapat digunakan nilai sebesar . Pemilihan nilai resistansi ini mengakibatkan persamaan tegangan _sweep_ yang dirasakan analit, sweep , dan nilai tegangan yang dikeluarkan ADC, Vin , memiliki hubungan berikut: 

**(III.2)** 

Sehingga, tegangan Vsweep dengan rentang -1 sampai 1 Volt dapat dicapai dengan mengatur mikrokontroler supaya memberikan tegangan Vin sebesar 

35 

2 sampai 3 Volt. Kelebihan dari pemilihan nilai ini juga adalah terdapat kemungkinan untuk kebutuhan Vsweep dengan rentang di luar -1 sampai 1 Volt. Hal ini dapat dicapai dengan memberikan nilai 7 (tegangan mikrokontroler) di luar range 2 sampai 3 Volt apabila dibutuhkan. 

3. Antarmuka sel elektrokimia 

Bagian rangkaian ini digunakan sebagai interkoneksi sistem potensiostat 

**==> picture [365 x 277] intentionally omitted <==**

**----- Start of picture text -----**<br>
dengan sel elektrokimia. Terdapat tiga buah  port  pada elektroda karbon<br>yang digunakan, yaitu Working Electrode (WE), Reference Electrode (RE),<br>dan Counter Electrode (CE). Sistem potensiostat mengatur tegangan antara<br>elektroda WE dan RE, dan mengembalikan arus yang mengalir antara<br>elektroda WE dan CE.<br>Vsweep ; be<br>VRE<br>Gambar III.4  Rangkaian antarmuka dengan sel elektrokimia<br>Rangkaian ini bekerja sama seperti rangkaian  buffer  menggunakan penguat<br>umen Asli<br>**----- End of picture text -----**<br>


Rangkaian ini bekerja sama seperti rangkaian _buffer_ menggunakan penguat operasional ( _op-amp_ ). Input _non-inverting_ menerima input tegangan _sweep_ hasil keluaran rangkaian sebelumnya ( _level shifter_ ), sedangkan pin input _inverting_ meneruskan tegangan tersebut ke elektroda RE. Umpan balik dari blok ini berasal dari hubungan elektroda CE dan RE melalui analit yang digunakan. Sementara itu, elektroda WE menjadi penghubung yang membawa nilai pengukuran arus dari blok sel elektrokimia ke blok berikutnya. 

4. Penguat transimpedansi ( _transimpedance amplifier_ /TIA) 

Penguat transimpedansi bertujuan mengubah arus menjadi tegangan, karena mikrokontroler hanya mampu membaca tegangan secara langsung. 

36 

Rangkaian penguat transimpedansi . Pemilihan nilai resistansi _multiplexer_ . Melihat dari rumusan 

**Gambar III.5** Rangkaian penguat transimpedansi 

Rangkaian transimpedansi direalisasikan melalui rangkaian pada Gambar III.5. Pada rangkaian ini, arus pada WE dikonversi menjadi tegangan pada TIA dengan rumusan . Pemilihan nilai resistansi _gain_ Rg 

bergantung pada besarnya arus yang hendak dideteksi. Implementasi dari pemilihan ini dapat menggunakan _multiplexer_ . Melihat dari rumusan UVTIA yang didapat sebelumnya, dapat disimpulkan bahwa apabila hendak dilakukan pengukuran arus dengan magnitude yang semakin kecil, diperlukan nilai yang semakin besar untuk mengkompensasi nilai UVTIA supaya rentangnya tidak terlalu berubah secara ekstrim. 

Pada potensiostat ini, terdapat empat pilihan nilai yang mungkin: nilai 

untuk pengukuran arus maksimum 6 mA, nilai 

untuk pengukuran arus maksimum 0.5 mA, nilai untuk pengukuran arus maksimum 56.36 A, dan untuk pengukuran arus maksimum 5.37 A. 

Penambahan sebuah kapasitor paralel pada rangkaian TIA ini didasarkan pada _noise gain_ dari op-amp yang digunakan. Menurut datasheet op-amp yang disediakan, pada frekuensi yang lebih tinggi, _gain_ untuk noise akan menjadi semakin kuat, dan batas frekuensi penguatan _noise_ ini bergantung pada nilai kapasitansi. Sehingga perlu dipilih nilai kapasitansi yang ideal supaya rentang frekuensi ketika _noise_ kecil menjadi semakin lebar, dan 

37 

_bandwidth_ atau komponen frekuensi yang diloloskan dari rangkaian TIA menjadi semakin lebar. 

5. Filter Analog Sallen-Key 

Diperlukan rangkaian _Low-Pass Filter_ (LPF) untuk melakukan filtering sehingga komponen _noise_ yang umumnya memiliki frekuensi tinggi dapat tereliminasi dari sinyal yang hendak diukur, sehingga data yang diperoleh memiliki kualitas yang lebih baik. Berikut topologi rangkaian filter analog Sallen-Key. LPF ini menerima input berupa tegangan keluaran dari TIA dan mengeluarkan tegangan yang memiliki _noise_ dengan besar yang lebih kecil dibandingkan tegangan keluaran TIA. Cy R oy, @ ’ a ;i **Gambar III.6** Rangkaian _Low-Pass-Filter_ (LPF) Sallen-Key Fungsi transfer dari filter Sallen-Key pada Gambar III.6. dapat dicari melalui analisis rangkaian sederhana. Tegangan merupakan tegangan keluaran dari TIA, dan merupakan tegangan keluaran filter Sallen-Key. Dari arus yang mengalir pada , , dan , diperoleh: 

**(III.3)** 

> Sedangkan dari arus pada . dan Cy diperoleh: 

38 

~ 1+ jaR2C, 

**(III.4)** 

Jika disubstitusikan ke persamaan sebelumnya, didapat: 

**(III.5)** Dalam domain Laplace, dengan mengambil dan menyusun ulang persamaan di atas, didapatkan fungsi transfer sebagai berikut: 

**(III.6)** 

Sehingga, frekuensi cut-off dari filter Sallen-Key ini adalah: 

**(III.7)** Komponen sinyal dengan frekuensi di atas akan diblokir, sedangkan komponen sinyal dengan frekuensi di bawah akan diteruskan. 6. Penggeser Tegangan ( _Level Shifter_ ) output 

Penggeser tegangan harus bisa menggeser tegangan pada rentang -5 V sampai +5 V menjadi rentang 0 sampai 5 V yang dapat diterima oleh ADC untuk diolah melalui perhitungan menjadi kuat arus listrik yang mengalir pada analit. Implementasi rangkaian ini cukup mirip dengan penggeser tegangan pada input, dengan skematik sebagai berikut. Pada rangkaian ini, Vout merupakan tegangan keluaran filter Sallen-Key dan vane merupakan tegangan analog yang akan diterima oleh ADC. 

39 

**==> picture [266 x 135] intentionally omitted <==**

**----- Start of picture text -----**<br>
Gambar III.7  Rangkaian penggeser tegangan keluaran<br>non-inverting<br>Asli<br>**----- End of picture text -----**<br>


Melalui persamaan arus pada kutub _non-inverting_ Op-Amp, didapat persamaan: 

**(III.8)** 

Dengan memilih nilai yang sama untuk kedua resistansi, didapat: 

**(III.9)** Untuk tegangan keluaran rangkaian sebelumnya yang berada pada rentang tegangan -5 sampai 5 Volt, dengan memasukkan titik ujung rentang ini pada persamaan di atas, didapat rentang tegangan yang diterima ADC, Vapc , adalah 0 sampai 5 Volt sesuai yang diinginkan. 

## 7. Filter Anti-Aliasing 

Filter Anti-Aliasing digunakan untuk menghilangkan komponen sinyal yang memiliki frekuensi tinggi, yaitu di atas dua kali frekuensi sampling ADC. Implementasi filter anti-aliasing menggunakan rangkaian RC seri dengan tegangan keluaran diambil pada kapasitor sehingga membentuk 

40 

sebuah Low Pass Filter. Rangkaian anti-aliasing juga berfungsi untuk mengurangi noise yang ada pada ADC itu sendiri, mengingat rangkaian anti-aliasing akan menjadi input dari rangkaian ADC. Penggunaan rangkaian RC ketimbang filter aktif dipilih karena rangkaian pasif memiliki konsumsi daya yang lebih rendah dibanding filter aktif (berbasis op-amp). 

**==> picture [284 x 177] intentionally omitted <==**

**----- Start of picture text -----**<br>
+<br>Vin Vo C<br>Gambar III.8  Rangkaian RC sebagai filter antialiasing<br>n Asli<br>**----- End of picture text -----**<br>


Fungsi transfer dari rangkaian ini dapat dicari dengan mudah melalui persamaan pembagian tegangan. 

**(III.10)** Dari persamaan fungsi transfer ini, frekuensi cut-off dari filter anti-aliasing RC yang menggunakan resistansi sebesar R dan kapasitansi C dapat dituliskan dalam bentuk rumusan matematis berikut. 

**==> picture [35 x 10] intentionally omitted <==**

Terdapat dua sumber _noise_ utama dari sistem rangkaian yang diusulkan, yaitu adanya _noise_ pada op-amp yang dihasilkan rangkaian transistor internalnya, serta _noise_ yang disebabkan reaksi elektrokimia yang efisiensinya tidak bisa diprediksi. 

41 

Adanya _noise_ akibat op-amp umumnya memiliki nilai yang sangat kecil (orde fA) sehingga dapat diabaikan, sedangkan _noise_ akibat analit dapat menyebabkan perbedaan hasil pengukuran untuk pengukuran yang diulang beberapa kali, namun hasilnya tidak akan berbeda secara signifikan. 

## **III.1.4 Modul dan Komponen yang Digunakan** 

Komponen yang digunakan pada sistem potensiostat ini antara lain: 

1. Mikrokontroler STM32F405RGT6 untuk komunikasi dan mikrokontroler 

STM32F411CEU6 sebagai pengolah data masing-masing _channel_ Mikrokontroler yang digunakan memiliki prosesor berbasis 32-bit yang memiliki kecepatan pemrosesan data secara umum lebih cepat daripada prosesor 8-bit sepertai ATMega328 pada Arduino Nano/Uno. Perhitungan _floating point_ pada STM32 juga lebih cepat karena di dalamnya terkandung _Floating Point Unit_ (FPU). Jumlah port yang dimiliki mikrokontroler ini juga cukup untuk menangani sinyal yang diperlukan, yakni berjumlah 2 port SPI, 1 port UART, dan 4 buah GPIO untuk control LED dan memilih konfigurasi Selain itu, kelebihan dari mikrokontroler ini juga memiliki GPIO dengan level HIGH fleksibel antara 3.3V dan 5 V, sehingga tidak dibutuhkan _converter_ apabila diinginkan _interfacing_ antara berbagai IC. Kelebihan yang lain, STM32 memiliki frekuensi _clock_ MHz (dapat diubah). Beberapa efek dari frekuensi clock yang lebih tinggi 

Jumlah port yang dimiliki mikrokontroler ini juga cukup untuk menangani sinyal yang diperlukan, yakni berjumlah 2 port SPI, 1 port UART, dan 4 buah GPIO untuk control LED dan memilih konfigurasi _analog multiplexer_ . Selain itu, kelebihan dari mikrokontroler ini juga memiliki GPIO dengan level HIGH fleksibel antara 3.3V dan 5 V, sehingga tidak dibutuhkan _level converter_ apabila diinginkan _interfacing_ antara berbagai IC. 

Kelebihan yang lain, STM32 memiliki frekuensi _clock_ 16 MHz sampai 100 MHz (dapat diubah). Beberapa efek dari frekuensi clock yang lebih tinggi ini antara lain: 

- Frekuensi maksimum SPI pada STM32 adalah 50 Mbit/s (setara dengan 50 MHz). IC DAC yang digunakan, yaitu DAC8531, memiliki frekuensi SPI maksimum 30 MHz. IC ADC yang digunakan, yaitu MCP33131-05, memiliki frekuensi SPI maksimum 100 MHz.  Misalkan digunakan frekuensi komunikasi SPI sebesar 25 MHz. Pada DAC, satu kali konversi memerlukan 3-byte data (1- 

STM32F411CEU6 sebagai pengolah data masing-masing _channel_ Mikrokontroler yang digunakan memiliki prosesor berbasis 32-bit yang memiliki kecepatan pemrosesan data secara umum lebih cepat daripada prosesor 8-bit sepertai ATMega328 pada Arduino Nano/Uno. Perhitungan _floating point_ pada STM32 juga lebih cepat karena di dalamnya terkandung _Floating Point Unit_ (FPU). 

42 

byte untuk inisialisasi dan 2-byte data yang ditransfer) sedangkan pada ADC, satu kali konversi memerlukan 2-byte data. Jumlah data yang dibutuhkan untuk konversi ini adalah 5-byte atau setara dengan 40-bit. Pengiriman data 40-bit ini memerlukan waktu sebesar ����������������atau sebesar 1.6�s. Jadi, frekuensi maksimum pembacaan dan penulisan tegangan analog adalah 625 kHz. 

- Frekuensi maksimum USART di STM32 adalah 12.5 MHz. Jika 

_core_ menuju PC, satu kali pengambilan data membutuhkan 6 byte data yang setara dengan 48 bit data yang terdiri atas 1-byte untuk label tegangan, 2-byte untuk tegangan output DAC, dan 1-byte untuk label arus, serta 2-byte untuk arus yang terukur. Pengiriman 48 bit data ini memerlukan waktu 3.84 �� sehingga frekuensi maksimum �� sehingga frekuensi maksimum  sehingga frekuensi maksimum pengiriman data adalah ����������. Apabila diperhitungkan overhead (setiap byte ditambah 1 start bit dan 1 stop bit sesuai konfigurasi UART 8N1), total bit yang diperlukan adalah 60 bit dan pengiriman data membutuhkan waktu 4.8 �� sehingga frekuensi maksimumnya 208.33 kHz. � Komunikasi tanpa processing akan membutuhkan waktu total 1.6 �� untuk pembacaan dan penulisan tegangan pada ADC dan DAC ditambah 4.8 �� untuk pengiriman data dengan UART, yaitu selama �� untuk pengiriman data dengan UART, yaitu selama  untuk pengiriman data dengan UART, yaitu selama 6.4 �� sehingga frekuensi maksimum adalah 156.25 kHz. �� sehingga frekuensi maksimum adalah 156.25 kHz.  sehingga frekuensi maksimum adalah 156.25 kHz. 2. ADC 16-bit dan DAC 16-bit 

� Komunikasi tanpa processing akan membutuhkan waktu total 1.6 �� untuk pembacaan dan penulisan tegangan pada ADC dan DAC ditambah 4.8 �� untuk pengiriman data dengan UART, yaitu selama �� untuk pengiriman data dengan UART, yaitu selama  untuk pengiriman data dengan UART, yaitu selama 6.4 �� sehingga frekuensi maksimum adalah 156.25 kHz. �� sehingga frekuensi maksimum adalah 156.25 kHz.  sehingga frekuensi maksimum adalah 156.25 kHz. 

Untuk meningkatkan presisi tegangan yang dibaca oleh ADC, digunakan ADC 16-bit MCP33131-05-E/MS. Resolusi tegangan yang dapat dideteksi � adalah Volt, atau setara dengan 76.3 �V. ADC ini juga dapat �[��] berkomunikasi dengan mikrokontroler melalui protokol komunikasi serial. 

frekuensi ini digunakan untuk transmisi data dari _core_ di channel menuju PC, satu kali pengambilan data membutuhkan 6 byte data yang setara dengan 48 bit data yang terdiri atas 1-byte untuk label tegangan, 2-byte untuk tegangan output DAC, dan 1-byte untuk label arus, serta 2-byte untuk arus yang terukur. Pengiriman 48 bit data ini memerlukan waktu 3.84 �� sehingga frekuensi maksimum �� sehingga frekuensi maksimum  sehingga frekuensi maksimum pengiriman data adalah ����������. Apabila diperhitungkan overhead (setiap byte ditambah 1 start bit dan 1 stop bit sesuai konfigurasi UART 8N1), total bit yang diperlukan adalah 60 bit dan pengiriman data membutuhkan waktu 4.8 �� sehingga frekuensi maksimumnya 208.33 kHz. 

43 

DAC yang digunakan adalah DAC8531E/2K5 yang memiliki resolusi 16bit, sama seperti ADC. Mengingat resolusi tegangan yang dapat dibaca adalah 76.3 EV , maka resolusi arus terkecil yang dapat diukur adalah 

**==> picture [399 x 394] intentionally omitted <==**

**----- Start of picture text -----**<br>
(III.12)<br>Dengan memasukkan resolusi   dan nilai resistansi gain<br>maksimum 931 , didapat resolusi arus yang dapat diukur adalah 0.16 nA.<br>3. Analog Multiplexer<br>Multiplexer yang digunakan adalah ADG409BRZ. Multiplexer ini<br>menerima input berupa empat buah sinyal diferensial (S1A/B sampai<br>S4A/B, untuk setiap pilihan resistansi  gain ) serta mengeluarkan output<br>diferensial (DA dan DB) berupa salah satu dari empat sinyal tersebut, sesuai<br>sinyal yang dipilih oleh pengguna.<br>aol) 7 16] At<br>EN [2 45] GND<br>Vss [3]| ADG409 [14] Vo<br>S14 [4] | woe to [Scate)] [[23)] [$18]<br>S2A [5| 42] $28<br>83a [6] it] $38<br>S4A [7] 110) S4B 3<br>DA[ea] 9] 08 F<br>16-LEAD PLASTIC DUAL IN-LINE PACKAGE [PDIP]<br>NARROW BODY<br>(N-16)<br>Dokumen Asli<br>**----- End of picture text -----**<br>


**Gambar III.9** Susunan pin ( _pinout_ ) dari multiplexer ADG409BRZ 

44 

Multiplexer yang digunakan bekerja dengan cara mengatur resistansi input dari masing-masing kanal input, sehingga hanya kanal dengan resistansi rendah yang sinyalnya dapat diteruskan menjadi sinyal output. 

4. Operational Amplifier 

Op-Amp yang digunakan adalah IC Op-Amp OPA2197xD. Kelebihan dari 

IC ini adalah memiliki tegangan catu yang rendah. Pada penelitian ini, IC Op-Amp ini dicatu menggunakan tegangan ����, sehingga konsumsi dayanya lebih rendah. 

Op-Amp ini dicatu menggunakan tegangan dayanya lebih rendah. **III.1.5 Rangkaian Dasar Perangkat Lunak** Beberapa fungsi dasar yang diperlukan pada perangkat potensiostat yang hendak dirancang antara lain: 1. Fungsi _running_ pengukuran _Cyclic Voltammetry_ (CV) Fungsi ini menerima masukan berupa parameter-parameter pengguna untuk pengukuran CV, meliputi tegangan minimum dan maksimum pada analit, jumlah siklus yang digunakan, _scan rate_ , jumlah kanal yang digunakan. Keluaran dari fungsi ini adalah bacaan nilai arus yang mengalir pada analit serta tegangan yang bersesuaian dengan arus tersebut. Fungsi ini juga perlu mengeluarkan tegangan dalam bentuk _ramp_ minimum sampai tegangan maksimum. 2. Fungsi _running_ pengukuran _Differential Pulse Voltammetry_ (DPV) 

## **III.1.5 Rangkaian Dasar Perangkat Lunak** 

Fungsi ini menerima masukan berupa parameter-parameter pengguna untuk pengukuran CV, meliputi tegangan minimum dan maksimum pada analit, jumlah siklus yang digunakan, _scan rate_ , jumlah kanal yang digunakan. Keluaran dari fungsi ini adalah bacaan nilai arus yang mengalir pada analit serta tegangan yang bersesuaian dengan arus tersebut. Fungsi ini juga perlu mengeluarkan tegangan dalam bentuk _ramp_ meningkat dari tegangan minimum sampai tegangan maksimum. 

Fungsi ini menerima masukan berupa parameter _scan rate_ , jumlah kanal yang digunakan, serta tegangan minimum dan maksimum pada analit. Fungsi ini perlu mengeluarkan tegangan berbentuk tangga sesuai dengan penjelasan pada bab sebelumnya (Bab II), dan mengeluarkan bacaan selisih arus yang mengalir ketika tegangan berada di puncak pulsa (yaitu �����) dan di dasar pulsa (yaitu �����). 

Beberapa fungsi dasar yang diperlukan pada perangkat potensiostat yang hendak dirancang antara lain: 1. Fungsi _running_ pengukuran _Cyclic Voltammetry_ (CV) 

45 

�������� ������ 

**(III.13)** 

## 3. Fungsi _running_ pengukuran _Linear Sweep Voltammetry_ (LSV) 

Fungsi ini menerima masukan berupa parameter _scan rate_ serta tegangan minimum dan maksimum pada analit. Selama _running_ proses pengukuran 

Arus yang mengalir pada analit didefinisikan sebagai arus yang mengalir pada elektroda WE. Nilai arus ini merupakan arus yang mengalir pada resistor pada rangkaian TIA, mengingat kapasitor pada rangkaian TIA menerima tegangan dengan frekuensi yang rendah sehingga memiliki impedansi yang sangat besar (mirip open-circuit). Sehingga, arus yang mengalir pada analit adalah: 

LSV, potensiostat perlu mengeluarkan tegangan berupa _ramp_ yang tersusun atas _step_ berukuran lebih kecil. Potensiostat juga melakukan pengukuran tegangan ADC dan melakukan konversi kembali menjadi arus yang mengalir pada analit. Pada dasarnya, prinsip kerja LSV sama dengan prinsip kerja CV, namun dilakukan hanya satu arah (dari tegangan minimum ke maksimum atau sebaliknya). 4. Fungsi _running_ pengukuran _Chronoamperometry_ (CA) Analisis CA merupakan analisis yang berbeda dari analisis lainnya karena merupakan analisis berbasis amperometri. Fungsi ini menerima input berupa tegangan pada analit selama proses CA (yang bernilai konstan) serta durasi pengukuran CA. Selama proses pengukuran, potensiostat mengukur arus yang terbentuk pada analit setiap interval waktu tertentu sehingga dapat diperoleh plot arus terhadap waktu pada analit. Analisis ini berbeda dengan analisis voltametri yang mengamati plot arus terhadap tegangan analit. 5. Perhitungan arus pada analit 

46 

**==> picture [205 x 52] intentionally omitted <==**

Pada persamaan ini, �� merupakan resistansi _gain_ pada TIA yang dipilih menggunakan _multiplexer_ . Pemilihan �� yang berbeda akan menghasilkan range pengukuran arus yang berbeda, bergantung pada kebutuhan 

pengguna. Namun, mengingat mikrokontroler menerima level tegangan _output_ dari _output level shifter_ , maka persamaan di atas perlu diubah supaya dapat ditentukan hubungan ���� dengan tegangan analog yang diterima ADC ����. Ini bisa dilakukan dengan mengingat hubungan dari level shifter: ���� �[�] ����� ����[�] ����� ��� � � **(III.15)** Sehingga didapat ���� ������ ��. Pada persamaan ini, ���� merupakan tegangan keluaran dari filter Sallen-Key, dan ���� merupakan tegangan keluaran dari rangkaian TIA. Akhirnya, arus analit dapat diperoleh melalui perhitungan sederhana melalui persamaan hubungan arus dengan tegangan yang dideteksi oleh ADC, yaitu: ��[��][���][��] � � **(III.16)** 

**III.2 Skema Perangkat Keras** 

## **III.2.1 Skematik Perangkat Keras** 

Skematik rangkaian yang hendak diimplementasikan menggabungkan dua bagian besar, yaitu rangkaian untuk komunikasi data dengan perangkat pengguna (PC/Laptop), serta rangkaian pengolah data yang terhubung langsung dengan sel elektrokimia yang hendak dianalisis. 

47 

**==> picture [401 x 446] intentionally omitted <==**

**----- Start of picture text -----**<br>
xo xp Gh vinSTMS2FAS1CEUS GND aeANALOG FRONT-END FOR ADC LoaGND. GND itlsssncnnSv 11tescssccc!-5va 11teennnn-5va  nn 233B87] | rTA<br>+3.3V +5VA ; DACBS31E/2K5ut2 +A +18 5 Vv CONNECTOR REeS7SELECT RE_SELECTceJP10 ~5VA<br>C24eBcs7 re)cao 53 vooVREFVFB eneSCLKGNDDIN] SSR[7EEXC22D.54 bxe_wosT]= 20uF /Tentalumcog =th c57suf LOr=sty|SaneHAN [= seux/wo$0012kofy82<2ADC_MOsi|90e-sene]_L2-ac=aiso] == cessuf || oet eyts WE_SELECT°ers28 orfr 5ts ‘WE_SELECT°SopPi xe] A0uFceo ono<br>16-BIT DACGND GND GND || GNDL 16-BIT ADC GNDcy MCP33L31-05-£/MSGND us cnvsT}S°2"ADE NSS] GND [| ‘CELSELECT=sP9 ‘CELSELECT=Jz OP—AMPCAPACITOR:BECoUPLING<br>ANALOG|ioP+5VA FRONT-END FOR DACu5A 1if| a) lj| |aFORwere+5VAurs suppty ian|| | !ih| i|| P testpointP nctestPoint RLP TestPaint<br>1 ZDAC_OUT OPA2197xD [1i} Al|B)S| onszisnouse |‘1 { i}i sa at ellBL<br>I — 1 Zee] |! — , opazie7ed | | jour 10uF 1<br>1 || (eRE>® i! 7 it S|<br>|! eal uN || [}} oa | Sheet: /CHANNEL_27<br>| UNIPOLARLEVEL SHIFTERTo BIPOLAR || || FORFEEDBACKCE ANDAMPLIFIERRE iti} Sv tiyy | File:Title:CHANNEL 2.kicad_sch<br>wae ELLs | |eee [SizeKiCad AS£.D.A, [DateskicadReve7.0.9<br>ee a. ee ee i ce Si -  | 6<br>Gambar III.10  Skema rangkaian pengolah data potensiostat<br>Gambar III.10. di atas menunjukkan skema rangkaian pengolah data potensiostat.<br>Mikrokontroler memberikan tegangan  sweep  (rentang 0 sampai 5 V) dibantu<br>dengan DAC 16-bit, yang kemudian dilewatkan pada  Unipolar to Bipolar Level<br>Shifter  sehingga level tegangannya mencakup level tegangan negatif yang<br>diperlukan untuk reaksi redoks sel elektrokimia. Kemudian, terdapat  Analog<br>Multiplexer  yang digunakan untuk melakukan pemilihan resistansi  gain  secara<br>otomatis, serta blok  transimpedance amplifier  (TIA) untuk mengkonversi arus pada<br>elektroda WE menjadi tegangan keluaran TIA. Kemudian, tegangan analog<br>keluaran TIA dilewatkan pada Sallen-Key LPF untuk mengurangi noise serta filter<br>anti-aliasing untuk menghilangkan komponen frekuensi tinggi. Hasil tegangan ini<br>kemudian diteruskan pada ADC 16-bit supaya dapat kembali dibaca oleh<br>mikrokontroler. Tegangan yang terbaca ADC ini kemudian akan dikonversi<br>menjadi arus yang terukur pada analit.<br>Dokumen Asli<br>**----- End of picture text -----**<br>


Selain itu, diperlukan pula konektor untuk memasangkan elektroda karbon ( _Screen Printed Carbon Electrode_ /SPCE) tempat analit diteteskan. Konektor ini 

48 

dipasangkan pada ujung dari PCB sehingga memudahkan pengguna dalam memasangkan SPCE pada potensiostat ini. Potensiostat juga dirancang multikanal, yakni dapat mengukur beberapa analit dalam waktu yang bersamaan, sehingga menghemat waktu pengujian elektrokimia karena pengguna tidak perlu mengecek sifat elektrokimia larutan satu per satu, melainkan bisa dua larutan secara sekaligus. 

## **III.2.2 Skema Komunikasi dengan PC** 

**==> picture [401 x 376] intentionally omitted <==**

**----- Start of picture text -----**<br>
Perangkat potensiostat yang dirancang menggunakan tiga buah  core . Dua buah  core<br>digunakan sebagai pengolah data tegangan dan arus pada potensiostat, sedangkan<br>core  yang ketiga digunakan untuk komunikasi data antara rangkaian potensiostat<br>dengan perangkat pengguna (PC/Laptop). Skema aliran data pada sistem<br>potensiostat yang dirancang disajikan pada Gambar III.11.<br>Mikrokontroler Digital7 to Analog AnalogEnd (AFE) Front ElectrodeScreen Printed(SPE)<br>Converter (DAC)<br>SPI SPI SPI VOUT ANALOG VIN CE ANALOG CE<br>ANALOG<br>USART RE RE<br>USART 1 USART SPI ANALOG ANALOG<br>SPI SPI VIN VOUT WE WE<br>Analog to Digital<br>CHANNEL 14 Converter (ADC)<br>Mikrokontroler ConverterDigital. to Analog(DAC AnalogEnd (A F rontE} ElectrodeScreen Printed(SPE)<br>USART 2 USART SPI SPI SPI VOUT ANALOG VIN CE ANALOG CE<br>USART RE RE<br>SPI SPI SPI VIN ANALOG VOUT WE ANALOG WE<br>Analog to Digital<br>usB CHANNEL 2 Convertes (ADC)<br>USB<br>™<br>Dokumen Asli Komputer Desktop<br>**----- End of picture text -----**<br>


**Gambar III.11** Skema komunikasi data potensiostat dengan PC 

Komunikasi data antara PC/Laptop pengguna dengan mikrokontroler menggunakan USB, sedangkan komunikasi antara mikrokontroler pengolah data analog dengan mikrokontroler untuk komunikasi dengan PC menggunakan komunikasi serial. Hal ini diimplementasikan melalui dua buah pin _Universal_ 

49 

_Synchronous/Asynchronous Receiver/Transmitter_ (USART) yang terdapat pada mikrokontroler komunikasi data yang dihubungkan pada pin USART yang terdapat pada mikrokontroler pengolah data tegangan pada potensiostat. 

**==> picture [401 x 463] intentionally omitted <==**

**----- Start of picture text -----**<br>
Kemudian, mikrokontroler pengolah data potensiostat (pada masing-masing<br>channel) melakukan pertukaran data dengan ADC dan DAC untuk memberikan<br>tegangan pada analit serta untuk melakukan pembacaan tegangan analit dan<br>mengkonversinya dengan arus. Pertukaran data ini dilakukan menggunakan<br>protokol  Serial Peripheral Interface  (SPI). Pada komunikasi ini, ADC dan DAC<br>berperan sebagai  slave , dan mikrokontroler pengolah data berperan sebagai  master .<br>Skematik rangkaian komunikasi ini ditunjukkan pada Gambar III.12.<br>Ss Es 5<br>[a |Te<br>1 SwL ‘sw2 USB INTERFACE AND ! +3.3V us +8 | 1<br>| RESET +33Vgooto +33 ESD PROTECTION Hy us SPraB1OMS—L 1-8 I<br>1| [onRs>(onnsDtao-2¢onRsT) +33) tT seot f 22 z&8 io) SRVOS=4 It cs. $ANSL117-3.34 43.36 cast TsA rn wy ||<br>|!I1 433vror—mis gee* pad aeeeacitt7s334 [a[EEROOTO. pk bale 2 eee=a 2fees=B 8ai og: . tim It[ilI!i 10uFof tei>vw 3.3 SOURCE10UF 100Fxo4 a]VOLTAGE REFERENCE:=oTonF 100 +1.0¥|| H|<br>||!1 GNDartiry [o.p0070anesr4inest9teem score SS88S8SS PaoRePAZEOCTHO RxD zo5S De Fy wl [Te i!ftH uy wuuaios‘SIGNAL-ay JonPROCESSING nase !<br>H | i 1 PHO PasPASEZCRXOIX2)PO +45 sy 5 3 |I! 27761 5A !!<br>I ¢t]200° aMiiz jae el 3 xf 7 ed Vt Tay (Nour |<br>| co P02 PABELs 10uF3 ono GNDa 1!it 2.20Fcio Slew vo} [] stoRi3 se ||<br>fl1I 2]x20pF S)pctPCO pasoPAS F2¢Tx0_RXSRxO. Tes GND | | inoicarar veo FoR al Itit 16fo =yce rout ] Riefooe 22k 1|<br>1 Foca Padi DATA TRANSMISSION g Vt c 22 a7 |<br>VT ddlecs Pad2| ewral sav FS it 52 oF |<br>1\ ST=Ligka!yay romsaau Pca Be paaspSCorel Tuaswoid) *% [|etk [IsLek (|:Lf IkLoe (leS Le [heEfe [2Le [JLo [Jz HH\!| &X “qeXA om 8 oo 1|<br>!1 So<o_swDi0wee] | [RODE SGq PCT os B 10uF T . it Hy! a |<br>\ 4 DO] Po pate x Y 02 VY 03 Y 04 V os Y 0s VY 07 V7 08 Y 09 Yoso | 11 Be) eee chal practssine |<br>{| Pci0 82 rZl cel rt ogt el og Regt ogf a |!! 3 |<br>{ <oSeeeoe sdrci rors ae 2 WB B % [tl Sus<br>| <2 SWCIK]) eee fal 5 av]/ i Fo fe i i Fy yin LM27750SG sya |<br>| XoY StecssPcas P76Poe pe o | Fe ee FE \|it rtern E vou} ca '!<br>H peep Our ip] 22 ouTDIS | C14 10uF !<br>1Hl Aver+ pas p2 FI 5 3] 11] sour Chen cue H<br>1 C3 cH Aycan 2 B11pmo nom] YY, e el bi a it 2 a- tur |<br>!! '2.2uF '2.2uF pai2pPOCRXO_TXt 5 iy g 6 3) S Z| Stack interface5 Sowse] It1 =|= HH<br>1 pps pt q 3 s | RxO1x3) |! v H<br>! oko < peepspai BS ialetls<i wo efEG RSC=ELC nace]Txoexs) ||!bPono GND eno CULATION SECTION |I<br>1I1|{ | FoRMAIN baraMICROCONTROLER HANDLING GioBe7an= STMS2FHOSRGTE 10uFca cho a i)iaei)s B a,9)|& Fa |gEi3) a bia|z DIGITAL~SOEcioDATA SECTION |1||<br>TTT1<br>1HHcomes ‘SCHEMATIC FOR CHANNEL 4 AVAILABLESenEUMEON SECONDFoRBOARD enamnE 3 | ||<br>| i<br>|i| Filer CHANNEL Heee-sch |<br>H1 cme. ‘SCHEMATIC FOR CHANNEL 2 Senne Fam come 6 [|] ||<br>H1<br>HAVAILABLE ON SECOND BOARD |<br>|if}| | Fler CHANNEL 2itcad_sch5 i! Sheet 7<br>! POrRWnosr Hane | File: Quad_Channel_Potentiostat.kicad_sch<br>ss a[Size:KiCad a4EDA, [DateswicedRevs7.0.9 ST 1d: 173 é<br>Gambar III.12  Rangkaian komunikasi data antara potensiostat dengan PC<br>Dokumen Asli<br>**----- End of picture text -----**<br>


**III.3 Skema Perangkat Lunak (** _**Firmware**_ **) Potensiostat III.3.1 Algoritma** _**Cyclic Voltammetry**_ **(CV)** 

50 

Untuk analisis elektrokimia dengan teknik voltametri siklik (CV) dibutuhkan tegangan berbentuk _ramp_ yang tersusun atas _step_ dengan kenaikan yang perlahan seperti dijelaskan pada Bagian III.1.5. 

Level tegangan minimum dan maksimum yang diinginkan pada analit (berkisar �1 V) pertama dikonversikan menjadi level tegangan digital yang perlu dikeluarkan oleh DAC (berkisar 0 sampai 5 V) melalui persamaan berikut, di mana ���� merupakan tegangan yang diterima oleh ADC (dalam Volt): 

**==> picture [399 x 372] intentionally omitted <==**

Level tegangan yang pertama kali dikeluarkan oleh DAC adalah level tegangan minimum. Pada tegangan ini, dilakukan pembacaan tegangan yang diterima oleh DAC dengan persamaan yang ada pada Bagian 3.1.3. sehingga didapatkan arus yang diperoleh. Kemudian, _Serial Monitor_ akan mencetak padanan nilai arus dan tegangan yang terbentuk pada analit. 

Langkah selanjutnya adalah perhitungan level tegangan yang berikutnya akan diberikan pada analit. Nilai ini bergantung pada _scan rate_ masukan dari pengguna. Setelah itu, DAC mengeluarkan tegangan senilai tegangan sebelumnya ditambah _increment_ (kenaikan) yang bergantung _scan rate_ tersebut. Arus kembali dicari dan dicetak bersamaan dengan tegangan yang bersesuaian pada analit. 

Proses di atas akan berulang terus untuk level tegangan minimum sampai maksimum (pengukuran maju), serta sebaliknya, yaitu dari tegangan maksimum dari minimum (pengukuran mundur). Setelah itu, siklus ini akan diulang beberapa kali, bergantung pada jumlah diklus yang diminta oleh pengguna. 

Berikut _pseudocode_ untuk analisis CV. 

51 

**==> picture [134 x 135] intentionally omitted <==**

**----- Start of picture text -----**<br>
Asli<br>**----- End of picture text -----**<br>


52 

## **III.3.2 Algoritma** _**Differential Pulse Voltammetry**_ **(DPV)** 

Pengukuran DPV mengandalkan besarnya pulsa yang diberikan pada analit, dan memberikan selisih arus pada puncak pulsa dan dasar pulsa. Masukan dari fungsi ini berupa batas tegangan maksimum dan minimum pada analit, _scan rate_ , besar pulsa, durasi pulsa, tegangan _step_ , dan durasi _sampling_ . 

Terdapat variabel yang berbeda dari pengukuran CV yaitu besar pulsa, durasi pulsa, 

tegangan _step_ , dan durasi _sampling_ . Pada pengukuran DPV, besar pulsa merupakan selisih tegangan antara dasar pulsa dan puncak pulsa, sedangkan durasi pulsa merupakan durasi tegangan puncak pulsa diberikan pada analit. Durasi ini diimplementasikan menggunakan _counter_ dengan periode sebesar durasi _sampling_ sebesar selama durasi pulsa , sehingga pulsa akan berakhir apabila 

_counter_ sudah mencapai nilai tertentu, yaitu: 

**(III.18)** 

Berikut pseudocode untuk fungsi DPV. 

53 

**==> picture [72 x 72] intentionally omitted <==**

**----- Start of picture text -----**<br>
li<br>**----- End of picture text -----**<br>


**III.3.3 Algoritma** _**Linear Sweep Voltammetry**_ **(LSV)** Pengukuran LSV memiliki parameter input yang sama persis dengan CV, kecuali parameter input jumlah siklus, dikarenakan LSV hanya memberikan tegangan _sweep_ satu arah dari negatif ke positif pada analit. Selain itu, cara kerjanya sama persis dengan pengukuran CV. Berikut pseudocode untuk fungsi implementasi LSV. 

## **III.3.3 Algoritma** _**Linear Sweep Voltammetry**_ **(LSV)** 

54 

**III.3.4 Algoritma** _**Chronoamperometry**_ **(CA)** Pengukuran CA merupakan plot yang berbasis amperometri, yaitu menganalisis arus pada analit terhadap waktu berjalannya reaksi. Fungsi pengukuran CA menerima input berupa tegangan yang hendak diberikan pada analit, waktu interval pengambilan data arus, serta waktu berjalannya CA. Berikut _pseudocode_ untuk algoritma pengukuran CA. 

## **III.3.4 Algoritma** _**Chronoamperometry**_ **(CA)** 

55 

**==> picture [401 x 372] intentionally omitted <==**

**----- Start of picture text -----**<br>
III.4  Rancangan PCB Potensiostat<br>III.4.1 Penempatan Komponen/ Layout  pada PCB<br>Penempatan masing-masing komponen rangkaian disajikan pada Gambar III.13 di<br>bawah ini.<br>Core 2 Core 3<br>(Data Processing) (Data Processing)<br>Konektor Core 1 Analog Front End Analog Front End<br>USB (Communications) (AFE) Circuit (AFE) Circuit<br>Channel 1 Channel 2<br>Konektor SPCE Konektor SPCE<br>Channel 1 Channel 2<br>Dokumen Asli<br>**----- End of picture text -----**<br>


**Gambar III.13** Rencana _layout_ komponen pada PCB 

Penempatan blok rangkaian memperhatikan cara penggunaan alat ini. Konektor SPCE harus dipasang pada bagian pinggir PCB supaya memudahkan pemasangan konektor SPCE, begitu pula dengan pemasangan konektor USB ke perangkat yang digunakan oleh pengguna. Penataan komponen di atas juga memisahkan bagian komunikasi data dengan laptop dengan bagian pemroses data potensiostat. Adapun 

56 

hasil _layouting_ dari rangkaian potensiostat ini menggunakan perangkat lunak KiCad dapat dilihat pada Gambar III.14 di bawah ini. 

a= KC a aes ay a **Gambar III.14** Hasil _layouting_ pada perangkat lunak KiCad Untuk memudahkan proses _troubleshooting_ , dibuat pula beberapa _pin_ yang dapat dihubungkan dengan kabel jumper maupun kabel buaya, serta _pin_ tegangan Ground sebagai acuan supaya dalam proses pengujian, apabila terjadi kesalahan, dapat dilakukan pengecekan apakah bentuk tegangan yang dikeluarkan sudah sesuai dengan yang diinginkan atau belum. Pin-pin ini terletak pada ujung papan, di dekat tempat pemasangan elektroda SPCE pada papan potensiostat. **III.4.2 Rancangan Rangkaian Fisik PCB** Menggunakan perangkat lunak KiCad, didapat hasil _3D Rendering_ rangkaian fisik potensiostat seperti berikut. 

Menggunakan perangkat lunak KiCad, didapat hasil _3D Rendering_ rangkaian fisik potensiostat seperti berikut. 

57 

**==> picture [370 x 372] intentionally omitted <==**

**----- Start of picture text -----**<br>
Gambar III.15  Hasil 3D  Rendering  dari rangkaian potensiostat<br>III.5  Perangkat Pembanding<br>Performansi potensiostat ini akan dibandingkan dengan potensiostat PalmSens4<br>yang tersedia secara komersil. Berikut beberapa spesifikasi dari potensiostat<br>PalmSens4:<br>1. Rentang tegangan DC: -5 V sampai +5 V<br>2. Arus maksimum: 30 mA<br>3. Resolusi tegangan DC 76.3<br>4. Akurasi tegangan yang dikeluarkan:   dengan  offset   1 mV<br>5. Rentang arus yang dapat diukur: 100 pA dampai 10 mA (terdapat 9<br>rus yang bisa diukur)<br>6. Akurasi pengukuran arus:<br>7. Resolusi arus yang diukur: 5 fA pada rentang 100 pA, 0.0025% dari rentang<br>10 mA<br>en Asli<br>Doku<br>**----- End of picture text -----**<br>


## **III.5 Perangkat Pembanding** 

Performansi potensiostat ini akan dibandingkan dengan potensiostat PalmSens4 yang tersedia secara komersil. Berikut beberapa spesifikasi dari potensiostat PalmSens4: 

5. Rentang arus yang dapat diukur: 100 pA dampai 10 mA (terdapat 9 _range_ rus yang bisa diukur) 

7. Resolusi arus yang diukur: 5 fA pada rentang 100 pA, 0.0025% dari rentang 10 mA 

**III.6 Harga** 

Dana yang dibutuhkan pada implementasi potensiostat ini dirincikan pada Tabel III.1. sebagai berikut. 

58 

**Tabel II.1** Biaya produksi potensiostat 

|**Tabel II.1**Biaya produksi potensiostat||
|---|---|
|Rincian|Biaya|
|Print PCB, komponen, jasa_assembly_untuk 5 PCB|Rp5.266.557,00|
|Biaya pengiriman|Rp   236.237,00|
|Pajak dan bea cukai|Rp1.125.364,00|
|**Total harga untuk 5 PCB**|Rp6.628.178,00|



Dari rincian harga di atas, biaya yang dibutuhkan untuk pembuatan satu board PCB adalah Rp1.325.635,00. Biaya ini sudah termasuk biaya pengiriman dan pajak serta bea cukai. Tanpa menghitung biaya tersebut, harga produksi per PCB potensiostat adalah Rp1.053.311,00. 

59 

## **Bab IV    Pengujian Sistem** 

## **IV.1 Desain Skema Pengujian** 

## **IV.1.1 Skema Pengujian** 

Pengujian alat potensiostat yang telah dirancang dilakukan dengan cara membandingkan data yang diperoleh dari potensiostat ini dengan data yang diperoleh pada potensiostat komersil, yaitu EmStat4. Larutan yang hendak 

digunakan sebagai analit adalah larutan kalium ferisianat (K3[Fe(CN)63[Fe(CN)6[Fe(CN)66]) dengan lima variasi konsentrasi. Terdapat dua tahapan pengujian dari alat yang dirancang, yaitu: 1. Pengujian Tegangan Keluaran Pada pengujian tahap pertama, pengguna memasukkan parameterparameter pengukuran yang hendak dilakukan untuk pengukuran CV, DPV, LSV, dan CA. Hasil tegangan keluaran diamati dengan menggunakan osiloskop, kemudian dibandingkan dengan tegangan input yang seharusnya yang terdapat pada literatur. 2. Pengujian Analisis Elektrokimia Tahapan terakhir pengujian merupakan tahap yang serupa dengan tahap kedua, namun resistor digantikan dengan larutan kalium ferisianat (K3[Fe(CN)6]) sebagai analit. Hasil pengujian ini akan dibandingkan 3[Fe(CN)6]) sebagai analit. Hasil pengujian ini akan dibandingkan [Fe(CN)6]) sebagai analit. Hasil pengujian ini akan dibandingkan 6]) sebagai analit. Hasil pengujian ini akan dibandingkan ]) sebagai analit. Hasil pengujian ini akan dibandingkan dengan pengujian voltammogram yang dihasilkan oleh potensiostat komersil yaitu EmStat4. **IV.1.2 Parameter Pengujian** 

**==> picture [365 x 95] intentionally omitted <==**

**----- Start of picture text -----**<br>
Pada pengujian tahap pertama, pengguna memasukkan parameter-<br>parameter pengukuran yang hendak dilakukan untuk pengukuran CV, DPV,<br>LSV, dan CA. Hasil tegangan keluaran diamati dengan menggunakan<br>osiloskop, kemudian dibandingkan dengan tegangan input yang seharusnya<br>yang terdapat pada literatur.<br>**----- End of picture text -----**<br>


Tahapan terakhir pengujian merupakan tahap yang serupa dengan tahap kedua, namun resistor digantikan dengan larutan kalium ferisianat (K3[Fe(CN)6]) sebagai analit. Hasil pengujian ini akan dibandingkan 3[Fe(CN)6]) sebagai analit. Hasil pengujian ini akan dibandingkan [Fe(CN)6]) sebagai analit. Hasil pengujian ini akan dibandingkan 6]) sebagai analit. Hasil pengujian ini akan dibandingkan ]) sebagai analit. Hasil pengujian ini akan dibandingkan dengan pengujian voltammogram yang dihasilkan oleh potensiostat komersil yaitu EmStat4. 

## **IV.1.2 Parameter Pengujian** 

Berikut beberapa parameter yang akan diujikan dari potensiostat yang telah dirancang. 

1. Parameter Pengujian Pengukuran Berbasis Voltametri (CV, DPV, LSV) 

Pada pengukuran CV, parameter yang hendak dibandingkan adalah arus puncak anodik dan katodik (Ipa dan Ipc berturut-turut), serta tegangan puncak 

digunakan sebagai analit adalah larutan kalium ferisianat (K3[Fe(CN)63[Fe(CN)6[Fe(CN)66]) dengan lima variasi konsentrasi. Terdapat dua tahapan pengujian dari alat yang dirancang, yaitu: 

60 

anodik dan katodik (Epa dan Epc berturut-turut). Keempat parameter ini diilustrasikan pada contoh voltammogram pada Gambar IV.1 berikut[20]. 

**==> picture [399 x 372] intentionally omitted <==**

**----- Start of picture text -----**<br>
a Be<br>65 3 i<br>i<br>E<br>PC<br>0.2 0.0 0.2 o.4 0.6 0.8<br>Potential [V]<br>Gambar IV.1  Contoh kurva voltamogram CV<br>Selain itu, dilakukan pula uji linearitas pada sistem, yaitu dengan melakukan<br>analisis regresi linear antara potensial puncak dan arus puncak anodik<br>maupun katodik. Nilai koefisien korelasi juga akan diamati sehingga<br>kualitas linearitas antara kedua variabel ini dapat terlihat dengan jelas.<br>Kurva regresi linear ini disebut sebagai kurva kalibrasi.[21]<br>5.00<br>450 ®) Js<br>400 P ii<br>Dokumen Asli<br>**----- End of picture text -----**<br>


**Gambar IV.2** Contoh kurva kalibrasi 

61 

**==> picture [399 x 521] intentionally omitted <==**

**----- Start of picture text -----**<br>
Pada pengukuran DPV, parameter yang hendak diukur sama dengan CV,<br>namun hanya pada bagian anodik (positif). Diamati arus puncak dan<br>tegangan puncak untuk beberapa konsentrasi, serta dilakukan pengamatan<br>linearitas melalui kurva kalibrasi yang dihasilkan dengan analisis regresi<br>linear. Sama pula dengan pengukuran LSV yang hanya melibatkan setengah<br>siklus pengukuran CV, parameter yang dilihat hanyalah arus puncak dan<br>tegangan yang bersesuaian pada kondisi katodik, serta pengamatan kurva<br>kalibrasi untuk menganalisis linearitas sistem.<br>2. Parameter Pengujian Pengukuran Chronoamperometry (CA)<br>Pengujian CA melihat arus yang terbentuk pada analit sebagai fungsi dari<br>waktu. Pengamatan yang dilakukan adalah besarnya arus  steady-state  yang<br>terbentuk pada analit saja, mengingat tegangan yang diberikan pada analit<br>bernilai konstan. Dilakukan pula kurva kalibrasi untuk melihat pengaruh<br>konsentrasi analit yang digunakan terhadap arus  steady-state  yang<br>terbentuk, seperti disajikan pada Gambar IV.3 berikut.[22]<br>(a)<br>35 (b)<br>33<br>34 2 pg/mL € 3.4<br>gut427as |f woe “ 3i==] =3 | lt: i :<br>225 = 2.8 t<br>ios N 0.5 pg/mL £26 i = 0.2478¢+ 2.6819<br>3” SQ ee R?= 0.8898<br>52a & 2.4<br>E19 \ EI<br>a! Re : o=<br>17 4) I:| °. 2<br>1s | ———— —__ 0 0.5 1 5 2<br>13 Concentration (ug/mL)<br>0.025 0.05 0.075 O.1 0.125 0.15 0.175 0.2 0.225 0.25<br>Dokumen Asli<br>**----- End of picture text -----**<br>


**Gambar IV.3** (a) Contoh kurva arus CA dan (b) Contoh kurva kalibrasi CA 

## **IV.2 Hasil Pengujian** 

## **IV.2.1 Bentuk Tegangan Keluaran** 

Dilakukan pengujian tegangan keluaran untuk seluruh mode pengukuran. Rentang tegangan keluaran yang diuji adalah rentang -1 V sampai +1 V. Secara umum, 

62 

potensiostat ini sudah mampu mengeluarkan tegangan yang sesuai dengan profil tegangan masing-masing pengukuran. 

Grafik tegangan pada analit untuk pengukuran CV disajikan pada gambar berikut. Pada gambar ini, digunakan _scan rate_ sebesar 50 mV/s dengan range tegangan -1 sampai 1 V, sehingga periode gelombang segitiga yang dihasilkan adalah 80 detik. Dilakukan proses _output_ sinyal sebanyak dua kali siklus dan didapat hasil tegangan keluaran yang sesuai dengan yang diinginkan. 

**==> picture [401 x 372] intentionally omitted <==**

**----- Start of picture text -----**<br>
CV Voltage (V)<br>1.5<br>1<br>_= 0.5<br>oO<br>2 0<br>re 0 20 40 60 80 00 120 14 160 180<br>> -0.5<br>-1<br>“1.5<br>Time (s)<br>Gambar IV.4  Hasil tegangan keluaran CV<br>Bentuk tegangan keluaran LSV serupa dengan CV, namun  sweep  tegangan hanya<br>dilakukan pada satu arah. Pada pengujian ini, dilakukan percobaan keluaran<br>tegangan LSV untuk  scan rate  50 mV/s pada rentang tegangan -1 sampai 1 V,<br>sehingga durasi keluaran tegangan yang diperlukan adalah 40 detik. Profil tegangan<br>LSV ini sudah sesuai dengan literatur.<br>Dokumen Asli<br>**----- End of picture text -----**<br>


63 

**Gambar IV.6** Hasil tegangan keluaran DPV 

Pengujian tegangan keluaran CA dilakukan untuk tegangan _step_ sebesar 1 V dengan durasi 20 detik. Tegangan keluaran dari potensiostat sudah sesuai dengan yang disajikan pada literatur referensi. 

-1.5 Time (s) **Gambar IV.5** Hasil tegangan keluaran LSV Pengujian tegangan keluaran DPV dilakukan dengan range tegangan -1 sampai 1 V. Didapatkan bentuk tangga dengan besar pulsa 0.2 V dan besar tegangan _step_ sebesar 50 mV. Pola tegangan ini akan diteruskan sampai tegangan dasar pulsa sebesar 1 V. Profil tegangan yang didapatkan sudah sesuai dengan profil yang seharusnya. DPV Voltage (V) 0 0 50 100 150 200 250 300 350 400 450 -0.2 — 0.4 = oO 9 -0.6 iS > 0.8 -1 -1.2 

64 

-10 5 0 5 10 15 20 25 Time (s) **Gambar IV.7** Hasil tegangan keluaran CA Secara umum, tegangan keluaran dari potensiostat sudah sesuai dengan literatur. Oleh karena itu, dilakukan tahapan pengujian berikutnya yaitu pengujian karakteristik senyawa kimia dengan berbagai metode pengukuran yang telah diujikan sebelumnya. **IV.2.2 Pengujian Karakteristik Elektrokimia Senyawa K3 6]** Berikut hasil pengujian karakteristik elektrokimia senyawa kalium ferisianat (K3[Fe(CN)6]) menggunakan metode pengukuran CV, DPV, CA, dan LSV. 3[Fe(CN)6]) menggunakan metode pengukuran CV, DPV, CA, dan LSV. [Fe(CN)6]) menggunakan metode pengukuran CV, DPV, CA, dan LSV. 6]) menggunakan metode pengukuran CV, DPV, CA, dan LSV. ]) menggunakan metode pengukuran CV, DPV, CA, dan LSV. 1. Hasil Pengukuran Metode _Cyclic Voltammetry_ (CV) Pengukuran CV dilakukan pada larutan kalium ferisianat dengan lima variasi konsentrasi molar, yaitu 2.5 mM, 5.0 mM, 10.0 mM, 15.0 mM, dan 20.0 mM. Sebelumnya, telha disiapkan larutan kalium ferisianat dengan melarutkan padatan kalium ferisianat dengan massa yang sesuai dalam pelarut _Phosphate-buffered saline_ (PBS) 0.1 M untuk menjaga kestabilan 

**==> picture [400 x 75] intentionally omitted <==**

**----- Start of picture text -----**<br>
Secara umum, tegangan keluaran dari potensiostat sudah sesuai dengan literatur.<br>Oleh karena itu, dilakukan tahapan pengujian berikutnya yaitu pengujian<br>karakteristik senyawa kimia dengan berbagai metode pengukuran yang telah<br>diujikan sebelumnya.<br>**----- End of picture text -----**<br>


Berikut hasil pengujian karakteristik elektrokimia senyawa kalium ferisianat (K3[Fe(CN)6]) menggunakan metode pengukuran CV, DPV, CA, dan LSV. 3[Fe(CN)6]) menggunakan metode pengukuran CV, DPV, CA, dan LSV. [Fe(CN)6]) menggunakan metode pengukuran CV, DPV, CA, dan LSV. 6]) menggunakan metode pengukuran CV, DPV, CA, dan LSV. ]) menggunakan metode pengukuran CV, DPV, CA, dan LSV. 

Pengukuran CV dilakukan pada larutan kalium ferisianat dengan lima variasi konsentrasi molar, yaitu 2.5 mM, 5.0 mM, 10.0 mM, 15.0 mM, dan 20.0 mM. Sebelumnya, telha disiapkan larutan kalium ferisianat dengan melarutkan padatan kalium ferisianat dengan massa yang sesuai dalam pelarut _Phosphate-buffered saline_ (PBS) 0.1 M untuk menjaga kestabilan pH larutan. Keluaran dari pengujian ini adalah voltammogram dari larutan kalium ferisianat, yakni grafik yang menunjukkan hubungan tegangan yang diberikan pada analit dengan arus yang mengalir pada analit. Parameter yang digunakan pada pengukuran CV ini adalah _scan rate_ 50 mV/s serta rentang tegangan pada analit sebesar -1 sampai 1 V. 

65 

**Gambar IV.9** Hasil pengujian CV larutan K3[Fe(CN)6] pada Channel 2 

Hasil pengukuran CV menunjukkan tren arus listrik yang mengalir pada analit menjadi semakin besar untuk konsentrasi analit yang semakin besar. 

a — 25mM — 5mM gn 10 mM — 15mM — 20mM -75 1 -0,5 0 0,5 1 Voltage (V) **Gambar IV.8** Hasil pengujian CV larutan K3[Fe(CN)6] pada Channel 1 pas, 50 . (SSS -25+ & a NS — 2.5mM — 5mM 50 10 mM — 15mM — 20mM -715 

66 

Hal ini sudah sesuai dengan yang tercantum pada berbagai literatur. Dalam pengukuran CV, terdapat dua buah arus puncak, yakni arus puncak anodik (Ipa) yang merupakan arus puncak positif, serta arus puncak katodik (Ipc) yang merupakan arus puncak negatif. Besaran arus tersebut dirangkum pada tabel di bawah, dengan data arus referensi yang diambil dari potensiostat PalmSens4. 

||<br>Konsentrasi<br>(mM)<br>2.5<br>5<br>10<br>15<br>20|<br>**Tabel IV.1**Data arus anodik CV larutan K3[Fe(CN)6]|<br>**Tabel IV.1**Data arus anodik CV larutan K3[Fe(CN)6]|<br>**Tabel IV.1**Data arus anodik CV larutan K3[Fe(CN)6]|
|---|---|---|---|---|
|||<br> <br>Arus puncak Ipa(�A)<br>Arus<br>referensi<br>(�A)<br>Channel 1<br>Channel 2||<br>Galat (%)|
|||||sl<br>Channel 1 Channel 2|
|||en<br>8.77<br>8.41<br>7.98<br>17.01<br>16.04<br>17.25<br>33.00<br>36.02<br>34.32<br>54.55<br>58.29<br>54.28<br>72.10<br>76.31<br>73.31||<br>9.96<br>5.48<br>1.39<br>6.99<br>3.86<br>4.94<br>0.50<br>7.39<br>1.66<br>4.10|
|||<br>**Tabel IV.2**Data arus katodik CV larutan K3[Fe(CN)6]|||
||<br>Konsentrasi<br>(mM)|um<br>Arus puncak Ipc(�A)<br>Arus<br>referensi<br>(�A)<br>Channel 1<br>Channel 2|<br>Galat (%)||
||||<br>Channel 1<br>Channel 2||
||Do<br>2.5<br>5<br>10<br>15<br>20|<br>7.46<br>7.71<br>7.68<br>16.59<br>20.01<br>17.40<br>36.29<br>38.72<br>38.15<br>58.92<br>61.69<br>61.76<br>79.85<br>83.05<br>84.94|<br>2.88<br>0.43<br>4.66<br>15.01<br>4.89<br>1.50<br>4.60<br>0.11<br>5.99<br>2.22||



Dari data yang didapat, akurasi relatif dari data ini dapat dihitung menggunakan persamaan 

**==> picture [166 x 32] intentionally omitted <==**

Rata-rata akurasi relatif dari data di atas adalah 95.57% dan rata-rata galat dari data-data yang didapat adalah 1.51 �A. Terdapat perbedaan data 

67 

dengan data referensi dikarenakan kondisi elektroda yang tidak sempurna serta terdapat kemungkinan galat pada konsentrasi zat yang digunakan sehingga tidak eksak sesuai dengan nilai yang tertulis (2.5, 5, 10, 15, atau 20 mM). 

Ketidaksempurnaan reaksi redoks pada elektroda merupakan faktor yang penting yang dapat mengubah nilai arus yang terukur. Hal ini dapat terlihat 

**==> picture [399 x 376] intentionally omitted <==**

**----- Start of picture text -----**<br>
juga ketika pengukuran analit yang sama menggunakan potensiostat<br>komersil PalmSens4, didapat hasil pengukuran yang tidak sama persis.<br>Sehingga, adanya perbedaan antara kedua potensiostat (PalmSens4 dan<br>hasil tesis ini) merupakan sesuatu yang wajar. Selain itu, terdapat<br>kemungkinan adanya perbedaan tegangan antara tegangan  sweep  yang<br>diberikan potensiostat ini dengan PalmSens4.<br>Selanjutnya, dapat disimpulkan pula bahwa data arus anodik dan katodik<br>untuk kedua kanal bersifat linear terhadap konsentrasinya. Hal ini dapat<br>dibuktikan menggunakan kurva kalibrasi berikut, yakni grafik yang<br>menunjukkan hubungan antara arus puncak Ipa dan Ipc dengan konsentrasi.<br>100<br>— Ch1 Anodic Current<br>— Ch2Anodic Current<br>-------- Ch2Ch1 CathodicCathodic CurrentCurrent os<br>50 Zo<br>a"<br>=<<br>=a<br>= 0<br>5= RKSy<br>Dokumen Asli<br>**----- End of picture text -----**<br>


**Gambar IV.10** Hasil kurva kalibrasi CV larutan K3[Fe(CN)6] 

68 

Terdapat empat persamaan regresi linear dari data yang ditunjukkan, yang dirangkum pada tabel di bawah ini dengan � menunjukkan konsentrasi larutan kalium ferisianat dalam mM, serta � menunjukkan arus yang mengalir pada analit dalam satuan ��. 

69 

**Tabel IV.3** Persamaan kurva kalibrasi CV larutan K3[Fe(CN)6] 

|Data Arus|Persamaan Regresi|Nilai R2|
|---|---|---|
|Arus anodik kanal 1|����������������|0.9974|
|Arus anodik kanal 2|����������������|0.9982|
|Arus katodik kanal 1|����������������|0.9990|
|Arus katodik kanal 2|����������������|0.9990|



|okumen Asli<br>Keseluruhan data telah menunjukkan linearitas yang baik, dilihat dari nilai<br>��yang mendekati 1.<br>Konsentrasi maksimum larutan yang dapat diukur juga dapat dicari<br>menggunakan fakta bahwa tegangan yang diterima ADC maksimal adalah<br>5 V dan tegangan minimal yang dapat terbaca yang bukan nol adalah<br>�<br>�����<br>V. Dari bab sebelumnya, didapat bahwa arus maksimum yang mengalir<br>pada analit adalah 6097.56��dan arus minimumnya 0.02232��. Dengan<br>memasukkan nilai arus ini pada masing-masing persamaan regresi, didapat<br>data rentang konsentrasi linear yang dapat terukur adalah sebagai berikut.<br>**Tabel IV.4**Rentang konsentrasi larutan K3[Fe(CN)6] terukur dengan metode CV<br>Data arus<br>Konsentrasi<br>maksimum<br>Konsentrasi<br>minimum<br>Arus anodik kanal 1<br>1.67 M<br>0.36 mM<br>Arus anodik kanal 2<br>1.54 M<br>0.67 mM<br>Arus katodik kanal 1<br>1.46 M<br>0.94 mM<br>Arus katodik kanal 2<br>1.45 M<br>0.61 mM|
|---|



�[�] yang mendekati 1. Konsentrasi maksimum larutan yang dapat diukur juga dapat dicari menggunakan fakta bahwa tegangan yang diterima ADC maksimal adalah 5 V dan tegangan minimal yang dapat terbaca yang bukan nol adalah V. Dari bab sebelumnya, didapat bahwa arus maksimum yang mengalir pada analit adalah 6097.56 �� dan arus minimumnya 0.02232 �� memasukkan nilai arus ini pada masing-masing persamaan regresi, didapat data rentang konsentrasi linear yang dapat terukur adalah sebagai berikut. **Tabel IV.4** Rentang konsentrasi larutan K3[Fe(CN)6] terukur dengan metode CV Konsentrasi Konsentrasi Data arus maksimum minimum Arus anodik kanal 1 1.67 M 0.36 mM Arus anodik kanal 2 1.54 M 0.67 mM Arus katodik kanal 1 1.46 M 0.94 mM Arus katodik kanal 2 1.45 M 0.61 mM 

Dengan mengambil irisan dari konsentrasi minimum dan maksimum yang dapat terukur, dapat disimpulkan bahwa rentang linearitas dari potensiostat yang dirancang untuk pengukuran CV pada larutan kalium ferisianat adalah untuk konsentrasi 0.94 mM sampai dengan konsentrasi 1.45 M. 

2. Hasil Pengukuran Metode _Linear Sweep Voltammetry_ (LSV) 

70 

**==> picture [399 x 521] intentionally omitted <==**

**----- Start of picture text -----**<br>
Telah dilakukan pula pengukuran LSV pada larutan kalium ferisianat<br>dengan lima variasi konsentrasi (2.5, 5, 10, 15, 20 mM) dalam pelarut PBS<br>0.1 M. Pengukuran LSV dilakukan dengan parameter  scan rate  50 mV/s<br>dan rentang tegangan -0.6 sampai 0.3 V. Keluaran dari pengukuran ini sama<br>dengan pada pengukuran CV, yakni voltammogram atau plot arus yang<br>mengalir pada analit terhadap tegangan yang diberikan pada analit.<br>— 2.5mM<br>— 5mM<br>10 mM<br>607 — 15mM<br>| — 20mm<br><<br>= [40]<br>c<br>£<br>|<br>(6)<br>20 4<br>————<br>-0,6 -0,4 -0,2 0 0,2 0,4<br>Voltage (V)<br>Gambar IV.11  Hasil pengujian LSV larutan K3[Fe(CN)6] pada Channel 1<br>—<br>60 — 2.5mM<br>— 5mM<br>10 mM<br>— 15mM<br>— 20mM<br>40<br><<br>=5 .<br>=<br>=<br>S)<br>Dokumen Asli<br>**----- End of picture text -----**<br>


**Gambar IV.12** Hasil pengujian LSV larutan K3[Fe(CN)6] pada Channel 2 

71 

Poin yang menarik yang dapat ditarik dari voltammogram ini adalah bentuknya yang cukup menyerupai arus puncak anodik pada pengukuran CV. Hal ini masuk akal dikarenakan tegangan yang diberikan pada pengukuran LSV merupakan setengah siklus dari pengukuran CV, sehingga arus yang dihasilkan pun hanya bagian arus yang bernilai positif (anodik). 

**==> picture [399 x 376] intentionally omitted <==**

**----- Start of picture text -----**<br>
Hasil pengukuran LSV menunjukkan tren meningkatnya arus puncak untuk<br>konsentrasi analit yang semakin besar, yang sudah sesuai dengan yang<br>terdapat pada literatur. Pengamatan akan nilai arus puncak Ipa dari<br>pengukuran LSV serta perbandingannya dengan arus yang didapat pada<br>potensiostat PalmSens4 dapat dilihat pada tabel berikut.<br>Tabel IV.5  Data arus LSV larutan K3[Fe(CN)6]<br>Arus puncak (�A)  Galat (%)<br>Konsentrasi  Arus referensi<br>Channel  Channel  Channel  Channel<br>(mM)  (�A)<br>1  2  1  2<br>2.5 7.65 7.13 5.665 35.06 25.82<br>5 16.61 15.59 15.25 8.92 2.24<br>10 34.61 34.52 30.97 11.77 11.45<br>15 52.15 51.30 48.78 6.92 5.16<br>20 71.42 68.46 67.83 5.29 0.93<br>Hasil pengukuran menunjukkan akurasi yang cukup baik, khususnya untuk<br>konsentrasi di atas 2.5 mM. Rata-rata akurasi relatif yang dihitung<br>menggunakan rumus yang sama dengan sebelumnya adalah 88.64% dengan<br>Dokumen Asli<br>**----- End of picture text -----**<br>


Hasil pengukuran menunjukkan akurasi yang cukup baik, khususnya untuk konsentrasi di atas 2.5 mM. Rata-rata akurasi relatif yang dihitung menggunakan rumus yang sama dengan sebelumnya adalah 88.64% dengan rata-rata galat absolut dari arus yang terukur sebesar 2.24 ��. Hal yang menarik dari data ini adalah linearitas dari potensiostat yang dirancang pada penelitian ini ternyata lebih baik daripada linearitas yang diperoleh dari data pada potensiostat referensi PalmSens4. Adapun perbedaan data yang didapat pada kedua potensiostat dapat disebabkan oleh kondisi elektroda yang tidak sempurna dan galat pada konsentrasi analit yang dapat disebabkan oleh galat atau ketidaktelitian dalam proses pembautan larutan. 

72 

Selanjutnya, uji linearitas dari arus pada kedua kanal dapat diuji melalui pembuatan kurva kalibrasi. Kurva kalibrasi disajikan pada gambar di bawah ini. 

|Dokumen Asli<br>**Gambar IV.13**Hasil kurva kalibrasi LSV larutan K3[Fe(CN)6]<br>Terdapat dua persamaan regresi linear dari data yang ditunjukkan, yang<br>dirangkum pada tabel di bawah ini dengan  menunjukkan konsentrasi<br>larutan kalium ferisianat dalam mM, serta<br>menunjukkan arus yang<br>mengalir pada analit dalam satuan<br>.<br>**Tabel IV.6**Persamaan kurva kalibrasi LSV larutan K3[Fe(CN)6]<br>Data Arus<br>Persamaan Regresi<br>Nilai R2<br>Arus puncak kanal 1<br>0.9974<br>Arus puncak kanal 2<br>0.9982<br>x=<br>5<br>40<br>s<br>oO<br>20<br>0<br>esa<br>eT<br>A<br>0<br>5<br>10<br>15<br>20<br>Concentration (mM)|
|---|



Nilai R[2] yang mendekati 1 menunjukkan bahwa arus memiliki hubungan linear dengan konsentrasi analit pada rentang 2.5 sampai dengan 20 mM. Dengan cara yang sama dengan pengukuran CV, dapat didapat pula konsentrasi maksimum dan minimum yang dapat terukur oleh potensiostat ini melalui masing-masing kanal adalah sebagai berikut. 

73 

**Tabel IV.7** Rentang konsentrasi terukur larutan K3[Fe(CN)6] metode LSV 

|Data kanal|Konsentrasi|Konsentrasi|
|---|---|---|
||maksimum|minimum|
|Kanal 1|1.68 M|0.42 mM|
|Kanal 2|1.73 M|0.43 mM|



Dari data konsentrasi di atas, dapat disimpulkan bahwa melalui pengambilan irisan kedua rentang konsentrasi yang dapat terukur, pengukuran LSV pada potensiostat yang dirancang memiliki rentang konsentrasi 0.43 mM sampai 1.68 M. 3. Hasil Pengukuran Metode _Differential Pulse Voltammetry_ (DPV) Telah dilakukan pula pengukuran DPV pada larutan kalium ferisianat dengan lima variasi konsentrasi (2.5, 5, 10, 15, 20 mM) dalam pelarut PBS 0.1 M. Pengukuran LSV dilakukan dengan parameter _scan rate_ 50 mV/s dan rentang tegangan -0.6 sampai 0.3 V, tinggi pulsa sebesar 0.2 V, dan besar _step voltage_ sebesa 5 mV sehingga didapat jumlah data sebesar 180 titik. Voltammogram hasil DPV disajikan pada gambar di bawah ini. 200 — 25mM — 5mM 10 mM — 15mM — 20mM 150 = =| 5 5[100] 

**Gambar IV.14** Hasil pengujian DPV larutan K3[Fe(CN)6] pada Channel 1 

74 

|Dokumen Asli<br>**Gambar IV.15**Hasil pengujian DPV larutan K3[Fe(CN)6] pada Channel 2<br>Dari hasil pengukuran DPV, dapat terlihat bahwa arus puncak selalu<br>meningkat seiring peningkatan konsentrasi, yang dirangkum dalam tabel<br>berikut sekaligus dengan perbandingan masing-masing arus puncak dengan<br>data arus puncak referensi pada potensiostat PalmSens4. Pengukuran DPV<br>menghasilkan grafik selisih arus pada puncak pulsa dan dasar pulsa, dan<br>pada potensial yang lebih kecil dari potensial puncak, didapat arus DPV<br>yang konstan, karena hilangnya efek arus kapasitif yang menyebabkan<br>kurva voltammogram menjadi miring pada pengukuran CV dan DPV.<br>**Tabel IV.8**Data arus DPV larutan K3[Fe(CN)6]<br>Konsentrasi<br>(mM)<br>Arus puncak ( A)<br>Arus<br>referensi<br>( A)<br>Galat (%)<br>Channel 1<br>Channel 2<br>Channel 1<br>Channel 2<br>50<br>0<br>-0,6<br>-0,4<br>-0,2<br>0<br>0,2<br>0,4<br>Voltage (V)<br>LU|
|---|
|2.5<br>18.28<br>16.91<br>17.76<br>2.92<br>4.79|
|5<br>40.10<br>50.69<br>35.99<br>11.43<br>40.84|
|10<br>82.35<br>92.75<br>80.86<br>1.84<br>14.70|
|15<br>147.60<br>128.44<br>127.1<br>16.13<br>1.05|
|20<br>180.19<br>173.55<br>174.3<br>3.38<br>0.43|



75 

Dari data arus puncak DPV, didapatkan besarnya akurasi relatif sebesar 90.25% dan galat absolut sebesar 6.20 L A. Berikutnya, dilakukan uji linearitas melalui pembuatan plot kalibrasi dengan nilai y sebagai arus puncak dalam LA dan  merupakan konsentrasi kalium ferisianat dalam x satuan mM. 200 — Channel1 — Channel2 150 = x = 5 100 5 O a 50 ) 0 0 5 10 15 20 Concentration (mM) **Gambar IV.16** Hasil kurva kalibrasi DPV larutan K3[Fe(CN)6] Persamaan kurva regresi yang didapat adalah sebagai berikut. **Tabel IV.9** Persamaan kurva kalibrasi DPV larutan K3[Fe(CN)6] Data Arus Persamaan Regresi Nilai R[2 ] Arus puncak kanal 1 0.9905 Arus puncak kanal 2 0.9932 

Nilai R[2] mendekati 1 menunjukkan linearitas yang baik untuk konsentrasi 2.5 sampai dengan 20 mM. Adapun konsentrasi minimum dan maksimum yang dapat terukur juga dapat dihitung dengan cara yang sama dengan sebelumnya. 

76 

**Tabel IV.10** Rentang konsentrasi terukur larutan K3[Fe(CN)6] metode DPV 

|Data kanal|Konsentrasi|Konsentrasi|
|---|---|---|
||maksimum|minimum|
|Kanal 1|634.4 mM|0.73 mM|
|Kanal 2|707.9 mM|0.23 mM|



Dari data pada tabel konsentrasi rentang linear, dapat disimpulkan bahwa pengukuran DPV pada potensiostat ini memiliki rentang linear dari 0.73 mM sampai 707.9 mM. 

mM sampai 707.9 mM. 4. Hasil Pengukuran Metode _Chronoamperometry_ (CA) Pengukuran CA telah dilakukan untuk lima variasi konsentrasi larutan kalium ferisianat (2.5, 5, 10, 15, dan 20 mM) dalam pelarut PBS 0.1 M. Pada pengukuran CA, diberikan tegangan yang konstan sebesar 50 mV pada analit selama dua menit, kemudian diamati kuat arus yang mengalir pada analit seiring berjalannya waktu. Arus yang dijadikan data acuan adalah arus pada akhir interval dua menit, ketika nilainya sudah relatif stabil. Plot arus terhadap waktu pada analit untuk kedua kanal disajikan pada gambar berikut. 

77 

**==> picture [370 x 372] intentionally omitted <==**

**----- Start of picture text -----**<br>
10<br>0<br>0 25 50 1 100 125<br>Time (s)<br>Gambar IV.17  Hasil pengujian CA larutan K3[Fe(CN)6] pada Channel 1<br>40<br>— 5mM<br>10 mM<br>30 \ — 2015 mM<br>x<br>=<br>5 [20]<br>=<br>a3<br>(3)<br>10;<br>0<br>0 25 50 75 100 125<br>Time (s)<br>Dokumen Asli<br>**----- End of picture text -----**<br>


**Gambar IV.18** Hasil pengujian CA larutan K3[Fe(CN)6] pada Channel 2 

Dari hasil arus yang didapat, bisa dilihat bahwa arus setelah interval 120 detik meningkat untuk konsentrasi yang semakin besar. Bentuk profil arus yang didapat juga sudah sesuai dengan referensi, yaitu arus yang nilainya menurun seiring berjalannya waktu sampai konvergen ke suatu nilai 

78 

tertentu. Data ini dirangkum dalam tabel berikut, sekaligus dengan perbandingannya dengan arus referensi pada potensiostat PalmSens4. 

**Tabel IV.11** Data arus _steady-state_ CA larutan K3[Fe(CN)6] 

|Dokumen Asli<br>Konsentrasi<br>(mM)<br>Arus puncak (�A)<br>Arus<br>referensi<br>(�A)<br>Galat (%)<br>Channel<br>1<br>Channel 2<br>Channel<br>1<br>Channel 2<br>2.5<br>2.72<br>2.22<br>2.02<br>34.94<br>10.23<br>5<br>4.91<br>4.22<br>3.95<br>24.34<br>6.82<br>10<br>9.16<br>8.70<br>8.55<br>7.05<br>1.70<br>15<br>14.19<br>13.78<br>12.59<br>12.72<br>9.48<br>20<br>19.40<br>18.55<br>19.16<br>1.25<br>3.19<br>Akurasi relatif dari data yang diperoleh adalah 88.65% dengan rata-rata<br>galat absolut sebesar 0.65��. Besarnya arus yang terukur secara umum<br>lebih kecil dibandingkan metode pengukuran lain, sehingga walaupun galat<br>absolutnya kecil, akurasi relatifnya tidak terjamin lebih baik. Selain itu,<br>didapat juga bahwa potensiostat ini memiliki persentase galat yang lebih<br>besar ketika mengukur arus pada satuan mikroampere, mengingat untuk<br>galat yang sama dan nilai yang referensi yang lebih kecil, maka persentase<br>akurasi menjadi lebih kecil. Adapun uji linearitas juga telah dilakukan<br>dengan membuat plot kurva kalibrasi untuk kelima variasi konsentrasi yang<br>telah diujikan.|Konsentrasi<br>(mM)|Arus puncak (�A)<br>Arus<br>referensi<br>(�A)<br>Channel<br>1<br>Channel 2|Galat (%)|
|---|---|---|---|
||||Channel<br>1<br>Channel 2|
||<br>2.5<br>5<br>10<br>15<br>20|Asli<br>2.72<br>2.22<br>2.02<br>34.94<br>10.23<br>4.91<br>4.22<br>3.95<br>24.34<br>6.82<br>9.16<br>8.70<br>8.55<br>7.05<br>1.70<br>14.19<br>13.78<br>12.59<br>12.72<br>9.48<br>19.40<br>18.55<br>19.16<br>1.25<br>3.19||



79 

|Doku en sli<br>**Gambar IV.19**Hasil kurva kalibrasi CA larutan K3[Fe(CN)6]<br>Dari kurva kalibrasi ini, diperoleh dua buah persamaan regresi linear dengan<br>variabel  adalah arus_steady-state_dari analit dalam<br>dan variabel<br>adalah konsentrasi analit dalam mM. Linearitas dari data ini dapat dikatakan<br>baik karena nilai R2yang didapat mendekati angka 1.<br>**Tabel IV.12**Persamaan kurva kalibrasi CA larutan K3[Fe(CN)6]<br>Data Arus<br>Persamaan Regresi<br>Nilai R2<br>Arus puncak kanal 1<br>0.9980<br>Arus puncak kanal 2<br>0.9989<br>**IV.3**<br>**Posisi Riset**<br>Perbandingan potensiostat hasil riset ini dengan potensiostat pada penelitian lain<br>dapat dilihat pada Tabel IV.x berikut.<br>0<br>0<br>5<br>10<br>15<br>20<br>Concentration (mM)<br>x|
|---|



**IV.3 Posisi Riset** Perbandingan potensiostat hasil riset ini dengan potensiostat pada penelitian lain dapat dilihat pada Tabel IV.x berikut. 

80 

||||||||||
|---|---|---|---|---|---|---|---|---|
|||<br>**Tabel IV.13**Persamaan kurva kalibrasi CA larutan K3[Fe(CN)6]|||||||
|Referensi|Harga|<br>_Interfacing_|<br>Mikrokontroler|<br>Range<br>Potensial|<br>Range<br>Arus|s<br>Resolusi<br>I/O|Metode<br>Pengukuran|Jumlah<br>Kanal|
|[23]|N/A|<br>Wi-Fi|<br>ARM Cortex-M4<br>dan CC3200|<br>-0.6 sampai<br>0.6 V|<br>N/A|<br>12-bit|DPV|1|
|[28]|45 USD|<br>N/A|<br>Arduino UNO|e<br>-3.3 sampai<br>3.3 V|<br>-13.75<br>sampai<br>13.75 mA|<br>ADC 16-<br>bit, DAC<br>10-bit|CV, LSV,<br>DPV, CA|1|
|[27]|15 USD|<br>N/A|u<br>Seeeduino XIAO|<br>-1.65<br>sampai 1.65<br>V|<br>N/A|<br>ADC 12-<br>bit, DAC<br>10-bit|CV, LSV,<br>DPV, CA|1|
|[26]|226.22<br>USD|<br>USB|ok<br>PIC16F1459|<br>-12 sampai<br>12 V|<br>-0.1 sampai<br>0.1 mA|<br>DAC 22-<br>bit, ADC<br>20-bit|CV|1|
|[25]|N/A|D<br>USB|<br>LMP91000, ARM<br>Cortex-M0 dan<br>SAMD21|<br>-0.35<br>sampai 1.4<br>V|<br>N/A|<br>10-bit|CV, SWV,<br>NPV, CA|1|



81 

**==> picture [9 x 305] intentionally omitted <==**

**----- Start of picture text -----**<br>
Koleksi digital milik UPT Perpustakaan ITB untuk keperluan pendidikan dan penelitian<br>**----- End of picture text -----**<br>


**==> picture [673 x 372] intentionally omitted <==**

**----- Start of picture text -----**<br>
DAC 12-<br>-1.5 sampai  -0.3 sampai<br>[24]  25.12 USD  Bluetooth  ESP32  bit, ADC 8- CV  1<br>1.5 V  0.3 mA<br>bit<br>-6.10  ADC 16-<br>-5 sampai 5  CV, DPV,<br>Tesis ini  82.8 USD  USB  STM32F4CE11U6  sampai  bit, DAC  2<br>V  LSV, CA<br>+6.10 mA  16-bit<br>Dokumen Asli<br>**----- End of picture text -----**<br>


82 

## **Bab V    Kesimpulan** 

## **V.1 Kesimpulan** 

Dari penelitian ini, dapat ditarik beberapa kesimpulan sebagai berikut. 

   1. Telah dirancang potensiostat multikanal dengan biaya satu prototipe sebesar Rp1.325.000 setiap prototipenya. Harga ini termasuk biaya-biaya yang bersifat nonteknis seperti pajak dan bea cukai serta biaya pengiriman, sehingga harga produksi bersih dari satu prototipe lebih rendah dari angka ini. 

- ini. 

- 2. Potensiostat yang dirancang berhasil diimplementasiken menggunakan komponen diskrit berupa op-amp, multiplexer, mikrokontroler berbasis STM32, resistor, dan kapasitor. Subsistem perangkat keras yang ada pada potensiostat ini mencakup penggeser tegangan, antarmuka sel elektrokimia, penguat transimpedansi, penggeser tegangan output, filter analog SallenKey, dan filter antialiasing untuk menghilangkan komponen sinyal berfrekuensi tinggi. 

- 3. Potensiostat yang dirancang dalam penelitian ini mampu melakukan pengukuran voltametri berupa _Cyclic Voltammetry_ (CV), _Voltammetry_ (DPV), _Linear Sweep Voltammetry_ amperometri yaitu _Chronoamperometry_ (CA). 

- 4. Subsistem perangkat lunak yang terlibat dalam potensiostat ini adalah fungsi mengeluarkan tegangan untuk teknik CV, DPV, LSV, dan CA, serta fungsi untuk menghitung arus yang mengalir pada analit berdasarkan nilai tegangan yang terbaca pada ADC. 

- 5. Pengujian potensiostat ini dilakukan dengan membandingkan hasil pengujian karakteristik elektrokimia larutan kalium 

   2. Potensiostat yang dirancang berhasil diimplementasiken menggunakan 

      - komponen diskrit berupa op-amp, multiplexer, mikrokontroler berbasis STM32, resistor, dan kapasitor. Subsistem perangkat keras yang ada pada potensiostat ini mencakup penggeser tegangan, antarmuka sel elektrokimia, penguat transimpedansi, penggeser tegangan output, filter analog SallenKey, dan filter antialiasing untuk menghilangkan komponen sinyal berfrekuensi tinggi. 

   3. Potensiostat yang dirancang dalam penelitian ini mampu melakukan pengukuran voltametri berupa _Cyclic Voltammetry_ (CV), _Differential Pulse Voltammetry_ (DPV), _Linear Sweep Voltammetry_ (LSV), serta pengukuran amperometri yaitu _Chronoamperometry_ (CA). 

   4. Subsistem perangkat lunak yang terlibat dalam potensiostat ini adalah fungsi mengeluarkan tegangan untuk teknik CV, DPV, LSV, dan CA, serta fungsi untuk menghitung arus yang mengalir pada analit berdasarkan nilai tegangan yang terbaca pada ADC. 

   5. Pengujian potensiostat ini dilakukan dengan membandingkan hasil pengujian karakteristik elektrokimia larutan kalium ferisianat (K3[Fe(CN)6]) dengan variasi konsentrasi 2.5, 5, 10, 15, dan 20 mM dalam pelarut _Phosphate-buffered Saline_ (PBS) 0.1 M dengan _Screen Printed Carbon Electrode_ (SPCE) yang diproduksi oleh Zimmer-Peacock menggunakan potensiostat komersil yaitu PalmSens4. 

   6. Metode pengujian dilakukan dengan melakukan masing-masing pengukuran (CV, DPV, LSV, dan CA) sebanyak tiga kali (triplo). 

83 

7. Pengukuran CV pada potensiostat ini dilakukan dengan rentang tegangan �1V dan menghasilkan akurasi relatif sebesar 95.57% dan galat mutlak 1.51��, dan terbentuk arus listrik yang linear dengan konsentrasi larutan kalium ferisianat untuk konsentrasi 2.5 sampai 20 mM. 

   8. Pengukuran LSV pada potensiostat ini dilakukan dengan rentang tegangan -0.6V sampai 0.3V dan menghasilkan akurasi relatif sebesar 88.64% dan galat mutlak 2.24��, dan terbentuk arus listrik yang linear dengan 

   - konsentrasi larutan kalium ferisianat untuk konsentrasi 2.5 sampai 20 mM. 

   - 9. Pengukuran DPV pada potensiostat ini dilakukan dengan rentang tegangan -0.6V sampai 0.3V dan menghasilkan akurasi relatif sebesar 90.25% dan galat mutlak 6.20��, dan terbentuk arus listrik yang linear dengan ��, dan terbentuk arus listrik yang linear dengan , dan terbentuk arus listrik yang linear dengan konsentrasi larutan kalium ferisianat untuk konsentrasi 2.5 sampai 20 mM. 

   - 10. Pengukuran CA pada potensiostat ini dilakukan dengan tegangan konstan 0.05 V dan menghasilkan akurasi relatif sebesar 88.65% dan galat mutlak 

9. Pengukuran DPV pada potensiostat ini dilakukan dengan rentang tegangan -0.6V sampai 0.3V dan menghasilkan akurasi relatif sebesar 90.25% dan galat mutlak 6.20��, dan terbentuk arus listrik yang linear dengan ��, dan terbentuk arus listrik yang linear dengan , dan terbentuk arus listrik yang linear dengan konsentrasi larutan kalium ferisianat untuk konsentrasi 2.5 sampai 20 mM. 

10. Pengukuran CA pada potensiostat ini dilakukan dengan tegangan konstan 0.05 V dan menghasilkan akurasi relatif sebesar 88.65% dan galat mutlak 0.65��, dan terbentuk arus listrik ��, dan terbentuk arus listrik , dan terbentuk arus listrik _steady-state_ konsentrasi larutan kalium ferisianat untuk konsentrasi 2.5 sampai 20 mM. 

11. Potensiostat yang dirancang pada penelitian ini diberi nama GaneStat v2 yang memiliki spesifikassi: � Akurasi relatif lebih dari 85%. � Resolusi tegangan 76.29 �� � Resolusi arus terkecil 0.16 nA � Rentang tegangan _sweep_ -5V sampai 5V � Rentang arus yang dapat diukur -3.05mA sampai 3.05mA � Metode pengukuran yang dapat dilakukan mencakup CV, DPV, LSV, dan CA. 

   - 0.65��, dan terbentuk arus listrik ��, dan terbentuk arus listrik , dan terbentuk arus listrik _steady-state_ yang linear dengan konsentrasi larutan kalium ferisianat untuk konsentrasi 2.5 sampai 20 mM. 

   - 11. Potensiostat yang dirancang pada penelitian ini diberi nama GaneStat v2 yang memiliki spesifikassi: � Akurasi relatif lebih dari 85%. 

      - Metode pengukuran yang dapat dilakukan mencakup CV, DPV, LSV, dan CA. 

      - Jumlah kanal yang dapat digunakan sejumlah 2. 

## **V.2 Saran** 

Beberapa saran yang dapat diimplementasikan untuk pengembangan berikutnya dari penelitian ini antara lain: 

84 

   1. Pengujian potensiostat ini untuk mendeteksi keberadaan analit biologis dengan cara memodifikasi elektroda/SPCE yang digunakan supaya lebih sensitif terhadap analit biologis. 

   2. Pembuatan _Graphical User Interface_ (GUI) untuk lebih memudahkan pengguna menggunakan potensiostat ini apabila hendak diproduksi secara komersial, dan membuat devais ini tidak bergantung pada PC pengguna sehingga memiliki portabilitas yang lebih baik. 

   3. Eksplorasi spesifikasi dari mikrokontroler STM32 dengan lebih dalam 

- dengan cara penggunaan 1 _core_ saja untuk mengolah data seluruh channel secara bergiliran ( _multiplexing_ ), sehingga pengembangan perangkat keras bisa lebih _low-cost_ , serta penggunaan filter digital untuk menghilangkan noise untuk menghemat jumlah komponen yang diperlukan. Selain itu, hal ini juga mampu memungkinkan perancangan potensiostat dengan jumlah kanal yang lebih banyak. 

dengan cara penggunaan 1 _core_ saja untuk mengolah data seluruh channel secara bergiliran ( _multiplexing_ ), sehingga pengembangan perangkat keras bisa lebih _low-cost_ , serta penggunaan filter digital untuk menghilangkan noise untuk menghemat jumlah komponen yang diperlukan. Selain itu, hal ini juga mampu memungkinkan perancangan potensiostat dengan jumlah kanal yang lebih banyak. 

85 

## **DAFTAR PUSTAKA** 

- [1] Wan, J., Ai, J., Zhang, Y. et al. Signal-off impedimetric immunosensor for the detection of Escherichia coli O157:H7. Sci Rep 6, 19806 (2016). https://doi.org/10.1038/srep19806 

- [2] Obeidat, Y., Rawashdeh, A.M., Hammoudeh, A. et al. Acetone sensing in liquid and gas phases using cyclic voltammetry. Sci Rep 12, 11010 (2022). https://doi.org/10.1038/s41598-022-15135-4 

- [3] Baranowska, I., Markowski, P., Gerle, A., Baranowski, J. Determination of selected drugs in human urine by differential pulse voltammetry technique. Bioelechem (2008). https://doi.org/10.1016/j.bioelechem.2008.04.022 

- [4] Allison V. Cordova-Huaman, Victor R. Jauja-Ccana, Adolfo La RosaToro, Low-cost smartphone-controlled potentiostat based on Arduino for teaching electrochemistry fundamentals and applications, Heliyon, Volume 7, Issue 2, 2021, https://doi.org/10.1016/j.heliyon.2021.e06259. 

- [5] P. Irving, R. Cecil, M.Z. Yates, MYSTAT: A compact potentiostat/galvanostat for general electrochemistry measurements, HardwareX, Volume 9, 2021, https://doi.org/10.1016/j.ohx.2020.e00163 

- [6] I. Anshori et al., "ESPotensio: A Low-Cost and Portable Potentiostat With Multi-Channel and Multi-Analysis Electrochemical Measurements," in IEEE Access, vol. 10, pp. 112578-112593, 2022, doi: 10.1109/ACCESS.2022.3213725. 

- [7] Bhalla N, Jolly P, Formisano N, Estrela P. Introduction to biosensors. Essays Biochem. 2016 Jun 30;60(1):1-8. doi: 10.1042/EBC20150001. PMID: 27365030; PMCID: PMC4986445. 

- [8] Raditya, A. N. Biofouling of indwelling electrochemical sensors. PhD Thesis. 2020 Imperial College London. 

- [9] Liu, J.; Xu, Y.; Liu, S.; Yu, S.; Yu, Z.; Low, S.S. Application and Progress of Chemometrics in Voltammetric Biosensing. Biosensors 2022, 12, 494. https://doi.org/10.3390/bios12070494 

- [10] B. Jill Venton, Dana J. DiScenza, Chapter 3 - Voltammetry, Editor(s): Bhavik Patel, Electrochemistry for Bioanalysis, Elsevier, 2020, Pages 27-50, ISBN 9780128212035, https://doi.org/10.1016/B978-0-12821203-5.00004-X. 

- [11] Aoki, K., Tokuda, K. and Matsuda, H., 1984. Theory of differential pulse voltammetry at stationary planar electrodes. Journal of electroanalytical 

- [11] Aoki, K., Tokuda, K. and Matsuda, H., 1984. Theory of differential pulse voltammetry at stationary planar electrodes. Journal of electroanalytical chemistry and interfacial electrochemistry. 

- [12] Irena Baranowska, Piotr Markowski, Anna Gerle, Jacek Baranowski, Determination of selected drugs in human urine by differential pulse voltammetry technique, Bioelectrochemistry, Volume 73, Issue 1, 2008, p5-10, ISSN 1567-5394, https://doi.org/10.1016/j.bioelechem.2008.04.022. 

- [13] A. J. Bard and L. Faulkner, Electrochemical Methods: Fundamentals and Applications, John Wiley & son, 2nd edn., 2001. 

- [14] H. Matsuda, Y. Ayabe, Z. Elektrochem., 1955, 59, 494-503. 

- [15] S. D. Adams, E. H. Doeven, K. Quayle and A. Z. Kouzani, "MiniStat: Development and Evaluation of a Mini-Potentiostat for Electrochemical 

86 

Measurements," in IEEE Access, vol. 7, pp. 31903-31912, 2019, doi: 10.1109/ACCESS.2019.2902575 

- [16] A. K. P. Souza, C. A. de Moraes Cruz, G. C. Marques, L. S. O. de Castro and T. B. Bezerra, "A Compact Current Conveyor CMOS Potentiostat Circuit for Electrochemical Sensors," 2019 4th International Symposium on Instrumentation Systems, Circuits and Transducers (INSCIT), Sao Paulo, Brazil, 2019, pp. 1-6, doi: 10.1109/INSCIT.2019.8868731. 

- [17] P. Konieczka, 2.31 - Validation and Regulatory Issues for Sample Preparation, Editor(s): Janusz Pawliszyn, Comprehensive Sampling and Sample Preparation, Academic Press, 2012, Pages 699-711, https://doi.org/10.1016/B978-0-12-381373-2.00064-8. 

- [18] Sevinc Kurbanoglu, Bengi Uslu, Sibel A. Ozkan, Chapter 28 - Carbonbased nanostructures for electrochemical analysis of oral medicines, Editor(s): Ecaterina Andronescu, Alexandru Mihai Grumezescu, In Micro and Nano Technologies, Nanostructures for Oral Medicine, Elsevier, 2017, Pages 885-938. 

- [19] Pine Research. _What is a potentiostat and how does it work?_ - 

- https://pineresearch.com/shop/kb/theory/instrumentation/what potentiostat-does/ diakses 29 Juli 2024 pukul 14:29 WIB. 

- [20] Wikipedia. _Cyclic Voltammetry._ https://en.wikipedia.org/wiki/Cyclic_voltammetry#/media/File:For_wik ipedia_2_with_white_background.svg diakses 15 Juli 2024 pukul 20.58 WIB. 

- [21] Weng, Yee & Rashidah, Azleen & Yusoff, Farhanini. (2019). Magnetite Graphene for Electrochemical Determination of Uric Acid. Malaysian Journal of Analytical Sciences. 23. 407-422. 10.17576/mjas-2019-230305. 

- [22] Ramanujam, Ashwin & Almodovar, Sharilyn & Botte, Gerardine. (2021). Ultra-Fast Electrochemical Sensor for Point-of-Care COVID-19 Diagnosis Using Non-Invasive Saliva Sampling. Processes. 9. 1236. 10.3390/pr9071236. 

- [23] V. Bianchi, A. Boni, M. Bassoli, M. Giannetto, S. Fortunati, M. Careri, I. De Munari, IoT and Biosensors: A Smart Portable Potentiostat With Advanced Cloud-Enabled Features, IEEE Access. 9 (2021) 

- [24] Anshori, I., Mufiddin, G.F., Ramadhan, I.F., Ariasena, E., Harimurti, S., Yunkins, H. and Kurniawan, C., 2022. Design of smartphone-controlled low-cost potentiostat for cyclic voltammetry analysis based on ESP32 microcontroller. Sensing and Bio-Sensing Research, 

- [22] Ramanujam, Ashwin & Almodovar, Sharilyn & Botte, Gerardine. (2021). Ultra-Fast Electrochemical Sensor for Point-of-Care COVID-19 Diagnosis Using Non-Invasive Saliva Sampling. Processes. 9. 1236. 10.3390/pr9071236. 

- [23] V. Bianchi, A. Boni, M. Bassoli, M. Giannetto, S. Fortunati, M. Careri, I. De Munari, IoT and Biosensors: A Smart Portable Potentiostat With Advanced Cloud-Enabled Features, IEEE Access. 9 (2021) 

- [24] Anshori, I., Mufiddin, G.F., Ramadhan, I.F., Ariasena, E., Harimurti, S., Yunkins, H. and Kurniawan, C., 2022. Design of smartphone-controlled low-cost potentiostat for cyclic voltammetry analysis based on ESP32 microcontroller. Sensing and Bio-Sensing Research, 

- [25] O.S. Hoilett, J.F. Walker, B.M. Balash, N.J. Jaras, S. Boppana, J.C. Linnes, KickStat: A coin-sized potentiostat for high-resolution electrochemical analysis, Sensors. 20 (2020) 

- [26] Irving, P., Cecil, R. and Yates, M.Z., 2021. MYSTAT: A compact potentiostat/galvanostat for general electrochemistry measurements. HardwareX, 9, p.e00163. 

- [27] I. Vamos and V. Kertesz, “Hunstat–a simple and low-cost potentiostat for analytical and educational purposes,” Analytical Methods, 2024. 

- [28] Tichter, Tim and Gernhard, Marius and Vesborg, Peter, Polarstat: An Arduino Based Potentiostat for Low-Power Electrochemical 

87 

Applications. Available at SSRN: https://ssrn.com/abstract=4341560 or http://dx.doi.org/10.2139/s srn.4341560 

88 

## **LAMPIRA�** 

## **Lampiran A: Prosedur Aktivasi Elektroda Karbon (SPCE)** 

Aktivasi SPCE diperlukan untuk mengondisikan SPCE supaya siap digunakan dalam uji elektrokimia yang hendak dilakukan. Telah dilakukan prosedur aktivasi sebagai berikut. 

   1. Disiapkan SPCE sejumlah yang dibutuhkan. 

   2. SPCE dihubungkan pada potensiostat PalmSens4. 

3. Diteteskan larutan asam sulfat (H2SO4) konsentrasi 0.5 M ke atas SPCE 2SO4) konsentrasi 0.5 M ke atas SPCE SO4) konsentrasi 0.5 M ke atas SPCE 4) konsentrasi 0.5 M ke atas SPCE ) konsentrasi 0.5 M ke atas SPCE sampai elektroda WE, RE, dan CE tertutup oleh larutan. 

4. Dilakukan _Cyclic Voltammetry_ (CV) pada larutan H2SO42SO4SO44 dengan rentang tegangan 0.9 V sampai 1.5 V dan _scan rate_ 0.1 V/s sebanyak tiga siklus. 

5. Dilakukan pembersihan SPCE dengan membilas menggunakan akuades dan dilakukan pengeringan dengan menggunakan balon peniup ( _blower_ ). 

   3. Diteteskan larutan asam sulfat (H2SO4) konsentrasi 0.5 M ke atas SPCE 2SO4) konsentrasi 0.5 M ke atas SPCE SO4) konsentrasi 0.5 M ke atas SPCE 4) konsentrasi 0.5 M ke atas SPCE ) konsentrasi 0.5 M ke atas SPCE 

   - tegangan 0.9 V sampai 1.5 V dan _scan rate_ 0.1 V/s sebanyak tiga siklus. 

   - 5. Dilakukan pembersihan SPCE dengan membilas menggunakan akuades dan 

sampai elektroda WE, RE, dan CE tertutup oleh larutan. 4. Dilakukan _Cyclic Voltammetry_ (CV) pada larutan H2SO42SO4SO44 dengan rentang 

89 

