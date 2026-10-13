"use client";

import { useRef, useState } from "react";
import { Card, SectionTitle, Pill, ProRangeBar } from "@/components/ui";
import ScoreRing from "@/components/ScoreRing";
import {
  UploadIcon,
  RecordIcon,
  CheckIcon,
  WarnIcon,
} from "@/components/icons";
import { type Metric } from "@/lib/mock";
import { analyzeSwing, type Analysis, type Club } from "@/lib/api";

const MAX_UPLOAD_MB = 100;

type Stage = "idle" | "processing" | "done" | "error";

export default function AnalyzePage() {
  const [stage, setStage] = useState<Stage>("idle");
  const [club, setClub] = useState<Club>("driver");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [error, setError] = useState("");

  async function start(video: File) {
    if (video.size > MAX_UPLOAD_MB * 1024 * 1024) {
      setError(`That video is too large (max ${MAX_UPLOAD_MB} MB). Try a shorter clip.`);
      setStage("error");
      return;
    }

    setStage("processing");
    try {
      setAnalysis(await analyzeSwing(video, club));
      setStage("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong analyzing your swing.");
      setStage("error");
    }
  }

  function reset() {
    setAnalysis(null);
    setError("");
    setStage("idle");
  }

  // On desktop, the capture steps sit in a centered column; results use the full width.
  const narrow = stage === "done" ? "" : "lg:mx-auto lg:w-full lg:max-w-md";

  return (
    <div className="flex flex-col gap-6">
      <header className={narrow}>
        <h1 className="font-display text-3xl font-bold tracking-tight text-ink">
          {stage === "done" ? "Your Swing" : "Analyze"}
        </h1>
        <p className="mt-1 text-sm text-muted">
          {stage === "done"
            ? "Skeleton overlay, key positions, and how they compare to the pros."
            : "Upload or record a down-the-line swing to get your breakdown."}
        </p>
      </header>

      <div className={narrow}>
        {stage === "idle" && <Capture club={club} onClubChange={setClub} onVideo={start} />}
        {stage === "processing" && <Processing />}
        {stage === "error" && <ErrorCard message={error} onRetry={reset} />}
        {stage === "done" && analysis && <Results analysis={analysis} onReset={reset} />}
      </div>
    </div>
  );
}

function Capture({
  club,
  onClubChange,
  onVideo,
}: {
  club: Club;
  onClubChange: (club: Club) => void;
  onVideo: (video: File) => void;
}) {
  const uploadInput = useRef<HTMLInputElement>(null);
  const recordInput = useRef<HTMLInputElement>(null);

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const video = e.target.files?.[0];
    e.target.value = "";
    if (video) onVideo(video);
  }

  return (
    <div className="flex flex-col gap-4">
      <div>
        <SectionTitle>Club</SectionTitle>
        <div className="flex gap-1 rounded-2xl bg-white p-1 ring-1 ring-line">
          {(["driver", "iron"] as const).map((option) => (
            <button
              key={option}
              onClick={() => onClubChange(option)}
              className={`flex-1 rounded-xl py-2.5 text-sm font-medium capitalize transition ${
                club === option ? "bg-brand text-white shadow-sm" : "text-muted hover:text-ink"
              }`}
            >
              {option}
            </button>
          ))}
        </div>
      </div>

      <input ref={uploadInput} type="file" accept="video/*" hidden onChange={handleFile} />
      <input
        ref={recordInput}
        type="file"
        accept="video/*"
        capture="environment"
        hidden
        onChange={handleFile}
      />

      <button
        onClick={() => uploadInput.current?.click()}
        className="flex flex-col items-center justify-center gap-3 rounded-[var(--radius-card)] border-2 border-dashed border-brand/30 bg-accent/25 py-12 transition active:scale-[0.99]"
      >
        <span className="flex h-14 w-14 items-center justify-center rounded-full bg-brand text-white">
          <UploadIcon className="h-7 w-7" />
        </span>
        <span className="font-display text-lg font-semibold text-brand-deep">
          Upload Video
        </span>
        <span className="text-xs text-muted">MP4 or MOV · up to 20s</span>
      </button>

      <div className="flex items-center gap-3 text-xs font-medium uppercase tracking-wide text-muted">
        <span className="h-px flex-1 bg-line" />
        or
        <span className="h-px flex-1 bg-line" />
      </div>

      <button
        onClick={() => recordInput.current?.click()}
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
        <p className="mt-3 text-xs text-muted">This usually takes 10–30 seconds.</p>
      </div>
    </Card>
  );
}

function ErrorCard({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <Card className="flex flex-col items-center gap-4 py-10 text-center">
      <span className="flex h-12 w-12 items-center justify-center rounded-full bg-warn/15 text-warn">
        <WarnIcon className="h-6 w-6" />
      </span>
      <div>
        <p className="font-display text-lg font-semibold text-ink">
          Couldn&rsquo;t analyze that swing
        </p>
        <p className="mt-1 text-sm text-muted">{message}</p>
      </div>
      <button
        onClick={onRetry}
        className="h-12 rounded-full bg-brand px-8 font-display font-semibold text-white transition active:scale-[0.98]"
      >
        Try again
      </button>
    </Card>
  );
}

function Results({ analysis, onReset }: { analysis: Analysis; onReset: () => void }) {
  return (
    <div className="grid animate-rise gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)] lg:items-start lg:gap-8">
      {/* Left on desktop: video + score stay in view while the breakdown scrolls */}
      <div className="flex flex-col gap-6 lg:sticky lg:top-24">
        {/* Skeleton overlay */}
        <Card className="overflow-hidden p-0">
          <video
            src={analysis.videoUrl}
            controls
            autoPlay
            muted
            loop
            playsInline
            className="mx-auto max-h-[70vh] w-full bg-ink object-contain lg:max-h-[60vh]"
          />
        </Card>

        {/* Overall */}
        <Card className="flex flex-col items-center gap-2 py-7">
          <ScoreRing score={analysis.score} size={150} label="overall score" />
          <Pill tone="brand">{analysis.club} · just now</Pill>
        </Card>
      </div>

      <div className="flex flex-col gap-6">

        {/* Strengths */}
        {analysis.strengths.length > 0 && (
          <section>
            <SectionTitle>Strengths</SectionTitle>
            <Card className="flex flex-col gap-3">
              {analysis.strengths.map((s) => (
                <div key={s} className="flex items-center gap-3">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-good/15 text-good">
                    <CheckIcon className="h-4 w-4" />
                  </span>
                  <span className="text-sm text-ink">{s}</span>
                </div>
              ))}
            </Card>
          </section>
        )}

        {/* Needs improvement */}
        {analysis.needsWork.length > 0 && (
          <section>
            <SectionTitle>Needs Improvement</SectionTitle>
            <Card className="flex flex-col gap-3">
              {analysis.needsWork.map((s) => (
                <div key={s} className="flex items-center gap-3">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-warn/15 text-warn">
                    <WarnIcon className="h-4 w-4" />
                  </span>
                  <span className="text-sm text-ink">{s}</span>
                </div>
              ))}
            </Card>
          </section>
        )}

        {/* Phase breakdown */}
        <section>
          <SectionTitle>Phase Breakdown</SectionTitle>
          <div className="flex flex-col gap-4">
            {analysis.phases.map((phase) => (
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

        <button
          onClick={onReset}
          className="flex h-13 items-center justify-center gap-2 rounded-full bg-brand py-3.5 font-display font-semibold text-white transition active:scale-[0.98]"
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
