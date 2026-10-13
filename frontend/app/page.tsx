import Link from "next/link";

export default function SplashPage() {
  return (
    <main className="min-h-dvh bg-brand text-white">
      <div className="mx-auto flex min-h-dvh max-w-md flex-col px-7 sm:max-w-xl sm:justify-center">
        {/* Logo, centered */}
        <div className="flex flex-1 flex-col items-center justify-center sm:flex-none">
          <h1 className="font-display text-6xl font-bold tracking-tight sm:text-7xl">
            SwingLabs
          </h1>
          <p className="mt-4 max-w-[16rem] text-center text-sm leading-relaxed text-accent/90 sm:max-w-sm sm:text-base">
            AI swing analysis that measures you against the pros — frame by frame.
          </p>
        </div>

        {/* CTA, pinned to bottom on phones, under the logo on larger screens */}
        <div className="flex flex-col items-center gap-4 pb-[max(28px,env(safe-area-inset-bottom))] sm:mt-14 sm:pb-0">
          <Link
            href="/analyze"
            className="flex h-14 w-full items-center justify-center rounded-full bg-accent font-display text-lg font-semibold text-brand-deep transition hover:bg-accent-deep active:scale-[0.98] sm:max-w-xs"
          >
            Analyze My Swing
          </Link>
          <p className="text-xs text-white/70">
            Upload or record a swing · results in about 30 seconds
          </p>
        </div>
      </div>
    </main>
  );
}
