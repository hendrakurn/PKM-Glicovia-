import { Panel } from "@/components/ui";

export function BarChartCard({
  title,
  description,
  items,
}: {
  title: string;
  description?: string;
  items: Array<{ label: string; value: number; color?: string; helper?: string }>;
}) {
  const max = Math.max(...items.map((item) => item.value), 1);

  return (
    <Panel className="p-5">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-[color:var(--text-primary)]">{title}</h2>
        {description ? <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{description}</p> : null}
      </div>
      <div className="space-y-4">
        {items.map((item) => {
          const width = `${Math.max((item.value / max) * 100, 8)}%`;
          return (
            <div key={item.label} className="space-y-1.5">
              <div className="flex items-center justify-between gap-4 text-sm">
                <span className="font-medium text-[color:var(--text-primary)]">{item.label}</span>
                <span className="font-mono text-[color:var(--text-muted)]">{item.value}</span>
              </div>
              <div className="h-2 rounded-full bg-[color:var(--surface-soft)]">
                <div
                  className="h-2 rounded-full"
                  style={{
                    width,
                    backgroundColor: item.color ?? "#076653",
                  }}
                />
              </div>
              {item.helper ? <p className="text-xs text-[color:var(--text-muted)]">{item.helper}</p> : null}
            </div>
          );
        })}
      </div>
    </Panel>
  );
}
