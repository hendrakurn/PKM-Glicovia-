import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

const buttonBase =
  "inline-flex items-center justify-center gap-2 rounded-[10px] px-4 py-2 text-sm font-medium transition-all duration-200 active:translate-y-px disabled:pointer-events-none disabled:opacity-50";

export function buttonClasses(variant: "primary" | "secondary" | "ghost" = "secondary") {
  if (variant === "primary") {
    return cn(
      buttonBase,
      "border border-[color:var(--green)] bg-[color:var(--green)] text-[color:var(--canvas)] shadow-[0_8px_24px_rgba(7,102,83,0.14)] hover:bg-[color:var(--ink)]"
    );
  }

  if (variant === "ghost") {
    return cn(buttonBase, "text-[color:var(--text-secondary)] hover:bg-[color:var(--surface-elevated)]");
  }

  return cn(
    buttonBase,
    "border border-[color:var(--border)] bg-[color:var(--surface)] text-[color:var(--text-primary)] hover:bg-[color:var(--surface-elevated)]"
  );
}

export function Panel({ className, children }: { className?: string; children: ReactNode }) {
  return <section className={cn("panel", className)}>{children}</section>;
}

export function SectionHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div className="space-y-2">
        {eyebrow ? (
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--text-muted)]">
            {eyebrow}
          </p>
        ) : null}
        <h1 className="text-3xl font-semibold tracking-tight text-[color:var(--text-primary)] md:text-4xl">
          {title}
        </h1>
        {description ? (
          <p className="max-w-3xl text-sm leading-6 text-[color:var(--text-secondary)] md:text-base">
            {description}
          </p>
        ) : null}
      </div>
      {action ? <div className="flex flex-wrap items-center gap-3">{action}</div> : null}
    </div>
  );
}

export function Badge({
  children,
  tone = "slate",
}: {
  children: ReactNode;
  tone?: "slate" | "emerald" | "amber" | "red" | "blue" | "indigo";
}) {
  const toneClasses = {
    slate: "border-[color:var(--green)] bg-[color:var(--surface-soft)] text-[color:var(--ink)]",
    emerald: "border-[color:var(--green)] bg-[color:var(--mint)] text-[color:var(--green)]",
    amber: "border-[color:var(--amber)] bg-[color:var(--butter)] text-[color:var(--ink)]",
    red: "border-[color:var(--ink)] bg-[color:var(--butter)] text-[color:var(--ink)]",
    blue: "border-[color:var(--blue)] bg-[color:var(--mint)] text-[color:var(--blue)]",
    indigo: "border-[color:var(--green)] bg-[color:var(--surface-soft)] text-[color:var(--green)]",
  } as const;

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium",
        toneClasses[tone]
      )}
    >
      {children}
    </span>
  );
}

export function StatusDot({
  tone = "emerald",
  label,
}: {
  tone?: "emerald" | "amber" | "red" | "slate" | "blue";
  label: string;
}) {
  const dot = {
    emerald: "bg-[color:var(--green)]",
    amber: "bg-[color:var(--amber)]",
    red: "bg-[color:var(--red)]",
    slate: "bg-[color:var(--ink-soft)]",
    blue: "bg-[color:var(--blue)]",
  } as const;

  return (
    <div className="flex items-center gap-2 text-sm text-[color:var(--text-secondary)]">
      <span className={cn("h-2.5 w-2.5 rounded-full", dot[tone])} />
      <span>{label}</span>
    </div>
  );
}

export function StatCard({
  label,
  value,
  helper,
  delta,
  icon,
  tone = "emerald",
}: {
  label: string;
  value: string;
  helper?: string;
  delta?: string;
  icon?: ReactNode;
  tone?: "emerald" | "teal" | "blue" | "amber" | "slate";
}) {
  const toneClasses = {
    emerald: "text-[color:var(--green)] bg-[color:var(--mint)] border-[color:var(--green)]",
    teal: "text-[color:var(--teal)] bg-[color:var(--mint)] border-[color:var(--teal)]",
    blue: "text-[color:var(--blue)] bg-[color:var(--mint)] border-[color:var(--blue)]",
    amber: "text-[color:var(--ink)] bg-[color:var(--butter)] border-[color:var(--amber)]",
    slate: "text-[color:var(--ink-muted)] bg-[color:var(--surface-soft)] border-[color:var(--green)]",
  } as const;

  return (
    <Panel className="flex flex-col gap-4 p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-[color:var(--text-secondary)]">{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-tight text-[color:var(--text-primary)]">
            {value}
          </p>
        </div>
        {icon ? (
          <div className={cn("flex h-10 w-10 items-center justify-center rounded-[12px] border", toneClasses[tone])}>
            {icon}
          </div>
        ) : null}
      </div>
      <div className="flex items-center justify-between gap-3 text-sm text-[color:var(--text-secondary)]">
        {helper ? <span>{helper}</span> : <span className="text-transparent">.</span>}
        {delta ? <span className="font-medium text-[color:var(--text-primary)]">{delta}</span> : null}
      </div>
    </Panel>
  );
}

export function EmptyState({
  title,
  description,
  action,
  icon,
}: {
  title: string;
  description: string;
  action?: ReactNode;
  icon?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-start gap-4 rounded-[14px] border border-dashed border-[color:var(--border)] bg-[color:var(--surface-elevated)] p-6 text-left">
      <div className="flex h-12 w-12 items-center justify-center rounded-[14px] border border-[color:var(--border)] bg-[color:var(--surface)] text-[color:var(--text-secondary)]">
        {icon ?? <span className="h-3.5 w-3.5 rounded-full bg-[color:var(--green)]" />}
      </div>
      <div className="space-y-1">
        <h3 className="text-base font-semibold text-[color:var(--text-primary)]">{title}</h3>
        <p className="max-w-xl text-sm leading-6 text-[color:var(--text-secondary)]">{description}</p>
      </div>
      {action ? action : null}
    </div>
  );
}

export function SkeletonBlock({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-[12px] bg-[color:var(--surface-soft)]", className)} />;
}

export function LoadingCard() {
  return (
    <Panel className="space-y-4 p-5">
      <div className="flex items-center justify-between gap-4">
        <div className="space-y-2">
          <SkeletonBlock className="h-3 w-24" />
          <SkeletonBlock className="h-8 w-32" />
        </div>
        <SkeletonBlock className="h-10 w-10 rounded-[12px]" />
      </div>
      <SkeletonBlock className="h-4 w-full" />
      <SkeletonBlock className="h-4 w-4/5" />
    </Panel>
  );
}

export function ToastPill({
  title,
  description,
  tone = "emerald",
}: {
  title: string;
  description?: string;
  tone?: "emerald" | "amber" | "red" | "blue";
}) {
  const accent = {
    emerald: "border-[color:var(--green)] bg-[color:var(--mint)] text-[color:var(--green)]",
    amber: "border-[color:var(--amber)] bg-[color:var(--butter)] text-[color:var(--ink)]",
    red: "border-[color:var(--ink)] bg-[color:var(--butter)] text-[color:var(--ink)]",
    blue: "border-[color:var(--blue)] bg-[color:var(--mint)] text-[color:var(--blue)]",
  } as const;

  return (
    <div className={cn("rounded-[14px] border px-4 py-3 shadow-[0_12px_30px_rgba(6,35,29,0.08)]", accent[tone])}>
      <div className="flex items-start gap-3">
        <span className="mt-1 h-3 w-3 rounded-full bg-current opacity-80" />
        <div>
          <p className="text-sm font-medium">{title}</p>
          {description ? <p className="text-sm text-current/75">{description}</p> : null}
        </div>
      </div>
    </div>
  );
}

export function GlyphMark({
  label,
  tone = "emerald",
  className,
}: {
  label: string;
  tone?: "emerald" | "teal" | "blue" | "amber" | "slate" | "red";
  className?: string;
}) {
  const tones = {
    emerald: "border-[color:var(--green)] bg-[color:var(--mint)] text-[color:var(--green)]",
    teal: "border-[color:var(--teal)] bg-[color:var(--mint)] text-[color:var(--teal)]",
    blue: "border-[color:var(--blue)] bg-[color:var(--mint)] text-[color:var(--blue)]",
    amber: "border-[color:var(--amber)] bg-[color:var(--butter)] text-[color:var(--ink)]",
    slate: "border-[color:var(--green)] bg-[color:var(--surface-soft)] text-[color:var(--ink-muted)]",
    red: "border-[color:var(--ink)] bg-[color:var(--butter)] text-[color:var(--ink)]",
  } as const;

  return (
    <div className={cn("flex h-10 w-10 items-center justify-center rounded-[12px] border text-sm font-semibold", tones[tone], className)}>
      {label}
    </div>
  );
}

export function MetricChip({ label, value, tone = "emerald" }: { label: string; value: string; tone?: "emerald" | "amber" | "red" | "blue" }) {
  const tones = {
    emerald: "border-[color:var(--green)] bg-[color:var(--mint)] text-[color:var(--green)]",
    amber: "border-[color:var(--amber)] bg-[color:var(--butter)] text-[color:var(--ink)]",
    red: "border-[color:var(--ink)] bg-[color:var(--butter)] text-[color:var(--ink)]",
    blue: "border-[color:var(--blue)] bg-[color:var(--mint)] text-[color:var(--blue)]",
  } as const;

  return (
    <div className={cn("flex items-center justify-between rounded-full border px-3 py-1.5 text-xs", tones[tone])}>
      <span className="font-medium">{label}</span>
      <span className="font-mono text-[11px]">{value}</span>
    </div>
  );
}

export function MiniField({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[12px] border border-[color:var(--border)] bg-[color:var(--surface-elevated)] p-3">
      <p className="text-[11px] uppercase tracking-[0.16em] text-[color:var(--text-muted)]">{label}</p>
      <p className="mt-1 text-sm font-medium text-[color:var(--text-primary)]">{value}</p>
    </div>
  );
}

export function InlineStat({ label, value, helper }: { label: string; value: string; helper?: string }) {
  return (
    <div className="rounded-[12px] border border-[color:var(--border)] bg-[color:var(--surface)] p-4">
      <p className="text-xs uppercase tracking-[0.14em] text-[color:var(--text-muted)]">{label}</p>
      <p className="mt-2 text-2xl font-semibold tracking-tight text-[color:var(--text-primary)]">{value}</p>
      {helper ? <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{helper}</p> : null}
    </div>
  );
}
