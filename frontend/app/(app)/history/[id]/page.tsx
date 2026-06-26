import Link from "next/link";
import { Card, SectionTitle, Pill, ProRangeBar } from "@/components/ui";
import ScoreRing from "@/components/ScoreRing";
import { CheckIcon, WarnIcon } from "@/components/icons";
import { getSwing, type Metric } from "@/lib/mock";

export default async function SwingDetailPage(
  props: PageProps<"/history/[id]">
) {
  const { id } = await props.params;
  const swing = getSwing(id);

  return (
    <div className="flex flex-col gap-6">
      <header>
        <Link href="/history" className="text-sm text-muted">
          ← History
        </Link>
        <h1 className="mt-3 font-display text-3xl font-bold tracking-tight text-ink">
          {swing.date}
        </h1>
        <p className="mt-1 text-sm text-muted">{swing.club}</p>
      </header>

      <Card className="flex flex-col items-center gap-2 py-7">
        <ScoreRing score={swing.score} size={150} />
        <Pill tone="brand">{swing.club}</Pill>
      </Card>

      {swing.strengths.length > 0 && (
        <section>
          <SectionTitle>Strengths</SectionTitle>
          <Card className="flex flex-col gap-3">
            {swing.strengths.map((s) => (
              <div key={s} className="flex items-center gap-3">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-good/15 text-good">
                  <CheckIcon className="h-4 w-4" />
                </span>
                <span className="text-sm text-ink">{s}</span>
              </div>
            ))}
          </Card>
        </section>
      )}

      {swing.needsWork.length > 0 && (
        <section>
          <SectionTitle>Needs Improvement</SectionTitle>
          <Card className="flex flex-col gap-3">
            {swing.needsWork.map((s) => (
              <div key={s} className="flex items-center gap-3">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-warn/15 text-warn">
                  <WarnIcon className="h-4 w-4" />
                </span>
                <span className="text-sm text-ink">{s}</span>
              </div>
            ))}
          </Card>
        </section>
      )}

      {swing.phases.length > 0 ? (
        <section>
          <SectionTitle>Phase Breakdown</SectionTitle>
          <div className="flex flex-col gap-4">
            {swing.phases.map((phase) => (
              <Card key={phase.key}>
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="font-display text-lg font-semibold text-ink">
                    {phase.name}
                  </h3>
                  <span className="font-display text-lg font-bold text-brand">
                    {phase.score}
                  </span>
                </div>
                <div className="flex flex-col gap-4">
                  {phase.metrics.map((m) => (
                    <MetricRow key={m.label} m={m} />
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </section>
      ) : (
        <Card className="text-center text-sm text-muted">
          Detailed phase breakdown isn’t available for this swing.
        </Card>
      )}
    </div>
  );
}

function MetricRow({ m }: { m: Metric }) {
  return (
    <div>
      <div className="mb-1.5 flex items-baseline justify-between">
        <span className="text-sm font-medium text-ink">{m.label}</span>
        <span
          className="font-display text-sm font-semibold"
          style={{
            color:
              m.status === "good" ? "var(--color-good)" : "var(--color-warn)",
          }}
        >
          {m.value}
          {m.unit}
        </span>
      </div>
      <ProRangeBar value={m.value} proAvg={m.proAvg} proStd={m.proStd} />
      <div className="mt-1.5 flex items-center justify-between">
        <span className="text-[11px] text-muted">
          Pro avg {m.proAvg}
          {m.unit} ± {m.proStd}
          {m.unit}
        </span>
        {m.note && <span className="text-[11px] text-warn">{m.note}</span>}
      </div>
    </div>
  );
}
