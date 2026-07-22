import Link from "next/link";
import { Badge, buttonClasses } from "@/components/ui";
import { navLinks } from "@/components/top-bar-links";

export function TopBar() {
  return (
    <header className="sticky top-0 z-20 border-b border-[color:var(--border)] bg-[color:var(--background)]/96 backdrop-blur supports-[backdrop-filter]:bg-[color:var(--background)]/92">
      <div className="mx-auto flex w-full max-w-[1540px] flex-col gap-3 px-4 py-3 lg:px-6">
        <div className="flex items-center justify-between gap-3">
          <div className="flex min-w-0 flex-1 items-center gap-3">
            <div className="flex h-10 w-full max-w-[520px] items-center gap-3 rounded-[12px] border border-[color:var(--border)] bg-[color:var(--surface)] px-3 text-[color:var(--text-muted)] shadow-[0_1px_2px_rgba(16,32,51,0.04)]">
              <span className="text-base leading-none">⌕</span>
              <span className="truncate text-sm">Search subject, reading, or model version</span>
            </div>
            <div className="hidden lg:flex items-center gap-2">
              <Badge tone="emerald">
                <span className="inline-flex items-center gap-1.5">
                  <span className="text-[11px] leading-none">●</span>
                  Live device online
                </span>
              </Badge>
              <Badge tone="blue">Last sync 32 s ago</Badge>
            </div>
          </div>
          <div className="hidden items-center gap-2 md:flex">
            <Link href="/ingestion" className={buttonClasses("secondary")}>
              <span className="text-sm leading-none">⇪</span>
              Ingest sample
            </Link>
            <Link href="/analytics" className={buttonClasses("primary")}>
              <span className="text-sm leading-none">↗</span>
              Export report
            </Link>
          </div>
        </div>

        <div className="flex items-center gap-2 overflow-x-auto pb-1 xl:hidden">
          {navLinks.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="whitespace-nowrap rounded-full border border-[color:var(--border)] bg-[color:var(--surface)] px-3 py-1.5 text-sm font-medium text-[color:var(--text-secondary)]"
            >
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </header>
  );
}
