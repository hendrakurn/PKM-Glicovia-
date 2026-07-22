import type { ReadingTrendRow } from "@/lib/api/types";
import { formatDateLabel, formatValue, toNumber } from "@/lib/utils";
import { StateBlock } from "@/components/glicovia-ui";

type TrendChartProps = {
  trends: ReadingTrendRow[];
};

export function TrendChart({ trends }: TrendChartProps) {
  const ordered = [...trends].reverse();
  const values = ordered
    .map((row) => ({ row, value: toNumber(row.salivary_glucose_avg) }))
    .filter((point): point is { row: ReadingTrendRow; value: number } => point.value !== null);

  if (values.length < 2) {
    return (
      <StateBlock
        tone="slate"
        title="Trend waits for more readings"
        description="At least two timestamped readings are needed before a movement pattern is useful."
      />
    );
  }

  const min = Math.min(...values.map((point) => point.value));
  const max = Math.max(...values.map((point) => point.value));
  const span = Math.max(1, max - min);
  const width = 640;
  const height = 230;
  const padding = 34;
  const points = values.map((point, index) => {
    const x = padding + (index / Math.max(1, values.length - 1)) * (width - padding * 2);
    const y = height - padding - ((point.value - min) / span) * (height - padding * 2);
    return { ...point, x, y };
  });
  const path = points.map((point) => `${point.x},${point.y}`).join(" ");
  const latest = points[points.length - 1];

  return (
    <div className="grid gap-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="label-text">Salivary glucose trend</p>
          <p className="mt-2 text-3xl font-black text-[color:var(--ink)]">{formatValue(latest.value, 1)}</p>
        </div>
        <div className="text-right text-sm font-bold text-[color:var(--ink-muted)]">
          <p>{formatDateLabel(values[0].row.bucket_start)} to {formatDateLabel(latest.row.bucket_start)}</p>
          <p>{values.length} buckets</p>
        </div>
      </div>

      <div className="overflow-hidden rounded-[8px] border-2 border-[color:var(--line)] bg-[color:var(--surface-soft)]">
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Average salivary glucose trend" className="h-[230px] w-full">
          {[0, 1, 2, 3].map((line) => {
            const y = padding + line * ((height - padding * 2) / 3);
            return <line key={line} x1={padding} x2={width - padding} y1={y} y2={y} stroke="rgba(23,19,15,0.22)" strokeWidth="2" />;
          })}
          <polyline points={path} fill="none" stroke="var(--line)" strokeWidth="5" strokeLinejoin="round" strokeLinecap="round" />
          <polyline points={path} fill="none" stroke="var(--green)" strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />
          {points.map((point, index) => (
            <circle key={`${point.row.bucket_start}-${index}`} cx={point.x} cy={point.y} r={index === points.length - 1 ? 7 : 5} fill={index === points.length - 1 ? "var(--butter)" : "var(--canvas)"} stroke="var(--line)" strokeWidth="3" />
          ))}
        </svg>
      </div>
    </div>
  );
}
