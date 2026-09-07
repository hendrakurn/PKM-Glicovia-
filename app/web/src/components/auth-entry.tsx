"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle, Eye, EyeSlash, LockKey, Pulse, UserCircle, WarningCircle } from "@phosphor-icons/react";
import { api } from "@/lib/api/client";
import { formatTimestamp } from "@/lib/utils";
import { Field, GlicoBadge, GlicoButton, GlicoPanel, RowStatus } from "@/components/glicovia-ui";
import { useAuth } from "@/components/auth-provider";

type AuthMode = "login" | "register";

export function AuthEntry() {
  const router = useRouter();
  const { signIn, status } = useAuth();
  const [mode, setMode] = useState<AuthMode>("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<{ ok: boolean; timestamp?: string } | null>(null);

  const passwordScore = useMemo(() => {
    let score = 0;
    if (password.length >= 8) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    return score;
  }, [password]);

  useEffect(() => {
    if (status === "authenticated") router.replace("/overview");
  }, [router, status]);

  useEffect(() => {
    let active = true;
    void api
      .health()
      .then((result) => {
        if (active) setHealth({ ok: result.status === "ok", timestamp: result.timestamp });
      })
      .catch(() => {
        if (active) setHealth({ ok: false });
      });
    return () => {
      active = false;
    };
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (!email.trim() || !password) {
      setError("Email and password are required.");
      return;
    }

    if (mode === "register" && password.length < 8) {
      setError("Use at least 8 characters for the password.");
      return;
    }

    try {
      setSubmitting(true);
      const response =
        mode === "login"
          ? await api.login({ email: email.trim(), password })
          : await api.register({ email: email.trim(), password, fullName: fullName.trim() || undefined });
      signIn(response);
      router.replace("/overview");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Authentication failed.");
    } finally {
      setSubmitting(false);
    }
  }

  const scoreLabel = ["Very weak", "Basic", "Better", "Strong", "Clinical grade"][passwordScore] ?? "Basic";

  return (
    <main className="min-h-[100dvh] px-4 py-5 sm:px-6 lg:px-8">
      <div className="mx-auto grid min-h-[calc(100dvh-2.5rem)] w-full max-w-[1360px] gap-5 lg:grid-cols-[minmax(0,1.08fr)_480px]">
        <section className="glico-panel reveal-up order-2 flex min-h-[560px] lg:order-none flex-col overflow-hidden bg-[color:var(--canvas)]">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b-2 border-[color:var(--line)] p-5">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-[8px] border-2 border-[color:var(--line)] bg-[color:var(--mint)] font-black">GV</div>
              <div>
                <p className="text-lg font-black leading-none text-[color:var(--ink)]">GLICOVIA Express</p>
                <p className="mt-1 text-xs font-bold text-[color:var(--ink-muted)]">Saliva glucose monitoring</p>
              </div>
            </div>
            {health ? (
              <RowStatus tone={health.ok ? "green" : "red"} label={health.ok ? `API ${formatTimestamp(health.timestamp)}` : "API offline"} />
            ) : (
              <RowStatus tone="slate" label="Checking API" />
            )}
          </div>

          <div className="grid flex-1 gap-0 lg:grid-cols-[minmax(0,1fr)_300px]">
            <div className="flex flex-col justify-between gap-8 p-6 sm:p-8 lg:p-10">
              <div className="max-w-3xl space-y-5">
                <GlicoBadge tone="butter">
                  <Pulse size={14} weight="bold" />
                  Patient-first monitor
                </GlicoBadge>
                <h1 className="max-w-3xl text-5xl font-black leading-[0.98] text-[color:var(--ink)] sm:text-6xl lg:text-7xl">
                  Understand the latest saliva glucose signal at a glance.
                </h1>
                <p className="max-w-2xl text-lg leading-8 text-[color:var(--ink-muted)]">
                  GLICOVIA Express brings current readings, device state, freshness, and model context into one calm health view.
                </p>
              </div>

              <div className="grid gap-3 md:grid-cols-3">
                <div className="soft-row bg-[color:var(--mint)] p-4">
                  <p className="label-text">Reading</p>
                  <p className="mt-3 text-2xl font-black text-[color:var(--ink)]">Current signal</p>
                </div>
                <div className="soft-row bg-[color:var(--sky)] p-4">
                  <p className="label-text">Trust</p>
                  <p className="mt-3 text-2xl font-black text-[color:var(--ink)]">Model context</p>
                </div>
                <div className="soft-row bg-[color:var(--butter)] p-4">
                  <p className="label-text">Device</p>
                  <p className="mt-3 text-2xl font-black text-[color:var(--ink)]">Freshness</p>
                </div>
              </div>
            </div>

            <div className="border-t-2 border-[color:var(--line)] bg-[color:var(--surface-soft)] p-5 lg:border-l-2 lg:border-t-0">
              <div className="grid gap-4">
                <div className="ink-panel p-5">
                  <p className="label-text text-[color:var(--butter)]">Primary view</p>
                  <p className="mt-3 text-3xl font-black leading-tight">Today, then detail.</p>
                  <p className="mt-3 text-sm leading-6 text-[color:var(--mint)]">The dashboard leads with meaning before raw rows.</p>
                </div>
                <div className="soft-row bg-[color:var(--canvas)] p-5">
                  <p className="label-text">Reviewer layer</p>
                  <p className="mt-3 text-sm font-bold leading-6 text-[color:var(--ink-muted)]">Predictions, models, confidence, and IDs stay visible for audit work.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <GlicoPanel className="reveal-up order-1 p-5 sm:p-6 lg:order-none" style={{ animationDelay: "90ms" }}>
          <div className="mb-5 flex rounded-[8px] border-2 border-[color:var(--line)] bg-[color:var(--surface-soft)] p-1">
            {(["login", "register"] as const).map((item) => (
              <button
                key={item}
                type="button"
                aria-pressed={mode === item}
                className={`min-h-10 flex-1 rounded-[6px] px-3 text-sm font-black capitalize transition ${mode === item ? "bg-[color:var(--canvas)] shadow-[2px_2px_0_var(--line)]" : "text-[color:var(--ink-muted)]"}`}
                onClick={() => {
                  setMode(item);
                  setError(null);
                }}
              >
                {item}
              </button>
            ))}
          </div>

          <form onSubmit={onSubmit} className="grid gap-4">
            {mode === "register" ? (
              <Field label="Full name">
                <div className="relative">
                  <UserCircle className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[color:var(--ink-muted)]" size={20} weight="bold" />
                  <input className="glico-input pl-10" value={fullName} onChange={(event) => setFullName(event.target.value)} autoComplete="name" placeholder="Optional display name" />
                </div>
              </Field>
            ) : null}

            <Field label="Email">
              <input className="glico-input" type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" placeholder="you@example.com" />
            </Field>

            <Field label="Password">
              <div className="relative">
                <LockKey className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[color:var(--ink-muted)]" size={19} weight="bold" />
                <input
                  className="glico-input pl-10 pr-12"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete={mode === "login" ? "current-password" : "new-password"}
                  placeholder={mode === "login" ? "Your password" : "At least 8 characters"}
                />
                <button
                  type="button"
                  className="absolute right-2 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-[8px] text-[color:var(--ink-muted)] hover:bg-[color:var(--surface-soft)]"
                  onClick={() => setShowPassword((current) => !current)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeSlash size={20} weight="bold" /> : <Eye size={20} weight="bold" />}
                </button>
              </div>
            </Field>

            {mode === "register" ? (
              <div className="grid gap-2">
                <div className="h-3 overflow-hidden rounded-full border-2 border-[color:var(--line)] bg-[color:var(--surface-soft)]">
                  <div className="h-full bg-[color:var(--mint)] transition-all" style={{ width: `${Math.max(12, passwordScore * 25)}%` }} />
                </div>
                <p className="text-sm font-bold text-[color:var(--ink-muted)]">Password strength: {scoreLabel}</p>
              </div>
            ) : null}

            {error ? (
              <div className="soft-row bg-[color:var(--coral)] p-3 text-sm font-bold text-[color:var(--ink)]" role="alert">
                <WarningCircle className="mr-2 inline" size={18} weight="bold" />
                {error}
              </div>
            ) : null}

            <GlicoButton type="submit" variant="ink" size="lg" className="mt-1 w-full" disabled={submitting || status === "booting"}>
              {submitting ? "Working" : mode === "login" ? "Enter dashboard" : "Create account"}
              <CheckCircle size={20} weight="bold" />
            </GlicoButton>
          </form>
        </GlicoPanel>
      </div>
    </main>
  );
}
