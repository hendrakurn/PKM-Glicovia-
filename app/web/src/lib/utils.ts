export function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

export function formatMgdl(value: number) {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatDecimal(value: number, digits = 1) {
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
}

export function formatPercent(value: number) {
  return `${value.toFixed(1)}%`;
}

export function formatDateLabel(value: string) {
  const date = new Date(value);
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  }).format(date);
}

export function toNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === "") return null;
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export function formatValue(value: unknown, digits = 0) {
  const number = toNumber(value);
  if (number === null) return "Not available";
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(number);
}

export function formatGlucose(value: unknown, digits = 0) {
  const number = toNumber(value);
  if (number === null) return "Not available";
  return `${formatValue(number, digits)} mg/dL`;
}

export function formatPercentValue(value: unknown) {
  const number = toNumber(value);
  if (number === null) return "Not available";
  const normalized = number <= 1 ? number * 100 : number;
  return `${normalized.toFixed(0)}%`;
}

export function formatTimestamp(value: string | null | undefined) {
  if (!value) return "Not available";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Not available";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

export function relativeFreshness(value: string | null | undefined) {
  if (!value) return "No timestamp";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Timestamp unavailable";
  const diffMs = Date.now() - date.getTime();
  if (diffMs < 0) return "Just received";
  const minutes = Math.floor(diffMs / 60_000);
  if (minutes < 1) return "Just received";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 48) return `${hours} hr ago`;
  const days = Math.floor(hours / 24);
  return `${days} days ago`;
}

export function dateInputToIso(value: string, endOfDay = false) {
  if (!value) return undefined;
  const suffix = endOfDay ? "T23:59:59.999" : "T00:00:00.000";
  const date = new Date(`${value}${suffix}`);
  return Number.isNaN(date.getTime()) ? undefined : date.toISOString();
}

export function dateTimeLocalToIso(value: string) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

export function truncateId(value: string | null | undefined, start = 7, end = 5) {
  if (!value) return "Not available";
  if (value.length <= start + end + 3) return value;
  return `${value.slice(0, start)}...${value.slice(-end)}`;
}

export function categoryTone(category: string | null | undefined) {
  const normalized = (category ?? "").toLowerCase();
  if (normalized.includes("normal") || normalized.includes("healthy")) return "green" as const;
  if (normalized.includes("pre") || normalized.includes("elevated") || normalized.includes("watch")) return "blue" as const;
  if (normalized.includes("hypo") || normalized.includes("low") || normalized.includes("high") || normalized.includes("diabetes")) return "red" as const;
  return "slate" as const;
}

export function qualityTone(flag: string | null | undefined) {
  const normalized = (flag ?? "").toLowerCase();
  if (normalized === "valid") return "green" as const;
  if (normalized === "suspect") return "amber" as const;
  if (normalized === "incomplete") return "red" as const;
  return "slate" as const;
}

export function statusTone(status: string | null | undefined) {
  const normalized = (status ?? "").toLowerCase();
  if (normalized === "online" || normalized === "paired" || normalized === "deployed" || normalized === "success") return "green" as const;
  if (normalized === "training" || normalized === "pending" || normalized === "offline") return "amber" as const;
  if (normalized === "inactive" || normalized === "failed" || normalized === "archived") return "red" as const;
  return "slate" as const;
}

export function readingMeaning(category: string | null | undefined) {
  const normalized = (category ?? "").toLowerCase();
  if (!normalized) return "No model category is available for this reading yet.";
  if (normalized.includes("normal")) return "This estimate sits in the expected range for the current model context.";
  if (normalized.includes("pre") || normalized.includes("elevated")) return "This estimate deserves attention, especially if it repeats across future readings.";
  if (normalized.includes("high") || normalized.includes("diabetes")) return "This estimate is outside the usual target context. Consider a fresh check and your usual care guidance.";
  if (normalized.includes("low") || normalized.includes("hypo")) return "This estimate reads low for the model context. Recheck if the reading does not match how you feel.";
  return "Use this category together with freshness, device state, and model confidence.";
}
