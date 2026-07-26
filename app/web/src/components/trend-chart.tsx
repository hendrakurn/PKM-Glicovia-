"use client";

import { useMemo, useState, type FormEvent } from "react";
import type { PredictionTrendRow, SubjectDeviceRow } from "@/lib/api/types";
import { formatDateLabel, formatGlucose, formatValue, toNumber } from "@/lib/utils";
import { Field, GlicoBadge, GlicoButton, StateBlock } from "@/components/glicovia-ui";

type TrendWindow = "week" | "month";

export type PredictionTrendFilters = {
  deviceId: string;
  range: TrendWindow;
  from: string;
  to: string;
};

type TrendChartProps = {
  trends: PredictionTrendRow[];
  devices: SubjectDeviceRow[];
  filters: PredictionTrendFilters;
  loading?: boolean;
  onFilterChange: (next: PredictionTrendFilters) => void;
  onApplyFilters: (event: FormEvent<HTMLFormElement>) => void;
  onResetFilters: () => void;
};

type HoveredPoint = {
  x: number;
  y: number;
  label: string;
  average: number;
  sampleCount: string;
  minimum: string;
  maximum: string;
};

function formatBucketLabel(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown date";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

export function TrendChart({ trends, devices, filters, loading = false, onFilterChange, onApplyFilters, onResetFilters }: TrendChartProps) {
  const [hoveredPoint, setHoveredPoint] = useState<HoveredPoint | null>(null);

  const values = useMemo(() => {
    return [...trends]
      .reverse()
      .map((row) => ({
        row,
        average: toNumber(row.glucose_estimate_avg),
        minimum: row.glucose_estimate_min ?? "Not available",
        maximum: row.glucose_estimate_max ?? "Not available",
      }))
      .filter((point): point is { row: PredictionTrendRow; average: number; minimum: string; maximum: string } => point.average !== null);
  }, [trends]);

  if (values.length === 0) {
    return (
      <div className="grid gap-5">
        <TrendControls
          devices={devices}
          filters={filters}
          loading={loading}
          onFilterChange={onFilterChange}
          onApplyFilters={onApplyFilters}
          onResetFilters={onResetFilters}
        />
        <StateBlock
          tone="slate"
          title="No prediction trend in this window"
          description="Adjust the device or date window, then wait for successful AI predictions to accumulate. This chart now follows blood glucose estimates from the SVM prediction log."
        />
      </div>
    );
  }

  const min = Math.min(...values.map((point) => point.average));
  const max = Math.max(...values.map((point) => point.average));
  const span = Math.max(10, max - min);
  const axisMin = Math.max(0, Math.floor((min - span * 0.15) / 10) * 10);
  const axisMax = Math.ceil((max + span * 0.15) / 10) * 10;
  const axisSpan = Math.max(10, axisMax - axisMin);
  const width = 860;
  const height = 360;
  const padding = { top: 28, right: 30, bottom: 70, left: 78 };

  const points = values.map((point, index) => {
    const x = values.length === 1
      ? width / 2
      : padding.left + (index / (values.length - 1)) * (width - padding.left - padding.right);
    const y = padding.top + (1 - (point.average - axisMin) / axisSpan) * (height - padding.top - padding.bottom);
    return { ...point, x, y };
  });

  const yTicks = Array.from({ length: 5 }, (_, index) => axisMin + (axisSpan / 4) * index).reverse();
  const path = points.map((point) => `${point.x},${point.y}`).join(" ");
  const latest = points[points.length - 1];
  const totalPredictions = values.reduce((sum, point) => sum + Number(point.row.prediction_count || 0), 0);

  return (
    <div className="grid gap-5">
      <TrendControls
        devices={devices}
        filters={filters}
        loading={loading}
        onFilterChange={onFilterChange}
        onApplyFilters={onApplyFilters}
        onResetFilters={onResetFilters}
      />

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_220px] lg:items-start">
        <div>
          <p className="label-text">Estimated blood glucose trend</p>
          <div className="mt-2 flex flex-wrap items-end gap-3">
            <p className="text-4xl font-black text-[color:var(--ink)]">{formatGlucose(latest.average).replace(" mg/dL", "")}</p>
            <p className="pb-1 text-base font-black text-[color:var(--ink-muted)]">mg/dL</p>
          </div>
          <p className="mt-2 text-sm leading-6 text-[color:var(--ink-muted)]">
            The line now tracks AI-estimated blood glucose from `prediction_results`, not raw salivary glucose.
          </p>
        </div>

        <div className="grid gap-2 text-sm font-bold text-[color:var(--ink-muted)] lg:text-right">
          <p>{formatDateLabel(values[0].row.bucket_start)} to {formatDateLabel(latest.row.bucket_start)}</p>
          <p>{values.length} buckets</p>
          <p>{totalPredictions} successful predictions</p>
          <div className="flex flex-wrap gap-2 lg:justify-end">
            <GlicoBadge tone="sky">Y axis: mg/dL</GlicoBadge>
            <GlicoBadge tone="mint">X axis: date</GlicoBadge>
          </div>
        </div>
      </div>

      <div className="relative overflow-hidden rounded-[8px] border-2 border-[color:var(--line)] bg-[color:var(--surface-soft)] p-4">
        {hoveredPoint ? (
          <div
            className="pointer-events-none absolute z-10 min-w-44 rounded-[8px] border-2 border-[color:var(--line)] bg-[color:var(--canvas)] px-3 py-2 text-xs font-bold text-[color:var(--ink)] shadow-[3px_3px_0_var(--line)]"
            style={{ left: Math.max(12, Math.min(hoveredPoint.x - 64, width - 180)), top: Math.max(12, hoveredPoint.y - 72) }}
          >
            <p>{hoveredPoint.label}</p>
            <p className="mt-1">Average: {formatGlucose(hoveredPoint.average)}</p>
            <p>Samples: {hoveredPoint.sampleCount}</p>
            <p>Range: {formatValue(hoveredPoint.minimum)} to {formatValue(hoveredPoint.maximum)} mg/dL</p>
          </div>
        ) : null}

        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Estimated blood glucose trend" className="h-[360px] w-full">
          <text x={padding.left} y={16} className="fill-[color:var(--ink-muted)] text-[12px] font-bold">Blood glucose (mg/dL)</text>
          {yTicks.map((tick) => {
            const y = padding.top + (1 - (tick - axisMin) / axisSpan) * (height - padding.top - padding.bottom);
            return (
              <g key={tick}>
                <line x1={padding.left} x2={width - padding.right} y1={y} y2={y} stroke="rgba(23,19,15,0.18)" strokeWidth="2" />
                <text x={padding.left - 12} y={y + 4} textAnchor="end" className="fill-[color:var(--ink-muted)] text-[11px] font-bold">
                  {Math.round(tick)}
                </text>
              </g>
            );
          })}

          <line x1={padding.left} x2={width - padding.right} y1={height - padding.bottom} y2={height - padding.bottom} stroke="var(--line)" strokeWidth="2.5" />
          <line x1={padding.left} x2={padding.left} y1={padding.top} y2={height - padding.bottom} stroke="var(--line)" strokeWidth="2.5" />

          <polyline points={path} fill="none" stroke="var(--line)" strokeWidth="5" strokeLinejoin="round" strokeLinecap="round" />
          <polyline points={path} fill="none" stroke="var(--green)" strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />

          {points.map((point, index) => (
            <g key={`${point.row.bucket_start}-${index}`}>
              <circle
                cx={point.x}
                cy={point.y}
                r={index === points.length - 1 ? 7 : 6}
                fill={index === points.length - 1 ? "var(--butter)" : "var(--canvas)"}
                stroke="var(--line)"
                strokeWidth="3"
                onMouseEnter={() => setHoveredPoint({
                  x: point.x,
                  y: point.y,
                  label: formatBucketLabel(point.row.bucket_start),
                  average: point.average,
                  sampleCount: point.row.prediction_count,
                  minimum: point.minimum,
                  maximum: point.maximum,
                })}
                onMouseLeave={() => setHoveredPoint(null)}
              />
              <text x={point.x} y={height - padding.bottom + 24} textAnchor="middle" className="fill-[color:var(--ink-muted)] text-[11px] font-bold">
                {formatDateLabel(point.row.bucket_start)}
              </text>
            </g>
          ))}

          <text x={width / 2} y={height - 18} textAnchor="middle" className="fill-[color:var(--ink-muted)] text-[12px] font-bold">Recorded date</text>
        </svg>
      </div>
    </div>
  );
}

function TrendControls({ devices, filters, loading, onFilterChange, onApplyFilters, onResetFilters }: {
  devices: SubjectDeviceRow[];
  filters: PredictionTrendFilters;
  loading: boolean;
  onFilterChange: (next: PredictionTrendFilters) => void;
  onApplyFilters: (event: FormEvent<HTMLFormElement>) => void;
  onResetFilters: () => void;
}) {
  return (
    <form onSubmit={onApplyFilters} className="grid gap-4 rounded-[8px] border-2 border-[color:var(--line)] bg-[color:var(--canvas)] p-4 lg:grid-cols-[minmax(190px,1fr)_150px_150px_150px_auto_auto] lg:items-end">
      <Field label="Device">
        <select
          className="glico-input"
          value={filters.deviceId}
          onChange={(event) => onFilterChange({ ...filters, deviceId: event.target.value })}
        >
          <option value="">All active devices</option>
          {devices.map((device) => (
            <option key={device.device_id} value={device.device_id}>{device.device_name || device.device_code}</option>
          ))}
        </select>
      </Field>
      <Field label="History view">
        <select
          className="glico-input"
          value={filters.range}
          onChange={(event) => onFilterChange({ ...filters, range: event.target.value as TrendWindow })}
        >
          <option value="week">Weekly</option>
          <option value="month">Monthly</option>
        </select>
      </Field>
      <Field label="From">
        <input className="glico-input" type="date" value={filters.from} onChange={(event) => onFilterChange({ ...filters, from: event.target.value })} />
      </Field>
      <Field label="To">
        <input className="glico-input" type="date" value={filters.to} onChange={(event) => onFilterChange({ ...filters, to: event.target.value })} />
      </Field>
      <GlicoButton type="submit" variant="ink" disabled={loading}>Apply</GlicoButton>
      <GlicoButton type="button" variant="secondary" disabled={loading} onClick={onResetFilters}>Reset</GlicoButton>
    </form>
  );
}
