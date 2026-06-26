import { ReactNode } from "react";

export function Card({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-[var(--radius-card)] border border-line bg-white p-5 ${className}`}
    >
      {children}
    </div>
  );
}

export function SectionTitle({ children }: { children: ReactNode }) {
  return (
    <h2 className="mb-3 text-xs font-semibold uppercase tracking-[0.14em] text-muted">
      {children}
    </h2>
  );
}

export function Pill({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "good" | "warn" | "brand";
}) {
  const tones: Record<string, string> = {
    neutral: "bg-smoke text-muted",
    good: "bg-good/12 text-good",
    warn: "bg-warn/15 text-warn",
    brand: "bg-accent text-brand-deep",
  };
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${tones[tone]}`}
    >
      {children}
    </span>
  );
}

// A bar showing where the user's value sits relative to the pro range (avg ± std).
export function ProRangeBar({
  value,
  proAvg,
  proStd,
}: {
  value: number;
  proAvg: number;
  proStd: number;
}) {
  // Build a window around the pro range so the marker has room.
  const span = Math.max(proStd * 4, Math.abs(value - proAvg) * 2.2, 12);
  const min = proAvg - span / 2;
  const clamp = (n: number) => Math.max(0, Math.min(100, ((n - min) / span) * 100));

  const bandStart = clamp(proAvg - proStd);
  const bandEnd = clamp(proAvg + proStd);
  const userPos = clamp(value);
  const inRange = value >= proAvg - proStd && value <= proAvg + proStd;

  return (
    <div className="relative h-2 w-full rounded-full bg-smoke">
      <div
        className="absolute top-0 h-2 rounded-full bg-accent"
        style={{ left: `${bandStart}%`, width: `${bandEnd - bandStart}%` }}
        title="Pro range"
      />
      <div
        className="absolute -top-1 h-4 w-4 -translate-x-1/2 rounded-full border-2 border-white shadow"
        style={{
          left: `${userPos}%`,
          background: inRange ? "var(--color-good)" : "var(--color-warn)",
        }}
        title="You"
      />
    </div>
  );
}
