%============================================================
% TEMPLATE LAPORAN KEMAJUAN PKM-KC 2026
% Sesuai Panduan Belmawa Kemdiktisaintek
%============================================================

\documentclass[12pt, a4paper]{article}

%------------------------------------------------------------
% PACKAGE
%------------------------------------------------------------
\usepackage[
  top=2cm,
  bottom=2cm,
  left=3cm,
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
% FORMAT BAB — sesuai template DOCX
% Contoh: "BAB 1. PENDAHULUAN" rata kiri, bold
%------------------------------------------------------------
\titleformat{\section}
  {\normalfont\fontsize{12}{14}\bfseries\centering}
  {BAB \thesection.}
  {0.5em}
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
% CAPTION — "Tabel X.X" / "Gambar X.X" di atas/bawah
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
% DAFTAR ISI — format mirip DOCX
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

% Tambahkan "BAB" di depan nomor section di ToC
\renewcommand{\cftsecpresnum}{BAB }
\renewcommand{\cftsecaftersnum}{.}
\setlength{\cftsecnumwidth}{2.2cm}

%------------------------------------------------------------
% BIBLIOGRAFI HARVARD
%------------------------------------------------------------
\setlength{\bibhang}{1.25cm}
\setlength{\bibitemsep}{0pt}
\renewcommand*{\bibfont}{\normalsize\setstretch{1.15}}

%============================================================
% DOKUMEN MULAI
%============================================================
\begin{document}

%------------------------------------------------------------
% BAGIAN AWAL
% Penomoran romawi kecil, sudut KANAN BAWAH
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
% Hapus bagian ini jika tidak ada gambar
\listoffigures
\addcontentsline{toc}{section}{DAFTAR GAMBAR}
\newpage

%--- DAFTAR TABEL ---%
% Hapus bagian ini jika tidak ada tabel
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
% Penomoran angka arab, sudut KANAN ATAS
% Dimulai dari halaman 1
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

Pada sub bab ini dijelaskan mengenai masalah yang membangkitkan inspirasi 
untuk diwujudkan dalam bentuk prototipe. Tekankan urgensi dari masalah yang 
akan diselesaikan. Sumber inspirasi bisa berasal dari kehidupan sehari-hari 
maupun masalah industri yang faktual dan perlu diatasi.

Jelaskan secara singkat kondisi eksisting dan kesenjangan yang mendorong 
lahirnya ide PKM-KC ini. Sertakan data atau fakta pendukung yang relevan 
untuk memperkuat urgensi permasalahan \parencite{contoh2023}.

\subsection{Gagasan Karsa Cipta}

Jelaskan gagasan yang diajukan pada bagian ini. Gagasan harus terlihat 
jelas hubungannya dengan latar belakang dan mengandung kebaharuan yang 
menampakkan karsa yang unik, original, serta manfaatnya jika diwujudkan.

Jika dasar inspirasi adalah hasil riset orang lain, nyatakan nama 
pelaksana dan institusi tim riset serta hasilnya yang akan dikonstruksikan 
dalam PKM-KC. Ungkapkan juga fase final yang akan dicapai.

\subsection{Kemutakhiran Iptek yang Diadopsi}

Berisi penjelasan kemutakhiran Iptek karsa cipta dan perbedaannya dengan 
produk/Iptek sejenis yang telah ada. Semakin mutakhir teknologi yang 
digunakan dan terbedakan dengan yang sudah ada akan semakin baik.

\subsection{Luaran PKM Karsa Cipta}

Luaran Program PKM-KC yang akan dihasilkan berupa:
\begin{enumerate}[leftmargin=1.75cm, label=\arabic{*}.]
  \item Laporan kemajuan
  \item Laporan akhir
  \item Prototipe [sebutkan nama prototipe secara spesifik]
  \item Akun media sosial
\end{enumerate}

\subsection{Kesesuaian Kegiatan dengan Tema PKM}

Kegiatan PKM-KC dengan judul \textit{``[Judul PKM-KC]''} sesuai dengan 
Tema PKM 2026, yaitu [sebutkan salah satu tema PKM 2026].

%============================================================
% BAB 2. TARGET LUARAN
%============================================================
\section{TARGET LUARAN}

Bab ini menguraikan capaian target luaran dari prototipe yang sudah 
dikerjakan. Berikut rekapitulasi capaian target luaran PKM-KC hingga 
saat penyusunan laporan kemajuan ini.

\begin{table}[h!]
  \centering
  \caption{Capaian Target Luaran PKM-KC}
  \label{tab:luaran}
  \begin{tabular}{|c|p{5.5cm}|p{3cm}|c|}
    \hline
    \textbf{No} & \textbf{Jenis Luaran} & \textbf{Target} & \textbf{Capaian (\%)} \\
    \hline
    1 & Prototipe [nama prototipe] & Prototipe fungsional & 70\% \\
    \hline
    2 & Laporan kemajuan & Selesai & 100\% \\
    \hline
    3 & Akun media sosial aktif & Aktif & 100\% \\
    \hline
    4 & Video konsep prototipe & Draft video & 50\% \\
    \hline
  \end{tabular}
\end{table}

%============================================================
% BAB 3. TAHAP PELAKSANAAN
%============================================================
\section{TAHAP PELAKSANAAN}

\subsection{Alat dan Bahan}

\subsubsection{Alat yang Digunakan}

Berikut adalah alat-alat yang digunakan selama pelaksanaan PKM-KC:


\subsubsection{Bahan yang Digunakan}

Berikut adalah bahan-bahan yang digunakan selama pelaksanaan PKM-KC:


\subsection{Diagram Alir Pelaksanaan}

% Sisipkan gambar diagram alir di sini
% Contoh:
% \begin{figure}[h!]
%   \centering
%   \includegraphics[width=0.85\textwidth]{gambar/diagram_alir.png}
%   \caption{Diagram alir pelaksanaan PKM-KC}
%   \label{fig:diagram}
% \end{figure}

\noindent[Sisipkan diagram alir pelaksanaan di sini. Diagram alir harus 
diacu dan dijelaskan dalam teks.]

\subsection{Tahap 1: Identifikasi Masalah dan Desain Awal}

Uraikan proses identifikasi masalah dan penyusunan desain awal prototipe 
secara rinci. Jelaskan hasil observasi lapangan, studi literatur, dan 
diskusi tim yang menjadi landasan desain.

\subsection{Tahap 2: Konstruksi Prototipe}

Uraikan proses pembuatan/konstruksi prototipe secara rinci. Jelaskan 
langkah-langkah pembuatan, komponen yang digunakan, serta kendala yang 
dihadapi beserta solusinya.

\subsection{Tahap 3: Pengujian}

Uraikan metode pengujian yang digunakan, parameter yang diukur, serta 
hasil pengujian yang telah dilakukan. Pengujian dapat dilakukan secara 
langsung pada produk fisik maupun menggunakan \textit{software} pendukung.

%============================================================
% BAB 4. HASIL YANG DICAPAI
%============================================================
\section{HASIL YANG DICAPAI}

\subsection{Hasil Prototipe}

Uraikan hasil prototipe yang sudah dikerjakan hingga saat ini. Jelaskan 
spesifikasi, fungsi, dan cara kerja prototipe yang telah berhasil dibuat.

% Sisipkan gambar prototipe
% \begin{figure}[h!]
%   \centering
%   \includegraphics[width=0.75\textwidth]{gambar/prototipe.jpg}
%   \caption{Foto prototipe [nama prototipe] yang telah dikerjakan}
%   \label{fig:prototipe}
% \end{figure}

\subsection{Capaian Kegiatan}

Secara keseluruhan, target kegiatan PKM-KC ini telah tercapai sebesar 
\textbf{XX\%} dari total rencana kegiatan yang diusulkan. Rincian capaian 
dapat dilihat pada Tabel \ref{tab:luaran}. Uraikan faktor-faktor yang 
mendukung maupun menghambat ketercapaian target tersebut.

\subsection{Kesesuaian dengan Rencana Kegiatan}

Uraikan kesesuaian antara pelaksanaan yang telah dilakukan dengan rencana 
awal yang tertuang dalam proposal. Jelaskan apabila terdapat penyesuaian 
terhadap rencana semula beserta alasannya.

%============================================================
% BAB 5. POTENSI HASIL
%============================================================
\section{POTENSI HASIL}

\subsection{Potensi Publikasi Ilmiah}

Hasil PKM-KC ini berpotensi untuk dipublikasikan dalam bentuk artikel 
ilmiah pada jurnal atau konferensi yang relevan dengan bidang keilmuan 
prototipe yang dikembangkan. Target publikasi yang dituju antara lain:

\subsection{Peluang Kekayaan Intelektual}

Uraikan peluang perolehan Kekayaan Intelektual (KI) dari prototipe yang 
dikembangkan, seperti paten, hak cipta, atau bentuk KI lainnya. Jelaskan 
aspek kebaharuan (novelty) yang menjadi dasar klaim KI tersebut.

\subsection{Prediksi Manfaat bagi Masyarakat}

Uraikan prediksi manfaat sosial, ekonomi, dan/atau pendidikan dari 
prototipe ini bagi masyarakat luas jika berhasil diwujudkan secara 
penuh. Sertakan estimasi skala dampak yang dapat ditimbulkan.

%============================================================
% BAB 6. RENCANA TAHAPAN BERIKUTNYA
%============================================================
\section{RENCANA TAHAPAN BERIKUTNYA}

Berikut adalah rencana tahapan kegiatan yang akan dilaksanakan untuk 
mencapai target 100\% kegiatan PKM-KC hingga batas akhir pelaksanaan.

\begin{table}[h!]
  \centering
  \caption{Rencana Tahapan Kegiatan Berikutnya}
  \label{tab:rencana}
  \begin{tabular}{|c|p{5.5cm}|c|p{3cm}|}
    \hline
    \textbf{No} & \textbf{Jenis Kegiatan} & \textbf{Target Waktu} & \textbf{Penanggung Jawab} \\
    \hline
    1 & Penyempurnaan desain dan konstruksi prototipe & Bulan ke-3 & Ketua \\
    \hline
    2 & Pengujian akhir dan validasi prototipe & Bulan ke-3 & Anggota 1 \\
    \hline
    3 & Pembuatan video prototipe final & Bulan ke-4 & Anggota 2 \\
    \hline
    4 & Unggahan media sosial (ads ke-2 \& ke-3) & Bulan ke-3--4 & Anggota 3 \\
    \hline
    5 & Penyusunan dan pengumpulan laporan akhir & Bulan ke-4 & Seluruh tim \\
    \hline
  \end{tabular}
\end{table}

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
   & Suku cadang/microcontroller/sensor/kit & & & \\
  \hline
   & Bahan lainnya sesuai program PKM-KC & & & \\
  \hline
  \multicolumn{4}{|r|}{\textbf{SUB TOTAL}} & \textbf{Rp\quad0,00} \\
  \hline
  \multicolumn{5}{|l|}{\textbf{2. Belanja Sewa (maks. 15\%)}} \\
  \hline
   & Sewa gedung/alat & & & \\
  \hline
   & Sewa server/hosting/domain/SSL/akses jurnal & & & \\
  \hline
   & Sewa lab (termasuk penggunaan alat lab) & & & \\
  \hline
  \multicolumn{4}{|r|}{\textbf{SUB TOTAL}} & \textbf{Rp\quad0,00} \\
  \hline
  \multicolumn{5}{|l|}{\textbf{3. Perjalanan Lokal (maks. 30\%)}} \\
  \hline
   & Kegiatan penyiapan bahan & & & \\
  \hline
   & Kegiatan pendampingan & & & \\
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
   & Ads (iklan berbayar) akun media sosial \textit{maks} Rp 500.000 & & & \\
  \hline
  \multicolumn{4}{|r|}{\textbf{SUB TOTAL}} & \textbf{Rp\quad0,00} \\
  \hline
  \multicolumn{4}{|r|}{\textbf{GRAND TOTAL}} & \textbf{Rp\quad0,00} \\
  \hline
  \multicolumn{5}{|l|}{\textbf{GRAND TOTAL (Terbilang: \textit{[tuliskan terbilang]}\ )}} \\
  \hline
\end{longtable}

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
%   \caption{[Deskripsi kegiatan]}
%   \label{fig:dok1}
% \end{figure}

\noindent Sisipkan foto dokumentasi pelaksanaan kegiatan di sini.

\vspace{0.5cm}
\subsubsection*{B. Bukti Pengeluaran Dana}

\noindent Sisipkan foto/scan nota atau kuitansi pengeluaran di sini.

\vspace{0.5cm}
\subsubsection*{C. Screenshot Akun Media Sosial}

\noindent Sisipkan screenshot akun media sosial dan unggahan PKM 
(termasuk bukti \textit{ads} berbayar) di sini.

%============================================================
% SELESAI
%============================================================
\end{document}