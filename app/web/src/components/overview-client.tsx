"use client";

import Link from "next/link";
import { useEffect, useMemo, useState, type FormEvent } from "react";
import { ArrowClockwise, Brain, Clock, DeviceMobile, Drop, WarningCircle } from "@phosphor-icons/react";
import { api, ApiError } from "@/lib/api/client";
import type { AuthProfile, PredictionResultRow, PredictionTrendRow, SensorReadingRow, SubjectDeviceRow } from "@/lib/api/types";
import { categoryTone, dateInputToIso, formatGlucose, formatPercentValue, formatTimestamp, qualityTone, readingMeaning, relativeFreshness, statusTone, toNumber } from "@/lib/utils";
import { GlicoBadge, GlicoButton, GlicoPanel, Heartbeat, KeyValue, PageHeader, SkeletonBlock, StateBlock, glicoButtonClasses } from "@/components/glicovia-ui";
import { useAuth } from "@/components/auth-provider";
import { TrendChart, type PredictionTrendFilters } from "@/components/trend-chart";

type OverviewData = {
  profile: AuthProfile;
  latest: SensorReadingRow | null;
  latestPrediction: PredictionResultRow | null;
  trends: PredictionTrendRow[];
  devices: SubjectDeviceRow[];
};

const initialTrendFilters: PredictionTrendFilters = {
  deviceId: "",
  range: "week",
  from: "",
  to: "",
};

function startOfDayIso(date: Date) {
  const value = new Date(date);
  value.setHours(0, 0, 0, 0);
  return value.toISOString();
}

function endOfDayIso(date: Date) {
  const value = new Date(date);
  value.setHours(23, 59, 59, 999);
  return value.toISOString();
}

function buildTrendQuery(filters: PredictionTrendFilters) {
  const now = new Date();
  const daysBack = filters.range === "month" ? 29 : 6;
  const fromDate = new Date(now);
  fromDate.setDate(now.getDate() - daysBack);

  return {
    device_id: filters.deviceId || undefined,
    from: filters.from ? dateInputToIso(filters.from) : startOfDayIso(fromDate),
    to: filters.to ? dateInputToIso(filters.to, true) : endOfDayIso(now),
    bucket: filters.range === "month" ? "week" as const : "day" as const,
    limit: filters.range === "month" ? 8 : 7,
  };
}

export function OverviewClient() {
  const { token } = useAuth();
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [trendFilters, setTrendFilters] = useState<PredictionTrendFilters>(initialTrendFilters);
  const [appliedTrendFilters, setAppliedTrendFilters] = useState<PredictionTrendFilters>(initialTrendFilters);

  useEffect(() => {
    if (!token) return;
    const authToken = token;
    let active = true;

    async function load() {
      try {
        setLoading(true);
        setError(null);
        const trendQuery = buildTrendQuery(appliedTrendFilters);
        const profile = await api.me(authToken);
        const [latestResult, latestPredictionResult, trendsResult, devicesResult] = await Promise.allSettled([
          api.latestReading({ device_id: appliedTrendFilters.deviceId || undefined }, authToken),
          api.myLatestPrediction({ device_id: appliedTrendFilters.deviceId || undefined }, authToken),
          api.myPredictionTrends(trendQuery, authToken),
          api.myDevices(authToken),
        ]);

        if (!active) return;

        let latest: SensorReadingRow | null = null;
        if (latestResult.status === "fulfilled") {
          latest = latestResult.value.reading;
        } else if (!(latestResult.reason instanceof ApiError && latestResult.reason.status === 404)) {
          throw latestResult.reason;
        }

        let latestPrediction: PredictionResultRow | null = null;
        if (latestPredictionResult.status === "fulfilled") {
          latestPrediction = latestPredictionResult.value.prediction;
        } else if (!(latestPredictionResult.reason instanceof ApiError && latestPredictionResult.reason.status === 404)) {
          throw latestPredictionResult.reason;
        }

        if (trendsResult.status === "rejected") throw trendsResult.reason;
        if (devicesResult.status === "rejected") throw devicesResult.reason;

        setData({
          profile,
          latest,
          latestPrediction,
          trends: trendsResult.value.trends,
          devices: devicesResult.value.devices,
        });
      } catch (caught) {
        if (active) setError(caught instanceof Error ? caught.message : "Unable to load overview.");
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, [appliedTrendFilters, refreshKey, token]);

  function applyTrendFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAppliedTrendFilters(trendFilters);
  }

  function resetTrendFilters() {
    setTrendFilters(initialTrendFilters);
    setAppliedTrendFilters(initialTrendFilters);
  }

  const latestPrediction = data?.latestPrediction ?? null;
  const primaryValue = latestPrediction?.glucose_estimate ?? data?.latest?.salivary_glucose ?? null;
  const hasPrimaryValue = toNumber(primaryValue) !== null;
  const primaryLabel = latestPrediction?.glucose_estimate ? "Estimated blood glucose" : "Saliva glucose signal";
  const category = latestPrediction?.clinical_category ?? (data?.latest ? "Reading received" : null);
  const freshness = relativeFreshness(latestPrediction?.sensor_recorded_at ?? data?.latest?.recorded_at);

  const nextAction = useMemo(() => {
    if (!data) return "Open the dashboard after sign-in.";
    if (data.devices.length === 0) return "Pair a GLICOVIA reader to begin collecting readings.";
    if (!data.latest) return "Keep the reader nearby and send the first saliva sample when ready.";
    if ((data.latest.quality_flag ?? "").toLowerCase() !== "valid") return "Repeat when convenient so the model receives a cleaner sample.";
    return "Keep your normal routine and compare the next blood glucose estimate for movement, not just a single point.";
  }, [data]);

  if (loading) return <OverviewSkeleton />;

  if (error) {
    return (
      <StateBlock
        tone="coral"
        title="Overview could not load"
        description={error}
        icon={<WarningCircle size={22} weight="bold" />}
        action={
          <GlicoButton type="button" variant="secondary" onClick={() => setRefreshKey((current) => current + 1)}>
            <ArrowClockwise size={18} weight="bold" />
            Try again
          </GlicoButton>
        }
      />
    );
  }

  if (!data) return null;

  return (
    <div className="grid gap-7">
      <PageHeader
        eyebrow="Subject overview"
        title={`Good data starts with context, ${data.profile.subject.display_name || data.profile.user.full_name || "there"}.`}
        description="The headline estimate, model trust, and historical blood-glucose trend now follow the AI prediction log rather than raw salivary glucose alone."
        action={
          <GlicoButton type="button" variant="secondary" onClick={() => setRefreshKey((current) => current + 1)}>
            <ArrowClockwise size={18} weight="bold" />
            Refresh
          </GlicoButton>
        }
      />

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1.35fr)_390px]">
        <GlicoPanel className="reveal-up overflow-hidden">
          <div className="grid gap-0 lg:grid-cols-[minmax(0,1fr)_280px]">
            <div className="p-6 sm:p-8">
              <div className="mb-5 flex flex-wrap items-center gap-2">
                <GlicoBadge tone={categoryTone(category)}>{category ?? "Waiting for reading"}</GlicoBadge>
                {data.latest ? <Heartbeat label={freshness} /> : null}
              </div>
              <p className="label-text">{primaryLabel}</p>
              <div className="mt-3 flex flex-wrap items-end gap-3">
                <p className="text-6xl font-black leading-none text-[color:var(--ink)] sm:text-7xl lg:text-8xl">
                  {hasPrimaryValue ? formatGlucose(primaryValue).replace(" mg/dL", "") : "--"}
                </p>
                <p className="pb-2 text-xl font-black text-[color:var(--ink-muted)]">mg/dL</p>
              </div>
              <p className="mt-5 max-w-2xl text-lg leading-8 text-[color:var(--ink-muted)]">{readingMeaning(latestPrediction?.clinical_category)}</p>
            </div>

            <div className="border-t-2 border-[color:var(--line)] bg-[color:var(--mint)] p-5 lg:border-l-2 lg:border-t-0">
              <p className="label-text">Next action</p>
              <p className="mt-3 text-2xl font-black leading-tight text-[color:var(--ink)]">{nextAction}</p>
              <div className="mt-6 grid gap-3">
                <Link href="/readings" className={glicoButtonClasses("secondary")}>Open readings</Link>
                <Link href="/devices" className={glicoButtonClasses("ink")}>Pair device</Link>
              </div>
            </div>
          </div>
        </GlicoPanel>

        <div className="hidden md:block">
          <TrustSignalsPanel latest={data.latest} latestPrediction={latestPrediction} />
        </div>
      </section>

      <section className="grid gap-5">
        <GlicoPanel className="reveal-up p-5 sm:p-6" style={{ animationDelay: "120ms" }}>
          <TrendChart
            trends={data.trends}
            devices={data.devices}
            filters={trendFilters}
            loading={loading}
            onFilterChange={setTrendFilters}
            onApplyFilters={applyTrendFilters}
            onResetFilters={resetTrendFilters}
          />
        </GlicoPanel>

        <div className="md:hidden">
          <TrustSignalsPanel latest={data.latest} latestPrediction={latestPrediction} />
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-3">
        <StateBlock tone="mint" title="Freshness" description={freshness} icon={<Clock size={22} weight="bold" />} />
        <StateBlock tone="sky" title="Data quality" description={data.latest?.quality_flag ?? "No reading has been received yet."} icon={<Drop size={22} weight="bold" />} />
        <StateBlock tone="butter" title="Subject code" description={data.profile.subject.subject_code} icon={<DeviceMobile size={22} weight="bold" />} />
      </section>
    </div>
  );
}

function TrustSignalsPanel({ latest, latestPrediction }: { latest: SensorReadingRow | null; latestPrediction: PredictionResultRow | null }) {
  return (
    <GlicoPanel className="reveal-up p-5" style={{ animationDelay: "70ms" }}>
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <p className="label-text">Trust signals</p>
          <h2 className="mt-2 text-2xl font-black text-[color:var(--ink)]">Why this reading is believable</h2>
        </div>
        <Brain size={30} weight="bold" />
      </div>
      <KeyValue label="Model" value={latestPrediction ? `${latestPrediction.model_name ?? "Model"} ${latestPrediction.model_version ?? "version pending"}` : "No prediction yet"} />
      <KeyValue label="Confidence" value={formatPercentValue(latestPrediction?.confidence_score)} />
      <KeyValue label="Inference" value={<GlicoBadge tone={statusTone(latestPrediction?.inference_status)}>{latestPrediction?.inference_status ?? "Not available"}</GlicoBadge>} />
      <KeyValue label="Reading quality" value={<GlicoBadge tone={qualityTone(latest?.quality_flag)}>{latest?.quality_flag ?? "No reading"}</GlicoBadge>} />
      <KeyValue label="Reading timestamp" value={formatTimestamp(latest?.recorded_at)} />
    </GlicoPanel>
  );
}

function OverviewSkeleton() {
  return (
    <div className="grid gap-7">
      <SkeletonBlock className="h-28" />
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.35fr)_390px]">
        <SkeletonBlock className="h-80" />
        <SkeletonBlock className="hidden h-80 md:block" />
      </div>
      <SkeletonBlock className="h-[620px]" />
      <SkeletonBlock className="h-80 md:hidden" />
    </div>
  );
}
