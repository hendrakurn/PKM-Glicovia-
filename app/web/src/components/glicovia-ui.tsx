import { cn } from "@/lib/utils";
import type { ButtonHTMLAttributes, HTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger" | "ink";
type ButtonSize = "sm" | "md" | "lg" | "icon";
export type GlicoviaTone = "slate" | "green" | "amber" | "red" | "blue" | "mint" | "sky" | "butter" | "coral" | "rose" | "ink";

const buttonBase =
  "inline-flex shrink-0 items-center justify-center gap-2 rounded-[8px] border-2 border-[color:var(--line)] font-extrabold leading-none transition duration-150 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-[color:var(--mint)] disabled:pointer-events-none disabled:opacity-50 active:translate-x-[2px] active:translate-y-[2px]";

export function glicoButtonClasses(variant: ButtonVariant = "secondary", size: ButtonSize = "md") {
  const variants: Record<ButtonVariant, string> = {
    primary: "bg-[color:var(--mint)] text-[color:var(--ink)] shadow-[3px_3px_0_var(--line)] hover:bg-[#bfe0cc]",
    secondary: "bg-[color:var(--canvas)] text-[color:var(--ink)] shadow-[3px_3px_0_var(--line)] hover:bg-white",
    ghost: "border-transparent bg-transparent text-[color:var(--ink-muted)] hover:bg-[color:var(--surface-soft)]",
    danger: "bg-[color:var(--coral)] text-[color:var(--ink)] shadow-[3px_3px_0_var(--line)] hover:bg-[#eaa690]",
    ink: "bg-[color:var(--ink)] text-[color:var(--canvas)] shadow-[3px_3px_0_var(--line)] hover:bg-[#2a241d]",
  };
  const sizes: Record<ButtonSize, string> = {
    sm: "min-h-9 px-3 py-2 text-xs",
    md: "min-h-11 px-4 py-3 text-sm",
    lg: "min-h-12 px-5 py-3.5 text-base",
    icon: "h-11 w-11 p-0",
  };
  return cn(buttonBase, variants[variant], sizes[size]);
}

export function GlicoButton({ className, variant = "secondary", size = "md", ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: ButtonVariant; size?: ButtonSize }) {
  return <button className={cn(glicoButtonClasses(variant, size), className)} {...props} />;
}

export function GlicoPanel({ className, children, ...props }: HTMLAttributes<HTMLElement>) {
  return <section className={cn("glico-panel", className)} {...props}>{children}</section>;
}

export function PageHeader({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div className="max-w-4xl space-y-2">
        {eyebrow ? <p className="label-text">{eyebrow}</p> : null}
        <h1 className="text-3xl font-black leading-[1.02] text-[color:var(--ink)] sm:text-4xl lg:text-5xl">{title}</h1>
        {description ? <p className="max-w-3xl text-base leading-7 text-[color:var(--ink-muted)]">{description}</p> : null}
      </div>
      {action ? <div className="flex flex-wrap items-center gap-3">{action}</div> : null}
    </div>
  );
}

export function GlicoBadge({ children, tone = "slate", className }: { children: ReactNode; tone?: GlicoviaTone; className?: string }) {
  const toneClasses: Record<GlicoviaTone, string> = {
    slate: "bg-[color:var(--surface-soft)] text-[color:var(--ink)]",
    green: "bg-[color:var(--mint)] text-[color:var(--ink)]",
    amber: "bg-[color:var(--butter)] text-[color:var(--ink)]",
    red: "bg-[color:var(--coral)] text-[color:var(--ink)]",
    blue: "bg-[color:var(--sky)] text-[color:var(--ink)]",
    mint: "bg-[color:var(--mint)] text-[color:var(--ink)]",
    sky: "bg-[color:var(--sky)] text-[color:var(--ink)]",
    butter: "bg-[color:var(--butter)] text-[color:var(--ink)]",
    coral: "bg-[color:var(--coral)] text-[color:var(--ink)]",
    rose: "bg-[color:var(--rose)] text-[color:var(--ink)]",
    ink: "bg-[color:var(--ink)] text-[color:var(--canvas)]",
  };
  return (
    <span className={cn("inline-flex max-w-full items-center gap-1.5 rounded-[999px] border-2 border-[color:var(--line)] px-3 py-1 text-xs font-extrabold", toneClasses[tone], className)}>
      {children}
    </span>
  );
}

export function Field({ label, error, children, hint }: { label: string; error?: string | null; hint?: string; children: ReactNode }) {
  return (
    <label className="grid gap-2">
      <span className="label-text">{label}</span>
      {children}
      {hint && !error ? <span className="text-sm leading-6 text-[color:var(--ink-muted)]">{hint}</span> : null}
      {error ? <span className="text-sm font-bold text-[color:var(--red)]">{error}</span> : null}
    </label>
  );
}

export function KeyValue({ label, value, mono = false }: { label: string; value: ReactNode; mono?: boolean }) {
  return (
    <div className="grid gap-1 border-t-2 border-[color:var(--line)] py-3 first:border-t-0 first:pt-0 last:pb-0">
      <p className="label-text text-[0.7rem]">{label}</p>
      <div className={cn("min-w-0 break-words text-sm font-bold leading-6 text-[color:var(--ink)]", mono && "font-mono text-xs")}>{value}</div>
    </div>
  );
}

export function StateBlock({ title, description, action, tone = "sky", icon }: { title: string; description: string; action?: ReactNode; tone?: "sky" | "mint" | "butter" | "coral" | "rose" | "slate"; icon?: ReactNode }) {
  const tones = {
    sky: "bg-[color:var(--sky)]",
    mint: "bg-[color:var(--mint)]",
    butter: "bg-[color:var(--butter)]",
    coral: "bg-[color:var(--coral)]",
    rose: "bg-[color:var(--rose)]",
    slate: "bg-[color:var(--surface-soft)]",
  };
  return (
    <div className={cn("soft-row p-5", tones[tone])}>
      <div className="flex items-start gap-4">
        {icon ? <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-[8px] border-2 border-[color:var(--line)] bg-[color:var(--canvas)]">{icon}</div> : null}
        <div className="min-w-0 space-y-2">
          <h3 className="text-lg font-black leading-tight text-[color:var(--ink)]">{title}</h3>
          <p className="text-sm leading-6 text-[color:var(--ink-muted)]">{description}</p>
          {action ? <div className="pt-2">{action}</div> : null}
        </div>
      </div>
    </div>
  );
}

export function SkeletonBlock({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-[8px] border-2 border-[color:var(--line)] bg-[color:var(--surface-soft)]", className)} />;
}

export function Heartbeat({ label = "Fresh signal" }: { label?: string }) {
  return (
    <div className="inline-flex items-center gap-2 rounded-[999px] border-2 border-[color:var(--line)] bg-[color:var(--canvas)] px-3 py-1.5 text-xs font-extrabold text-[color:var(--ink)]">
      <span className="relative h-2.5 w-8 overflow-hidden rounded-full bg-[color:var(--surface-soft)]" aria-hidden="true">
        <span className="pulse-line absolute left-0 top-0 h-full w-full rounded-full bg-[color:var(--green)]" />
      </span>
      {label}
    </div>
  );
}

export function RowStatus({ tone = "green", label }: { tone?: "green" | "amber" | "red" | "slate" | "blue"; label: string }) {
  const dot = {
    green: "bg-[color:var(--green)]",
    amber: "bg-[color:var(--amber)]",
    red: "bg-[color:var(--red)]",
    slate: "bg-[color:var(--ink-soft)]",
    blue: "bg-[color:var(--blue)]",
  } as const;

  return (
    <span className="inline-flex min-w-0 items-center gap-2 text-sm font-bold text-[color:var(--ink-muted)]">
      <span className={cn("h-2.5 w-2.5 shrink-0 rounded-full", dot[tone])} />
      <span className="min-w-0 truncate">{label}</span>
    </span>
  );
}
