"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Badge, GlyphMark, StatusDot } from "@/components/ui";

const navItems = [
  { href: "/", label: "Dashboard", glyph: "D" },
  { href: "/subjects", label: "Subjects", glyph: "S" },
  { href: "/ingestion", label: "Data Ingestion", glyph: "I" },
  { href: "/predictions", label: "Predictions", glyph: "P" },
  { href: "/analytics", label: "Analytics", glyph: "A" },
  { href: "/settings", label: "Settings", glyph: "G" },
];

export function SidebarNav() {
  const pathname = usePathname();

  return (
    <aside className="sticky top-0 hidden h-[100dvh] flex-col border-r border-[color:var(--border)] bg-[color:var(--surface)] xl:flex">
      <div className="flex h-16 items-center gap-3 border-b border-[color:var(--border)] px-5">
        <GlyphMark label="G" tone="teal" />
        <div>
          <p className="text-sm font-semibold text-[color:var(--text-primary)]">GLICOVIA</p>
          <p className="text-xs text-[color:var(--text-muted)]">Clinical monitoring suite</p>
        </div>
      </div>

      <nav className="flex-1 space-y-2 px-3 py-4">
        {navItems.map((item) => {
          const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-[12px] px-3 py-2.5 text-sm transition-colors",
                active
                  ? "bg-emerald-50 text-emerald-800 ring-1 ring-emerald-200"
                  : "text-[color:var(--text-secondary)] hover:bg-[color:var(--surface-elevated)] hover:text-[color:var(--text-primary)]"
              )}
            >
              <GlyphMark label={item.glyph} tone={active ? "teal" : "slate"} className="h-8 w-8 text-[10px]" />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="space-y-4 border-t border-[color:var(--border)] p-4">
        <div className="rounded-[14px] border border-[color:var(--border)] bg-[color:var(--surface-elevated)] p-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-medium text-[color:var(--text-primary)]">Device status</p>
              <p className="mt-1 text-xs text-[color:var(--text-secondary)]">Prototype bridge connected</p>
            </div>
            <Badge tone="emerald">Online</Badge>
          </div>
          <div className="mt-4 space-y-3">
            <StatusDot tone="emerald" label="Latency 180 ms" />
            <StatusDot tone="blue" label="Queue 1 packet" />
          </div>
        </div>
      </div>
    </aside>
  );
}
