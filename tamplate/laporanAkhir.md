%============================================================
% TEMPLATE LAPORAN AKHIR PKM-KC 2026
% Disusun berdasarkan resource/GuideBookPKMKC.md
% Layout mengikuti gaya tamplate/laporanKemajuan.md
%============================================================

\documentclass[12pt, a4paper]{article}

%------------------------------------------------------------
% PACKAGE
%------------------------------------------------------------
\usepackage[
  top=3cm,
  bottom=3cm,
  left=4cm,
  right=3cm
]{geometry}

\usepackage{fontspec}
\setmainfont{Times New Roman}

\usepackage{setspace}
\setstretch{1.15}

\usepackage{ragged2e}
\justifying

\usepackage{titlesec}
\usepackage{tocloft}
\usepackage{fancyhdr}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{caption}
\usepackage{hyperref}
\usepackage{indentfirst}
\usepackage{parskip}
\usepackage{array}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{multirow}
\usepackage{tabularx}
\usepackage{makecell}
\usepackage{chngcntr}

\usepackage[
  backend=biber,
  style=authoryear,
  sorting=nyt,
  dashed=false
]{biblatex}
\addbibresource{daftarpustaka.bib}

%------------------------------------------------------------
% HYPERREF
%------------------------------------------------------------
\hypersetup{
  colorlinks=true,
  linkcolor=black,
  citecolor=black,
  urlcolor=black,
  hidelinks
}

%------------------------------------------------------------
% INDENT & PARAGRAPH
%------------------------------------------------------------
\setlength{\parindent}{1.25cm}
\setlength{\parskip}{6pt}

%------------------------------------------------------------
% FORMAT BAB
%------------------------------------------------------------
\titleformat{\section}
  {\normalfont\fontsize{12}{14}\bfseries\centering}
  {BAB \thesection.}
  {0.5em}
  {\MakeUppercase}
  []

\titleformat{name=\section,numberless}
  {\normalfont\fontsize{12}{14}\bfseries\centering}
  {}
  {0pt}
  {\MakeUppercase}
  []

\titleformat{\subsection}
  {\normalfont\fontsize{12}{14}\bfseries}
  {\thesubsection}
  {0.5em}
  {}

\titleformat{\subsubsection}
  {\normalfont\fontsize{12}{14}\bfseries}
  {\thesubsubsection}
  {0.5em}
  {}

\titlespacing{\section}{0pt}{40pt}{6pt}
\titlespacing{\subsection}{0pt}{12pt}{4pt}
\titlespacing{\subsubsection}{0pt}{10pt}{2pt}

%------------------------------------------------------------
% COUNTER
%------------------------------------------------------------
\renewcommand{\thesection}{\arabic{section}}
\renewcommand{\thesubsection}{\arabic{section}.\arabic{subsection}}
\renewcommand{\thesubsubsection}{\arabic{section}.\arabic{subsection}.\arabic{subsubsection}}

\counterwithin{figure}{section}
\counterwithin{table}{section}
\renewcommand{\thefigure}{\arabic{section}.\arabic{figure}}
\renewcommand{\thetable}{\arabic{section}.\arabic{table}}

%------------------------------------------------------------
% CAPTION
%------------------------------------------------------------
\captionsetup[figure]{
  labelfont=normalfont,
  textfont=normalfont,
  justification=centering,
  font={stretch=1.15},
  position=below
}
\captionsetup[table]{
  labelfont=normalfont,
  textfont=normalfont,
  justification=centering,
  font={stretch=1.15},
  position=above
}
\renewcommand{\figurename}{Gambar}
\renewcommand{\tablename}{Tabel}

%------------------------------------------------------------
% DAFTAR ISI
%------------------------------------------------------------
\renewcommand{\contentsname}{\centerline{DAFTAR ISI}}
\renewcommand{\listfigurename}{\centerline{DAFTAR GAMBAR}}
\renewcommand{\listtablename}{\centerline{DAFTAR TABEL}}

\renewcommand{\cftsecfont}{}
\renewcommand{\cftsecpagefont}{}
\renewcommand{\cftsecleader}{\cftdotfill{\cftdotsep}}
\renewcommand{\cftsubsecleader}{\cftdotfill{\cftdotsep}}

\setlength{\cftbeforesecskip}{4pt}
\setlength{\cftbeforesubsecskip}{1pt}
\setlength{\cftsecindent}{0pt}
\setlength{\cftsubsecindent}{1.25cm}

\renewcommand{\cftsecpresnum}{BAB }
\renewcommand{\cftsecaftersnum}{.}
\setlength{\cftsecnumwidth}{2.2cm}

%------------------------------------------------------------
% BIBLIOGRAFI
%------------------------------------------------------------
\setlength{\bibhang}{1.25cm}
\setlength{\bibitemsep}{0pt}
\renewcommand*{\bibfont}{\normalsize\setstretch{1.15}}

%============================================================
% DOKUMEN MULAI
%============================================================
\begin{document}

%------------------------------------------------------------
% RINGKASAN
% Tanpa nomor halaman
%------------------------------------------------------------
\pagestyle{empty}

\newpage

%------------------------------------------------------------
% BAGIAN AWAL
% Penomoran romawi kecil, sudut kanan bawah
%------------------------------------------------------------
\pagenumbering{roman}

\fancypagestyle{romanstyle}{
  \fancyhf{}
  \renewcommand{\headrulewidth}{0pt}
  \renewcommand{\footrulewidth}{0pt}
  \fancyfoot[R]{\fontsize{12}{14}\selectfont\thepage}
}
\pagestyle{romanstyle}

%--- DAFTAR ISI ---%
\setcounter{tocdepth}{2}
\tableofcontents
\newpage

%--- DAFTAR GAMBAR ---%
% Hapus bagian ini jika tidak ada gambar.
\listoffigures
\addcontentsline{toc}{section}{DAFTAR GAMBAR}
\newpage

%--- DAFTAR TABEL ---%
% Hapus bagian ini jika tidak ada tabel.
\listoftables
\addcontentsline{toc}{section}{DAFTAR TABEL}
\newpage

%--- DAFTAR LAMPIRAN ---%
\section*{\centerline{DAFTAR LAMPIRAN}}
\addcontentsline{toc}{section}{DAFTAR LAMPIRAN}

\vspace{0.5cm}
\noindent
\begin{tabular}{@{}lp{11cm}r@{}}
  Lampiran 1. & Penggunaan Dana & \pageref{lamp1} \\[4pt]
  Lampiran 2. & Bukti-Bukti Pendukung Kegiatan & \pageref{lamp2} \\[4pt]
\end{tabular}

\newpage

%------------------------------------------------------------
% BAGIAN INTI
% Penomoran arab, sudut kanan atas
%------------------------------------------------------------
\pagenumbering{arabic}
\setcounter{page}{1}

\fancypagestyle{arabicstyle}{
  \fancyhf{}
  \renewcommand{\headrulewidth}{0pt}
  \renewcommand{\footrulewidth}{0pt}
  \fancyhead[R]{\fontsize{12}{14}\selectfont\thepage}
}
\pagestyle{arabicstyle}

%============================================================
% BAB 1. PENDAHULUAN
%============================================================
\section{PENDAHULUAN}

\subsection{Latar Belakang}

Jelaskan sumber inspirasi dan tantangan intelektual yang melatarbelakangi
transformasi ide kreatif menjadi prototipe. Uraikan persoalan nyata yang
melandasi pengembangan, kondisi eksisting, serta alasan mengapa solusi yang
ditawarkan perlu diwujudkan.

\subsection{Sumber Inspirasi dan Keunikan Teknologi}

Jelaskan asal ide, hasil observasi, kebutuhan lapangan, atau hasil riset yang
menjadi pijakan kegiatan PKM-KC ini. Tegaskan keunikan teknologi yang telah
diterapkan dibandingkan pendekatan atau produk sejenis.

\subsection{Tujuan Pengembangan Prototipe}

Tuliskan tujuan umum dan tujuan khusus dari pengembangan prototipe secara
ringkas, terukur, dan selaras dengan luaran kegiatan.

%============================================================
% BAB 2. TINJAUAN PUSTAKA
%============================================================
\section{TINJAUAN PUSTAKA}

\subsection{Kajian Teori}

Uraikan teori, konsep, prinsip kerja, atau dasar ilmiah yang berkaitan langsung
dengan tantangan intelektual serta pengembangan prototipe. Gunakan referensi
yang relevan dan mutakhir untuk memperkuat argumentasi \parencite{contoh2023}.

\subsection{Produk atau Penelitian Sejenis}

Jelaskan produk, sistem, atau penelitian yang memiliki kedekatan dengan
prototipe yang dikembangkan. Paparkan persamaan, perbedaan, kekurangan, dan
celah pengembangan yang diisi oleh prototipe PKM-KC ini.

\subsection{Posisi Kebaruan Prototipe}

Rumusan pada subbab ini menegaskan letak kebaruan atau diferensiasi utama
prototipe, baik pada aspek desain, fitur, metode kerja, integrasi teknologi,
maupun manfaat bagi pengguna.

%============================================================
% BAB 3. TAHAP PELAKSANAAN
%============================================================
\section{TAHAP PELAKSANAAN}

\subsection{Tahapan Umum Pelaksanaan}

Uraikan prosedur konstruksi mulai dari munculnya inspirasi sampai dengan
tahapan mewujudkan prototipe. Penjelasan dapat dibagi menjadi identifikasi
masalah, perancangan, pembuatan, integrasi, pengujian, dan evaluasi.

\subsection{Alat dan Bahan}

\subsubsection{Alat}

Tuliskan alat utama yang digunakan selama proses perancangan, pembuatan, dan
pengujian prototipe.

\subsubsection{Bahan dan Komponen}

Tuliskan bahan, komponen, modul, perangkat lunak, atau material utama yang
digunakan dalam pengembangan prototipe.

\subsection{Diagram Alir atau Skema Pelaksanaan}

% Contoh penyisipan gambar:
% \begin{figure}[h!]
%   \centering
%   \includegraphics[width=0.85\textwidth]{gambar/diagram_alir.png}
%   \caption{Diagram alir tahapan pelaksanaan PKM-KC}
%   \label{fig:diagram-alir}
% \end{figure}

\noindent
[Sisipkan diagram alir, skema sistem, atau bagan tahapan pelaksanaan pada
bagian ini, lalu jelaskan keterkaitannya di dalam narasi.]

\subsection{Pelaksanaan Setiap Tahap}

Jelaskan secara rinci tiap tahap yang telah dilakukan, metode yang digunakan,
hasil antara yang diperoleh, serta kendala dan solusi pada masing-masing tahap.

%============================================================
% BAB 4. HASIL YANG DICAPAI DAN POTENSI KHUSUS
%============================================================
\section{HASIL YANG DICAPAI DAN POTENSI KHUSUS}

\subsection{Deskripsi Prototipe yang Dihasilkan}

Jelaskan prototipe yang berhasil dihasilkan, fungsi utamanya, spesifikasi pokok,
serta cara kerja sistem secara umum.

% Contoh penyisipan gambar:
% \begin{figure}[h!]
%   \centering
%   \includegraphics[width=0.75\textwidth]{gambar/prototipe.jpg}
%   \caption{Visualisasi prototipe yang dihasilkan}
%   \label{fig:prototipe}
% \end{figure}

\subsection{Capaian Hasil terhadap Target Kegiatan}

Paparkan kesesuaian jenis dan jumlah luaran yang telah dihasilkan, serta
persentase ketercapaian terhadap keseluruhan target kegiatan.

\begin{table}[h!]
  \centering
  \caption{Capaian Hasil terhadap Target Kegiatan}
  \label{tab:capaian}
  \begin{tabular}{|c|p{5.8cm}|p{3.2cm}|c|}
    \hline
    \textbf{No} & \textbf{Jenis Luaran} & \textbf{Target} & \textbf{Capaian (\%)} \\
    \hline
    1 & Prototipe [nama prototipe] & Prototipe siap uji/fungsional & 100\% \\
    \hline
    2 & Laporan akhir & Selesai & 100\% \\
    \hline
    3 & Akun media sosial aktif & Aktif dan terdokumentasi & 100\% \\
    \hline
    4 & Luaran tambahan [jika ada] & [isi target] & XX\% \\
    \hline
  \end{tabular}
\end{table}

\subsection{Keunggulan dan Potensi Khusus}

Jelaskan keunggulan prototipe dibandingkan solusi yang sudah ada, baik dari sisi
fungsi, efisiensi, keamanan, biaya, kemudahan penggunaan, maupun aspek teknis
lain yang relevan.

\subsection{Prediksi Kemanfaatan bagi Pengguna}

Uraikan potensi manfaat sosial, ekonomi, pendidikan, lingkungan, atau manfaat
praktis lainnya bagi pengguna atau pihak sasaran apabila prototipe digunakan
lebih lanjut.

\subsection{Peluang Pengembangan Lanjutan}

Paparkan potensi hasil dalam bentuk artikel ilmiah, peluang perolehan Kekayaan
Intelektual (KI), hilirisasi produk, kerja sama mitra, atau pengembangan menuju
tahap implementasi yang lebih luas.

%============================================================
% BAB 5. PENUTUP
%============================================================
\section{PENUTUP}

\subsection{Kesimpulan}

Tuliskan kesimpulan yang terkait langsung dengan proses pengembangan dan hasil
prototipe yang telah dicapai.

\subsection{Saran}

Tuliskan saran yang relevan untuk penyempurnaan prototipe, pengujian lanjutan,
atau implementasi pada tahap berikutnya.

%============================================================
% DAFTAR PUSTAKA
%============================================================
\newpage
\section*{DAFTAR PUSTAKA}
\addcontentsline{toc}{section}{DAFTAR PUSTAKA}

\printbibliography[heading=none]

%============================================================
% LAMPIRAN
%============================================================
\newpage
\section*{LAMPIRAN}
\addcontentsline{toc}{section}{LAMPIRAN}

%------------------------------------------------------------
% LAMPIRAN 1: PENGGUNAAN DANA
%------------------------------------------------------------
\subsection*{Lampiran 1. Penggunaan Dana}
\label{lamp1}
\addcontentsline{toc}{subsection}{Lampiran 1. Penggunaan Dana}

\begin{longtable}{|c|p{5.5cm}|c|r|r|}
  \hline
  \textbf{No} & \textbf{Jenis Pengeluaran} & \textbf{Volume} &
  \textbf{\makecell{Harga Satuan\\(Rp)}} & \textbf{Total (Rp)} \\
  \hline
  \endfirsthead
  \multicolumn{5}{l}{\textit{(Lanjutan Lampiran 1)}} \\[4pt]
  \hline
  \textbf{No} & \textbf{Jenis Pengeluaran} & \textbf{Volume} &
  \textbf{\makecell{Harga Satuan\\(Rp)}} & \textbf{Total (Rp)} \\
  \hline
  \endhead
  \hline
  \endlastfoot
  \multicolumn{5}{|l|}{\textbf{1. Belanja Bahan (maks. 60\%)}} \\
  \hline
   & Kabel/engsel/mur/baut dan sejenisnya & & & \\
  \hline
   & Bahan kimia lab/bahan logam/kayu dan sejenisnya & & & \\
  \hline
   & Suku cadang/\textit{microcontroller}/sensor/\textit{kit} & & & \\
  \hline
   & Bahan lainnya sesuai program PKM-KC & & & \\
  \hline
  \multicolumn{4}{|r|}{\textbf{SUB TOTAL}} & \textbf{Rp\quad0,00} \\
  \hline
  \multicolumn{5}{|l|}{\textbf{2. Belanja Sewa (maks. 15\%)}} \\
  \hline
   & Sewa gedung/alat & & & \\
  \hline
   & Sewa server/\textit{hosting}/domain/SSL/akses jurnal & & & \\
  \hline
   & Sewa laboratorium (termasuk penggunaan alat laboratorium) & & & \\
  \hline
  \multicolumn{4}{|r|}{\textbf{SUB TOTAL}} & \textbf{Rp\quad0,00} \\
  \hline
  \multicolumn{5}{|l|}{\textbf{3. Perjalanan Lokal (maks. 30\%)}} \\
  \hline
   & Kegiatan penyiapan bahan & & & \\
  \hline
   & Kegiatan pendampingan/pengujian lapangan & & & \\
  \hline
  \multicolumn{4}{|r|}{\textbf{SUB TOTAL}} & \textbf{Rp\quad0,00} \\
  \hline
  \multicolumn{5}{|l|}{\textbf{4. Lain-Lain (maks. 15\%)}} \\
  \hline
   & Jasa bengkel/uji coba & & & \\
  \hline
   & Percetakan produk & & & \\
  \hline
   & ATK lainnya & & & \\
  \hline
   & \textit{Ads} akun media sosial (maks. Rp500.000,00) & & & \\
  \hline
  \multicolumn{4}{|r|}{\textbf{SUB TOTAL}} & \textbf{Rp\quad0,00} \\
  \hline
  \multicolumn{4}{|r|}{\textbf{GRAND TOTAL}} & \textbf{Rp\quad0,00} \\
  \hline
  \multicolumn{5}{|l|}{\textbf{GRAND TOTAL (Terbilang: \textit{[tuliskan terbilang]})}} \\
  \hline
\end{longtable}

\noindent
Lampirkan juga bukti pengeluaran dana yang relevan setelah tabel rekapitulasi
jika diperlukan oleh format unggah institusi atau pembimbing.

%------------------------------------------------------------
% LAMPIRAN 2: BUKTI-BUKTI PENDUKUNG KEGIATAN
%------------------------------------------------------------
\newpage
\subsection*{Lampiran 2. Bukti-Bukti Pendukung Kegiatan}
\label{lamp2}
\addcontentsline{toc}{subsection}{Lampiran 2. Bukti-Bukti Pendukung Kegiatan}

\subsubsection*{A. Dokumentasi Pelaksanaan Kegiatan}

% \begin{figure}[h!]
%   \centering
%   \includegraphics[width=0.75\textwidth]{gambar/dokumentasi1.jpg}
%   \caption{Dokumentasi kegiatan [isi deskripsi]}
%   \label{fig:dokumentasi1}
% \end{figure}

\noindent
Sisipkan foto atau tangkapan layar dokumentasi kegiatan yang menunjukkan proses
perancangan, pembuatan, pengujian, diskusi tim, atau demonstrasi prototipe.

\vspace{0.5cm}
\subsubsection*{B. Bukti Pengeluaran Dana}

\noindent
Sisipkan foto atau hasil pindai nota, kuitansi, invoice, atau bukti transaksi
lain yang mendukung rincian penggunaan dana pada Lampiran 1.

\vspace{0.5cm}
\subsubsection*{C. Bukti Luaran dan Media Sosial}

\noindent
Sisipkan tangkapan layar akun media sosial, unggahan wajib PKM, bukti
\textit{ads} berbayar, atau bukti luaran tambahan lain yang relevan.

%============================================================
% SELESAI
%============================================================
\end{document}
