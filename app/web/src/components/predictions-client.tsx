"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Brain, CaretLeft, CaretRight, CheckCircle, FunnelSimple, Plus, ShieldCheck, WarningCircle } from "@phosphor-icons/react";
import { api } from "@/lib/api/client";
import type { ModelVersionRow, PredictionResultRow } from "@/lib/api/types";
import { categoryTone, dateTimeLocalToIso, formatGlucose, formatPercentValue, formatTimestamp, statusTone, truncateId } from "@/lib/utils";
import { Field, GlicoBadge, GlicoButton, GlicoPanel, KeyValue, PageHeader, SkeletonBlock, StateBlock } from "@/components/glicovia-ui";

type ModelForm = {
  model_name: string;
  version: string;
  status: "training" | "deployed" | "archived";
  artifact_url: string;
  trained_at: string;
  deployed_at: string;
  notes: string;
};

const initialModelForm: ModelForm = {
  model_name: "",
  version: "",
  status: "training",
  artifact_url: "",
  trained_at: "",
  deployed_at: "",
  notes: "",
};

function readOffset(searchParams: URLSearchParams) {
  const parsed = Number(searchParams.get("offset") ?? "0");
  return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : 0;
}

export function PredictionsClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryString = searchParams.toString();
  const urlParams = useMemo(() => new URLSearchParams(queryString), [queryString]);
  const [models, setModels] = useState<ModelVersionRow[]>([]);
  const [predictions, setPredictions] = useState<PredictionResultRow[]>([]);
  const [sensorReadingId, setSensorReadingId] = useState(urlParams.get("sensor_reading_id") ?? "");
  const [modelVersionId, setModelVersionId] = useState(urlParams.get("model_version_id") ?? "");
  const [limit, setLimit] = useState(urlParams.get("limit") ?? "25");
  const [modelForm, setModelForm] = useState<ModelForm>(initialModelForm);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const offset = readOffset(urlParams);
  const effectiveLimit = Math.min(100, Math.max(1, Number(urlParams.get("limit") ?? "25") || 25));

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const [nextModels, nextPredictions] = await Promise.all([
          api.models(),
          api.predictions({
            limit: effectiveLimit,
            offset,
            sensor_reading_id: urlParams.get("sensor_reading_id") ?? undefined,
            model_version_id: urlParams.get("model_version_id") ?? undefined,
          }),
        ]);
        if (active) {
          setModels(nextModels);
          setPredictions(nextPredictions);
        }
      } catch (caught) {
        if (active) setError(caught instanceof Error ? caught.message : "Unable to load predictions.");
      } finally {
        if (active) setLoading(false);
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, [effectiveLimit, offset, urlParams]);

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const next = new URLSearchParams();
    if (sensorReadingId.trim()) next.set("sensor_reading_id", sensorReadingId.trim());
    if (modelVersionId) next.set("model_version_id", modelVersionId);
    if (limit) next.set("limit", limit);
    next.set("offset", "0");
    router.replace(`/predictions?${next.toString()}`);
  }

  function pageTo(nextOffset: number) {
    const next = new URLSearchParams(queryString);
    next.set("limit", String(effectiveLimit));
    next.set("offset", String(Math.max(0, nextOffset)));
    router.replace(`/predictions?${next.toString()}`);
  }

  async function createModel(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!modelForm.model_name.trim() || !modelForm.version.trim()) {
      setError("model_name and version are required.");
      return;
    }

    try {
      setCreating(true);
      setError(null);
      setMessage(null);
      const model = await api.createModel({
        model_name: modelForm.model_name.trim(),
        version: modelForm.version.trim(),
        status: modelForm.status,
        artifact_url: modelForm.artifact_url.trim() || null,
        trained_at: dateTimeLocalToIso(modelForm.trained_at),
        deployed_at: dateTimeLocalToIso(modelForm.deployed_at),
        notes: modelForm.notes.trim() || null,
      });
      setMessage(`${model.model_name} ${model.version} created.`);
      setModelForm(initialModelForm);
      setModels((current) => [model, ...current]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Model creation failed.");
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="grid gap-7">
      <PageHeader
        eyebrow="Predictions and models"
        title="Reviewer context without hiding uncertainty."
        description="Predictions are read from the backend result log, while model versions can be registered exactly through the `/api/models` body contract."
      />

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_430px]">
        <div className="grid gap-5">
          <GlicoPanel className="p-5 sm:p-6">
            <form onSubmit={applyFilters} className="grid gap-4 lg:grid-cols-[minmax(180px,1fr)_minmax(180px,1fr)_120px_auto] lg:items-end">
              <Field label="Sensor reading ID">
                <input className="glico-input font-mono" value={sensorReadingId} onChange={(event) => setSensorReadingId(event.target.value)} placeholder="Optional reading id" />
              </Field>
              <Field label="Model version">
                <select className="glico-input" value={modelVersionId} onChange={(event) => setModelVersionId(event.target.value)}>
                  <option value="">All models</option>
                  {models.map((model) => (
                    <option key={model.id} value={model.id}>{model.model_name} {model.version}</option>
                  ))}
                </select>
              </Field>
              <Field label="Limit">
                <select className="glico-input" value={limit} onChange={(event) => setLimit(event.target.value)}>
                  <option value="10">10</option>
                  <option value="25">25</option>
                  <option value="50">50</option>
                  <option value="100">100</option>
                </select>
              </Field>
              <GlicoButton type="submit" variant="ink"><FunnelSimple size={18} weight="bold" /> Filter</GlicoButton>
            </form>
          </GlicoPanel>

          {loading ? (
            <SkeletonBlock className="h-[560px]" />
          ) : error ? (
            <StateBlock tone="coral" title="Prediction context could not load" description={error} icon={<WarningCircle size={22} weight="bold" />} />
          ) : predictions.length === 0 ? (
            <StateBlock tone="slate" title="No predictions returned" description="The backend currently stores prediction metadata only when another process writes results." icon={<Brain size={22} weight="bold" />} />
          ) : (
            <GlicoPanel className="overflow-hidden">
              <div className="border-b-2 border-[color:var(--line)] bg-[color:var(--rose)] p-5">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="label-text">Prediction log</p>
                    <h2 className="mt-2 text-2xl font-black text-[color:var(--ink)]">{predictions.length} predictions</h2>
                  </div>
                  <ShieldCheck size={32} weight="bold" />
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full min-w-[860px] border-collapse text-left">
                  <thead className="bg-[color:var(--surface-soft)]">
                    <tr className="border-b-2 border-[color:var(--line)] text-xs font-black uppercase text-[color:var(--ink-muted)]">
                      <th className="px-4 py-3">Predicted</th>
                      <th className="px-4 py-3">Estimate</th>
                      <th className="px-4 py-3">Category</th>
                      <th className="px-4 py-3">Confidence</th>
                      <th className="px-4 py-3">Inference</th>
                      <th className="px-4 py-3">Model</th>
                      <th className="px-4 py-3">Reading</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y-2 divide-[color:var(--line)]">
                    {predictions.map((prediction) => (
                      <tr key={prediction.id} className="bg-[color:var(--canvas)] align-top">
                        <td className="px-4 py-4 text-sm font-bold text-[color:var(--ink)]">{formatTimestamp(prediction.predicted_at ?? prediction.created_at)}</td>
                        <td className="px-4 py-4 text-sm font-black text-[color:var(--ink)]">{formatGlucose(prediction.glucose_estimate)}</td>
                        <td className="px-4 py-4"><GlicoBadge tone={categoryTone(prediction.clinical_category)}>{prediction.clinical_category ?? "Not labeled"}</GlicoBadge></td>
                        <td className="px-4 py-4 text-sm font-bold text-[color:var(--ink-muted)]">{formatPercentValue(prediction.confidence_score)}</td>
                        <td className="px-4 py-4"><GlicoBadge tone={statusTone(prediction.inference_status)}>{prediction.inference_status}</GlicoBadge></td>
                        <td className="px-4 py-4 text-sm font-bold text-[color:var(--ink)]">{prediction.model_name ?? "Model"} {prediction.model_version ?? ""}</td>
                        <td className="px-4 py-4 font-mono text-xs font-bold text-[color:var(--ink-muted)]">{truncateId(prediction.sensor_reading_id)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-3 border-t-2 border-[color:var(--line)] p-4">
                <GlicoButton type="button" variant="secondary" disabled={offset === 0} onClick={() => pageTo(offset - effectiveLimit)}><CaretLeft size={18} weight="bold" /> Previous</GlicoButton>
                <p className="font-mono text-xs font-bold text-[color:var(--ink-muted)]">limit={effectiveLimit} offset={offset}</p>
                <GlicoButton type="button" variant="secondary" disabled={predictions.length < effectiveLimit} onClick={() => pageTo(offset + effectiveLimit)}>Next <CaretRight size={18} weight="bold" /></GlicoButton>
              </div>
            </GlicoPanel>
          )}
        </div>

        <div className="grid gap-5">
          <GlicoPanel className="p-5 sm:p-6">
            <div className="mb-5">
              <p className="label-text">Register model</p>
              <h2 className="mt-2 text-3xl font-black leading-tight text-[color:var(--ink)]">Add a model version.</h2>
            </div>
            <form onSubmit={createModel} className="grid gap-4">
              <Field label="model_name">
                <input className="glico-input" value={modelForm.model_name} onChange={(event) => setModelForm((current) => ({ ...current, model_name: event.target.value }))} placeholder="svr_saliva_glucose" />
              </Field>
              <Field label="version">
                <input className="glico-input" value={modelForm.version} onChange={(event) => setModelForm((current) => ({ ...current, version: event.target.value }))} placeholder="v1.0.0" />
              </Field>
              <Field label="status">
                <select className="glico-input" value={modelForm.status} onChange={(event) => setModelForm((current) => ({ ...current, status: event.target.value as ModelForm["status"] }))}>
                  <option value="training">training</option>
                  <option value="deployed">deployed</option>
                  <option value="archived">archived</option>
                </select>
              </Field>
              <Field label="artifact_url">
                <input className="glico-input" value={modelForm.artifact_url} onChange={(event) => setModelForm((current) => ({ ...current, artifact_url: event.target.value }))} placeholder="Optional artifact URL" />
              </Field>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="trained_at">
                  <input className="glico-input" type="datetime-local" value={modelForm.trained_at} onChange={(event) => setModelForm((current) => ({ ...current, trained_at: event.target.value }))} />
                </Field>
                <Field label="deployed_at">
                  <input className="glico-input" type="datetime-local" value={modelForm.deployed_at} onChange={(event) => setModelForm((current) => ({ ...current, deployed_at: event.target.value }))} />
                </Field>
              </div>
              <Field label="notes">
                <textarea className="glico-input min-h-24 resize-y" value={modelForm.notes} onChange={(event) => setModelForm((current) => ({ ...current, notes: event.target.value }))} placeholder="Optional reviewer note" />
              </Field>
              <GlicoButton type="submit" variant="ink" disabled={creating}><Plus size={18} weight="bold" /> Create model</GlicoButton>
            </form>
          </GlicoPanel>

          <GlicoPanel className="overflow-hidden">
            <div className="border-b-2 border-[color:var(--line)] bg-[color:var(--sky)] p-5">
              <p className="label-text">Model versions</p>
              <h2 className="mt-2 text-2xl font-black text-[color:var(--ink)]">{models.length} registered</h2>
            </div>
            {models.length === 0 ? (
              <div className="p-5"><StateBlock tone="slate" title="No model versions" description="Create the first model version to attach context to future predictions." /></div>
            ) : (
              <div className="divide-y-2 divide-[color:var(--line)]">
                {models.slice(0, 6).map((model) => (
                  <div key={model.id} className="p-5">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="text-lg font-black text-[color:var(--ink)]">{model.model_name}</p>
                        <p className="mt-1 font-mono text-xs font-bold text-[color:var(--ink-muted)]">{model.version} - {truncateId(model.id)}</p>
                      </div>
                      <GlicoBadge tone={statusTone(model.status)}>{model.status}</GlicoBadge>
                    </div>
                    <KeyValue label="Deployed" value={formatTimestamp(model.deployed_at)} />
                    <KeyValue label="Notes" value={model.notes || "No notes"} />
                  </div>
                ))}
              </div>
            )}
          </GlicoPanel>
        </div>
      </section>

      {message ? <StateBlock tone="mint" title="Model saved" description={message} icon={<CheckCircle size={22} weight="bold" />} /> : null}
    </div>
  );
}
