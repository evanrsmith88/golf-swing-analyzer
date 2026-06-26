import Link from "next/link";
import { Card, SectionTitle } from "@/components/ui";
import { ChevronRight, ArrowUp } from "@/components/icons";
import { swings, scoreColor } from "@/lib/mock";

export default function HistoryPage() {
  const best = Math.max(...swings.map((s) => s.score));
  const avg = Math.round(
    swings.reduce((a, s) => a + s.score, 0) / swings.length
  );

  return (
    <div className="flex flex-col gap-6">
      <header>
        <h1 className="font-display text-3xl font-bold tracking-tight text-ink">
          History
        </h1>
        <p className="mt-1 text-sm text-muted">{swings.length} swings analyzed</p>
      </header>

      {/* Summary stats */}
      <div className="grid grid-cols-2 gap-3">
        <Card className="py-4">
          <p className="text-xs uppercase tracking-wide text-muted">Best</p>
          <p className="mt-1 font-display text-3xl font-bold text-ink">{best}</p>
        </Card>
        <Card className="py-4">
          <p className="flex items-center gap-1 text-xs uppercase tracking-wide text-muted">
            Average
            <ArrowUp className="h-3 w-3 text-good" />
          </p>
          <p className="mt-1 font-display text-3xl font-bold text-ink">{avg}</p>
        </Card>
      </div>

      {/* Swing list */}
      <section>
        <SectionTitle>All Swings</SectionTitle>
        <div className="flex flex-col gap-3">
          {swings.map((s) => (
            <Link key={s.id} href={`/history/${s.id}`}>
              <Card className="flex items-center gap-4 py-4 transition active:scale-[0.99]">
                <span
                  className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full font-display text-lg font-bold text-white"
                  style={{ background: scoreColor(s.score) }}
                >
                  {s.score}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-ink">
                    {s.date} · {s.club}
                  </p>
                  <p className="truncate text-sm text-muted">{s.topIssue}</p>
                </div>
                <ChevronRight className="h-5 w-5 shrink-0 text-muted" />
              </Card>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
