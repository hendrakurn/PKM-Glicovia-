"use client";

import { Printer } from "@phosphor-icons/react";
import { useSyncExternalStore } from "react";
import { createPortal } from "react-dom";
import type { PredictionResultRow, PredictionTrendRow, SensorReadingRow, SubjectDeviceRow } from "@/lib/api/types";
import { formatGlucose, formatPercentValue, formatTimestamp, toNumber } from "@/lib/utils";
import { GlicoButton } from "@/components/glicovia-ui";

const dateId = new Intl.DateTimeFormat("id-ID", { day: "numeric", month: "long", year: "numeric" });

const MEANING_ID: Array<[string[], string]> = [
  [["normal"], "Estimasi berada pada rentang yang diharapkan."],
  [["pre", "elevated"], "Estimasi perlu diperhatikan, terutama jika berulang pada pembacaan berikutnya."],
  [["high", "diabetes"], "Estimasi di atas rentang target. Pertimbangkan pemeriksaan ulang dan konsultasi sesuai arahan perawatan Anda."],
  [["low", "hypo"], "Estimasi tergolong rendah. Periksa ulang jika tidak sesuai dengan kondisi Anda."],
];

// Ambang sama dengan ml_classification/cls/dataset.py (label dari glukosa darah).
function categoryFromGlucose(value: unknown) {
  const n = toNumber(value);
  if (n === null) return null;
  return n < 100 ? "NORMAL" : n < 126 ? "PREDIABETES" : "DIABETES";
}

function meaningId(category: string | null | undefined) {
  const value = (category ?? "").toLowerCase();
  if (!value) return "Belum ada kategori model untuk pembacaan ini.";
  return MEANING_ID.find(([keys]) => keys.some((key) => value.includes(key)))?.[1] ?? "Baca kategori ini bersama kualitas data dan tingkat keyakinan model.";
}

const REPORT_CSS = `.print-report { display: none; }

@media print {
  @page { size: A4; margin: 16mm; }
  body > :not(.print-report) { display: none !important; }
  .print-report { display: block; width: 100%; color: #000; background: #fff; font-size: 11pt; line-height: 1.5; }
  .print-report section { break-inside: avoid; margin-top: 14pt; }
  .print-report h1 { font-size: 18pt; font-weight: 900; }
  .print-report h2 { font-size: 12pt; font-weight: 800; border-bottom: 1px solid #000; margin-bottom: 6pt; }
  .report-head { border-bottom: 2px solid #000; padding-bottom: 8pt; }
  .report-grid { display: grid; grid-template-columns: 11rem 1fr; gap: 2pt 8pt; }
  .report-grid dt { font-weight: 700; }
  .report-table { width: 100%; border-collapse: collapse; margin-top: 8pt; }
  .report-table th, .report-table td { border: 1px solid #000; padding: 3pt 6pt; text-align: left; }
  .report-foot { margin-top: 18pt; font-size: 9pt; border-top: 1px solid #000; padding-top: 6pt; }
}`;

export function ExportReportButton() {
  return (
    <GlicoButton type="button" variant="ink" onClick={() => window.print()}>
      <Printer size={18} weight="bold" />
      Ekspor PDF
    </GlicoButton>
  );
}

function TrendLine({ points }: { points: number[] }) {
  if (points.length < 2) return <p className="text-sm">Data tren belum cukup untuk grafik.</p>;
  const w = 640;
  const h = 160;
  const pad = 12;
  const min = Math.min(...points);
  const max = Math.max(...points);
  const span = max - min || 1;
  const coords = points.map((p, i) => `${pad + (i * (w - 2 * pad)) / (points.length - 1)},${h - pad - ((p - min) / span) * (h - 2 * pad)}`);
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full" role="img" aria-label={`Grafik tren glukosa, ${min.toFixed(0)} sampai ${max.toFixed(0)} mg/dL`}>
      <rect x="0" y="0" width={w} height={h} fill="none" stroke="#000" strokeWidth="1" />
      <polyline points={coords.join(" ")} fill="none" stroke="#000" strokeWidth="2" />
      {coords.map((c) => {
        const [x, y] = c.split(",");
        return <circle key={c} cx={x} cy={y} r="3" fill="#000" />;
      })}
    </svg>
  );
}

type ReportSheetProps = {
  subjectName: string;
  subjectCode: string;
  periodLabel: string;
  latest: SensorReadingRow | null;
  prediction: PredictionResultRow | null;
  classification: PredictionResultRow | null;
  trends: PredictionTrendRow[];
  devices: SubjectDeviceRow[];
};

export function ReportSheet({ subjectName, subjectCode, periodLabel, latest, prediction, classification, trends, devices }: ReportSheetProps) {
  const category = categoryFromGlucose(prediction?.glucose_estimate) ?? (classification?.inference_status === "success" ? classification.clinical_category : prediction?.clinical_category);
  const value = prediction?.glucose_estimate ?? latest?.salivary_glucose ?? null;
  const points = trends.map((row) => toNumber(row.glucose_estimate_avg)).filter((n): n is number => n !== null);

  // Portal ke <body> agar saat cetak seluruh layout aplikasi bisa display:none tanpa menyisakan halaman kosong.
  const mounted = useSyncExternalStore(() => () => {}, () => true, () => false);
  if (!mounted) return null;

  return createPortal(
    <article className="print-report" aria-hidden="true">
      <style>{REPORT_CSS}</style>
      <header className="report-head">
        <h1>Laporan Hasil Pemeriksaan GLICOVIA</h1>
        <p>Dicetak {dateId.format(new Date())} · Periode: {periodLabel}</p>
      </header>

      <section>
        <h2>Identitas Subjek</h2>
        <dl className="report-grid">
          <dt>Nama</dt><dd>{subjectName}</dd>
          <dt>Kode subjek</dt><dd>{subjectCode}</dd>
          <dt>Perangkat</dt><dd>{devices.length ? devices.map((d) => d.device_name || d.device_code).join(", ") : "Belum ada perangkat"}</dd>
        </dl>
      </section>

      <section>
        <h2>Pembacaan Terbaru</h2>
        <dl className="report-grid">
          <dt>Waktu</dt><dd>{formatTimestamp(prediction?.sensor_recorded_at ?? latest?.recorded_at)}</dd>
          <dt>{prediction?.glucose_estimate ? "Estimasi glukosa darah" : "Sinyal glukosa saliva"}</dt><dd>{formatGlucose(value)}</dd>
          <dt>Kategori</dt><dd>{category ?? "Belum tersedia"}</dd>
          <dt>Keyakinan model</dt><dd>{prediction?.confidence_score != null ? formatPercentValue(prediction.confidence_score) : "Tidak tersedia"}</dd>
          <dt>Kualitas data</dt><dd>{latest?.quality_flag ?? "Tidak tersedia"}</dd>
        </dl>
        <p>{meaningId(category)}</p>
      </section>

      <section>
        <h2>Tren Rata-rata Estimasi Glukosa</h2>
        <TrendLine points={points} />
        <table className="report-table">
          <thead>
            <tr><th>Periode</th><th>Jumlah</th><th>Rata-rata</th><th>Min</th><th>Maks</th></tr>
          </thead>
          <tbody>
            {trends.length === 0 ? (
              <tr><td colSpan={5}>Tidak ada data pada periode ini.</td></tr>
            ) : (
              trends.map((row) => (
                <tr key={row.bucket_start}>
                  <td>{dateId.format(new Date(row.bucket_start))}</td>
                  <td>{row.prediction_count}</td>
                  <td>{formatGlucose(row.glucose_estimate_avg)}</td>
                  <td>{formatGlucose(row.glucose_estimate_min)}</td>
                  <td>{formatGlucose(row.glucose_estimate_max)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>

      <footer className="report-foot">
        Model: {prediction?.model_name ?? "-"}. Laporan ini hasil estimasi berbasis AI dari sampel saliva dan bukan diagnosis medis. Konsultasikan hasil dengan tenaga kesehatan.
      </footer>
    </article>,
    document.body,
  );
}
