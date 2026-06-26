import Link from "next/link";

export default function LoginPage() {
  return (
    <main className="relative mx-auto flex min-h-dvh max-w-md flex-col bg-brand px-7 text-white">
      <div className="pt-16">
        <Link href="/" className="text-sm text-white/70">
          ← Back
        </Link>
        <h1 className="mt-8 font-display text-4xl font-bold tracking-tight">
          Welcome back
        </h1>
        <p className="mt-2 text-sm text-accent/90">
          Sign in to pick up where you left off.
        </p>
      </div>

      <form className="mt-10 flex flex-col gap-4">
        <label className="flex flex-col gap-1.5">
          <span className="text-xs font-medium uppercase tracking-wide text-white/70">
            Email
          </span>
          <input
            type="email"
            placeholder="you@example.com"
            className="h-13 rounded-2xl bg-white/10 px-4 py-3.5 text-white placeholder:text-white/40 outline-none ring-1 ring-white/15 focus:ring-accent"
          />
        </label>
        <label className="flex flex-col gap-1.5">
          <span className="text-xs font-medium uppercase tracking-wide text-white/70">
            Password
          </span>
          <input
            type="password"
            placeholder="••••••••"
            className="h-13 rounded-2xl bg-white/10 px-4 py-3.5 text-white placeholder:text-white/40 outline-none ring-1 ring-white/15 focus:ring-accent"
          />
        </label>
      </form>

      <div className="mt-auto flex flex-col items-center gap-4 pb-[max(28px,env(safe-area-inset-bottom))]">
        <Link
          href="/home"
          className="flex h-14 w-full items-center justify-center rounded-full bg-accent font-display text-lg font-semibold text-brand-deep transition active:scale-[0.98]"
        >
          Sign In
        </Link>
        <Link href="/" className="text-sm font-medium text-white/85">
          Need an account? <span className="underline">Sign up</span>
        </Link>
      </div>
    </main>
  );
}
