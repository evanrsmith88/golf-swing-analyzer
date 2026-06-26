import Link from "next/link";
import { Card, SectionTitle } from "@/components/ui";
import ScoreRing from "@/components/ScoreRing";
import { ArrowRight, ArrowUp, WarnIcon } from "@/components/icons";
import { user, latestSwing, recentProgress } from "@/lib/mock";

export default function HomePage() {
  return (
    <div className="flex flex-col gap-6">
      {/* Greeting */}
      <header>
        <p className="text-sm text-muted">Welcome back</p>
        <h1 className="font-display text-3xl font-bold tracking-tight text-ink">
          {user.name}
        </h1>
      </header>

      {/* Last swing hero */}
      <Card className="flex items-center gap-5">
        <ScoreRing score={latestSwing.score} size={116} label="last swing" />
        <div className="flex-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted">
            {latestSwing.date} · {latestSwing.club}
          </p>
          <div className="mt-2 flex items-start gap-2 rounded-xl bg-warn/10 p-3">
            <WarnIcon className="mt-0.5 h-4 w-4 shrink-0 text-warn" />
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-wide text-warn">
                Top issue
              </p>
              <p className="text-sm leading-snug text-ink">
                {latestSwing.topIssue}
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Primary CTA */}
      <Link
        href="/analyze"
        className="flex h-14 items-center justify-center gap-2 rounded-full bg-brand font-display text-lg font-semibold text-white transition active:scale-[0.98]"
      >
        Analyze New Swing
        <ArrowRight className="h-5 w-5" />
      </Link>

      {/* Recent progress */}
      <section>
        <SectionTitle>Recent Progress</SectionTitle>
        <div className="flex flex-col gap-3">
          {recentProgress.map((t) => {
            const delta = t.to - t.from;
            return (
              <Card key={t.label} className="flex items-center justify-between py-4">
                <div>
                  <p className="text-sm font-medium text-ink">{t.label}</p>
                  <p className="mt-0.5 font-display text-lg font-semibold text-ink">
                    {t.from}
                    {t.unit}{" "}
                    <span className="text-muted">→</span> {t.to}
                    {t.unit}
                  </p>
                </div>
                <span className="inline-flex items-center gap-1 rounded-full bg-good/12 px-2.5 py-1 text-sm font-semibold text-good">
                  <ArrowUp className="h-3.5 w-3.5" />
                  {delta > 0 ? "+" : ""}
                  {delta}
                  {t.unit}
                </span>
              </Card>
            );
          })}
        </div>
      </section>
    </div>
  );
}
