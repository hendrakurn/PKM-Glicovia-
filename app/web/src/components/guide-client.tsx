"use client";

import { WarningCircle } from "@phosphor-icons/react";
import { GlicoBadge, GlicoPanel, PageHeader } from "@/components/glicovia-ui";

const prepSteps = [
  {
    title: "Persiapan sebelum pemeriksaan",
    items: [
      "Jangan makan atau minum selain air putih selama kurang lebih 2 jam sebelum pemeriksaan.",
      "Pastikan perangkat GLICOVIA dan seluruh komponen pendukung bersih dan siap digunakan.",
      "Pastikan cartridge tersedia dan sudah didisinfeksi sesuai petunjuk penggunaan.",
    ],
  },
  {
    title: "Pengambilan sampel saliva",
    items: [
      "Kumpulkan saliva segar memakai sendok stainless steel yang sudah disterilkan.",
      "Gunakan saliva yang terkumpul alami di rongga mulut (unstimulated saliva), bukan hasil berkumur.",
      "Siapkan 1 mL saliva untuk setiap cartridge.",
      "Segera gunakan sampel setelah diambil. Jangan simpan lebih dari 2 jam sebelum pemeriksaan.",
    ],
  },
  {
    title: "Penyimpanan perangkat dan komponen",
    items: [
      "Simpan perangkat GLICOVIA dan komponen pendukung pada suhu ruang 20–25°C.",
      "Hindari tempat dengan kelembapan tinggi.",
      "Pastikan perangkat dan cartridge kering serta terlindung dari cairan dan kontaminan.",
    ],
  },
];

const steps = [
  {
    title: "Menyalakan alat",
    items: [
      "Nyalakan alat. OLED menampilkan “Sistem Glicovia – Memulai…”, lalu “Siap. Mode siaga otomatis”.",
      "Pasang strip kering ke konektor dengan rapat. Pasang strip sebelum sampel diteteskan.",
      "OLED menampilkan “Siaga – Teteskan sampel”. Alat sedang membaca baseline, jangan teteskan sampel dulu.",
    ],
  },
  {
    title: "Meneteskan sampel saliva",
    items: [
      "Kumpulkan saliva secara alami di mulut.",
      "Teteskan saliva ke strip sampai ketiga elektroda tertutup rata.",
      "Setelah itu jangan sentuh atau geser alat dan strip.",
    ],
  },
  {
    title: "Proses otomatis",
    items: [
      "Alat mendeteksi sampel sendiri lewat lonjakan arus. Tidak perlu menekan tombol apa pun.",
      "Sampel terdeteksi → Tunggu stabil (10 detik): sinyal awal dibiarkan stabil.",
      "Mengambil sampel: alat membaca fruktosamin, glukosa saliva, dan pH. Jangan disentuh.",
      "Mengirim ke cloud → Menunggu prediksi: data dikirim lewat WiFi dan dihitung model AI.",
    ],
  },
  {
    title: "Membaca hasil",
    items: [
      "OLED menampilkan klasifikasi: NORMAL, PREDIABETES, DIABETES, atau UNCERTAIN. Hasil tertahan sekitar 60 detik, lalu alat kembali siaga.",
      "Web menampilkan estimasi glukosa (mg/dL), kategori, kelas klasifikasi, dan confidence di menu Readings dan Models.",
      "UNCERTAIN berarti model belum yakin. Ulangi dengan strip baru.",
    ],
  },
  {
    title: "Pengukuran berikutnya",
    items: [
      "Lepas dan buang strip lama, lalu pasang strip kering yang baru.",
      "Tunggu OLED kembali ke “Siaga”, lalu teteskan sampel.",
    ],
  },
];

const webSteps = [
  {
    title: "Login",
    items: [
      "Buka website Glicovia, lalu isi email dan password di tab Login.",
      "Belum punya akun? Pilih tab Register, isi data, lalu masuk.",
      "Klik “Enter dashboard”. Setelah berhasil, kamu langsung masuk ke Overview.",
    ],
  },
  {
    title: "Overview",
    items: [
      "Kartu utama menampilkan estimasi glukosa darah (mg/dL), kategori (NORMAL, PREDIABETES, DIABETES, atau UNCERTAIN), dan waktu pengukuran terakhir.",
      "Grafik tren menunjukkan perubahan estimasi glukosa. Atur perangkat, rentang tampilan, dan tanggal, lalu klik Apply.",
      "Freshness menunjukkan seberapa baru data terakhir, dan Data quality menunjukkan apakah data valid.",
      "Klik Refresh untuk memuat hasil pengukuran terbaru setelah tes selesai.",
    ],
  },
  {
    title: "Panduan",
    items: [
      "Buka menu Panduan di sidebar (atau di bar menu atas pada layar kecil).",
      "Halaman ini berisi langkah penggunaan alat dan website. Buka lagi kapan saja saat ragu.",
    ],
  },
];

function StepList({ steps, label }: { steps: Array<{ title: string; items: string[] }>; label: string }) {
  return (
    <div className="grid gap-5">
      {steps.map((step, index) => (
        <GlicoPanel key={step.title} className="p-5">
          <div className="space-y-3">
            <GlicoBadge tone="mint">{label} {index + 1}</GlicoBadge>
            <h2 className="text-xl font-black text-[color:var(--ink)]">{step.title}</h2>
            <ul className="list-disc space-y-2 pl-5 text-sm leading-6 text-[color:var(--ink-muted)]">
              {step.items.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </GlicoPanel>
      ))}
    </div>
  );
}

export function GuideClient() {
  return (
    <>
      <PageHeader eyebrow="Panduan" title="Penggunaan Alat Glicovia" description="Langkah pengambilan sampel saliva sampai hasil tampil di OLED dan dashboard." />

      <StepList steps={prepSteps} label="Tahap" />

      <PageHeader eyebrow="Alat" title="Langkah Pemeriksaan" description="Dari menyalakan alat sampai hasil tampil di OLED." />
      <StepList steps={steps} label="Langkah" />

      <PageHeader eyebrow="Website" title="Menggunakan Website" description="Cara masuk, membaca hasil, dan membuka panduan di dashboard Glicovia." />
      <StepList steps={webSteps} label="Menu" />

      <GlicoPanel className="flex gap-3 bg-[color:var(--butter)] p-5">
        <WarningCircle size={24} weight="bold" className="shrink-0" />
        <ul className="list-disc space-y-1 pl-4 text-sm font-bold leading-6 text-[color:var(--ink)]">
          <li>Glicovia adalah alat screening awal, bukan diagnosis. Hasilnya tidak menggantikan pemeriksaan darah atau dokter.</li>
          <li>Jika hasil PREDIABETES atau DIABETES, konfirmasi dengan tes gula darah di fasilitas kesehatan.</li>
          <li>Strip sekali pakai. Buang strip bekas ke tempat sampah tertutup.</li>
          <li>Batas penyimpanan saliva maksimal 2 jam, tetapi sebaiknya tetap gunakan saliva yang baru dikumpulkan.</li>
          <li>Versi prototipe: kalibrasi masih sementara, hasil bersifat perkiraan.</li>
        </ul>
      </GlicoPanel>
    </>
  );
}
