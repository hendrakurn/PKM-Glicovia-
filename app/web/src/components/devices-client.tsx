"use client";

import { useEffect, useState, type FormEvent } from "react";
import { ArrowClockwise, CheckCircle, DeviceMobile, Key, LinkSimple, WarningCircle } from "@phosphor-icons/react";
import { api } from "@/lib/api/client";
import type { SubjectDeviceRow } from "@/lib/api/types";
import { formatTimestamp, statusTone, truncateId } from "@/lib/utils";
import { Field, GlicoBadge, GlicoButton, GlicoPanel, KeyValue, PageHeader, SkeletonBlock, StateBlock } from "@/components/glicovia-ui";
import { useAuth } from "@/components/auth-provider";

export function DevicesClient() {
  const { token, profile } = useAuth();
  const [devices, setDevices] = useState<SubjectDeviceRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [scanToken, setScanToken] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!token) return;
    const authToken = token;
    let active = true;

    async function load() {
      try {
        setLoading(true);
        setError(null);
        const result = await api.myDevices(authToken);
        if (active) setDevices(result.devices);
      } catch (caught) {
        if (active) setError(caught instanceof Error ? caught.message : "Unable to load devices.");
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, [refreshKey, token]);

  async function pairDevice(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !scanToken.trim()) return;
    try {
      setBusyId("pair");
      setError(null);
      setMessage(null);
      const result = await api.scanPairingToken({ token: scanToken.trim() }, token);
      setMessage(`${result.device.name || result.device.device_code} paired to your subject profile.`);
      setScanToken("");
      setRefreshKey((current) => current + 1);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Pairing failed.");
    } finally {
      setBusyId(null);
    }
  }

  async function unpairDevice(deviceId: string) {
    if (!token) return;
    try {
      setBusyId(deviceId);
      setError(null);
      setMessage(null);
      const result = await api.unpairDevice({ deviceId }, token);
      setMessage(`${result.device.name || result.device.device_code} was unpaired.`);
      setRefreshKey((current) => current + 1);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unpair failed.");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="grid gap-7">
      <PageHeader
        eyebrow="Devices and pairing"
        title="Keep the reader connection understandable."
        description="Active devices, pairing-token scan, unpairing, and device status are handled through the backend pairing and subject-device APIs."
        action={
          <GlicoButton type="button" variant="secondary" onClick={() => setRefreshKey((current) => current + 1)}>
            <ArrowClockwise size={18} weight="bold" />
            Refresh
          </GlicoButton>
        }
      />

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_420px]">
        <GlicoPanel className="overflow-hidden">
          <div className="border-b-2 border-[color:var(--line)] bg-[color:var(--butter)] p-5">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="label-text">Active devices</p>
                <h2 className="mt-2 text-3xl font-black text-[color:var(--ink)]">{devices.length} reader{devices.length === 1 ? "" : "s"}</h2>
              </div>
              <DeviceMobile size={36} weight="bold" />
            </div>
          </div>

          {loading ? (
            <div className="grid gap-4 p-5">
              <SkeletonBlock className="h-28" />
              <SkeletonBlock className="h-28" />
            </div>
          ) : devices.length === 0 ? (
            <div className="p-5">
              <StateBlock tone="slate" title="No active device" description="Use a pending pairing token from an operator to attach a reader to this subject account." icon={<Key size={22} weight="bold" />} />
            </div>
          ) : (
            <div className="divide-y-2 divide-[color:var(--line)]">
              {devices.map((device) => (
                <div key={device.device_assignment_id} className="grid gap-4 p-5 lg:grid-cols-[minmax(0,1fr)_190px] lg:items-center">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-xl font-black text-[color:var(--ink)]">{device.device_name || device.device_code}</h3>
                      <GlicoBadge tone={statusTone(device.device_status)}>{device.device_status}</GlicoBadge>
                    </div>
                    <div className="mt-3 grid gap-2 text-sm font-bold text-[color:var(--ink-muted)] sm:grid-cols-2">
                      <span className="min-w-0 truncate font-mono">{device.mqtt_topic}</span>
                      <span>Assigned {formatTimestamp(device.assigned_at)}</span>
                      <span className="inline-flex items-center gap-1"><LinkSimple size={14} weight="bold" /> {truncateId(device.device_id)}</span>
                      <span>{device.subject_code}</span>
                    </div>
                  </div>
                  <GlicoButton type="button" variant="danger" disabled={busyId === device.device_id} onClick={() => void unpairDevice(device.device_id)}>
                    Unpair
                  </GlicoButton>
                </div>
              ))}
            </div>
          )}
        </GlicoPanel>

        <GlicoPanel className="p-5 sm:p-6">
          <div className="mb-5">
            <p className="label-text">Pairing scan</p>
            <h2 className="mt-2 text-3xl font-black leading-tight text-[color:var(--ink)]">Enter a reader token.</h2>
            <p className="mt-3 text-sm leading-6 text-[color:var(--ink-muted)]">Tokens come from the operator pairing screen and are consumed by `/api/pairing/scan`.</p>
          </div>

          <form onSubmit={pairDevice} className="grid gap-4">
            <Field label="Pairing token">
              <textarea
                className="glico-input min-h-28 resize-y font-mono text-sm"
                value={scanToken}
                onChange={(event) => setScanToken(event.target.value)}
                placeholder="Paste token"
              />
            </Field>
            <GlicoButton type="submit" variant="ink" disabled={busyId === "pair" || !scanToken.trim()}>
              <Key size={18} weight="bold" />
              Pair reader
            </GlicoButton>
          </form>

          <div className="mt-6">
            <KeyValue label="Subject" value={profile?.subject.subject_code ?? "Not available"} mono />
            <KeyValue label="Assignment rule" value="The backend allows one active reader per subject and one active subject per reader." />
          </div>
        </GlicoPanel>
      </section>

      {message ? <StateBlock tone="mint" title="Device action complete" description={message} icon={<CheckCircle size={22} weight="bold" />} /> : null}
      {error ? <StateBlock tone="coral" title="Device action needs attention" description={error} icon={<WarningCircle size={22} weight="bold" />} /> : null}
    </div>
  );
}
