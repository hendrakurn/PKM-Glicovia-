import { Panel } from "@/components/ui";

type Series = {
  label: string;
  color: string;
  values: number[];
};

function buildPoints(values: number[], width: number, height: number, padding: { top: number; right: number; bottom: number; left: number }, min: number, max: number) {
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;
  const step = values.length > 1 ? innerWidth / (values.length - 1) : innerWidth;

  return values
    .map((value, index) => {
      const x = padding.left + step * index;
      const y = padding.top + (1 - (value - min) / Math.max(max - min, 1)) * innerHeight;
      return [x, y] as const;
    })
    .map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`)
    .join(" ");
}

function buildArea(values: number[], width: number, height: number, padding: { top: number; right: number; bottom: number; left: number }, min: number, max: number) {
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;
  const step = values.length > 1 ? innerWidth / (values.length - 1) : innerWidth;
  const points = values.map((value, index) => {
    const x = padding.left + step * index;
    const y = padding.top + (1 - (value - min) / Math.max(max - min, 1)) * innerHeight;
    return [x, y] as const;
  });
  const baseY = height - padding.bottom;
  const start = points[0];
  const end = points[points.length - 1];

  return `M ${start[0].toFixed(1)} ${baseY.toFixed(1)} L ${start[0].toFixed(1)} ${start[1].toFixed(1)} ${points
    .slice(1)
    .map(([x, y]) => `L ${x.toFixed(1)} ${y.toFixed(1)}`)
    .join(" ")} L ${end[0].toFixed(1)} ${baseY.toFixed(1)} Z`;
}

export function LineChartCard({
  title,
  description,
  labels,
  series,
  height = 280,
}: {
  title: string;
  description?: string;
  labels: string[];
  series: Series[];
  height?: number;
}) {
  const width = 760;
  const padding = { top: 22, right: 18, bottom: 42, left: 42 };
  const values = series.flatMap((item) => item.values);
  const min = Math.min(...values) - 6;
  const max = Math.max(...values) + 6;
  const gridLines = 4;

  return (
    <Panel className="p-5">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-[color:var(--text-primary)]">{title}</h2>
          {description ? <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{description}</p> : null}
        </div>
        <div className="hidden items-center gap-4 md:flex">
          {series.map((item) => (
            <div key={item.label} className="flex items-center gap-2 text-sm text-[color:var(--text-secondary)]">
              <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
              {item.label}
            </div>
          ))}
        </div>
      </div>

      <div className="overflow-hidden rounded-[12px] border border-[color:var(--border)] bg-[linear-gradient(180deg,rgba(226,251,206,0.92),rgba(255,253,238,0.92))] p-3">
        <svg viewBox={`0 0 ${width} ${height}`} className="h-[280px] w-full">
          {Array.from({ length: gridLines + 1 }).map((_, index) => {
            const y = padding.top + ((height - padding.top - padding.bottom) / gridLines) * index;
            return (
              <g key={index}>
                <line x1={padding.left} x2={width - padding.right} y1={y} y2={y} stroke="#E2FBCE" strokeWidth="1" />
                <text x={12} y={y + 4} style={{ fill: "var(--text-muted)" }} className="text-[10px] font-medium">
                  {Math.round(max - ((max - min) / gridLines) * index)}
                </text>
              </g>
            );
          })}

          {labels.map((label, index) => {
            const step = labels.length > 1 ? (width - padding.left - padding.right) / (labels.length - 1) : width;
            const x = padding.left + step * index;
            return (
              <text key={label} x={x} y={height - 12} textAnchor="middle" style={{ fill: "var(--text-muted)" }} className="text-[10px] font-medium">
                {label}
              </text>
            );
          })}

          {series.map((item, index) => {
            const points = buildPoints(item.values, width, height, padding, min, max);
            const area = buildArea(item.values, width, height, padding, min, max);
            return (
              <g key={item.label}>
                <path d={area} fill={`${item.color}18`} />
                <polyline
                  points={points}
                  fill="none"
                  stroke={item.color}
                  strokeWidth={index === 0 ? 3 : 2.5}
                  strokeLinejoin="round"
                  strokeLinecap="round"
                />
                {item.values.map((value, pointIndex) => {
                  const step = item.values.length > 1 ? (width - padding.left - padding.right) / (item.values.length - 1) : width;
                  const x = padding.left + step * pointIndex;
                  const y = padding.top + (1 - (value - min) / Math.max(max - min, 1)) * (height - padding.top - padding.bottom);
                  return <circle key={`${item.label}-${pointIndex}`} cx={x} cy={y} r={index === 0 ? 4 : 3.5} fill={item.color} stroke="#FFFDEE" strokeWidth="2" />;
                })}
              </g>
            );
          })}
        </svg>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-3 md:hidden">
        {series.map((item) => (
          <div key={item.label} className="flex items-center gap-2 text-sm text-[color:var(--text-secondary)]">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
            {item.label}
          </div>
        ))}
      </div>
    </Panel>
  );
}
