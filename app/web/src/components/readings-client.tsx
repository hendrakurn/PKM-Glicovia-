"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { CaretLeft, CaretRight, FunnelSimple, WarningCircle } from "@phosphor-icons/react";
import { api } from "@/lib/api/client";
import type { SensorReadingRow, SubjectDeviceRow } from "@/lib/api/types";
import { dateInputToIso, formatTimestamp, formatValue, qualityTone, truncateId } from "@/lib/utils";
import { Field, GlicoBadge, GlicoButton, GlicoPanel, PageHeader, SkeletonBlock, StateBlock } from "@/components/glicovia-ui";
import { useAuth } from "@/components/auth-provider";

type ReadingsData = {
  devices: SubjectDeviceRow[];
  readings: SensorReadingRow[];
};

type FilterForm = {
  deviceId: string;
  from: string;
  to: string;
  limit: string;
};

function readForm(searchParams: URLSearchParams): FilterForm {
  return {
    deviceId: searchParams.get("device_id") ?? "",
    from: searchParams.get("from") ?? "",
    to: searchParams.get("to") ?? "",
    limit: searchParams.get("limit") ?? "25",
  };
}

function readOffset(searchParams: URLSearchParams) {
  const parsed = Number(searchParams.get("offset") ?? "0");
  return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : 0;
}

export function ReadingsClient() {
  const { token } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryString = searchParams.toString();
  const urlParams = useMemo(() => new URLSearchParams(queryString), [queryString]);
  const [form, setForm] = useState<FilterForm>(() => readForm(urlParams));
  const [data, setData] = useState<ReadingsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const offset = readOffset(urlParams);
  const limit = Math.min(100, Math.max(1, Number(urlParams.get("limit") ?? "25") || 25));

  useEffect(() => {
    if (!token) return;
    const authToken = token;
    let active = true;

    async function load() {
      try {
        setLoading(true);
        setError(null);
        const [devices, readings] = await Promise.all([
          api.myDevices(authToken),
          api.myReadings(
            {
              device_id: urlParams.get("device_id") ?? undefined,
              from: dateInputToIso(urlParams.get("from") ?? ""),
              to: dateInputToIso(urlParams.get("to") ?? "", true),
              limit,
              offset,
            },
            authToken
          ),
        ]);
        if (active) setData({ devices: devices.devices, readings: readings.readings });
      } catch (caught) {
        if (active) setError(caught instanceof Error ? caught.message : "Unable to load readings.");
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, [limit, offset, token, urlParams]);

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const next = new URLSearchParams();
    if (form.deviceId) next.set("device_id", form.deviceId);
    if (form.from) next.set("from", form.from);
    if (form.to) next.set("to", form.to);
    if (form.limit) next.set("limit", form.limit);
    next.set("offset", "0");
    router.replace(`/readings?${next.toString()}`);
  }

  function pageTo(nextOffset: number) {
    const next = new URLSearchParams(queryString);
    next.set("limit", String(limit));
    next.set("offset", String(Math.max(0, nextOffset)));
    router.replace(`/readings?${next.toString()}`);
  }

  const deviceNames = useMemo(() => {
    const map = new Map<string, string>();
    data?.devices.forEach((device) => map.set(device.device_id, device.device_name || device.device_code));
    return map;
  }, [data?.devices]);

  return (
    <div className="grid gap-7">
      <PageHeader
        eyebrow="Readings"
        title="Signal history with backend-backed filters."
        description="The table follows the readings API exactly, including device, date window, limit, and offset query parameters."
      />

      <GlicoPanel className="p-5 sm:p-6">
        <form onSubmit={applyFilters} className="grid gap-4 lg:grid-cols-[minmax(180px,1fr)_160px_160px_130px_auto] lg:items-end">
          <Field label="Device">
            <select className="glico-input" value={form.deviceId} onChange={(event) => setForm((current) => ({ ...current, deviceId: event.target.value }))}>
              <option value="">All active devices</option>
              {data?.devices.map((device) => (
                <option key={device.device_id} value={device.device_id}>
                  {device.device_name || device.device_code}
                </option>
              ))}
            </select>
          </Field>
          <Field label="From">
            <input className="glico-input" type="date" value={form.from} onChange={(event) => setForm((current) => ({ ...current, from: event.target.value }))} />
          </Field>
          <Field label="To">
            <input className="glico-input" type="date" value={form.to} onChange={(event) => setForm((current) => ({ ...current, to: event.target.value }))} />
          </Field>
          <Field label="Limit">
            <select className="glico-input" value={form.limit} onChange={(event) => setForm((current) => ({ ...current, limit: event.target.value }))}>
              <option value="10">10</option>
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </Field>
          <GlicoButton type="submit" variant="ink">
            <FunnelSimple size={18} weight="bold" />
            Filter
          </GlicoButton>
        </form>
      </GlicoPanel>

      {loading ? (
        <SkeletonBlock className="h-[520px]" />
      ) : error ? (
        <StateBlock tone="coral" title="Readings could not load" description={error} icon={<WarningCircle size={22} weight="bold" />} />
      ) : data?.readings.length === 0 ? (
        <StateBlock tone="slate" title="No readings in this window" description="Try a wider date range, another device, or wait for the next saliva sample to arrive." />
      ) : (
        <GlicoPanel className="overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b-2 border-[color:var(--line)] bg-[color:var(--mint)] p-5">
            <div>
              <p className="label-text">Reading rows</p>
              <h2 className="mt-2 text-2xl font-black text-[color:var(--ink)]">{data?.readings.length ?? 0} returned</h2>
            </div>
            <GlicoBadge tone="sky">Offset {offset}</GlicoBadge>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[860px] border-collapse text-left">
              <thead className="bg-[color:var(--surface-soft)]">
                <tr className="border-b-2 border-[color:var(--line)] text-xs font-black uppercase text-[color:var(--ink-muted)]">
                  <th className="px-4 py-3">Recorded</th>
                  <th className="px-4 py-3">Device</th>
                  <th className="px-4 py-3">Salivary glucose</th>
                  <th className="px-4 py-3">pH</th>
                  <th className="px-4 py-3">Fructosamine</th>
                  <th className="px-4 py-3">Quality</th>
                  <th className="px-4 py-3">Payload</th>
                </tr>
              </thead>
              <tbody className="divide-y-2 divide-[color:var(--line)]">
                {data?.readings.map((reading) => (
                  <tr key={reading.id} className="bg-[color:var(--canvas)] align-top">
                    <td className="px-4 py-4 text-sm font-bold text-[color:var(--ink)]">{formatTimestamp(reading.recorded_at)}</td>
                    <td className="px-4 py-4">
                      <p className="text-sm font-black text-[color:var(--ink)]">{deviceNames.get(reading.device_id) ?? truncateId(reading.device_id)}</p>
                      <p className="mt-1 font-mono text-xs text-[color:var(--ink-muted)]">{truncateId(reading.id)}</p>
                    </td>
                    <td className="px-4 py-4 text-sm font-black text-[color:var(--ink)]">{formatValue(reading.salivary_glucose, 1)}</td>
                    <td className="px-4 py-4 text-sm font-bold text-[color:var(--ink-muted)]">{formatValue(reading.ph, 2)}</td>
                    <td className="px-4 py-4 text-sm font-bold text-[color:var(--ink-muted)]">{formatValue(reading.fructosamine, 1)}</td>
                    <td className="px-4 py-4"><GlicoBadge tone={qualityTone(reading.quality_flag)}>{reading.quality_flag}</GlicoBadge></td>
                    <td className="px-4 py-4 text-sm font-bold text-[color:var(--ink-muted)]">{reading.raw_payload ? "Captured" : "Empty"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 border-t-2 border-[color:var(--line)] p-4">
            <GlicoButton type="button" variant="secondary" disabled={offset === 0} onClick={() => pageTo(offset - limit)}>
              <CaretLeft size={18} weight="bold" />
              Previous
            </GlicoButton>
            <p className="font-mono text-xs font-bold text-[color:var(--ink-muted)]">limit={limit} offset={offset}</p>
            <GlicoButton type="button" variant="secondary" disabled={(data?.readings.length ?? 0) < limit} onClick={() => pageTo(offset + limit)}>
              Next
              <CaretRight size={18} weight="bold" />
            </GlicoButton>
          </div>
        </GlicoPanel>
      )}
    </div>
  );
}
