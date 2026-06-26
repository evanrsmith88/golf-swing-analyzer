import { scoreColor } from "@/lib/mock";

type Props = {
  score: number;
  size?: number;
  stroke?: number;
  label?: string;
  className?: string;
};

export default function ScoreRing({
  score,
  size = 140,
  stroke = 11,
  label = "out of 100",
  className,
}: Props) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, score)) / 100;
  const dash = c * pct;
  const color = scoreColor(score);

  return (
    <div
      className={className}
      style={{ width: size, height: size, position: "relative" }}
    >
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="var(--color-line)"
          strokeWidth={stroke}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${dash} ${c}`}
        />
      </svg>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <span
          className="font-display font-bold leading-none text-ink"
          style={{ fontSize: size * 0.32 }}
        >
          {score}
        </span>
        <span className="mt-1 text-[10px] uppercase tracking-wide text-muted">
          {label}
        </span>
      </div>
    </div>
  );
}
