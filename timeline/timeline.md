# Timeline PKM 2026

## Informasi Umum
Timeline resmi Program Kreativitas Mahasiswa (PKM) Tahun 2026.

---

## Timeline Kegiatan

| No | Kegiatan | Waktu |
|---|---|---|
| 1 | Peluncuran Program | 9 Maret 2026 |
| 2 | Sosialisasi PKM | 12 Maret 2026 |
| 3 | PT melakukan seleksi internal | 9 Maret – 9 April 2026 |
| 4 | Akun operator PT mengunggah dokumen berita acara hasil evaluasi internal beserta lampiran identitas proposal dan surat komitmen dana tambahan PT pada Simbelmawa | 9 Maret – 9 April 2026, 23:59 WIB |
| 5 | Akun operator PT mendaftarkan judul proposal yang sesuai kriteria dan lolos evaluasi internal PT pada Simbelmawa | 9 Maret – 9 April 2026, 23:59 WIB |
| 6 | Akun mahasiswa mengunggah proposal, melengkapi biodata, dan memilih tema prioritas nasional pada Simbelmawa | 9 Maret – 9 April 2026, 23:59 WIB |
| 7 | Akun pimpinan PT dan akun dosen melakukan validasi proposal pada Simbelmawa | 9 Maret – 9 April 2026, 23:59 WIB |
| 8 | Penilaian proposal PKM skema pendanaan | April 2026 |
| 9 | Penilaian proposal PKM skema insentif | April 2026 |
| 10 | Pengumuman PKM skema pendanaan | 7 Mei 2026 |
| 11 | Pengumuman PKM skema insentif | 7 Mei 2026 |
| 12 | Pelaksanaan PKM skema pendanaan | 7 Mei – 11 September 2026 |
| 13 | Penilaian Kemajuan Pelaksanaan PKM (PKP2) skema pendanaan | 18–22 Agustus 2026 |
| 14 | Unggah Laporan Akhir PKM | 11–25 September 2026 |
| 15 | Pengumuman Peserta PIMNAS | 28 September 2026 |
| 16 | Pelaksanaan PIMNAS | 19–24 Oktober 2026 |

---

## Format Timeline untuk AI Agent

```yaml
timeline_pkm_2026:
  - id: 1
    kegiatan: "Peluncuran Program"
    waktu: "2026-03-09"

  - id: 2
    kegiatan: "Sosialisasi PKM"
    waktu: "2026-03-12"

  - id: 3
    kegiatan: "PT melakukan seleksi internal"
    mulai: "2026-03-09"
    selesai: "2026-04-09"

  - id: 4
    kegiatan: "Upload berita acara evaluasi internal dan surat komitmen dana tambahan"
    actor: "Operator PT"
    platform: "Simbelmawa"
    deadline: "2026-04-09 23:59 WIB"

  - id: 5
    kegiatan: "Pendaftaran judul proposal hasil evaluasi internal"
    actor: "Operator PT"
    platform: "Simbelmawa"
    deadline: "2026-04-09 23:59 WIB"

  - id: 6
    kegiatan: "Upload proposal dan melengkapi biodata"
    actor: "Mahasiswa"
    platform: "Simbelmawa"
    deadline: "2026-04-09 23:59 WIB"

  - id: 7
    kegiatan: "Validasi proposal"
    actor:
      - "Pimpinan PT"
      - "Dosen"
    platform: "Simbelmawa"
    deadline: "2026-04-09 23:59 WIB"

  - id: 8
    kegiatan: "Penilaian proposal PKM skema pendanaan"
    waktu: "2026-04"

  - id: 9
    kegiatan: "Penilaian proposal PKM skema insentif"
    waktu: "2026-04"

  - id: 10
    kegiatan: "Pengumuman PKM skema pendanaan"
    waktu: "2026-05-07"

  - id: 11
    kegiatan: "Pengumuman PKM skema insentif"
    waktu: "2026-05-07"

  - id: 12
    kegiatan: "Pelaksanaan PKM skema pendanaan"
    mulai: "2026-05-07"
    selesai: "2026-09-11"

  - id: 13
    kegiatan: "Penilaian Kemajuan Pelaksanaan PKM (PKP2)"
    mulai: "2026-08-18"
    selesai: "2026-08-22"

  - id: 14
    kegiatan: "Unggah Laporan Akhir PKM"
    mulai: "2026-09-11"
    selesai: "2026-09-25"

  - id: 15
    kegiatan: "Pengumuman Peserta PIMNAS"
    waktu: "2026-09-28"

  - id: 16
    kegiatan: "Pelaksanaan PIMNAS"
    mulai: "2026-10-19"
    selesai: "2026-10-24"