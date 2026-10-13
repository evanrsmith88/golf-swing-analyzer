import Link from "next/link";

// v1 has one screen (Analyze), so a simple top bar replaces BottomNav.
// Home/History/Profile still exist on mock data but aren't linked until after v1.
export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-dvh bg-smoke">
      <header className="sticky top-0 z-40 border-b border-line bg-white/95 pt-[env(safe-area-inset-top)] backdrop-blur">
        <div className="mx-auto flex h-14 max-w-5xl items-center px-5">
          <Link href="/" className="font-display text-xl font-bold tracking-tight text-brand">
            SwingLabs
          </Link>
        </div>
      </header>
      <main className="mx-auto max-w-md px-5 pb-16 pt-8 lg:max-w-5xl lg:pt-12">
        {children}
      </main>
    </div>
  );
}
