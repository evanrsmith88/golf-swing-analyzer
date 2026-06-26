import Link from "next/link";

export default function SplashPage() {
  return (
    <main className="relative mx-auto flex min-h-dvh max-w-md flex-col bg-brand px-7 text-white">
      {/* Logo, centered */}
      <div className="flex flex-1 flex-col items-center justify-center">
        <h1 className="font-display text-6xl font-bold tracking-tight">
          SwingLabs
        </h1>
        <p className="mt-4 max-w-[16rem] text-center text-sm leading-relaxed text-accent/90">
          AI swing analysis that measures you against the pros — frame by frame.
        </p>
      </div>

      {/* CTA, pinned to bottom */}
      <div className="flex flex-col items-center gap-4 pb-[max(28px,env(safe-area-inset-bottom))]">
        <Link
          href="/home"
          className="flex h-14 w-full items-center justify-center rounded-full bg-accent font-display text-lg font-semibold text-brand-deep transition active:scale-[0.98]"
        >
          Sign Up
        </Link>
        <Link
          href="/login"
          className="text-sm font-medium text-white/85 underline-offset-4 hover:underline"
        >
          I have an account
        </Link>
      </div>
    </main>
  );
}
