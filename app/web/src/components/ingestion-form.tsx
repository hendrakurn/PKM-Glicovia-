"use client";

import { useMemo, useState, type FormEvent, type ReactNode } from "react";
import { Badge, Panel, ToastPill } from "@/components/ui";

type FormState = {
  source: "hardware" | "manual";
  subjectId: string;
  samplingDate: string;
  samplingTime: string;
  fastingHours: string;
  salivaPh: string;
  salivaViscositySec: string;
  salivaGlucoseMgdl: string;
  bgReferenceMgdl: string;
  protoGlucoseRaw: string;
  deviceStatus: "Online" | "Syncing" | "Offline";
};

type Errors = Partial<Record<keyof FormState, string>>;

const initialState: FormState = {
  source: "hardware",
  subjectId: "SUB-1201",
  samplingDate: "2026-07-04",
  samplingTime: "16:05",
  fastingHours: "8",
  salivaPh: "6.5",
  salivaViscositySec: "4.8",
  salivaGlucoseMgdl: "11.2",
  bgReferenceMgdl: "121",
  protoGlucoseRaw: "1094",
  deviceStatus: "Online",
};

export function IngestionForm() {
  const [form, setForm] = useState<FormState>(initialState);
  const [errors, setErrors] = useState<Errors>({});
  const [success, setSuccess] = useState<string | null>(null);

  const fieldCount = useMemo(() => Object.keys(form).length, [form]);

  const updateField = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((current) => ({ ...current, [key]: value }));
    setErrors((current) => ({ ...current, [key]: undefined }));
  };

  const validate = () => {
    const next: Errors = {};
    if (!/^SUB-\d{4}$/.test(form.subjectId)) next.subjectId = "Use anonymous IDs like SUB-1201.";
    if (!form.samplingDate) next.samplingDate = "Date is required.";
    if (!form.samplingTime) next.samplingTime = "Time is required.";
    const fasting = Number(form.fastingHours);
    if (Number.isNaN(fasting) || fasting < 0 || fasting > 18) next.fastingHours = "Fasting window must be between 0 and 18 hours.";
    const ph = Number(form.salivaPh);
    if (Number.isNaN(ph) || ph < 5.5 || ph > 7.5) next.salivaPh = "Saliva pH should stay within 5.5 to 7.5.";
    const viscosity = Number(form.salivaViscositySec);
    if (Number.isNaN(viscosity) || viscosity <= 0) next.salivaViscositySec = "Viscosity must be greater than 0.";
    const salivaGlucose = Number(form.salivaGlucoseMgdl);
    if (Number.isNaN(salivaGlucose) || salivaGlucose < 0) next.salivaGlucoseMgdl = "Saliva glucose needs a valid positive value.";
    const ref = Number(form.bgReferenceMgdl);
    if (Number.isNaN(ref) || ref < 40 || ref > 500) next.bgReferenceMgdl = "Reference BG must stay in a believable clinical range.";
    const raw = Number(form.protoGlucoseRaw);
    if (Number.isNaN(raw) || raw <= 0) next.protoGlucoseRaw = "Raw packet value is required.";
    return next;
  };

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    const next = validate();
    setErrors(next);
    if (Object.keys(next).length > 0) {
      setSuccess(null);
      return;
    }

    setSuccess(`Sample ${form.subjectId} accepted and queued for prediction.`);
    window.setTimeout(() => setSuccess(null), 3600);
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.5fr)_360px]">
      <Panel className="p-0 overflow-hidden">
        <div className="border-b border-[color:var(--border)] p-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-[color:var(--text-primary)]">Submit a measurement</h2>
              <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Accepts hardware payloads and manual data during prototype validation.</p>
            </div>
            <Badge tone="emerald">{fieldCount} fields</Badge>
          </div>
        </div>

        <form onSubmit={onSubmit} className="grid gap-5 p-5 md:grid-cols-2">
          <Field label="Source" error={errors.source}>
            <select value={form.source} onChange={(event) => updateField("source", event.target.value as FormState["source"])} className="input-field">
              <option value="hardware">Hardware</option>
              <option value="manual">Manual</option>
            </select>
          </Field>
          <Field label="Device status" error={errors.deviceStatus}>
            <select value={form.deviceStatus} onChange={(event) => updateField("deviceStatus", event.target.value as FormState["deviceStatus"])} className="input-field">
              <option value="Online">Online</option>
              <option value="Syncing">Syncing</option>
              <option value="Offline">Offline</option>
            </select>
          </Field>
          <Field label="Anonymous subject ID" error={errors.subjectId}>
            <input value={form.subjectId} onChange={(event) => updateField("subjectId", event.target.value)} className="input-field" placeholder="SUB-1201" />
          </Field>
          <Field label="Sampling date" error={errors.samplingDate}>
            <input type="date" value={form.samplingDate} onChange={(event) => updateField("samplingDate", event.target.value)} className="input-field" />
          </Field>
          <Field label="Sampling time" error={errors.samplingTime}>
            <input type="time" value={form.samplingTime} onChange={(event) => updateField("samplingTime", event.target.value)} className="input-field" />
          </Field>
          <Field label="Fasting hours" error={errors.fastingHours}>
            <input type="number" step="0.1" value={form.fastingHours} onChange={(event) => updateField("fastingHours", event.target.value)} className="input-field" />
          </Field>
          <Field label="Saliva pH" error={errors.salivaPh}>
            <input type="number" step="0.1" value={form.salivaPh} onChange={(event) => updateField("salivaPh", event.target.value)} className="input-field" />
          </Field>
          <Field label="Viscosity" error={errors.salivaViscositySec}>
            <input type="number" step="0.1" value={form.salivaViscositySec} onChange={(event) => updateField("salivaViscositySec", event.target.value)} className="input-field" />
          </Field>
          <Field label="Saliva glucose" error={errors.salivaGlucoseMgdl}>
            <input type="number" step="0.1" value={form.salivaGlucoseMgdl} onChange={(event) => updateField("salivaGlucoseMgdl", event.target.value)} className="input-field" />
          </Field>
          <Field label="Reference BG" error={errors.bgReferenceMgdl}>
            <input type="number" step="1" value={form.bgReferenceMgdl} onChange={(event) => updateField("bgReferenceMgdl", event.target.value)} className="input-field" />
          </Field>
          <Field label="Proto raw value" error={errors.protoGlucoseRaw}>
            <input type="number" step="1" value={form.protoGlucoseRaw} onChange={(event) => updateField("protoGlucoseRaw", event.target.value)} className="input-field" />
          </Field>
          <div className="md:col-span-2 flex flex-wrap items-center gap-3 pt-2">
            <button type="submit" className="inline-flex items-center gap-2 rounded-[10px] border border-[color:var(--green)] bg-[color:var(--green)] px-4 py-2.5 text-sm font-medium text-[color:var(--canvas)] hover:bg-[color:var(--ink)]">
              <span className="text-sm leading-none">⇪</span>
              Submit reading
            </button>
            <button type="button" className="inline-flex items-center gap-2 rounded-[10px] border border-[color:var(--border)] bg-[color:var(--surface)] px-4 py-2.5 text-sm font-medium text-[color:var(--text-primary)] hover:bg-[color:var(--surface-elevated)]">
              <span className="text-sm leading-none">↗</span>
              Preview payload
            </button>
            <p className="text-sm text-[color:var(--text-secondary)]">Fields marked in monospace feed the model and the request log.</p>
          </div>
        </form>
      </Panel>

      <div className="space-y-6">
        <Panel className="p-5">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 text-[color:var(--green)]">✓</span>
            <div>
              <h3 className="text-base font-semibold text-[color:var(--text-primary)]">Validation guide</h3>
              <p className="mt-1 text-sm text-[color:var(--text-secondary)]">Anonymous IDs, believable ranges, and a stable device status keep the pipeline clean.</p>
            </div>
          </div>
          <div className="mt-4 space-y-3 text-sm text-[color:var(--text-secondary)]">
            <p>Subject IDs should follow the same format used in the registry.</p>
            <p>Reference BG is only used for evaluation and comparison views.</p>
            <p>Raw packet values are preserved exactly as sent from the prototype reader.</p>
          </div>
        </Panel>

        <Panel className="p-5">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 text-[color:var(--amber)]">!</span>
            <div>
              <h3 className="text-base font-semibold text-[color:var(--text-primary)]">Submission result</h3>
              <p className="mt-1 text-sm text-[color:var(--text-secondary)]">A toast appears after a valid submit so the team can confirm the entry went through.</p>
            </div>
          </div>
          <div className="mt-4 space-y-3">
            {success ? <ToastPill title={success} description="It is ready for prediction and history sync." tone="emerald" /> : <ToastPill title="Awaiting input" description="Fill the form and submit a sample to generate feedback." tone="blue" />}
          </div>
        </Panel>

        <Panel className="p-5">
          <div className="mb-4">
            <h3 className="text-base font-semibold text-[color:var(--text-primary)]">Last request log</h3>
            <p className="mt-1 text-sm text-[color:var(--text-secondary)]">The log mirrors what the backend receives in development.</p>
          </div>
          <div className="space-y-3 font-mono text-xs text-[color:var(--text-secondary)]">
            <LogLine label="10:42:11" value="POST /api/ingest accepted" />
            <LogLine label="10:45:22" value="Manual entry validated" />
            <LogLine label="10:53:09" value="Viscosity warning tagged" />
          </div>
        </Panel>
      </div>
    </div>
  );
}

function Field({ label, error, children }: { label: string; error?: string; children: ReactNode }) {
  return (
    <label className="space-y-2">
      <span className="block text-sm font-medium text-[color:var(--text-primary)]">{label}</span>
      {children}
      {error ? <span className="block text-sm text-[color:var(--red)]">{error}</span> : null}
    </label>
  );
}

function LogLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-[12px] border border-[color:var(--border)] bg-[color:var(--surface-elevated)] px-3 py-2">
      <span className="text-[color:var(--text-muted)]">{label}</span>
      <span className="text-[color:var(--text-primary)]">{value}</span>
    </div>
  );
}
