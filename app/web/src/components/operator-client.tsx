"use client";

import { useEffect, useState, type FormEvent } from "react";
import { ArrowClockwise, CheckCircle, DeviceMobile, Key, PencilSimple, Plus, Trash, WarningCircle } from "@phosphor-icons/react";
import { api } from "@/lib/api/client";
import type { DeviceStatus, DeviceWithAssignment, PairingTokenRecord } from "@/lib/api/types";
import { formatTimestamp, statusTone, truncateId } from "@/lib/utils";
import { Field, GlicoBadge, GlicoButton, GlicoPanel, KeyValue, PageHeader, SkeletonBlock, StateBlock } from "@/components/glicovia-ui";
import { useAuth } from "@/components/auth-provider";

const statuses: DeviceStatus[] = ["unpaired", "paired", "offline", "online", "inactive"];

type DeviceForm = {
  deviceCode: string;
  name: string;
  mqttTopic: string;
  status: DeviceStatus;
  firmwareVersion: string;
};

const initialForm: DeviceForm = {
  deviceCode: "",
  name: "",
  mqttTopic: "",
  status: "unpaired",
  firmwareVersion: "",
};

export function OperatorClient() {
  const { token } = useAuth();
  const [devices, setDevices] = useState<DeviceWithAssignment[]>([]);
  const [selected, setSelected] = useState<DeviceWithAssignment | null>(null);
  const [deviceForm, setDeviceForm] = useState<DeviceForm>(initialForm);
  const [selectedStatus, setSelectedStatus] = useState<DeviceStatus>("unpaired");
  const [expiresInMinutes, setExpiresInMinutes] = useState("15");
  const [pairingToken, setPairingToken] = useState<PairingTokenRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const result = await api.listDevices(token);
        if (active) setDevices(result);
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

  async function openDevice(deviceId: string) {
    try {
      setBusy(deviceId);
      setPairingToken(null);
      setError(null);
      const result = await api.getDevice(deviceId, token);
      setSelected(result);
      setSelectedStatus(result.status);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Device detail could not load.");
    } finally {
      setBusy(null);
    }
  }

  async function createDevice(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!deviceForm.deviceCode.trim() || !deviceForm.mqttTopic.trim()) {
      setError("deviceCode and mqttTopic are required.");
      return;
    }

    try {
      setBusy("create");
      setError(null);
      setMessage(null);
      const created = await api.createDevice(
        {
          deviceCode: deviceForm.deviceCode.trim(),
          name: deviceForm.name.trim() || null,
          mqttTopic: deviceForm.mqttTopic.trim(),
          status: deviceForm.status,
          firmwareVersion: deviceForm.firmwareVersion.trim() || null,
        },
        token
      );
      setMessage(`${created.device_code} created.`);
      setDeviceForm(initialForm);
      setRefreshKey((current) => current + 1);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Device creation failed.");
    } finally {
      setBusy(null);
    }
  }

  async function updateSelectedDevice() {
    if (!selected) return;
    try {
      setBusy("update");
      setError(null);
      setMessage(null);
      const updated = await api.updateDevice(
        selected.id,
        { status: selectedStatus, lastSeenAt: selectedStatus === "online" ? new Date().toISOString() : undefined },
        token
      );
      setMessage(`${updated.device_code} updated to ${updated.status}.`);
      setSelected((current) => (current ? { ...current, ...updated } : current));
      setRefreshKey((current) => current + 1);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Device update failed.");
    } finally {
      setBusy(null);
    }
  }

  async function deleteSelectedDevice() {
    if (!selected) return;
    if (!window.confirm(`Delete device ${selected.device_code}?`)) return;
    try {
      setBusy("delete");
      setError(null);
      setMessage(null);
      await api.deleteDevice(selected.id, token);
      setMessage(`${selected.device_code} deleted.`);
      setSelected(null);
      setRefreshKey((current) => current + 1);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Device deletion failed.");
    } finally {
      setBusy(null);
    }
  }

  async function generatePairingToken() {
    if (!selected) return;
    const minutes = Math.max(1, Math.min(1440, Number(expiresInMinutes) || 15));
    try {
      setBusy("token");
      setError(null);
      setMessage(null);
      const result = await api.createPairingToken({ deviceId: selected.id, expiresInMinutes: minutes }, token);
      setPairingToken(result.pairingToken);
      setMessage(`Pairing token generated for ${result.device.device_code}.`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Pairing token creation failed.");
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="grid gap-7">
      <PageHeader
        eyebrow="Operator device management"
        title="Raw device operations stay out of the patient view."
        description="This area represents the backend device CRUD and pairing-token capabilities. It does not assume role enforcement that the backend does not currently implement."
        action={
          <GlicoButton type="button" variant="secondary" onClick={() => setRefreshKey((current) => current + 1)}>
            <ArrowClockwise size={18} weight="bold" />
            Refresh
          </GlicoButton>
        }
      />

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_460px]">
        <GlicoPanel className="overflow-hidden">
          <div className="border-b-2 border-[color:var(--line)] bg-[color:var(--ink)] p-5 text-[color:var(--canvas)]">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="label-text text-[color:var(--butter)]">Registered devices</p>
                <h2 className="mt-2 text-3xl font-black">{devices.length} records</h2>
              </div>
              <DeviceMobile size={36} weight="bold" />
            </div>
          </div>

          {loading ? (
            <div className="grid gap-4 p-5"><SkeletonBlock className="h-24" /><SkeletonBlock className="h-24" /></div>
          ) : devices.length === 0 ? (
            <div className="p-5"><StateBlock tone="slate" title="No devices registered" description="Create the first device record before generating a pairing token." /></div>
          ) : (
            <div className="divide-y-2 divide-[color:var(--line)]">
              {devices.map((device) => (
                <button
                  key={device.id}
                  type="button"
                  className="grid w-full gap-3 bg-[color:var(--canvas)] p-5 text-left transition hover:bg-[color:var(--surface-elevated)] md:grid-cols-[minmax(0,1fr)_140px] md:items-center"
                  onClick={() => void openDevice(device.id)}
                >
                  <span className="min-w-0">
                    <span className="block text-lg font-black text-[color:var(--ink)]">{device.name || device.device_code}</span>
                    <span className="mt-1 block truncate font-mono text-xs font-bold text-[color:var(--ink-muted)]">{device.mqtt_topic}</span>
                    <span className="mt-2 block text-xs font-bold text-[color:var(--ink-muted)]">{truncateId(device.id)}</span>
                  </span>
                  <span className="flex items-center justify-start md:justify-end">
                    <GlicoBadge tone={statusTone(device.status)}>{busy === device.id ? "Loading" : device.status}</GlicoBadge>
                  </span>
                </button>
              ))}
            </div>
          )}
        </GlicoPanel>

        <div className="grid gap-5">
          <GlicoPanel className="p-5 sm:p-6">
            <div className="mb-5">
              <p className="label-text">Create device</p>
              <h2 className="mt-2 text-3xl font-black leading-tight text-[color:var(--ink)]">Register a reader.</h2>
            </div>
            <form onSubmit={createDevice} className="grid gap-4">
              <Field label="deviceCode">
                <input className="glico-input" value={deviceForm.deviceCode} onChange={(event) => setDeviceForm((current) => ({ ...current, deviceCode: event.target.value }))} placeholder="GLV-001" />
              </Field>
              <Field label="name">
                <input className="glico-input" value={deviceForm.name} onChange={(event) => setDeviceForm((current) => ({ ...current, name: event.target.value }))} placeholder="Optional reader label" />
              </Field>
              <Field label="mqttTopic">
                <input className="glico-input font-mono" value={deviceForm.mqttTopic} onChange={(event) => setDeviceForm((current) => ({ ...current, mqttTopic: event.target.value }))} placeholder="devices/glv-001/readings" />
              </Field>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="status">
                  <select className="glico-input" value={deviceForm.status} onChange={(event) => setDeviceForm((current) => ({ ...current, status: event.target.value as DeviceStatus }))}>
                    {statuses.map((status) => <option key={status} value={status}>{status}</option>)}
                  </select>
                </Field>
                <Field label="firmwareVersion">
                  <input className="glico-input" value={deviceForm.firmwareVersion} onChange={(event) => setDeviceForm((current) => ({ ...current, firmwareVersion: event.target.value }))} placeholder="v0.3.1" />
                </Field>
              </div>
              <GlicoButton type="submit" variant="ink" disabled={busy === "create"}><Plus size={18} weight="bold" /> Create device</GlicoButton>
            </form>
          </GlicoPanel>
        </div>
      </section>

      {selected ? (
        <GlicoPanel className="overflow-hidden">
          <div className="border-b-2 border-[color:var(--line)] bg-[color:var(--sky)] p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="label-text">Selected device</p>
                <h2 className="mt-2 text-3xl font-black text-[color:var(--ink)]">{selected.name || selected.device_code}</h2>
              </div>
              <GlicoBadge tone={statusTone(selected.status)}>{selected.status}</GlicoBadge>
            </div>
          </div>

          <div className="grid gap-0 xl:grid-cols-[minmax(0,1fr)_420px]">
            <div className="p-5 sm:p-6">
              <div className="grid gap-5 md:grid-cols-2">
                <KeyValue label="Device ID" value={selected.id} mono />
                <KeyValue label="MQTT topic" value={selected.mqtt_topic} mono />
                <KeyValue label="Firmware" value={selected.firmware_version ?? "Not set"} />
                <KeyValue label="Last seen" value={formatTimestamp(selected.last_seen_at)} />
                <KeyValue label="Created" value={formatTimestamp(selected.created_at)} />
                <KeyValue label="Active assignment" value={selected.active_assignment ? `${selected.active_assignment.subject_code ?? selected.active_assignment.subject_id} since ${formatTimestamp(selected.active_assignment.assigned_at)}` : "None"} />
              </div>

              <div className="mt-6 grid gap-4 sm:grid-cols-[220px_auto_auto] sm:items-end">
                <Field label="Patch status">
                  <select className="glico-input" value={selectedStatus} onChange={(event) => setSelectedStatus(event.target.value as DeviceStatus)}>
                    {statuses.map((status) => <option key={status} value={status}>{status}</option>)}
                  </select>
                </Field>
                <GlicoButton type="button" variant="secondary" onClick={() => void updateSelectedDevice()} disabled={busy === "update"}><PencilSimple size={18} weight="bold" /> Update</GlicoButton>
                <GlicoButton type="button" variant="danger" onClick={() => void deleteSelectedDevice()} disabled={busy === "delete"}><Trash size={18} weight="bold" /> Delete</GlicoButton>
              </div>
            </div>

            <div className="border-t-2 border-[color:var(--line)] bg-[color:var(--butter)] p-5 sm:p-6 xl:border-l-2 xl:border-t-0">
              <p className="label-text">Pairing token</p>
              <h3 className="mt-2 text-2xl font-black text-[color:var(--ink)]">Generate for subject scan.</h3>
              <div className="mt-5 grid gap-4 sm:grid-cols-[1fr_auto] sm:items-end">
                <Field label="expiresInMinutes">
                  <input className="glico-input" type="number" min="1" max="1440" value={expiresInMinutes} onChange={(event) => setExpiresInMinutes(event.target.value)} />
                </Field>
                <GlicoButton type="button" variant="ink" onClick={() => void generatePairingToken()} disabled={busy === "token"}><Key size={18} weight="bold" /> Generate</GlicoButton>
              </div>
              {pairingToken ? (
                <div className="mt-5 grid gap-3">
                  <div className="soft-row bg-[color:var(--canvas)] p-4">
                    <p className="label-text">Token</p>
                    <p className="mt-2 break-all font-mono text-xs font-black text-[color:var(--ink)]">{pairingToken.token}</p>
                  </div>
                  <KeyValue label="Expires" value={formatTimestamp(pairingToken.expires_at)} />
                  <KeyValue label="QR payload" value={pairingToken.qr_payload} mono />
                </div>
              ) : null}
            </div>
          </div>
        </GlicoPanel>
      ) : null}

      {message ? <StateBlock tone="mint" title="Operator action complete" description={message} icon={<CheckCircle size={22} weight="bold" />} /> : null}
      {error ? <StateBlock tone="coral" title="Operator action needs attention" description={error} icon={<WarningCircle size={22} weight="bold" />} /> : null}
    </div>
  );
}
