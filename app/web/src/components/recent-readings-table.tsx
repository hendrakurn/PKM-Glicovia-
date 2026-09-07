"use client";

import { useMemo, useState } from "react";
import { Badge, Panel } from "@/components/ui";
import { cn, formatDecimal, formatMgdl } from "@/lib/utils";
import type { Reading } from "@/lib/data";

type SortKey = "samplingDate" | "subjectId" | "predictedBgMgdl" | "clinicalCategory" | "fastingHours";

const sortLabel: Record<SortKey, string> = {
  samplingDate: "Time",
  subjectId: "Subject",
  predictedBgMgdl: "Predicted BG",
  clinicalCategory: "Category",
  fastingHours: "Fasting",
};

export function RecentReadingsTable({ rows, title = "Recent readings", subtitle = "Latest measurements from the prototype and manual entry flow." }: { rows: Reading[]; title?: string; subtitle?: string }) {
  const [sortKey, setSortKey] = useState<SortKey>("samplingDate");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  const [selected, setSelected] = useState<Reading | null>(rows[0] ?? null);

  const sorted = useMemo(() => {
    const list = [...rows].sort((a, b) => {
      let left: number | string = a[sortKey];
      let right: number | string = b[sortKey];

      if (sortKey === "samplingDate") {
        left = `${a.samplingDate} ${a.samplingTime}`;
        right = `${b.samplingDate} ${b.samplingTime}`;
      }

      if (typeof left === "string" && typeof right === "string") {
        return sortDirection === "asc" ? left.localeCompare(right) : right.localeCompare(left);
      }

      return sortDirection === "asc" ? Number(left) - Number(right) : Number(right) - Number(left);
    });

    return list;
  }, [rows, sortKey, sortDirection]);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
      return;
    }
    setSortKey(key);
    setSortDirection("desc");
  };

  return (
    <Panel className="p-0 overflow-hidden">
      <div className="flex flex-col gap-3 border-b border-[color:var(--border)] p-5 md:flex-row md:items-end md:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-[color:var(--text-primary)]">{title}</h2>
          <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{subtitle}</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-[color:var(--text-secondary)]">
          <span className="text-[color:var(--green)]">✓</span>
          {sorted.length} records visible
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-[1100px] w-full border-collapse">
          <thead className="bg-[color:var(--surface-elevated)] text-left text-xs uppercase tracking-[0.14em] text-[color:var(--text-muted)]">
            <tr>
              {(["subjectId", "samplingDate", "fastingHours", "predictedBgMgdl", "clinicalCategory"] as SortKey[]).map((key) => (
                <th key={key} className="px-5 py-4">
                  <button className="inline-flex items-center gap-1.5 font-medium" onClick={() => toggleSort(key)}>
                    {sortLabel[key]}
                    {sortKey === key ? (sortDirection === "asc" ? <span>▲</span> : <span>▼</span>) : <span className="opacity-30">↕</span>}
                  </button>
                </th>
              ))}
              <th className="px-5 py-4">Status</th>
              <th className="px-5 py-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((row) => {
              const categoryTone = row.clinicalCategory === "Normal" ? "emerald" : row.clinicalCategory === "Pre-Diabetes" ? "blue" : "red";
              const deviceTone = row.deviceStatus === "Online" ? "emerald" : row.deviceStatus === "Syncing" ? "blue" : "red";

              return (
                <tr
                  key={row.id}
                  className={cn(
                    "border-t border-[color:var(--border)] transition-colors hover:bg-[color:var(--surface-elevated)]",
                    selected?.id === row.id && "bg-[color:var(--mint)]/50"
                  )}
                >
                  <td className="px-5 py-4">
                    <div className="space-y-1">
                      <p className="font-medium text-[color:var(--text-primary)]">{row.subjectId}</p>
                      <p className="text-sm text-[color:var(--text-secondary)]">{row.samplingDate}</p>
                    </div>
                  </td>
                  <td className="px-5 py-4 font-mono text-sm text-[color:var(--text-primary)]">{row.samplingTime}</td>
                  <td className="px-5 py-4 text-sm text-[color:var(--text-primary)]">{row.fastingHours} h</td>
                  <td className="px-5 py-4">
                    <div className="space-y-1">
                      <p className="font-semibold text-[color:var(--text-primary)]">{formatMgdl(row.predictedBgMgdl)} mg/dL</p>
                      <p className="text-sm text-[color:var(--text-secondary)]">Ref {formatMgdl(row.bgReferenceMgdl)} mg/dL</p>
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <Badge tone={categoryTone}>{row.clinicalCategory}</Badge>
                  </td>
                  <td className="px-5 py-4">
                    <Badge tone={deviceTone}>{row.deviceStatus}</Badge>
                  </td>
                  <td className="px-5 py-4">
                    <button
                      type="button"
                      onClick={() => setSelected(row)}
                      className="inline-flex items-center gap-2 rounded-[10px] border border-[color:var(--border)] bg-[color:var(--surface)] px-3 py-1.5 text-sm font-medium text-[color:var(--text-primary)] transition-colors hover:bg-[color:var(--surface-elevated)]"
                    >
                      Review
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {selected ? (
        <aside className="border-t border-[color:var(--border)] bg-[color:var(--surface-elevated)] p-5">
          <div className="mb-4 flex items-start justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.14em] text-[color:var(--text-muted)]">Record detail</p>
              <h3 className="mt-1 text-lg font-semibold text-[color:var(--text-primary)]">{selected.subjectId}</h3>
            </div>
            <button type="button" onClick={() => setSelected(null)} className="rounded-full border border-[color:var(--border)] bg-[color:var(--surface)] px-3 py-1.5 text-sm text-[color:var(--text-secondary)]">
              Close
            </button>
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <DetailField label="Sampling" value={`${selected.samplingDate} ${selected.samplingTime}`} />
            <DetailField label="Fasting" value={`${selected.fastingHours} hours`} />
            <DetailField label="Saliva pH" value={formatDecimal(selected.salivaPh, 1)} />
            <DetailField label="Viscosity" value={`${formatDecimal(selected.salivaViscositySec, 1)} sec`} />
            <DetailField label="Saliva glucose" value={`${formatMgdl(selected.salivaGlucoseMgdl)} mg/dL`} />
            <DetailField label="Predicted BG" value={`${formatMgdl(selected.predictedBgMgdl)} mg/dL`} />
            <DetailField label="Reference BG" value={`${formatMgdl(selected.bgReferenceMgdl)} mg/dL`} />
            <DetailField label="Raw packet" value={`${selected.protoGlucoseRaw}`} />
          </div>
          {selected.anomaly ? (
            <div className="mt-4 flex items-start gap-3 rounded-[12px] border border-[color:var(--amber)] bg-[color:var(--butter)] p-4 text-[color:var(--ink)]">
              <span className="mt-0.5 text-base leading-none">!</span>
              <div>
                <p className="font-medium">Anomaly note</p>
                <p className="text-sm text-[color:var(--ink-muted)]">{selected.anomaly}</p>
              </div>
            </div>
          ) : null}
        </aside>
      ) : null}
    </Panel>
  );
}

function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[12px] border border-[color:var(--border)] bg-[color:var(--surface)] p-3">
      <p className="text-[11px] uppercase tracking-[0.16em] text-[color:var(--text-muted)]">{label}</p>
      <p className="mt-1 text-sm font-medium text-[color:var(--text-primary)]">{value}</p>
    </div>
  );
}
