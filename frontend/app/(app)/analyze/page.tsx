"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, SectionTitle, Pill, ProRangeBar } from "@/components/ui";
import ScoreRing from "@/components/ScoreRing";
import {
  UploadIcon,
  RecordIcon,
  CheckIcon,
  WarnIcon,
  ArrowRight,
} from "@/components/icons";
import { latestSwing, type Metric } from "@/lib/mock";

type Stage = "idle" | "processing" | "done";

export default function AnalyzePage() {
  const [stage, setStage] = useState<Stage>("idle");

  function start() {
    setStage("processing");
    // Simulated pipeline run.
    setTimeout(() => setStage("done"), 2600);
  }

  return (
    <div className="flex flex-col gap-6">
      <header>
        <h1 className="font-display text-3xl font-bold tracking-tight text-ink">
          Analyze
        </h1>
        <p className="mt-1 text-sm text-muted">
          Upload or record a down-the-line swing to get your breakdown.
        </p>
      </header>

      {stage === "idle" && <Capture onStart={start} />}
      {stage === "processing" && <Processing />}
      {stage === "done" && <Results onReset={() => setStage("idle")} />}
    </div>
  );
}

function Capture({ onStart }: { onStart: () => void }) {
  return (
    <div className="flex flex-col gap-4">
      <button
        onClick={onStart}
        className="flex flex-col items-center justify-center gap-3 rounded-[var(--radius-card)] border-2 border-dashed border-brand/30 bg-accent/25 py-12 transition active:scale-[0.99]"
      >
        <span className="flex h-14 w-14 items-center justify-center rounded-full bg-brand text-white">
          <UploadIcon className="h-7 w-7" />
        </span>
        <span className="font-display text-lg font-semibold text-brand-deep">
          Upload Video
        </span>
        <span className="text-xs text-muted">MP4 or MOV · up to 30s</span>
      </button>

      <div className="flex items-center gap-3 text-xs font-medium uppercase tracking-wide text-muted">
        <span className="h-px flex-1 bg-line" />
        or
        <span className="h-px flex-1 bg-line" />
      </div>

      <button
        onClick={onStart}
        className="flex h-14 items-center justify-center gap-2 rounded-full border border-brand/30 bg-white font-display text-lg font-semibold text-brand transition active:scale-[0.98]"
      >
        <RecordIcon className="h-5 w-5" />
        Record Swing
      </button>

      <p className="mt-2 text-center text-xs text-muted">
        Tip: film from down-the-line, full body in frame, in good light.
      </p>
    </div>
  );
}

function Processing() {
  return (
    <Card className="flex flex-col items-center gap-5 py-14">
      <div className="h-12 w-12 rounded-full border-[3px] border-line border-t-brand animate-spin-slow" />
      <div className="text-center">
        <p className="font-display text-lg font-semibold text-ink">
          Processing…
        </p>
        <p className="mt-1 text-sm text-muted">
          Detecting pose · measuring angles · comparing to pros
        </p>
      </div>
    </Card>
  );
}

function Results({ onReset }: { onReset: () => void }) {
  const swing = latestSwing;
  return (
    <div className="flex animate-rise flex-col gap-6">
      {/* Overall */}
      <Card className="flex flex-col items-center gap-2 py-7">
        <ScoreRing score={swing.score} size={150} label="overall score" />
        <Pill tone="brand">{swing.club} · just now</Pill>
      </Card>

      {/* Strengths */}
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

      {/* Needs improvement */}
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

      {/* Phase breakdown */}
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

      <div className="flex flex-col gap-3">
        <Link
          href="/history"
          className="flex h-13 items-center justify-center gap-2 rounded-full bg-brand py-3.5 font-display font-semibold text-white transition active:scale-[0.98]"
        >
          Save to History
          <ArrowRight className="h-5 w-5" />
        </Link>
        <button
          onClick={onReset}
          className="text-sm font-medium text-muted underline-offset-4 hover:underline"
        >
          Analyze another swing
        </button>
      </div>
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
            color: m.status === "good" ? "var(--color-good)" : "var(--color-warn)",
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
        {m.note && (
          <span className="text-[11px] text-warn">{m.note}</span>
        )}
      </div>
    </div>
  );
}
