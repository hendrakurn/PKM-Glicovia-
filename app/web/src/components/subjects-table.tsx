"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { Badge, Panel } from "@/components/ui";
import { cn, formatMgdl } from "@/lib/utils";
import type { Subject } from "@/lib/data";

const filters = ["All", "Online", "Syncing", "Offline"] as const;

type Filter = (typeof filters)[number];
type SortKey = "recordsCount" | "latestSampling" | "latestPredictedBgMgdl";

export function SubjectsTable({ subjects }: { subjects: Subject[] }) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("All");
  const [sortKey, setSortKey] = useState<SortKey>("latestSampling");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  const visible = useMemo(() => {
    const filtered = subjects.filter((subject) => {
      const matchesQuery = [subject.code, subject.alias, subject.cohort, subject.note].some((value) =>
        value.toLowerCase().includes(query.toLowerCase())
      );
      const matchesFilter = filter === "All" ? true : subject.deviceStatus === filter;
      return matchesQuery && matchesFilter;
    });

    return [...filtered].sort((a, b) => {
      const left = a[sortKey];
      const right = b[sortKey];
      if (typeof left === "string" && typeof right === "string") {
        return sortDirection === "asc" ? left.localeCompare(right) : right.localeCompare(left);
      }
      return sortDirection === "asc" ? Number(left) - Number(right) : Number(right) - Number(left);
    });
  }, [subjects, query, filter, sortKey, sortDirection]);

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
      <div className="flex flex-col gap-4 border-b border-[color:var(--border)] p-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-[color:var(--text-primary)]">Anonymous subject registry</h2>
          <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Search the cohort, filter live device states, and open each subject profile.</p>
        </div>
        <label className="flex h-10 min-w-[280px] items-center gap-2 rounded-[12px] border border-[color:var(--border)] bg-[color:var(--surface)] px-3 text-[color:var(--text-muted)]">
          <span className="text-base leading-none">⌕</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search code, alias, or note"
            className="w-full bg-transparent text-sm text-[color:var(--text-primary)] outline-none placeholder:text-[color:var(--text-muted)]"
          />
        </label>
      </div>

      <div className="flex flex-wrap gap-2 border-b border-[color:var(--border)] px-5 py-4">
        {filters.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setFilter(item)}
            className={cn(
              "rounded-full border px-3 py-1.5 text-sm font-medium transition-colors",
              filter === item
                ? "border-[color:var(--green)] bg-[color:var(--mint)] text-[color:var(--green)]"
                : "border-[color:var(--border)] bg-[color:var(--surface)] text-[color:var(--text-secondary)] hover:bg-[color:var(--surface-elevated)]"
            )}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-[1040px] w-full border-collapse">
          <thead className="bg-[color:var(--surface-elevated)] text-left text-xs uppercase tracking-[0.14em] text-[color:var(--text-muted)]">
            <tr>
              {[
                ["latestSampling", "Last sampling"],
                ["recordsCount", "Records"],
                ["latestPredictedBgMgdl", "Predicted BG"],
              ].map(([key, label]) => (
                <th key={key} className="px-5 py-4">
                  <button type="button" onClick={() => toggleSort(key as SortKey)} className="inline-flex items-center gap-1.5 font-medium">
                    {label}
                    {sortKey === key ? (sortDirection === "asc" ? <span>▲</span> : <span>▼</span>) : <span className="opacity-30">↕</span>}
                  </button>
                </th>
              ))}
              <th className="px-5 py-4">Subject</th>
              <th className="px-5 py-4">Cohort</th>
              <th className="px-5 py-4">Status</th>
              <th className="px-5 py-4">Action</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((subject) => {
              const tone = subject.deviceStatus === "Online" ? "emerald" : subject.deviceStatus === "Syncing" ? "blue" : "red";
              const categoryTone = subject.clinicalCategory === "Normal" ? "emerald" : subject.clinicalCategory === "Pre-Diabetes" ? "blue" : "red";

              return (
                <tr key={subject.id} className="border-t border-[color:var(--border)] hover:bg-[color:var(--surface-elevated)]">
                  <td className="px-5 py-4 font-mono text-sm text-[color:var(--text-primary)]">{subject.latestSampling}</td>
                  <td className="px-5 py-4 text-sm text-[color:var(--text-primary)]">{subject.recordsCount}</td>
                  <td className="px-5 py-4">
                    <div className="space-y-1">
                      <p className="font-semibold text-[color:var(--text-primary)]">{formatMgdl(subject.latestPredictedBgMgdl)} mg/dL</p>
                      <p className="text-sm text-[color:var(--text-secondary)]">Ref {formatMgdl(subject.lastReferenceBgMgdl)} mg/dL</p>
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <div className="space-y-1">
                      <Link href={`/subjects/${subject.id.toLowerCase()}`} className="font-semibold text-[color:var(--text-primary)] hover:text-[color:var(--green)]">
                        {subject.code}
                      </Link>
                      <p className="text-sm text-[color:var(--text-secondary)]">{subject.alias}</p>
                    </div>
                  </td>
                  <td className="px-5 py-4 text-sm text-[color:var(--text-primary)]">{subject.cohort}</td>
                  <td className="px-5 py-4 space-y-2">
                    <Badge tone={tone}>{subject.deviceStatus}</Badge>
                    <div>
                      <Badge tone={categoryTone}>{subject.clinicalCategory}</Badge>
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <Link href={`/subjects/${subject.id.toLowerCase()}`} className="inline-flex items-center rounded-[10px] border border-[color:var(--border)] bg-[color:var(--surface)] px-3 py-1.5 text-sm font-medium text-[color:var(--text-primary)] hover:bg-[color:var(--surface-elevated)]">
                      Open profile
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="border-t border-[color:var(--border)] px-5 py-4 text-sm text-[color:var(--text-secondary)]">
        Showing {visible.length} of {subjects.length} subjects
      </div>
    </Panel>
  );
}
