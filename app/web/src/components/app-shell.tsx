"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import type { Icon } from "@phosphor-icons/react";
import { Brain, ChartLine, DeviceMobile, House, Pulse, SignOut, Wrench } from "@phosphor-icons/react";
import { api } from "@/lib/api/client";
import { cn, formatTimestamp } from "@/lib/utils";
import { GlicoBadge, GlicoButton, Heartbeat, RowStatus, SkeletonBlock } from "@/components/glicovia-ui";
import { useAuth } from "@/components/auth-provider";

const navItems: Array<{ href: string; label: string; icon: Icon; tone: string }> = [
  { href: "/overview", label: "Overview", icon: House, tone: "bg-[color:var(--mint)]" },
  { href: "/readings", label: "Readings", icon: ChartLine, tone: "bg-[color:var(--sky)]" },
  { href: "/devices", label: "Devices", icon: DeviceMobile, tone: "bg-[color:var(--butter)]" },
  { href: "/predictions", label: "Models", icon: Brain, tone: "bg-[color:var(--rose)]" },
  { href: "/operator", label: "Operator", icon: Wrench, tone: "bg-[color:var(--coral)]" },
];

export function AppShell({ children }: { children: ReactNode }) {
  const { profile, signOut, status } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [health, setHealth] = useState<{ ok: boolean; timestamp?: string } | null>(null);

  useEffect(() => {
    if (status === "unauthenticated") router.replace("/");
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

  if (status === "booting" || !profile) {
    return <ShellSkeleton />;
  }

  const displayName = profile.subject.display_name || profile.user.full_name || profile.user.email;

  return (
    <div className="page-fade min-h-[100dvh]">
      <div className="grid min-h-[100dvh] xl:grid-cols-[292px_minmax(0,1fr)]">
        <aside className="sticky top-0 hidden h-[100dvh] border-r-2 border-[color:var(--line)] bg-[color:var(--canvas)] xl:flex xl:flex-col">
          <div className="border-b-2 border-[color:var(--line)] p-5">
            <Link href="/overview" className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-[8px] border-2 border-[color:var(--line)] bg-[color:var(--mint)] font-black">GV</div>
              <div>
                <p className="text-lg font-black leading-none text-[color:var(--ink)]">GLICOVIA</p>
                <p className="mt-1 text-xs font-bold text-[color:var(--ink-muted)]">Express monitor</p>
              </div>
            </Link>
          </div>

          <nav className="flex-1 space-y-2 p-4" aria-label="Primary navigation">
            {navItems.map((item) => {
              const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
              const IconComponent = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "group flex items-center gap-3 rounded-[8px] border-2 border-transparent px-3 py-3 text-sm font-black text-[color:var(--ink-muted)] transition",
                    active
                      ? "border-[color:var(--line)] bg-[color:var(--canvas)] text-[color:var(--ink)] shadow-[3px_3px_0_var(--line)]"
                      : "hover:border-[color:var(--line)] hover:bg-white hover:text-[color:var(--ink)]"
                  )}
                >
                  <span className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-[8px] border-2 border-[color:var(--line)]", item.tone)}>
                    <IconComponent size={20} weight={active ? "fill" : "bold"} />
                  </span>
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="space-y-4 border-t-2 border-[color:var(--line)] p-4">
            <div className="soft-row bg-[color:var(--surface-soft)] p-4">
              <p className="label-text">Signed in subject</p>
              <p className="mt-2 truncate text-sm font-black text-[color:var(--ink)]">{displayName}</p>
              <p className="mt-1 truncate font-mono text-xs text-[color:var(--ink-muted)]">{profile.subject.subject_code}</p>
            </div>
            <GlicoButton
              type="button"
              variant="ghost"
              className="w-full justify-start"
              onClick={() => {
                signOut();
                router.replace("/");
              }}
            >
              <SignOut size={18} weight="bold" />
              Sign out
            </GlicoButton>
          </div>
        </aside>

        <div className="min-w-0">
          <header className="sticky top-0 z-30 border-b-2 border-[color:var(--line)] bg-[color:var(--background)]/95 backdrop-blur supports-[backdrop-filter]:bg-[color:var(--background)]/90">
            <div className="mx-auto flex w-full max-w-[1500px] flex-col gap-3 px-4 py-3 lg:px-6">
              <div className="flex items-center justify-between gap-3">
                <Link href="/overview" className="flex min-w-0 items-center gap-3 xl:hidden">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[8px] border-2 border-[color:var(--line)] bg-[color:var(--mint)] text-sm font-black">GV</span>
                  <span className="truncate text-sm font-black text-[color:var(--ink)]">GLICOVIA Express</span>
                </Link>

                <div className="hidden min-w-0 items-center gap-3 xl:flex">
                  <Heartbeat label="Session active" />
                  {health ? (
                    <RowStatus tone={health.ok ? "green" : "red"} label={health.ok ? `API ${formatTimestamp(health.timestamp)}` : "API offline"} />
                  ) : (
                    <RowStatus tone="slate" label="Checking API" />
                  )}
                </div>

                <div className="ml-auto flex items-center gap-2">
                  <GlicoBadge tone="sky" className="hidden sm:inline-flex">
                    <Pulse size={14} weight="bold" />
                    {profile.user.role}
                  </GlicoBadge>
                  <GlicoButton
                    type="button"
                    variant="ghost"
                    size="icon"
                    aria-label="Sign out"
                    onClick={() => {
                      signOut();
                      router.replace("/");
                    }}
                  >
                    <SignOut size={19} weight="bold" />
                  </GlicoButton>
                </div>
              </div>

              <nav className="flex gap-2 overflow-x-auto pb-1 xl:hidden" aria-label="Mobile navigation">
                {navItems.map((item) => {
                  const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
                  const IconComponent = item.icon;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={cn(
                        "inline-flex min-h-10 shrink-0 items-center gap-2 rounded-[8px] border-2 border-[color:var(--line)] px-3 text-xs font-black",
                        active ? "bg-[color:var(--mint)] text-[color:var(--ink)]" : "bg-[color:var(--canvas)] text-[color:var(--ink-muted)]"
                      )}
                    >
                      <IconComponent size={16} weight="bold" />
                      {item.label}
                    </Link>
                  );
                })}
              </nav>
            </div>
          </header>

          <main className="mx-auto flex w-full max-w-[1500px] flex-col gap-7 px-4 py-6 lg:px-6 lg:py-8">{children}</main>
        </div>
      </div>
    </div>
  );
}

function ShellSkeleton() {
  return (
    <div className="min-h-[100dvh] p-4 lg:p-8">
      <div className="mx-auto grid max-w-[1200px] gap-5 lg:grid-cols-[260px_minmax(0,1fr)]">
        <SkeletonBlock className="hidden h-[calc(100dvh-4rem)] lg:block" />
        <div className="space-y-5">
          <SkeletonBlock className="h-16" />
          <div className="grid gap-5 md:grid-cols-3">
            <SkeletonBlock className="h-40" />
            <SkeletonBlock className="h-40" />
            <SkeletonBlock className="h-40" />
          </div>
          <SkeletonBlock className="h-96" />
        </div>
      </div>
    </div>
  );
}
